import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from pymongo import MongoClient

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
import os


def cosine(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    num = sum(x * y for x, y in zip(a, b))
    da = sum(x * x for x in a) ** 0.5
    db = sum(y * y for y in b) ** 0.5
    if da == 0.0 or db == 0.0:
        return 0.0
    return num / (da * db)


@dataclass
class RedundancyConfig(BaseStageConfig):
    threshold: float = 0.92
    llm_margin: float = 0.03
    nonadj_fallback: bool = True
    adj_override: float = 0.975
    skip_adjacent: bool = True
    use_llm: bool = False

    @classmethod
    def from_args_env(cls, args, env, default_db):
        base = BaseStageConfig.from_args_env(args, env, default_db)
        use_llm = bool(
            getattr(args, "llm", False)
            or (env.get("REDUNDANCY_WITH_LLM") == "1")
            or (env.get("DEDUP_WITH_LLM") == "1")
        )

        def _getf(keys: List[str], default: float) -> float:
            for k in keys:
                v = env.get(k)
                if v is not None:
                    try:
                        return float(v)
                    except Exception:
                        pass
            return default

        def _getb(keys: List[str], default: bool) -> bool:
            for k in keys:
                v = env.get(k)
                if v is not None:
                    if str(v).strip().lower() in {"1", "true", "yes", "on"}:
                        return True
                    if str(v).strip().lower() in {"0", "false", "no", "off"}:
                        return False
            return default

        threshold = _getf(["REDUNDANCY_THRESHOLD", "DEDUP_THRESHOLD"], 0.92)
        llm_margin = _getf(["REDUNDANCY_LLM_MARGIN", "DEDUP_LLM_MARGIN"], 0.03)
        nonadj_fallback = _getb(
            ["REDUNDANCY_NONADJ_FALLBACK", "DEDUP_NONADJ_FALLBACK"], True
        )
        adj_override = _getf(["REDUNDANCY_ADJ_OVERRIDE", "DEDUP_ADJ_OVERRIDE"], 0.975)
        skip_adjacent = _getb(["REDUNDANCY_SKIP_ADJACENT", "DEDUP_SKIP_ADJACENT"], True)
        return cls(
            **vars(base),
            threshold=threshold,
            llm_margin=llm_margin,
            nonadj_fallback=nonadj_fallback,
            adj_override=adj_override,
            skip_adjacent=skip_adjacent,
            use_llm=use_llm,
        )


class RedundancyStage(BaseStage):
    name = "redundancy"
    description = (
        "Mark redundant chunks using cosine, adjacency guard, and optional LLM."
    )
    ConfigCls = RedundancyConfig

    def iter_docs(self):
        src_db = self.config.read_db_name or self.config.db_name
        coll = self.get_collection(
            self.config.read_coll or COLL_CHUNKS, io="read", db_name=src_db
        )
        chunks = list(coll.find({}, {"video_id": 1, "chunk_id": 1, "embedding": 1}))
        by_video: Dict[str, List[Dict[str, Any]]] = {}
        for c in chunks:
            by_video.setdefault(c.get("video_id"), []).append(c)
        return [{"video_id": vid, "items": items} for vid, items in by_video.items()]

    def handle_doc(self, group):
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
            # If best is adjacent and we skip adjacency, optionally choose best non-adjacent
            if best is not None and self.config.skip_adjacent:
                try:

                    def _suffix_num(cid: str) -> int:
                        parts = (cid or "").split(":")
                        return (
                            int(parts[-1])
                            if parts and parts[-1].isdigit()
                            else -(10**9)
                        )

                    this_n = _suffix_num(str(ci.get("chunk_id")))
                    best_n = _suffix_num(str(best.get("chunk_id")))
                    best_is_adj = (
                        ci.get("video_id") == best.get("video_id")
                        and abs(this_n - best_n) == 1
                    )
                except Exception:
                    best_is_adj = False
                if best_is_adj and self.config.nonadj_fallback:
                    alt_best = None
                    alt_score = -1.0
                    for j, cj in enumerate(items):
                        if i == j:
                            continue
                        vj = cj.get("embedding", [])
                        s = cosine(vi, vj)
                        try:
                            n = _suffix_num(str(cj.get("chunk_id")))
                            if (
                                ci.get("video_id") == cj.get("video_id")
                                and abs(this_n - n) == 1
                            ):
                                continue
                        except Exception:
                            pass
                        if s > alt_score:
                            alt_score = s
                            alt_best = cj
                    if alt_best is not None:
                        best = alt_best
                        best_score = alt_score
            method = "cosine"
            reason = "high_sim" if best_score >= self.config.threshold else None
            is_dup = best_score >= self.config.threshold
            # Trigger LLM only for borderline cases around threshold
            borderline = (
                abs(best_score - self.config.threshold) <= self.config.llm_margin
            )
            if self.config.use_llm and best is not None and borderline:
                try:
                    from agents.dedup_agent import DeduplicateAgent

                    from_text = coll.find_one(
                        {
                            "video_id": ci.get("video_id"),
                            "chunk_id": ci.get("chunk_id"),
                        },
                        {"text": 1},
                    )
                    to_text = coll.find_one(
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
                        best_score >= self.config.threshold
                    )
                    method = "llm"
                    reason = "borderline"
                except Exception:
                    is_dup = best_score >= self.config.threshold
            # Adjacency guard: skip duplicates when best is immediate neighbor
            if is_dup and best is not None and self.config.skip_adjacent:
                try:

                    def _suffix_num(cid: str) -> int:
                        # chunk_id format: <video_id>:NNNN
                        parts = (cid or "").split(":")
                        return (
                            int(parts[-1])
                            if parts and parts[-1].isdigit()
                            else -(10**9)
                        )

                    this_n = _suffix_num(str(ci.get("chunk_id")))
                    best_n = _suffix_num(str(best.get("chunk_id")))
                    if (
                        ci.get("video_id") == best.get("video_id")
                        and abs(this_n - best_n) == 1
                        and best_score < self.config.adj_override
                    ):
                        is_dup = False
                        reason = None
                except Exception:
                    pass

            # Canonicalization: make lexicographically smaller chunk the primary
            primary_chunk_id = None
            if is_dup and best is not None:
                try:
                    a = str(ci.get("chunk_id"))
                    b = str(best.get("chunk_id"))
                    primary_chunk_id = min(a, b)
                    if a == primary_chunk_id:
                        # current is primary → keep it non-redundant
                        is_dup = False
                        reason = None
                except Exception:
                    primary_chunk_id = best.get("chunk_id") if best else None

            if not self.config.upsert_existing:
                # Only update when fields are missing
                existing = coll.find_one(
                    {"video_id": ci.get("video_id"), "chunk_id": ci.get("chunk_id")},
                    {"is_redundant": 1, "redundancy_score": 1},
                )
                if (
                    existing
                    and "is_redundant" in existing
                    and "redundancy_score" in existing
                ):
                    continue
            coll.update_one(
                {"video_id": ci.get("video_id"), "chunk_id": ci.get("chunk_id")},
                {
                    "$set": {
                        "is_redundant": bool(is_dup),
                        # store only peer chunk_id (no double video_id)
                        "duplicate_of": (
                            primary_chunk_id
                            if (
                                is_dup
                                and primary_chunk_id
                                and primary_chunk_id != ci.get("chunk_id")
                            )
                            else None
                        ),
                        "redundancy_score": float(best_score),
                        "redundancy_method": method,
                        "redundancy_reason": reason,
                    }
                },
                upsert=False,
            )
        print(f"Redundancy pass done for video {video_id} (llm={self.config.use_llm})")


if __name__ == "__main__":
    stage = RedundancyStage()
    raise SystemExit(stage.run())
