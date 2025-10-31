# GraphRAG Pipeline Test Analysis - 25 Chunks (Single Video)

## Date: October 30, 2025

## Test Configuration

- **Chunks Processed**: 25 (all from video ZA-tUyM_y7s)
- **Pipeline**: Full GraphRAG with comprehensive improvements
- **Max Cluster Size**: 10
- **Min Cluster Size**: 2

## Results Summary

| Metric              | Count |
| ------------------- | ----- |
| **Entities**        | 84    |
| **Relations**       | 3,591 |
| **Entity Mentions** | 141   |
| **Communities**     | 0     |

## Detailed Stage Analysis

### 1. Graph Extraction ✅ SUCCESS

- **Time**: 405.2s (~6.8 minutes)
- **Processed**: 25/25 chunks
- **Updated**: 25/25 chunks
- **Failed**: 0

**LLM Extraction Results** (from logs):

- Average 4-8 entities per chunk
- Average 4-6 relationships per chunk
- Total raw extractions: ~125 relationships

### 2. Entity Resolution ✅ SUCCESS

- **Time**: 17.4s
- **Processed**: 25/25 chunks
- **Updated**: 25/25 chunks
- **Failed**: 0

**Resolution Results**:

- 84 unique resolved entities (good deduplication)
- Average 5-6 entities per chunk

### 3. Graph Construction ✅ SUCCESS

- **Time**: 703.5s (~11.7 minutes)
- **Processed**: 25/25 chunks
- **Updated**: 25/25 chunks
- **Failed**: 0

**LLM-Extracted Relationships**:

- ~115 relationships from LLM extraction

**Post-Processing Results**:

| Step                   | Added     | Skipped   | Time        |
| ---------------------- | --------- | --------- | ----------- |
| 1. Co-occurrence       | 212       | 145       | ~24s        |
| 2. Semantic Similarity | 426       | 311       | ~3 min      |
| 3. Cross-Chunk         | 2,749     | 737       | ~11 min     |
| 4. Bidirectional       | 88        | 3         | ~7s         |
| 5. Link Prediction     | 0         | N/A       | <1s         |
| **Total**              | **3,475** | **1,196** | **~14 min** |

**Key Insight**: Post-processing added **3,475 relationships** vs. ~115 from LLM extraction (30x multiplier!)

### 4. Community Detection ❌ FAILED

- **Time**: 9.4s
- **Processed**: 25/25 chunks
- **Updated**: 0/25 chunks
- **Failed**: 25/25 chunks

**Detection Results**:

- Graph created: **84 nodes, 3,486 edges**
- Graph density: **1.0 (COMPLETE GRAPH!)**
- Communities detected by hierarchical_leiden: 84
- Communities with ≥2 entities: **0**
- All 84 communities had exactly 1 entity each

**Failure Reason**: All communities filtered out by `min_cluster_size=2` post-filtering

## Problem Analysis

### Critical Issue: Graph is TOO Connected

**Graph Statistics**:

- Nodes: 84
- Edges: 3,486
- **Maximum Possible Edges**: 84 × 83 / 2 = **3,486**
- **Actual Edges**: 3,486
- **Graph Density**: 3,486 / 3,486 = **1.0 (100%)**

**This is a COMPLETE GRAPH** - every entity is connected to every other entity!

### Why `hierarchical_leiden` Failed

When a graph is completely connected with uniform edge weights:

1. **No Natural Clusters**: Every node is equally connected to every other node
2. **Algorithm Behavior**: Leiden defaults to putting each node in its own community
3. **No Modularity Gain**: Grouping nodes doesn't improve modularity score
4. **Result**: N communities of size 1 (where N = number of nodes)

### Root Cause: Cross-Chunk Relationships

From the logs (line 2713):

```
Found 1 videos with entity mentions
```

**The Problem**:

- All 25 chunks are from the **same video**
- Cross-chunk post-processing creates relationships between **ALL entity pairs in the same video**
- With 84 entities from 1 video → 84 × 83 / 2 = **3,486 cross-chunk relationships**
- This creates a complete graph!

**Cross-Chunk Added**: 2,749 relationships (line 2768)

- This is the single biggest contributor
- Created too many connections between unrelated entities

### Secondary Issues

1. **Semantic Similarity (426 relationships)**:

   - Threshold 0.85 may be too low
   - Creating relationships between concepts that are only moderately similar
   - e.g., "Input" ≈ "Inputs", "Algorithm" ≈ "Linear Algorithm"

