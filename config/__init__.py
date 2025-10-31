"""Configuration module for YoutubeRAG."""

# Database and collection constants
from core.config.paths import (
    DB_NAME,
    COLL_RAW_VIDEOS,
    COLL_CLEANED,
    COLL_ENRICHED,
    COLL_MULTIMODAL,
    COLL_CHUNKS,
    COLL_MEMORY_LOGS,
    COLL_VIDEO_FEEDBACK,
    COLL_CHUNK_FEEDBACK,
    COLL_ENTITIES,
    COLL_RELATIONS,
    COLL_COMMUNITIES,
    COLL_ENTITY_MENTIONS,
    VECTOR_INDEX_NAME,
    VECTOR_PATH,
    VECTOR_DIM,
    VECTOR_SIMILARITY,
)

# Runtime configuration
from core.config.runtime import (
    MAX_RETRIES,
    WORDS_PER_MINUTE,
    RAG_WEIGHT_VECTOR,
    RAG_WEIGHT_TRUST,
    RAG_WEIGHT_RECENCY,
)

# Stage configuration
from core.models.config import BaseStageConfig

# GraphRAG configuration
from core.config.graphrag import (
    GraphExtractionConfig,
    EntityResolutionConfig,
    GraphConstructionConfig,
    CommunityDetectionConfig,
    GraphRAGQueryConfig,
    GraphRAGPipelineConfig,
)

__all__ = [
    # Paths
    "DB_NAME",
    "COLL_RAW_VIDEOS",
    "COLL_CLEANED",
    "COLL_ENRICHED",
    "COLL_MULTIMODAL",
    "COLL_CHUNKS",
    "COLL_MEMORY_LOGS",
    "COLL_VIDEO_FEEDBACK",
    "COLL_CHUNK_FEEDBACK",
    "COLL_ENTITIES",
    "COLL_RELATIONS",
    "COLL_COMMUNITIES",
    "COLL_ENTITY_MENTIONS",
    "VECTOR_INDEX_NAME",
    "VECTOR_PATH",
    "VECTOR_DIM",
    "VECTOR_SIMILARITY",
    # Runtime
    "MAX_RETRIES",
    "WORDS_PER_MINUTE",
    "RAG_WEIGHT_VECTOR",
    "RAG_WEIGHT_TRUST",
    "RAG_WEIGHT_RECENCY",
    # Stage Config
    "BaseStageConfig",
    # GraphRAG Config
    "GraphExtractionConfig",
    "EntityResolutionConfig",
    "GraphConstructionConfig",
    "CommunityDetectionConfig",
    "GraphRAGQueryConfig",
    "GraphRAGPipelineConfig",
]
