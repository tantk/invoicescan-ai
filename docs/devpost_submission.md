# Devpost Submission — InvoiceScan AI

## Title
InvoiceScan AI — Voice-Powered Invoice Scanner with Global Tax Intelligence

## Tagline
Scan any invoice from any country. Talk to it. Trust it.

---

## Inspiration

Document AI is powerful but limited to 46 standard fields. Every industry, every country has fields it doesn't know about — PO numbers, project codes, HSN codes, split tax rates, retainage percentages. Training Document AI to extract new fields requires manually labeled samples. Lots of them.

My family runs a small business. Every month, we process invoices from suppliers across different countries. I realized: if I build an app that people actually want to use for their daily invoice scanning, every scan generates labeled training data — for free. Users get value (tax verification, fraud detection, auto-logging), and the system collects the samples it needs to improve Document AI.

The voice agent, the recipes, the community sharing — they're not just features. They're a data collection flywheel disguised as a useful product.

## What it does

InvoiceScan AI is a **voice-powered invoice scanning agent** — but its real purpose is **automated data collection for Document AI uptraining**.

**What the user sees:**
1. **Scan** — Snap a photo, hear the vendor and total instantly via Gemini Live
2. **Verify** — Tax math checked against 57 country regimes with historical rates
3. **Catch fraud** — 7 automated checks: duplicates, bank changes, suspicious amounts
4. **Log** — Auto-added to Google Sheets with dynamic columns
5. **Talk** — Voice conversation: "is this claimable?", "is the tax right?"
6. **Recipes** — "Always extract the PO number" → agent creates a recipe, auto-runs forever
7. **Share** — Subscribe to community recipes from Firestore

**What the system is actually doing:**
1. **Collecting labeled samples** — Every Gemini Vision extraction is an implicit training sample. User doesn't correct it = approved label. User corrects it = even better label.
2. **Scaling via community** — When one user's recipe runs across all subscribers' invoices, training data accumulates 10x faster.
3. **Graduating fields** — At 50+ approved samples with 85%+ accuracy, a field can be uptrained into Document AI — moving from Layer 2 (Gemini, slow, expensive) to Layer 1 (Document AI, fast, grounded).
4. **Self-improving** — The more people use it, the fewer fields need Gemini Vision. The end state: Document AI handles everything.

## How we built it

### Direct Gemini Live — No Proxy

The browser connects **directly** to Gemini Live API via WebSocket. Audio and images go straight from phone to Gemini — no server in the middle. This gives us sub-second voice latency. The server only handles REST: uploads, Document AI, Sheets, tool dispatch.

```
Phone ──WebSocket──► Gemini Live API (voice + vision, direct)
  │                       │
  │                  tool call ──► Server ──► Firestore
  │
  └──── upload ────► Server ──► Document AI ──► Sheets
                                    │
                              [background]
                              tax verify + fraud + recipes
                                    │
                              Analysis column in Sheets
```

### 1 Tool, Everything Else Automatic

We optimized from 14 tools down to **1 tool** on the Gemini Live agent: `manage_recipes`. Everything else runs automatically on upload — no agent intervention needed.

**Automatic pipeline (on every upload):**
- Document AI extraction (46 fields)
- Tax regime detection (57 countries)
- Fraud detection (7 checks)
- Google Sheets logging
- Vertex AI Search indexing

**Background post-processing:**
- Tax math verification against historical rates
- Low-confidence field escalation to Gemini Vision
- Compliance validation
- Auto-run matching user recipes from Firestore

This means the agent can focus on conversation — it doesn't waste turns on infrastructure. When the user asks "is the tax right?", the answer is already in the Analysis column.

### Three-Layer Extraction

| Layer | Engine | What | When |
|-------|--------|------|------|
| **1** | Document AI | 46 standard fields, bounding boxes, confidence scores | Every upload |
| **2** | Gemini Vision | 228+ custom fields across 16 industry presets | Via recipes |
| **3** | Community Recipes | User-created extraction prompts, shared via Firestore | Auto-matched |

### Firestore Recipe System

Recipes are the learning mechanism. When the default extraction misses something:

1. User says "extract the PO number" via voice
2. Agent creates a recipe (Gemini Vision prompt) and saves to Firestore
3. Tests it against the current invoice — user confirms it works
4. Recipe auto-runs on all future matching invoices
5. Other users can discover and subscribe to the recipe

Each user has their own subscription list (`users/{user_id}/recipe_ids`). Recipes track usage stats — score rises with successful extractions, falls on failures.

