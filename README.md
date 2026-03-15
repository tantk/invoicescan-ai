# InvoiceScan AI

**Point your phone at any invoice. The AI reads it, verifies the tax, catches fraud, logs it to Google Sheets, and talks to you about it — in real time.**

Works with invoices from 57 countries. Gets smarter with every scan through user-created recipes.

## The Big Idea — Every Scan Is Training Data

The real purpose of InvoiceScan AI is **data collection for Document AI uptraining**. The voice agent, recipes, and community sharing are all designed to make users scan invoices naturally — and every scan generates labeled training data as a side effect.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    THE SELF-IMPROVING FLYWHEEL                      │
│                                                                     │
│   User scans invoice (they get value — tax verified, logged, etc.)  │
│       │                                                             │
│       ▼                                                             │
│   Document AI extracts 46 fields (Layer 1 — fast, grounded)        │
│       │                                                             │
│       ▼                                                             │
│   Gemini Vision extracts custom fields via recipes (Layer 2)        │
│       │                                                             │
│       ├── User says nothing ──► implicit approval (labeled sample)  │
│       └── User corrects it ──► even better label                    │
│               │                                                     │
│               ▼                                                     │
│       50+ approved samples for a field                              │
│               │                                                     │
│               ▼                                                     │
│       Trigger Document AI uptraining                                │
│               │                                                     │
│               ▼                                                     │
│   Field GRADUATES: Layer 2 (Gemini, flexible)                       │
│                  → Layer 1 (Document AI, grounded + fast)           │
│               │                                                     │
│               ▼                                                     │
│   Document AI gets better → fewer fields need Gemini Vision         │
│               │                                                     │
│               └──────────────── cycle repeats ──────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

**Community recipes accelerate this.** When one user creates a recipe that works, other users subscribe to it. Now that recipe runs across dozens of users' invoices — generating training data 10x faster than a single user could.

The end state: Document AI handles everything. Gemini Vision is only needed for truly novel field types. The system trains itself out of needing the expensive model.

## Quick Start

```bash
# 1. Set up credentials
gcloud auth application-default login
cp server/.env.example server/.env   # fill in your config

# 2. Start server
cd server && pip install -r requirements.txt && python main.py

# 3. Open on phone (HTTPS required for mic/camera)
https://your-host:8002
```

## What It Does

1. **Scan** — Snap a photo or upload an invoice
2. **Extract** — Document AI pulls 46 standard fields (vendor, total, tax, line items, dates)
3. **Verify** — Background: tax math checked against 57 country regimes with historical rates
4. **Catch Problems** — Duplicates, wrong tax, missing fields, suspicious amounts — all automatic
5. **Log** — Auto-added to Google Sheets with dynamic columns
6. **Talk** — Voice conversation via Gemini Live: "is this claimable?", "what's the total?"
7. **Recipes** — Create custom extraction recipes that auto-run on future invoices
8. **Share** — Subscribe to community recipes from Firestore so everyone benefits

## System Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                            PHONE / BROWSER                              │
│                                                                          │
│   ┌──────────┐  ┌──────────────────────┐  ┌───────────────────┐         │
│   │   Mic    │  │  Camera (snap)       │  │  Cookie: user_id  │         │
│   │ (toggle) │  │  or Upload (file)    │  │  (persistent ID)  │         │
│   └────┬─────┘  └────┬─────────────────┘  └───────────────────┘         │
│        │              │                                                  │
│        │              ├──────────────────────────────┐                   │
│        │              │ BOTH paths fire in parallel  │                   │
│        │              │                              │                   │
│   ┌────▼──────────────▼──┐               ┌───────────▼──────────────┐   │
│   │  Gemini Live WS      │               │  REST /api/upload        │   │
│   │  (direct, no proxy)  │               │  + user_id query param   │   │
│   │  Instant visual read │               │  Document AI processing  │   │
│   └────┬────────────┬────┘               └───────────┬──────────────┘   │
│        │            │                                │                   │
└────────┼────────────┼────────────────────────────────┼──────────────────┘
         │            │                                │
   ══════▼════════    │                          ══════▼══════════════════
   GEMINI LIVE API    │                          FASTAPI SERVER (Cloud Run)
   (Google Cloud)     │                          ════════════════════════
                      │                                │
   ┌──────────────┐   │          ┌─────────────────────▼──────────────┐
   │ Voice in/out │   │          │  Upload Pipeline (every scan)      │
   │ Image vision │   │          │                                    │
   │ Transcription│   │          │  1. Document AI ──► 46 fields     │
   │              │   │          │  2. Fraud check ──► 7 checks      │
   │  ┌────────┐  │   │          │  3. Google Sheets ──► auto-log    │
   │  │ Tools: │  │   │          │  4. Vertex Search ──► indexed     │
   │  │ manage │──┼───┘          │  5. Regime detection              │
   │  │ recipes│  │              │                                    │
   │  └────────┘  │              │  Background (async):              │
   └──────────────┘              │  ├── Tax math verification        │
         │                       │  ├── Confidence escalation        │
         │  tool call            │  ├── Compliance validation        │
         │                       │  └── Recipe auto-run ─────────┐   │
   ┌─────▼──────────┐           └────────────────────────────────┼───┘
   │ POST /api/tool │                                            │
   │ manage_recipes │                                            │
   └─────┬──────────┘                                            │
         │                                                       │
   ══════▼═══════════════════════════════════════════════════════▼═══
   FIRESTORE                          GOOGLE SHEETS
   ═════════════════════════          ═════════════════════════
   │                       │          │                       │
   │  recipes/{id}         │          │  Invoices sheet       │
   │  ├── name             │          │  ├── 46+ dynamic cols │
   │  ├── extraction_prompt│          │  ├── Recipe columns   │
   │  ├── trigger_regime   │          │  ├── Remarks          │
   │  ├── score, times_used│          │  └── Analysis column  │
   │  └── created_by       │          │                       │
   │                       │          │  Line Items sheet     │
   │  users/{user_id}      │          │  Tax Breakdown sheet  │
   │  └── recipe_ids: [...]│          │                       │
   │                       │          │                       │
   └───────────────────────┘          └───────────────────────┘
