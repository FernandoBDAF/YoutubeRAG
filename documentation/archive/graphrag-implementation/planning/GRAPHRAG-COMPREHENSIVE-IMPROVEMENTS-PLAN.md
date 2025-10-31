# GraphRAG Comprehensive Graph Structure Improvements Plan

## Date: October 31, 2025

## Overview

This plan consolidates all remaining graph structure improvements from the analysis into a single unified implementation. It covers 6 major enhancements across 3 phases to achieve target metrics: 300+ relationships, <10% isolated nodes, and 10-15 meaningful communities.

## Current State vs. Target Metrics

| Metric                   | Current | Target     | Improvement    |
| ------------------------ | ------- | ---------- | -------------- |
| Relationships            | 100     | 300+       | 3x increase    |
| Graph Density            | 0.0107  | 0.030      | 2.8x increase  |
| Isolated Nodes           | 36(26%) | <14 (<10%) | 2.5x reduction |
| Leaf Nodes               | 68(50%) | <41 (<30%) | 1.7x reduction |
| Connected Components     | 46      | <20        | 2.3x reduction |
| Average Degree           | 1.46    | 2.5+       | 1.7x increase  |
| Communities (multi-node) | 0       | 10-15      | New            |

## Implementation Phases

### Phase 1: Semantic Similarity Relationships (Post-Processing)

**Status**: Remaining from Phase 1 Quick Wins

**Objective**: Add ~30-50 relationships by connecting semantically similar entities

**Files to Modify**:

1. `app/stages/graph_construction.py` - Add semantic similarity post-processing

**Implementation Details**:

#### 1.1 Add Semantic Similarity Method

Add method `_add_semantic_similarity_relationships()` to `GraphConstructionStage`:

```python
def _add_semantic_similarity_relationships(self, similarity_threshold: float = 0.85) -> int:
    """
    Add semantic similarity relationships between entities based on embeddings.

    Args:
        similarity_threshold: Minimum cosine similarity to create relationship

    Returns:
        Number of similarity relationships added
    """
    logger.info("Starting semantic similarity relationship post-processing")

    entities_collection = self.graphrag_collections["entities"]
    relations_collection = self.graphrag_collections["relations"]

    # Step 1: Get all entities without embeddings and generate them
    entities_to_embed = list(entities_collection.find({"entity_embedding": {"$exists": False}}))

    if entities_to_embed:
        logger.info(f"Generating embeddings for {len(entities_to_embed)} entities")

        for entity in entities_to_embed:
            # Create embedding text from name + description
            embedding_text = f"{entity['name']}: {entity.get('description', '')}"

            try:
                from app.stages.embed import embed_texts
                embedding = embed_texts([embedding_text])[0]

                entities_collection.update_one(
                    {"entity_id": entity["entity_id"]},
                    {"$set": {
                        "entity_embedding": embedding,
                        "entity_embedding_text": embedding_text,
                        "entity_embedding_dim": len(embedding)
                    }}
                )
            except Exception as e:
                logger.error(f"Failed to embed entity {entity['entity_id']}: {e}")

    # Step 2: Get all entities with embeddings
    entities_with_embeddings = list(
        entities_collection.find({"entity_embedding": {"$exists": True}})
    )

    logger.info(f"Calculating similarity for {len(entities_with_embeddings)} entities")

    # Step 3: Calculate pairwise cosine similarity
    added_count = 0
    skipped_count = 0

    import numpy as np
    from itertools import combinations

    for entity1, entity2 in combinations(entities_with_embeddings, 2):
        entity1_id = entity1["entity_id"]
        entity2_id = entity2["entity_id"]

        # Check if relationship already exists
        existing = relations_collection.find_one({
            "$or": [
                {"subject_id": entity1_id, "object_id": entity2_id},
                {"subject_id": entity2_id, "object_id": entity1_id}
            ]
        })

        if existing:
            skipped_count += 1
            continue

        # Calculate cosine similarity
        emb1 = np.array(entity1["entity_embedding"])
        emb2 = np.array(entity2["entity_embedding"])

        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))

        if similarity >= similarity_threshold:
            # Create similarity relationship
            relationship_id = ResolvedRelationship.generate_relationship_id(
                entity1_id, entity2_id, "semantically_similar_to"
            )

            relationship_doc = {
                "relationship_id": relationship_id,
                "subject_id": entity1_id,
                "object_id": entity2_id,
                "predicate": "semantically_similar_to",
                "description": f"Entities are semantically similar (cosine similarity: {similarity:.3f})",
                "confidence": float(similarity),
                "source_count": 1,
                "source_chunks": [],
                "created_at": time.time(),
                "updated_at": time.time(),
                "relationship_type": "semantic_similarity",
                "similarity_score": float(similarity),
            }

            try:
                relations_collection.insert_one(relationship_doc)
                added_count += 1

                if added_count % 10 == 0:
                    logger.debug(f"Added {added_count} semantic similarity relationships")

            except Exception as e:
                logger.error(
                    f"Failed to insert similarity relationship "
                    f"{entity1_id} <-> {entity2_id}: {e}"
                )

    logger.info(
        f"Semantic similarity post-processing complete: "
        f"added {added_count} relationships, skipped {skipped_count} existing"
    )

    return added_count
```

