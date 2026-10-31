"""PayPal 账单助手 Agent · FastAPI 后端。

支付链路：PayPal Orders v2（沙箱 api-m.sandbox.paypal.com）。
未配置 PAYPAL_CLIENT_ID / PAYPAL_CLIENT_SECRET 时自动进入 MOCK 演示模式——
完整模拟 create → approve → capture 闭环，接口形态与真实沙箱一致，
供演示视频与无凭证评审使用（响应带 "mode": "mock" 明确标注为模拟）。

AI 账单解析：配置了 AI_BILL_API_KEY（OpenAI 风格 chat/completions）时走大模型
抽取，否则走本地规则解析；两条路径均可用，演示不依赖外部凭证。
"""
import os
import re
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Literal

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

try:
    from . import invoicing  # package run (uvicorn backend.app:app)
except ImportError:  # direct run from backend/
    import invoicing

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"

PAYPAL_BASE = os.environ.get("PAYPAL_API_BASE", "https://api-m.sandbox.paypal.com").rstrip("/")
PAYPAL_CLIENT_ID = os.environ.get("PAYPAL_CLIENT_ID", "").strip()
PAYPAL_CLIENT_SECRET = os.environ.get("PAYPAL_CLIENT_SECRET", "").strip()
AI_KEY = os.environ.get("AI_BILL_API_KEY", "").strip()
AI_BASE = os.environ.get("AI_BILL_BASE_URL", "https://api.deepseek.com").rstrip("/")
AI_MODEL = os.environ.get("AI_BILL_MODEL", "deepseek-chat")

AMOUNT_RE = re.compile(r"(\d+(?:\.\d+)?)")
DATE_RE = re.compile(r"(\d{4})[-/年.](\d{1,2})[-/月.](\d{1,2})")
LARGE_AMOUNT = 100.0  # 单笔超过该值视为「金额较大」，提示二次确认


# ---------------- 数据模型 ----------------
class Bill(BaseModel):
    label: str = Field(description="账单名称/科目")
    amount: float
    currency: str = "USD"
    due_date: str | None = None  # YYYY-MM-DD
    vendor: str | None = None


class ParseRequest(BaseModel):
    text: str | None = None
    bills: list[Bill] | None = None


class AnalyzeRequest(BaseModel):
    bills: list[Bill]


class PrepareRequest(BaseModel):
    bills: list[Bill] = Field(description="用户确认要支付的账单（多轮确认后选中项）")
    return_url: str | None = Field(default=None, description="沙箱授权后回跳地址（前端传入当前 origin）")


# ---------------- 账单解析 ----------------
def parse_bills_rules(text: str) -> list[Bill]:
    """本地规则解析：每行一条账单，抽取金额与日期，其余作为名称。"""
    bills: list[Bill] = []
    for raw in re.split(r"[\n;；]", text):
        line = raw.strip().lstrip("-•*·、").strip()
        if not line:
            continue
        am = AMOUNT_RE.search(line.replace(",", ""))
        if not am:
            continue
        amount = float(am.group(1))
        dm = DATE_RE.search(line)
        due = None
        if dm:
            try:
                due = date(int(dm.group(1)), int(dm.group(2)), int(dm.group(3))).isoformat()
            except ValueError:
                due = None
        label = line
        for frag in (am.group(0), dm.group(0) if dm else None):
            if frag:
                label = label.replace(frag, " ")
        label = re.sub(r"(人民币|美元|RMB|USD|CNY|元|¥|￥|\$)", " ", label)
        label = re.sub(r"\s+", " ", label).strip(" ：:（）()") or "Untitled bill"
        currency = "CNY" if ("¥" in line or "￥" in line or "元" in line) else "USD"
        bills.append(Bill(label=label, amount=amount, currency=currency, due_date=due))
    return bills


