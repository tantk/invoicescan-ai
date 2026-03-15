# InvoiceScan AI — Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  FRONTENDS                                                       │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐    │
│  │ Web (mobile) │  │ Web (desktop)│  │ Desktop Viewfinder  │    │
│  │ Camera scan  │  │ File upload  │  │ F2=Talk F3=Scan     │    │
│  └──────┬──────┘  └──────┬───────┘  └──────────┬──────────┘    │
│         └────────────────┼──────────────────────┘               │
│                          │                                       │
│                   REST + WebSocket                               │
└──────────────────────────┼───────────────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────────────┐
│  FASTAPI SERVER (Cloud Run)                                      │
│                                                                   │
│  POST /api/upload ──────────────────────────────────────────┐    │
│  │                                                           │    │
│  │  Step 1: Document AI (Layer 1)                            │    │
│  │          46 standard fields + confidence scores           │    │
│  │                                                           │    │
│  │  Step 2: Fraud check (before Sheets)                      │    │
│  │          Duplicate? → block from Sheets                   │    │
│  │                                                           │    │
│  │  Step 3: IN PARALLEL ─────────────────────────────────┐   │    │
│  │  │ Vertex Search ingest                               │   │    │
│  │  │ Google Sheets logging                              │   │    │
│  │  │ Tax regime detection                               │   │    │
│  │  │ Community recipe matching                          │   │    │
│  │  └───────────────────────────────────────────────────┘   │    │
│  │                                                           │    │
│  │  Step 4: Currency detection                               │    │
│  │  Step 5: Return all results to frontend                   │    │
│  └───────────────────────────────────────────────────────────┘    │
│                                                                   │
│  WS /ws/{user}/{session} ────────────────────────────────────┐   │
│  │                                                            │   │
│  │  Gemini Live API (bidirectional audio + vision)            │   │
│  │  ┌────────────────────────────────────────────────────┐   │   │
│  │  │  invoice_scanner (root coordinator)                 │   │   │
│  │  │  ├── tax_analyst (6 tools)                          │   │   │
│  │  │  ├── field_specialist (17 tools)                    │   │   │
│  │  │  └── data_manager (8 tools)                         │   │   │
│  │  └────────────────────────────────────────────────────┘   │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────────────┐
│  GOOGLE CLOUD SERVICES                                           │
│                                                                   │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────────┐      │
│  │ Document AI   │  │ Gemini 2.5    │  │ Vertex AI Search │      │
│  │ Invoice Parser│  │ Flash (Live)  │  │ Past invoices +  │      │
│  │ 46 fields     │  │ Voice+Vision  │  │ tax guides (RAG) │      │
│  └──────────────┘  └───────────────┘  └──────────────────┘      │
│                                                                   │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────────┐      │
│  │ Google Sheets │  │ Firestore     │  │ Cloud Run        │      │
│  │ 3 sheets +   │  │ Community     │  │ Serverless       │      │
│  │ remarks      │  │ recipes +     │  │ deployment       │      │
│  │              │  │ voting        │  │                  │      │
│  └──────────────┘  └───────────────┘  └──────────────────┘      │
│                                                                   │
│  ┌──────────────┐                                                │
│  │ ADK          │                                                │
│  │ Multi-agent  │                                                │
│  │ framework    │                                                │
│  └──────────────┘                                                │
└───────────────────────────────────────────────────────────────────┘
```

## Three-Layer Extraction

```
Layer 1: Document AI        → 46 standard fields, grounded, always runs
                              confidence scores, line items, VAT breakdown

Layer 2: Gemini Vision      → 228+ custom fields via 16 industry presets
                              on demand, learns from user, flexible

Layer 3: Community Recipes  → crowd-sourced extraction prompts
                              stored in Firestore, implicit voting
                              trust levels: NEW → GOOD → TRUSTED
```

## Self-Improving Pipeline

```
User points out missing field
         │
         ▼
Agent extracts with Gemini Vision (Layer 2)
         │
         ▼
Sample recorded (implicit label)
         │
    ┌────┴────┐
    │         │
User silent  User corrects
= approved   = better label
    │         │
    └────┬────┘
         │
    Samples accumulate (50+)
         │
         ▼
    Ready for Document AI uptraining
    Field graduates: Layer 2 → Layer 1
```

## Community Recipe Lifecycle

```
User A: Japanese invoice missing tax rates
         │
         ▼
Agent creates recipe (custom Gemini prompt)
         │
         ▼
Tests locally → works!
         │
         ▼
"Want to share?" → Yes → publish to Firestore
         │
         ▼
User B: Japanese invoice → search_recipes("JP_CT")
         │
         ▼
Finds recipe → run_community_recipe() → works → implicit upvote
         │
         ▼
Score: 83% → 85% → 90% → TRUSTED (auto-runs silently)
```

## Context Management

```
Invoice 1-50:     Normal context growth
Invoice 50-100:   Getting large
Invoice 100-150:  Approaching threshold
Invoice 150+:     COMPACTION TRIGGERED
                  │
                  ▼
              Summary generated:
              - All invoices (1-line each)
              - Last 3 in full detail
              - User preferences
              - Learned fields
              - Unresolved issues
                  │
                  ▼
              Injected into new context
              Old history discarded
              Continue seamlessly
```

## Fraud Detection Flow

```
New invoice uploaded
         │
         ▼
┌─ Layer 1: In-Memory (current session) ──────────┐
│  Catches accidental double-scans                  │
│  Instant — no API call                            │
└──────────────────────────────────────────────────┘
         │
         ▼
┌─ Layer 2: Vertex AI Search (history) ────────────┐
│  Catches cross-session duplicates                 │
│  Survives server restarts                         │
└──────────────────────────────────────────────────┘
         │
         ▼
  7 checks: exact dupe, near dupe, suspicious amount,
  bank change, round number, weekend date, sequence gap
         │
         ▼
  CRITICAL → block from Sheets
  HIGH → warn user
  CLEAN → proceed normally
```