```

### Data Flow — Snap a Photo (Both Paths Fire Simultaneously)

```
User taps camera → ONE photo, TWO parallel paths:

PATH 1 — Instant (< 1 second)                PATH 2 — Thorough (2-5 seconds)
─────────────────────────────                 ────────────────────────────────
Photo → Gemini Live WebSocket                Photo → Server /api/upload
Gemini sees image immediately                 │
Speaks: "Acme Inc, twelve fifty"              ├── Document AI → 46 fields
                                              ├── Fraud check → 7 checks
                                              ├── Google Sheets → auto-log
                                              ├── Vertex Search → indexed
                                              └── Grounding → sent to Gemini
                                                   (only if flags: duplicate,
                                                    fraud, tax mismatch)

                                              Background (async, 5-15 seconds):
                                              ├── Tax math verification
                                              ├── Confidence escalation
                                              ├── Compliance validation
                                              ├── Recipe auto-run
                                              └── Results → Analysis column
```

### Data Flow — Upload a File (Document AI First)

```
User picks file → Server gets it FIRST:

1. Server /api/upload
   ├── Document AI → 46 fields
   ├── Fraud check, Sheets, Search
   └── Grounding text built

2. Image + grounding sent to Gemini together
   Gemini speaks with grounded data (more accurate than visual read)

3. Background analysis runs same as snap
```

### Data Flow — Create a Recipe

```
1. User: "Extract the PO number from invoices"
2. Gemini calls manage_recipes(action: "create", name: "po_number",
                               extraction_prompt: "Find the purchase order number...")
3. Server saves to Firestore → user auto-subscribed
4. User: "Test it on this invoice"
5. Gemini calls manage_recipes(action: "test", name: "po_number", invoice_id: "abc123")
6. Server runs Gemini Vision with the prompt → returns extracted fields
7. Next upload → server finds matching recipe → auto-runs → results in Sheets
```

### Three-Layer Extraction

| Layer | Engine | Fields | When |
|-------|--------|--------|------|
| **1** | Document AI | 46 standard fields | Every upload (automatic) |
| **2** | Gemini Vision | 228+ custom fields (16 industry presets) | Via recipes |
| **3** | Community Recipes | User-created extraction prompts | Auto-matched by regime/industry |

### Dual Processing Flow

| Flow | Trigger | Sequence |
|------|---------|----------|
| **A** (Upload) | File picker / long press | Document AI first → image + grounding sent to Gemini together |
| **B** (Snap) | Camera tap | Gemini sees image first (quick read) → Document AI grounding arrives later |

## Gemini Live Agent — 1 Tool

The voice agent has a single tool: `manage_recipes`. Everything else runs automatically.

### manage_recipes(action, ...)

| Action | What | When |
|--------|------|------|
| `create` | Save a new recipe with extraction prompt + triggers | User teaches the agent |
| `test` | Run recipe against current invoice, show results | User verifies it works |
| `list` | Show user's subscribed recipes | User asks "what recipes do I have?" |
| `delete` | Remove recipe (creator deletes, others unsubscribe) | User cleanup |
| `search` | Find community recipes by regime/industry | Discovery |
| `subscribe` | Add existing recipe to user's list | Adopt community recipe |
| `unsubscribe` | Remove from user's list | Stop auto-running a recipe |

### What Runs Automatically (no tool needed)

- Document AI extraction (46 fields)
- Tax regime detection (57 countries)
- Tax math verification
- Fraud/duplicate detection (7 checks)
- Compliance validation
- Matching recipe auto-run
- Google Sheets logging
- Vertex AI Search indexing

## Recipes (Firestore)

Recipes are custom Gemini Vision prompts stored in Firestore. Each user subscribes to the recipes they want.

```
Firestore:
  recipes/{recipe_id}     ← shared, global
    name, extraction_prompt, triggers, score, times_used

  users/{user_id}          ← per-user subscriptions
    recipe_ids: ["abc", "def", ...]
