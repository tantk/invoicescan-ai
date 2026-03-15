"""Service factories for sessions, memory, and search.

Two modes:
- Local dev: InMemory for both (no GCP needed)
- Production: Vertex AI Agent Engine for both (persistent, managed)

Set GOOGLE_CLOUD_PROJECT + AGENT_ENGINE_ID to auto-switch to Vertex.
"""

import logging

from .config import (
    GCP_PROJECT,
    GCP_LOCATION,
    SESSION_BACKEND,
    MEMORY_BACKEND,
    AGENT_ENGINE_ID,
    VERTEX_SEARCH_ENABLED,
    VERTEX_SEARCH_DATA_STORE_PATH,
)

logger = logging.getLogger(__name__)


def create_session_service():
    """Create session service — Vertex AI or in-memory."""
    if SESSION_BACKEND == "vertex":
        from google.adk.sessions import VertexAiSessionService

        logger.info(f"Sessions: Vertex AI ({GCP_PROJECT}/{GCP_LOCATION})")
        return VertexAiSessionService(
            project=GCP_PROJECT,
            location=GCP_LOCATION,
        )

    from google.adk.sessions import InMemorySessionService

    logger.info("Sessions: in-memory (non-persistent, for local dev)")
    return InMemorySessionService()


def create_memory_service():
    """Create memory service — Vertex AI Memory Bank or in-memory."""
    if MEMORY_BACKEND == "vertex" and GCP_PROJECT and AGENT_ENGINE_ID:
        from google.adk.memory import VertexAiMemoryBankService

        logger.info(f"Memory: Vertex AI Memory Bank (engine={AGENT_ENGINE_ID})")
        return VertexAiMemoryBankService(
            project=GCP_PROJECT,
            location=GCP_LOCATION,
            agent_engine_id=AGENT_ENGINE_ID,
        )

    from google.adk.memory import InMemoryMemoryService

    logger.info("Memory: in-memory (non-persistent, for local dev)")
    return InMemoryMemoryService()


def get_search_tool():
    """Create VertexAiSearchTool if configured, else None."""
    if not VERTEX_SEARCH_ENABLED:
        logger.info("Search: not configured — agent won't search past invoices")
        return None

    from google.adk.tools import VertexAiSearchTool

    logger.info(f"Search: Vertex AI Search ({VERTEX_SEARCH_DATA_STORE_PATH})")
    return VertexAiSearchTool(
        data_store_id=VERTEX_SEARCH_DATA_STORE_PATH,
    )