#### 1.2 Integrate into Finalize Method

Update `finalize()` method to call semantic similarity:

```python
def finalize(self) -> None:
    """Finalize the graph construction stage with all post-processing."""

    # 1. Co-occurrence relationships (already implemented)
    logger.info("Running post-processing: adding co-occurrence relationships")
    try:
        co_occurrence_count = self._add_co_occurrence_relationships()
        logger.info(f"Added {co_occurrence_count} co-occurrence relationships")
    except Exception as e:
        logger.error(f"Failed to add co-occurrence relationships: {e}")

    # 2. Semantic similarity relationships (new)
    logger.info("Running post-processing: adding semantic similarity relationships")
    try:
        similarity_threshold = float(os.getenv("GRAPHRAG_SIMILARITY_THRESHOLD", "0.85"))
        similarity_count = self._add_semantic_similarity_relationships(similarity_threshold)
        logger.info(f"Added {similarity_count} semantic similarity relationships")
    except Exception as e:
        logger.error(f"Failed to add semantic similarity relationships: {e}")

    # Call parent finalize to log statistics
    super().finalize()
```

**Expected Impact**: Add 30-50 relationships, connect 15-20 isolated entities

---

### Phase 2: Enhanced Extraction Improvements

**Status**: Phase 2 Extraction Improvements

**Objective**: Improve LLM extraction to get more relationships, including multiple types, cross-chunk, bidirectional, and hierarchical

#### 2.1 Multiple Relationship Types Extraction

**Files to Modify**: `agents/graph_extraction_agent.py`

**Change**: Enhance system prompt to extract multiple relationship types per entity pair

**Current Prompt Section**:

```text
2. **Relationship Extraction**: Identify relationships between entities. Focus on:
- Direct relationships mentioned in the text
- Clear connections between entities
- Avoid inferring relationships not explicitly stated
```

**Enhanced Prompt Section**:

```text
2. **Relationship Extraction**: Extract ALL relationship types between each entity pair:
- **Multiple Types**: If Entity A relates to Entity B, extract ALL applicable relationships
  * Example: "Algorithm uses Data Structure" → extract: 'uses', 'applies_to', 'depends_on'
  * Example: "Person teaches Concept" → extract: 'teaches', 'explains', 'demonstrates'
- **Direct and Indirect**: Include both explicit and strongly implied relationships
- **Hierarchical**: Extract parent-child, part-of, is-a relationships
  * "Sorting Algorithm" is a type of "Algorithm" → 'is_a', 'subtype_of'
  * "Step" is part of "Algorithm" → 'part_of', 'component_of'
- **Bidirectional**: Consider reverse relationships
  * "Algorithm uses Data Structure" ↔ "Data Structure used_by Algorithm"
  * "Person teaches Concept" ↔ "Concept taught_by Person"
- **Semantic Relationships**: Include conceptual connections
  * "Algorithm requires Data Structure" → 'requires', 'needs'
  * "Concept related_to Concept" → 'related_to', 'similar_to'

**Goal**: Extract 2-5 relationship types per connected entity pair for rich graph connectivity
```

**Implementation**:

