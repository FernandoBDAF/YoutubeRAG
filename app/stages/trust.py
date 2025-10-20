import math
from dataclasses import dataclass
from typing import Any, Dict

from dotenv import load_dotenv
from pymongo import MongoClient
import os

try:
    from app.services.utils import get_mongo_client
    from core.base_stage import BaseStage
    from core.stage_config import BaseStageConfig
except ModuleNotFoundError:
    import sys as _sys, os as _os

    _sys.path.append(
        _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
    )
    from app.services.utils import get_mongo_client
    from core.base_stage import BaseStage
    from core.stage_config import BaseStageConfig
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


@dataclass
class TrustConfig(BaseStageConfig):
    use_llm: bool = False
    auto_llm: bool = True
    band_low: float = 0.40
    band_high: float = 0.70
    neighbors: int = 2

    @classmethod
    def from_args_env(cls, args, env, default_db):
        base = BaseStageConfig.from_args_env(args, env, default_db)
        use_llm = bool(
            getattr(args, "llm", False) or (env.get("TRUST_WITH_LLM") == "1")
        )
        auto_llm = (env.get("TRUST_LLM_AUTO", "true") or "true").lower() in {
            "1",
            "true",
            "yes",
            "on",
        }

        def _getf(key: str, default: float) -> float:
            try:
                return float(env.get(key, str(default)))
            except Exception:
                return default

        band_low = _getf("TRUST_LLM_BAND_LOW", 0.40)
        band_high = _getf("TRUST_LLM_BAND_HIGH", 0.70)

        def _geti(key: str, default: int) -> int:
            try:
                return int(env.get(key, str(default)))
            except Exception:
                return default

        neighbors = _geti("TRUST_LLM_NEIGHBORS", 2)
        return cls(
            **vars(base),
            use_llm=use_llm,
            auto_llm=auto_llm,
            band_low=band_low,
            band_high=band_high,
            neighbors=neighbors
        )


class TrustStage(BaseStage):
    name = "trust"
    description = (
        "Compute trust scores with heuristic base and optional LLM for borderline cases"
    )
    ConfigCls = TrustConfig

    def iter_docs(self):
        src_db = self.config.read_db_name or self.config.db_name
        coll = self.get_collection(
            self.config.read_coll or COLL_CHUNKS, io="read", db_name=src_db
        )
        return list(
            coll.find(
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
            )
        )

    def handle_doc(self, c):
        dst_db = self.config.write_db_name or self.config.db_name
        coll = self.get_collection(
            self.config.write_coll or COLL_CHUNKS, io="write", db_name=dst_db
        )
        if self.config.use_llm:
            try:
                from agents.trust_agent import TrustRankAgent

                payload = {
                    "chunk_text": c.get("text", ""),
                    "similar_chunks": [],
                    "channel_metrics": {},
                    "published_at": None,
                    "code_valid": bool(c.get("metadata", {}).get("code_present")),
                }
                heuristic_score = compute_trust_score(c)
                do_llm = self.config.auto_llm and (
                    self.config.band_low
                    <= float(c.get("redundancy_score", 0.0) or 0.0)
                    <= self.config.band_high
                    or bool(c.get("metadata", {}).get("code_present"))
                    or float(c.get("metadata", {}).get("age_days", 365) or 365) < 30
                )
                score = heuristic_score
                method = "heuristic"
                if do_llm:
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
                        topn = []
                        for d, _ in sims[: max(0, self.config.neighbors)]:
                            topn.append(
                                {
                                    "chunk_id": d.get("chunk_id"),
                                    "text": (d.get("text", "")[:500]),
                                }
                            )
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
        if not self.config.upsert_existing:
            existing = coll.find_one({"_id": c["_id"]}, {"trust_score": 1})
            if existing and "trust_score" in existing:
                return
        coll.update_one(
            {"_id": c["_id"]},
            {"$set": {"trust_score": float(score), "trust_method": method}},
        )


if __name__ == "__main__":
    stage = TrustStage()
    raise SystemExit(stage.run())
