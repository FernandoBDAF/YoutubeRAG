"""
Chat Export Helpers.

This module handles exporting chat conversations to various formats.
Part of the BUSINESS layer - chat services.
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from core.libraries.serialization import json_encoder  # MongoDB type handling

try:
    from bson import ObjectId
    from bson.decimal128 import Decimal128
except Exception:
    ObjectId = None
    Decimal128 = None

from business.services.chat.citations import format_citations


def export_last_turn(
    last_turn: Optional[Dict[str, Any]], fmt: str, path: Optional[str], session_id: str
) -> Optional[str]:
    """Export the last conversation turn to a file.

    Args:
        last_turn: Last turn data (query, answer, hits, etc.)
        fmt: Export format ('json', 'txt', 'md')
        path: Optional export path (default: auto-generated)
        session_id: Session identifier for filename

    Returns:
        Path to exported file, or None if no turn to export
    """
    if not last_turn:
        return None

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    fmt = (fmt or "json").lower()

    if fmt in {"text", "plain"}:
        fmt = "txt"
    if fmt not in {"json", "txt", "md"}:
        fmt = "json"

    default_name = f"export_{session_id}_{ts}.{fmt}"
    if path:
        out_path = Path(path)
        if not out_path.suffix:
            out_path = out_path.with_suffix(f".{fmt}")
    else:
        out_path = Path(default_name)

    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Use centralized JSON encoder from serialization library (replaces manual to_plain)
    if fmt == "json":
        payload = {
            "session_id": session_id,
            **{k: v for k, v in last_turn.items()},
        }
        out_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, default=json_encoder),
            encoding="utf-8",
        )
    else:
        q = last_turn.get("user_query_raw", "")
        rq = last_turn.get("user_query_rewritten", "")
        mode = last_turn.get("mode", "")
        k = last_turn.get("k", "")
        filters = last_turn.get("filters", {})
        answer = last_turn.get("answer", "")
        citations = format_citations(last_turn.get("hits", []) or [])

        if fmt == "txt":
            content = (
                f"Session: {session_id}\n\n"
                f"Question: {q}\nRewritten: {rq}\nMode: {mode}  k={k}\nFilters: {json.dumps(filters)}\n\n"
                f"Answer:\n{answer}\n\nCitations:\n{citations}\n"
            )
        else:  # md
            content = (
                f"# Export — Session {session_id}\n\n"
                f"## Question\n{q}\n\n"
                f"## Rewritten\n{rq}\n\n"
                f"## Retrieval\n- Mode: `{mode}`  k={k}\n- Filters: `{json.dumps(filters)}`\n\n"
                f"## Answer\n\n{answer}\n\n"
                f"## Citations\n\n{citations}\n"
            )

        out_path.write_text(content, encoding="utf-8")

    return str(out_path)
