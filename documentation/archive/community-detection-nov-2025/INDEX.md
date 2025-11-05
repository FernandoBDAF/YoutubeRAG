# Community Detection Archive - November 2025

**Implementation Period**: November 4, 2025  
**Duration**: ~3 hours  
**Result**: Louvain algorithm integration with 1000× performance improvement  
**Status**: Complete

---

## Purpose

This archive documents the switch from `hierarchical_leiden` to `Louvain` algorithm for community detection, including the massive performance improvement from batch update optimization.

**Use for**: Understanding community detection algorithm selection, debugging community detection issues, learning about performance optimization.

**Current Documentation**:
- Technical: `documentation/technical/COMMUNITY-DETECTION.md`
- Plan: `PLAN-EXPERIMENT-INFRASTRUCTURE.md` (root, active - combined with experiments)

---

## What Was Built

A production-ready Louvain community detection implementation with thread safety and massive performance improvements.

**Key Features**:
- Louvain algorithm implementation (`_detect_louvain` method)
- Algorithm selection (Louvain vs hierarchical_leiden)
- Configurable resolution parameter
- Batch update mechanism (updates all chunks at once)
- Thread-safe execution (detection runs only once)
- Comprehensive logging and metrics

**Metrics/Impact**:
- **Performance**: 1000× faster (17 minutes → 1 second for 12,959 chunks)
- **Algorithm**: Louvain produces more meaningful communities for sparse graphs
- **Thread Safety**: Prevents duplicate detection runs
- **Modularity**: Typical scores 0.3-0.5 (good quality)

---

## Archive Contents

### implementation/ (1 file)

**`LOUVAIN-IMPLEMENTATION-COMPLETE.md`** - Complete implementation details
- Full technical description
- Code changes
- Performance analysis
- Design decisions
- Usage examples

---

## Key Documents

**Most Important**:

1. **`LOUVAIN-IMPLEMENTATION-COMPLETE.md`** - Everything about this implementation
   - Understand the algorithm switch rationale
   - See the massive performance improvement
   - Learn about batch update optimization
   - Understand thread safety considerations

---

## Implementation Timeline

**November 4, 2025**: Started - Identified hierarchical_leiden issues  
**November 4, 2025**: Implemented Louvain algorithm  
**November 4, 2025**: Added batch update optimization  
**November 4, 2025**: Added thread safety  
**November 4, 2025**: Completed and tested

---

## Code Changes

**Files Modified**:
- `business/agents/graphrag/community_detection.py`:
  - Added `algorithm` parameter
  - Implemented `_detect_louvain()` method
  - Renamed existing to `_detect_hierarchical_leiden()`
  - Added algorithm selection logic
  - Updated resolution parameter default

- `business/stages/graphrag/community_detection.py`:
  - Added `_batch_update_all_chunks()` method (MASSIVE performance win)
  - Added thread lock (`self._detection_lock`) for safety
  - Modified `handle_doc()` to use batch update
  - Updated configuration to support algorithm parameter

**Key Innovation**: Batch update mechanism
```python
# Before: Update chunks one by one
for chunk in chunks:
    collection.update_one({"chunk_id": chunk.id}, payload)
# Time: ~17 minutes for 12,959 chunks

# After: Update all chunks at once
collection.update_many(query, payload)
# Time: ~1 second for 12,959 chunks
```

---

## Performance Analysis

**Before** (hierarchical_leiden + individual updates):
- Algorithm: Struggled with sparse graphs
- Update time: ~17 minutes (silent, appeared frozen)
- User experience: Poor (no feedback, seemed stuck)

**After** (Louvain + batch update):
- Algorithm: Better for sparse graphs (modularity 0.3-0.5)
- Update time: ~1 second
- User experience: Excellent (fast, responsive)
- Improvement: **~1000× faster**

---

## Design Decisions

### Why Louvain?

**Problem with hierarchical_leiden**:
- Designed for dense graphs
- Our YouTube knowledge graphs are sparse
- Produced too many small communities
- Low modularity scores

**Why Louvain works**:
- Well-suited for sparse graphs
- Produces hierarchical structure
- Good modularity scores (0.3-0.5)
- Fast and scalable
- Resolution parameter allows granularity control

### Resolution Parameter

**Default**: 1.0 (standard)  
**Range**: 0.5-2.0
- Lower (0.5-0.8): Fewer, larger communities
- Higher (1.5-2.0): More, smaller communities

**Tuning**: See experiment configs in `configs/graphrag/`

---

## Testing

**Tests**: Manual validation with production data  
**Coverage**: Algorithm execution, batch updates, thread safety  
**Status**: Tested with 12,959 chunks, ~2000 entities

**Validation**:
- Communities detected: 50-200 (typical)
- Modularity: 0.3-0.5 (good)
- Performance: Consistent 1-2 seconds

---

## Related Archives

- `experiment-infrastructure-nov-2025/` - Experiment system (uses Louvain configs)
- `concurrency-optimization-nov-2025/` - Batch operations pattern
- `session-summaries-nov-2025/` - Session context

---

## Next Steps (See Active Plan)

**Active Plan**: `PLAN-EXPERIMENT-INFRASTRUCTURE.md` (root)

**Planned Experiments**:
- Resolution parameter sweep (0.5, 0.8, 1.0, 1.2, 1.5, 2.0)
- Min/max cluster size variations
- Compare Louvain vs hierarchical_leiden
- Quality metrics across configurations

---

**Archive Complete**: 1 file preserved  
**Reference from**: `documentation/technical/COMMUNITY-DETECTION.md`  
**Code**: `business/agents/graphrag/community_detection.py`, `business/stages/graphrag/community_detection.py`