2. **No Edge Weights**:

   - `hierarchical_leiden` is treating all relationships equally
   - High-confidence LLM extractions = same weight as inferred co-occurrence
   - No way to distinguish strong vs. weak connections

3. **Wrong Configuration**:
   - `max_cluster_size=10` is too small for a complete graph
   - Should be closer to 50 (as we updated in config, but not reflected in logs line 2787)

## Implications

### For Single Video (25 chunks):

❌ **Problem**: Cross-chunk creates complete graph  
❌ **Problem**: No meaningful communities can be detected  
❌ **Problem**: Too many low-quality relationships

### For Full Dataset (13k chunks):

⚠️ **CRITICAL**: If you run this on 13k chunks:

- Thousands of entities
- Millions of cross-chunk relationships (if all from same video)
- **Pipeline will take HOURS or DAYS**
- **Database will be MASSIVE**
- **Community detection will still fail**

## Recommendations

### Immediate Fixes (Required Before Full Run)

#### 1. Fix Cross-Chunk Relationship Strategy

**Current Behavior**: Creates relationship between EVERY entity pair in same video

**Proposed Fix**: Be more selective - only connect entities that appear in ADJACENT or NEARBY chunks

```python
def _add_cross_chunk_relationships(self) -> int:
    # CHANGE: Group by (video_id, chunk_sequence) instead of just video_id
    # Only connect entities in chunks that are close together (e.g., within 5 chunks)

    mentions_collection = self.graphrag_collections["entity_mentions"]
    chunks_collection = self.get_collection(COLL_CHUNKS, io="read")

    # Get chunk sequences
    chunk_sequences = {}
    for chunk in chunks_collection.find({"video_id": {"$exists": True}}):
        chunk_id = chunk.get("chunk_id")
        video_id = chunk.get("video_id")
        # Infer sequence from timestamp or use chunk order
        timestamp = chunk.get("timestamp_start", "00:00:00")
        chunk_sequences[chunk_id] = (video_id, timestamp)

    # Group entities by chunk
    chunk_entities = defaultdict(set)
    for mention in mentions_collection.find():
        chunk_id = mention.get("chunk_id")
        entity_id = mention.get("entity_id")
        if chunk_id and entity_id:
            chunk_entities[chunk_id].add(entity_id)

    # Only connect entities in nearby chunks (window of 5 chunks)
    CHUNK_WINDOW = 5
    added_count = 0

    # For each video, sort chunks by sequence
    video_chunks = defaultdict(list)
    for chunk_id, (video_id, timestamp) in chunk_sequences.items():
        if chunk_id in chunk_entities:
            video_chunks[video_id].append((timestamp, chunk_id))

    for video_id, chunks in video_chunks.items():
        # Sort by timestamp
        chunks.sort()

        # Only connect entities in nearby chunks
        for i, (ts1, chunk1) in enumerate(chunks):
            for j in range(i+1, min(i+CHUNK_WINDOW+1, len(chunks))):
                ts2, chunk2 = chunks[j]

                # Connect entities between these two chunks
                entities1 = chunk_entities[chunk1]
                entities2 = chunk_entities[chunk2]

                for entity1_id in entities1:
                    for entity2_id in entities2:
                        if entity1_id != entity2_id:
                            # Check if relationship exists, create if not
                            # ... (rest of logic)
                            added_count += 1

    return added_count
```

**Expected Impact**: Reduce cross-chunk relationships from 2,749 to ~200-500

#### 2. Increase Semantic Similarity Threshold

```bash
export GRAPHRAG_SIMILARITY_THRESHOLD=0.90  # From 0.85 to 0.90
```

**Expected Impact**: Reduce semantic similarity relationships from 426 to ~100-200

#### 3. Use Edge Weights in Community Detection

**Problem**: All relationships treated equally

**Solution**: Modify `CommunityDetectionAgent.detect_communities()` to use edge weights

```python
# In agents/community_detection_agent.py
def _create_networkx_graph(self, entities, relationships):
    G = nx.Graph()

    for entity in entities:
        G.add_node(entity.entity_id, **entity.dict())

    for relationship in relationships:
        # Use confidence as edge weight
        weight = relationship.confidence

        # Downweight auto-generated relationships
        if relationship.get("relationship_type") in ["co_occurrence", "cross_chunk", "semantic_similarity", "predicted"]:
            weight *= 0.3  # 70% penalty for inferred relationships

        G.add_edge(
            relationship.subject_id,
            relationship.object_id,
            weight=weight,
            **relationship
        )

    return G
```

