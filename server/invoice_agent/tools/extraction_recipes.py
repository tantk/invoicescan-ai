"""Extraction Recipes — the agent creates custom extraction strategies on the spot.

The problem:
  Document AI misses per-line-item tax rates.
  Layer 2 default prompt also misses it.
  But with a BETTER prompt, Gemini Vision CAN extract it.

The solution:
  The agent crafts a custom extraction prompt during conversation,
  tests it against the current invoice, and if it works, saves it
  as a reusable "recipe" for future invoices.

A recipe is:
  - name: "japan_line_item_tax_rates"
  - trigger: when to apply (country, industry, keywords)
  - prompt: the custom Gemini Vision prompt that works
  - output_format: what the response looks like
  - created_from: which invoice it was first created for

The agent can create, test, edit, and delete recipes during live conversation.
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Optional

from google import genai
from google.genai import types as genai_types

from ..config import GCP_PROJECT, GCP_LOCATION

logger = logging.getLogger(__name__)

# Store recipes in a JSON file (persistent across restarts)
RECIPES_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "extraction_recipes.json")

# In-memory cache
_recipes: dict[str, dict] = {}


def _load_recipes():
    """Load recipes from disk."""
    global _recipes
    try:
        if os.path.exists(RECIPES_PATH):
            with open(RECIPES_PATH, "r", encoding="utf-8") as f:
                _recipes = json.load(f)
    except Exception:
        _recipes = {}


def _save_recipes():
    """Save recipes to disk."""
    try:
        with open(RECIPES_PATH, "w", encoding="utf-8") as f:
            json.dump(_recipes, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to save recipes: {e}")


# Load on import
_load_recipes()


def create_recipe(
    name: str,
    description: str,
    extraction_prompt: str,
    trigger_regime: str = "",
    trigger_industry: str = "",
    trigger_keywords: str = "",
) -> dict:
    """Create a new extraction recipe that the agent can use on future invoices.

    Use this when the default extraction misses something and you need a
    custom prompt to extract it properly. Test the recipe first with
    test_recipe() before saving.

    Args:
        name: Short name for the recipe (e.g., "japan_split_tax_rates").
        description: What this recipe extracts and when to use it.
        extraction_prompt: The full Gemini Vision prompt to use.
            This should be specific enough to reliably extract the data.
            Include format instructions (JSON structure expected).
        trigger_regime: Tax regime code to auto-apply (e.g., "JP_CT"). Empty = manual only.
        trigger_industry: Industry to auto-apply (e.g., "construction"). Empty = manual only.
        trigger_keywords: Comma-separated keywords in invoice text that trigger this recipe.

    Returns:
        The created recipe.
    """
    name = name.strip().lower().replace(" ", "_")

    recipe = {
        "name": name,
        "description": description,
        "extraction_prompt": extraction_prompt,
        "trigger_regime": trigger_regime,
        "trigger_industry": trigger_industry,
        "trigger_keywords": [k.strip() for k in trigger_keywords.split(",") if k.strip()],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "times_used": 0,
        "success_count": 0,
    }

    _recipes[name] = recipe
    _save_recipes()

    logger.info(f"Created extraction recipe '{name}': {description}")

    return {
        "status": "created",
        "recipe": recipe,
        "message": f"Recipe '{name}' created. Use test_recipe('{name}', invoice_id) to test it.",
    }


def test_recipe(name: str, invoice_id: str) -> dict:
    """Test an extraction recipe against an invoice to see if it works.

    Run the recipe's custom prompt against the invoice image and return
    what Gemini Vision extracts. If the result looks good, the recipe
    is ready for production use.

    Args:
        name: The recipe name to test.
        invoice_id: The invoice to test against.

    Returns:
        The extraction result from running the recipe.
    """
    from .invoice_parser import invoice_store

    name = name.strip().lower().replace(" ", "_")

    if name not in _recipes:
        return {"error": f"Recipe '{name}' not found. Available: {list(_recipes.keys())}"}

    if invoice_id not in invoice_store:
        return {"error": f"Invoice '{invoice_id}' not found."}

    recipe = _recipes[name]
    invoice = invoice_store[invoice_id]

    try:
        client = genai.Client(
            vertexai=True,
            project=GCP_PROJECT,
            location=GCP_LOCATION,
        )

        image_part = genai_types.Part.from_bytes(
            data=invoice["image_bytes"],
            mime_type=invoice["mime_type"],
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[image_part, recipe["extraction_prompt"]],
            config=genai_types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json",
            ),
        )

        raw_text = response.text.strip()
        if raw_text.startswith("```"):
            raw_text = raw_text.split("\n", 1)[1]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3].strip()

        extracted = json.loads(raw_text)

        recipe["times_used"] += 1
        _save_recipes()

        return {
            "status": "success",
            "recipe": name,
            "result": extracted,
            "message": "Recipe produced results. If they look correct, this recipe is ready to use.",
        }

    except Exception as e:
        return {
            "status": "error",
            "recipe": name,
            "error": str(e),
        }


def run_recipe(name: str, invoice_id: str) -> dict:
    """Run a saved recipe on an invoice and store the results.

    Like test_recipe but also saves results to the invoice store
    and Google Sheets.

    Args:
        name: The recipe name.
        invoice_id: The invoice to run against.

    Returns:
        Extraction results.
    """
    result = test_recipe(name, invoice_id)

    if result.get("status") != "success":
        return result

    from .invoice_parser import invoice_store

    # Store results
    invoice = invoice_store.get(invoice_id, {})
    if "recipe_results" not in invoice:
        invoice["recipe_results"] = {}
    invoice["recipe_results"][name] = result["result"]

    # Track success
    _recipes[name]["success_count"] += 1
    _save_recipes()

    # Save to Google Sheets
    try:
        from .sheets import (
            _get_client, _get_or_create_worksheet, _ensure_columns,
            _format_headers, SHEETS_SPREADSHEET_ID,
        )
        from ..config import SHEETS_ENABLED

        if SHEETS_ENABLED:
            extracted = result["result"]
            client = _get_client()
            spreadsheet = client.open_by_key(SHEETS_SPREADSHEET_ID)

            if isinstance(extracted, dict):
                # If result has line_items array → update Line Items sheet
                if "line_items" in extracted and isinstance(extracted["line_items"], list):
                    items = extracted["line_items"]

                    # Collect all keys from all items
                    all_keys = set()
                    for item in items:
                        all_keys.update(item.keys())
                    all_keys = sorted(all_keys)

                    headers = ["Scan ID", "Item #"] + [k.replace("_", " ").title() for k in all_keys]
                    ws = _get_or_create_worksheet(spreadsheet, "Line Items", headers)
                    current_headers = ws.row_values(1)
                    if not current_headers:
                        current_headers = headers
                        ws.update("A1", [current_headers])
                        _format_headers(ws, len(current_headers))
                    else:
                        current_headers = _ensure_columns(ws, current_headers, headers)

                    rows = []
                    for i, item in enumerate(items, 1):
                        row = []
                        for h in current_headers:
                            if h == "Scan ID":
                                row.append(invoice_id)
                            elif h == "Item #":
                                row.append(str(i))
                            else:
                                key = h.lower().replace(" ", "_")
                                row.append(str(item.get(key, "") or ""))
                        rows.append(row)

                    if rows:
                        ws.append_rows(rows, value_input_option="USER_ENTERED")
                        logger.info(f"Recipe '{name}' saved {len(rows)} line items to Sheet")

                else:
                    # Flat dict → add as columns to Invoices sheet
                    invoices_ws = spreadsheet.worksheet("Invoices")
                    all_values = invoices_ws.get_all_values()
                    if all_values:
                        current_headers = all_values[0]
                        # Find the row
                        for row_idx, row in enumerate(all_values[1:], start=2):
                            if row[0] == invoice_id:
                                # Add new columns for each extracted field
                                new_headers = [f"Recipe {k.replace('_', ' ').title()}" for k in extracted.keys()]
                                current_headers = _ensure_columns(invoices_ws, current_headers, new_headers)
                                for k, v in extracted.items():
                                    col_name = f"Recipe {k.replace('_', ' ').title()}"
                                    col_idx = current_headers.index(col_name) + 1
                                    invoices_ws.update_cell(row_idx, col_idx, str(v or ""))
                                logger.info(f"Recipe '{name}' saved {len(extracted)} fields to Invoices sheet")
                                break

    except Exception as e:
        logger.error(f"Recipe Sheets save failed: {e}")

    return result


def list_recipes() -> dict:
    """List all saved extraction recipes.

    Shows available recipes with their triggers and usage stats.

    Returns:
        All recipes with metadata.
    """
    if not _recipes:
        return {"recipes": {}, "message": "No recipes yet. Create one with create_recipe()."}

    return {
        "recipes": {
            name: {
                "description": r["description"],
                "triggers": {
                    "regime": r.get("trigger_regime", ""),
                    "industry": r.get("trigger_industry", ""),
                    "keywords": r.get("trigger_keywords", []),
                },
                "times_used": r.get("times_used", 0),
                "success_count": r.get("success_count", 0),
            }
            for name, r in _recipes.items()
        },
        "total": len(_recipes),
    }


def delete_recipe(name: str) -> dict:
    """Delete an extraction recipe.

    Args:
        name: Recipe to delete.

    Returns:
        Confirmation.
    """
    name = name.strip().lower().replace(" ", "_")
    if name in _recipes:
        del _recipes[name]
        _save_recipes()
        return {"status": "deleted", "message": f"Recipe '{name}' deleted."}
    return {"error": f"Recipe '{name}' not found."}


def get_matching_recipes(
    regime: str = "",
    industry: str = "",
    text: str = "",
) -> list[str]:
    """Find recipes that match the given invoice characteristics.

    Called internally during upload to check if any recipes should auto-run.

    Returns:
        List of matching recipe names.
    """
    matches = []
    text_lower = text.lower()

    for name, recipe in _recipes.items():
        # Check regime trigger
        if recipe.get("trigger_regime") and recipe["trigger_regime"] == regime:
            matches.append(name)
            continue

        # Check industry trigger
        if recipe.get("trigger_industry") and recipe["trigger_industry"] == industry:
            matches.append(name)
            continue

        # Check keyword triggers
        keywords = recipe.get("trigger_keywords", [])
        if keywords and any(kw.lower() in text_lower for kw in keywords):
            matches.append(name)

    return matches
