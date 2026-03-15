"""Configuration for the Invoice Scanner agent."""

import os

# ── Model Selection ───────────────────────────────────────────────────────
_use_vertex = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "").upper() == "TRUE"

AVAILABLE_MODELS = {
    "gemini-2.5-flash": {
        # Vertex AI and AI Studio use different model IDs for Live
        "model_id": "gemini-live-2.5-flash-native-audio" if _use_vertex else "gemini-2.5-flash-native-audio-preview-12-2025",
        "display_name": "Gemini Flash Live",
    },
}

_model_key = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
if _model_key not in AVAILABLE_MODELS:
    _model_key = "gemini-2.5-flash"

MODEL_ID = AVAILABLE_MODELS[_model_key]["model_id"]
MODEL_DISPLAY_NAME = AVAILABLE_MODELS[_model_key]["display_name"]

# Voice
VOICE_NAME = "Aoede"

# ── Google Cloud ──────────────────────────────────────────────────────────
GCP_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
GCP_LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")

# ── Document AI ───────────────────────────────────────────────────────────
DOCAI_LOCATION = os.environ.get("DOCAI_LOCATION", "us")
DOCAI_PROCESSOR_ID = os.environ.get("DOCAI_PROCESSOR_ID", "")
DOCAI_ENABLED = bool(GCP_PROJECT and DOCAI_PROCESSOR_ID)

# ── Vertex AI Search (Data Store for invoice RAG) ────────────────────────
VERTEX_SEARCH_LOCATION = os.environ.get("VERTEX_SEARCH_LOCATION", "global")
VERTEX_SEARCH_DATA_STORE_ID = os.environ.get("VERTEX_SEARCH_DATA_STORE_ID", "")
VERTEX_SEARCH_ENGINE_ID = os.environ.get("VERTEX_SEARCH_ENGINE_ID", "")

VERTEX_SEARCH_ENABLED = bool(GCP_PROJECT and VERTEX_SEARCH_DATA_STORE_ID)

# Full data store path for ADK VertexAiSearchTool
VERTEX_SEARCH_DATA_STORE_PATH = ""
if VERTEX_SEARCH_ENABLED:
    VERTEX_SEARCH_DATA_STORE_PATH = (
        f"projects/{GCP_PROJECT}/locations/{VERTEX_SEARCH_LOCATION}"
        f"/collections/default_collection/dataStores/{VERTEX_SEARCH_DATA_STORE_ID}"
    )

# ── Google Sheets ─────────────────────────────────────────────────────────
SHEETS_SPREADSHEET_ID = os.environ.get("SHEETS_SPREADSHEET_ID", "")
SHEETS_ENABLED = bool(SHEETS_SPREADSHEET_ID)

# ── Agent Engine (Memory Bank + Sessions) ─────────────────────────────────
# When AGENT_ENGINE_ID is set, both sessions and memory use Vertex AI.
# Otherwise falls back to local (in-memory) for dev.
AGENT_ENGINE_ID = os.environ.get("AGENT_ENGINE_ID", "")
_USE_VERTEX_SERVICES = bool(GCP_PROJECT and AGENT_ENGINE_ID)

# Auto-select backend: vertex if Agent Engine is configured, local otherwise
MEMORY_BACKEND = os.environ.get("MEMORY_BACKEND", "vertex" if _USE_VERTEX_SERVICES else "local")
SESSION_BACKEND = os.environ.get("SESSION_BACKEND", "vertex" if _USE_VERTEX_SERVICES else "memory")
