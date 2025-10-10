from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timezone

from config.paths import COLL_VIDEO_FEEDBACK, COLL_CHUNK_FEEDBACK


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _sanitize_tags(tags: Optional[List[str]]) -> List[str]:
    if not tags:
        return []
    cleaned: List[str] = []
    for t in tags[:10]:  # cap max 10
        s = (t or "").strip()
        if s:
            cleaned.append(s[:64])
    return cleaned


def upsert_video_feedback(
    db,
    session_id: str,
    video_id: str,
    rating: int,
    tags: Optional[List[str]] = None,
    note: Optional[str] = None,
) -> None:
    doc = {
        "session_id": session_id,
        "video_id": video_id,
        "rating": max(1, min(5, int(rating))),
        "tags": _sanitize_tags(tags),
        "note": (note or "")[:2000],
        "updated_at": _now(),
    }
    coll = db[COLL_VIDEO_FEEDBACK]
    coll.update_one(
        {"session_id": session_id, "video_id": video_id},
        {"$set": doc, "$setOnInsert": {"created_at": _now()}},
        upsert=True,
    )


def upsert_chunk_feedback(
    db,
    session_id: str,
    chunk_id: str,
    video_id: str,
    rating: int,
    tags: Optional[List[str]] = None,
    note: Optional[str] = None,
) -> None:
    doc = {
        "session_id": session_id,
        "chunk_id": chunk_id,
        "video_id": video_id,
        "rating": max(1, min(5, int(rating))),
        "tags": _sanitize_tags(tags),
        "note": (note or "")[:2000],
        "updated_at": _now(),
    }
    coll = db[COLL_CHUNK_FEEDBACK]
    coll.update_one(
        {"session_id": session_id, "chunk_id": chunk_id},
        {"$set": doc, "$setOnInsert": {"created_at": _now()}},
        upsert=True,
    )


def get_video_feedback_for_session(
    db, session_id: str, video_id: str
) -> Optional[Dict[str, Any]]:
    return db[COLL_VIDEO_FEEDBACK].find_one(
        {"session_id": session_id, "video_id": video_id}
    )


def get_chunk_feedback_for_session(
    db, session_id: str, chunk_id: str
) -> Optional[Dict[str, Any]]:
    return db[COLL_CHUNK_FEEDBACK].find_one(
        {"session_id": session_id, "chunk_id": chunk_id}
    )


def aggregate_video_feedback(db, video_id: str) -> Dict[str, Any]:
    cursor = db[COLL_VIDEO_FEEDBACK].aggregate(
        [
            {"$match": {"video_id": video_id}},
            {
                "$group": {
                    "_id": "$video_id",
                    "avg_rating": {"$avg": "$rating"},
                    "count": {"$sum": 1},
                    "all_tags": {"$push": "$tags"},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "avg_rating": 1,
                    "count": 1,
                    "tags": {
                        "$reduce": {
                            "input": "$all_tags",
                            "initialValue": [],
                            "in": {"$concatArrays": ["$$value", "$$this"]},
                        }
                    },
                }
            },
        ]
    )
    agg = next(cursor, None) or {"avg_rating": None, "count": 0, "tags": []}
    # compute top tags
    top_map: Dict[str, int] = {}
    for t in agg.get("tags", [])[:2000]:
        if t:
            top_map[t] = top_map.get(t, 0) + 1
    top = sorted(top_map.items(), key=lambda x: x[1], reverse=True)[:10]
    return {
        "avg_rating": agg.get("avg_rating"),
        "count": agg.get("count"),
        "top_tags": top,
    }


def aggregate_chunk_feedback(db, chunk_id: str) -> Dict[str, Any]:
    cursor = db[COLL_CHUNK_FEEDBACK].aggregate(
        [
            {"$match": {"chunk_id": chunk_id}},
            {
                "$group": {
                    "_id": "$chunk_id",
                    "avg_rating": {"$avg": "$rating"},
                    "count": {"$sum": 1},
                    "all_tags": {"$push": "$tags"},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "avg_rating": 1,
                    "count": 1,
                    "tags": {
                        "$reduce": {
                            "input": "$all_tags",
                            "initialValue": [],
                            "in": {"$concatArrays": ["$$value", "$$this"]},
                        }
                    },
                }
            },
        ]
    )
    agg = next(cursor, None) or {"avg_rating": None, "count": 0, "tags": []}
    top_map: Dict[str, int] = {}
    for t in agg.get("tags", [])[:2000]:
        if t:
            top_map[t] = top_map.get(t, 0) + 1
    top = sorted(top_map.items(), key=lambda x: x[1], reverse=True)[:10]
    return {
        "avg_rating": agg.get("avg_rating"),
        "count": agg.get("count"),
        "top_tags": top,
    }
