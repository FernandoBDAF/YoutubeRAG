import math
from typing import Any, Dict

from dotenv import load_dotenv
from pymongo import MongoClient

from utils import get_mongo_client
from config.paths import DB_NAME, COLL_CHUNKS


def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def compute_trust_score(chunk: Dict[str, Any]) -> float:
    # Simple heuristic per USE-CASE.md
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
    except Exception:
        pass
    client: MongoClient = get_mongo_client()
    db = client[DB_NAME]
    coll = db[COLL_CHUNKS]
    for c in coll.find(
        {}, {"metadata": 1, "is_redundant": 1, "redundancy_score": 1, "text": 1}
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
                agent = TrustRankAgent()
                out = agent.score(payload)
                score = out.get("trust_score")
                if score is None:
                    score = compute_trust_score(c)
            except Exception:
                score = compute_trust_score(c)
        else:
            score = compute_trust_score(c)
        coll.update_one({"_id": c["_id"]}, {"$set": {"trust_score": float(score)}})
    print(f"Trust scores updated. (llm={use_llm})")


if __name__ == "__main__":
    main()