def parse_bills_llm(text: str) -> list[Bill]:
    """大模型抽取（OpenAI 风格），失败抛错由调用方回退规则解析。"""
    prompt = (
        "从下面的账单/催缴信息中抽取所有账单，仅返回 JSON："
        '{"bills":[{"label":"","amount":0,"currency":"CNY|USD","due_date":"YYYY-MM-DD或null","vendor":""}]}\n\n'
        + text
    )
    with httpx.Client(timeout=30) as client:
        resp = client.post(
            f"{AI_BASE}/chat/completions",
            headers={"Authorization": f"Bearer {AI_KEY}"},
            json={"model": AI_MODEL, "messages": [{"role": "user", "content": prompt}],
                  "temperature": 0, "response_format": {"type": "json_object"}},
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
    start, end = content.find("{"), content.rfind("}")
    import json

    data = json.loads(content[start:end + 1])
    return [Bill(**b) for b in data.get("bills", []) if b.get("amount")]


def parse_bills(req: ParseRequest) -> tuple[list[Bill], str]:
    if req.bills:
        return list(req.bills), "client"
    text = (req.text or "").strip()
    if not text:
        return [], "client"
    if AI_KEY:
        try:
            bills = parse_bills_llm(text)
            if bills:
                return bills, "llm"
        except Exception:
            pass
    return parse_bills_rules(text), "rules"


# ---------------- 风险分析 ----------------
def analyze_bills(req: AnalyzeRequest) -> dict:
    today = date.today()
    bills, flagged = [], []
    seen: dict[tuple, int] = {}
    for b in req.bills:
        risks: list[str] = []
        if b.due_date:
            try:
                due = date.fromisoformat(b.due_date)
                delta = (due - today).days
                if delta < 0:
                    risks.append(f"Overdue by {-delta} days")
                elif delta <= 3:
                    risks.append(f"Due in {delta} days")
            except ValueError:
                pass
        if b.amount >= LARGE_AMOUNT:
            risks.append(f"Large amount ({b.amount:g}) - confirm twice")
        key = (b.label, round(b.amount, 2), b.due_date)
        seen[key] = seen.get(key, 0) + 1
        if seen[key] > 1:
            risks.append("Possible duplicate")
        entry = b.model_dump()
        entry["risks"] = risks
        bills.append(entry)
        if risks:
            flagged.append(entry)
    total = round(sum(b.amount for b in req.bills), 2)
    return {"bills": bills, "flagged": flagged, "total": total, "currency": req.bills[0].currency if req.bills else "USD"}


# ---------------- PayPal 集成 ----------------
def paypal_token() -> str:
    with httpx.Client(timeout=30) as client:
        resp = client.post(
            f"{PAYPAL_BASE}/v1/oauth2/token",
            auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET),
            data={"grant_type": "client_credentials"},
        )
        resp.raise_for_status()
        return resp.json()["access_token"]


def paypal_create_order(bills: list[Bill], total: float, currency: str, return_url: str | None) -> tuple[str, str]:
    token = paypal_token()
    items = [
        {
            "name": b.label[:127] or "账单",
            "unit_amount": {"currency_code": b.currency, "value": f"{b.amount:.2f}"},
            "quantity": "1",
        }
        for b in bills
    ]
    payload = {
        "intent": "CAPTURE",
        "purchase_units": [
            {"items": items, "amount": {"currency_code": currency, "value": f"{total:.2f}"}}
        ],
    }
    if return_url:
        payload["application_context"] = {
            "return_url": return_url,
            "cancel_url": return_url,
            "brand_name": "PayPal 账单助手 Agent",
            "user_action": "PAY_NOW",
        }
    with httpx.Client(timeout=30) as client:
        resp = client.post(
            f"{PAYPAL_BASE}/v2/checkout/orders",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json=payload,
        )
        resp.raise_for_status()
        order = resp.json()
    approve = next((l["href"] for l in order.get("links", []) if l.get("rel") == "approve"), "")
    return order["id"], approve


def paypal_capture(order_id: str) -> dict:
    token = paypal_token()
    with httpx.Client(timeout=30) as client:
        resp = client.post(
            f"{PAYPAL_BASE}/v2/checkout/orders/{order_id}/capture",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        )
        resp.raise_for_status()
        order = resp.json()
    capture = order["purchase_units"][0]["payments"]["captures"][0]
    return {
        "status": capture["status"],
        "transaction_id": capture["id"],
        "amount": capture["amount"]["value"],
        "currency": capture["amount"]["currency_code"],
    }


