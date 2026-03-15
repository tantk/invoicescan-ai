"""Firestore-backed extraction recipes — per-user subscriptions + shared recipes.

Recipes are shared documents in Firestore. Each user subscribes to the recipes
they want. On upload, the server reads the user's subscribed recipe IDs,
fetches each recipe, checks triggers, and auto-runs matches.

Firestore structure:
  recipes/{recipe_id}              ← shared, global
    name: "japan_split_tax"
    extraction_prompt: "Look for 税率 column..."
    description: "Per-line-item tax rates for Japanese invoices"
    trigger_regime: "JP_CT"
    trigger_industry: ""
    trigger_keywords: ["税率", "軽減税率"]
    created_by: "userA"
    created_at: "2026-03-16T..."
    times_used: 42
    success: 40
    failed: 2
    score: 95.2

  users/{user_id}                  ← per-user preferences
    recipe_ids: ["recipe_abc", "recipe_def", ...]

Agent tool: manage_recipes(action, ...) — create/test/list/delete/search/subscribe/unsubscribe
Server auto-run: get_user_recipes() → match triggers → run_recipe()
"""

import json
import logging
from datetime import datetime, timezone

from google.cloud import firestore
from google import genai
from google.genai import types as genai_types

from .config import GCP_PROJECT, GCP_LOCATION

logger = logging.getLogger(__name__)

RECIPES_COLLECTION = "recipes"
USERS_COLLECTION = "users"
_db = None


def _get_db():
    global _db
    if _db is None:
        _db = firestore.Client(project=GCP_PROJECT)
    return _db


def _run_extraction(invoice: dict, prompt: str) -> dict:
    """Run a Gemini Vision extraction prompt against an invoice image."""
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
        contents=[image_part, prompt],
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

    return json.loads(raw_text)


def _save_recipe_results_to_sheets(invoice_id: str, recipe_name: str, extracted: dict):
    """Save recipe extraction results to Google Sheets."""
    try:
        from .tools.sheets import (
            _get_client, _get_or_create_worksheet, _ensure_columns,
            _format_headers, SHEETS_SPREADSHEET_ID,
        )
        from .config import SHEETS_ENABLED

        if not SHEETS_ENABLED:
            return

        client = _get_client()
        spreadsheet = client.open_by_key(SHEETS_SPREADSHEET_ID)

        if isinstance(extracted, dict) and "line_items" in extracted:
            items = extracted["line_items"]
            all_keys = sorted(set(k for item in items for k in item.keys()))
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
                logger.info(f"Recipe '{recipe_name}' saved {len(rows)} line items")

        elif isinstance(extracted, dict):
            invoices_ws = spreadsheet.worksheet("Invoices")
            all_values = invoices_ws.get_all_values()
            if all_values:
                current_headers = all_values[0]
                for row_idx, row in enumerate(all_values[1:], start=2):
                    if row[0] == invoice_id:
                        new_headers = [f"Recipe {k.replace('_', ' ').title()}" for k in extracted.keys()]
                        current_headers = _ensure_columns(invoices_ws, current_headers, new_headers)
                        for k, v in extracted.items():
                            col_name = f"Recipe {k.replace('_', ' ').title()}"
                            col_idx = current_headers.index(col_name) + 1
                            invoices_ws.update_cell(row_idx, col_idx, str(v or ""))
                        logger.info(f"Recipe '{recipe_name}' saved {len(extracted)} fields")
                        break

    except Exception as e:
        logger.error(f"Recipe Sheets save failed: {e}")


# ── User recipe list helpers ──────────────────────────────────────────────


def _get_user_recipe_ids(user_id: str) -> list[str]:
    """Get a user's subscribed recipe IDs from Firestore."""
    db = _get_db()
    doc = db.collection(USERS_COLLECTION).document(user_id).get()
    if doc.exists:
        return doc.to_dict().get("recipe_ids", [])
    return []


def _add_recipe_to_user(user_id: str, recipe_id: str):
    """Add a recipe ID to a user's subscription list."""
    db = _get_db()
    user_ref = db.collection(USERS_COLLECTION).document(user_id)
    user_ref.set(
        {"recipe_ids": firestore.ArrayUnion([recipe_id])},
        merge=True,
    )


def _remove_recipe_from_user(user_id: str, recipe_id: str):
    """Remove a recipe ID from a user's subscription list."""
    db = _get_db()
    user_ref = db.collection(USERS_COLLECTION).document(user_id)
    user_ref.set(
        {"recipe_ids": firestore.ArrayRemove([recipe_id])},
        merge=True,
    )