```python
# In GraphExtractionAgent.__init__()
self.system_prompt = """
You are an expert at extracting entities and relationships from YouTube content transcripts.

Your task is to identify all entities and their relationships from the given text chunk.

## Instructions:

1. **Entity Extraction**: [existing instructions...]

2. **Relationship Extraction**: Extract ALL relationship types between each entity pair:
- **Multiple Types**: If Entity A relates to Entity B, extract ALL applicable relationships
  * Example: "Algorithm uses Data Structure" → extract: 'uses', 'applies_to', 'depends_on'
  * Example: "Person teaches Concept" → extract: 'teaches', 'explains', 'demonstrates'
- **Direct and Indirect**: Include both explicit and strongly implied relationships
- **Hierarchical**: Extract parent-child, part-of, is-a relationships
  * "Sorting Algorithm" is a type of "Algorithm" → 'is_a', 'subtype_of'
  * "Step" is part of "Algorithm" → 'part_of', 'component_of'
- **Bidirectional**: Consider reverse relationships
  * "Algorithm uses Data Structure" ↔ "Data Structure used_by Algorithm"
  * "Person teaches Concept" ↔ "Concept taught_by Person"
- **Semantic Relationships**: Include conceptual connections
  * "Algorithm requires Data Structure" → 'requires', 'needs'
  * "Concept related_to Concept" → 'related_to', 'similar_to'

**Goal**: Extract 2-5 relationship types per connected entity pair for rich graph connectivity

3. **Quality Guidelines**: [existing guidelines...]

4. **YouTube Content Considerations**: [existing considerations...]

## Output Format:
Return a structured response with entities and relationships as specified in the KnowledgeModel schema.
"""
```

**Expected Impact**: Double relationship count (100 → 200), improve average degree (1.46 → 2.5)

#### 2.2 Cross-Chunk Relationship Extraction

**Files to Modify**: `app/stages/graph_construction.py`

**Implementation**: Add method `_add_cross_chunk_relationships()` for post-processing

```python
def _add_cross_chunk_relationships(self) -> int:
    """
    Add relationships between entities mentioned in different chunks but related globally.

    Uses entity mentions and co-occurrence patterns across multiple chunks to infer
    cross-chunk relationships.

    Returns:
        Number of cross-chunk relationships added
    """
    logger.info("Starting cross-chunk relationship post-processing")

    mentions_collection = self.graphrag_collections["entity_mentions"]
    relations_collection = self.graphrag_collections["relations"]
    entities_collection = self.graphrag_collections["entities"]

    # Strategy 1: Entities mentioned in same video but different chunks
    # Group entity mentions by video_id
    from collections import defaultdict
    video_entities = defaultdict(set)

    for mention in mentions_collection.find():
        video_id = mention.get("video_id")
        entity_id = mention.get("entity_id")
        if video_id and entity_id:
            video_entities[video_id].add(entity_id)

    logger.info(f"Found {len(video_entities)} videos with entity mentions")

    added_count = 0
    skipped_count = 0

    for video_id, entity_ids in video_entities.items():
        if len(entity_ids) < 2:
            continue

        # For entities in same video, check if they have similar types
        # and create weak cross-chunk relationships
        entity_list = list(entity_ids)

        for i, entity1_id in enumerate(entity_list):
            for entity2_id in entity_list[i+1:]:
                # Check if relationship already exists
                existing = relations_collection.find_one({
                    "$or": [
                        {"subject_id": entity1_id, "object_id": entity2_id},
                        {"subject_id": entity2_id, "object_id": entity1_id}
                    ]
                })

                if existing:
                    skipped_count += 1
                    continue

                # Get entity types to determine relationship type
                entity1 = entities_collection.find_one({"entity_id": entity1_id})
                entity2 = entities_collection.find_one({"entity_id": entity2_id})

                if not entity1 or not entity2:
                    continue

                # Create cross-chunk relationship based on entity types
                predicate = self._determine_cross_chunk_predicate(entity1, entity2)

                if predicate:
                    relationship_id = ResolvedRelationship.generate_relationship_id(
                        entity1_id, entity2_id, predicate
                    )

                    relationship_doc = {
                        "relationship_id": relationship_id,
                        "subject_id": entity1_id,
                        "object_id": entity2_id,
                        "predicate": predicate,
                        "description": f"Entities mentioned in same video (cross-chunk relationship)",
                        "confidence": 0.6,  # Lower confidence for inferred relationships
                        "source_count": 1,
                        "source_chunks": [],
                        "video_id": video_id,
                        "created_at": time.time(),
                        "updated_at": time.time(),
                        "relationship_type": "cross_chunk",
                    }

                    try:
                        relations_collection.insert_one(relationship_doc)
                        added_count += 1

                        if added_count % 50 == 0:
                            logger.debug(f"Added {added_count} cross-chunk relationships")

                    except Exception as e:
                        logger.error(
                            f"Failed to insert cross-chunk relationship "
                            f"{entity1_id} <-> {entity2_id}: {e}"
                        )

    logger.info(
        f"Cross-chunk post-processing complete: "
        f"added {added_count} relationships, skipped {skipped_count} existing"
    )

    return added_count

def _determine_cross_chunk_predicate(self, entity1: Dict, entity2: Dict) -> Optional[str]:
    """
    Determine appropriate predicate for cross-chunk relationship based on entity types.

    Args:
        entity1: First entity document
        entity2: Second entity document

    Returns:
        Predicate string or None if no relationship should be created
    """
    type1 = entity1.get("type", "OTHER")
    type2 = entity2.get("type", "OTHER")

    # Define type-based relationship patterns
    type_patterns = {
        ("PERSON", "CONCEPT"): "discusses",
        ("PERSON", "TECHNOLOGY"): "uses",
        ("PERSON", "ORGANIZATION"): "affiliated_with",
        ("CONCEPT", "CONCEPT"): "related_to",
        ("CONCEPT", "TECHNOLOGY"): "implemented_in",
        ("TECHNOLOGY", "TECHNOLOGY"): "works_with",
        ("ORGANIZATION", "TECHNOLOGY"): "develops",
    }

    # Try both directions
    predicate = type_patterns.get((type1, type2))
    if not predicate:
        predicate = type_patterns.get((type2, type1))

    return predicate if predicate else "mentioned_together"
```

