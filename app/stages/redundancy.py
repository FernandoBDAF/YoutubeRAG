import os
from typing import Any, Dict, List

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
from config.paths import DB_NAME, COLL_CHUNKS


def cosine(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    num = sum(x * y for x, y in zip(a, b))
    da = sum(x * x for x in a) ** 0.5
    db = sum(y * y for y in b) ** 0.5
    if da == 0.0 or db == 0.0:
        return 0.0
    return num / (da * db)


def main(threshold: float = 0.92, k: int = 8) -> None:
    load_dotenv()
    use_llm = os.getenv("DEDUP_WITH_LLM") == "1" or "--llm" in os.sys.argv
    client: MongoClient = get_mongo_client()
    db = client[DB_NAME]
    chunks = list(
        db[COLL_CHUNKS].find({}, {"video_id": 1, "chunk_id": 1, "embedding": 1})
    )
    by_video: Dict[str, List[Dict[str, Any]]] = {}
    for c in chunks:
        by_video.setdefault(c.get("video_id"), []).append(c)

    for video_id, items in by_video.items():
        for i, ci in enumerate(items):
            vi = ci.get("embedding", [])
            best_score = -1.0
            best = None
            for j, cj in enumerate(items):
                if i == j:
                    continue
                vj = cj.get("embedding", [])
                s = cosine(vi, vj)
                if s > best_score:
                    best_score = s
                    best = cj
            if use_llm and best is not None:
                try:
                    from agents.dedup_agent import DeduplicateAgent

                    from_text = db[COLL_CHUNKS].find_one(
                        {
                            "video_id": ci.get("video_id"),
                            "chunk_id": ci.get("chunk_id"),
                        },
                        {"text": 1},
                    )
                    to_text = db[COLL_CHUNKS].find_one(
                        {
                            "video_id": best.get("video_id"),
                            "chunk_id": best.get("chunk_id"),
                        },
                        {"text": 1},
                    )
                    agent = DeduplicateAgent()
                    verdict = agent.is_redundant(
                        (from_text or {}).get("text", ""),
                        (to_text or {}).get("text", ""),
                    )
                    is_dup = bool(verdict.get("redundant", False)) or (
                        best_score >= threshold
                    )
                except Exception:
                    is_dup = best_score >= threshold
            else:
                is_dup = best_score >= threshold
            db[COLL_CHUNKS].update_one(
                {"video_id": ci.get("video_id"), "chunk_id": ci.get("chunk_id")},
                {
                    "$set": {
                        "is_redundant": bool(is_dup),
                        "duplicate_of": (
                            f"{best.get('video_id')}:{best.get('chunk_id')}"
                            if best
                            else None
                        ),
                        "redundancy_score": float(best_score),
                    }
                },
                upsert=False,
            )
        print(f"Redundancy pass done for video {video_id} (llm={use_llm})")


if __name__ == "__main__":
    main()
