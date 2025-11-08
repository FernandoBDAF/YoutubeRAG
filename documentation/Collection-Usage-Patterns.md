# Collection Usage Patterns

**Purpose**: Demonstrate how different components use legacy and new collections  
**Date**: 2025-11-10  
**Status**: Active Reference Guide

---

## Quick Reference

### Import Pattern

```python
# All collection names now defined in core/config/paths.py
from core.config.paths import (
    # Legacy collections
    COLL_ENTITIES,
    COLL_RELATIONS,
    COLL_COMMUNITIES,
    COLL_ENTITY_MENTIONS,

    # New collections
    COLL_TRANSFORMATION_LOGS,
    COLL_ENTITIES_RAW,
    COLL_ENTITIES_RESOLVED,
    COLL_RELATIONS_RAW,
    COLL_RELATIONS_FINAL,
    COLL_GRAPH_PRE_DETECTION,
    COLL_QUALITY_METRICS,
    COLL_GRAPHRAG_RUNS,
)
```

### Access Pattern

```python
# Using collection names from paths.py
db = get_database()
legacy_entities = db[COLL_ENTITIES]
new_transformation_logs = db[COLL_TRANSFORMATION_LOGS]

# Not recommended (hardcoding):
# legacy_entities = db['entities']  # ❌ Avoid
```

---

## Domain-Specific Patterns

### 1. Extraction Stage

**Role**: Takes text chunks and extracts initial entities and relationships

**Collections Used**:

| Collection          | Access | Purpose                       | Schema                                               |
| ------------------- | ------ | ----------------------------- | ---------------------------------------------------- |
| video_chunks        | Read   | Input text to extract from    | { \_id, text, chunk_id }                             |
| entities_raw        | Write  | Store extracted entities      | { trace_id, raw_entity_id, text, type, confidence }  |
| relations_raw       | Write  | Store extracted relationships | { trace_id, raw_rel_id, subject, predicate, object } |
| transformation_logs | Write  | Log extraction operations     | { trace_id, operation: "EXTRACT" }                   |

**Code Example** (Extraction Service):

```python
from core.config.paths import COLL_ENTITIES_RAW, COLL_TRANSFORMATION_LOGS

class ExtractionService:
    def extract_entities(self, chunk, trace_id):
        # Extract entities from chunk
        raw_entities = self.llm.extract_entities(chunk.text)

        # Store in new collection
        entities_raw = self.db[COLL_ENTITIES_RAW]
        for entity in raw_entities:
            entities_raw.insert_one({
                "trace_id": trace_id,
                "raw_entity_id": generate_id(),
                "text": entity.text,
                "type": entity.type,
                "confidence": entity.confidence,
                "timestamp": time.time(),
            })

        # Log extraction
        logger.log_extraction(trace_id, len(raw_entities))

        return raw_entities
```

**What Happens**:

1. Chunk enters extraction stage
2. LLM extracts entities and relationships
3. Raw entities stored in `entities_raw`
4. Raw relationships stored in `relations_raw`
5. Operation logged to `transformation_logs`
6. Quality metrics will later compare raw vs resolved counts

---

### 2. Entity Resolution Stage

**Role**: Deduplicates and merges entity references into canonical entities

**Collections Used**:

| Collection          | Access     | Purpose                       | Schema                                                   |
| ------------------- | ---------- | ----------------------------- | -------------------------------------------------------- |
| entities_raw        | Read       | Input: raw extracted entities | { trace_id, raw_entity_id, text, type, confidence }      |
| entities            | Read/Write | Legacy: final entities list   | { \_id, type, properties }                               |
| entities_resolved   | Write      | Output: deduplicated entities | { trace_id, entity_id, canonical_text, merged_from: [] } |
| transformation_logs | Write      | Log merge operations          | { operation: "MERGE", entity_id, reason, confidence }    |

**Code Example** (Entity Resolution):

