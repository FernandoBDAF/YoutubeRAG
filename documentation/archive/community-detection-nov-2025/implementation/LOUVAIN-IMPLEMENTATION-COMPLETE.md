# Louvain Algorithm Implementation - Complete

**Date**: November 4, 2025  
**Status**: ✅ **IMPLEMENTED - READY FOR TESTING**  
**Reason**: hierarchical_leiden produced single-entity communities on sparse graphs

---

## Problem

**Observed**: hierarchical_leiden consistently produced single-entity communities

**Logs showed**:

```
2025-11-04 15:37:17 - DEBUG - Skipping community with 1 entities (min_cluster_size=2)
2025-11-04 15:37:17 - DEBUG - Skipping community with 1 entities (min_cluster_size=2)
... (hundreds of times)
```

**Root Cause**: hierarchical_leiden not suitable for sparse, diverse GraphRAG entity graphs

---

## Solution - Switch to Louvain Algorithm

### Why Louvain?

As documented in `documentation/technical/COMMUNITY-DETECTION.md`:

✅ **Proven for GraphRAG-like graphs**  
✅ **Handles sparse, diverse entity graphs**  
✅ **Fast and reliable**  
✅ **Produces meaningful communities** (tested: 6 communities with sizes 22, 20, 15, 12, 9, 6)  
✅ **Battle-tested** (millions of nodes)  
✅ **Modularity optimization** (better quality)

---

## Changes Made

### 1. CommunityDetectionAgent (`business/agents/graphrag/community_detection.py`)

**Updated**:

- Default algorithm: `louvain` (was: `hierarchical_leiden`)
- Added `algorithm` parameter to `__init__()`
- Created `_detect_louvain()` method
- Kept `_detect_hierarchical_leiden()` for backward compatibility
- Updated `detect_communities()` to route to appropriate algorithm

**Code**:

```python
class CommunityDetectionAgent:
    def __init__(
        self,
        algorithm: str = "louvain",  # NEW: Algorithm selection
        max_cluster_size: int = 50,  # Increased from 10
        resolution_parameter: float = 1.0,
        ...
    ):
        self.algorithm = algorithm
        ...

    def detect_communities(self, entities, relationships):
        """Detect communities using selected algorithm."""
        if self.algorithm == "louvain":
            communities = self._detect_louvain(G)
        elif self.algorithm == "hierarchical_leiden":
            communities = self._detect_hierarchical_leiden(G)
        ...

    def _detect_louvain(self, G):
        """Run Louvain algorithm with edge weights."""
        communities = nx_community.louvain_communities(
            G,
            resolution=self.resolution_parameter,
            seed=int(os.getenv("GRAPHRAG_RANDOM_SEED", "42")),
            weight='weight',  # Use relationship confidence as weight
        )

        modularity = nx_community.modularity(G, communities, weight='weight')
        logger.info(f"Louvain: {len(communities)} communities (modularity={modularity:.4f})")

        return list(communities)
```

### 2. CommunityDetectionConfig (`core/config/graphrag.py`)

**Added**:

- `algorithm: str = "louvain"` - Algorithm selection
- `GRAPHRAG_COMMUNITY_ALGORITHM` env var (default: "louvain")
- Updated `max_cluster_size` default: 10 → 50 (Louvain produces larger communities)

**Environment Variables**:

```bash
GRAPHRAG_COMMUNITY_ALGORITHM=louvain  # Default: louvain
GRAPHRAG_MAX_CLUSTER_SIZE=50         # Default: 50 (was 10)
GRAPHRAG_RESOLUTION_PARAMETER=1.0    # Default: 1.0 (tune: 0.5-2.0)
GRAPHRAG_RANDOM_SEED=42              # Default: 42 (reproducibility)
```

### 3. CommunityDetectionStage (`business/stages/graphrag/community_detection.py`)

**Updated**:

- Passes `algorithm` parameter to `CommunityDetectionAgent`

---

## Testing

### Quick Test

```bash
# Test with 100 chunks
python -m app.cli.graphrag --stage community_detection \
  --read-db-name validation_db \
  --write-db-name validation_db \
  --max 100
```

### Full Test

```bash
# Test with all chunks
python -m app.cli.graphrag --stage community_detection \
  --read-db-name validation_db \
  --write-db-name validation_db
```

