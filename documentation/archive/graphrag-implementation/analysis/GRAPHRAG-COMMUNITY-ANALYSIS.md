# GraphRAG Community Detection Analysis

## Problem Statement

After running the GraphRAG pipeline, we observe:

- **90 communities** detected
- **All communities have `entity_count: 1`** (single entity each)
- **All communities have `relationship_count: 0`** (no relationships)
- **All communities have `coherence_score: 1.0`** (artificially high)

This defeats the purpose of community detection, which should identify **groups of related entities**, not individual isolated entities.

## Root Cause Analysis

### 1. **Isolated Entity Problem** ⚠️

The graph likely has **very few or no relationships** connecting entities. Looking at the sample communities:

- Entities like "Algorithm", "Problem Specification", "N", "Student N Plus 1", "IBM", "Computer Scientist", "Recitation"
- All are isolated with 0 relationships
- This suggests relationships are either:
  - Not being extracted properly in `graph_extraction`
  - Not being resolved/stored properly in `graph_construction`
  - Being filtered out during validation

### 2. **Community Detection Logic Issue** 🐛

**Location**: `agents/community_detection_agent.py`, `_fallback_community_detection()` method (lines 167-199)

**Problem**: The fallback community detection creates communities for isolated nodes even though `min_cluster_size=2`:

```python
def _fallback_community_detection(self, G: nx.Graph) -> List[Any]:
    communities = []
    for i, component in enumerate(nx.connected_components(G)):
        if len(component) >= self.min_cluster_size:  # ✅ Only creates if >= 2
            # ... creates community
        # ❌ BUT: Single isolated nodes are NOT in connected_components
        # They're implicitly added as separate communities somewhere
```

**Actual Issue**: If the graph has many isolated nodes (entities with no relationships), and `hierarchical_leiden` fails or returns single-node communities, the code doesn't filter them out properly.

### 3. **No Single-Entity Filtering** ❌

**Location**: `agents/community_detection_agent.py`, `_organize_communities_by_level()` method (lines 201-276)

**Problem**: The code processes ALL communities returned by the detection algorithm, including single-entity ones. There's no filtering based on `min_cluster_size` or `min_entity_count`:

```python
def _organize_communities_by_level(...):
    # Processes all communities, including single-entity ones
    for community in communities:
        # ... creates community data structure
        # ❌ No check for min_entity_count here!
```

**Config Setting**: `CommunityDetectionConfig.min_entity_count: int = 2` exists but **is not used** to filter communities.

### 4. **Coherence Score Issue** 📊

**Location**: `agents/community_detection_agent.py`, `_calculate_coherence_score()` method (lines 278-326)

**Problem**: Single-entity communities automatically get `coherence_score = 1.0`:

```python
if len(entities) == 1:
    return 1.0  # ❌ Artificially high score for isolated entities
```

This masks the fact that these are low-quality, isolated communities.

## Impact Assessment

### Data Quality Issues

1. **90 communities with 1 entity each** = 90 isolated entities, not meaningful communities
2. **0 relationships** = Graph is not connected, relationships may not be working
3. **Coherence = 1.0** = Misleading quality metric
4. **Community summaries** = Wasted LLM calls summarizing single entities as "communities"

### Functional Issues

1. **Community-based retrieval won't work** - Can't find related entities if none are connected
2. **Graph traversal fails** - No paths between entities
3. **Query expansion ineffective** - Can't expand queries to related entities
4. **Wasted resources** - LLM summarization of non-communities

## Investigation Steps

### Step 1: Check Relationship Data ✅

```python
# Check if relationships exist
db = client[mongo_hack]
relations = db.relations
print(f"Total relationships: {relations.count_documents({})}")

# Check relationship distribution
for rel in relations.find().limit(10):
    print(rel)
```

**Expected**: Should see many relationships with `subject_id` and `object_id` (32-char MD5 hashes)

**If 0 relationships**: The problem is in `graph_extraction` or `graph_construction`

### Step 2: Check Graph Connectivity ✅

```python
# Check entity-to-relationship mapping
entities = db.entities
relations = db.relations

entity_ids = {e["entity_id"] for e in entities.find()}
related_entity_ids = set()

for rel in relations.find():
    related_entity_ids.add(rel["subject_id"])
    related_entity_ids.add(rel["object_id"])

isolated_entities = entity_ids - related_entity_ids
print(f"Total entities: {len(entity_ids)}")
print(f"Entities in relationships: {len(related_entity_ids)}")
print(f"Isolated entities: {len(isolated_entities)}")
```

**Expected**: Most entities should be in relationships, few isolated

**If many isolated**: Relationships not being extracted/created properly

### Step 3: Check Community Detection Input ✅

```python
# Check what community detection received
entities_count = entities.count_documents({})
relationships_count = relations.count_documents({})

print(f"Community detection input:")
print(f"  Entities: {entities_count}")
print(f"  Relationships: {relationships_count}")
print(f"  Graph should have {relationships_count} edges")
```

**Expected**: Reasonable number of relationships (at least 10% of entities should have relationships)

## Recommended Fixes