ORDERS: dict[str, dict] = {}  # 内存订单簿（演示用；生产可换 SQLite，见仓库 README）


def mock_create_order(bills: list[Bill], total: float, currency: str) -> tuple[str, str]:
    order_id = "MOCK-" + uuid.uuid4().hex[:10].upper()
    ORDERS[order_id] = {"total": total, "currency": currency, "bills": [b.model_dump() for b in bills]}
    return order_id, f"/#mock-approve?order_id={order_id}"


def mock_capture(order_id: str) -> dict:
    order = ORDERS.get(order_id, {"total": 0, "currency": "USD"})
    return {
        "status": "COMPLETED",
        "transaction_id": "MOCKTX-" + uuid.uuid4().hex[:10].upper(),
        "amount": f"{order['total']:.2f}",
        "currency": order["currency"],
    }


# ---------------- 应用 ----------------
def create_app() -> FastAPI:
    app = FastAPI(title="PayPal 账单助手 Agent", version="0.2.0")
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

    paypal_mode = "sandbox" if (PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET) else "mock"

    # v0.2: two-way money flow - invoices (get paid) alongside orders (pay bills)
    invoicing.register_invoicing_routes(app, paypal_mode, paypal_token, "Bill Agent Demo")

    @app.get("/api/agent/capabilities")
    def agent_capabilities():
        try:
            try:
                from . import toolkit_bridge as tb
            except ImportError:
                import toolkit_bridge as tb
            st = tb.status()
        except Exception as e:
            st = {"installed": False, "error": str(e)}
        return {
            "mode": paypal_mode,
            "agent_toolkit": st,
            "mcp_server": "backend/mcp_server.py (stdio, connectable from Claude Desktop)",
            "paypal_surfaces": [
                "OAuth2 client credentials",
                "Orders v2 (direct REST, verified)",
                "Invoicing v2 (official Agent Toolkit, auto-send disabled for human-in-the-loop)",
            ],
        }

    @app.get("/api/health")
    def health():
        return {"status": "ok", "paypal_mode": paypal_mode, "model_configured": bool(AI_KEY)}

    @app.post("/api/bills/parse")
    def parse(req: ParseRequest):
        bills, source = parse_bills(req)
        return {"bills": [b.model_dump() for b in bills], "source": source}

    @app.post("/api/bills/analyze")
    def analyze(req: AnalyzeRequest):
        if not req.bills:
            raise HTTPException(400, "账单列表为空")
        return analyze_bills(req)

    @app.post("/api/pay/prepare")
    def prepare(req: PrepareRequest):
        if not req.bills:
            raise HTTPException(400, "没有选中的账单")
        currencies = {b.currency for b in req.bills}
        if len(currencies) > 1:
            raise HTTPException(400, f"不支持混合币种支付：{sorted(currencies)}")
        currency = req.bills[0].currency
        total = round(sum(b.amount for b in req.bills), 2)
        try:
            if paypal_mode == "sandbox":
                order_id, approve_url = paypal_create_order(req.bills, total, currency, req.return_url)
            else:
                order_id, approve_url = mock_create_order(req.bills, total, currency)
        except httpx.HTTPError as e:
            return JSONResponse(status_code=502, content={"error": f"PayPal API 调用失败: {e}"})
        return {
            "mode": paypal_mode,
            "order_id": order_id,
            "approve_url": approve_url,
            "total": f"{total:.2f}",
            "currency": currency,
            "items": [{"label": b.label, "amount": b.amount} for b in req.bills],
        }

    @app.post("/api/pay/capture")
    def capture(payload: dict):
        order_id = str(payload.get("order_id", ""))
        if not order_id:
            raise HTTPException(400, "缺少 order_id")
        try:
            result = paypal_capture(order_id) if paypal_mode == "sandbox" else mock_capture(order_id)
        except httpx.HTTPError as e:
            return JSONResponse(status_code=502, content={"error": f"PayPal 捕获失败: {e}"})
        result["mode"] = paypal_mode
        result["order_id"] = order_id
        return result

    if FRONTEND.exists():
        app.mount("/", StaticFiles(directory=FRONTEND, html=True), name="frontend")
    return app


app = create_app()