**Integration**: Add to `finalize()` method

**Expected Impact**: Add 30-50 relationships, reduce fragmentation (46 → 30 components)

#### 2.3 Bidirectional Relationship Creation

**Files to Modify**: `app/stages/graph_construction.py`

**Implementation**: Add method `_add_bidirectional_relationships()` for post-processing

```python
def _add_bidirectional_relationships(self) -> int:
    """
    Create reverse relationships for asymmetric relationships to make graph more navigable.

    This creates bidirectional edges for relationships like:
    - "Algorithm uses Data Structure" → "Data Structure used_by Algorithm"
    - "Person teaches Concept" → "Concept taught_by Person"

    Returns:
        Number of reverse relationships added
    """
    logger.info("Starting bidirectional relationship post-processing")

    relations_collection = self.graphrag_collections["relations"]

    # Define reverse predicate mappings
    reverse_predicates = {
        "uses": "used_by",
        "teaches": "taught_by",
        "creates": "created_by",
        "develops": "developed_by",
        "implements": "implemented_by",
        "contains": "contained_in",
        "has": "belongs_to",
        "manages": "managed_by",
        "leads": "led_by",
        "explains": "explained_by",
        "demonstrates": "demonstrated_by",
        "requires": "required_by",
        "depends_on": "dependency_of",
        "applies_to": "applied_by",
        "works_at": "employs",
        "part_of": "has_part",
        "subtype_of": "has_subtype",
        "is_a": "has_instance",
    }

    # Get all relationships that have reverse predicates
    added_count = 0
    skipped_count = 0

    for relationship in relations_collection.find():
        predicate = relationship.get("predicate", "")

        if predicate not in reverse_predicates:
            continue

        reverse_predicate = reverse_predicates[predicate]
        subject_id = relationship["subject_id"]
        object_id = relationship["object_id"]

        # Check if reverse relationship already exists
        existing = relations_collection.find_one({
            "subject_id": object_id,
            "object_id": subject_id,
            "predicate": reverse_predicate
        })

        if existing:
            skipped_count += 1
            continue

        # Create reverse relationship
        relationship_id = ResolvedRelationship.generate_relationship_id(
            object_id, subject_id, reverse_predicate
        )

        reverse_relationship_doc = {
            "relationship_id": relationship_id,
            "subject_id": object_id,
            "object_id": subject_id,
            "predicate": reverse_predicate,
            "description": f"Reverse of: {relationship.get('description', '')}",
            "confidence": relationship.get("confidence", 0.7),
            "source_count": relationship.get("source_count", 1),
            "source_chunks": relationship.get("source_chunks", []),
            "created_at": time.time(),
            "updated_at": time.time(),
            "relationship_type": "bidirectional",
            "original_relationship_id": relationship["relationship_id"],
        }

        try:
            relations_collection.insert_one(reverse_relationship_doc)
            added_count += 1

            if added_count % 50 == 0:
                logger.debug(f"Added {added_count} reverse relationships")

        except Exception as e:
            logger.error(
                f"Failed to insert reverse relationship for {relationship['relationship_id']}: {e}"
            )

    logger.info(
        f"Bidirectional relationship post-processing complete: "
        f"added {added_count} relationships, skipped {skipped_count} existing"
    )

    return added_count
```