```python
from core.config.paths import (
    COLL_ENTITIES_RAW,
    COLL_ENTITIES,
    COLL_ENTITIES_RESOLVED,
    COLL_TRANSFORMATION_LOGS
)

class EntityResolutionService:
    def resolve_entities(self, trace_id):
        # Read raw extracted entities
        entities_raw = self.db[COLL_ENTITIES_RAW]
        raw_entities = list(entities_raw.find({"trace_id": trace_id}))

        # Deduplicate and merge
        resolved_groups = self.deduplicate(raw_entities)

        # Store in new collection
        entities_resolved = self.db[COLL_ENTITIES_RESOLVED]
        for group in resolved_groups:
            resolved_doc = {
                "trace_id": trace_id,
                "entity_id": generate_id(),
                "canonical_text": group.canonical,
                "merged_from": [e["raw_entity_id"] for e in group.members],
                "confidence": group.confidence,
            }
            entities_resolved.insert_one(resolved_doc)

            # Log merge operation
            self.logger.log_merge(
                trace_id=trace_id,
                entity_id=resolved_doc["entity_id"],
                merge_count=len(group.members),
                reason="deduplication"
            )

        # Also update legacy collection for backward compatibility
        legacy_entities = self.db[COLL_ENTITIES]
        for resolved in entities_resolved.find({"trace_id": trace_id}):
            legacy_entities.update_one(
                {"_id": resolved["entity_id"]},
                {"$set": resolved},
                upsert=True
            )

        return resolved_groups
```

**What Happens**:

1. Raw entities read from `entities_raw`
2. Deduplication merges similar entities
3. Resolved entities stored in `entities_resolved`
4. Legacy entities also updated for backward compatibility
5. Each merge operation logged to `transformation_logs`
6. Quality metrics later calculate merge_rate from raw vs resolved counts

---

### 3. Graph Construction Stage

**Role**: Builds entity-relationship graph from resolved entities and relationships

**Collections Used**:

| Collection          | Access     | Purpose                             | Schema                                                        |
| ------------------- | ---------- | ----------------------------------- | ------------------------------------------------------------- |
| entities_resolved   | Read       | Canonical entities                  | { trace_id, entity_id, canonical_text }                       |
| relations_raw       | Read       | Raw extracted relationships         | { trace_id, subject_text, predicate, object_text }            |
| relations           | Read/Write | Legacy: final relationships         | { \_id, source, target, predicate }                           |
| relations_final     | Write      | Output: validated relationships     | { trace_id, relation_id, source_entity_id, target_entity_id } |
| graph_pre_detection | Write      | Pre-detection graph snapshot        | { trace_id, nodes: [], edges: [] }                            |
| transformation_logs | Write      | Log filtering/validation operations | { operation: "VALIDATE_RELATION" }                            |

**Code Example** (Graph Construction):

```python
from core.config.paths import (
    COLL_ENTITIES_RESOLVED,
    COLL_RELATIONS_RAW,
    COLL_RELATIONS,
    COLL_RELATIONS_FINAL,
    COLL_GRAPH_PRE_DETECTION,
    COLL_TRANSFORMATION_LOGS
)

class GraphConstructionService:
    def construct_graph(self, trace_id):
        # Read resolved entities
        entities_resolved = self.db[COLL_ENTITIES_RESOLVED]
        entities = list(entities_resolved.find({"trace_id": trace_id}))

        # Read raw relationships
        relations_raw = self.db[COLL_RELATIONS_RAW]
        raw_relations = list(relations_raw.find({"trace_id": trace_id}))

        # Build and validate graph
        validated_relations = self.validate_relations(raw_relations, entities)

        # Store final relationships
        relations_final = self.db[COLL_RELATIONS_FINAL]
        for rel in validated_relations:
            relations_final.insert_one({
                "trace_id": trace_id,
                "relation_id": generate_id(),
                "source_entity_id": rel.source_id,
                "target_entity_id": rel.target_id,
                "predicate": rel.predicate,
                "confidence": rel.confidence,
            })

            # Log validation
            self.logger.log_relation_validation(
                trace_id=trace_id,
                predicate=rel.predicate,
                status="valid"
            )

        # Store legacy relationships for backward compatibility
        legacy_relations = self.db[COLL_RELATIONS]
        for rel in relations_final.find({"trace_id": trace_id}):
            legacy_relations.update_one(
                {"_id": rel["relation_id"]},
                {"$set": rel},
                upsert=True
            )

        # Store pre-detection snapshot
        graph_snapshot = {
            "trace_id": trace_id,
            "nodes": [e["entity_id"] for e in entities],
            "edges": [
                (r["source_entity_id"], r["target_entity_id"])
                for r in relations_final.find({"trace_id": trace_id})
            ],
            "node_count": len(entities),
            "edge_count": len(list(relations_final.find({"trace_id": trace_id}))),
        }
        self.db[COLL_GRAPH_PRE_DETECTION].insert_one(graph_snapshot)

        return graph_snapshot
```

