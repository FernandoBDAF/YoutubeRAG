from typing import List
from app.services.indexes import ensure_vector_search_index


REQUIRED_COLLECTIONS: List[str] = [
    "raw_videos",
    "video_chunks",
    "cleaned_transcripts",
    "enriched_transcripts",
    "memory_logs",
    "video_feedback",
    "chunk_feedback",
]


def ensure_collections_and_indexes(db) -> None:
    """Create base collections and the Vector Search index if missing.

    Uses Atlas CLI if available and PROJECT_ID/CLUSTER_NAME are set. Otherwise prints
    instructions to create the index via UI/CLI.
    """
    existing = set(db.list_collection_names())
    created_any = False
    for name in REQUIRED_COLLECTIONS:
        if name not in existing:
            db.create_collection(name)
            created_any = True

    # Ensure feedback indexes
    try:
        db["video_feedback"].create_index(
            [("video_id", 1), ("session_id", 1)], unique=True
        )
    except Exception:
        pass
    try:
        db["chunk_feedback"].create_index(
            [("chunk_id", 1), ("session_id", 1)], unique=True
        )
    except Exception:
        pass
    try:
        db["video_feedback"].create_index([("video_id", 1)])
        db["chunk_feedback"].create_index([("chunk_id", 1)])
    except Exception:
        pass

    # Ensure Vector Search index in code (single source of truth)
    try:
        ensure_vector_search_index(db["video_chunks"])
    except Exception as e:
        print(f"Warning: could not ensure vector index via code: {e}")


def wait_for_index_ready(
    index_name: str, timeout_s: int = 300, poll_s: int = 5
) -> None:
    return