**Integration**: Add to `finalize()` method

**Expected Impact**: Double effective edges, improve path finding, better community detection

---

### Phase 3: Advanced Improvements

**Status**: Phase 3 Advanced Improvements

#### 3.1 Graph Embedding-Based Link Prediction

**Files to Create/Modify**:

1. `agents/graph_link_prediction_agent.py` (new)
2. `app/stages/graph_construction.py` (integrate)

**Implementation**: Create link prediction agent using graph embeddings

```python
# agents/graph_link_prediction_agent.py
"""
Graph Link Prediction Agent

Uses graph structure and entity embeddings to predict missing relationships.
"""

import logging
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
import networkx as nx
from collections import defaultdict

logger = logging.getLogger(__name__)


class GraphLinkPredictionAgent:
    """
    Agent for predicting missing links in knowledge graph using graph embeddings.
    """

    def __init__(
        self,
        confidence_threshold: float = 0.65,
        max_predictions_per_entity: int = 5,
        use_structural_features: bool = True,
    ):
        """
        Initialize link prediction agent.

        Args:
            confidence_threshold: Minimum confidence for predicted links
            max_predictions_per_entity: Maximum predicted links per entity
            use_structural_features: Use graph structure for prediction
        """
        self.confidence_threshold = confidence_threshold
        self.max_predictions_per_entity = max_predictions_per_entity
        self.use_structural_features = use_structural_features

    def predict_missing_links(
        self,
        entities: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]],
    ) -> List[Tuple[str, str, str, float]]:
        """
        Predict missing links in the graph.

        Args:
            entities: List of entity documents with embeddings
            relationships: List of existing relationship documents

        Returns:
            List of (subject_id, object_id, predicate, confidence) tuples
        """
        logger.info(f"Starting link prediction for {len(entities)} entities")

        # Build NetworkX graph
        G = nx.Graph()

        for entity in entities:
            G.add_node(entity["entity_id"], **entity)

        for rel in relationships:
            G.add_edge(rel["subject_id"], rel["object_id"], **rel)

        logger.info(f"Built graph with {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

        predictions = []

        # Strategy 1: Common neighbors (structural)
        if self.use_structural_features:
            structural_predictions = self._predict_via_common_neighbors(G)
            predictions.extend(structural_predictions)

        # Strategy 2: Embedding similarity (semantic)
        entities_with_embeddings = [e for e in entities if "entity_embedding" in e]
        if entities_with_embeddings:
            semantic_predictions = self._predict_via_embeddings(
                entities_with_embeddings, G
            )
            predictions.extend(semantic_predictions)

        # Deduplicate and rank by confidence
        predictions = self._deduplicate_predictions(predictions)
        predictions = sorted(predictions, key=lambda x: x[3], reverse=True)

        logger.info(f"Generated {len(predictions)} link predictions")

        return predictions

    def _predict_via_common_neighbors(
        self, G: nx.Graph
    ) -> List[Tuple[str, str, str, float]]:
        """
        Predict links based on common neighbors (Adamic-Adar, Jaccard similarity).

        Args:
            G: NetworkX graph

        Returns:
            List of predictions
        """
        predictions = []

        # Use Adamic-Adar index for link prediction
        try:
            # Get non-edges (potential links)
            non_edges = list(nx.non_edges(G))

            # Calculate Adamic-Adar scores
            aa_scores = nx.adamic_adar_index(G, non_edges[:1000])  # Limit for performance

            for u, v, score in aa_scores:
                if score > 0.5:  # Threshold for structural similarity
                    confidence = min(0.9, score / 10)  # Normalize to 0-0.9

                    # Determine predicate based on node types
                    u_type = G.nodes[u].get("type", "OTHER")
                    v_type = G.nodes[v].get("type", "OTHER")
                    predicate = self._infer_predicate_from_types(u_type, v_type)

                    predictions.append((u, v, predicate, confidence))

        except Exception as e:
            logger.error(f"Failed to compute Adamic-Adar scores: {e}")

        return predictions

    def _predict_via_embeddings(
        self, entities: List[Dict[str, Any]], G: nx.Graph
    ) -> List[Tuple[str, str, str, float]]:
        """
        Predict links based on entity embedding similarity.

        Args:
            entities: Entities with embeddings
            G: NetworkX graph

        Returns:
            List of predictions
        """
        predictions = []

        entity_dict = {e["entity_id"]: e for e in entities}

        # For each entity, find most similar entities without existing connections
        for entity in entities:
            entity_id = entity["entity_id"]
            entity_embedding = np.array(entity["entity_embedding"])

            # Get existing neighbors
            existing_neighbors = set(G.neighbors(entity_id)) if entity_id in G else set()

            similarities = []

            for other_entity in entities:
                other_id = other_entity["entity_id"]

                if other_id == entity_id or other_id in existing_neighbors:
                    continue

                other_embedding = np.array(other_entity["entity_embedding"])

                # Calculate cosine similarity
                similarity = np.dot(entity_embedding, other_embedding) / (
                    np.linalg.norm(entity_embedding) * np.linalg.norm(other_embedding)
                )

                if similarity >= self.confidence_threshold:
                    similarities.append((other_id, similarity))

            # Get top N similar entities
            similarities = sorted(similarities, key=lambda x: x[1], reverse=True)
            top_similar = similarities[:self.max_predictions_per_entity]

            for other_id, similarity in top_similar:
                # Determine predicate
                entity_type = entity.get("type", "OTHER")
                other_type = entity_dict[other_id].get("type", "OTHER")
                predicate = self._infer_predicate_from_types(entity_type, other_type)

                predictions.append((entity_id, other_id, predicate, float(similarity)))

        return predictions

    def _infer_predicate_from_types(self, type1: str, type2: str) -> str:
        """Infer relationship predicate from entity types."""

        type_patterns = {
            ("PERSON", "CONCEPT"): "discusses",
            ("PERSON", "TECHNOLOGY"): "uses",
            ("CONCEPT", "CONCEPT"): "related_to",
            ("CONCEPT", "TECHNOLOGY"): "implemented_in",
            ("TECHNOLOGY", "TECHNOLOGY"): "works_with",
        }

        predicate = type_patterns.get((type1, type2))
        if not predicate:
            predicate = type_patterns.get((type2, type1), "related_to")

        return predicate

    def _deduplicate_predictions(
        self, predictions: List[Tuple[str, str, str, float]]
    ) -> List[Tuple[str, str, str, float]]:
        """Remove duplicate predictions, keeping highest confidence."""

        seen = {}

        for subj, obj, pred, conf in predictions:
            # Create bidirectional key (order-independent)
            key = tuple(sorted([subj, obj])) + (pred,)

            if key not in seen or conf > seen[key][3]:
                seen[key] = (subj, obj, pred, conf)

        return list(seen.values())
```

