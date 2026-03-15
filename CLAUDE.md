# InvoiceScan AI — Project Instructions

## What This Is
A voice-powered invoice scanner for family business use. Users scan invoices from phone or desktop. A Gemini Live agent analyzes, verifies tax, detects fraud/duplicates, converts currencies, and logs to Google Sheets. 57 countries, user-created extraction recipes shared via Firestore.

## Running
```bash
# Server (HTTPS via Tailscale for mobile mic/camera)
cd server && python main.py  # https://titan.tail2e1adb.ts.net:8002

# Desktop app (optional)
cd desktop && python main.py  # F2=Talk, F3=Scan, ESC=Quit

# Both at once (Windows)
start.bat
```

## GCP Config
- Project: set in `server/.env` → `GOOGLE_CLOUD_PROJECT`
- Document AI: set in `server/.env` → `DOCAI_PROCESSOR_ID`
- Vertex AI Search: set in `server/.env` → `VERTEX_SEARCH_DATA_STORE_ID` / `VERTEX_SEARCH_ENGINE_ID`
- Sheets: set in `server/.env` → `SHEETS_SPREADSHEET_ID`
- Firestore: `(default)` database, `recipes` + `users` collections
- API Key: via `GEMINI_API_KEY` env var (never hardcoded)

## Architecture

### Direct Gemini Live Connection
Browser connects directly to Gemini Live API via WebSocket for low-latency audio. Server handles REST endpoints only (upload, tool dispatch, config).

```
Phone ──WebSocket──► Gemini Live API (direct, low latency)
                         │
                    tool call? → POST /api/tool/manage_recipes → Server → Firestore
                         │
                    ◄── Gemini speaks result

Phone ──REST──► Server /api/upload
                    │
               DocAI → Sheets → Search
                    │
               [background] tax verify + confidence + compliance + recipe auto-run
                    │
               → Analysis column in Sheets
```

### Agent Tool — 1 tool only
The Gemini Live agent has one tool: `manage_recipes` with actions: create, test, list, delete, search, subscribe, unsubscribe.

Everything else runs automatically on upload:
- Document AI extraction (46 fields)
- Tax regime detection (57 countries)
- Fraud/duplicate detection
- Google Sheets logging
- Vertex AI Search indexing
- Background: tax verification, confidence check, compliance, recipe auto-run

### Firestore Recipe System
```
recipes/{recipe_id}     ← shared, global
  name, extraction_prompt, triggers, created_by, score, times_used

users/{user_id}          ← per-user subscriptions
  recipe_ids: ["abc", "def", ...]
```
- Users create recipes via voice → saved to Firestore
- Users subscribe to community recipes → auto-run on matching uploads
- Usage stats tracked (implicit voting via success/failure)

### Dual Processing Flow
**Flow B (Snap):** Gemini sees image first → quick visual read → Document AI grounding arrives later
**Flow A (Upload):** Document AI first → image + grounding sent to Gemini together

### Three-Layer Extraction
- **Layer 1**: Document AI (46 fields, grounded, always runs)
- **Layer 2**: Gemini Vision (228+ custom fields via 16 presets, via recipes)
- **Layer 3**: Community Recipes (Firestore, user-created, auto-matched)

### Voice & Audio
- Mic is a **toggle** (tap on/off), not push-to-talk
- Gemini Live API has built-in VAD — detects speech/silence automatically
- Audio resampled from browser native rate (44.1/48kHz) to 16kHz for Gemini
- Auto-reconnect on Live API crash (3 retries)

### User Identity
- Browser generates UUID on first visit, stored in cookie (`invoicescan_uid`)
- Sent with all uploads and tool calls
- Used for Firestore recipe ownership and subscriptions
- Persists across Cloud Run deploys (cookie is client-side)

### Post-Processing (Background)
After upload, a background task runs: tax math verification, confidence escalation, compliance validation, and recipe auto-run. Results written to Analysis column in Sheets.

## Key Files
| File | What |
|------|------|
| `server/main.py` | FastAPI + REST + /api/tool endpoint + background analysis |
| `server/invoice_agent/agent.py` | Agent builder (ADK) |
| `server/invoice_agent/prompts.py` | System prompt (1 tool: manage_recipes) |
| `server/invoice_agent/config.py` | Model config, GCP settings |
| `server/invoice_agent/recipe_mcp.py` | Firestore recipes: manage_recipes tool + auto-run pipeline |
| `server/invoice_agent/tools/tax_engine.py` | 57 regimes, historical rates, 8 industry detectors |
| `server/invoice_agent/tools/custom_extractor.py` | 16 presets, 228+ fields, Gemini Vision |
| `server/invoice_agent/tools/fraud_detector.py` | 7 fraud checks, duplicate detection |
| `server/invoice_agent/tools/smart_extraction.py` | Confidence escalation, XML parsing |
| `server/invoice_agent/tools/sheets.py` | Google Sheets (3 dynamic sheets + analysis column) |
| `server/invoice_agent/tools/search_store.py` | Vertex AI Search ingestion |
| `server/static/js/app.js` | Main app: tool dispatch, mic toggle, thumbnail queue |
| `server/static/js/websocket.js` | Direct Gemini Live WebSocket + tool declarations |
| `server/static/js/scanner.js` | Camera viewfinder, snap capture, file upload |
| `server/static/js/audio.js` | Audio recording (16kHz resample) + playback |
| `server/static/history.html` | Invoice history with bounding box overlays |

## Adding a New Country
1. Create `data/tax_guides/{country}_{tax}.md`
2. Add `TaxRegime` entry in `tools/tax_engine.py` → `TAX_REGIMES`
3. Add `RATE_HISTORY` entry if rate has changed historically
4. Add currency mapping in `_detect_regime_from_currency()`
5. Add field detection in `_detect_regime_from_fields()` if distinctive patterns exist
6. Run `python scripts/ingest_tax_guides.py` to update Vertex AI Search

## Adding a New Industry
1. Add to `INDUSTRY_MARKERS` in `tools/tax_engine.py`
2. Add preset to `INDUSTRY_FIELDS` in `tools/custom_extractor.py`

## Deploy
```bash
export GEMINI_API_KEY=your_key
cd scripts && bash deploy_cloudrun.sh
```
