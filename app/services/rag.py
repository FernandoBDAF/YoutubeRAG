import os
from typing import Any, Dict, List, Optional

import requests
from pymongo import MongoClient

from app.services.utils import get_mongo_client
from app.services.rate_limit import RateLimiter
from config.paths import DB_NAME, COLL_CHUNKS, COLL_MEMORY_LOGS
from config.runtime import (
    RAG_WEIGHT_VECTOR,
    RAG_WEIGHT_TRUST,
    RAG_WEIGHT_RECENCY,
)


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


def answer_with_openai(contexts: List[Dict[str, Any]], question: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        joined = "\n\n".join(f"[ctx] {c.get('text','')[:500]}" for c in contexts)
        return f"Context (no LLM configured):\n\n{joined}"
    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        messages = [
            {
                "role": "system",
                "content": "You are a precise educational assistant. Answer using only the provided context. Cite (video_id:chunk_id).",
            },
            {
                "role": "user",
                "content": "Question: "
                + question
                + "\n\nContext:\n"
                + "\n\n".join(
                    f"({c.get('video_id')}:{c.get('chunk_id')})\n{c.get('text','')[:1200]}"
                    for c in contexts
                ),
            },
        ]
        resp = client.chat.completions.create(
            model=os.getenv("DEFAULT_MODEL", "gpt-4o-mini"), messages=messages
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        joined = "\n\n".join(f"[ctx] {c.get('text','')[:500]}" for c in contexts)
        return f"Context (LLM error: {e}):\n\n{joined}"


def rag_answer(
    query: str,
    k: int = 8,
    filters: Optional[Dict[str, Any]] = None,
    weights: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    client: MongoClient = get_mongo_client()
    db = client[DB_NAME]
    col = db[COLL_CHUNKS]
    logs = db[COLL_MEMORY_LOGS]

    qvec = embed_query(query)
    hits = vector_search(col, qvec, k=k, filters=filters)
    wv = (weights or {}).get("vector", RAG_WEIGHT_VECTOR)
    wt = (weights or {}).get("trust", RAG_WEIGHT_TRUST)
    wr = (weights or {}).get("recency", RAG_WEIGHT_RECENCY)
    total = max(1e-8, float(wv + wt + wr))
    hits = rerank_hits(
        hits, w_vector=wv / total, w_trust=wt / total, w_recency=wr / total
    )
    answer = answer_with_openai(hits, query)

    logs.insert_one(
        {
            "query": query,
            "retrieved": [
                {
                    "video_id": h.get("video_id"),
                    "chunk_id": h.get("chunk_id"),
                    "score": h.get("score"),
                }
                for h in hits
            ],
            "answer": answer,
        }
    )

    return {"answer": answer, "hits": hits}
