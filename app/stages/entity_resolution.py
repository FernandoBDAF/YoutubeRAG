"""
Entity Resolution Stage

This stage resolves and canonicalizes entities extracted from chunks.
It groups similar entities and stores resolved entities in the entities collection.
"""

import logging
import time
from typing import Dict, List, Any, Optional, Iterator
from pymongo.collection import Collection
from pymongo.database import Database
from core.base_stage import BaseStage
from config.graphrag_config import EntityResolutionConfig
from agents.entity_resolution_agent import EntityResolutionAgent
from core.graphrag_models import ResolvedEntity
from app.services.graphrag_indexes import get_graphrag_collections
from config.paths import COLL_CHUNKS

logger = logging.getLogger(__name__)


class EntityResolutionStage(BaseStage):
    """
    Stage for resolving and canonicalizing entities across chunks.
    """

    name = "entity_resolution"
    description = "Resolve and canonicalize entities across chunks"
    ConfigCls = EntityResolutionConfig

    def __init__(self):
        """Initialize the Entity Resolution Stage."""
        super().__init__()
        # Don't initialize agent here - will be done in setup()

    def setup(self):
        """Setup the stage with config-dependent initialization."""
        super().setup()

        # Initialize OpenAI client for LLM operations
        import os
        from openai import OpenAI

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is required for GraphRAG stages. Set it in .env file."
            )
        self.llm_client = OpenAI(api_key=api_key, timeout=60)

        # Initialize the resolution agent now that we have access to self.config
        self.resolution_agent = EntityResolutionAgent(
            llm_client=self.llm_client,
            model_name=self.config.model_name,
            temperature=self.config.temperature,
            similarity_threshold=self.config.similarity_threshold,
            max_retries=self.config.llm_retries,
            retry_delay=self.config.llm_backoff_s,
        )

        # Get GraphRAG collections
        self.graphrag_collections = get_graphrag_collections(self.db)

        logger.info(
            f"Initialized {self.name} with similarity threshold {self.config.similarity_threshold}"
        )

    def iter_docs(self) -> Iterator[Dict[str, Any]]:
        """
        Iterate over chunks that have completed entity extraction.

        Yields:
            Chunk documents that have been processed for entity extraction
        """
        src_db = self.config.read_db_name or self.config.db_name
        src_coll_name = self.config.read_coll or COLL_CHUNKS
        collection = self.get_collection(src_coll_name, io="read", db_name=src_db)

        # Query for chunks that have completed extraction but not resolution
        query = {
            "graphrag_extraction.status": "completed",
            "$or": [
                {"graphrag_resolution": {"$exists": False}},
                {"graphrag_resolution.status": {"$ne": "completed"}},
            ],
        }

        # Skip chunks marked for exclusion (used in random chunk testing)
        query["_test_exclude"] = {"$exists": False}

        if self.config.video_id:
            query["video_id"] = self.config.video_id

        logger.info(f"Querying chunks for entity resolution: {query}")

        cursor = collection.find(query).limit(self.config.max or float("inf"))

        for doc in cursor:
            yield doc

    def handle_doc(self, doc: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a single chunk for entity resolution and write to database.

        Args:
            doc: Chunk document to process

        Returns:
            None (writes directly to database via update_one)
        """
        chunk_id = doc.get("chunk_id", "unknown")
        video_id = doc.get("video_id", "unknown")

        logger.debug(
            f"Processing chunk {chunk_id} from video {video_id} for entity resolution"
        )

        try:
            # Extract entity data from the chunk
            extraction_data = doc.get("graphrag_extraction", {}).get("data", {})

            if not extraction_data or "entities" not in extraction_data:
                logger.warning(f"No entity extraction data found in chunk {chunk_id}")
                return self._mark_resolution_failed(doc, "no_extraction_data")

            # Resolve entities for this chunk
            resolved_entities = self.resolution_agent.resolve_entities(
                [extraction_data]
            )

            if not resolved_entities:
                logger.warning(f"No entities resolved for chunk {chunk_id}")
                return self._mark_resolution_failed(doc, "no_entities_resolved")

            # Store resolved entities in the entities collection
            stored_entities = self._store_resolved_entities(
                resolved_entities, chunk_id, video_id
            )

            # Store entity mentions
            self._store_entity_mentions(resolved_entities, chunk_id, video_id)

            # Prepare resolution payload
            resolution_payload = {
                "graphrag_resolution": {
                    "status": "completed",
                    "resolved_entities": len(resolved_entities),
                    "stored_entities": len(stored_entities),
                    "processed_at": time.time(),
                    "model_used": self.config.model_name,
                }
            }

            # Write to database
            dst_db = self.config.write_db_name or self.config.db_name
            dst_coll_name = self.config.write_coll or COLL_CHUNKS
            collection = self.get_collection(dst_coll_name, io="write", db_name=dst_db)

            # Check if already processed (unless upsert_existing is True)
            if not self.config.upsert_existing:
                existing = collection.find_one(
                    {"video_id": video_id, "chunk_id": chunk_id},
                    {"graphrag_resolution.status": 1},
                )
                if (
                    existing
                    and existing.get("graphrag_resolution", {}).get("status")
                    == "completed"
                ):
                    logger.debug(
                        f"Skipping chunk {chunk_id} - already has completed resolution"
                    )
                    self.stats["skipped"] += 1
                    return None

            # Update the chunk with resolution results
            collection.update_one(
                {"video_id": video_id, "chunk_id": chunk_id},
                {"$set": resolution_payload},
                upsert=False,
            )

            self.stats["updated"] += 1
            logger.debug(
                f"Successfully resolved {len(resolved_entities)} entities "
                f"for chunk {chunk_id}"
            )

            return None

        except Exception as e:
            logger.error(
                f"Error processing chunk {chunk_id} for entity resolution: {e}"
            )
            return self._mark_resolution_failed(doc, str(e))

    def _store_resolved_entities(
        self, resolved_entities: List[ResolvedEntity], chunk_id: str, video_id: str
    ) -> List[str]:
        """
        Store resolved entities in the entities collection.

        Args:
            resolved_entities: List of resolved entities
            chunk_id: Source chunk ID
            video_id: Source video ID

        Returns:
            List of stored entity IDs
        """
        entities_collection = self.graphrag_collections["entities"]
        stored_entity_ids = []

        for entity in resolved_entities:
            try:
                # Check if entity already exists
                existing_entity = entities_collection.find_one(
                    {"entity_id": entity.entity_id}
                )

                if existing_entity:
                    # Update existing entity
                    self._update_existing_entity(
                        existing_entity, entity, chunk_id, video_id
                    )
                else:
                    # Insert new entity
                    self._insert_new_entity(entity, chunk_id, video_id)

                stored_entity_ids.append(entity.entity_id)

            except Exception as e:
                logger.error(f"Failed to store entity {entity.entity_id}: {e}")
                continue

        return stored_entity_ids

    def _update_existing_entity(
        self,
        existing_entity: Dict[str, Any],
        resolved_entity: ResolvedEntity,
        chunk_id: str,
        video_id: str,
    ) -> None:
        """
        Update an existing entity with new information.

        Args:
            existing_entity: Existing entity document
            resolved_entity: New resolved entity
            chunk_id: Source chunk ID
            video_id: Source video ID
        """
        entities_collection = self.graphrag_collections["entities"]

        # Update source count and aliases
        update_data = {
            "$inc": {"source_count": 1},
            "$addToSet": {
                "aliases": {"$each": resolved_entity.aliases},
                "source_chunks": chunk_id,
            },
            "$set": {"updated_at": time.time(), "last_seen": time.time()},
        }

        # Update confidence if new entity has higher confidence
        if resolved_entity.confidence > existing_entity.get("confidence", 0):
            update_data["$set"]["confidence"] = resolved_entity.confidence

        # Update description if new entity has more comprehensive description
        if len(resolved_entity.description) > len(
            existing_entity.get("description", "")
        ):
            update_data["$set"]["description"] = resolved_entity.description

        entities_collection.update_one(
            {"entity_id": resolved_entity.entity_id}, update_data
        )

    def _insert_new_entity(
        self, resolved_entity: ResolvedEntity, chunk_id: str, video_id: str
    ) -> None:
        """
        Insert a new entity into the entities collection.

        Args:
            resolved_entity: Resolved entity to insert
            chunk_id: Source chunk ID
            video_id: Source video ID
        """
        entities_collection = self.graphrag_collections["entities"]

        entity_doc = {
            "entity_id": resolved_entity.entity_id,
            "canonical_name": resolved_entity.canonical_name,
            "name": resolved_entity.name,
            "type": resolved_entity.type.value,
            "description": resolved_entity.description,
            "confidence": resolved_entity.confidence,
            "source_count": resolved_entity.source_count,
            "resolution_methods": resolved_entity.resolution_methods,
            "aliases": resolved_entity.aliases,
            "source_chunks": [chunk_id],
            "video_id": video_id,
            "created_at": time.time(),
            "updated_at": time.time(),
            "first_seen": time.time(),
            "last_seen": time.time(),
            "trust_score": 0.0,  # Will be updated by trust stage
            "centrality_score": 0.0,  # Will be updated by graph construction
        }

        entities_collection.insert_one(entity_doc)

    def _store_entity_mentions(
        self, resolved_entities: List[ResolvedEntity], chunk_id: str, video_id: str
    ) -> None:
        """
        Store entity mentions in the entity_mentions collection.

        Args:
            resolved_entities: List of resolved entities
            chunk_id: Source chunk ID
            video_id: Source video ID
        """
        mentions_collection = self.graphrag_collections["entity_mentions"]

        mentions = []
        for entity in resolved_entities:
            mention_doc = {
                "entity_id": entity.entity_id,
                "chunk_id": chunk_id,
                "video_id": video_id,
                "confidence": entity.confidence,
                "position": 0,  # Could be enhanced to track position in chunk
                "created_at": time.time(),
            }
            mentions.append(mention_doc)

        if mentions:
            mentions_collection.insert_many(mentions)

    def _mark_resolution_failed(self, doc: Dict[str, Any], error_message: str) -> None:
        """
        Mark resolution as failed for a document.

        Args:
            doc: Document to mark as failed
            error_message: Error message describing the failure
        """
        chunk_id = doc.get("chunk_id", "unknown")
        video_id = doc.get("video_id", "unknown")

        resolution_payload = {
            "graphrag_resolution": {
                "status": "failed",
                "error": error_message,
                "processed_at": time.time(),
                "model_used": self.config.model_name,
            }
        }

        # Write failure status to database
        dst_db = self.config.write_db_name or self.config.db_name
        dst_coll_name = self.config.write_coll or COLL_CHUNKS
        collection = self.get_collection(dst_coll_name, io="write", db_name=dst_db)

        collection.update_one(
            {"video_id": video_id, "chunk_id": chunk_id},
            {"$set": resolution_payload},
            upsert=False,
        )

        self.stats["failed"] += 1
        logger.warning(f"Marked chunk {chunk_id} resolution as failed: {error_message}")

        return None

    def process_batch(
        self, docs: List[Dict[str, Any]]
    ) -> List[Optional[Dict[str, Any]]]:
        """
        Process a batch of documents for entity resolution.

        Args:
            docs: List of documents to process

        Returns:
            List of processed documents (or None for failed processing)
        """
        logger.info(f"Processing batch of {len(docs)} chunks for entity resolution")

        results = []
        for i, doc in enumerate(docs):
            logger.debug(f"Processing document {i + 1}/{len(docs)}")

            try:
                result = self.handle_doc(doc)
                results.append(result)

                # Add small delay to avoid rate limiting
                if i < len(docs) - 1:
                    time.sleep(0.1)

            except Exception as e:
                logger.error(f"Error processing document {i + 1}: {e}")
                results.append(None)

        successful_count = sum(1 for r in results if r is not None)
        logger.info(
            f"Batch processing completed: {successful_count}/{len(docs)} successful"
        )

        return results

    def get_resolution_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the resolution stage.

        Returns:
            Dictionary containing resolution statistics
        """
        src_db = self.config.read_db_name or self.config.db_name
        src_coll_name = self.config.read_coll or COLL_CHUNKS
        collection = self.get_collection(src_coll_name, io="read", db_name=src_db)
        entities_collection = self.graphrag_collections["entities"]

        # Count total chunks with extraction
        total_extracted = collection.count_documents(
            {"graphrag_extraction.status": "completed"}
        )

        # Count resolved chunks
        resolved_chunks = collection.count_documents(
            {"graphrag_resolution.status": "completed"}
        )

        # Count failed chunks
        failed_chunks = collection.count_documents(
            {"graphrag_resolution.status": "failed"}
        )

        # Count pending chunks
        pending_chunks = total_extracted - resolved_chunks - failed_chunks

        # Count total entities
        total_entities = entities_collection.count_documents({})

        # Count entity mentions
        mentions_collection = self.graphrag_collections["entity_mentions"]
        total_mentions = mentions_collection.count_documents({})

        return {
            "total_extracted_chunks": total_extracted,
            "resolved_chunks": resolved_chunks,
            "failed_chunks": failed_chunks,
            "pending_chunks": pending_chunks,
            "total_entities": total_entities,
            "total_mentions": total_mentions,
            "completion_rate": (
                resolved_chunks / total_extracted if total_extracted > 0 else 0
            ),
            "failure_rate": (
                failed_chunks / total_extracted if total_extracted > 0 else 0
            ),
        }

    def cleanup_failed_resolutions(self) -> int:
        """
        Clean up failed resolution records to allow retry.

        Returns:
            Number of failed resolutions cleaned up
        """
        src_db = self.config.read_db_name or self.config.db_name
        src_coll_name = self.config.read_coll or COLL_CHUNKS
        collection = self.get_collection(src_coll_name, io="read", db_name=src_db)

        result = collection.update_many(
            {"graphrag_resolution.status": "failed"},
            {"$unset": {"graphrag_resolution": 1}},
        )

        logger.info(f"Cleaned up {result.modified_count} failed resolutions")
        return result.modified_count
