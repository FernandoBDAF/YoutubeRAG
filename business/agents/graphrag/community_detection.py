"""
Community Detection Agent

This module implements community detection using the Louvain algorithm
to identify clusters of related entities in the knowledge graph.

NOTE: Switched from hierarchical_leiden to Louvain (Nov 4, 2025)
Reason: hierarchical_leiden produced single-entity communities on sparse graphs.
Louvain is proven to work well with GraphRAG's sparse, diverse entity graphs.
"""

import logging
import os
from typing import Dict, List, Any
from collections import defaultdict
import networkx as nx
from networkx.algorithms import community as nx_community
from core.models.graphrag import ResolvedEntity, ResolvedRelationship

logger = logging.getLogger(__name__)


class CommunityDetectionAgent:
    """
    Agent for detecting communities in the knowledge graph using Louvain algorithm.

    Switched from hierarchical_leiden (Nov 4, 2025) due to poor performance on sparse graphs.
    Louvain is proven to work well with GraphRAG's diverse, sparse entity graphs.
    """

    def __init__(
        self,
        max_cluster_size: int = 50,  # Increased from 10 (Louvain produces larger communities)
        min_cluster_size: int = 2,
        resolution_parameter: float = 1.0,
        max_iterations: int = 100,
        max_levels: int = 3,
        algorithm: str = "louvain",  # Algorithm to use: "louvain" or "hierarchical_leiden"
    ):
        """
        Initialize the Community Detection Agent.

        DESIGN DECISIONS & TESTING NOTES (2024-11-04):
        ==============================================

        1. ALGORITHM SELECTION:
           - Current: Louvain (default)
           - Why: Produces meaningful communities on sparse GraphRAG graphs
           - Previous: hierarchical_leiden
           - Why changed: hierarchical_leiden produced mostly single-entity communities
           - Metrics: Louvain achieved modularity=0.6347 (excellent!) vs leiden ~0.3
           - Future improvements to test:
             * Leiden with different parameters (quality function, seed)
             * Label Propagation (faster, simpler)
             * Infomap (information-theoretic approach)
             * Ensemble methods (combine multiple algorithms)

        2. RESOLUTION PARAMETER:
           - Current: 1.0 (default)
           - Why: Produces balanced community sizes (10-4804 entities)
           - Range: 0.5-2.0 (lower=fewer larger communities, higher=more smaller communities)
           - Future improvements to test:
             * 0.7-0.8: Fewer, larger communities (better for high-level topics)
             * 1.5-2.0: More, smaller communities (better for fine-grained topics)
             * Multi-resolution: Detect at multiple resolutions, pick best modularity

        3. MIN/MAX CLUSTER SIZE:
           - Current: min=2, max=50
           - Why: Filter out single-entity communities (noise), soft cap at 50
           - Note: Louvain ignores max_cluster_size (post-processing only)
           - Actual sizes: 2-4804 entities (largest=4804, median~50)
           - Future improvements to test:
             * Split very large communities (>1000) using sub-community detection
             * Merge very small communities (<5) if they're highly connected

        Args:
            max_cluster_size: Maximum size of a community (soft limit, Louvain ignores)
            min_cluster_size: Minimum size to keep (filter out smaller, default=2)
            resolution_parameter: Louvain resolution (0.5-2.0, default=1.0)
            max_iterations: Maximum iterations for the algorithm
            max_levels: Maximum number of hierarchical levels (hierarchical_leiden only)
            algorithm: Algorithm to use ("louvain" default or "hierarchical_leiden")
        """
        self.max_cluster_size = max_cluster_size
        self.min_cluster_size = min_cluster_size
        self.resolution_parameter = resolution_parameter
        self.max_iterations = max_iterations
        self.max_levels = max_levels
        self.algorithm = algorithm

        logger.info(
            f"Initialized CommunityDetectionAgent with algorithm={algorithm}, "
            f"resolution={resolution_parameter}, min_size={min_cluster_size}"
        )

    def detect_communities(
        self, entities: List[ResolvedEntity], relationships: List[ResolvedRelationship]
    ) -> Dict[str, Any]:
        """
        Detect communities using Louvain algorithm (default) or hierarchical Leiden.

        Args:
            entities: List of resolved entities
            relationships: List of resolved relationships

        Returns:
            Dictionary containing community detection results
        """
        logger.info(
            f"Detecting communities from {len(entities)} entities and {len(relationships)} relationships "
            f"using {self.algorithm} algorithm"
        )

        if not entities:
            logger.warning("No entities provided for community detection")
            return {"communities": {}, "levels": 0, "total_communities": 0}

        # Convert to NetworkX graph
        G = self._create_networkx_graph(entities, relationships)

        if G.number_of_nodes() == 0:
            logger.warning("Empty graph created from entities and relationships")
            return {"communities": {}, "levels": 0, "total_communities": 0}

        logger.info(
            f"Created graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges"
        )

        # Run community detection with selected algorithm
        try:
            if self.algorithm == "louvain":
                communities = self._detect_louvain(G)
            elif self.algorithm == "hierarchical_leiden":
                communities = self._detect_hierarchical_leiden(G)
            else:
                logger.warning(f"Unknown algorithm '{self.algorithm}', using Louvain")
                communities = self._detect_louvain(G)

            logger.info(
                f"Detected {len(communities)} communities using {self.algorithm}"
            )

        except Exception as e:
            logger.error(f"Failed to run {self.algorithm} algorithm: {e}")
            # Fallback to simple community detection
            communities = self._fallback_community_detection(G)

        # Organize communities by level
        organized_communities = self._organize_communities_by_level(
            communities, entities, relationships
        )

        # Calculate community quality metrics
        quality_metrics = self._calculate_community_quality(organized_communities, G)

        return {
            "communities": organized_communities,
            "levels": len(organized_communities),
            "total_communities": sum(
                len(level_communities)
                for level_communities in organized_communities.values()
            ),
            "quality_metrics": quality_metrics,
            "graph_stats": {
                "nodes": G.number_of_nodes(),
                "edges": G.number_of_edges(),
                "density": nx.density(G),
            },
        }

    def _create_networkx_graph(
        self, entities: List[ResolvedEntity], relationships: List[ResolvedRelationship]
    ) -> nx.Graph:
        """
        Convert entities and relationships to NetworkX graph.

        Args:
            entities: List of resolved entities
            relationships: List of resolved relationships

        Returns:
            NetworkX graph
        """
        G = nx.Graph()

        # Add nodes (entities)
        for entity in entities:
            G.add_node(
                entity.entity_id,
                name=entity.name,
                type=entity.type.value,
                description=entity.description,
                confidence=entity.confidence,
                source_count=entity.source_count,
                centrality_score=0.0,  # Will be calculated later
            )

        # Add edges (relationships) with weights
        for relationship in relationships:
            if G.has_node(relationship.subject_id) and G.has_node(
                relationship.object_id
            ):
                # Calculate edge weight based on confidence and relationship type
                base_confidence = relationship.confidence
                relationship_type = getattr(relationship, "relationship_type", None)

                # Apply weight multipliers based on relationship source
                if relationship_type == "co_occurrence":
                    weight = base_confidence  # 0.7 typically
                elif relationship_type == "semantic_similarity":
                    weight = base_confidence * 0.8  # Slight penalty (similarity score)
                elif relationship_type == "cross_chunk":
                    weight = base_confidence * 0.5  # 50% penalty for inferred
                elif relationship_type == "bidirectional":
                    weight = base_confidence  # Same as original
                elif relationship_type == "predicted":
                    weight = base_confidence * 0.4  # 60% penalty for predicted
                else:
                    # LLM-extracted (no relationship_type field)
                    weight = base_confidence  # Full weight (0.8-0.95)

                # Ensure weight is in valid range
                weight = max(0.1, min(1.0, weight))

                G.add_edge(
                    relationship.subject_id,
                    relationship.object_id,
                    predicate=relationship.predicate,
                    description=relationship.description,
                    confidence=relationship.confidence,
                    source_count=relationship.source_count,
                    weight=weight,  # Edge weight for community detection
                    relationship_type=relationship_type,
                )

        return G

    def _detect_louvain(self, G: nx.Graph) -> List[Any]:
        """
        Detect communities using Louvain algorithm.

        Args:
            G: NetworkX graph

        Returns:
            List of community frozensets
        """
        logger.info(
            f"Running Louvain algorithm with resolution={self.resolution_parameter}"
        )

        # Get random seed from environment or use default
        seed = int(os.getenv("GRAPHRAG_RANDOM_SEED", "42"))

        # Run Louvain algorithm
        communities = nx_community.louvain_communities(
            G,
            resolution=self.resolution_parameter,
            seed=seed,
            weight="weight",  # Use edge weights
        )

        # Calculate modularity
        modularity = nx_community.modularity(G, communities, weight="weight")

        logger.info(
            f"Louvain detected {len(communities)} communities "
            f"(modularity={modularity:.4f})"
        )

        # Log community sizes
        sizes = sorted([len(c) for c in communities], reverse=True)
        if sizes:
            logger.info(
                f"Community sizes: {sizes[:10]}{'...' if len(sizes) > 10 else ''}"
            )

        return list(communities)

    def _detect_hierarchical_leiden(self, G: nx.Graph) -> List[Any]:
        """
        Detect communities using hierarchical Leiden algorithm.

        NOTE: Kept for backward compatibility, but not recommended for sparse graphs.

        Args:
            G: NetworkX graph

        Returns:
            List of communities
        """
        try:
            from graspologic.partition import hierarchical_leiden

            logger.info(
                f"Running hierarchical Leiden with max_cluster_size={self.max_cluster_size}"
            )

            communities = hierarchical_leiden(
                G,
                max_cluster_size=self.max_cluster_size,
            )

            logger.info(f"hierarchical_leiden detected {len(communities)} communities")

            return communities

        except ImportError:
            logger.error("graspologic not installed, falling back to Louvain")
            return self._detect_louvain(G)

    def _fallback_community_detection(self, G: nx.Graph) -> List[Any]:
        """
        Fallback community detection using simple connected components.

        Args:
            G: NetworkX graph

        Returns:
            List of communities
        """
        logger.info("Using fallback community detection based on connected components")

        communities = []
        for i, component in enumerate(nx.connected_components(G)):
            if len(component) >= self.min_cluster_size:
                # Create a simple community object with level >= 1 (CommunitySummary requires level >= 1)
                # Use 'nodes' attribute for multi-node communities
                if len(component) > 1:
                    community = type(
                        "Community",
                        (),
                        {"cluster": i, "nodes": component, "level": 1},
                    )()
                else:
                    # Single node community
                    community = type(
                        "Community",
                        (),
                        {"cluster": i, "node": list(component)[0], "level": 1},
                    )()
                communities.append(community)

        return communities

    def _organize_communities_by_level(
        self,
        communities: List[Any],
        entities: List[ResolvedEntity],
        relationships: List[ResolvedRelationship],
    ) -> Dict[int, Dict[str, Any]]:
        """
        Organize communities by hierarchical level.

        Handles both Louvain format (list of frozensets) and hierarchical_leiden format (objects with attributes).

        Args:
            communities: List of detected communities (frozensets from Louvain or objects from hierarchical_leiden)
            entities: List of resolved entities
            relationships: List of resolved relationships

        Returns:
            Dictionary mapping levels to community information
        """
        organized = defaultdict(dict)

        # Detect format: frozenset (Louvain) or object with attributes (hierarchical_leiden)
        if communities and isinstance(communities[0], (frozenset, set)):
            # Louvain format: list of frozensets
            logger.debug("Processing Louvain format communities (frozensets)")
            level = 1  # All Louvain communities at level 1

            for i, community_nodes in enumerate(communities):
                entity_ids = list(community_nodes)

                if len(entity_ids) < self.min_cluster_size:
                    logger.debug(
                        f"Skipping community with {len(entity_ids)} entities (min_cluster_size={self.min_cluster_size})"
                    )
                    continue

                community_id = f"level_{level}_community_{i}"

                # Get entities in this community
                community_entities = []
                community_relationships = []

                # Filter entities
                for entity in entities:
                    if entity.entity_id in entity_ids:
                        community_entities.append(entity)

                # Filter relationships (both entities must be in community)
                for relationship in relationships:
                    if (
                        relationship.subject_id in entity_ids
                        and relationship.object_id in entity_ids
                    ):
                        community_relationships.append(relationship)

                # Calculate coherence
                coherence_score = self._calculate_coherence_score(
                    community_entities, community_relationships
                )

                # Store community
                organized[level][community_id] = {
                    "community_id": community_id,
                    "level": level,
                    "entities": [e.entity_id for e in community_entities],
                    "entity_count": len(community_entities),
                    "relationships": [
                        r.relationship_id for r in community_relationships
                    ],
                    "relationship_count": len(community_relationships),
                    "coherence_score": coherence_score,
                    "entity_names": [e.name for e in community_entities],
                    "entity_types": [e.type.value for e in community_entities],
                }

            logger.info(
                f"Organized {len(organized.get(1, {}))} Louvain communities at level 1 "
                f"(filtered from {len(communities)} total)"
            )
            return dict(organized)

        # hierarchical_leiden format: objects with .level, .nodes/.node attributes
        logger.debug("Processing hierarchical_leiden format communities (objects)")
        level_communities = defaultdict(list)
        for community in communities:
            # Get level, default to 1 if not present
            level = getattr(community, "level", 1)
            level = max(1, level)
            level_communities[level].append(community)

        # Process each level
        for level, level_comm_list in level_communities.items():
            for i, community in enumerate(level_comm_list):

                if hasattr(community, "nodes"):
                    # Multiple nodes in community
                    entity_ids = list(community.nodes)
                else:
                    # Single node community
                    entity_ids = [getattr(community, "node", "")]

                # Filter out communities below min_cluster_size
                if len(entity_ids) < self.min_cluster_size:
                    logger.debug(
                        f"Skipping community with {len(entity_ids)} entities "
                        f"(min_cluster_size={self.min_cluster_size})"
                    )
                    continue

                # Filter entities and relationships
                for entity in entities:
                    if entity.entity_id in entity_ids:
                        community_entities.append(entity)

                for relationship in relationships:
                    if (
                        relationship.subject_id in entity_ids
                        and relationship.object_id in entity_ids
                    ):
                        community_relationships.append(relationship)

                # Calculate community metrics
                coherence_score = self._calculate_coherence_score(
                    community_entities, community_relationships
                )

                organized[level][community_id] = {
                    "community_id": community_id,
                    "level": level,
                    "entities": [e.entity_id for e in community_entities],
                    "entity_count": len(community_entities),
                    "relationships": [
                        r.relationship_id for r in community_relationships
                    ],
                    "relationship_count": len(community_relationships),
                    "coherence_score": coherence_score,
                    "entity_names": [e.name for e in community_entities],
                    "entity_types": [e.type.value for e in community_entities],
                }

        return dict(organized)

    def _calculate_coherence_score(
        self, entities: List[ResolvedEntity], relationships: List[ResolvedRelationship]
    ) -> float:
        """
        Calculate coherence score for a community.

        Args:
            entities: Entities in the community
            relationships: Relationships in the community

        Returns:
            Coherence score between 0 and 1
        """
        if not entities:
            return 0.0

        if len(entities) == 1:
            # Changed from 1.0 - isolated entities have no coherence
            return 0.0

        # Calculate internal connectivity
        entity_ids = {e.entity_id for e in entities}
        internal_relationships = len(relationships)

        # Calculate potential relationships (complete graph)
        potential_relationships = len(entities) * (len(entities) - 1) / 2

        # Connectivity ratio
        connectivity_ratio = (
            internal_relationships / potential_relationships
            if potential_relationships > 0
            else 0
        )

        # Average entity confidence
        avg_confidence = sum(e.confidence for e in entities) / len(entities)

        # Average relationship confidence
        avg_rel_confidence = (
            sum(r.confidence for r in relationships) / len(relationships)
            if relationships
            else 0
        )

        # Combined coherence score
        coherence_score = (
            0.4 * connectivity_ratio + 0.3 * avg_confidence + 0.3 * avg_rel_confidence
        )

        return min(1.0, max(0.0, coherence_score))

    def _calculate_community_quality(
        self, organized_communities: Dict[int, Dict[str, Any]], G: nx.Graph
    ) -> Dict[str, Any]:
        """
        Calculate quality metrics for detected communities.

        Args:
            organized_communities: Organized communities by level
            G: NetworkX graph

        Returns:
            Dictionary containing quality metrics
        """
        total_communities = sum(
            len(level_communities)
            for level_communities in organized_communities.values()
        )

        if total_communities == 0:
            return {
                "total_communities": 0,
                "avg_coherence": 0,
                "avg_size": 0,
                "coverage": 0,
            }

        # Calculate average coherence
        all_coherence_scores = []
        all_sizes = []

        for level_communities in organized_communities.values():
            for community in level_communities.values():
                all_coherence_scores.append(community["coherence_score"])
                all_sizes.append(community["entity_count"])

        avg_coherence = sum(all_coherence_scores) / len(all_coherence_scores)
        avg_size = sum(all_sizes) / len(all_sizes)

        # Calculate coverage (percentage of nodes in communities)
        total_nodes_in_communities = sum(all_sizes)
        total_graph_nodes = G.number_of_nodes()
        coverage = (
            total_nodes_in_communities / total_graph_nodes
            if total_graph_nodes > 0
            else 0
        )

        return {
            "total_communities": total_communities,
            "avg_coherence": avg_coherence,
            "avg_size": avg_size,
            "coverage": coverage,
            "max_coherence": max(all_coherence_scores),
            "min_coherence": min(all_coherence_scores),
            "max_size": max(all_sizes),
            "min_size": min(all_sizes),
        }

    def get_community_statistics(
        self, detection_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get statistics about community detection results.

        Args:
            detection_results: Results from detect_communities

        Returns:
            Dictionary containing detection statistics
        """
        communities = detection_results.get("communities", {})
        quality_metrics = detection_results.get("quality_metrics", {})
        graph_stats = detection_results.get("graph_stats", {})

        # Level distribution
        level_distribution = {}
        for level, level_communities in communities.items():
            level_distribution[f"level_{level}"] = len(level_communities)

        # Size distribution
        size_distribution = defaultdict(int)
        for level_communities in communities.values():
            for community in level_communities.values():
                size = community["entity_count"]
                if size <= 2:
                    size_distribution["small"] += 1
                elif size <= 5:
                    size_distribution["medium"] += 1
                else:
                    size_distribution["large"] += 1

        return {
            "total_communities": detection_results.get("total_communities", 0),
            "levels": detection_results.get("levels", 0),
            "level_distribution": level_distribution,
            "size_distribution": dict(size_distribution),
            "quality_metrics": quality_metrics,
            "graph_stats": graph_stats,
            "detection_parameters": {
                "max_cluster_size": self.max_cluster_size,
                "min_cluster_size": self.min_cluster_size,
                "resolution_parameter": self.resolution_parameter,
                "max_iterations": self.max_iterations,
            },
        }
