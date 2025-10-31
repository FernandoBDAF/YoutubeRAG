"""
Community Detection Stage

This stage detects communities in the knowledge graph and generates summaries
for each community using hierarchical Leiden algorithm and LLM-based summarization.
"""

import logging
import time
from typing import Dict, List, Any, Optional, Iterator
from pymongo.collection import Collection
from pymongo.database import Database
from core.base.stage import BaseStage
from core.config.graphrag import CommunityDetectionConfig
from business.agents.graphrag.community_detection import CommunityDetectionAgent
from business.agents.graphrag.community_summarization import CommunitySummarizationAgent
from core.models.graphrag import ResolvedEntity, ResolvedRelationship, CommunitySummary
from business.services.graphrag.indexes import get_graphrag_collections
from core.config.paths import COLL_CHUNKS

logger = logging.getLogger(__name__)


class CommunityDetectionStage(BaseStage):
    """
    Stage for detecting communities in the knowledge graph and generating summaries.
    """

    name = "community_detection"
    description = "Detect communities and generate summaries"
    ConfigCls = CommunityDetectionConfig

    def __init__(self):
        """Initialize the Community Detection Stage."""
        super().__init__()
        # Don't initialize agents here - will be done in setup()

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

        # Initialize the community detection agent now that we have access to self.config
        self.detection_agent = CommunityDetectionAgent(
            max_cluster_size=self.config.max_cluster_size,
            min_cluster_size=self.config.min_cluster_size,
            resolution_parameter=self.config.resolution_parameter,
            max_iterations=self.config.max_iterations,
            max_levels=self.config.max_levels,
        )

        # Initialize the community summarization agent
        self.summarization_agent = CommunitySummarizationAgent(
            llm_client=self.llm_client,
            model_name=self.config.model_name,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            max_summary_length=self.config.max_summary_length,
            min_summary_length=self.config.min_summary_length,
            max_retries=self.config.llm_retries,
            retry_delay=self.config.llm_backoff_s,
        )

        # Get GraphRAG collections
        self.graphrag_collections = get_graphrag_collections(self.db)

        # Flag to ensure community detection runs only once across all chunks
        self._communities_detected = False

        logger.info(
            f"Initialized {self.name} with max_cluster_size={self.config.max_cluster_size}"
        )

    def iter_docs(self) -> Iterator[Dict[str, Any]]:
        """
        Iterate over chunks that have completed graph construction.

        Yields:
            Chunk documents that have been processed for graph construction
        """
        src_db = self.config.read_db_name or self.config.db_name
        src_coll_name = self.config.read_coll or COLL_CHUNKS
        collection = self.get_collection(src_coll_name, io="read", db_name=src_db)

        # Query for chunks that have completed construction but not community detection
        query = {
            "graphrag_construction.status": "completed",
            "$or": [
                {"graphrag_communities": {"$exists": False}},
                {"graphrag_communities.status": {"$ne": "completed"}},
            ],
        }

        # Skip chunks marked for exclusion (used in random chunk testing)
        query["_test_exclude"] = {"$exists": False}

        if self.config.video_id:
            query["video_id"] = self.config.video_id

        logger.info(f"Querying chunks for community detection: {query}")

        cursor = collection.find(query).limit(self.config.max or float("inf"))

        for doc in cursor:
            yield doc

    def handle_doc(self, doc: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a single chunk for community detection and write to database.

        Args:
            doc: Chunk document to process

        Returns:
            None (writes directly to database via update_one)
        """
        chunk_id = doc.get("chunk_id", "unknown")
        video_id = doc.get("video_id", "unknown")

        logger.debug(
            f"Processing chunk {chunk_id} from video {video_id} for community detection"
        )

        try:
            # Community detection should run ONCE for the entire graph, not per-chunk
            # Check if communities have already been detected (in this run or previous)
            communities_collection = self.graphrag_collections["communities"]
            existing_communities = list(communities_collection.find({}).limit(1))

            # Also check in-memory flag to avoid race conditions in concurrent processing
            if self._communities_detected or existing_communities:
                # Communities already exist - just mark this chunk as processed
                logger.info(
                    f"Communities already detected in database ({len(existing_communities)} found). "
                    f"Marking chunk {chunk_id} as processed without re-running detection."
                )

                detection_payload = {
                    "graphrag_communities": {
                        "status": "completed",
                        "note": "communities_already_exist",
                        "processed_at": time.time(),
                    }
                }

                dst_db = self.config.write_db_name or self.config.db_name
                dst_coll_name = self.config.write_coll or COLL_CHUNKS
                collection = self.get_collection(
                    dst_coll_name, io="write", db_name=dst_db
                )

                collection.update_one(
                    {"video_id": video_id, "chunk_id": chunk_id},
                    {"$set": detection_payload},
                    upsert=False,
                )

                self.stats["updated"] += 1
                return None

            # First time - detect communities for the entire graph
            logger.info(
                f"First chunk detected - running community detection on entire graph "
                f"for chunk {chunk_id}"
            )

            # Get all entities and relationships from the database
            entities = self._get_all_entities()
            relationships = self._get_all_relationships()

            if not entities:
                logger.warning("No entities found for community detection")
                return self._mark_detection_failed(doc, "no_entities")

            # Detect communities
            detection_results = self.detection_agent.detect_communities(
                entities, relationships
            )

            if not detection_results.get("communities"):
                logger.warning("No communities detected")
                return self._mark_detection_failed(doc, "no_communities_detected")

            # Generate community summaries
            community_summaries = self.summarization_agent.summarize_communities(
                detection_results["communities"], entities, relationships
            )

            if not community_summaries:
                logger.warning("No community summaries generated")
                return self._mark_detection_failed(doc, "no_summaries_generated")

            # Store communities in the communities collection
            stored_communities = self._store_communities(
                community_summaries, chunk_id, video_id
            )

            # Mark that communities have been detected (prevents re-detection for other chunks)
            self._communities_detected = True

            # Update entities with community assignments
            self._update_entity_communities(community_summaries)

            # Prepare detection payload
            detection_payload = {
                "graphrag_communities": {
                    "status": "completed",
                    "detected_communities": len(detection_results["communities"]),
                    "total_communities": detection_results["total_communities"],
                    "levels": detection_results["levels"],
                    "stored_communities": len(stored_communities),
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
                    {"graphrag_communities.status": 1},
                )
                if (
                    existing
                    and existing.get("graphrag_communities", {}).get("status")
                    == "completed"
                ):
                    logger.debug(
                        f"Skipping chunk {chunk_id} - already has completed detection"
                    )
                    self.stats["skipped"] += 1
                    return None

            # Update the chunk with detection results
            collection.update_one(
                {"video_id": video_id, "chunk_id": chunk_id},
                {"$set": detection_payload},
                upsert=False,
            )

            self.stats["updated"] += 1
            logger.debug(
                f"Successfully detected {len(stored_communities)} communities "
                f"for chunk {chunk_id}"
            )

            return None

        except Exception as e:
            logger.error(
                f"Error processing chunk {chunk_id} for community detection: {e}"
            )
            return self._mark_detection_failed(doc, str(e))

    def _get_all_entities(self) -> List[ResolvedEntity]:
        """
        Get all entities from the entities collection.

        Returns:
            List of ResolvedEntity objects
        """
        entities_collection = self.graphrag_collections["entities"]

        entity_docs = entities_collection.find({})
        entities = []

        for doc in entity_docs:
            try:
                entity = ResolvedEntity(
                    entity_id=doc["entity_id"],
                    canonical_name=doc["canonical_name"],
                    name=doc["name"],
                    type=doc["type"],
                    description=doc["description"],
                    confidence=doc.get("confidence", 0.0),
                    source_count=doc.get("source_count", 1),
                    resolution_methods=doc.get("resolution_methods", []),
                    aliases=doc.get("aliases", []),
                )
                entities.append(entity)
            except Exception as e:
                logger.warning(f"Failed to parse entity document: {e}")
                continue

        logger.debug(f"Retrieved {len(entities)} entities")
        return entities

    def _get_all_relationships(self) -> List[ResolvedRelationship]:
        """
        Get all relationships from the relations collection.

        Returns:
            List of ResolvedRelationship objects
        """
        relations_collection = self.graphrag_collections["relations"]

        relationship_docs = relations_collection.find({})
        relationships = []

        for doc in relationship_docs:
            try:
                relationship = ResolvedRelationship(
                    relationship_id=doc["relationship_id"],
                    subject_id=doc["subject_id"],
                    object_id=doc["object_id"],
                    predicate=doc["predicate"],
                    description=doc["description"],
                    confidence=doc.get("confidence", 0.0),
                    source_count=doc.get("source_count", 1),
                )
                relationships.append(relationship)
            except Exception as e:
                logger.warning(f"Failed to parse relationship document: {e}")
                continue

        logger.debug(f"Retrieved {len(relationships)} relationships")
        return relationships

    def _store_communities(
        self,
        community_summaries: Dict[str, CommunitySummary],
        chunk_id: str,
        video_id: str,
    ) -> List[str]:
        """
        Store community summaries in the communities collection.

        Args:
            community_summaries: Dictionary of community summaries
            chunk_id: Source chunk ID
            video_id: Source video ID

        Returns:
            List of stored community IDs
        """
        communities_collection = self.graphrag_collections["communities"]
        stored_community_ids = []

        for community_id, summary in community_summaries.items():
            try:
                # Check if community already exists
                existing_community = communities_collection.find_one(
                    {"community_id": community_id}
                )

                if existing_community:
                    # Update existing community
                    self._update_existing_community(
                        existing_community, summary, chunk_id, video_id
                    )
                else:
                    # Insert new community
                    self._insert_new_community(summary, chunk_id, video_id)

                stored_community_ids.append(community_id)

            except Exception as e:
                logger.error(f"Failed to store community {community_id}: {e}")
                continue

        return stored_community_ids

    def _update_existing_community(
        self,
        existing_community: Dict[str, Any],
        summary: CommunitySummary,
        chunk_id: str,
        video_id: str,
    ) -> None:
        """
        Update an existing community with new information.

        Args:
            existing_community: Existing community document
            summary: New community summary
            chunk_id: Source chunk ID
            video_id: Source video ID
        """
        communities_collection = self.graphrag_collections["communities"]

        # Update summary if new one is more comprehensive
        update_data = {
            "$addToSet": {"source_chunks": chunk_id},
            "$set": {"updated_at": time.time()},
        }

        if len(summary.summary) > len(existing_community.get("summary", "")):
            update_data["$set"]["summary"] = summary.summary
            update_data["$set"]["title"] = summary.title

        communities_collection.update_one(
            {"community_id": summary.community_id}, update_data
        )

    def _insert_new_community(
        self, summary: CommunitySummary, chunk_id: str, video_id: str
    ) -> None:
        """
        Insert a new community into the communities collection.

        Args:
            summary: Community summary to insert
            chunk_id: Source chunk ID
            video_id: Source video ID
        """
        communities_collection = self.graphrag_collections["communities"]

        community_doc = {
            "community_id": summary.community_id,
            "level": summary.level,
            "title": summary.title,
            "summary": summary.summary,
            "entities": summary.entities,
            "entity_count": summary.entity_count,
            "relationship_count": summary.relationship_count,
            "coherence_score": summary.coherence_score,
            "source_chunks": [chunk_id],
            "video_id": video_id,
            "created_at": time.time(),
            "updated_at": time.time(),
        }

        communities_collection.insert_one(community_doc)

    def _update_entity_communities(
        self, community_summaries: Dict[str, CommunitySummary]
    ) -> None:
        """
        Update entities with their community assignments.

        Args:
            community_summaries: Dictionary of community summaries
        """
        entities_collection = self.graphrag_collections["entities"]

        for community_id, summary in community_summaries.items():
            # Update entities with community assignment
            entities_collection.update_many(
                {"entity_id": {"$in": summary.entities}},
                {
                    "$addToSet": {
                        f"community_assignments.level_{summary.level}": community_id
                    },
                    "$set": {"community_updated_at": time.time()},
                },
            )

    def _mark_detection_failed(self, doc: Dict[str, Any], error_message: str) -> None:
        """
        Mark detection as failed for a document.

        Args:
            doc: Document to mark as failed
            error_message: Error message describing the failure
        """
        chunk_id = doc.get("chunk_id", "unknown")
        video_id = doc.get("video_id", "unknown")

        detection_payload = {
            "graphrag_communities": {
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
            {"$set": detection_payload},
            upsert=False,
        )

        self.stats["failed"] += 1
        logger.warning(f"Marked chunk {chunk_id} detection as failed: {error_message}")

        return None

    def process_batch(
        self, docs: List[Dict[str, Any]]
    ) -> List[Optional[Dict[str, Any]]]:
        """
        Process a batch of documents for community detection.

        Args:
            docs: List of documents to process

        Returns:
            List of processed documents (or None for failed processing)
        """
        logger.info(f"Processing batch of {len(docs)} chunks for community detection")

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

    def get_detection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the detection stage.

        Returns:
            Dictionary containing detection statistics
        """
        src_db = self.config.read_db_name or self.config.db_name
        src_coll_name = self.config.read_coll or COLL_CHUNKS
        collection = self.get_collection(src_coll_name, io="read", db_name=src_db)
        communities_collection = self.graphrag_collections["communities"]

        # Count total chunks with construction
        total_constructed = collection.count_documents(
            {"graphrag_construction.status": "completed"}
        )

        # Count detected chunks
        detected_chunks = collection.count_documents(
            {"graphrag_communities.status": "completed"}
        )

        # Count failed chunks
        failed_chunks = collection.count_documents(
            {"graphrag_communities.status": "failed"}
        )

        # Count pending chunks
        pending_chunks = total_constructed - detected_chunks - failed_chunks

        # Count total communities
        total_communities = communities_collection.count_documents({})

        # Count communities by level
        level_pipeline = [{"$group": {"_id": "$level", "count": {"$sum": 1}}}]
        level_results = list(communities_collection.aggregate(level_pipeline))
        level_distribution = {
            str(result["_id"]): result["count"] for result in level_results
        }

        return {
            "total_constructed_chunks": total_constructed,
            "detected_chunks": detected_chunks,
            "failed_chunks": failed_chunks,
            "pending_chunks": pending_chunks,
            "total_communities": total_communities,
            "level_distribution": level_distribution,
            "completion_rate": (
                detected_chunks / total_constructed if total_constructed > 0 else 0
            ),
            "failure_rate": (
                failed_chunks / total_constructed if total_constructed > 0 else 0
            ),
        }

    def cleanup_failed_detections(self) -> int:
        """
        Clean up failed detection records to allow retry.

        Returns:
            Number of failed detections cleaned up
        """
        src_db = self.config.read_db_name or self.config.db_name
        src_coll_name = self.config.read_coll or COLL_CHUNKS
        collection = self.get_collection(src_coll_name, io="read", db_name=src_db)

        result = collection.update_many(
            {"graphrag_communities.status": "failed"},
            {"$unset": {"graphrag_communities": 1}},
        )

        logger.info(f"Cleaned up {result.modified_count} failed detections")
        return result.modified_count
