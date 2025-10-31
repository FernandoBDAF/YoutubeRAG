"""
Chat Retrieval Orchestration.

This module orchestrates retrieval across different search modes for chat.
Part of the BUSINESS layer - chat feature logic.
"""

import logging
from typing import Any, Dict, List, Optional

from dependencies.database.mongodb import get_mongo_client
from core.config.paths import DB_NAME, COLL_CHUNKS
from business.services.rag.retrieval import vector_search, hybrid_search, keyword_search
from business.services.rag.indexes import ensure_vector_search_index
from business.services.rag.core import embed_query


def run_retrieval(
    mode: str,
    query_text: str,
    top_k: int,
    filters: Optional[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Run retrieval using specified mode.

    Args:
        mode: Retrieval mode ('vector', 'hybrid', 'keyword', 'auto')
        query_text: Query text
        top_k: Number of results to retrieve
        filters: Optional filters for search

    Returns:
        List of search hit documents

    Note:
        - Hybrid mode only works without filters (knnBeta limitation)
        - When filters present, falls back to vector search
        - Ensures indexes exist on first call
    """
    client = get_mongo_client()
    db = client[DB_NAME]
    col = db[COLL_CHUNKS]

    # Ensure indexes exist once at first retrieval (silent if exists)
    prev_level = logging.getLogger("pymongo").level
    logging.getLogger("pymongo").setLevel(logging.WARNING)
    ensure_vector_search_index(col)
    logging.getLogger("pymongo").setLevel(prev_level)

    # Use hybrid only when no filters (knnBeta + $search filters use different syntax)
    # When filters present, use vector-only $vectorSearch which accepts our filter format
    if mode == "hybrid" and not filters:
        # hybrid_search expects both query_text and query_vector
        qvec = embed_query(query_text)
        return hybrid_search(
            col, query_text=query_text, query_vector=qvec, top_k=top_k, filters=None
        )
    elif mode == "keyword":
        return keyword_search(col, query_text=query_text, top_k=top_k, filters=filters)
    else:
        # vector or auto->vector by default; also used when filters are present
        qvec = embed_query(query_text)
        return vector_search(col, qvec, k=top_k, filters=filters)


def normalize_context_blocks(hits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Ensure context blocks have consistent field structure for answer composition.

    Args:
        hits: List of search hit documents

    Returns:
        Normalized hit documents with 'embedding_text' field

    Note:
        If only 'text' exists, mirrors into 'embedding_text' for answer helper.
    """
    out: List[Dict[str, Any]] = []
    for h in hits:
        block = dict(h)
        # If only 'text' exists, mirror into 'embedding_text' for the answer helper
        if "embedding_text" not in block and "text" in block:
            block["embedding_text"] = block.get("text")
        out.append(block)
    return out
