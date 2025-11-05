# Graph Construction & Community Detection Validation Plan

**Date**: November 3, 2025  
**Purpose**: Systematic validation of graph_construction finalize() and community_detection  
**Critical Issue**: Community detection needs finalize() post-processing to work

---

## 🔍 The Problem (From Documentation)

### Why finalize() Was Created

**Root Cause**: Sparse graphs lead to single-entity communities

**Evidence** (from GRAPHRAG-COMMUNITY-DIAGNOSIS.md):

- **Graph**: 106 nodes, 61 edges
- **Density**: ~0.011 (very sparse!)
- **Result**: 90 communities, all with 1 entity each
- **Problem**: hierarchical_leiden creates single-node communities for isolated entities

**Solution**: Add 5 types of post-processing relationships to **increase graph connectivity**

**Without finalize()**:

- Only LLM-extracted relationships (~61 for 106 entities)
- Sparse graph
- Many isolated entities
- Community detection fails (all single-node communities)

**With finalize()**:

- LLM relationships + co-occurrence + semantic + cross-chunk + bidirectional + predicted
- Denser graph
- Fewer isolated entities
- Community detection works (real communities with multiple entities)

---

## 🎯 Validation Strategy

### Step 1: Run WITHOUT finalize() (Baseline) ⚠️

**Purpose**: See the problem - sparse graph, single-entity communities

### Step 2: Run WITH finalize() (Full) ✅

**Purpose**: See the solution - denser graph, real communities

### Step 3: Compare Results

**Purpose**: Validate that finalize() improves community detection

---

## 📋 Execution Plan

### Test 1: Simple Graph Construction (WITHOUT finalize post-processing)

**Setup**: Temporarily disable finalize() post-processing

**Command**:

```bash
# Option A: Modify code temporarily
# Comment out the 5 batch operations in finalize()

# Option B: Run with small dataset
python -m app.cli.graphrag --stage graph_construction --max 10

# Then check communities
python -m app.cli.graphrag --stage community_detection --max 10
```

**Expected Results** (BAD - demonstrates the problem):

```
Graph Construction:
- Processes 10 chunks
- Stores only LLM-extracted relationships
- NO post-processing (no batch inserts)
- Sparse graph

Community Detection:
- Detects X communities
- Most communities have 1 entity each ❌
- Low connectivity
- Coherence scores artificially high
```

**Purpose**: Demonstrates why finalize() is needed

---

### Test 2: Full Graph Construction (WITH finalize post-processing) ✅

**Command**:

```bash
python -m app.cli.graphrag --stage graph_construction --max 100
```

**Expected Results** (GOOD):

```
Per-Chunk Processing:
- Processes 100 chunks
- Resolves relationships per chunk
- Stores LLM relationships
- Marks chunks as completed

Finalize Post-Processing:
[1/5] Adding co-occurrence relationships...
  Inserting X co-occurrence relationships in batch
  Co-occurrence batch insert: X/X successful, 0 failed
  ✓ Added X co-occurrence relationships (density: 0.XXXX)

[2/5] Adding semantic similarity relationships...
  Inserting X semantic similarity relationships in batch
  Semantic similarity batch insert: X/X successful, 0 failed
  ✓ Added X semantic similarity relationships (density: 0.XXXX)

[3/5] Adding cross-chunk relationships...
  Inserting X cross-chunk relationships in batch
  Cross-chunk batch insert: X/X successful, 0 failed
  ✓ Added X cross-chunk relationships (density: 0.XXXX)

[4/5] Adding bidirectional relationships...
  Inserting X reverse relationships in batch
  Bidirectional batch insert: X/X successful, 0 failed
  ✓ Added X bidirectional relationships (density: 0.XXXX)

[5/5] Adding predicted link relationships...
  Inserting X predicted relationships in batch
  Link prediction batch insert: X/X successful, 0 failed
  ✓ Added X predicted relationships (density: 0.XXXX)

Graph post-processing complete: added Y total relationships
```

**Validation Criteria**:

- ✅ All 5 batch operations execute
- ✅ All show "0 failed"
- ✅ Graph density increases with each operation
- ✅ May stop early if density reaches max (0.3)

---

### Test 3: Community Detection (AFTER finalize) ✅

**Command**:

```bash
python -m app.cli.graphrag --stage community_detection --max 100
```

**Expected Results** (GOOD):

