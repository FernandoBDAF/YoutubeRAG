"""
Chat Filter Sanitization and Expansion.

This module handles filter sanitization for chat queries.
Part of the BUSINESS layer - chat services.
"""

from typing import Any, Dict, List, Optional

from business.services.ingestion.metadata import expand_filter_values


def sanitize_filters(
    raw: Optional[Dict[str, Any]], full_catalog: Optional[Dict[str, List[Any]]] = None
) -> Optional[Dict[str, Any]]:
    """Sanitize filters - expand patterns to exact matches from catalog.

    Since $vectorSearch.filter doesn't support $regex, we expand filter values
    to include all matching variants from the full catalog, then use simple $in.

    Example:
        "RAG" expands to ["RAG", "rag", "RAG framework", "Graph RAG", ...]

    Args:
        raw: Raw filters from query rewriter
        full_catalog: Full metadata catalog for expansion

    Returns:
        Sanitized filters dict or None if invalid

    Note:
        Only allows fields that are indexed for $vectorSearch filter.
    """
    if not isinstance(raw, dict) or not raw:
        return None

    # First expand filter values to include all semantic variants
    if full_catalog:
        expanded = expand_filter_values(raw, full_catalog)
    else:
        expanded = raw

    safe: Dict[str, Any] = {}

    # Only allow fields that are indexed for $vectorSearch filter
    allowed: Dict[str, str] = {
        "context.tags": "context.tags",
        "concepts.name": "concepts.name",
        "entities.name": "entities.name",
        "relations.subject": "relations.subject",
        "age_days": "metadata.age_days",
        "metadata.age_days": "metadata.age_days",
        "published_at": "published_at",
        "trust_score": "trust_score",
    }

    for k, v in expanded.items():
        key = allowed.get(k)
        if not key:
            continue

        # Coerce lists to $in, scalars to direct match
        if isinstance(v, list):
            scalars = [x for x in v if isinstance(x, (str, int, float, bool))]
            if scalars:
                safe[key] = {"$in": scalars}
        elif isinstance(v, (str, int, float, bool)):
            safe[key] = v

    return safe or None
