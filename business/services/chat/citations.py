"""
Chat Citation Formatting.

This module handles citation formatting for chat search results.
Part of the BUSINESS layer - chat services.
"""

from typing import Any, Dict, List


def format_citations(hits: List[Dict[str, Any]], max_items: int = 5) -> str:
    """Format search hits as citations for display.

    Args:
        hits: List of search hit documents
        max_items: Maximum number of citations to format (default: 5)

    Returns:
        Formatted citation string with video_id:chunk_id and scores
    """
    items: List[str] = []
    seen: set[str] = set()

    for h in hits:
        vid = str(h.get("video_id"))
        cid = str(h.get("chunk_id"))
        key = f"{vid}:{cid}"

        if key in seen:
            continue
        seen.add(key)

        score = h.get("final_score") or h.get("score") or h.get("search_score")
        items.append(
            f"({key}) score={score:.3f}"
            if isinstance(score, (int, float))
            else f"({key})"
        )

        if len(items) >= max_items:
            break

    return "\n".join(items)
