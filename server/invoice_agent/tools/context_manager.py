"""Context window management — compaction for long scanning sessions.

Problem: After scanning 50+ invoices with voice conversation, tool calls,
and grounding text, the context window fills up and the agent degrades.

Solution: Track approximate context usage. When threshold is exceeded,
generate a compact summary of the session, then restart the live session
with the summary injected as initial context. Key state is preserved.

The compaction preserves:
- User preferences (currency, tax jurisdiction, business type)
- Learned fields (what extra fields to look for)
- Session statistics (total scanned, total amount, vendors seen)
- Last few invoices in detail (for continuity)
- Any active issues or follow-ups

The compaction discards:
- Old grounding text from early invoices (already in Sheets/Search)
- Intermediate tool call results
- Repetitive detection/verification outputs
"""

import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

# Approximate token counts for common operations
APPROX_TOKENS = {
    "system_prompt": 3000,
    "grounding_text": 800,
    "tool_call_result": 500,
    "voice_turn": 200,
    "image_frame": 1500,
}

# Threshold: trigger compaction when estimated tokens exceed this
# Gemini 2.5 Flash has 1M context, but we want to compact well before that
# to maintain response quality (models degrade as context fills)
COMPACTION_THRESHOLD = 120000  # ~120K tokens — compact at ~12% of 1M
KEEP_RECENT_INVOICES = 3  # Keep last N invoices in full detail


