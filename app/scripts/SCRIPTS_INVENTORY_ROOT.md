# GraphRAG Scripts Inventory - POST MIGRATION

**Location**: `scripts/` (root level)  
**Date**: December 9, 2025  
**Status**: After migration - most scripts moved to new locations

---

## Migration Summary

The scripts have been reorganized into logical categories:

| Category | New Location | Scripts Moved |
|----------|--------------|---------------|
| Testing | `tests/` | 6 scripts + 15 bash tests |
| Data Ingestion | `data/` | 5 scripts |
| Experiments | `experiments/` | 2 scripts |
| Analysis | `analysis/` | 5 scripts |
| Maintenance | `maintenance/` | 4 scripts |
| Dev Tools | `tools/`, `.git-hooks/` | 2 scripts |

---

## Current scripts/ Structure

After migration, `scripts/` contains only:

```
scripts/
├── SCRIPTS_INVENTORY.md    # This document
├── MIGRATION_PLAN.md       # Migration planning document
└── repositories/           # Research & query scripts (kept)
    ├── graphrag/
    │   ├── explain/        # Debugging/explanation tools
    │   │   ├── __init__.py
    │   │   ├── explain_community_formation.py
    │   │   ├── explain_entity_merge.py
    │   │   ├── explain_relationship_filter.py
    │   │   ├── explain_utils.py
    │   │   ├── README.md
    │   │   ├── trace_entity_journey.py
    │   │   └── visualize_graph_evolution.py
    │   ├── queries/        # Query utilities
    │   │   ├── compare_before_after_construction.py
    │   │   ├── compare_before_after_resolution.py
    │   │   ├── compare_detection_algorithms.py
    │   │   ├── compare_extraction_runs.py
    │   │   ├── find_resolution_errors.py
    │   │   ├── query_graph_evolution.py
    │   │   ├── query_pre_detection_graph.py
    │   │   ├── query_raw_entities.py
    │   │   ├── query_raw_relationships.py
    │   │   ├── query_resolution_decisions.py
    │   │   ├── query_utils.py
    │   │   └── README.md
    │   ├── query_communities.py
    │   ├── query_entities.py
    │   ├── query_graphrag_runs.py
    │   ├── query_relations.py
    │   └── stats_summary.py
    ├── monitoring/
    │   ├── error_summary.py
    │   └── metrics_summary.py
    ├── rag/
    │   └── query_chunks.py
    └── README.md
```

---

## Migrated Scripts Reference

### Testing (moved to `tests/`)

| Old Location | New Location |
|--------------|--------------|
| `scripts/run_tests.py` | `tests/run_tests.py` |
| `scripts/validate_imports.py` | `tests/quality/validate_imports.py` |
| `scripts/audit_error_handling.py` | `tests/quality/audit_error_handling.py` |
| `scripts/validate_metrics.py` | `tests/quality/validate_metrics.py` |
| `scripts/validate_entity_resolution_test.py` | `tests/business/validate_entity_resolution.py` |
| `scripts/test_api/*.sh` | `tests/api/graph_api/*.sh` |

### Data Ingestion (moved to `data/`)

| Old Location | New Location |
|--------------|--------------|
| `scripts/generate_db_with_raw_videos.py` | `data/ingestion/generate_db_with_raw_videos.py` |
| `scripts/fetch_playlist_transcripts.py` | `data/ingestion/fetch_playlist_transcripts.py` |
| `scripts/transcribe_missing.py` | `data/ingestion/transcribe_missing.py` |
| `scripts/setup_validation_db.py` | `data/setup/setup_validation_db.py` |
| `scripts/copy_chunks_to_validation_db.py` | `data/setup/copy_chunks_to_validation_db.py` |

### Experiments (moved to `experiments/`)

| Old Location | New Location |
|--------------|--------------|
| `scripts/run_experiments.py` | `experiments/run_experiments.py` |
| `scripts/compare_graphrag_experiments.py` | `experiments/compare_experiments.py` |

### Analysis (moved to `analysis/`)

| Old Location | New Location |
|--------------|--------------|
| `scripts/analyze_entity_types.py` | `analysis/quality/analyze_entity_types.py` |
| `scripts/analyze_predicate_distribution.py` | `analysis/quality/analyze_predicate_distribution.py` |
| `scripts/compare_extraction_quality.py` | `analysis/quality/compare_extraction_quality.py` |
| `scripts/derive_ontology.py` | `analysis/ontology/derive_ontology.py` |
| `scripts/build_predicate_map.py` | `analysis/ontology/build_predicate_map.py` |

