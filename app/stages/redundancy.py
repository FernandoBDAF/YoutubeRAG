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


def main(threshold: float = 0.92, k: int = 8) -> None:
    load_dotenv()
    use_llm = os.getenv("DEDUP_WITH_LLM") == "1" or "--llm" in os.sys.argv
    # Env-configurable parameters
    try:
        threshold = float(os.getenv("DEDUP_THRESHOLD", threshold))
    except Exception:
        pass
    try:
        llm_margin = float(os.getenv("DEDUP_LLM_MARGIN", 0.03))
    except Exception:
        llm_margin = 0.03
    # Tunables for adjacency handling
    nonadj_fallback = str(
        os.getenv("DEDUP_NONADJ_FALLBACK", "true")
    ).strip().lower() in {"1", "true", "yes", "on"}
    try:
        adj_override = float(os.getenv("DEDUP_ADJ_OVERRIDE", "0.975"))
    except Exception:
        adj_override = 0.975
    client: MongoClient = get_mongo_client()
    db = client[DB_NAME]
    chunks = list(
        db[COLL_CHUNKS].find({}, {"video_id": 1, "chunk_id": 1, "embedding": 1})
    )
    # If skipping updates for existing flags is desired, env can disable
    skip_existing = str(os.getenv("DEDUP_UPSERT_EXISTING", "false")).lower() not in {
        "1",
        "true",
        "yes",
        "on",
    }
    by_video: Dict[str, List[Dict[str, Any]]] = {}
    for c in chunks:
        by_video.setdefault(c.get("video_id"), []).append(c)

    skip_adjacent = str(os.getenv("DEDUP_SKIP_ADJACENT", "true")).strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }

    for video_id, items in by_video.items():
        # ensure deterministic order for canonicalization
        try:
            items.sort(key=lambda d: str(d.get("chunk_id", "")))
        except Exception:
            pass
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
            if best is not None and skip_adjacent:
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
                if best_is_adj and nonadj_fallback:
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
            reason = "high_sim" if best_score >= threshold else None
            is_dup = best_score >= threshold
            # Trigger LLM only for borderline cases around threshold
            borderline = abs(best_score - threshold) <= llm_margin
            if use_llm and best is not None and borderline:
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
                    method = "llm"
                    reason = "borderline"
                except Exception:
                    is_dup = best_score >= threshold
            # Adjacency guard: skip duplicates when best is immediate neighbor
            if is_dup and best is not None and skip_adjacent:
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
                        and best_score < adj_override
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

            if skip_existing:
                # Only update when fields are missing
                existing = db[COLL_CHUNKS].find_one(
                    {"video_id": ci.get("video_id"), "chunk_id": ci.get("chunk_id")},
                    {"is_redundant": 1, "redundancy_score": 1},
                )
                if (
                    existing
                    and "is_redundant" in existing
                    and "redundancy_score" in existing
                ):
                    continue
            db[COLL_CHUNKS].update_one(
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
        print(f"Redundancy pass done for video {video_id} (llm={use_llm})")


if __name__ == "__main__":
    main()