**Expected Impact**: LLM-extracted relationships get higher weights, better clustering

#### 4. Update Community Detection Config

The logs show `max_cluster_size=10` (line 2787), but we updated it to 50 in the config.

**Check**: Verify the config is being read correctly or add explicit parameter passing

### Alternative Strategy: Filter Low-Confidence Relationships

Instead of creating millions of relationships, filter them:

```python
# In finalize() method, before each post-processing step

# Only add relationships if graph density is below threshold
current_density = self._calculate_graph_density()

if current_density < 0.3:  # Only if graph is not too dense
    # Add co-occurrence, semantic similarity, cross-chunk, etc.
else:
    logger.warning(f"Graph density too high ({current_density:.3f}), skipping post-processing")
```

## Recommended Action Plan

### Option A: Fix and Re-test (Recommended)

1. ✅ **Disable cross-chunk** temporarily: `export GRAPHRAG_ENABLE_CROSS_CHUNK=false`
2. ✅ **Increase similarity threshold**: `export GRAPHRAG_SIMILARITY_THRESHOLD=0.90`
3. ✅ **Use edge weights** in community detection
4. ✅ **Re-run** on same 25 chunks
5. ✅ **Verify** we get 10-15 meaningful communities

### Option B: Parameter Tuning Only (Quick Test)

1. ✅ **Drop communities**: `db.communities.drop()`
2. ✅ **Update config**: Set `max_cluster_size=84` to allow one big community
3. ✅ **Add relationship filtering**: Only use high-confidence relationships for community detection
4. ✅ **Re-run** community detection stage only

### Option C: Full Cleanup and Selective Post-Processing (Best for 13k chunks)

1. ✅ **Redesign cross-chunk**: Use chunk proximity instead of video-level
2. ✅ **Add density checks**: Stop post-processing if graph gets too dense
3. ✅ **Add edge weights**: Use relationship confidence and type for weighting
4. ✅ **Clean and re-run**: Full cleanup and fresh run

## Metrics Analysis

### Graph Structure

| Metric     | Value | Status                                                            |
| ---------- | ----- | ----------------------------------------------------------------- |
| Nodes      | 84    | ✅ Good                                                           |
| Edges      | 3,486 | 🔴 **TOO HIGH**                                                   |
| Density    | 1.0   | 🔴 **COMPLETE GRAPH**                                             |
| Avg Degree | 82.9  | 🔴 **TOO HIGH** (every node connected to almost every other node) |

### Relationship Breakdown

| Type                | Count     | % of Total |
| ------------------- | --------- | ---------- |
| LLM Extracted       | ~115      | 3.2%       |
| Co-occurrence       | 212       | 5.9%       |
| Semantic Similarity | 426       | 11.9%      |
| Cross-Chunk         | 2,749     | 76.5%      |
| Bidirectional       | 88        | 2.5%       |
| Predicted           | 0         | 0%         |
| **Total**           | **3,591** | **100%**   |

**Critical Finding**: **76.5% of relationships are cross-chunk** (auto-generated based on same video)

### Community Detection

- Communities detected: 84 (all single-entity)
- Communities after filtering: 0
- **Result**: FAILED

## Conclusion

The comprehensive improvements worked **TOO WELL** for a single-video test case:

✅ **Success**: Post-processing added 3,475 relationships (30x multiplier!)  
❌ **Failure**: Created a complete graph (density = 1.0)  
❌ **Failure**: No meaningful communities can be detected in a complete graph

### Root Cause

**Cross-chunk relationships** created connections between **every entity pair in the same video**, resulting in:

- Complete graph (3,486 edges for 84 nodes)
- No natural clusters
- `hierarchical_leiden` unable to find meaningful communities

### Before Running on 13k Chunks

**MUST FIX**:

1. Redesign cross-chunk to use chunk proximity (not video-level)
2. Add density checks to stop post-processing if graph gets too dense
3. Use edge weights in community detection
4. Test on multiple videos (not just one) to verify cross-video behavior

**Estimated Impact on 13k chunks without fixes**:

- Millions of relationships
- Hours/days of processing time
- Massive database size
- Still 0 communities