**What Happens**:

1. Resolved entities read from `entities_resolved`
2. Raw relationships read from `relations_raw`
3. Relationships validated against entity list
4. Valid relationships stored in `relations_final`
5. Graph snapshot saved pre-community-detection
6. Both new and legacy collections updated
7. Operations logged to `transformation_logs`

---

### 4. Community Detection Stage

**Role**: Identifies clusters (communities) of related entities

**Collections Used**:

| Collection          | Access     | Purpose                          | Schema                     |
| ------------------- | ---------- | -------------------------------- | -------------------------- |
| graph_pre_detection | Read       | Graph structure before detection | { trace_id, nodes, edges } |
| communities         | Read/Write | Legacy: detected communities     | { \_id, members: [] }      |
| transformation_logs | Write      | Log clustering operations        | { operation: "CLUSTER" }   |

**Code Example** (Community Detection):

```python
from core.config.paths import (
    COLL_GRAPH_PRE_DETECTION,
    COLL_COMMUNITIES,
    COLL_TRANSFORMATION_LOGS
)

class CommunityDetectionService:
    def detect_communities(self, trace_id):
        # Read pre-detection graph
        graph_collection = self.db[COLL_GRAPH_PRE_DETECTION]
        graph = graph_collection.find_one({"trace_id": trace_id})

        if not graph:
            logger.warning(f"No graph found for trace_id={trace_id}")
            return []

        # Detect communities using algorithm
        communities = self.community_algorithm(graph)

        # Store in legacy collection
        communities_col = self.db[COLL_COMMUNITIES]
        for community in communities:
            communities_col.insert_one({
                "_id": generate_id(),
                "members": community.member_ids,
                "size": len(community.member_ids),
                "trace_id": trace_id,
            })

            # Log clustering
            self.logger.log_clustering(
                trace_id=trace_id,
                community_size=len(community.member_ids),
                algorithm="louvain"
            )

        return communities
```

**What Happens**:

1. Pre-detection graph read from `graph_pre_detection`
2. Community algorithm applied to graph
3. Communities stored in legacy `communities` collection
4. Clustering operations logged
5. Quality metrics will calculate modularity, coverage from final communities

---

### 5. Quality Metrics Engine

**Role**: Calculates 23 quality metrics from intermediate data and transformation logs

**Collections Used** (Complex Multi-Collection Analysis):

| Collection          | Access | Purpose             | Calculation Basis                 |
| ------------------- | ------ | ------------------- | --------------------------------- |
| entities_raw        | Read   | Raw entities        | Baseline for raw_entity_count     |
| entities_resolved   | Read   | Resolved entities   | For merge_rate calculation        |
| relations_raw       | Read   | Raw relationships   | Baseline for relationship quality |
| relations_final     | Read   | Final relationships | For predicate distribution        |
| transformation_logs | Read   | All transformations | For operation counts, reasons     |
| quality_metrics     | Write  | Calculated metrics  | Stores 23 calculated values       |
| graphrag_runs       | Write  | Run metadata        | Stores trace_id, timing, config   |

**Code Example** (Quality Metrics):

