"""Ingest processed invoices into Vertex AI Search data store.

After Document AI extracts structured data from an invoice, we push
that data into Vertex AI Search so the agent can semantically search
across all past invoices.
"""

import json
import logging
from typing import Optional

from google.api_core.client_options import ClientOptions
from google.protobuf.struct_pb2 import Struct

from ..config import (
    GCP_PROJECT,
    VERTEX_SEARCH_ENABLED,
    VERTEX_SEARCH_LOCATION,
    VERTEX_SEARCH_DATA_STORE_ID,
)

logger = logging.getLogger(__name__)


def ingest_invoice_to_search(
    invoice_id: str,
    extracted_data: dict,
    filename: Optional[str] = None,
) -> bool:
    """Push extracted invoice data into the Vertex AI Search data store.

    Creates a structured document with all invoice fields and line items,
    making it searchable via semantic and keyword queries.

    Args:
        invoice_id: Unique invoice identifier.
        extracted_data: Dict from Document AI extraction (fields, line_items, full_text).
        filename: Original filename for reference.

    Returns:
        True if ingestion succeeded.
    """
    if not VERTEX_SEARCH_ENABLED:
        logger.debug("Vertex AI Search not configured — skipping ingestion")
        return False

    try:
        from google.cloud import discoveryengine

        client_options = (
            ClientOptions(
                api_endpoint=f"{VERTEX_SEARCH_LOCATION}-discoveryengine.googleapis.com"
            )
            if VERTEX_SEARCH_LOCATION != "global"
            else None
        )

        client = discoveryengine.DocumentServiceClient(
            client_options=client_options
        )

        parent = client.branch_path(
            project=GCP_PROJECT,
            location=VERTEX_SEARCH_LOCATION,
            data_store=VERTEX_SEARCH_DATA_STORE_ID,
            branch="default_branch",
        )

        # Build a rich text content for semantic search
        content_parts = []

        fields = extracted_data.get("fields", {})
        if fields:
            content_parts.append("=== Invoice Details ===")
            for field_type, field_data in fields.items():
                label = field_type.replace("_", " ").title()
                content_parts.append(f"{label}: {field_data['value']}")

        line_items = extracted_data.get("line_items", [])
        if line_items:
            content_parts.append(f"\n=== Line Items ({len(line_items)}) ===")
            for i, item in enumerate(line_items, 1):
                parts = []
                for prop_type, prop_data in item.items():
                    label = prop_type.replace("line_item/", "").replace("_", " ").title()
                    parts.append(f"{label}: {prop_data['value']}")
                content_parts.append(f"{i}. {' | '.join(parts)}")

        full_text = extracted_data.get("full_text", "")
        if full_text:
            content_parts.append(f"\n=== Raw OCR Text ===\n{full_text}")

        content = "\n".join(content_parts)

        # Build struct_data for structured filtering
        struct_data = Struct()
        flat_fields = {k: v["value"] for k, v in fields.items()}
        flat_fields["invoice_id"] = invoice_id
        flat_fields["line_item_count"] = str(len(line_items))
        if filename:
            flat_fields["filename"] = filename

        # Store source map (bounding boxes for audit trail)
        annotations = extracted_data.get("annotations", [])
        if annotations:
            import json as _json
            flat_fields["source_map"] = _json.dumps({
                a["type"]: {
                    "value": a["value"],
                    "bbox": a["bbox"],
                    "confidence": a["confidence"],
                }
                for a in annotations
            }, ensure_ascii=False)

        struct_data.update(flat_fields)

        # Create the document
        document = discoveryengine.Document(
            id=invoice_id,
            content=discoveryengine.Document.Content(
                mime_type="text/plain",
                raw_bytes=content.encode("utf-8"),
            ),
            struct_data=struct_data,
        )

        request = discoveryengine.CreateDocumentRequest(
            parent=parent,
            document=document,
            document_id=invoice_id,
        )

        result = client.create_document(request=request)
        logger.info(f"Ingested invoice {invoice_id} into Vertex AI Search")
        return True

    except Exception as e:
        logger.error(f"Failed to ingest invoice {invoice_id}: {e}")
        return False


def search_invoices(query: str, max_results: int = 5) -> list[dict]:
    """Search past invoices using Vertex AI Search.

    This is a direct search function (not an agent tool — the agent uses
    VertexAiSearchTool instead). Used by REST API endpoints.

    Args:
        query: Natural language search query.
        max_results: Maximum results to return.

    Returns:
        List of matching invoice summaries.
    """
    if not VERTEX_SEARCH_ENABLED:
        return []

    try:
        from google.cloud import discoveryengine_v1 as discoveryengine

        client_options = (
            ClientOptions(
                api_endpoint=f"{VERTEX_SEARCH_LOCATION}-discoveryengine.googleapis.com"
            )
            if VERTEX_SEARCH_LOCATION != "global"
            else None
        )

        client = discoveryengine.SearchServiceClient(
            client_options=client_options
        )

        # Use engine if available, otherwise data store
        from ..config import VERTEX_SEARCH_ENGINE_ID

        if VERTEX_SEARCH_ENGINE_ID:
            serving_config = (
                f"projects/{GCP_PROJECT}/locations/{VERTEX_SEARCH_LOCATION}"
                f"/collections/default_collection/engines/{VERTEX_SEARCH_ENGINE_ID}"
                f"/servingConfigs/default_config"
            )
        else:
            serving_config = (
                f"projects/{GCP_PROJECT}/locations/{VERTEX_SEARCH_LOCATION}"
                f"/collections/default_collection/dataStores/{VERTEX_SEARCH_DATA_STORE_ID}"
                f"/servingConfigs/default_config"
            )

        request = discoveryengine.SearchRequest(
            serving_config=serving_config,
            query=query,
            page_size=max_results,
            content_search_spec=discoveryengine.SearchRequest.ContentSearchSpec(
                snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
                    return_snippet=True,
                ),
                summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
                    summary_result_count=max_results,
                    include_citations=True,
                ),
            ),
        )

        results = []
        for response in client.search(request):
            doc = response.document
            results.append({
                "id": doc.id,
                "data": dict(doc.struct_data) if doc.struct_data else {},
                "snippet": (
                    response.document.derived_struct_data.get("snippets", [{}])[0].get("snippet", "")
                    if response.document.derived_struct_data
                    else ""
                ),
            })

        return results

    except Exception as e:
        logger.error(f"Search failed: {e}")
        return []
