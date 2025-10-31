# GraphRAG Complete Graph Analysis - 25 Chunks Test

## Date: October 30, 2025

## Database: mongo_hack (MongoDB Atlas)

## Executive Summary

The GraphRAG pipeline successfully processed 25 chunks and created **3,591 relationships** between **84 entities**. However, the graph became a **complete graph** (density = 1.0), where every entity is connected to every other entity. This prevented meaningful community detection.

**Status**: ✅ Pipeline works, ❌ Graph structure needs optimization

---

## Test Data

- **Chunks**: 25 (all from same video: ZA-tUyM_y7s)
- **Entities**: 84
- **Relations**: 3,591
- **Entity Mentions**: 141
- **Communities**: 0 (all filtered out as single-entity)

---

## Graph Structure Metrics

### Complete Graph Confirmation

| Metric                   | Value               | Analysis                                        |
| ------------------------ | ------------------- | ----------------------------------------------- |
| **Nodes**                | 84                  | ✅ Good entity count                            |
| **Edges**                | 3,486               | 🔴 **MAXIMUM POSSIBLE** (complete graph)        |
| **Max Possible**         | 84 × 83 / 2 = 3,486 | 🔴 **100% connectivity**                        |
| **Graph Density**        | 1.000               | 🔴 **Complete graph**                           |
| **Avg Degree**           | 83.0                | 🔴 **Every node connected to all others**       |
| **Diameter**             | 1                   | 🔴 **All nodes 1 hop apart**                    |
| **Clustering Coeff**     | 1.000               | 🔴 **Perfect clustering (all triangles exist)** |
| **Isolated Nodes**       | 0                   | ✅ No isolation                                 |
| **Connected Components** | 1                   | ✅ Single component                             |

**Conclusion**: This is a **mathematically complete graph** - literally every entity pair is connected.

---

## Relationship Analysis

### Relationship Type Distribution

| Type                    | Count     | % of Total | Source                       | Quality             |
| ----------------------- | --------- | ---------- | ---------------------------- | ------------------- |
| **cross_chunk**         | 2,749     | **76.6%**  | Auto-generated (same video)  | 🔴 **Problem**      |
| **semantic_similarity** | 426       | 11.9%      | Embedding similarity (≥0.85) | ⚠️ **Too many**     |
| **co_occurrence**       | 212       | 5.9%       | Same chunk entities          | ✅ **Good**         |
| **llm_extracted**       | 116       | 3.2%       | LLM entity extraction        | ✅ **High quality** |
| **bidirectional**       | 88        | 2.5%       | Reverse of LLM relationships | ✅ **Good**         |
| **Total**               | **3,591** | **100%**   |                              |                     |

**Critical Finding**: **76.6% of relationships are cross-chunk**, creating the complete graph.

### Top Relationship Predicates

| Predicate                 | Count | Primary Source                   |
| ------------------------- | ----- | -------------------------------- |
| `related_to`              | 1,079 | Cross-chunk (CONCEPT↔CONCEPT)    |
| `mentioned_together`      | 949   | Cross-chunk (generic fallback)   |
| `semantically_similar_to` | 426   | Semantic similarity              |
| `discusses`               | 384   | Cross-chunk (PERSON↔CONCEPT)     |
| `implemented_in`          | 283   | Cross-chunk (CONCEPT↔TECHNOLOGY) |
| `co_occurs_with`          | 212   | Co-occurrence                    |
| `uses`                    | 46    | LLM extracted                    |
| `used_by`                 | 46    | Bidirectional                    |

---

## Entity Quality Analysis

### Sample Entities (High Quality) ✅

**1. Jason Ku (PERSON)**

- Confidence: 0.950
- Source Count: 12 (mentioned in 12 chunks)
- Description: "An instructor or speaker discussing concepts related to proofs and algorithms..."
- Has Embedding: Yes (1024 dims)

**2. Introduction To Algorithms (CONCEPT)**

- Confidence: 0.900
- Source Count: 1
- Description: "A course focused on teaching algorithms, problem-solving, and communication..."
- Has Embedding: Yes (1024 dims)

**Entity Type Distribution**:

- CONCEPT: 56 (66.7%)
- OTHER: 12 (14.3%)
- PERSON: 8 (9.5%)
- TECHNOLOGY: 6 (7.1%)
- ORGANIZATION: 2 (2.4%)

**Assessment**: ✅ Entity extraction quality is **excellent**

---

## Relationship Quality Analysis