```python
from core.config.paths import (
    COLL_ENTITIES_RAW,
    COLL_ENTITIES_RESOLVED,
    COLL_RELATIONS_RAW,
    COLL_RELATIONS_FINAL,
    COLL_TRANSFORMATION_LOGS,
    COLL_QUALITY_METRICS,
    COLL_GRAPHRAG_RUNS
)

class QualityMetricsEngine:
    def calculate_metrics(self, trace_id):
        # Read intermediate data
        entities_raw = list(self.db[COLL_ENTITIES_RAW].find({"trace_id": trace_id}))
        entities_resolved = list(self.db[COLL_ENTITIES_RESOLVED].find({"trace_id": trace_id}))
        relations_raw = list(self.db[COLL_RELATIONS_RAW].find({"trace_id": trace_id}))
        relations_final = list(self.db[COLL_RELATIONS_FINAL].find({"trace_id": trace_id}))
        logs = list(self.db[COLL_TRANSFORMATION_LOGS].find({"trace_id": trace_id}))

        # Calculate 23 metrics
        metrics = {
            "trace_id": trace_id,

            # Entity metrics
            "raw_entity_count": len(entities_raw),
            "resolved_entity_count": len(entities_resolved),
            "merge_rate": (len(entities_raw) - len(entities_resolved)) / len(entities_raw) if entities_raw else 0,
            "entity_type_diversity": len(set(e.get("type") for e in entities_raw)),
            "average_confidence": sum(e.get("confidence", 0) for e in entities_resolved) / len(entities_resolved) if entities_resolved else 0,

            # Relationship metrics
            "raw_relation_count": len(relations_raw),
            "final_relation_count": len(relations_final),
            "relation_filter_rate": (len(relations_raw) - len(relations_final)) / len(relations_raw) if relations_raw else 0,
            "predicate_diversity": len(set(r.get("predicate") for r in relations_final)),

            # Transformation metrics
            "merge_operations": len([l for l in logs if l.get("operation") == "MERGE"]),
            "filter_operations": len([l for l in logs if l.get("operation") == "FILTER"]),
            "create_operations": len([l for l in logs if l.get("operation") == "CREATE"]),

            # Calculated metrics (23 total)
            # ... other 13 metrics ...

            "timestamp": time.time(),
        }

        # Store metrics
        self.db[COLL_QUALITY_METRICS].insert_one(metrics)

        # Store run metadata
        run_metadata = {
            "trace_id": trace_id,
            "metrics_count": len(metrics),
            "calculation_time": time.time(),
            "status": "complete",
        }
        self.db[COLL_GRAPHRAG_RUNS].insert_one(run_metadata)

        return metrics
```

**What Happens**:

1. All intermediate collections queried
2. 23 metrics calculated from before/after data
3. Metrics stored in `quality_metrics`
4. Run metadata stored in `graphrag_runs`
5. Metrics become queryable for analysis and visualization

---

### 6. Query Scripts (Analysis Tools)

**Role**: Enable users to query and analyze pipeline behavior

**Collections Used**:

| Script                   | Collections                     | Purpose                   | Example Query                             |
| ------------------------ | ------------------------------- | ------------------------- | ----------------------------------------- |
| query_entities.py        | entities (legacy)               | Query final entities      | Find entities of type "PERSON"            |
| query_relations.py       | relations (legacy)              | Query final relationships | Find relationships with predicate "leads" |
| explain_merge.py         | transformation_logs             | Why entities merged       | Show merge reason for entity_id           |
| show_entity_evolution.py | entities_raw, entities_resolved | Entity transformation     | Show how entities changed                 |
| analyze_quality.py       | quality_metrics                 | Quality analysis          | Show merge_rate and false_negative_rate   |
| debug_stage.py           | intermediate collections        | Debug specific stage      | Show relations_raw vs relations_final     |

**Code Example** (Explain Merge Query):

```python
from core.config.paths import COLL_TRANSFORMATION_LOGS, COLL_ENTITIES_RESOLVED

def explain_merge(entity_id):
    """Explain why an entity exists and what was merged into it"""

    # Find merge operations for this entity
    logs = db[COLL_TRANSFORMATION_LOGS].find({
        "operation": "MERGE",
        "entity_id": entity_id
    })

    merge_events = list(logs)

    print(f"Entity {entity_id} was created by merging {len(merge_events)} raw entities:")
    for event in merge_events:
        print(f"  - {event['reason']}")
        print(f"    Confidence: {event['confidence']}")
        print(f"    Timestamp: {event['timestamp']}")

    # Show final entity
    final_entity = db[COLL_ENTITIES_RESOLVED].find_one({
        "entity_id": entity_id
    })
    print(f"\nFinal entity properties:")
    print(f"  Canonical text: {final_entity['canonical_text']}")
    print(f"  Merged from: {final_entity['merged_from']}")
```

