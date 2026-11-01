# Demo video script (<3 min) — AI Bill & Invoice Agent
> Winning-pattern structure: hook (15s) -> end-to-end real run (75s) -> tech depth (35s) -> value + close (25s).
> Record 1080p, browser fullscreen, hide bookmarks. Narration clips: assets/narration/*.mp3 (pre-generated TTS).

## 0:00-0:15 Hook (narration 01)
ON SCREEN: empty app, badge shows "PayPal Sandbox - demo mode".
LINE: "Small businesses lose money twice: bills they forget to pay, and clients they forget to bill. This agent closes both directions - on PayPal."

## 0:15-0:45 Bill direction, part 1 (narration 02)
ON SCREEN: click "Load sample" -> "AI Parse Bills". Risk chips appear (red OVERDUE, amber LARGE AMOUNT).
LINE: "Paste any messy bill text. The AI parses it into structured bills, and a risk engine flags what is overdue, what lands in two days, what is suspiciously large or duplicated."

## 0:45-1:15 Bill direction, part 2 (narration 03)
ON SCREEN: select bills, total updates, click "Pay $... with PayPal" -> consent screen -> receipt (COMPLETED, transaction id).
LINE: "I choose what to pay - the agent never moves money on its own. It creates the PayPal order, the buyer consents on PayPal, and the payment is captured. Receipt, transaction id, done."

## 1:15-1:55 Invoice direction (narration 04)
ON SCREEN: switch tab "Get Paid - Invoices" -> Load sample -> Create invoice -> DRAFT row -> Send -> SENT -> Mark paid -> Reconcile view with payment record.
LINE: "Now the other direction. The agent drafts a real PayPal invoice - but it lands as a draft. I review, then it is sent. When the client pays, reconciliation pulls the actual transaction from PayPal. Paying and getting paid, one agent, both auditable."

## 1:55-2:30 Tech depth (narration 05)
ON SCREEN: open /api/agent/capabilities in a second tab; show JSON; flash README MCP config; mention toolkit name on screen.
LINE: "Under the hood: PayPal Orders v2 plus Invoicing v2 through the official PayPal Agent Toolkit. One deliberate design choice - the toolkit auto-sends invoices, we disabled that, control stays with the human. The same agent speaks MCP: seven tools, connectable from Claude Desktop. And a three-tier contract - sandbox toolkit, direct REST fallback, and a mock mode with zero credentials, so you can run everything you just saw offline."

## 2:30-2:55 Close (narration 06)
ON SCREEN: back to app, show badge + repo URL + Devpost link.
LINE: "Decision to the AI, execution to PayPal, control to the human. Try the live demo, or run it from the repo in three minutes. AI Bill and Invoice Agent."

## Recording checklist
- [ ] Prefer live sandbox mode (creds set) - else demo mode, badge visible, honesty is fine
- [ ] Wake Render 50s before recording the hosted URL shot (or record localhost)
- [ ] 1920x1080, browser zoom 100%, clean profile
- [ ] Record segments separately, cut on narration boundaries
- [ ] End frame: repo URL + Devpost project link, 5s hold
