"""Invoice Scanner — Multi-Agent Architecture.

Root agent (voice conversation) delegates to specialist sub-agents:

  invoice_scanner (root — talks to user)
    ├── tax_analyst        → detect regime, verify math, check compliance
    ├── field_specialist   → custom extraction, learning, uptraining
    └── data_manager       → sheets, export, search

The root agent handles the conversation. When it needs analysis,
it delegates to the appropriate specialist. ADK handles the routing.

Additionally, server-side parallel processing on upload runs
Document AI + regime detection + sheets logging concurrently
BEFORE the agent even starts talking.
"""

from google.adk.agents import Agent

from .config import MODEL_ID, SHEETS_ENABLED
from .prompts import SYSTEM_INSTRUCTION, TAX_ANALYST_INSTRUCTION, FIELD_SPECIALIST_INSTRUCTION, DATA_MANAGER_INSTRUCTION
from .services import get_search_tool
from .tools.invoice_parser import (
    parse_invoice,
    get_invoice_data,
)
from .tools.tax_engine import (
    detect_invoice_type,
    validate_compliance,
    verify_tax_math,
)
from .tools.web_search import (
    fetch_tax_page,
    get_tax_authority_url,
)
from .tools.custom_extractor import (
    extract_custom_fields,
    list_industry_fields,
)
from .tools.field_learning import (
    learn_field,
    forget_field,
    get_learned_fields,
)
from .tools.auto_uptrainer import (
    correct_extraction,
    get_training_status,
    trigger_uptraining,
)
from .tools.fraud_detector import check_duplicate
from .tools.smart_extraction import check_confidence_and_escalate
from .recipe_mcp import manage_recipes
from .tools.sheets import add_to_spreadsheet, add_remark, get_spreadsheet_summary

# Overlay control store — the agent writes, WebSocket downstream reads
_overlay_commands: list = []


def highlight_fields(fields: str, action: str = "show") -> dict:
    """Control what fields are highlighted on the invoice overlay.

    Use this to visually point out specific fields to the user.
    The overlay draws labeled bounding boxes on the invoice image.

    Args:
        fields: Comma-separated field names to highlight.
                E.g., "total_amount,supplier_name,invoice_id"
                Or "all" to show everything, or "none" to hide overlay.
        action: "show" to highlight specific fields,
                "show_all" to show everything,
                "hide" to clear the overlay.

    Returns:
        Confirmation of what's being highlighted.
    """
    if fields == "all":
        action = "show_all"
    elif fields == "none":
        action = "hide"

    cmd = {"action": action}
    if action == "show":
        cmd["fields"] = [f.strip() for f in fields.split(",")]

    _overlay_commands.append(cmd)

    return {
        "status": "ok",
        "action": action,
        "fields": cmd.get("fields", []),
        "message": f"Overlay updated: {action}",
    }


def build_agent() -> Agent:
    """Build multi-agent system with sub-agents.

    Root agent has NO tools — only delegates via transfer_to_agent.
    Each sub-agent lists its own tools in its own prompt.
    This prevents the root from hallucinating direct tool calls.

    All tools are imported above — uncomment to re-enable.
    """

    # ── Tax Analyst ───────────────────────────────────────────────────
    tax_analyst = Agent(
        name="tax_analyst",
        model=MODEL_ID,
        description="Tax regime detection, tax math verification, and duplicate/fraud checks.",
        instruction=TAX_ANALYST_INSTRUCTION,
        tools=[
            detect_invoice_type,
            verify_tax_math,
            check_duplicate,
            # ── Available but disabled for speed ──
            # validate_compliance,
            # fetch_tax_page,
            # get_tax_authority_url,
        ],
    )

    # ── Data Manager ──────────────────────────────────────────────────
    data_tools = [
        parse_invoice,
        highlight_fields,
        extract_custom_fields,
    ]
    if SHEETS_ENABLED:
        data_tools.append(add_to_spreadsheet)
        # ── Available but disabled for speed ──
        # data_tools.extend([add_remark, get_spreadsheet_summary])

    search_tool = get_search_tool()
    if search_tool:
        data_tools.append(search_tool)

    data_manager = Agent(
        name="data_manager",
        model=MODEL_ID,
        description="Invoice parsing, custom field extraction, Google Sheets logging, field highlighting, and invoice search.",
        instruction=DATA_MANAGER_INSTRUCTION,
        tools=data_tools,
    )

    # ═══════════════════════════════════════════════════════════════════
    # Choose ONE of the three options below. Comment out the others.
    # ═══════════════════════════════════════════════════════════════════

    # ── OPTION 1: Minimal (current) — no tools, pure voice ───────────
    # Fastest response. Agent just reads images and talks.
    return Agent(
        name="invoice_scanner",
        model=MODEL_ID,
        description="Voice-powered invoice scanning assistant.",
        instruction=SYSTEM_INSTRUCTION,
        tools=[],
    )

    # ── OPTION 2: Sub-agents — root delegates via transfer_to_agent ──
    # Root has parse_invoice only. Tax/data work goes to sub-agents.
    # return Agent(
    #     name="invoice_scanner",
    #     model=MODEL_ID,
    #     description="Voice-powered invoice scanning assistant.",
    #     instruction=SYSTEM_INSTRUCTION,
    #     tools=[parse_invoice],
    #     sub_agents=[tax_analyst, data_manager],
    # )

    # ── OPTION 3: Flat — all tools on root, no sub-agents ────────────
    # Most tools available, but larger setup payload.
    # all_tools = [
    #     detect_invoice_type, verify_tax_math, check_duplicate,
    #     parse_invoice, highlight_fields, extract_custom_fields,
    # ]
    # if SHEETS_ENABLED: all_tools.append(add_to_spreadsheet)
    # st = get_search_tool()
    # if st: all_tools.append(st)
    # return Agent(
    #     name="invoice_scanner",
    #     model=MODEL_ID,
    #     description="Voice-powered invoice scanning assistant.",
    #     instruction=SYSTEM_INSTRUCTION,
    #     tools=all_tools,
    # )


root_agent = build_agent()