```

**Create flow:**
```
"Extract the PO number from this invoice"
  → Agent creates recipe with extraction prompt
  → Tests against current invoice
  → Saved to Firestore, auto-subscribed
  → Auto-runs on future matching invoices
```

**Community flow:**
```
User A creates "japan_split_tax" recipe → works well → score rises
User B: "find recipes for Japanese invoices" → agent searches Firestore
  → finds User A's recipe → User B subscribes
  → auto-runs for User B on future Japanese invoices
```

## Post-Processing (Background)

After every upload, a background task runs and writes results to the **Analysis** column in Sheets:

| Check | What |
|-------|------|
| Tax math verification | Recalculates tax, flags mismatches |
| Confidence escalation | Low-confidence fields re-read by Gemini Vision |
| Compliance validation | Checks mandatory fields for detected regime |
| Recipe auto-run | Runs matching user recipes, saves results |
| Fraud detection | Duplicates, bank changes, suspicious amounts |

## 57 Countries

**Americas:** US, Canada, Mexico, Brazil, Argentina, Chile, Peru, Colombia, Ecuador, Costa Rica, Uruguay

**Europe:** EU, UK, Germany, France, Italy, Spain, Netherlands, Sweden, Switzerland, Poland, Romania, Denmark, Norway, Finland, Hungary, Czech Republic, Israel

**Middle East & Africa:** Saudi Arabia, UAE, Bahrain, Oman, Egypt, Nigeria, Kenya, South Africa, Ghana, Tanzania, Morocco

**Asia-Pacific:** India, Japan, China, Australia, New Zealand, Singapore, Malaysia, Thailand, Indonesia, Vietnam, South Korea, Taiwan, Philippines, Pakistan, Bangladesh, Sri Lanka, Hong Kong

Each country has: tax regime detection, historical rate tracking, compliance rules, and a detailed tax guide in `data/tax_guides/`.

## Google Sheets (Dynamic)

Every scan is auto-logged. Columns create themselves as new field types appear:

- **Invoices** — one row per invoice, all fields + Recipe columns + Remarks + Analysis
- **Line Items** — one row per line item
- **Tax Breakdown** — VAT rate details

## Fraud Detection (7 checks)

| Check | What It Catches |
|-------|----------------|
| Exact duplicate | Same invoice # + same vendor |
| Near duplicate | Same amount + vendor within 30 days |
| Suspicious amount | Same amount from different vendors |
| Bank change | Vendor's bank details changed |
| Round number | Exact round amounts ($10,000) |
| Weekend date | Invoice dated Saturday/Sunday (for corporate) |
| Sequence gap | Missing invoice numbers |

## History View

Tap the clock icon to see all scanned invoices with bounding box overlays:
- Color-coded by field type (vendor=blue, total=green, tax=red)
- Tap individual fields to toggle highlight
- Show All / Hide All buttons
- Dashed lines for Gemini-approximated boxes

## Project Structure

```
invoicescan-ai/
├── server/
│   ├── main.py                          # FastAPI + REST + /api/tool endpoint
│   ├── Dockerfile                       # Cloud Run deployment
│   ├── invoice_agent/
│   │   ├── agent.py                     # Agent builder (ADK)
│   │   ├── prompts.py                   # System instructions
│   │   ├── config.py                    # All configuration
│   │   ├── recipe_mcp.py               # Firestore recipes (manage_recipes tool)
│   │   └── tools/
│   │       ├── invoice_parser.py        # Document AI (Layer 1)
│   │       ├── custom_extractor.py      # Gemini Vision (Layer 2, 16 presets)
│   │       ├── tax_engine.py            # 57 regimes + historical rates
│   │       ├── fraud_detector.py        # 7 fraud checks
│   │       ├── smart_extraction.py      # Confidence escalation
│   │       ├── sheets.py               # Google Sheets (3 sheets + analysis)
│   │       ├── search_store.py          # Vertex AI Search
│   │       └── currency.py              # Exchange rate conversion
│   └── static/                          # Web app (mobile-first)
│       ├── js/app.js                    # Main app + tool dispatch
│       ├── js/websocket.js              # Direct Gemini Live connection
│       ├── js/scanner.js                # Camera + upload
│       ├── js/audio.js                  # Mic recording + playback
│       └── history.html                 # Invoice history + bounding boxes
├── desktop/                             # Desktop viewfinder app
├── data/
│   ├── tax_guides/                      # 64 country guides
│   └── demo_invoices/                   # Demo invoices
├── scripts/
│   ├── deploy_cloudrun.sh
│   └── setup_vertex_search.py
└── start.bat                            # Start server + desktop
```

## Google Cloud Services

| Service | Purpose |
|---------|---------|
| Gemini 2.5 Flash (Live API) | Voice + vision agent |
| Document AI | Invoice Parser (Layer 1) |
| Vertex AI Search | RAG over past invoices |
| Google Sheets API | Auto-log invoices |
| Firestore | User recipes + subscriptions |
| Cloud Run | Serverless deployment |

## Setup (Full Spin-Up)

### Prerequisites
- Python 3.11+
- Google Cloud account with billing enabled
- `gcloud` CLI installed

### Step 1: Clone and configure

```bash
git clone https://github.com/tantk/invoicescan-ai.git
cd invoicescan-ai
cp .env.example server/.env
```

Edit `server/.env` with your values:

```env
# Required — browser uses this to connect directly to Gemini Live
GEMINI_API_KEY=your-gemini-api-key

