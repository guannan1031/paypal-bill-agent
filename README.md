# AI Bill & Invoice Agent

> **PayPal AI Hackathon 2026 submission** — Agentic Commerce with a human in the loop.
> One agent, two directions of money flow: it **pays your bills** and it **gets you paid**.

## The problem

Freelancers, solo founders and small businesses juggle bills scattered across providers — credit cards, cloud servers, utilities, subscriptions. Due dates are missed, duplicates slip through, large amounts get paid twice. And on the other side of their life, they need to **invoice clients** and chase who has actually paid.

Existing tools make you do the bookkeeping. This agent does the running around.

## What it does

**Direction 1 — Pay bills**
1. Paste raw bills / payment reminders (any messy text format)
2. AI parses them into structured bills (LLM extraction, rules-engine fallback)
3. A risk engine flags: overdue, due soon, large amount, suspected duplicates
4. You explicitly select what to pay — the agent never moves money on its own
5. PayPal **Orders v2**: create order → buyer consent → capture → transaction receipt

**Direction 2 — Get paid**
1. Describe the client and line items
2. Agent drafts a real invoice via PayPal **Invoicing v2** (DRAFT state)
3. You review, then send it
4. Reconcile: who paid, when, which transaction — straight from PayPal records

**Design principle: decision to the AI, execution to PayPal, control stays with the human.**

## Quick start (3 minutes, zero credentials)

```bash
git clone https://github.com/guannan1031/paypal-bill-agent
cd paypal-bill-agent
python -m venv .venv
.venv\Scripts\activate          # Windows  (source .venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
python deploy_run.py            # serves frontend + API on http://127.0.0.1:8878
```

Open `http://127.0.0.1:8878` → **Load sample** → **AI Parse Bills** → select bills →
**Pay with PayPal** → consent screen → receipt.

Without any configuration the app runs in **demo (mock) mode**: the full
create → consent → capture loop is simulated with the exact same API contract,
clearly labeled on every response and in the UI. Judges can evaluate everything
without a single key.

## Connect the real PayPal sandbox (free)

1. Create a developer app at [developer.paypal.com](https://developer.paypal.com) (Sandbox)
2. Set environment variables:

```bash
set PAYPAL_CLIENT_ID=your_sandbox_client_id
set PAYPAL_CLIENT_SECRET=your_sandbox_secret
```

3. Restart. The header badge flips from *demo mode* to *live*; buyer consent now
   happens on PayPal-hosted sandbox pages, and invoices are real sandbox objects.

## Official Agent Toolkit & MCP integration

The sandbox Invoicing surface runs through the official
[paypal-agent-toolkit](https://github.com/paypal/agent-toolkit) (v1.1.0):
OAuth2 client, official parameter models and tool handlers.

One deliberate deviation: the toolkit's `create_invoice` handler **auto-sends**
the invoice right after creating it. We disable that — our product keeps an
explicit `DRAFT → human review → send` step, because an agent that spends and
bills money autonomously is exactly what we don't want to demo. Every toolkit
call is fail-soft: on error the app falls back to direct REST with the same
contract.

`GET /api/agent/capabilities` reports the live integration status.

### Plug the agent into Claude Desktop (MCP)

`backend/mcp_server.py` is a standard MCP **stdio server exposing 7 tools**:

| Tool | What it does |
| --- | --- |
| `parse_bills` | raw text → structured bills (LLM or rules) |
| `analyze_risks` | overdue / due-soon / large-amount / duplicate flags |
| `create_payment_order` | PayPal order (sandbox) or mock order |
| `capture_payment` | capture + transaction receipt |
| `create_invoice` | invoice for a client (Agent Toolkit in sandbox mode) |
| `list_invoices` | invoice book |
| `get_invoice` | one invoice + payment/reconciliation status |

Add to Claude Desktop `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "paypal-bill-agent": {
      "command": "python",
      "args": ["backend/mcp_server.py"],
      "cwd": "<path to this repo>"
    }
  }
}
```

Works with zero credentials (mock tools) and upgrades to the PayPal sandbox
automatically when `PAYPAL_CLIENT_ID` / `PAYPAL_CLIENT_SECRET` are present.

## Architecture

```
                    ┌────────────────────────────────────────────┐
 bills (raw text) → │ parse: LLM (OpenAI-compatible) ──fall back─┤→ rules engine
                    │ risk engine: overdue/due-soon/large/dup    │
                    │ human confirmation (explicit selection)    │
                    ├────────────────────────────────────────────┤
  pay direction     │ Orders v2: create → consent → capture      │
  get-paid          │ Invoicing v2 via Agent Toolkit 1.1.0       │
                    │   (auto-send disabled, DRAFT→review→send)  │
                    ├────────────────────────────────────────────┤
  three-tier        │ sandbox creds? → Agent Toolkit             │
  contract          │   toolkit error? → direct REST             │
                    │   no creds?      → mock (contract-identical)│
                    └────────────────────────────────────────────┘
```

Key endpoints: `POST /api/bills/parse`, `POST /api/bills/analyze`,
`POST /api/pay/prepare`, `POST /api/pay/capture`,
`POST /api/invoices/create|send`, `GET /api/invoices[/{id}]`,
`GET /api/agent/capabilities`, `GET /api/health`.

## Deploy on Render

This repo ships `render.yaml` (Blueprint). On [render.com](https://render.com):
**New → Blueprint → pick this repo** → deploy. Free instance includes cold-start
sleep (~50s first request). Set `PAYPAL_CLIENT_ID` / `PAYPAL_CLIENT_SECRET` as
environment variables for live sandbox mode.

## Tech stack

FastAPI · PayPal Orders v2 + Invoicing v2 · official `paypal-agent-toolkit` 1.1.0 ·
MCP (`mcp` 2.3.0) · httpx · vanilla-JS single-file frontend (no build step) ·
Render Blueprint.

## Data & privacy

No real personal or financial data anywhere — demo bills are synthetic,
credentials are read from environment variables only, and nothing is persisted
beyond the in-memory demo book.

## License

MIT — see [LICENSE](LICENSE).
