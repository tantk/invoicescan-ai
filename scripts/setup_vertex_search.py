"""Setup script: Create Vertex AI Search data store and engine for InvoiceScan AI.

Run once to provision the search infrastructure:
    cd server && python -m scripts.setup_vertex_search

Requires:
    - GOOGLE_CLOUD_PROJECT set in .env
    - gcloud auth application-default login
    - Document AI API and Discovery Engine API enabled
"""

import os
import sys
import time

from dotenv import load_dotenv

# Load from server/.env
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "server", ".env"))

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
LOCATION = os.environ.get("VERTEX_SEARCH_LOCATION", "global")
DATA_STORE_ID = "invoicescan-invoices"
ENGINE_ID = "invoicescan-engine"

if not PROJECT_ID:
    print("ERROR: Set GOOGLE_CLOUD_PROJECT in your .env file")
    sys.exit(1)


def create_data_store():
    """Create the invoice data store."""
    from google.api_core.client_options import ClientOptions
    from google.cloud import discoveryengine

    client_options = (
        ClientOptions(api_endpoint=f"{LOCATION}-discoveryengine.googleapis.com")
        if LOCATION != "global"
        else None
    )
    client = discoveryengine.DataStoreServiceClient(client_options=client_options)

    parent = client.collection_path(
        project=PROJECT_ID,
        location=LOCATION,
        collection="default_collection",
    )

    data_store = discoveryengine.DataStore(
        display_name="InvoiceScan Invoices",
        industry_vertical=discoveryengine.IndustryVertical.GENERIC,
        solution_types=[discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH],
        content_config=discoveryengine.DataStore.ContentConfig.CONTENT_REQUIRED,
    )

    print(f"Creating data store '{DATA_STORE_ID}' in {PROJECT_ID}/{LOCATION}...")

    try:
        operation = client.create_data_store(
            request=discoveryengine.CreateDataStoreRequest(
                parent=parent,
                data_store_id=DATA_STORE_ID,
                data_store=data_store,
            )
        )
        result = operation.result()
        print(f"Data store created: {result.name}")
        return True
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"Data store '{DATA_STORE_ID}' already exists — OK")
            return True
        print(f"ERROR creating data store: {e}")
        return False


def create_search_engine():
    """Create a search engine linked to the data store."""
    from google.api_core.client_options import ClientOptions
    from google.cloud import discoveryengine_v1 as discoveryengine

    client_options = (
        ClientOptions(api_endpoint=f"{LOCATION}-discoveryengine.googleapis.com")
        if LOCATION != "global"
        else None
    )
    client = discoveryengine.EngineServiceClient(client_options=client_options)

    parent = client.collection_path(
        project=PROJECT_ID,
        location=LOCATION,
        collection="default_collection",
    )

    engine = discoveryengine.Engine(
        display_name="InvoiceScan Search Engine",
        industry_vertical=discoveryengine.IndustryVertical.GENERIC,
        solution_type=discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH,
        search_engine_config=discoveryengine.Engine.SearchEngineConfig(
            search_tier=discoveryengine.SearchTier.SEARCH_TIER_ENTERPRISE,
            search_add_ons=[discoveryengine.SearchAddOn.SEARCH_ADD_ON_LLM],
        ),
        data_store_ids=[DATA_STORE_ID],
    )

    print(f"Creating search engine '{ENGINE_ID}'...")

    try:
        operation = client.create_engine(
            request=discoveryengine.CreateEngineRequest(
                parent=parent,
                engine=engine,
                engine_id=ENGINE_ID,
            )
        )
        result = operation.result()
        print(f"Search engine created: {result.name}")
        return True
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"Search engine '{ENGINE_ID}' already exists — OK")
            return True
        print(f"ERROR creating search engine: {e}")
        return False


def print_env_config():
    """Print the .env values to add."""
    print("\n" + "=" * 60)
    print("Add these to your server/.env file:")
    print("=" * 60)
    print(f"VERTEX_SEARCH_LOCATION={LOCATION}")
    print(f"VERTEX_SEARCH_DATA_STORE_ID={DATA_STORE_ID}")
    print(f"VERTEX_SEARCH_ENGINE_ID={ENGINE_ID}")
    print("=" * 60)


if __name__ == "__main__":
    print(f"Project: {PROJECT_ID}")
    print(f"Location: {LOCATION}")
    print()

    if create_data_store():
        time.sleep(2)  # Brief pause between operations
        create_search_engine()

    print_env_config()