### Fix 1: Filter Single-Entity Communities 🔧

**Location**: `agents/community_detection_agent.py`, `_organize_communities_by_level()`

**Change**: Filter out communities that don't meet `min_entity_count`:

```python
def _organize_communities_by_level(
    self,
    communities: List[Any],
    entities: List[ResolvedEntity],
    relationships: List[ResolvedRelationship],
) -> Dict[int, Dict[str, Any]]:
    organized = defaultdict(dict)
    level_communities = defaultdict(list)

    for community in communities:
        level = max(1, getattr(community, "level", 1))
        level_communities[level].append(community)

    for level, level_comm_list in level_communities.items():
        for i, community in enumerate(level_comm_list):
            # Get entity IDs
            if hasattr(community, "nodes"):
                entity_ids = list(community.nodes)
            else:
                entity_ids = [getattr(community, "node", "")]

            # ✅ FILTER: Skip single-entity communities
            if len(entity_ids) < self.min_cluster_size:
                logger.debug(
                    f"Skipping single-entity community with {len(entity_ids)} entities "
                    f"(min_cluster_size={self.min_cluster_size})"
                )
                continue

            # ... rest of processing
```

### Fix 2: Improve Coherence Score for Isolated Entities 🔧

**Location**: `agents/community_detection_agent.py`, `_calculate_coherence_score()`

**Change**: Penalize single-entity communities:

```python
def _calculate_coherence_score(...) -> float:
    if not entities:
        return 0.0

    if len(entities) == 1:
        return 0.0  # ✅ Changed from 1.0 - isolated entities have no coherence
        # Or return 0.1 if you want to keep them but mark as low quality

    # ... rest of calculation
```

### Fix 3: Add Relationship Extraction Validation 🔧

**Location**: `app/stages/graph_extraction.py`

**Action**: Add logging to verify relationships are being extracted:

```python
def handle_doc(self, doc: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    # ... extraction logic ...

    # ✅ ADD: Log relationship extraction stats
    if knowledge_model:
        entity_count = len(knowledge_model.entities)
        relationship_count = len(knowledge_model.relationships)

        logger.info(
            f"Chunk {chunk_id}: Extracted {entity_count} entities, "
            f"{relationship_count} relationships"
        )

        # Warn if no relationships extracted
        if relationship_count == 0 and entity_count > 1:
            logger.warning(
                f"Chunk {chunk_id}: {entity_count} entities but 0 relationships "
                f"extracted - potential extraction issue"
            )
```

### Fix 4: Validate Graph Construction Output 🔧

**Location**: `app/stages/graph_construction.py`

**Action**: Add validation that relationships are being created:

```python
def handle_doc(self, doc: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    # ... construction logic ...

    # ✅ ADD: Validate relationships were stored
    stored_relationships = self._store_resolved_relationships(...)

    if len(stored_relationships) == 0:
        logger.warning(
            f"Chunk {chunk_id}: No relationships stored despite "
            f"{len(validated_relationships)} resolved relationships"
        )
```

## Immediate Actions

### 1. Query Database to Understand Current State

Run these queries to understand the data:

```python
from app.services.utils import get_mongo_client
from config.paths import DB_NAME

client = get_mongo_client()
db = client[DB_NAME]

# Count entities
entities_count = db.entities.count_documents({})
print(f"Total entities: {entities_count}")

# Count relationships
relations_count = db.relations.count_documents({})
print(f"Total relationships: {relations_count}")

# Count communities
communities_count = db.communities.count_documents({})
print(f"Total communities: {communities_count}")

# Check community sizes
community_sizes = {}
for comm in db.communities.find():
    size = comm.get("entity_count", 0)
    community_sizes[size] = community_sizes.get(size, 0) + 1

print(f"Community size distribution: {community_sizes}")

# Check if relationships exist
if relations_count > 0:
    sample_rel = db.relations.find_one()
    print(f"Sample relationship: {sample_rel}")
else:
    print("⚠️ NO RELATIONSHIPS FOUND - This is the root cause!")
```

### 2. Check Graph Extraction Output

```python
# Check if chunks have relationship data
chunk_with_rels = db.video_chunks.find_one({
    "graphrag_extraction.data.relationships": {"$exists": True, "$ne": []}
})

if chunk_with_rels:
    extraction_data = chunk_with_rels.get("graphrag_extraction", {}).get("data", {})
    print(f"Sample extraction - entities: {len(extraction_data.get('entities', []))}")
    print(f"Sample extraction - relationships: {len(extraction_data.get('relationships', []))}")
else:
    print("⚠️ NO CHUNKS WITH RELATIONSHIPS - Check graph_extraction stage!")
```

## Conclusion

**Primary Issue**: Either relationships are not being extracted, or they're not being stored/connected properly, resulting in a disconnected graph with isolated entities.

**Secondary Issue**: Community detection is creating communities for isolated entities instead of filtering them out, wasting LLM calls and creating misleading data.

**Next Steps**:

1. Run database queries above to confirm root cause
2. Fix relationship extraction/storage if needed
3. Add filtering for single-entity communities
4. Re-run community detection after fixes
