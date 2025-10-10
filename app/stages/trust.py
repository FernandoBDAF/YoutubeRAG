import math
from typing import Any, Dict

from dotenv import load_dotenv
from pymongo import MongoClient
import os

try:
    from app.services.utils import get_mongo_client
except ModuleNotFoundError:
    import sys as _sys, os as _os

    _sys.path.append(
        _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
    )
    from app.services.utils import get_mongo_client
from config.paths import DB_NAME, COLL_CHUNKS


def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def compute_trust_score(chunk: Dict[str, Any]) -> float:
    redundancy = float(chunk.get("redundancy_score", 0.0) or 0.0)
    is_redundant = bool(chunk.get("is_redundant", False))
    engagement = float(chunk.get("metadata", {}).get("engagement_norm", 0.0) or 0.0)
    recency_days = float(chunk.get("metadata", {}).get("age_days", 365) or 365)

    consensus = redundancy if is_redundant else 0.5 * redundancy
    recency_component = sigmoid(max(-6.0, min(6.0, (180.0 - recency_days) / 60.0)))
    engagement_component = max(0.0, min(1.0, engagement))

    w1, w2, w3, w4 = 0.4, 0.3, 0.2, 0.1
    code_valid = 1.0 if chunk.get("metadata", {}).get("code_present") else 0.6
    score = (
        w1 * consensus
        + w2 * recency_component
        + w3 * engagement_component
        + w4 * code_valid
    )
    return max(0.0, min(1.0, score))


def main() -> None:
    load_dotenv()
    use_llm = False
    try:
        import os as _os

        use_llm = _os.getenv("TRUST_WITH_LLM") == "1" or "--llm" in _os.sys.argv
        auto_llm = _os.getenv("TRUST_LLM_AUTO", "true").lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        try:
            band_low = float(_os.getenv("TRUST_LLM_BAND_LOW", "0.40"))
        except Exception:
            band_low = 0.40
        try:
            band_high = float(_os.getenv("TRUST_LLM_BAND_HIGH", "0.70"))
        except Exception:
            band_high = 0.70
        try:
            neigh = int(_os.getenv("TRUST_LLM_NEIGHBORS", "2"))
        except Exception:
            neigh = 2
    except Exception:
        auto_llm, band_low, band_high, neigh = True, 0.40, 0.70, 2
    client: MongoClient = get_mongo_client()
    db = client[DB_NAME]
    coll = db[COLL_CHUNKS]
    skip_existing = str(os.getenv("TRUST_UPSERT_EXISTING", "false")).lower() not in {
        "1",
        "true",
        "yes",
        "on",
    }
    for c in coll.find(
        {},
        {
            "video_id": 1,
            "chunk_id": 1,
            "metadata": 1,
            "is_redundant": 1,
            "redundancy_score": 1,
            "text": 1,
            "embedding": 1,
        },
    ):
        if use_llm:
            try:
                from agents.trust_agent import TrustRankAgent

                payload = {
                    "chunk_text": c.get("text", ""),
                    "similar_chunks": [],
                    "channel_metrics": {},
                    "published_at": None,
                    "code_valid": bool(c.get("metadata", {}).get("code_present")),
                }
                # Heuristic first
                heuristic_score = compute_trust_score(c)
                do_llm = True
                if not (_os.getenv("TRUST_WITH_LLM") == "1" or "--llm" in _os.sys.argv):
                    # decide by auto trigger
                    do_llm = auto_llm and (
                        band_low
                        <= float(c.get("redundancy_score", 0.0) or 0.0)
                        <= band_high
                        or bool(c.get("metadata", {}).get("code_present"))
                        or float(c.get("metadata", {}).get("age_days", 365) or 365) < 30
                    )
                score = heuristic_score
                method = "heuristic"
                if do_llm:
                    # find top-N similar neighbors in same video by cosine
                    try:
                        from math import sqrt

                        vid = c.get("video_id")
                        base = c.get("embedding", [])
                        neigh_docs = list(
                            coll.find(
                                {"video_id": vid},
                                {"chunk_id": 1, "text": 1, "embedding": 1},
                            ).limit(50)
                        )
                        sims = []

                        def _cos(a, b):
                            if not a or not b or len(a) != len(b):
                                return 0.0
                            s = sum(x * y for x, y in zip(a, b))
                            da = sqrt(sum(x * x for x in a)) or 1.0
                            db = sqrt(sum(y * y for y in b)) or 1.0
                            return s / (da * db)

                        for d in neigh_docs:
                            if d.get("chunk_id") == c.get("chunk_id"):
                                continue
                            sims.append((d, _cos(base, d.get("embedding", []))))
                        sims.sort(key=lambda x: x[1], reverse=True)
                        topn = [
                            {
                                "chunk_id": d.get("chunk_id"),
                                "text": (d.get("text", "")[:500]),
                            }
                            for d, _ in sims[: max(0, neigh)]
                        ]
                        payload["similar_chunks"] = topn
                    except Exception:
                        pass
                    agent = TrustRankAgent()
                    out = agent.score(payload)
                    s = out.get("trust_score")
                    if s is not None:
                        score = s
                        method = "llm"
            except Exception:
                score = compute_trust_score(c)
                method = "heuristic"
        else:
            score = compute_trust_score(c)
            method = "heuristic"
        if skip_existing:
            existing = coll.find_one({"_id": c["_id"]}, {"trust_score": 1})
            if existing and "trust_score" in existing:
                continue
        coll.update_one(
            {"_id": c["_id"]},
            {"$set": {"trust_score": float(score), "trust_method": method}},
        )
    print(f"Trust scores updated. (llm={use_llm})")


if __name__ == "__main__":
    main()