# ── Agent Tool: manage_recipes ────────────────────────────────────────────


def manage_recipes(
    action: str,
    user_id: str = "default",
    name: str = "",
    description: str = "",
    extraction_prompt: str = "",
    trigger_regime: str = "",
    trigger_industry: str = "",
    trigger_keywords: str = "",
    invoice_id: str = "",
    recipe_id: str = "",
    regime: str = "",
    industry: str = "",
) -> dict:
    """Manage extraction recipes — create, test, list, delete, search, subscribe, unsubscribe.

    Recipes are custom Gemini Vision prompts stored in Firestore. Users subscribe
    to recipes they want. Subscribed recipes auto-run on future uploads when
    triggers match the invoice.

    Args:
        action: One of: create, test, list, delete, search, subscribe, unsubscribe.
        user_id: The current user.
        name: Recipe name (for create/test/delete).
        description: What the recipe extracts (for create).
        extraction_prompt: The Gemini Vision prompt (for create).
        trigger_regime: Auto-match tax regime, e.g. "JP_CT" (for create/search).
        trigger_industry: Auto-match industry, e.g. "construction" (for create/search).
        trigger_keywords: Comma-separated trigger keywords (for create).
        invoice_id: Invoice to test against (for test).
        recipe_id: Recipe ID to subscribe/unsubscribe to.
        regime: Search by regime (for search).
        industry: Search by industry (for search).

    Returns:
        Action result.
    """
    action = action.strip().lower()

    if action == "create":
        return _create_recipe(user_id, name, description, extraction_prompt,
                              trigger_regime, trigger_industry, trigger_keywords)
    elif action == "test":
        return _test_recipe(recipe_id or name, invoice_id)
    elif action == "list":
        return _list_recipes(user_id)
    elif action == "delete":
        return _delete_recipe(user_id, recipe_id or name)
    elif action == "search":
        return _search_recipes(regime or trigger_regime, industry or trigger_industry)
    elif action == "subscribe":
        return _subscribe_recipe(user_id, recipe_id)
    elif action == "unsubscribe":
        return _unsubscribe_recipe(user_id, recipe_id or name)
    else:
        return {"error": f"Unknown action: {action}. Use: create, test, list, delete, search, subscribe, unsubscribe."}


def _create_recipe(user_id, name, description, extraction_prompt,
                   trigger_regime, trigger_industry, trigger_keywords):
    if not name or not extraction_prompt:
        return {"error": "name and extraction_prompt are required."}

    db = _get_db()
    name = name.strip().lower().replace(" ", "_")

    recipe = {
        "name": name,
        "description": description,
        "extraction_prompt": extraction_prompt,
        "trigger_regime": trigger_regime,
        "trigger_industry": trigger_industry,
        "trigger_keywords": [k.strip() for k in trigger_keywords.split(",") if k.strip()] if trigger_keywords else [],
        "created_by": user_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "times_used": 0,
        "success": 0,
        "failed": 0,
        "score": 0.0,
    }

    # Save recipe and get its auto-generated ID
    doc_ref = db.collection(RECIPES_COLLECTION).document()
    recipe_id = doc_ref.id
    recipe["recipe_id"] = recipe_id
    doc_ref.set(recipe)

    # Auto-subscribe the creator
    _add_recipe_to_user(user_id, recipe_id)

    logger.info(f"Recipe '{name}' created (id={recipe_id}) by user={user_id}")

    return {
        "status": "created",
        "recipe_id": recipe_id,
        "name": name,
        "message": f"Recipe '{name}' saved and subscribed. It will auto-run on matching invoices.",
    }


def _test_recipe(recipe_id_or_name, invoice_id):
    from .tools.invoice_parser import invoice_store

    if not recipe_id_or_name or not invoice_id:
        return {"error": "recipe_id (or name) and invoice_id are required."}

    if invoice_id not in invoice_store:
        return {"error": f"Invoice '{invoice_id}' not found."}

    # Find recipe by ID or name
    recipe_data = _find_recipe(recipe_id_or_name)
    if not recipe_data:
        return {"error": f"Recipe '{recipe_id_or_name}' not found."}

    prompt = recipe_data.get("extraction_prompt", "")
    if not prompt:
        return {"error": f"Recipe '{recipe_data.get('name', '?')}' has no extraction prompt."}

    try:
        extracted = _run_extraction(invoice_store[invoice_id], prompt)
        return {
            "status": "success",
            "recipe_id": recipe_data.get("recipe_id", ""),
            "recipe": recipe_data.get("name", ""),
            "result": extracted,
            "message": "Test complete. Review the results.",
        }
    except Exception as e:
        return {"status": "error", "recipe": recipe_data.get("name", ""), "error": str(e)}


