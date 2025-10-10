"""
Centralized constants and lightweight helpers for the self-contained Mongo_Hack project.
This module must not import anything from outside Mongo_Hack/.
"""

import os
from typing import Final

# Database and collection names
DB_NAME: Final[str] = os.getenv("MONGODB_DB", "mongo_hack")

COLL_RAW_VIDEOS: Final[str] = "raw_videos"
COLL_CLEANED: Final[str] = "cleaned_transcripts"
COLL_ENRICHED: Final[str] = "enriched_transcripts"
COLL_MULTIMODAL: Final[str] = "multimodal_segments"
COLL_CHUNKS: Final[str] = "video_chunks"
COLL_MEMORY_LOGS: Final[str] = "memory_logs"
COLL_VIDEO_FEEDBACK: Final[str] = "video_feedback"
COLL_CHUNK_FEEDBACK: Final[str] = "chunk_feedback"

# Vector index constants
VECTOR_INDEX_NAME: Final[str] = "embedding_index"
VECTOR_PATH: Final[str] = "embedding"
VECTOR_DIM: Final[int] = 1024
VECTOR_SIMILARITY: Final[str] = "cosine"