**What Happens**:

1. Query scripts search transformation_logs for operations
2. Can correlate with intermediate data for before/after analysis
3. Combine legacy and new collections for complete picture
4. Enable root cause analysis and debugging

---

## Best Practices

### 1. Use Constants from paths.py

✅ **Do This**:

```python
from core.config.paths import COLL_ENTITIES_RAW, COLL_ENTITIES_RESOLVED
collection = db[COLL_ENTITIES_RAW]
```

❌ **Don't Do This**:

```python
collection = db["entities_raw"]  # Hardcoded
```

**Why**: Constants in one place, changes propagate automatically

### 2. Include trace_id for Traceability

✅ **Do This**:

```python
document = {
    "trace_id": trace_id,  # Links to other pipeline data
    "entity_id": entity_id,
    "data": data,
}
```

❌ **Don't Do This**:

```python
document = {
    "entity_id": entity_id,  # No trace link
    "data": data,
}
```

**Why**: Enables correlation across collections for analysis

### 3. Support Both Legacy and New Collections

✅ **Do This**:

```python
# Update both for compatibility during coexistence period
legacy_collection.insert_one(doc_for_legacy)
new_collection.insert_one(doc_for_new)
```

❌ **Don't Do This**:

```python
# Only write to new collection
new_collection.insert_one(doc_for_new)
# Breaks legacy code reading from old collection
```

**Why**: Maintains backward compatibility during transition

### 4. Use Indexes for Performance

✅ **Do This**:

```python
# In initialization
collection.create_index("trace_id")
collection.create_index([("trace_id", 1), ("entity_id", 1)])
```

❌ **Don't Do This**:

```python
# No indexes - queries slow on large collections
```

**Why**: Intermediate data collections large and frequently queried

### 5. Log Operations for Traceability

✅ **Do This**:

```python
logger.log_merge(
    trace_id=trace_id,
    entity_id=resolved_entity_id,
    reason="duplicate_detection",
    confidence=confidence_score
)
```

❌ **Don't Do This**:

```python
# Silent operation - no logging
```

**Why**: transformation_logs enable "why" questions later

---

## Migration Notes (Future)

### When Migrating from Coexistence to Single Schema

1. **Stop dual-writing** to legacy collections (Phase 2, future)
2. **Migrate queries** one-by-one to new collections
3. **Validate results** match between old and new
4. **Archive legacy** data to historical collections
5. **Update imports** to use new collection constants
6. **Deprecate old constants** (keep for backward compatibility period)

### Gradual Transition Example

```python
# Phase 1 (Current): Write to both
legacy_col.insert_one(doc_legacy)
new_col.insert_one(doc_new)

# Phase 2 (Future): Write to new, read from both
new_col.insert_one(doc_new)
legacy_data = legacy_col.find()  # Still read from old during validation

# Phase 3 (Future): Only new collection
new_col.insert_one(doc_new)
# Stop reading from legacy
```

---

## References

**Configuration**:

- `core/config/paths.py` - Collection constant definitions

**Services Using Collections**:

- `business/services/graphrag/transformation_logger.py` - Writes transformation_logs
- `business/services/graphrag/intermediate_data.py` - Manages intermediate collections
- `business/services/graphrag/quality_metrics.py` - Reads intermediate, writes quality_metrics
- `business/stages/graphrag/*.py` - Stage implementations

**Query Scripts**:

- `scripts/repositories/graphrag/` - Analysis and query tools

**Related Documentation**:

- `Collection-Compatibility-Matrix.md` - High-level collection relationships
- `PLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE.md` - Infrastructure implementation plan
- `PLAN_GRAPHRAG-OBSERVABILITY-VALIDATION.md` - Validation plan

---

**Status**: ✅ Complete - Usage patterns documented and exemplified  
**Last Updated**: 2025-11-10
