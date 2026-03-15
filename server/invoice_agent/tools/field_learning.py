"""User field learning — the agent learns what fields each user cares about.

When a user says "you missed the project code", the agent:
1. Extracts the field immediately via Gemini Vision (Layer 2)
2. Stores it in the learned fields registry (in memory service)
3. Next time a similar invoice arrives, auto-extracts those fields

No uptraining needed. No samples needed. Works instantly.

The registry maps:
  user → vendor patterns → custom fields
  user → industry → custom fields
  user → "always" → custom fields (apply to all invoices)
"""

import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# In-memory learned fields registry
# Structure: {user_id: {scope: [field_names]}}
# Scopes: "always", "industry:construction", "vendor:acme", etc.
_learned_fields: dict[str, dict[str, list[str]]] = {}


def _get_user_fields(user_id: str) -> dict[str, list[str]]:
    """Get all learned fields for a user."""
    if user_id not in _learned_fields:
        _learned_fields[user_id] = {}
    return _learned_fields[user_id]


def learn_field(
    field_name: str,
    scope: str = "always",
    user_id: str = "default",
) -> dict:
    """Teach the agent to always look for a specific field on future invoices.

    When the user points out a missing field, call this to remember it.
    Next time a matching invoice is scanned, the agent will automatically
    extract this field using Gemini Vision.

    Scopes control WHEN to look for the field:
    - "always" — extract from every invoice
    - "industry:construction" — only for construction invoices
    - "industry:healthcare" — only for healthcare invoices
    - "vendor:acme" — only for invoices from Acme Corp
    - "country:IN" — only for Indian invoices

    Args:
        field_name: The field to learn (e.g., "project_code", "department",
                   "approved_by", "cost_center"). Use snake_case.
        scope: When to apply this field. Default "always".
        user_id: The user ID (for per-user learning).

    Returns:
        Confirmation with the updated field registry.
    """
    field_name = field_name.strip().lower().replace(" ", "_")
    scope = scope.strip().lower()

    user_fields = _get_user_fields(user_id)

    if scope not in user_fields:
        user_fields[scope] = []

    if field_name not in user_fields[scope]:
        user_fields[scope].append(field_name)
        logger.info(f"Learned field '{field_name}' for user={user_id} scope={scope}")

    return {
        "status": "learned",
        "field": field_name,
        "scope": scope,
        "message": f"Got it! I'll look for '{field_name}' on {_scope_description(scope)} from now on.",
        "all_learned_fields": user_fields,
    }


def forget_field(
    field_name: str,
    scope: str = "always",
    user_id: str = "default",
) -> dict:
    """Stop looking for a specific field.

    Args:
        field_name: The field to forget.
        scope: The scope to remove it from.
        user_id: The user ID.

    Returns:
        Confirmation.
    """
    field_name = field_name.strip().lower().replace(" ", "_")
    scope = scope.strip().lower()

    user_fields = _get_user_fields(user_id)

    if scope in user_fields and field_name in user_fields[scope]:
        user_fields[scope].remove(field_name)
        if not user_fields[scope]:
            del user_fields[scope]
        return {
            "status": "forgotten",
            "field": field_name,
            "scope": scope,
            "message": f"Removed '{field_name}' from {_scope_description(scope)}.",
        }

    return {
        "status": "not_found",
        "message": f"Field '{field_name}' was not in scope '{scope}'.",
    }


def get_learned_fields(
    user_id: str = "default",
    scope: Optional[str] = None,
) -> dict:
    """Show all fields the agent has learned to look for.

    Use this to see what custom fields will be extracted automatically.

    Args:
        user_id: The user ID.
        scope: Filter to a specific scope, or None for all.

    Returns:
        All learned fields, optionally filtered by scope.
    """
    user_fields = _get_user_fields(user_id)

    if scope:
        fields = user_fields.get(scope, [])
        return {
            "user_id": user_id,
            "scope": scope,
            "fields": fields,
            "total": len(fields),
        }

    total = sum(len(v) for v in user_fields.values())
    return {
        "user_id": user_id,
        "scopes": {k: v for k, v in user_fields.items()},
        "total_fields": total,
    }


def get_fields_for_invoice(
    user_id: str,
    detected_regime: Optional[str] = None,
    detected_industry: Optional[str] = None,
    vendor_name: Optional[str] = None,
) -> list[str]:
    """Get all learned fields that apply to a specific invoice.

    Called internally when processing a new invoice. Collects all
    fields from matching scopes.

    Args:
        user_id: The user.
        detected_regime: Tax regime code (e.g., "IN_GST", "EU_VAT").
        detected_industry: Industry code (e.g., "construction").
        vendor_name: Vendor name for vendor-specific fields.

    Returns:
        Deduplicated list of field names to extract.
    """
    user_fields = _get_user_fields(user_id)
    result = set()

    # Always-extract fields
    result.update(user_fields.get("always", []))

    # Industry-scoped fields
    if detected_industry:
        result.update(user_fields.get(f"industry:{detected_industry}", []))

    # Country/regime-scoped fields
    if detected_regime:
        result.update(user_fields.get(f"country:{detected_regime}", []))
        # Also check country code prefix
        country = detected_regime.split("_")[0] if "_" in detected_regime else detected_regime
        result.update(user_fields.get(f"country:{country.lower()}", []))

    # Vendor-scoped fields
    if vendor_name:
        vendor_key = vendor_name.strip().lower().replace(" ", "_")
        result.update(user_fields.get(f"vendor:{vendor_key}", []))

    return sorted(result)


def _scope_description(scope: str) -> str:
    """Human-readable description of a scope."""
    if scope == "always":
        return "all future invoices"
    if scope.startswith("industry:"):
        return f"{scope.split(':')[1]} industry invoices"
    if scope.startswith("vendor:"):
        return f"invoices from {scope.split(':')[1]}"
    if scope.startswith("country:"):
        return f"invoices from {scope.split(':')[1]}"
    return f"'{scope}' scoped invoices"