```
Community Detection:
- Retrieved X entities
- Retrieved Y relationships (including post-processed ones)
- Created graph with X nodes and Y edges
- Density: 0.XXX (much higher than without finalize)
- Detected N communities using hierarchical Leiden
- Communities with entity counts > 1 ✅
- Real community structure detected

Community Summarization:
- Generated summaries for N communities
- Stored in communities collection
```

**Validation Criteria**:

- ✅ Graph density > 0.05 (better connectivity)
- ✅ Most communities have > 1 entity
- ✅ Coherence scores vary (not all 1.0)
- ✅ Communities represent real topic clusters

---

## 🎯 Recommended Execution Order

### Phase 1: Validate with Small Dataset (--max 10)

**Purpose**: Quick validation, easy to debug

```bash
# 1. Run graph_construction (will run finalize)
python -m app.cli.graphrag --stage graph_construction --max 10 \
  --log-file logs/test_graph_construction_10.log

# 2. Check finalize logs
grep "batch insert\|post-processing\|\[1/5\]\|\[2/5\]" logs/test_graph_construction_10.log

# 3. Run community_detection
python -m app.cli.graphrag --stage community_detection --max 10 \
  --log-file logs/test_community_detection_10.log

# 4. Check results
grep "Detected.*communities\|entity_count\|coherence" logs/test_community_detection_10.log
```

**Expected Time**: ~5-10 minutes

---

### Phase 2: Validate with Medium Dataset (--max 100)

**Purpose**: Confirm scalability

```bash
# 1. Run graph_construction
python -m app.cli.graphrag --stage graph_construction --max 100 \
  --log-file logs/test_graph_construction_100.log

# 2. Verify all 5 batch operations
grep "batch insert" logs/test_graph_construction_100.log | grep -E "co-occurrence|semantic|cross-chunk|bidirectional|predicted"

# 3. Run community_detection
python -m app.cli.graphrag --stage community_detection --max 100 \
  --log-file logs/test_community_detection_100.log

# 4. Analyze communities
python -c "
from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()
client = MongoClient(os.getenv('MONGODB_URI'))
db = client[os.getenv('DB_NAME', 'mongo_hack')]

# Count communities
total = db.communities.count_documents({})
single_entity = db.communities.count_documents({'entity_count': 1})
multi_entity = total - single_entity

print(f'Total communities: {total}')
print(f'Single-entity: {single_entity} ({single_entity/total*100:.1f}%)')
print(f'Multi-entity: {multi_entity} ({multi_entity/total*100:.1f}%)')
print(f'✓ Expect multi-entity > 50% if finalize() working')
"
```

**Expected Time**: ~20-30 minutes

---

## 📊 Success Criteria

### Graph Construction

- [ ] All 5 batch operations execute
- [ ] All show "X/X successful, 0 failed"
- [ ] Graph density increases progressively
- [ ] Total relationships added > 0
- [ ] No errors during finalize()

### Community Detection

- [ ] Detects communities successfully
- [ ] > 50% of communities have entity_count > 1
- [ ] Coherence scores vary (not all 1.0 or all 0.0)
- [ ] Communities represent topic clusters
- [ ] Summaries generated successfully

---

## ⚠️ Known Issues to Watch For

### Issue 1: Graph Density Limit

**Symptom**: Post-processing stops early  
**Message**: "Graph density reached maximum (0.3). Skipping remaining post-processing"  
**Status**: Expected behavior (prevents over-connection)

### Issue 2: No Communities Detected

**Symptom**: "No communities detected"  
**Cause**: Graph too sparse even after finalize()  
**Solution**: Check if finalize() actually ran

### Issue 3: All Single-Entity Communities

**Symptom**: All communities have entity_count: 1  
**Cause**: finalize() didn't run or didn't add enough relationships  
**Solution**: Verify batch insert logs

---

## 📝 Validation Checklist

**Before Running**:

- [ ] Entity resolution stage completed (13,031 chunks)
- [ ] Entities collection has data
- [ ] Relations collection exists

**During graph_construction**:

- [ ] Per-chunk relationship resolution works
- [ ] finalize() executes after all chunks
- [ ] All 5 batch operations run
- [ ] Batch inserts successful

**During community_detection**:

- [ ] Retrieves entities and relationships
- [ ] Builds NetworkX graph
- [ ] Detects communities
- [ ] Filters single-entity communities
- [ ] Generates summaries

**After Completion**:

- [ ] Check community entity counts
- [ ] Verify coherence scores
- [ ] Inspect sample communities

---

**Ready to Execute**: Start with --max 10 for quick validation, then scale up ✅