def _list_recipes(user_id):
    recipe_ids = _get_user_recipe_ids(user_id)

    if not recipe_ids:
        return {"recipes": [], "message": "No recipes subscribed. Create one or search for community recipes."}

    db = _get_db()
    recipes = []
    for rid in recipe_ids:
        doc = db.collection(RECIPES_COLLECTION).document(rid).get()
        if doc.exists:
            data = doc.to_dict()
            recipes.append({
                "recipe_id": rid,
                "name": data.get("name", ""),
                "description": data.get("description", ""),
                "trigger_regime": data.get("trigger_regime", ""),
                "trigger_industry": data.get("trigger_industry", ""),
                "created_by": data.get("created_by", ""),
                "times_used": data.get("times_used", 0),
                "score": data.get("score", 0),
            })

    return {"recipes": recipes, "total": len(recipes)}


def _delete_recipe(user_id, recipe_id_or_name):
    if not recipe_id_or_name:
        return {"error": "recipe_id or name is required."}

    recipe_data = _find_recipe(recipe_id_or_name)
    if not recipe_data:
        return {"error": f"Recipe '{recipe_id_or_name}' not found."}

    recipe_id = recipe_data.get("recipe_id", "")
    name = recipe_data.get("name", "")

    # Only the creator can delete the recipe itself
    if recipe_data.get("created_by") == user_id:
        db = _get_db()
        db.collection(RECIPES_COLLECTION).document(recipe_id).delete()
        _remove_recipe_from_user(user_id, recipe_id)
        logger.info(f"Recipe '{name}' (id={recipe_id}) deleted by creator {user_id}")
        return {"status": "deleted", "name": name, "message": f"Recipe '{name}' permanently deleted."}
    else:
        # Non-creators just unsubscribe
        _remove_recipe_from_user(user_id, recipe_id)
        return {"status": "unsubscribed", "name": name, "message": f"Removed '{name}' from your list. Recipe still exists for other users."}


def _search_recipes(regime, industry):
    """Search all recipes by regime/industry (community discovery)."""
    db = _get_db()
    recipes_ref = db.collection(RECIPES_COLLECTION)
    matches = []

    if regime:
        for doc in recipes_ref.where("trigger_regime", "==", regime).stream():
            data = doc.to_dict()
            data["recipe_id"] = doc.id
            data["match_reason"] = f"regime:{regime}"
            matches.append(data)

    if industry and not matches:
        for doc in recipes_ref.where("trigger_industry", "==", industry).stream():
            data = doc.to_dict()
            data["recipe_id"] = doc.id
            data["match_reason"] = f"industry:{industry}"
            matches.append(data)

    # Deduplicate by ID
    seen = set()
    unique = []
    for m in matches:
        rid = m.get("recipe_id", "")
        if rid not in seen:
            seen.add(rid)
            unique.append(m)

    unique.sort(key=lambda r: r.get("score", 0), reverse=True)

    return {
        "recipes": [
            {
                "recipe_id": r.get("recipe_id", ""),
                "name": r.get("name", ""),
                "description": r.get("description", ""),
                "created_by": r.get("created_by", ""),
                "score": r.get("score", 0),
                "times_used": r.get("times_used", 0),
                "match_reason": r.get("match_reason", ""),
            }
            for r in unique
        ],
        "total": len(unique),
    }


def _subscribe_recipe(user_id, recipe_id):
    if not recipe_id:
        return {"error": "recipe_id is required."}

    db = _get_db()
    doc = db.collection(RECIPES_COLLECTION).document(recipe_id).get()
    if not doc.exists:
        return {"error": f"Recipe '{recipe_id}' not found."}

    data = doc.to_dict()
    _add_recipe_to_user(user_id, recipe_id)

    return {
        "status": "subscribed",
        "recipe_id": recipe_id,
        "name": data.get("name", ""),
        "message": f"Subscribed to '{data.get('name', '')}'. It will auto-run on matching invoices.",
    }