### LLM-Extracted Relationships (High Quality) ✅

**Top 10 by Confidence**:

1. **[teaches]** Jason Ku → Introduction To Algorithms (0.950)
2. **[teaches]** Eric Demaine → Introduction To Algorithms (0.950)
3. **[taught_by]** Introduction To Algorithms → Jason Ku (0.950)
4. **[produces]** Algorithm → Output (0.900)
5. **[takes]** Algorithm → Input (0.900)
6. **[defined_by]** Computational Problem → Predicate (0.900)
7. **[represents]** Binary Relation → Bipartite Graph (0.900)

**Assessment**: ✅ LLM-extracted relationships are **semantically meaningful and accurate**

### Co-Occurrence Relationships (Good Quality) ✅

**Example**: Eric Demaine ↔ Justin Solomon (co-occurs in chunk)

- Confidence: 0.700
- Meaningful: Yes (both are instructors mentioned together)

**Assessment**: ✅ Co-occurrence makes sense for entities in same chunk

### Semantic Similarity Relationships (Mixed Quality) ⚠️

**Good Example**: Inputs ↔ Input (similarity: 0.975)

- These are clearly duplicates/variants that should be linked

**Concern**: 426 similarity relationships for 84 entities is **very high**

- This means ~10% of all entity pairs are "semantically similar"
- At threshold 0.85, we're catching moderate similarities

**Assessment**: ⚠️ Too permissive - should increase threshold to 0.90-0.92

### Cross-Chunk Relationships (Major Problem) 🔴

**Examples**:

