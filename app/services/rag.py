import os
from typing import Any, Dict, Iterable, List, Optional

import requests
from pymongo import MongoClient

from app.services.utils import get_mongo_client
from app.services.rate_limit import RateLimiter
from config.paths import DB_NAME, COLL_CHUNKS, COLL_MEMORY_LOGS
from config.runtime import RAG_WEIGHT_VECTOR, RAG_WEIGHT_TRUST, RAG_WEIGHT_RECENCY
from app.services.retrieval import vector_search, rerank_hits
from app.services.generation import answer_with_openai, stream_answer_with_openai
from app.services.retrieval import hybrid_search as _hybrid_search
import pandas as pd
from app.services.indexes import ensure_vector_search_index, ensure_hybrid_search_index


def embed_query(text: str) -> List[float]:
    api_key = os.getenv("VOYAGE_API_KEY")
    if not api_key:
        raise RuntimeError("VOYAGE_API_KEY is not set")
    model = os.getenv("VOYAGE_EMBED_MODEL", "voyage-2")
    limiter = RateLimiter()
    # Prefer official client
    try:
        import voyageai  # type: ignore

        client = voyageai.Client(
            api_key=api_key,
            max_retries=int(os.getenv("VOYAGE_MAX_RETRIES", "4")),
            timeout=int(os.getenv("VOYAGE_TIMEOUT", "30")),
        )
        limiter.wait()
        res = client.embed([text], model=model, input_type="query")
        return list(res.embeddings[0])
    except Exception:
        pass

    # Fallback HTTP
    limiter.wait()
    r = requests.post(
        "https://api.voyageai.com/v1/embeddings",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={"model": model, "input": [text]},
        timeout=30,
    )
    r.raise_for_status()
    payload = r.json()
    if "data" in payload:
        return payload["data"][0]["embedding"]
    if "embeddings" in payload:
        return payload["embeddings"][0]
    raise RuntimeError("Unexpected Voyage embeddings response shape")


def rag_answer(
    query: str,
    k: int = 8,
    filters: Optional[Dict[str, Any]] = None,
    weights: Optional[Dict[str, float]] = None,
    streaming: bool = False,
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    client: MongoClient = get_mongo_client()
    db = client[DB_NAME]
    col = db[COLL_CHUNKS]
    logs = db[COLL_MEMORY_LOGS]

    ensure_vector_search_index(col)
    # Hybrid index is useful for $search paths
    try:
        ensure_hybrid_search_index(col)
    except Exception:
        pass

    qvec = embed_query(query)
    hits = vector_search(col, qvec, k=k, filters=filters)

    hits_df = pd.DataFrame(hits)
    print(hits_df)

    # wv = (weights or {}).get("vector", RAG_WEIGHT_VECTOR)
    # wt = (weights or {}).get("trust", RAG_WEIGHT_TRUST)
    # wr = (weights or {}).get("recency", RAG_WEIGHT_RECENCY)
    # total = max(1e-8, float(wv + wt + wr))
    # hits = rerank_hits(
    #     hits, w_vector=wv / total, w_trust=wt / total, w_recency=wr / total
    # )
    if streaming:
        # For now, collect streamed tokens into a single string so UI remains simple
        buf: List[str] = []
        for token in stream_answer_with_openai(hits, query):
            buf.append(token)
        answer = "".join(buf)
    else:
        answer = answer_with_openai(hits, query)

    mode = "vector"  # base path for now; hybrid UI path remains separate
    # logs.insert_one(
    #     {
    #         "query": query,
    #         "mode": mode,
    #         "session_id": session_id,
    #         "weights": {"vector": wv, "trust": wt, "recency": wr},
    #         "retrieved": [
    #             {
    #                 "video_id": h.get("video_id"),
    #                 "chunk_id": h.get("chunk_id"),
    #                 "score": h.get("score"),
    #             }
    #             for h in hits
    #         ],
    #         "answer": answer,
    #     }
    # )

    return {"answer": answer, "hits": hits}


def rag_hybrid_answer(
    query: str,
    k: int = 8,
    filters: Optional[Dict[str, Any]] = None,
    weights: Optional[Dict[str, float]] = None,
    streaming: bool = False,
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    client: MongoClient = get_mongo_client()
    db = client[DB_NAME]
    col = db[COLL_CHUNKS]
    logs = db[COLL_MEMORY_LOGS]

    # Embed query for knnBeta path and pass full text for keyword path
    qvec = embed_query(query)
    hits = _hybrid_search(
        col, query_text=query, query_vector=qvec, top_k=k, filters=filters
    )

    # Normalize score field for rerank: use search_score as the base vector component
    for h in hits:
        if "score" not in h and "search_score" in h:
            h["score"] = h.get("search_score")

    wv = (weights or {}).get("vector", RAG_WEIGHT_VECTOR)
    wt = (weights or {}).get("trust", RAG_WEIGHT_TRUST)
    wr = (weights or {}).get("recency", RAG_WEIGHT_RECENCY)
    total = max(1e-8, float(wv + wt + wr))
    hits = rerank_hits(
        hits, w_vector=wv / total, w_trust=wt / total, w_recency=wr / total
    )

    if streaming:
        buf: List[str] = []
        for token in stream_answer_with_openai(hits, query):
            buf.append(token)
        answer = "".join(buf)
    else:
        answer = answer_with_openai(hits, query)

    logs.insert_one(
        {
            "query": query,
            "mode": "hybrid",
            "session_id": session_id,
            "weights": {"vector": wv, "trust": wt, "recency": wr},
            "retrieved": [
                {
                    "video_id": h.get("video_id"),
                    "chunk_id": h.get("chunk_id"),
                    "search_score": h.get("search_score"),
                    "keyword_score": h.get("keyword_score"),
                    "vector_score": h.get("vector_score"),
                }
                for h in hits
            ],
            "answer": answer,
        }
    )

    return {"answer": answer, "hits": hits}