**Integration into GraphConstructionStage**:

```python
def _add_predicted_relationships(self) -> int:
    """
    Add predicted relationships using graph link prediction.

    Returns:
        Number of predicted relationships added
    """
    logger.info("Starting link prediction post-processing")

    from agents.graph_link_prediction_agent import GraphLinkPredictionAgent

    entities_collection = self.graphrag_collections["entities"]
    relations_collection = self.graphrag_collections["relations"]

    # Get all entities and relationships
    entities = list(entities_collection.find())
    relationships = list(relations_collection.find())

    # Initialize link prediction agent
    link_predictor = GraphLinkPredictionAgent(
        confidence_threshold=float(os.getenv("GRAPHRAG_LINK_PREDICTION_THRESHOLD", "0.65")),
        max_predictions_per_entity=int(os.getenv("GRAPHRAG_MAX_PREDICTIONS_PER_ENTITY", "5")),
        use_structural_features=True,
    )

    # Predict missing links
    predictions = link_predictor.predict_missing_links(entities, relationships)

    logger.info(f"Got {len(predictions)} link predictions")

    added_count = 0

    for subject_id, object_id, predicate, confidence in predictions:
        # Check if relationship already exists
        existing = relations_collection.find_one({
            "$or": [
                {"subject_id": subject_id, "object_id": object_id},
                {"subject_id": object_id, "object_id": subject_id}
            ]
        })

        if existing:
            continue

        # Create predicted relationship
        relationship_id = ResolvedRelationship.generate_relationship_id(
            subject_id, object_id, predicate
        )

        relationship_doc = {
            "relationship_id": relationship_id,
            "subject_id": subject_id,
            "object_id": object_id,
            "predicate": predicate,
            "description": f"Predicted relationship (confidence: {confidence:.3f})",
            "confidence": float(confidence),
            "source_count": 0,  # No direct source
            "source_chunks": [],
            "created_at": time.time(),
            "updated_at": time.time(),
            "relationship_type": "predicted",
            "prediction_confidence": float(confidence),
        }

        try:
            relations_collection.insert_one(relationship_doc)
            added_count += 1

            if added_count % 50 == 0:
                logger.debug(f"Added {added_count} predicted relationships")

        except Exception as e:
            logger.error(
                f"Failed to insert predicted relationship "
                f"{subject_id} <-> {object_id}: {e}"
            )

    logger.info(
        f"Link prediction post-processing complete: added {added_count} relationships"
    )

    return added_count
```

