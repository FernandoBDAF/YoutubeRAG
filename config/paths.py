"""
Centralized constants and lightweight helpers for the self-contained Mongo_Hack project.
This module must not import anything from outside Mongo_Hack/.
"""

import os
from typing import Final

# Database and collection names
DB_NAME: Final[str] = os.getenv("MONGODB_DB", "mongo_hack")

# Raw document collections - source-specific (one per document type)
# Each document type (YouTube, PDF, HTML, etc.) should have its own raw collection
# Examples: raw_videos, raw_pdfs, raw_html, etc.
COLL_RAW_VIDEOS: Final[str] = "raw_videos"
COLL_CLEANED: Final[str] = "cleaned_transcripts"
COLL_ENRICHED: Final[str] = "enriched_transcripts"
COLL_MULTIMODAL: Final[str] = "multimodal_segments"

# Unified chunks collection - contains chunks from all document sources
# All chunks should include a "source_type" field indicating origin (e.g., "youtube", "pdf", "html")
# and source-specific identifiers (e.g., "video_id" for YouTube, "document_id" for PDFs)
COLL_CHUNKS: Final[str] = (
    "video_chunks"  # Note: Consider renaming to "document_chunks" in future
)
COLL_MEMORY_LOGS: Final[str] = "memory_logs"
COLL_VIDEO_FEEDBACK: Final[str] = "video_feedback"
COLL_CHUNK_FEEDBACK: Final[str] = "chunk_feedback"

# GraphRAG collections
COLL_ENTITIES: Final[str] = "entities"
COLL_RELATIONS: Final[str] = "relations"
COLL_COMMUNITIES: Final[str] = "communities"
COLL_ENTITY_MENTIONS: Final[str] = "entity_mentions"

# Vector index constants
VECTOR_INDEX_NAME: Final[str] = "embedding_index"
VECTOR_PATH: Final[str] = "embedding"
VECTOR_DIM: Final[int] = 1024
VECTOR_SIMILARITY: Final[str] = "cosine"
