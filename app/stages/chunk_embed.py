import os
from typing import Any, Dict, List

import requests
import time
from dotenv import load_dotenv
from pymongo import MongoClient

try:
    from app.services.utils import get_mongo_client
except ModuleNotFoundError:
    import sys as _sys, os as _os

    _sys.path.append(
        _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
    )
    from app.services.utils import get_mongo_client
from app.services.rate_limit import RateLimiter
from config.paths import (
    DB_NAME,
    COLL_ENRICHED,
    COLL_CHUNKS,
    VECTOR_DIM,
)


def chunk_text_segments(
    segments: List[Dict[str, Any]], target_tokens: int = 500
) -> List[Dict[str, Any]]:
    chunks: List[Dict[str, Any]] = []
    current_text: List[str] = []
    current_count = 0
    for seg in segments:
        text = seg.get("text", "")
        tokens = max(1, len(text.split()))
        if current_count + tokens > target_tokens and current_text:
            chunks.append({"text": "\n\n".join(current_text)})
            # simple overlap: keep last sentence as seed
            tail = current_text[-1] if current_text else ""
            current_text = [tail] if tail else []
            current_count = max(1, len(tail.split())) if tail else 0
        current_text.append(text)
        current_count += tokens
    if current_text:
        chunks.append({"text": "\n\n".join(current_text)})
    return chunks


def embed_texts(texts: List[str]) -> List[List[float]]:
    api_key = os.getenv("VOYAGE_API_KEY")
    if not api_key:
        raise RuntimeError("VOYAGE_API_KEY is not set")
    model = os.getenv("VOYAGE_EMBED_MODEL", "voyage-2")
    # Rate limiter shared per process
    limiter = RateLimiter()
    # Try official client first (handles retries/rate limits)
    try:
        import voyageai  # type: ignore

        client = voyageai.Client(
            api_key=api_key,
            max_retries=int(os.getenv("VOYAGE_MAX_RETRIES", "4")),
            timeout=int(os.getenv("VOYAGE_TIMEOUT", "60")),
        )
        limiter.wait()
        res = client.embed(texts, model=model, input_type="document")
        return list(res.embeddings)
    except Exception:
        pass

    # Fallback to HTTP with exponential backoff
    max_retries = int(os.getenv("VOYAGE_MAX_RETRIES", "4"))
    backoff_base = float(os.getenv("VOYAGE_BACKOFF_BASE", "1.5"))

    for attempt in range(max_retries + 1):
        try:
            limiter.wait()
            r = requests.post(
                "https://api.voyageai.com/v1/embeddings",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={"model": model, "input": texts},
                timeout=60,
            )
            if r.status_code in (429, 500, 502, 503, 504):
                retry_after = r.headers.get("Retry-After")
                if retry_after:
                    try:
                        sleep_s = float(retry_after)
                    except Exception:
                        sleep_s = backoff_base**attempt
                else:
                    sleep_s = backoff_base**attempt
                if attempt < max_retries:
                    limiter.delay(max(0.5, min(30.0, sleep_s)))
                    time.sleep(max(0.5, min(30.0, sleep_s)))
                    continue
            r.raise_for_status()
            payload = r.json()
            if "data" in payload:
                return [v.get("embedding", []) for v in payload.get("data", [])]
            if "embeddings" in payload:
                return payload.get("embeddings", [])
            return []
        except requests.HTTPError as e:
            if (
                getattr(e.response, "status_code", 0) in (429, 500, 502, 503, 504)
                and attempt < max_retries
            ):
                time.sleep(max(0.5, min(30.0, backoff_base**attempt)))
                continue
            raise
        except Exception:
            if attempt < max_retries:
                time.sleep(max(0.5, min(15.0, backoff_base**attempt)))
                continue
            raise
    print("Voyage embeddings: exhausted retries; skipping batch")
    return []


def main() -> None:
    load_dotenv()
    use_llm = os.getenv("CHUNK_WITH_LLM") == "1" or "--llm" in os.sys.argv
    client: MongoClient = get_mongo_client()
    db = client[DB_NAME]
    enriched = db[COLL_ENRICHED]
    chunks_coll = db[COLL_CHUNKS]

    for doc in enriched.find({"segments": {"$exists": True, "$ne": []}}).limit(20):
        video_id = doc.get("video_id")
        segments = doc.get("segments", [])
        if not video_id or not segments:
            continue
        # try to fetch channel_id and published_at from raw_videos if present
        try:
            rv = db["raw_videos"].find_one(
                {"video_id": video_id}, {"channel_id": 1, "published_at": 1}
            )
        except Exception:
            rv = None
        if use_llm:
            try:
                from agents.chunk_agent import ChunkEmbedAgent

                agent = ChunkEmbedAgent()
                chunks_plain = agent.make_chunks(segments) or []
            except Exception:
                chunks_plain = chunk_text_segments(segments)
        else:
            chunks_plain = chunk_text_segments(segments)
        texts = [c["text"] for c in chunks_plain]
        vectors = embed_texts(texts) if texts else []
        # derive basic metadata proxies (MVP)
        # compute age_days if possible
        age_days = 180
        channel_id = None
        try:
            from datetime import datetime, timezone

            if rv and rv.get("published_at"):
                published = rv.get("published_at")
                if isinstance(published, str):
                    try:
                        published_dt = datetime.fromisoformat(
                            published.replace("Z", "+00:00")
                        )
                    except Exception:
                        published_dt = None
                else:
                    published_dt = published
                if published_dt:
                    now = datetime.now(timezone.utc)
                    age_days = max(0, int((now - published_dt).days))
            if rv and rv.get("channel_id"):
                channel_id = rv.get("channel_id")
        except Exception:
            pass
        code_present_any = any(bool(s.get("code_blocks")) for s in segments)
        tags_union: List[str] = sorted({t for s in segments for t in s.get("tags", [])})
        out_docs: List[Dict[str, Any]] = []
        for i, (text, vec) in enumerate(zip(texts, vectors), start=1):
            out_docs.append(
                {
                    "video_id": video_id,
                    "chunk_id": f"{video_id}:{i:04d}",
                    "text": text,
                    "metadata": {
                        "tags": tags_union,
                        "age_days": age_days,
                        "code_present": code_present_any,
                        "channel_id": channel_id,
                    },
                    "embedding": vec,
                    "embedding_model": "voyage-2",
                    "embedding_dim": VECTOR_DIM,
                }
            )
        if out_docs:
            # Upsert per chunk_id
            for d in out_docs:
                chunks_coll.update_one(
                    {"video_id": d["video_id"], "chunk_id": d["chunk_id"]},
                    {"$set": d},
                    upsert=True,
                )
            print(
                f"Chunked+Embedded {video_id}: {len(out_docs)} chunks (llm={use_llm})"
            )


if __name__ == "__main__":
    main()