### Maintenance (moved to `maintenance/`)

| Old Location | New Location |
|--------------|--------------|
| `scripts/clean_extraction_status.py` | `maintenance/cleanup/clean_extraction_status.py` |
| `scripts/clean_graphrag_fields.py` | `maintenance/cleanup/clean_graphrag_fields.py` |
| `scripts/archive_plan.py` | `maintenance/archive/archive_plan.py` |
| `scripts/move_archive_files.py` | `maintenance/archive/move_archive_files.py` |

### Dev Tools (moved to `tools/` and `.git-hooks/`)

| Old Location | New Location |
|--------------|--------------|
| `scripts/quick_test.sh` | `tools/quick_test.sh` |
| `scripts/pre-commit-hook.sh` | `.git-hooks/pre-commit` |

---

## Remaining: repositories/

The `repositories/` subfolder contains specialized query and debugging scripts that are unique to GraphRAG research and development. These are kept in `scripts/` because they:

1. **Are not API candidates** - They're interactive debugging tools
2. **Require human interpretation** - Output is for analysis, not UI consumption
3. **Have specialized dependencies** - May require optional packages
4. **Are organized logically** - Already well-structured by purpose

### repositories/graphrag/explain/

Debugging tools for understanding GraphRAG decisions:

- `explain_community_formation.py` - Why communities were formed
- `explain_entity_merge.py` - Why entities were merged during resolution
- `explain_relationship_filter.py` - Why relationships were filtered
- `trace_entity_journey.py` - Track an entity through all pipeline stages
- `visualize_graph_evolution.py` - Visualize graph changes over time
- `explain_utils.py` - Shared utilities

### repositories/graphrag/queries/

Query utilities for comparing pipeline states:

- `compare_before_after_*.py` - Compare pipeline stage outputs
- `query_raw_*.py` - Query raw extraction output
- `query_resolution_decisions.py` - Query entity resolution decisions
- `find_resolution_errors.py` - Find potential resolution errors
- `query_utils.py` - Shared query utilities

### repositories/monitoring/

Monitoring and error tracking:

- `error_summary.py` - Summarize errors from logs
- `metrics_summary.py` - Summarize pipeline metrics

### repositories/rag/

RAG-specific queries:

- `query_chunks.py` - Query chunk data for RAG testing

---

## New Directory Structure Overview

```
GraphRAG/
├── app/
│   ├── graph_api/          # Graph Data API (port 8081)
│   ├── stages_api/         # Pipeline API (port 8080)
│   └── scripts/            # App-level utilities
│
├── data/                   # NEW: Data ingestion & setup
│   ├── ingestion/
│   └── setup/
│
├── experiments/            # NEW: Experiment orchestration
│   ├── run_experiments.py
│   └── compare_experiments.py
│
├── analysis/               # NEW: Quality & ontology analysis
│   ├── quality/
│   └── ontology/
│
├── maintenance/            # NEW: Cleanup & maintenance
│   ├── cleanup/
│   └── archive/
│
├── tools/                  # NEW: Development utilities
│   └── quick_test.sh
│
├── tests/                  # ENHANCED: All testing
│   ├── run_tests.py        # Moved from scripts/
│   ├── quality/            # NEW: Quality gates
│   ├── api/graph_api/      # NEW: Graph API tests
│   └── business/           # Business logic tests
│
├── scripts/                # CLEANED: Only repositories/ remains
│   ├── SCRIPTS_INVENTORY.md
│   ├── MIGRATION_PLAN.md
│   └── repositories/       # Research/query scripts
│
└── .git-hooks/             # NEW: Git hooks
    └── pre-commit
```

---

## Related Documentation

- [Migration Plan](./MIGRATION_PLAN.md) - Full migration documentation
- [Data README](../data/README.md) - Data ingestion documentation
- [Experiments README](../experiments/README.md) - Experiment documentation
- [Analysis README](../analysis/README.md) - Analysis tools documentation
- [Maintenance README](../maintenance/README.md) - Maintenance scripts documentation
- [Tests API README](../tests/api/graph_api/README.md) - API test documentation
- [Tools README](../tools/README.md) - Development tools documentation

---

**End of Post-Migration Inventory**
