import os
from typing import Any, Dict, List, Optional

from config.runtime import (
    RAG_WEIGHT_VECTOR,
    RAG_WEIGHT_TRUST,
    RAG_WEIGHT_RECENCY,
)

from pymongo.collection import Collection


def hybrid_search(
    col: Collection,
    query_text: str,
    query_vector: List[float],
    top_k: int = 8,
    filters: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Run a hybrid Atlas Search query (text + knnBeta) with graceful fallback.

    If $search is unavailable or fails, falls back to vector-only search via $vectorSearch.
    """
    compound_should: List[Dict[str, Any]] = []
    if query_text and query_text.strip():
        compound_should.append(
            {"text": {"query": query_text, "path": ["text", "display_text"]}}
        )
    if query_vector:
        compound_should.append(
            {
                "knnBeta": {
                    "vector": query_vector,
                    "path": "embedding",
                    "k": max(1, int(top_k)),
                }
            }
        )
    if not compound_should:
        return []
    search_stage: Dict[str, Any] = {
        "$search": {"compound": {"should": compound_should}}
    }
    if filters:
        search_stage["$search"]["filter"] = filters

    # Include scoreDetails to approximate per-operator contributions when available
    pipeline = [
        search_stage,
        {
            "$project": {
                "video_id": 1,
                "chunk_id": 1,
                "text": {"$ifNull": ["$display_text", "$text"]},
                "metadata": 1,
                "trust_score": 1,
                "search_score": {"$meta": "searchScore"},
                "_sd": {"$meta": "searchScoreDetails"},
            }
        },
        {
            "$addFields": {
                "keyword_score": {
                    "$let": {
                        "vars": {"d": "$_sd"},
                        "in": {
                            "$cond": [
                                {"$gt": [{"$type": "$$d"}, "missing"]},
                                {"$ifNull": ["$$d.textScore", None]},
                                None,
                            ]
                        },
                    }
                },
                "vector_score": {
                    "$let": {
                        "vars": {"d": "$_sd"},
                        "in": {
                            "$cond": [
                                {"$gt": [{"$type": "$$d"}, "missing"]},
                                {"$ifNull": ["$$d.vectorSearchScore", None]},
                                None,
                            ]
                        },
                    }
                },
            }
        },
        {"$project": {"_sd": 0}},
        {"$limit": int(top_k)},
    ]
    try:
        return list(col.aggregate(pipeline))
    except Exception:
        # Fallback to vectorSearch only
        vs_pipeline = [
            {
                "$vectorSearch": {
                    "index": os.getenv("VECTOR_INDEX_NAME", "embedding_index"),
                    "path": "embedding",
                    "queryVector": query_vector,
                    "numCandidates": max(50, top_k * 10),
                    "limit": top_k,
                    "filter": filters or {},
                }
            },
            {
                "$project": {
                    "video_id": 1,
                    "chunk_id": 1,
                    "text": {"$ifNull": ["$display_text", "$text"]},
                    "metadata": 1,
                    "trust_score": 1,
                    "search_score": {"$meta": "vectorSearchScore"},
                    "vector_score": {"$meta": "vectorSearchScore"},
                    "keyword_score": None,
                }
            },
        ]
        return list(col.aggregate(vs_pipeline))


def keyword_search(
    col: Collection,
    query_text: str,
    top_k: int = 8,
    filters: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    if not (query_text and query_text.strip()):
        return []
    stage: Dict[str, Any] = {
        "$search": {
            "text": {
                "query": query_text,
                "path": ["text", "display_text"],
            }
        }
    }
    if filters:
        stage["$search"]["filter"] = filters
    pipeline = [
        stage,
        {
            "$project": {
                "video_id": 1,
                "chunk_id": 1,
                "text": {"$ifNull": ["$display_text", "$text"]},
                "metadata": 1,
                "trust_score": 1,
                "search_score": {"$meta": "searchScore"},
            }
        },
        {"$limit": int(top_k)},
    ]
    try:
        return list(col.aggregate(pipeline))
    except Exception:
        return []


def structured_search(
    col: Collection,
    filters: Optional[Dict[str, Any]] = None,
    sort_by: Optional[Dict[str, int]] = None,
    top_k: int = 8,
) -> List[Dict[str, Any]]:
    query = filters or {}
    projection = {
        "video_id": 1,
        "chunk_id": 1,
        "text": 1,
        "metadata": 1,
        "trust_score": 1,
    }
    try:
        cur = col.find(query, projection)
        if sort_by:
            cur = cur.sort(list(sort_by.items()))
        cur = cur.limit(int(top_k))
        return list(cur)
    except Exception:
        return []


def vector_search(
    col, query_vector: List[float], k: int = 8, filters: Optional[Dict[str, Any]] = None
):
    pipeline = [
        {
            "$vectorSearch": {
                "index": "embedding_index",
                "path": "embedding",
                "queryVector": query_vector,
                "numCandidates": 200,
                "limit": k,
                "filter": filters or {},
            }
        },
        {
            "$project": {
                "video_id": 1,
                "chunk_id": 1,
                "text": 1,
                "metadata": 1,
                "trust_score": 1,
                "score": {"$meta": "vectorSearchScore"},
            }
        },
    ]
    return list(col.aggregate(pipeline))


def rerank_hits(
    hits: List[Dict[str, Any]],
    w_vector: float = RAG_WEIGHT_VECTOR,
    w_trust: float = RAG_WEIGHT_TRUST,
    w_recency: float = RAG_WEIGHT_RECENCY,
) -> List[Dict[str, Any]]:
    ranked: List[Dict[str, Any]] = []
    for h in hits:
        meta = h.get("metadata", {})
        trust = float(h.get("trust_score", meta.get("trust_score", 0.5)) or 0.5)
        score = float(h.get("score", 0.0) or 0.0)
        age_days = float(meta.get("age_days", 180) or 180)
        recency = 1.0 / (1.0 + age_days / 180.0)
        final = w_vector * score + w_trust * trust + w_recency * recency
        h["final_score"] = final
        ranked.append(h)
    ranked.sort(key=lambda x: x.get("final_score", 0.0), reverse=True)
    return ranked
