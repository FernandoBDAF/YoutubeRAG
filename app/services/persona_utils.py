from typing import Dict, List


def infer_top_tags(db, session_id: str, limit: int = 5) -> List[str]:
    tag_counts: Dict[str, int] = {}
    for r in (
        db["video_feedback"].find({"session_id": session_id}, {"tags": 1}).limit(200)
    ):
        for t in r.get("tags", []) or []:
            t2 = (t or "").strip().lower().replace("_", "-")
            if t2:
                tag_counts[t2] = tag_counts.get(t2, 0) + 1
    return [
        t
        for t, _ in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[
            : int(limit)
        ]
    ]