def _unsubscribe_recipe(user_id, recipe_id_or_name):
    if not recipe_id_or_name:
        return {"error": "recipe_id or name is required."}

    recipe_data = _find_recipe(recipe_id_or_name)
    if recipe_data:
        recipe_id = recipe_data.get("recipe_id", "")
        name = recipe_data.get("name", "")
    else:
        recipe_id = recipe_id_or_name
        name = recipe_id_or_name

    _remove_recipe_from_user(user_id, recipe_id)

    return {
        "status": "unsubscribed",
        "name": name,
        "message": f"Unsubscribed from '{name}'.",
    }


def _find_recipe(recipe_id_or_name: str) -> dict | None:
    """Find a recipe by ID or by name."""
    db = _get_db()

    # Try as document ID first
    doc = db.collection(RECIPES_COLLECTION).document(recipe_id_or_name).get()
    if doc.exists:
        data = doc.to_dict()
        data["recipe_id"] = doc.id
        return data

    # Try by name
    name = recipe_id_or_name.strip().lower().replace(" ", "_")
    docs = db.collection(RECIPES_COLLECTION).where("name", "==", name).limit(1).stream()
    for doc in docs:
        data = doc.to_dict()
        data["recipe_id"] = doc.id
        return data

    return None


# ── Server Auto-Run: called from upload pipeline ─────────────────────────


def get_user_recipes(user_id: str, regime: str = "", industry: str = "") -> list[dict]:
    """Get a user's subscribed recipes that match the given invoice triggers.

    Called by the upload pipeline to find recipes to auto-run.

    Returns:
        List of matching recipes with recipe_id, name, and extraction_prompt.
    """
    recipe_ids = _get_user_recipe_ids(user_id)
    if not recipe_ids:
        return []

    db = _get_db()
    matches = []

    for rid in recipe_ids:
        doc = db.collection(RECIPES_COLLECTION).document(rid).get()
        if not doc.exists:
            continue

        data = doc.to_dict()
        data["recipe_id"] = rid
        r_regime = data.get("trigger_regime", "")
        r_industry = data.get("trigger_industry", "")

        # No triggers = always run
        if not r_regime and not r_industry:
            matches.append(data)
            continue

        # Match regime
        if r_regime and regime and r_regime == regime:
            matches.append(data)
            continue

        # Match industry
        if r_industry and industry and r_industry == industry:
            matches.append(data)
            continue

    return matches


def run_recipe(recipe_id: str, invoice_id: str) -> dict:
    """Run a recipe on an invoice — extract, save to Sheets, record usage.

    Called by the server background pipeline (auto-run).

    Args:
        recipe_id: The Firestore recipe document ID.
        invoice_id: The invoice to run against.

    Returns:
        Extraction results.
    """
    from .tools.invoice_parser import invoice_store

    if invoice_id not in invoice_store:
        return {"error": f"Invoice '{invoice_id}' not found."}

    db = _get_db()
    doc = db.collection(RECIPES_COLLECTION).document(recipe_id).get()
    if not doc.exists:
        return {"error": f"Recipe '{recipe_id}' not found."}

    recipe_data = doc.to_dict()
    name = recipe_data.get("name", recipe_id)
    prompt = recipe_data.get("extraction_prompt", "")
    if not prompt:
        return {"error": f"Recipe '{name}' has no extraction prompt."}

    invoice = invoice_store[invoice_id]

    try:
        extracted = _run_extraction(invoice, prompt)
    except Exception as e:
        _record_usage(recipe_id, "failed")
        return {"status": "error", "recipe": name, "error": str(e)}

    # Save to Sheets
    _save_recipe_results_to_sheets(invoice_id, name, extracted)

    # Record success
    _record_usage(recipe_id, "success")

    # Store in invoice_store
    if "recipe_results" not in invoice:
        invoice["recipe_results"] = {}
    invoice["recipe_results"][name] = extracted

    return {
        "status": "success",
        "recipe": name,
        "recipe_id": recipe_id,
        "result": extracted,
    }


def _record_usage(recipe_id: str, result: str):
    """Record usage stats for a recipe."""
    try:
        db = _get_db()
        doc_ref = db.collection(RECIPES_COLLECTION).document(recipe_id)

        updates = {"times_used": firestore.Increment(1)}
        if result == "success":
            updates["success"] = firestore.Increment(1)
        elif result == "failed":
            updates["failed"] = firestore.Increment(1)

        doc_ref.update(updates)

        # Recalculate score
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            total = data.get("times_used", 0)
            if total > 0:
                score = round((data.get("success", 0) / total) * 100, 1)
                doc_ref.update({"score": score})
    except Exception as e:
        logger.debug(f"Usage recording failed: {e}")