**Expected Impact**: Discover implicit relationships, fill connectivity gaps

---

## Implementation Order

The implementation will be executed in this order within `graph_construction.py`:

1. **Enhanced Extraction Prompt** (Phase 2.1) - First, to capture more relationships in future extractions
2. **Semantic Similarity** (Phase 1) - Post-processing after all chunks processed
3. **Cross-Chunk Relationships** (Phase 2.2) - Post-processing using entity mentions
4. **Bidirectional Relationships** (Phase 2.3) - Post-processing to double edges
5. **Link Prediction** (Phase 3.1) - Final post-processing using graph structure

### Updated `finalize()` Method

```python
def finalize(self) -> None:
    """
    Finalize the graph construction stage with all post-processing.

    This method runs after all documents are processed and performs
    comprehensive post-processing to improve graph connectivity and quality.
    """
    logger.info("=" * 80)
    logger.info("Starting comprehensive graph post-processing")
    logger.info("=" * 80)

    total_added = 0

    # 1. Co-occurrence relationships (already implemented)
    logger.info("[1/5] Adding co-occurrence relationships...")
    try:
        count = self._add_co_occurrence_relationships()
        total_added += count
        logger.info(f"✓ Added {count} co-occurrence relationships")
    except Exception as e:
        logger.error(f"✗ Failed to add co-occurrence relationships: {e}")

    # 2. Semantic similarity relationships
    logger.info("[2/5] Adding semantic similarity relationships...")
    try:
        similarity_threshold = float(os.getenv("GRAPHRAG_SIMILARITY_THRESHOLD", "0.85"))
        count = self._add_semantic_similarity_relationships(similarity_threshold)
        total_added += count
        logger.info(f"✓ Added {count} semantic similarity relationships")
    except Exception as e:
        logger.error(f"✗ Failed to add semantic similarity relationships: {e}")

    # 3. Cross-chunk relationships
    logger.info("[3/5] Adding cross-chunk relationships...")
    try:
        count = self._add_cross_chunk_relationships()
        total_added += count
        logger.info(f"✓ Added {count} cross-chunk relationships")
    except Exception as e:
        logger.error(f"✗ Failed to add cross-chunk relationships: {e}")

    # 4. Bidirectional relationships
    logger.info("[4/5] Adding bidirectional relationships...")
    try:
        count = self._add_bidirectional_relationships()
        total_added += count
        logger.info(f"✓ Added {count} bidirectional relationships")
    except Exception as e:
        logger.error(f"✗ Failed to add bidirectional relationships: {e}")

    # 5. Link prediction (optional, can be disabled)
    if os.getenv("GRAPHRAG_ENABLE_LINK_PREDICTION", "true").lower() == "true":
        logger.info("[5/5] Adding predicted relationships...")
        try:
            count = self._add_predicted_relationships()
            total_added += count
            logger.info(f"✓ Added {count} predicted relationships")
        except Exception as e:
            logger.error(f"✗ Failed to add predicted relationships: {e}")
    else:
        logger.info("[5/5] Link prediction disabled (GRAPHRAG_ENABLE_LINK_PREDICTION=false)")

    logger.info("=" * 80)
    logger.info(f"Graph post-processing complete: added {total_added} total relationships")
    logger.info("=" * 80)

    # Call parent finalize to log statistics
    super().finalize()
```

---

## Configuration

Add these environment variables to `.env`:

```bash
# Graph Construction Post-Processing
GRAPHRAG_SIMILARITY_THRESHOLD=0.85          # Minimum cosine similarity for semantic links
GRAPHRAG_LINK_PREDICTION_THRESHOLD=0.65     # Minimum confidence for predicted links
GRAPHRAG_MAX_PREDICTIONS_PER_ENTITY=5       # Max predicted links per entity
GRAPHRAG_ENABLE_LINK_PREDICTION=true        # Enable/disable link prediction
```

