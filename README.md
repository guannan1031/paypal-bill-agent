# 💳 PayPal 账单助手 Agent（Bill Pay Agent）

> **AI Agentic Commerce 演示项目 · PayPal AI Hackathon 2026 参赛作品**
> 用自然语言把一堆账单交给 AI Agent：自动解析、风险提示、多轮确认，然后**一键调用 PayPal 完成付款闭环**。

---

## 它解决什么问题

个人和小微经营者每月面对电费、信用卡、云服务、订阅等多笔账单，分散在不同渠道、日期不一、容易漏付逾期。
传统做法是逐笔打开支付页面手动操作。本项目让 **AI Agent 代理完成整个付账流程**：

1. **理解**：粘贴原始账单/催缴文本，Agent 解析出结构化账单（科目、金额、币种、到期日）；
2. **判断**：自动标记风险——已逾期、临近到期、金额较大需二次确认、疑似重复账单；
3. **确认**：用户勾选确认应付账单（人机协同，Agent 不擅自付款）；
4. **执行**：调用 **PayPal Orders v2 API（沙箱）**创建订单 → 用户授权 → 捕获付款 → 返回交易回执。

## 为什么是 Agentic Commerce

付款决策交给 AI、执行交给 PayPal、控制权留给人——这是"AI 代理替你完成商业闭环"的完整最小样本：

```
┌─────────────┐   解析/风险   ┌──────────────┐  确认   ┌─────────────────┐
│ 账单原始文本  │ ───────────► │ AI 账单 Agent  │ ─────► │ 人工勾选确认      │
└─────────────┘              └──────────────┘        └────────┬────────┘
                                                              │ 选中账单
                                                              ▼
                          ┌──────────────────────────────────────────┐
                          │ PayPal Orders v2（沙箱）                  │
                          │  create order → 买家授权(approve) → capture │
                          └──────────────────────────────────────────┘
```

## 快速开始（本地跑，3 分钟）

```bash
git clone <你的仓库地址>
cd paypal-bill-agent
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python deploy_run.py                                 # 默认 http://127.0.0.1:8878
```

打开浏览器访问 `http://127.0.0.1:8878` → 点「填入示例」→「AI 解析账单」→ 勾选 →「用 PayPal 一键支付」。

**未配置任何密钥也能完整跑通**：自动进入 MOCK 演示模式，完整模拟 create → approve → capture 闭环（界面明确标注"演示模式"）。

## 接入真实 PayPal 沙箱（免费）

1. 注册 [PayPal Developer](https://developer.paypal.com) → Dashboard → **Sandbox** → 创建 App，拿到 `Client ID` / `Secret`；
2. 复制环境变量模板并填写：

```bash
cp .env.example .env
# 编辑 .env：PAYPAL_CLIENT_ID / PAYPAL_CLIENT_SECRET
```

3. 重启后 `GET /api/health` 返回 `"paypal_mode": "sandbox"`，付款将跳转 PayPal 沙箱托管授权页，回跳后自动捕获——**零真实资金**。

## 接入大模型账单解析（可选）

默认使用本地规则解析（无需密钥）。在 `.env` 配置任意 **OpenAI 风格**接口即可切换为大模型抽取：

```
AI_BILL_API_KEY=sk-...
AI_BILL_BASE_URL=https://api.deepseek.com   # 或任意兼容端点
AI_BILL_MODEL=deepseek-chat
```

解析失败自动回退规则解析，演示不中断。

## API 一览

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/health` | 运行模式（sandbox/mock）、模型是否配置 |
| POST | `/api/bills/parse` | 账单解析：`{text}` 或 `{bills:[...]}` → 结构化账单 |
| POST | `/api/bills/analyze` | 风险分析：逾期/临期/大额/重复标记 + 合计 |
| POST | `/api/pay/prepare` | 创建 PayPal 订单（或 MOCK 订单），返回 approve_url |
| POST | `/api/pay/capture` | 捕获付款，返回交易号/状态/金额 |

## 技术栈

- **后端**：Python · FastAPI · httpx（直连 PayPal REST，无重 SDK）
- **前端**：原生 HTML/CSS/JS 单页（零构建依赖）
- **AI**：可选 LLM 账单抽取 + 本地规则兜底（双通道）
- **支付**：PayPal Orders v2（CAPTURE 意图，沙箱环境）
- **存储**：内存订单簿（演示）；生产可换 SQLite（README 已注明）

## 目录结构

```
├── backend/app.py        # FastAPI：解析 Agent + 风险引擎 + PayPal 集成
├── frontend/index.html   # 单页演示界面（三步流程）
├── deploy_run.py         # 入口：读 $PORT，放行反代域名
├── requirements.txt      # 依赖（含锁定版本）
├── render.yaml           # Render 一键部署蓝图
└── .env.example          # 环境变量模板
```

## 部署

已附 `render.yaml`（Render 蓝图）：推送到公开仓库后，在 Render 选择该仓库即可一键部署免费实例，自动安装依赖并启动。
也可以任何支持 Python 单端口服务的平台运行（ Railway / Fly.io / 自有服务器）。

## 测试

```bash
# 本地冒烟（服务启动后）
curl http://127.0.0.1:8878/api/health
curl -X POST http://127.0.0.1:8878/api/bills/parse \
  -H "Content-Type: application/json" \
  -d '{"text":"电费 89.5 元 2026-11-05\n信用卡还款 3200 元 2026-10-25"}'
```

## 参赛信息

- **赛事**：PayPal AI Hackathon 2026（Devpost，https://paypalaihackathon.devpost.com/）
- **提交物**：可运行原型（本仓库 + 部署 URL）· 项目描述 · 工具说明 · 公开仓库（本仓库）· <3 分钟演示视频
- **冲击方向**：Best Use of Agentic Commerce / Best AI Agent 单项奖

## License

MIT（见 [LICENSE](./LICENSE)）
