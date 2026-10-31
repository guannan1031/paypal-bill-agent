"""Official MCP server for the AI Bill & Invoice Agent.

Exposes the agent's tools over stdio so judges (and anyone) can plug it into
Claude Desktop or any MCP client:

    {
      "mcpServers": {
        "paypal-bill-agent": {
          "command": "<python>",
          "args": ["backend/mcp_server.py"],
          "cwd": "<repo root>"
        }
      }
    }

Tools run with ZERO credentials (mock mode) and automatically switch to the
PayPal sandbox when PAYPAL_CLIENT_ID / PAYPAL_CLIENT_SECRET are present -
the same three-tier contract as the HTTP API (mock -> toolkit -> direct REST).
"""
import json

try:
    from mcp.server import MCPServer as _ServerCls  # mcp 2.x
except ImportError:
    try:
        from mcp.server.fastmcp import FastMCP as _ServerCls  # mcp 1.x
    except ImportError:  # standalone fastmcp distribution
        from fastmcp import FastMCP as _ServerCls

try:
    from . import invoicing, toolkit_bridge
    from . import app as app_module
except ImportError:  # executed as a plain script from the repo root
    import pathlib as _pl
    import sys as _sys
    _sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
    import invoicing, toolkit_bridge
    import app as app_module

mcp = _ServerCls("paypal-bill-agent")


@mcp.tool()
def parse_bills(text: str) -> str:
    """Parse raw bill / payment-reminder text into structured bills (LLM if configured, else rules engine)."""
    bills, source = app_module.parse_bills(app_module.ParseRequest(text=text))
    return json.dumps({"source": source, "bills": [b.model_dump() for b in bills]})


@mcp.tool()
def analyze_risks(bills: list) -> str:
    """Flag overdue / due-soon / large-amount / duplicate risks and compute the total to pay."""
    parsed = [app_module.Bill(**b) for b in bills]
    return json.dumps(app_module.analyze_bills(app_module.AnalyzeRequest(bills=parsed)))


@mcp.tool()
def create_payment_order(bills: list, return_url: str = "") -> str:
    """Create a PayPal order (sandbox) or a mock order (demo mode) for the confirmed bills."""
    parsed = [app_module.Bill(**b) for b in bills]
    currency = parsed[0].currency
    total = round(sum(b.amount for b in parsed), 2)
    if app_module.PAYPAL_CLIENT_ID and app_module.PAYPAL_CLIENT_SECRET:
        order_id, approve_url = app_module.paypal_create_order(parsed, total, currency, return_url or None)
        mode = "sandbox"
    else:
        order_id, approve_url = app_module.mock_create_order(parsed, total, currency)
        mode = "mock"
    return json.dumps({"mode": mode, "order_id": order_id, "approve_url": approve_url, "total": f"{total:.2f}", "currency": currency})


@mcp.tool()
def capture_payment(order_id: str) -> str:
    """Capture a created PayPal order and return the transaction receipt."""
    if app_module.PAYPAL_CLIENT_ID and app_module.PAYPAL_CLIENT_SECRET:
        result = app_module.paypal_capture(order_id)
        mode = "sandbox"
    else:
        result = app_module.mock_capture(order_id)
        mode = "mock"
    result["mode"] = mode
    result["order_id"] = order_id
    return json.dumps(result)


@mcp.tool()
def create_invoice(client_name: str, items: list, client_email: str = "", note: str = "") -> str:
    """Create an invoice for a client (PayPal Invoicing via the official Agent Toolkit in sandbox mode; mock book in demo mode)."""
    req = invoicing.InvoiceCreateRequest(
        client_name=client_name,
        client_email=client_email or None,
        items=[invoicing.InvoiceItem(**it) for it in items],
        note=note or None,
    )
    mode = "sandbox" if (app_module.PAYPAL_CLIENT_ID and app_module.PAYPAL_CLIENT_SECRET) else "mock"
    if mode == "sandbox":
        try:
            return json.dumps(toolkit_bridge.invoice_create(req.model_dump()))
        except Exception:
            return json.dumps(invoicing._sandbox_create(req))
    return json.dumps(invoicing._mock_invoice(req))


@mcp.tool()
def list_invoices() -> str:
    """List invoices in the book (sandbox via Agent Toolkit, demo via mock book)."""
    mode = "sandbox" if (app_module.PAYPAL_CLIENT_ID and app_module.PAYPAL_CLIENT_SECRET) else "mock"
    if mode == "sandbox":
        try:
            return json.dumps(toolkit_bridge.invoice_list({}))
        except Exception:
            pass
    return json.dumps({"mode": mode, "invoices": [
        {k: inv.get(k) for k in ("invoice_id", "status", "amount", "currency")} for inv in invoicing.INVOICES.values()
    ]})


@mcp.tool()
def get_invoice(invoice_id: str) -> str:
    """Fetch one invoice with its payment/reconciliation status."""
    mode = "sandbox" if (app_module.PAYPAL_CLIENT_ID and app_module.PAYPAL_CLIENT_SECRET) else "mock"
    if mode == "sandbox":
        try:
            return json.dumps(toolkit_bridge.invoice_get({"invoice_id": invoice_id}))
        except Exception:
            return json.dumps(invoicing._sandbox_get(invoice_id))
    inv = invoicing.INVOICES.get(invoice_id)
    if not inv:
        return json.dumps({"error": "invoice not found"})
    return json.dumps(inv)


if __name__ == "__main__":
    mcp.run()
