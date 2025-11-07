# Testing Scripts

Scripts for testing GraphRAG pipeline components with sample data.

## Scripts

### run_random_chunk_test.py

Setup script for random chunk testing. Selects random chunks from different videos, cleans GraphRAG data, and prepares for pipeline run.

**Usage**:
```bash
python scripts/testing/run_random_chunk_test.py
```

**Configuration**:
- NUM_CHUNKS: Number of chunks to test (default: 12)
- SEED: Random seed for reproducibility

---

### test_random_chunks.py

Comprehensive test script for running GraphRAG pipeline on random chunks.

**Usage**:
```bash
python scripts/testing/test_random_chunks.py
```

---

### test_community_detection.py

Test script specifically for community detection validation.

**Usage**:
```bash
python scripts/testing/test_community_detection.py
```

---

## Dependencies

- `pymongo`: MongoDB client
- `python-dotenv`: Environment variable loading
- `networkx`: Graph analysis (for some tests)

---

**Created**: November 7, 2025  
**Purpose**: Testing infrastructure for GraphRAG pipeline validation