# Required for Document AI, Sheets, Search, Firestore
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=us-central1
```

### Step 2: GCP authentication

```bash
gcloud auth application-default login
gcloud config set project your-gcp-project-id
```

### Step 3: Create GCP resources

**Gemini API Key** (for browser → Gemini Live):
- Go to [Google AI Studio](https://aistudio.google.com/apikey)
- Create an API key → paste into `GEMINI_API_KEY` in `.env`

**Document AI** (invoice extraction):
- Go to [Document AI Console](https://console.cloud.google.com/ai/document-ai)
- Create an **Invoice Parser** processor in `us` region
- Copy processor ID → paste into `DOCAI_PROCESSOR_ID` in `.env`

**Google Sheets** (auto-logging):
- Create a blank Google Sheet
- Share it with your ADC email (or service account)
- Copy the spreadsheet ID from the URL → paste into `SHEETS_SPREADSHEET_ID`

**Firestore** (recipes):
- Go to [Firestore Console](https://console.cloud.google.com/firestore)
- Create database in `(default)` mode (Native)
- No collections needed — they auto-create on first recipe

**Vertex AI Search** (optional — semantic search over past invoices):
```bash
python scripts/setup_vertex_search.py
# Paste the data store ID and engine ID into .env
```

### Step 4: Install and run

```bash
cd server
pip install -r requirements.txt
python main.py
```

Server starts on:
- `http://localhost:8002` (or HTTPS if Tailscale certs are present)
- `http://localhost:8003` (HTTP fallback)

### Step 5: Access

- **Desktop:** Open `http://localhost:8002` in Chrome
- **Phone:** You need HTTPS for mic/camera. Options:
  - Use [Tailscale](https://tailscale.com/) for automatic HTTPS certs
  - Use `ngrok` or similar tunnel
  - Deploy to Cloud Run (see below)

### HTTPS for mobile (Tailscale)

```bash
# Install Tailscale, then:
tailscale cert your-hostname.ts.net
# Place cert and key in server/ directory
# Server auto-detects *.crt and *.key files
```

## Deploy to Cloud Run

```bash
export GEMINI_API_KEY=your-gemini-api-key
cd scripts && bash deploy_cloudrun.sh
```

The deploy script:
1. Builds container with Cloud Build
2. Deploys to Cloud Run with all env vars
3. Prints the service URL

The API key is passed as a Cloud Run environment variable — never in code. The server exposes `/api/config` which the browser fetches on page load.

### Cloud Run env vars set by the deploy script:
- `GEMINI_API_KEY` — browser Gemini connection
- `GOOGLE_CLOUD_PROJECT` — GCP project
- `DOCAI_PROCESSOR_ID` — Document AI processor
- `SHEETS_SPREADSHEET_ID` — Google Sheets
- `VERTEX_SEARCH_DATA_STORE_ID` / `VERTEX_SEARCH_ENGINE_ID` — search (optional)
