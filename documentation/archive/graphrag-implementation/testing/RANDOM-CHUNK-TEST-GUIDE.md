# Random Chunk Test Guide

## Why Random Chunks?

Testing with **consecutive chunks from one video** creates a transitive connection problem where all entities become one connected component, making community detection impossible.

**Random chunks from different videos** provides:

- ✅ Multiple disconnected components (different topics)
- ✅ Realistic cross-video behavior
- ✅ True community structure
- ✅ Accurate density metrics

---

## Your Dataset

- **Total chunks**: 13,069
- **Total videos**: 638
- **Average**: ~20 chunks/video
- **Perfect for GraphRAG!** ✅

---

## How to Run Random Chunk Test

### Step 1: Select and Prepare Random Chunks

```bash
python scripts/run_random_chunk_test.py
```

This will:

1. Select 12 random chunks from 12 DIFFERENT videos
2. Clear all GraphRAG collections
3. Clear GraphRAG metadata from all chunks
4. Mark ONLY the 12 selected chunks for processing (sets `_test_exclude` flag on others)

### Step 2: Run GraphRAG Pipeline

```bash
python run_graphrag_pipeline.py --max 12 --log-file logs/pipeline/graphrag_random_test.log --verbose
```

The pipeline will automatically **only process the 12 selected chunks** (skips chunks with `_test_exclude` flag).

### Step 3: Analyze Results

```bash
# Check adaptive windows used
grep "using adaptive window" logs/pipeline/graphrag_random_test.log

# Check density progression
grep "density:" logs/pipeline/graphrag_random_test.log

# Analyze graph structure
python scripts/analyze_graph_structure.py

# Test community detection
python scripts/test_community_detection.py
```

### Step 4: Clean Up Test Markers

```bash
python -c "from pymongo import MongoClient; import os; from dotenv import load_dotenv; load_dotenv(); c = MongoClient(os.getenv('MONGODB_URI')); db = c[os.getenv('DB_NAME', 'mongo_hack')]; result = db.video_chunks.update_many({}, {'\$unset': {'_test_exclude': 1}}); print(f'Removed test markers from {result.modified_count} chunks')"
```

---

## Expected Results (12 Chunks from 12 Videos)

### Graph Structure

| Metric                  | Expected      | Reasoning                    |
| ----------------------- | ------------- | ---------------------------- |
| Entities                | 40-80         | ~3-7 entities per video      |
| Relationships           | 150-300       | Mixed sources                |
| Graph Density           | **0.05-0.15** | Low (unrelated videos)       |
| Disconnected Components | **4-12**      | Videos with different topics |
| Communities             | **12-60**     | 1-5 per video or topic-based |

### Relationship Breakdown

| Type                | Expected | %                             |
| ------------------- | -------- | ----------------------------- |
| LLM Extracted       | 50-100   | ~30%                          |
| Co-occurrence       | 60-120   | ~35%                          |
| Semantic Similarity | 20-40    | ~10%                          |
| Cross-Chunk         | 20-60    | ~15% (only within same video) |
| Bidirectional       | 20-40    | ~10%                          |

### Key Differences from Single-Video Test

| Metric                  | Single Video (12 chunks) | Random (12 videos) |
| ----------------------- | ------------------------ | ------------------ |
| Disconnected Components | 1                        | **4-12**           |
| Density                 | 0.50+                    | **0.05-0.15**      |
| Communities             | 0                        | **12-60**          |
| Cross-Chunk Impact      | Massive                  | Minimal            |

---

## What This Proves

### If Random Test Succeeds:

✅ **Communities Detected**: System works with diverse data  
✅ **Low Density**: Cross-chunk doesn't over-connect  
✅ **Adaptive Window Works**: Different windows for different videos  
✅ **Ready for 13k**: Can confidently run overnight

### If Random Test Still Fails:

Need to investigate community detection algorithm parameters (not a cross-chunk issue anymore).

---

## For Tonight's 13k Run

**After random test succeeds**, for the full 13k run:

```bash
# Make sure to clean up test markers first!
python -c "from pymongo import MongoClient; import os; from dotenv import load_dotenv; load_dotenv(); c = MongoClient(os.getenv('MONGODB_URI')); db = c[os.getenv('DB_NAME', 'mongo_hack')]; db.video_chunks.update_many({}, {'\$unset': {'_test_exclude': 1}})"

# Then full cleanup
python scripts/full_cleanup.py

# Run full dataset
python run_graphrag_pipeline.py --log-file logs/pipeline/graphrag_full.log --verbose
```

With 638 videos, you'll get:

- Entities: 3,000-5,000
- Communities: 100-500
- Density: 0.10-0.20
- Processing: 2-4 hours

---

## Summary

✅ **Implementation Complete**:

- All GraphRAG stages skip `_test_exclude` chunks
- `run_random_chunk_test.py` handles selection and marking
- Adaptive window adjusts per video
- Edge weights prioritize quality relationships

✅ **Ready to Test**:

```bash
python scripts/run_random_chunk_test.py
python run_graphrag_pipeline.py --max 12 --log-file logs/pipeline/graphrag_random_test.log --verbose
```

This should finally show meaningful communities! 🎯
