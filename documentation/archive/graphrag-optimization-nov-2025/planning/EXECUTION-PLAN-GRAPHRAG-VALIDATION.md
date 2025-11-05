# GraphRAG Validation Execution Plan

**Date**: November 3, 2025  
**Purpose**: Step-by-step commands to validate graph_construction and community_detection  
**Status**: Ready to execute

---

## ✅ Prerequisites

**Already Complete**:

- ✅ Entity resolution stage completed (13,031 chunks processed)
- ✅ Entities collection populated
- ✅ Entity mentions collection populated
- ✅ 113 tests passing

**Verify Prerequisites**:

```bash
python -c "
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv('MONGODB_URI'))
db = client[os.getenv('DB_NAME', 'mongo_hack')]

chunks_resolved = db.video_chunks.count_documents({'graphrag_resolution.status': 'completed'})
entities_count = db.entities.count_documents({})
mentions_count = db.entity_mentions.count_documents({})

print(f'✓ Resolved chunks: {chunks_resolved:,}')
print(f'✓ Entities: {entities_count:,}')
print(f'✓ Entity mentions: {mentions_count:,}')
print('')
print('Prerequisites met ✅' if chunks_resolved > 0 else 'ERROR: No resolved chunks')
"
```

**Expected Output**:

```
✓ Resolved chunks: 13,031
✓ Entities: ~20,000-30,000
✓ Entity mentions: ~60,000-80,000

Prerequisites met ✅
```

---

## 📋 Phase 1: Graph Construction Validation

### Step 1.1: Run Graph Construction Stage

**Command**:

```bash
python -m app.cli.graphrag --stage graph_construction --max 1000 \
  --log-file logs/test_graph_construction.log \
  --verbose
```

**What This Does**:

1. Processes first 1,000 chunks with completed entity resolution
2. Resolves relationships per chunk (using relationship_resolution agent)
3. Stores relationships in relations collection
4. **CRITICAL**: Runs `finalize()` which executes 5 batch operations
5. Creates log file for analysis