### Expected Results

**Before** (hierarchical_leiden):

- Hundreds of single-entity communities (all skipped)
- No meaningful community summaries
- Total communities: ~2,000+ (all size 1)

**After** (Louvain):

- 6-20 meaningful communities
- Community sizes: 20-100+ entities
- Modularity: 0.3-0.6 (good quality)
- Summaries: Comprehensive and useful

---

## Configuration Options

### Algorithm Selection

```bash
# Use Louvain (default)
GRAPHRAG_COMMUNITY_ALGORITHM=louvain python -m app.cli.graphrag --stage community_detection

# Use hierarchical_leiden (backward compatibility)
GRAPHRAG_COMMUNITY_ALGORITHM=hierarchical_leiden python -m app.cli.graphrag --stage community_detection
```

### Resolution Tuning

```bash
# Lower resolution = fewer, larger communities
GRAPHRAG_RESOLUTION_PARAMETER=0.5 python -m app.cli.graphrag --stage community_detection

# Higher resolution = more, smaller communities
GRAPHRAG_RESOLUTION_PARAMETER=1.5 python -m app.cli.graphrag --stage community_detection
```

### Seed for Reproducibility

```bash
# Set random seed
GRAPHRAG_RANDOM_SEED=42 python -m app.cli.graphrag --stage community_detection
```

---

## Validation

### Check Community Quality

```python
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv('MONGODB_URI'))
db = client['validation_db']

# Check communities
communities = db.communities
total = communities.count_documents({})
print(f"Total communities: {total}")

# Check sizes
sizes = []
for comm in communities.find({}, {'entity_count': 1}):
    sizes.append(comm.get('entity_count', 0))

sizes.sort(reverse=True)
print(f"Community sizes: {sizes[:10]}")
print(f"Largest: {sizes[0]}, Smallest: {sizes[-1]}, Avg: {sum(sizes)/len(sizes):.1f}")
```

---

## Expected Impact

**Community Quality**:

- ✅ Meaningful communities (20-100+ entities)
- ✅ Cross-topic grouping
- ✅ Better for RAG queries

**Summarization**:

- ✅ Comprehensive summaries (many entities to summarize)
- ✅ More context per community
- ✅ Better query results

**Performance**:

- ✅ Fast (Louvain is O(n log n))
- ✅ Scalable (millions of nodes)
- ✅ Concurrent summarization benefits from larger batch sizes

---

## Backward Compatibility

**hierarchical_leiden** still available:

```bash
GRAPHRAG_COMMUNITY_ALGORITHM=hierarchical_leiden python -m app.cli.graphrag --stage community_detection
```

**Fallback**: If graspologic not installed, automatically falls back to Louvain

---

## Next Steps

1. ✅ Implementation complete
2. ⏳ Test with validation_db data
3. ⏳ Validate community quality
4. ⏳ Run full 13k pipeline with Louvain
5. ⏳ Compare results with hierarchical_leiden (if desired)

---

## Files Modified

1. ✅ `business/agents/graphrag/community_detection.py`

   - Added `_detect_louvain()` method
   - Added `_detect_hierarchical_leiden()` method
   - Updated `detect_communities()` to route by algorithm
   - Added algorithm parameter

2. ✅ `business/stages/graphrag/community_detection.py`

   - Passes algorithm parameter to agent

3. ✅ `core/config/graphrag.py`

   - Added `algorithm` field to `CommunityDetectionConfig`
   - Added `GRAPHRAG_COMMUNITY_ALGORITHM` env var
   - Updated defaults (max_cluster_size: 50)

4. ✅ `documentation/technical/GRAPHRAG-OPTIMIZATION.md`
   - Marked algorithm switch as implemented

---

## Summary

✅ **Louvain algorithm implemented as default**  
✅ **hierarchical_leiden kept for backward compatibility**  
✅ **Configuration via env var** (`GRAPHRAG_COMMUNITY_ALGORITHM`)  
✅ **No linter errors**  
✅ **Ready for testing**

**Next**: Run community_detection stage to validate Louvain produces meaningful communities! 🎉

---

**Date**: November 4, 2025, 4:25 PM  
**Status**: ✅ **LOUVAIN IMPLEMENTATION COMPLETE - READY TO TEST**
