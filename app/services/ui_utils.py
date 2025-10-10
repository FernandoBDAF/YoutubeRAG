from typing import Any, Dict, List, Optional


def rows_from_hits(
    hits: List[Dict[str, Any]], mode: str = "hybrid"
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for h in hits:
        row: Dict[str, Any] = {
            "video_id": h.get("video_id"),
            "chunk_id": h.get("chunk_id"),
            "text": (h.get("text", "") or "")[:160],
        }
        if mode == "vector":
            row["score"] = h.get("score")
        elif mode == "hybrid":
            row["search_score"] = h.get("search_score")
            if "keyword_score" in h:
                row["keyword_score"] = h.get("keyword_score")
            if "vector_score" in h:
                row["vector_score"] = h.get("vector_score")
        else:
            row["score"] = h.get("score") or h.get("search_score")
        meta = h.get("metadata", {}) or {}
        row["trust"] = h.get("trust_score")
        tags = meta.get("tags", []) or []
        row["tags"] = ", ".join(tags[:6])
        rows.append(row)
    return rows


def render_table_and_csv(name: str, rows: List[Dict[str, Any]]) -> Optional[bytes]:
    try:
        import pandas as pd  # type: ignore

        df = pd.DataFrame(rows)
        return df.to_csv(index=False).encode("utf-8")
    except Exception:
        return None