class ContextTracker:
    """Tracks approximate context usage and triggers compaction."""

    def __init__(self):
        self.estimated_tokens = APPROX_TOKENS["system_prompt"]
        self.invoice_count = 0
        self.tool_call_count = 0
        self.voice_turn_count = 0
        self.image_frame_count = 0
        self.compaction_count = 0

        # State to preserve across compaction
        self.invoices_summary: list[dict] = []  # All invoices seen
        self.recent_invoices: list[dict] = []  # Last N in full detail
        self.user_preferences: dict = {}
        self.vendors_seen: set = set()
        self.total_amount: float = 0.0
        self.currency: str = "USD"
        self.issues_flagged: list[str] = []

    def record_grounding(self, invoice_id: str, fields: dict, grounding_text: str):
        """Record a new invoice being processed."""
        self.estimated_tokens += APPROX_TOKENS["grounding_text"]
        self.invoice_count += 1

        # Extract key info for summary
        vendor = fields.get("supplier_name", {})
        vendor_name = vendor.get("value", "Unknown") if isinstance(vendor, dict) else str(vendor or "Unknown")
        total = fields.get("total_amount", {})
        total_val = total.get("value", "?") if isinstance(total, dict) else str(total or "?")
        date = fields.get("invoice_date", {})
        date_val = date.get("value", "?") if isinstance(date, dict) else str(date or "?")
        inv_num = fields.get("invoice_id", {})
        inv_num_val = inv_num.get("value", "?") if isinstance(inv_num, dict) else str(inv_num or "?")

        self.vendors_seen.add(vendor_name)

        invoice_summary = {
            "invoice_id": invoice_id,
            "vendor": vendor_name,
            "total": total_val,
            "date": date_val,
            "invoice_number": inv_num_val,
        }

        self.invoices_summary.append(invoice_summary)
        self.recent_invoices.append({
            **invoice_summary,
            "grounding_text": grounding_text,
        })

        # Keep only last N in full detail
        if len(self.recent_invoices) > KEEP_RECENT_INVOICES:
            self.recent_invoices = self.recent_invoices[-KEEP_RECENT_INVOICES:]

    def record_tool_call(self):
        """Record a tool call."""
        self.estimated_tokens += APPROX_TOKENS["tool_call_result"]
        self.tool_call_count += 1

    def record_voice_turn(self):
        """Record a voice interaction turn."""
        self.estimated_tokens += APPROX_TOKENS["voice_turn"]
        self.voice_turn_count += 1

    def record_image_frame(self):
        """Record a camera frame sent to the agent."""
        self.estimated_tokens += APPROX_TOKENS["image_frame"]
        self.image_frame_count += 1

    def record_issue(self, issue: str):
        """Record a flagged issue (fraud, compliance, etc.)."""
        self.issues_flagged.append(issue)

    def record_preference(self, key: str, value: str):
        """Record a user preference learned during the session."""
        self.user_preferences[key] = value

    def needs_compaction(self) -> bool:
        """Check if context should be compacted."""
        return self.estimated_tokens >= COMPACTION_THRESHOLD

    def get_session_summary(self) -> str:
        """Brief summary for re-injection on reconnect."""
        if not self.invoices_summary:
            return ""
        lines = [f"{self.invoice_count} invoices scanned this session:"]
        for inv in self.invoices_summary[-10:]:  # Last 10
            lines.append(f"- {inv['vendor']}: {inv['total']} ({inv['invoice_number']})")
        if self.issues_flagged:
            lines.append(f"Issues flagged: {', '.join(self.issues_flagged[-5:])}")
        return " ".join(lines)

    def get_stats(self) -> dict:
        """Get current context usage statistics."""
        return {
            "estimated_tokens": self.estimated_tokens,
            "threshold": COMPACTION_THRESHOLD,
            "usage_percent": round(self.estimated_tokens / COMPACTION_THRESHOLD * 100, 1),
            "invoices": self.invoice_count,
            "tool_calls": self.tool_call_count,
            "voice_turns": self.voice_turn_count,
            "compactions": self.compaction_count,
            "needs_compaction": self.needs_compaction(),
        }

    def generate_compaction_summary(self) -> str:
        """Generate a compact summary of the session for context restart.

        This summary becomes the initial context for the new session,
        preserving everything important while discarding bulk.
        """
        lines = [
            "[SESSION COMPACTION — Previous context was compacted to save space]",
            f"Compaction #{self.compaction_count + 1} at {datetime.now(timezone.utc).strftime('%H:%M UTC')}",
            "",
            f"## Session Summary ({self.invoice_count} invoices scanned)",
            f"- Total invoices: {self.invoice_count}",
            f"- Unique vendors: {len(self.vendors_seen)} ({', '.join(list(self.vendors_seen)[:10])}{'...' if len(self.vendors_seen) > 10 else ''})",
            f"- Tool calls made: {self.tool_call_count}",
            f"- Voice turns: {self.voice_turn_count}",
        ]

        # User preferences
        if self.user_preferences:
            lines.append("")
            lines.append("## User Preferences (remember these)")
            for k, v in self.user_preferences.items():
                lines.append(f"- {k}: {v}")

        # Learned fields
        from .field_learning import _learned_fields
        if _learned_fields:
            lines.append("")
            lines.append("## Learned Fields (auto-extract these)")
            for user_id, scopes in _learned_fields.items():
                for scope, fields in scopes.items():
                    lines.append(f"- {scope}: {', '.join(fields)}")

        # Issues flagged
        if self.issues_flagged:
            lines.append("")
            lines.append("## Issues Flagged (unresolved)")
            for issue in self.issues_flagged[-5:]:  # Last 5
                lines.append(f"- {issue}")

        # All invoices (brief)
        if self.invoices_summary:
            lines.append("")
            lines.append("## Invoice History (brief)")
            for inv in self.invoices_summary:
                lines.append(f"- {inv['invoice_number']} | {inv['vendor']} | {inv['total']} | {inv['date']}")

        # Recent invoices (full detail for continuity)
        if self.recent_invoices:
            lines.append("")
            lines.append(f"## Recent Invoices (last {len(self.recent_invoices)}, full detail)")
            for inv in self.recent_invoices:
                lines.append("")
                lines.append(inv.get("grounding_text", f"Invoice {inv['invoice_id']}: {inv['vendor']} {inv['total']}"))

        lines.append("")
        lines.append("[END SESSION COMPACTION — Continue the conversation naturally]")

        return "\n".join(lines)

    def compact(self) -> str:
        """Perform compaction and return the summary text.

        After calling this, the caller should:
        1. End the current live session
        2. Start a new session
        3. Inject this summary as initial context
        """
        summary = self.generate_compaction_summary()
        self.compaction_count += 1

        # Reset token estimate (summary + system prompt)
        old_tokens = self.estimated_tokens
        self.estimated_tokens = APPROX_TOKENS["system_prompt"] + len(summary) // 4  # ~4 chars per token

        logger.info(
            f"Context compacted: {old_tokens} → {self.estimated_tokens} tokens "
            f"(compaction #{self.compaction_count}, {self.invoice_count} invoices)"
        )

        return summary


# Global tracker per session (keyed by user_id)
_trackers: dict[str, ContextTracker] = {}


def get_tracker(user_id: str) -> ContextTracker:
    """Get or create a context tracker for a user session."""
    if user_id not in _trackers:
        _trackers[user_id] = ContextTracker()
    return _trackers[user_id]


def check_and_compact(user_id: str) -> Optional[str]:
    """Check if compaction is needed and perform it if so.

    Returns the compaction summary text if compacted, None otherwise.
    The caller should use this to restart the live session.
    """
    tracker = get_tracker(user_id)
    if tracker.needs_compaction():
        return tracker.compact()
    return None
