"""Ingest tax guide documents into the Vertex AI Search data store.

This populates the RAG layer so the agent can retrieve curated tax
knowledge alongside live search results.

Run: python scripts/ingest_tax_guides.py

Requires VERTEX_SEARCH_DATA_STORE_ID and GOOGLE_CLOUD_PROJECT in .env.
"""

import os
import sys

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "server", ".env"))

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
LOCATION = os.environ.get("VERTEX_SEARCH_LOCATION", "global")
DATA_STORE_ID = os.environ.get("VERTEX_SEARCH_DATA_STORE_ID", "invoicescan-invoices")
GUIDES_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "tax_guides")

if not PROJECT_ID:
    print("ERROR: Set GOOGLE_CLOUD_PROJECT in server/.env")
    sys.exit(1)


def ingest_guides():
    """Read all markdown tax guides and ingest as documents."""
    from google.api_core.client_options import ClientOptions
    from google.cloud import discoveryengine

    client_options = (
        ClientOptions(api_endpoint=f"{LOCATION}-discoveryengine.googleapis.com")
        if LOCATION != "global"
        else None
    )
    client = discoveryengine.DocumentServiceClient(client_options=client_options)

    parent = client.branch_path(
        project=PROJECT_ID,
        location=LOCATION,
        data_store=DATA_STORE_ID,
        branch="default_branch",
    )

    guide_files = [f for f in os.listdir(GUIDES_DIR) if f.endswith(".md")]
    print(f"Found {len(guide_files)} tax guides in {GUIDES_DIR}")

    for filename in guide_files:
        filepath = os.path.join(GUIDES_DIR, filename)
        doc_id = f"tax-guide-{filename.replace('.md', '').replace('_', '-')}"

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract title from first heading
        title = filename.replace(".md", "").replace("_", " ").title()
        for line in content.split("\n"):
            if line.startswith("# "):
                title = line[2:].strip()
                break

        document = discoveryengine.Document(
            id=doc_id,
            content=discoveryengine.Document.Content(
                mime_type="text/plain",
                raw_bytes=content.encode("utf-8"),
            ),
            struct_data={
                "title": title,
                "type": "tax_guide",
                "filename": filename,
            },
        )

        try:
            result = client.create_document(
                request=discoveryengine.CreateDocumentRequest(
                    parent=parent,
                    document=document,
                    document_id=doc_id,
                )
            )
            print(f"  Ingested: {doc_id} — {title}")
        except Exception as e:
            if "already exists" in str(e).lower():
                # Update existing
                document.name = f"{parent}/documents/{doc_id}"
                client.update_document(
                    request=discoveryengine.UpdateDocumentRequest(
                        document=document,
                    )
                )
                print(f"  Updated: {doc_id} — {title}")
            else:
                print(f"  ERROR: {doc_id} — {e}")

    print(f"\nDone. {len(guide_files)} guides ingested into data store '{DATA_STORE_ID}'.")


if __name__ == "__main__":
    ingest_guides()
