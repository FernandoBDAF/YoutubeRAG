# Script Consolidation Analysis

**Date**: November 7, 2025  
**Purpose**: Analyze overlap between `app/scripts` and `scripts/repositories` to consolidate and organize scripts

---

## Current State

### app/scripts/ (Legacy)

**app/scripts/graphrag/** (8 scripts):
- `analyze_graph_structure.py` - Analyzes graph structure with NetworkX
- `diagnose_communities.py` - Diagnoses community detection issues
- `inspect_community_detection.py` - Inspects community detection results
- `monitor_density.py` - Monitors graph density
- `run_random_chunk_test.py` - Setup for random chunk testing
- `sample_graph_data.py` - Samples graph data for inspection
- `test_community_detection.py` - Tests community detection
- `test_random_chunks.py` - Tests with random chunks

**app/scripts/utilities/** (3 scripts):
- `check_data.py` - Checks GraphRAG data across databases
- `full_cleanup.py` - Full GraphRAG data cleanup
- `seed/seed_indexes.py` - Seeds database indexes

### scripts/repositories/ (New)

**scripts/repositories/graphrag/** (5 scripts):
- `query_entities.py` - Query entities with filters
- `query_relations.py` - Query relationships
- `query_communities.py` - Query communities
- `query_graphrag_runs.py` - Query run metadata
- `stats_summary.py` - Overall statistics

**scripts/repositories/rag/** (1 script):
- `query_chunks.py` - Query video chunks

**scripts/repositories/monitoring/** (2 scripts):
- `metrics_summary.py` - Metrics aggregation
- `error_summary.py` - Error analysis

---

## Analysis

### Overlap & Duplication

1. **sample_graph_data.py** ↔ **stats_summary.py**
   - **Overlap**: Both show entity/relation counts and types
   - **Difference**: sample_graph_data.py shows samples, stats_summary.py shows aggregates
   - **Recommendation**: Keep both, different use cases

2. **check_data.py** ↔ **stats_summary.py**
   - **Overlap**: Both check collection counts
   - **Difference**: check_data.py checks all databases, stats_summary.py is more detailed
   - **Recommendation**: Merge or complement

3. **analyze_graph_structure.py** ↔ **query_relations.py / query_entities.py**
   - **Overlap**: Some overlap in data access
   - **Difference**: analyze_graph_structure.py uses NetworkX for advanced analysis
   - **Recommendation**: Keep separate, different purposes

### Scripts to Incorporate

**Testing Scripts** (should move to `scripts/testing/`):
- `run_random_chunk_test.py` - Test setup
- `test_random_chunks.py` - Random chunk tests
- `test_community_detection.py` - Community detection tests

**Analysis Scripts** (should move to `scripts/repositories/graphrag/analysis/`):
- `analyze_graph_structure.py` - Advanced graph analysis
- `diagnose_communities.py` - Community diagnostics
- `inspect_community_detection.py` - Community inspection
- `monitor_density.py` - Density monitoring

**Utility Scripts** (should move to `scripts/repositories/utilities/`):
- `check_data.py` - Data checking
- `full_cleanup.py` - Data cleanup
- `seed_indexes.py` - Index seeding

---

## Recommended Structure

```
scripts/
├── repositories/           # Database query scripts (NEW)
│   ├── graphrag/
│   │   ├── query_entities.py
│   │   ├── query_relations.py
│   │   ├── query_communities.py
│   │   ├── query_graphrag_runs.py
│   │   ├── stats_summary.py
│   │   └── analysis/      # Advanced analysis (FROM app/scripts)
│   │       ├── analyze_graph_structure.py
│   │       ├── diagnose_communities.py
│   │       ├── inspect_community_detection.py
│   │       └── monitor_density.py
│   ├── rag/
│   │   └── query_chunks.py
│   ├── monitoring/
│   │   ├── metrics_summary.py
│   │   └── error_summary.py
│   └── utilities/         # Utility scripts (FROM app/scripts)
│       ├── check_data.py
│       ├── full_cleanup.py
│       └── seed_indexes.py
├── testing/               # Testing scripts (FROM app/scripts)
│   ├── run_random_chunk_test.py
│   ├── test_random_chunks.py
│   └── test_community_detection.py
└── README.md

app/scripts/               # DEPRECATED - to be removed
```

---

## Consolidation Plan

### Phase 1: Move Analysis Scripts

1. Create `scripts/repositories/graphrag/analysis/` directory
2. Move from `app/scripts/graphrag/`:
   - `analyze_graph_structure.py`
   - `diagnose_communities.py`
   - `inspect_community_detection.py`
   - `monitor_density.py`

### Phase 2: Move Testing Scripts

1. Create `scripts/testing/` directory
2. Move from `app/scripts/graphrag/`:
   - `run_random_chunk_test.py`
   - `test_random_chunks.py`
   - `test_community_detection.py`

### Phase 3: Move Utility Scripts

1. Create `scripts/repositories/utilities/` directory
2. Move from `app/scripts/utilities/`:
   - `check_data.py`
   - `full_cleanup.py`
   - `seed/seed_indexes.py`

### Phase 4: Remove Duplicates

1. Check `sample_graph_data.py` - if redundant with stats_summary.py, remove or merge
2. Deprecate `app/scripts/` directory

---

## Implementation

**Effort**: 30-45 minutes  
**Risk**: Low (moving files, no code changes)  
**Benefit**: Better organization, reduced duplication

---

**Next Steps**: Execute consolidation plan