1. **[discusses]** Quadratic → Computer Scientist

   - Predicate: Type-inferred (CONCEPT → PERSON = "discusses")
   - Meaningfulness: ❌ **Questionable** (Quadratic concept doesn't "discuss" a person)

2. **[related_to]** Quadratic → Input

   - Predicate: Generic fallback
   - Meaningfulness: ⚠️ **Vague** (could be true, but no evidence)

3. **[implemented_in]** Quadratic → CPU

   - Predicate: Type-inferred (CONCEPT → TECHNOLOGY)
   - Meaningfulness: ❌ **Doesn't make sense**

4. **[mentioned_together]** Quadratic → K Plus 1Th Student
   - Predicate: Generic fallback
   - Meaningfulness: ❌ **Unlikely to be meaningful**

**Problem**: Cross-chunk created **2,749 relationships** between ALL entity pairs in the same video, regardless of actual semantic relationship.

**Assessment**: 🔴 **Cross-chunk is creating too many low-quality relationships**

---

## Why Community Detection Failed

### The Complete Graph Problem

When `hierarchical_leiden` ran:

```
Created graph with 84 nodes and 3486 edges
Detected 84 communities using hierarchical Leiden
Skipping community with 1 entities (min_cluster_size=2) [×84 times]
No communities detected
```

**Why it failed**:

1. **No Natural Clusters**: In a complete graph, every node is equally connected to every other node
2. **No Modularity**: Grouping nodes doesn't improve modularity score
3. **Algorithm Defaults**: Leiden puts each node in its own community (N communities of size 1)
4. **Post-Filtering**: All single-entity communities filtered out by `min_cluster_size=2`

**Result**: 0 communities

---

## Root Cause Analysis

### Problem 1: Cross-Chunk Strategy (76.6% of relationships)

**Current Behavior**:

```python
# Groups ALL entities by video_id
for video_id, entity_ids in video_entities.items():
    # Creates relationship between EVERY entity pair in video
    for entity1_id, entity2_id in all_pairs(entity_ids):
        create_relationship(entity1_id, entity2_id, inferred_predicate)
```

**Impact**:

- 84 entities from 1 video
- 84 × 83 / 2 = 3,486 possible pairs
- Created 2,749 cross-chunk relationships (79% of maximum)
- Remaining 737 were skipped because they already existed from other post-processing steps

**Why This is Wrong**:

- Entities in chunk 1 (00:00-01:00) are NOT related to entities in chunk 25 (24:00-25:00)
- Same video ≠ semantically related
- Creates noise, not signal

### Problem 2: Semantic Similarity Threshold (11.9% of relationships)

**Current**: threshold = 0.85

**Impact**: 426 / 3,486 possible pairs = **12.2%** of entity pairs are "similar"

**Analysis**:

- Some are good: "Inputs" ↔ "Input" (0.975 similarity)
- But 426 is still very high for 84 entities
- At 0.85, we're catching moderately similar concepts that may not need explicit links

**Recommendation**: Increase to 0.90-0.92

---

## Impact on 13k Chunks

If you run this on 13k chunks without fixes:

### Estimated Scale

Assuming:

- ~50 entities per video (estimate based on 84 entities / 25 chunks × chunking rate)
- ~100 videos in the dataset
- Cross-chunk creates relationships between all entities in same video

**Worst Case (all chunks from same video)**:

- Entities: ~5,000
- Max possible edges: 5,000 × 4,999 / 2 = **12.5 million**
- Cross-chunk relationships: **~10 million**
- Processing time: **Days**
- Database size: **Gigabytes**

**Best Case (chunks distributed across videos)**:

- Entities: ~5,000
- Cross-chunk per video: 50 × 49 / 2 = 1,225 per video
- Total cross-chunk: 1,225 × 100 = **122,500**
- Processing time: **Hours**
- Still results in very dense graph

---

## Key Findings

### ✅ What's Working Well

1. **LLM Entity Extraction**: High-quality entities with good descriptions
2. **Entity Resolution**: Good deduplication (141 mentions → 84 unique entities)
3. **LLM Relationship Extraction**: Semantically meaningful, high-confidence relationships
4. **Co-occurrence**: Makes sense for entities in same chunk
5. **Bidirectional**: Proper reverse relationships created
6. **Pipeline Performance**: Stages run efficiently, good logging

### ❌ What's Not Working

1. **Cross-Chunk Relationships**: Creates complete graph by connecting ALL entities in same video
2. **Community Detection**: Can't find clusters in a complete graph
3. **Relationship Quality**: 76.6% of relationships are low-confidence, auto-generated
4. **Scalability**: Will not scale to 13k chunks without fixes

---

## Recommendations

### Critical Fixes (Required Before Scaling)

#### 1. Redesign Cross-Chunk Relationships

**Current**: Video-level (all entities in same video)  
**Proposed**: Chunk-proximity (only nearby chunks)

**Strategy**: Only connect entities in chunks within a small window (e.g., 5 chunks)

**Expected Impact**:

- Reduce cross-chunk from 2,749 to ~200-500
- Create local connectivity, not global
- Preserve temporal relationships
- Allow meaningful communities to form

#### 2. Increase Semantic Similarity Threshold

**Current**: 0.85  
**Proposed**: 0.90-0.92

**Expected Impact**:

- Reduce from 426 to ~100-150 relationships
- Keep only highly similar entities (true duplicates/variants)
- Reduce noise

#### 3. Add Edge Weights to Community Detection

**Problem**: All relationships treated equally

**Solution**: Weight by confidence and type:

- LLM-extracted: weight = confidence (0.8-0.95)
- Co-occurrence: weight = 0.7
- Semantic similarity: weight = similarity score
- Cross-chunk: weight = 0.3 (70% penalty)
- Bidirectional: weight = original relationship weight

**Expected Impact**:

- Leiden algorithm can distinguish strong vs weak connections
- Meaningful communities based on high-confidence relationships
- Low-quality auto-generated relationships don't dominate clustering

#### 4. Add Density Safeguards

**Strategy**: Stop post-processing if graph gets too dense

```python
def finalize(self):
    # ... co-occurrence ...

    # Check density before continuing
    current_density = self._calculate_density()
    if current_density > 0.3:
        logger.warning(f"Graph density too high ({current_density:.3f}), skipping remaining post-processing")
        return

    # ... semantic similarity, cross-chunk, etc ...
```

**Expected Impact**: Prevent runaway relationship creation

---

## Action Plan

### Phase 1: Quick Validation (Immediate)

**Disable problematic post-processing**, re-run community detection only:

```bash
# 1. Drop communities
python -c "from pymongo import MongoClient; import os; from dotenv import load_dotenv; load_dotenv(); c = MongoClient(os.getenv('MONGODB_URI')); db = c[os.getenv('DB_NAME', 'mongo_hack')]; db.communities.drop(); db.video_chunks.update_many({}, {'\$unset': {'graphrag_communities': 1}}); print('Communities cleared')"

# 2. Temporarily remove cross-chunk and semantic similarity relationships
python -c "from pymongo import MongoClient; import os; from dotenv import load_dotenv; load_dotenv(); c = MongoClient(os.getenv('MONGODB_URI')); db = c[os.getenv('DB_NAME', 'mongo_hack')]; result = db.relations.delete_many({'relationship_type': {'\$in': ['cross_chunk', 'semantic_similarity']}}); print(f'Deleted {result.deleted_count} relationships')"

# 3. Check remaining relationships
python -c "from pymongo import MongoClient; import os; from dotenv import load_dotenv; load_dotenv(); c = MongoClient(os.getenv('MONGODB_URI')); db = c[os.getenv('DB_NAME', 'mongo_hack')]; print(f'Relations: {db.relations.count_documents({})}')"

# 4. Re-run graph structure analysis
python scripts/analyze_graph_structure.py

# 5. If graph looks good, re-run community detection stage only
```

**Expected Results**:

- Relationships: ~340 (116 LLM + 212 co-occurrence + 88 bidirectional + some duplicates removed)
- Graph density: ~0.05-0.10 (much more reasonable)
- Communities: Should detect 5-15 meaningful communities

### Phase 2: Full Fix (Before 13k Chunk Run)

Implement the fixes detailed in `GRAPHRAG-COMPREHENSIVE-IMPROVEMENTS-PLAN.md`:

1. **Redesign cross-chunk** - Use chunk proximity (window of 5 chunks)
2. **Increase similarity threshold** - 0.85 → 0.92
3. **Add edge weights** - Weight by confidence and type
4. **Add density safeguards** - Stop if density > 0.3
5. **Test on 100 chunks** - Verify improvements before full scale

---

## Sample Data Quality

### High-Quality LLM Relationships ✅

```
[teaches] Jason Ku → Introduction To Algorithms (conf: 0.950)
[produces] Algorithm → Output (conf: 0.900)
[uses] Algorithm → Recursion (conf: 0.850)
[defined_by] Computational Problem → Predicate (conf: 0.900)
```

**Assessment**: These are accurate, semantically meaningful relationships

### Good Co-Occurrence ✅

```
[co_occurs_with] Eric Demaine ↔ Justin Solomon (conf: 0.700)
```

**Assessment**: Makes sense - both instructors mentioned in same context

### Good Semantic Similarity ✅

```
[semantically_similar_to] Inputs ↔ Input (similarity: 0.975)
```

**Assessment**: Correctly identifies near-duplicate entities

### Problematic Cross-Chunk 🔴

```
[discusses] Quadratic → Computer Scientist (conf: 0.600)
[implemented_in] Quadratic → CPU (conf: 0.600)
[mentioned_together] Quadratic → K Plus 1Th Student (conf: 0.600)
```

**Assessment**: These don't make semantic sense - they're just entities from the same video

---

## Conclusion

### What We Learned

1. ✅ **Pipeline Works**: All stages execute successfully with good logging
2. ✅ **LLM Quality**: Entity and relationship extraction is high quality
3. ✅ **Post-Processing Works**: All 5 post-processing steps executed
4. ❌ **Cross-Chunk Broken**: Video-level strategy creates complete graph
5. ❌ **Can't Scale**: Will not work on 13k chunks without fixes

### Immediate Next Steps

**Option A: Quick Validation** (Recommended)

1. Remove cross-chunk + semantic similarity relationships
2. Re-run graph analysis
3. Verify communities are detected
4. Confirms that without over-connection, system works

**Option B: Full Fix First**

1. Implement all 4 critical fixes
2. Full cleanup and re-run on 25 chunks
3. Takes longer but gets to production-ready state

### Before Running on 13k Chunks

**MUST DO**:

- ✅ Fix cross-chunk to use chunk proximity
- ✅ Increase semantic similarity threshold
- ✅ Add edge weights to community detection
- ✅ Test on 100 chunks from multiple videos
- ✅ Verify graph density < 0.3
- ✅ Verify 10-15 meaningful communities detected

---

## Summary Statistics

| Metric        | Current        | Target     | Fix Needed            |
| ------------- | -------------- | ---------- | --------------------- |
| Relationships | 3,591          | 300-500    | Reduce cross-chunk    |
| Graph Density | 1.000          | 0.05-0.20  | Fix cross-chunk       |
| LLM Quality   | Excellent      | -          | ✅ Keep               |
| Co-occurrence | Good           | -          | ✅ Keep               |
| Semantic Sim  | Too many       | Reduce     | Increase threshold    |
| Cross-Chunk   | Complete graph | Local only | Redesign              |
| Communities   | 0              | 10-15      | Fix after graph fixed |

The system has **excellent foundation** (entity extraction, LLM relationships), but needs **cross-chunk redesign** before scaling.