**Expected Duration**: 20-40 minutes (depends on # of relationships)

---

### Step 1.2: Monitor Progress (Optional)

**While running**, in another terminal:

```bash
# Watch progress
tail -f logs/test_graph_construction.log | grep -E "Progress:|batch insert|Adding"

# See current stats
tail -100 logs/test_graph_construction.log
```

---

### Step 1.3: Validate Batch Operations

**After completion**, check logs:

```bash
# Check all 5 batch operations ran
grep "batch insert" logs/test_graph_construction.log | grep -E "co-occurrence|semantic|cross-chunk|Bidirectional|Link prediction"
```

**Expected Output**:

```
Co-occurrence batch insert: X/X successful, 0 failed
Semantic similarity batch insert: X/X successful, 0 failed
Cross-chunk batch insert: X/X successful, 0 failed
Bidirectional batch insert: X/X successful, 0 failed
Link prediction batch insert: X/X successful, 0 failed
```

**Success Criteria**:

- ✅ All 5 operations show batch insert logs
- ✅ All show "0 failed"
- ✅ Counts > 0 for each type

---

### Step 1.4: Check Graph Statistics

```bash
python -c "
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv('MONGODB_URI'))
db = client[os.getenv('DB_NAME', 'mongo_hack')]

# Get relationship counts by type
pipeline = [
    {'\$group': {
        '_id': '\$relationship_type',
        'count': {'\$sum': 1}
    }},
    {'\$sort': {'count': -1}}
]

results = list(db.relations.aggregate(pipeline))

print('Relationship Counts by Type:')
print('-' * 50)
for result in results:
    rel_type = result['_id'] or 'llm_extracted'
    count = result['count']
    print(f'  {rel_type:30} {count:,}')

total = db.relations.count_documents({})
print('-' * 50)
print(f'  TOTAL:                         {total:,}')
print('')

# Calculate graph density
entities = db.entities.count_documents({})
if entities > 1:
    max_possible = entities * (entities - 1) / 2
    density = total / max_possible
    print(f'Graph Density: {density:.4f}')
    print(f'  Entities: {entities:,}')
    print(f'  Relationships: {total:,}')
    print(f'  Max possible: {max_possible:,.0f}')
"
```

**Expected Output**:

```
Relationship Counts by Type:
--------------------------------------------------
  llm_extracted                  ~100,000
  co_occurrence                  ~50,000
  cross_chunk                    ~30,000
  bidirectional                  ~20,000
  semantic_similarity            ~5,000
  predicted                      ~3,000
--------------------------------------------------
  TOTAL:                         ~208,000

Graph Density: 0.XXXX
  Entities: ~20,000
  Relationships: ~208,000
  Max possible: ~200,000,000
```

**Success Criteria**:

- ✅ Multiple relationship types present
- ✅ Auto-generated types (co_occurrence, etc.) exist
- ✅ Total relationships >> entities (good connectivity)

---

## 📋 Phase 2: Community Detection Validation

### Step 2.1: Run Community Detection Stage

**Command**:

```bash
python -m app.cli.graphrag --stage community_detection --max 1000 \
  --log-file logs/test_community_detection.log \
  --verbose
```

**What This Does**:

1. Detects communities haven't been run yet
2. Loads ALL entities and relationships from database
3. Builds NetworkX graph
4. Runs hierarchical_leiden algorithm
5. **Filters single-entity communities** (min_cluster_size=2)
6. Generates LLM summaries for each community
7. Stores in communities collection

**Expected Duration**: 10-20 minutes

**IMPORTANT**: Community detection runs ONCE for entire graph, not per-chunk!

---

### Step 2.2: Check Community Detection Logs

```bash
# Check if communities were detected
grep -E "Detected.*communities|Retrieved.*entities|Retrieved.*relationships" logs/test_community_detection.log

# Check for filtering
grep "Skipping community with 1 entities" logs/test_community_detection.log | wc -l

# Check summaries
grep "Generated.*summaries|Stored.*communities" logs/test_community_detection.log
```

**Expected Output**:

```
Retrieved X entities
Retrieved Y relationships
Created graph with X nodes and Y edges
Detected N communities using hierarchical Leiden
Skipping community with 1 entities (min_cluster_size=2)  # Many of these
... (filtering single-entity communities)
Generated summaries for M communities  # M < N (after filtering)
Stored M communities
```

---

### Step 2.3: Analyze Community Results

```bash
python -c "
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv('MONGODB_URI'))
db = client[os.getenv('DB_NAME', 'mongo_hack')]

# Get community statistics
total = db.communities.count_documents({})

# Count by entity size
single_entity = db.communities.count_documents({'entity_count': 1})
small_communities = db.communities.count_documents({'entity_count': {'$gte': 2, '$lte': 5}})
medium_communities = db.communities.count_documents({'entity_count': {'$gte': 6, '$lte': 10}})
large_communities = db.communities.count_documents({'entity_count': {'$gt': 10}})

print('Community Analysis:')
print('=' * 60)
print(f'Total communities: {total}')
print(f'  Single-entity (1):           {single_entity:4} ({single_entity/total*100 if total else 0:5.1f}%)')
print(f'  Small (2-5 entities):        {small_communities:4} ({small_communities/total*100 if total else 0:5.1f}%)')
print(f'  Medium (6-10 entities):      {medium_communities:4} ({medium_communities/total*100 if total else 0:5.1f}%)')
print(f'  Large (>10 entities):        {large_communities:4} ({large_communities/total*100 if total else 0:5.1f}%)')
print('')

# Show sample communities
print('Sample Communities:')
print('-' * 60)
for community in db.communities.find().limit(5):
    print(f\"  {community['title'][:50]:50} (entities: {community['entity_count']:2})\")

print('')

# Success criteria
multi_entity_pct = (total - single_entity) / total * 100 if total > 0 else 0
if multi_entity_pct > 50:
    print(f'✅ SUCCESS: {multi_entity_pct:.1f}% communities are multi-entity')
else:
    print(f'⚠️  WARNING: Only {multi_entity_pct:.1f}% communities are multi-entity')
    print('   This may indicate finalize() did not run or graph is still too sparse')
"
```

**Expected Output (SUCCESS)**:

```
Community Analysis:
============================================================
Total communities: 50
  Single-entity (1):              0 (  0.0%)
  Small (2-5 entities):          30 ( 60.0%)
  Medium (6-10 entities):        15 ( 30.0%)
  Large (>10 entities):           5 ( 10.0%)

Sample Communities:
------------------------------------------------------------
  Python Programming Ecosystem                   (entities: 12)
  Machine Learning Concepts                      (entities:  8)
  Web Development Technologies                   (entities:  6)
  ...

✅ SUCCESS: 100.0% communities are multi-entity
```

**Expected Output (PROBLEM)**:

```
Community Analysis:
============================================================
Total communities: 90
  Single-entity (1):             90 (100.0%)
  Small (2-5 entities):           0 (  0.0%)
  ...

⚠️  WARNING: Only 0.0% communities are multi-entity
   This may indicate finalize() did not run or graph is still too sparse
```

---

## 🎯 Success Criteria Summary

### Graph Construction ✅

- [ ] Processes X chunks successfully
- [ ] **finalize() executes** after all chunks
- [ ] **All 5 batch operations run**:
  - [ ] Co-occurrence: X/X successful
  - [ ] Semantic similarity: X/X successful
  - [ ] Cross-chunk: X/X successful
  - [ ] Bidirectional: X/X successful
  - [ ] Link prediction: X/X successful
- [ ] Graph density increases
- [ ] Total relationships > 100,000

### Community Detection ✅

- [ ] Detects > 0 communities
- [ ] **> 50% are multi-entity** (not single)
- [ ] Coherence scores vary (not all 1.0)
- [ ] Summaries generated
- [ ] Communities represent real topic clusters

---

## 📝 Quick Start Commands

### Minimal Test (Fast - 5 minutes)

```bash
# Test with 10 chunks
python -m app.cli.graphrag --stage graph_construction --max 10
python -m app.cli.graphrag --stage community_detection --max 10

# Check results
python -c "from pymongo import MongoClient; import os; from dotenv import load_dotenv; load_dotenv(); client = MongoClient(os.getenv('MONGODB_URI')); db = client[os.getenv('DB_NAME', 'mongo_hack')]; print(f'Communities: {db.communities.count_documents({})}'); print(f'Multi-entity: {db.communities.count_documents({\"entity_count\": {\"$gt\": 1}})}')"
```

### Full Test (Recommended - 30-40 minutes)

```bash
# Test with 1000 chunks
python -m app.cli.graphrag --stage graph_construction --max 1000 --log-file logs/test_graph_const.log
python -m app.cli.graphrag --stage community_detection --max 1000 --log-file logs/test_community.log

# Analyze results (use scripts above)
```

---

## 📊 Troubleshooting

### If finalize() doesn't run:

- Check: Did graph_construction stage complete?
- Check: Any errors in logs?
- Look for: "[1/5] Adding co-occurrence..." in logs

### If all communities are single-entity:

- Check: Did finalize() actually run? (search logs for "batch insert")
- Check: Were relationships added? (count by type)
- Check: Is graph still too sparse? (calculate density)

### If community_detection fails:

- Check: Do entities and relationships exist?
- Check: Is NetworkX graph created successfully?
- Check: Any errors in hierarchical_leiden call?

---

**Ready to Execute**: Start with minimal test (--max 10), then scale up to full test ✅  
**Total Time**: ~5 minutes (minimal) or ~40 minutes (full)  
**All tests created**: 113 tests passing ✅