---

## Files to Modify/Create

### Files to Modify:

1. **`agents/graph_extraction_agent.py`**

   - Update system prompt for multiple relationship types
   - Lines 52-88 (system_prompt)

2. **`app/stages/graph_construction.py`**
   - Add 5 new post-processing methods
   - Update `finalize()` method
   - Add imports: `numpy`, `networkx`

### Files to Create:

3. **`agents/graph_link_prediction_agent.py`** (new)
   - Implement link prediction agent
   - ~300 lines

---

## Dependencies

Add to `requirements.txt`:

```
networkx>=3.0
numpy>=1.24.0
scikit-learn>=1.3.0  # For additional graph algorithms if needed
```

---

## Testing Strategy

### 1. Unit Tests

- Test each post-processing method independently
- Mock MongoDB collections
- Verify relationship creation logic

### 2. Integration Test

Run complete pipeline and verify:

```bash
# Run GraphRAG pipeline with all improvements
python run_graphrag_pipeline.py --db-name youtube_rag --max 100

# Verify improvements
python scripts/analyze_graph_structure.py
```

### 3. Metrics Verification

Check that metrics meet targets:

- **Relationships**: 100 → 300+ (3x increase)
- **Graph Density**: 0.0107 → 0.030 (2.8x increase)
- **Isolated Nodes**: 36 → <14 (60% reduction)
- **Average Degree**: 1.46 → 2.5+ (70% increase)
- **Communities**: 0 → 10-15 multi-entity communities

---

## Performance Considerations

### Optimization Strategies:

1. **Batching**: Process embeddings in batches of 100
2. **Caching**: Cache entity embeddings after first computation
3. **Indexing**: Ensure MongoDB indexes on `entity_id`, `subject_id`, `object_id`
4. **Parallel Processing**: Use ThreadPoolExecutor for independent post-processing steps
5. **Limiting**: Use limits for combinatorial operations (e.g., max 1000 entity pairs for similarity)

### Expected Runtime:

- **Semantic Similarity**: ~2-3 minutes for 137 entities (with embedding generation)
- **Cross-Chunk**: ~1-2 minutes
- **Bidirectional**: ~30 seconds
- **Link Prediction**: ~2-3 minutes
- **Total Post-Processing**: ~10-15 minutes for complete graph

---

## Rollback Plan

If improvements cause issues:

1. **Disable post-processing**: Set `GRAPHRAG_ENABLE_LINK_PREDICTION=false`
2. **Remove predicted relationships**:
   ```python
   db.relations.deleteMany({"relationship_type": {"$in": ["co_occurrence", "semantic_similarity", "cross_chunk", "bidirectional", "predicted"]}})
   ```
3. **Revert extraction prompt**: Restore original `system_prompt` in `graph_extraction_agent.py`

---

## Success Criteria

### Phase Completion:

- ✅ **Phase 1**: Semantic similarity implemented, 30-50 new relationships
- ✅ **Phase 2**: Enhanced extraction + cross-chunk + bidirectional, 150-200 new relationships
- ✅ **Phase 3**: Link prediction working, 20-30 predicted relationships

### Overall Success:

- ✅ Relationship count ≥ 300
- ✅ Isolated nodes < 15
- ✅ Multi-entity communities ≥ 10
- ✅ Graph density ≥ 0.025
- ✅ No performance degradation (pipeline completes in reasonable time)

---

## Next Steps After Implementation

1. **Monitor**: Track relationship quality and graph metrics over multiple runs
2. **Tune**: Adjust confidence thresholds based on results
3. **Extend**: Add more sophisticated link prediction (e.g., graph neural networks)
4. **Visualize**: Create graph visualization to inspect improvements
5. **Query**: Test GraphRAG queries to ensure improved retrieval quality

---

## Summary

This comprehensive plan consolidates all 6 remaining improvements into a unified implementation that will:

- **Triple relationship count** (100 → 300+)
- **Reduce isolated entities by 60%** (36 → <15)
- **Create 10-15 meaningful communities**
- **Improve graph density by 180%** (0.0107 → 0.030)
- **Enable rich graph traversal and query capabilities**

All improvements are implemented as post-processing steps in `graph_construction.py`, making them modular, testable, and configurable via environment variables.
