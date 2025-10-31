# GraphRAG Community Detection Diagnosis

## Key Findings from Logs

From the latest successful run (after fixes):

- **Graph structure**: 106 nodes, 61 edges
- **hierarchical_leiden output**: Detected **90 communities** from 106 nodes
- **Result**: All 90 communities have `entity_count: 1` and `relationship_count: 0`

## The Problem

### 1. **hierarchical_leiden is Working** ✅

Logs show:

```
Created graph with 106 nodes and 61 edges
Detected 90 communities using hierarchical Leiden
```

**This means `hierarchical_leiden` IS running successfully** (after removing unsupported parameters).

### 2. **The Algorithm is Creating Single-Node Communities** ❌

**Math Check**:

- 106 nodes → 90 communities
- Ratio: ~1.18 nodes per community
- **This means most communities have only 1 node!**

### 3. **Why This Happens**

#### A. **Sparse Graph**

- **Graph density**: 61 edges / (106 × 105 / 2) = **~0.011** (very sparse!)
- **Low connectivity**: Only 61 edges connecting 106 nodes means many isolated or weakly connected nodes
- **Isolated entities**: 36 entities have no relationships (from diagnostic script)

#### B. **hierarchical_leiden Behavior**

`hierarchical_leiden` with `max_cluster_size=10`:

- **Creates communities for ALL nodes**, including isolated ones
- **Isolated nodes** (no edges) get their own single-node community
- **Weakly connected nodes** might also get single-node communities if connections are weak
- The algorithm doesn't filter based on minimum size

#### C. **Our Code Doesn't Filter**

**Location**: `agents/community_detection_agent.py`, `_organize_communities_by_level()` (lines 238-274)

**The Bug**:

```python
if hasattr(community, "nodes"):
    entity_ids = list(community.nodes)
else:
    # Single node community - NO FILTERING HERE!
    entity_ids = [getattr(community, "node", "")]
```

**Problem**: The code processes ALL communities returned by `hierarchical_leiden`, including single-node ones. There's **no check for `min_cluster_size`**.

**Config exists but isn't used**:

- `CommunityDetectionConfig.min_cluster_size: int = 2` ✅ Defined
- `CommunityDetectionConfig.min_entity_count: int = 2` ✅ Defined
- **But neither is checked in `_organize_communities_by_level()`** ❌

## Root Cause Summary

1. ✅ **Graph has relationships** (105 relationships, 61 edges)
2. ✅ **hierarchical_leiden is working** (detecting 90 communities)
3. ❌ **Graph is sparse** (low density, 36 isolated entities)
4. ❌ **hierarchical_leiden creates single-node communities** for isolated/weak nodes
5. ❌ **Our code doesn't filter** single-node communities (ignores `min_cluster_size`)

## What hierarchical_leiden Returns

Based on the code structure, `hierarchical_leiden` returns a list of community objects where:

- Each community object can have:
  - `nodes` (set) - for multi-node communities
  - `node` (single value) - for single-node communities
  - `level` (int) - hierarchical level
  - `cluster` (int) - cluster ID

The algorithm returns **one community per node** when:

- Nodes are isolated (no edges)
- Graph connectivity is very low
- `max_cluster_size` forces small communities

## Solutions

### Solution 1: Filter Single-Node Communities (Immediate Fix) 🔧

**Location**: `agents/community_detection_agent.py`, `_organize_communities_by_level()`

**Fix**: Add filtering based on `min_cluster_size`:

```python
def _organize_communities_by_level(...):
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

            # ✅ ADD FILTER: Skip communities below min_cluster_size
            if len(entity_ids) < self.min_cluster_size:
                logger.debug(
                    f"Skipping community with {len(entity_ids)} entities "
                    f"(min_cluster_size={self.min_cluster_size})"
                )
                continue

            # ... rest of processing
```

### Solution 2: Improve Graph Connectivity (Long-term) 🎯

The graph is too sparse. To create meaningful communities:

1. **Extract more relationships**:

   - Improve relationship extraction in `graph_extraction` stage
   - Extract implicit relationships (co-occurrence, semantic similarity)
   - Extract hierarchical relationships (parent-child, part-of)

2. **Link isolated entities**:

   - Use entity similarity to connect similar entities
   - Use co-occurrence to create edges
   - Use semantic embeddings to find related entities

3. **Adjust community detection parameters**:
   - Increase `max_cluster_size` to allow larger communities
   - Use different resolution parameters
   - Consider alternative algorithms for sparse graphs

### Solution 3: Handle Isolated Entities Differently 📊

Instead of creating communities for isolated entities:

1. **Create a separate "orphan" collection** for isolated entities
2. **Don't summarize them as communities** (save LLM costs)
3. **Flag them for later enrichment** (link them when more data arrives)

## Expected Behavior After Fix

**Before Fix**:

- 90 communities (all single-entity)
- 90 LLM summarization calls (wasteful)
- Misleading community data

**After Filtering Fix**:

- ~2-5 real communities (multi-entity, connected)
- ~2-5 LLM summarization calls (efficient)
- 36 isolated entities stored separately or ignored

## Next Steps

1. ✅ **Investigation Complete**: We understand the problem
2. 🔧 **Apply Filter Fix**: Filter single-node communities in `_organize_communities_by_level()`
3. 🧪 **Test**: Re-run community detection and verify only multi-entity communities are created
4. 📊 **Analyze Results**: Check if remaining communities have relationships
5. 🎯 **Improve Graph**: Work on increasing relationship extraction to improve connectivity