### Tech Stack

- **AI:** Gemini 2.5 Flash Live (native audio + vision, direct browser WebSocket)
- **Extraction:** Google Document AI Invoice Parser
- **Custom Fields:** Gemini Vision (structured JSON, 16 industry presets)
- **Recipes:** Cloud Firestore (per-user subscriptions, community sharing)
- **Search:** Vertex AI Search (semantic search over past invoices)
- **Logging:** Google Sheets API (3 dynamic sheets + Analysis column)
- **Backend:** FastAPI on Cloud Run
- **Frontend:** Mobile-first HTML/CSS/JS (camera, mic, thumbnail queue, history view)

## Challenges we ran into

1. **14 tools was too many.** Gemini Live wasted turns calling tools that already ran automatically (parse_invoice on data that was already parsed). We iterated down to 1 tool by moving everything to the server pipeline and background processing. Less is more.

2. **Tax complexity is insane.** India has compound taxes (cess on top of CGST+SGST). Brazil has 5 overlapping taxes. US has state+county+city. Hotels can have 20+ line items with different rates. We built a detection engine with 57 regimes and historical rate tracking.

3. **Historical rates matter.** A 2023 Singapore invoice at 8% GST is correct — the rate changed to 9% in January 2024. Our engine checks the invoice DATE, not today's rate. We track rate change history for every regime.

4. **Recipes replaced three systems.** We originally had separate systems for field learning, local recipes, and community recipes. After iteration, we realized they all do the same thing: store a prompt, run it on matching invoices. One Firestore collection with user subscriptions replaced all three.

5. **API key in client-side JS.** The browser connects directly to Gemini — it needs the API key. We solved this with a `/api/config` endpoint that serves the key from an environment variable. Never in code, never in git history.

## Accomplishments that we're proud of

- **57 countries** with tax regime detection, historical rate verification, and compliance checking
- **1 tool** on the voice agent — everything else is automatic. Clean, fast, no wasted turns
- **Sub-second voice response** via direct browser-to-Gemini WebSocket (no server proxy for audio)
- **Recipe system** where users teach the AI via voice and it remembers forever (Firestore-persistent)
- **Community sharing** — one user's recipe benefits everyone who subscribes
- **7 fraud checks** running automatically on every upload
- **Dynamic Google Sheets** that handle any invoice format without schema changes
- **History view** with Document AI bounding box overlays — tap any field to highlight it on the invoice image

## What we learned

- **Fewer tools = better agent.** Going from 14 to 1 tool made the agent faster, more accurate, and more conversational. The agent should talk, not orchestrate infrastructure.
- **Automate everything you can.** If the server can do it on upload, don't make the agent call a tool for it. Tax verification, fraud detection, compliance — all background tasks now.
- **Recipes > field learning.** A recipe is just a prompt with triggers. It subsumes field learning, custom extraction, and community sharing into one concept. Users understand "recipe" intuitively.
- **Direct WebSocket matters.** Proxying audio through our server added 200-400ms latency. Direct browser-to-Gemini eliminated it. The voice experience went from "okay" to "wow."
- **Global tax is an opportunity.** The harder the invoice, the more value the AI adds. A US sales tax invoice is easy. A Brazilian nota fiscal with ICMS + IPI + PIS + COFINS is where the agent really shines.

## What's next for InvoiceScan AI

- **Accounting integrations** — QuickBooks, Xero, FreshBooks via MCP servers for automatic bookkeeping
- **Multi-invoice analysis** — "How much did I spend on office supplies this quarter?" across all scanned invoices
- **E-invoicing validation** — verify against Peppol, ZATCA, CFDI, FatturaPA standards
- **Recipe marketplace** — browse and subscribe to popular recipes by country/industry
- **Offline scanning** — PWA with camera capture, sync recipes and results when connected

## Built With

- gemini-live-api
- gemini-2.5-flash
- google-document-ai
- google-cloud-firestore
- vertex-ai-search
- google-cloud-run
- google-sheets-api
- fastapi
- python
- javascript

---

## GCP Services Used

| Service | Purpose |
|---------|---------|
| Gemini 2.5 Flash (Live API) | Voice + vision agent (direct browser WebSocket) |
| Document AI | Invoice Parser — 46 field extraction with bounding boxes |
| Cloud Firestore | Recipe storage + user subscriptions |
| Vertex AI Search | Semantic search over past invoices |
| Google Sheets API | Auto-log invoices (3 dynamic sheets) |
| Cloud Run | Serverless deployment |
