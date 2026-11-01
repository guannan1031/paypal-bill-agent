# Devpost submission copy — AI Bill & Invoice Agent
> Fill the Devpost form with the text below. Placeholders: [HOSTED_URL], [VIDEO_URL].

## Project title
AI Bill & Invoice Agent — pay bills & get paid with PayPal, human-in-the-loop

## Tagline
One agent for both directions of your money flow: AI parses your bills and pays them via PayPal, then invoices your clients and reconciles who paid.

## The story (Inspiration)
Freelancers and small-business owners juggle bills scattered across providers — missed due dates, accidental duplicates, scary large amounts — and on the other side they must invoice clients and chase payments. Existing tools are bookkeeping dashboards that still make you do everything. We asked: what if an agent did the running around, while a human keeps the trigger?

## What it does
- Paste messy bill text → AI parses structured bills (LLM with rules-engine fallback)
- Risk engine flags overdue / due-soon / large-amount / duplicates before any money moves
- You explicitly select bills → agent executes PayPal Orders v2 (create → consent → capture → receipt)
- Second direction: create invoices via PayPal Invoicing v2, review as DRAFT, send, then reconcile payments straight from PayPal records
- Three-tier contract: mock (zero credentials) → official Agent Toolkit (sandbox) → direct REST (fallback) — the demo never breaks

## How we built it
FastAPI backend; PayPal Orders v2 and Invoicing v2; official paypal-agent-toolkit 1.1.0 for the sandbox invoicing surface; an MCP stdio server (7 tools) so the same agent can be driven from Claude Desktop; a no-build vanilla-JS frontend; render.yaml Blueprint for hosting.

## Challenges
- The official toolkit's create_invoice auto-SENDS the invoice; we deliberately disabled that to keep DRAFT → human review → send, because an agent that bills autonomously is the failure mode we're arguing against.
- Making the full payment loop evaluable without credentials: mock mode mirrors the real API contract exactly, so judges can run everything offline.

## Accomplishments we're proud of
- A complete two-way money flow demo that runs end-to-end in under 3 minutes with zero setup
- MCP integration: judges can connect the agent to Claude Desktop and drive it conversationally
- Fail-soft architecture: toolkit errors transparently fall back to direct REST

## What we learned
Consent UX is the product. The moment real money is involved, the differentiator is not model quality but how visibly the human stays in control.

## What's next
Recurring bills & subscription awareness, multi-currency consolidation, an Arabic/English locale pack for UAE SMEs entering mandatory e-invoicing, and dispute-aware risk scoring.

## Links
- GitHub: https://github.com/guannan1031/paypal-bill-agent
- Hosted demo: [HOSTED_URL]
- Video (YouTube, <3 min): [VIDEO_URL]

## Tools used
PayPal Orders API (v2), PayPal Invoicing API (v2), PayPal Developer Sandbox, paypal-agent-toolkit (official, 1.1.0), Model Context Protocol (mcp 2.3.0), FastAPI, Python 3.13, httpx, Render (Blueprint), GitHub.
