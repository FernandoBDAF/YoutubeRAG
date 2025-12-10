# Scripts Migration Plan

**Date**: December 9, 2025  
**Status**: COMPLETED - Migration Executed  
**Purpose**: Reorganize scripts/ folder for better maintainability

---

## Executive Summary

This document outlines a comprehensive plan to migrate all scripts from the root `scripts/` folder to appropriate locations based on their purpose and usage patterns. The goal is to create a clear, organized structure that separates concerns and reduces confusion.

**Current State**: 25 root scripts + 85+ files in subdirectories (110+ total)  
**Target State**: Organized into logical categories with clear ownership

---

## Migration Principles

1. **Separate by Purpose**: Group scripts by what they do, not just where they fit
2. **API-Adjacent Placement**: Scripts that could become APIs should be near API code
3. **Test Co-location**: Tests should live near what they test
4. **Single Source of Truth**: Eliminate remaining duplicates
5. **Clear Ownership**: Each script category has a clear home

---

## Table of Contents

1. [Migration Categories](#migration-categories)
2. [Detailed Migration Plan](#detailed-migration-plan)
3. [New Directory Structure](#new-directory-structure)
4. [File-by-File Migration](#file-by-file-migration)
5. [API Enhancement Candidates](#api-enhancement-candidates)
6. [Implementation Steps](#implementation-steps)

---

## Migration Categories

### Category A: Move to app/graph_api/

**Criteria**: Scripts that provide functionality related to graph data queries

| Script | Current Path | New Path | Reason |
|--------|--------------|----------|--------|
| None identified | - | - | Graph API is complete |

**Note**: Current scripts don't duplicate Graph API functionality. They provide analysis that could become future API endpoints.

---

### Category B: Move to app/scripts/

**Criteria**: Scripts that support app-level operations (pipelines, utilities)

| Script | Current Path | New Path | Reason |
|--------|--------------|----------|--------|
| None needed | - | - | app/scripts already has utilities |

---

### Category C: Move to tests/

**Criteria**: Testing and validation scripts

| Script | Current Path | New Path | Reason |
|--------|--------------|----------|--------|
| `run_tests.py` | `scripts/` | `tests/run_tests.py` | Test runner belongs with tests |
| `validate_imports.py` | `scripts/` | `tests/quality/validate_imports.py` | Quality gate test |
| `audit_error_handling.py` | `scripts/` | `tests/quality/audit_error_handling.py` | Quality gate test |
| `validate_metrics.py` | `scripts/` | `tests/quality/validate_metrics.py` | Quality gate test |
| `validate_entity_resolution_test.py` | `scripts/` | `tests/business/validate_entity_resolution.py` | Entity resolution test |
| `test_api/*.sh` (15 files) | `scripts/test_api/` | `tests/api/graph_api/` | API integration tests |

---

### Category D: Move to tools/

**Criteria**: Development tools not directly related to testing

| Script | Current Path | New Path | Reason |
|--------|--------------|----------|--------|
| `pre-commit-hook.sh` | `scripts/` | `.git-hooks/pre-commit` | Git workflow |
| `quick_test.sh` | `scripts/` | `tools/quick_test.sh` | Dev convenience |

---

### Category E: Create data/ folder

**Criteria**: Data ingestion and preparation scripts

| Script | Current Path | New Path | Reason |
|--------|--------------|----------|--------|
| `generate_db_with_raw_videos.py` | `scripts/` | `data/ingestion/generate_db_with_raw_videos.py` | Database setup |
| `fetch_playlist_transcripts.py` | `scripts/` | `data/ingestion/fetch_playlist_transcripts.py` | YouTube ingestion |
| `transcribe_missing.py` | `scripts/` | `data/ingestion/transcribe_missing.py` | AWS transcription |
| `setup_validation_db.py` | `scripts/` | `data/setup/setup_validation_db.py` | DB setup |
| `copy_chunks_to_validation_db.py` | `scripts/` | `data/setup/copy_chunks_to_validation_db.py` | DB setup |

---

### Category F: Create experiments/ folder

**Criteria**: Experiment orchestration and analysis

| Script | Current Path | New Path | Reason |
|--------|--------------|----------|--------|
| `run_experiments.py` | `scripts/` | `experiments/run_experiments.py` | Experiment runner |
| `compare_graphrag_experiments.py` | `scripts/` | `experiments/compare_experiments.py` | Experiment comparison |

---

### Category G: Create analysis/ folder

**Criteria**: Data quality analysis and ontology development

| Script | Current Path | New Path | Reason |
|--------|--------------|----------|--------|
| `analyze_entity_types.py` | `scripts/` | `analysis/quality/analyze_entity_types.py` | Quality analysis |
| `analyze_predicate_distribution.py` | `scripts/` | `analysis/quality/analyze_predicate_distribution.py` | Quality analysis |
| `compare_extraction_quality.py` | `scripts/` | `analysis/quality/compare_extraction_quality.py` | Quality comparison |
| `derive_ontology.py` | `scripts/` | `analysis/ontology/derive_ontology.py` | Ontology generation |
| `build_predicate_map.py` | `scripts/` | `analysis/ontology/build_predicate_map.py` | Ontology tooling |

---

### Category H: Create maintenance/ folder

**Criteria**: Database cleanup and maintenance scripts

| Script | Current Path | New Path | Reason |
|--------|--------------|----------|--------|
| `clean_extraction_status.py` | `scripts/` | `maintenance/clean_extraction_status.py` | Data cleanup |
| `clean_graphrag_fields.py` | `scripts/` | `maintenance/clean_graphrag_fields.py` | Data cleanup |
| `archive_plan.py` | `scripts/` | `maintenance/archive_plan.py` | File management |
| `move_archive_files.py` | `scripts/` | `maintenance/move_archive_files.py` | File management |

---

### Category I: Consolidate repositories/

**Criteria**: Already organized, needs minor cleanup

| Current Location | Action | Reason |
|-----------------|--------|--------|
| `repositories/graphrag/explain/` | ✅ Keep | Unique debugging tools |
| `repositories/graphrag/queries/` | ✅ Keep | Specialized queries |
| `repositories/graphrag/*.py` (5 root files) | 🔄 Move to `queries/` | Consolidate |
| `repositories/monitoring/` | ✅ Keep | Monitoring utilities |
| `repositories/rag/` | ✅ Keep | RAG-specific queries |

---

## Detailed Migration Plan

### Phase 1: Create New Directory Structure

```bash
# Create new directories
mkdir -p data/ingestion
mkdir -p data/setup
mkdir -p experiments
mkdir -p analysis/quality
mkdir -p analysis/ontology
mkdir -p maintenance
mkdir -p tools
mkdir -p tests/quality
mkdir -p tests/api/graph_api
```

---

### Phase 2: Migrate Testing Scripts

**Rationale**: Tests belong in the `tests/` directory, not `scripts/`

#### 2.1 Move Test Runner

```bash
# Primary test runner
mv scripts/run_tests.py tests/run_tests.py

# Update shebang and imports if needed
```

**Updates Required**:
- Update import paths (if any relative imports)
- Update documentation references
- Update CI/CD scripts

---

#### 2.2 Move Quality Gates

```bash
# Quality validation scripts
mv scripts/validate_imports.py tests/quality/validate_imports.py
mv scripts/audit_error_handling.py tests/quality/audit_error_handling.py
mv scripts/validate_metrics.py tests/quality/validate_metrics.py
mv scripts/validate_entity_resolution_test.py tests/business/validate_entity_resolution.py
```

**Updates Required**:
- Update `pre-commit-hook.sh` to point to new locations
- Update CI/CD references

---

#### 2.3 Migrate API Tests

```bash
# Bash API test scripts (15 files)
mv scripts/test_api/*.sh tests/api/graph_api/

# Update test URLs in scripts (if needed)
# Most should still work - endpoints unchanged
```

**Updates Required**:
- Review each bash script
- Update base URLs if changed
- Add README explaining how to run tests

---

### Phase 3: Migrate Data Ingestion Scripts

**Rationale**: Data ingestion is a separate concern from core business logic

```bash
# Create data/ directory structure
mkdir -p data/ingestion
mkdir -p data/setup

# Move ingestion scripts
mv scripts/generate_db_with_raw_videos.py data/ingestion/
mv scripts/fetch_playlist_transcripts.py data/ingestion/
mv scripts/transcribe_missing.py data/ingestion/

# Move setup scripts
mv scripts/setup_validation_db.py data/setup/
mv scripts/copy_chunks_to_validation_db.py data/setup/
```

**Updates Required**:
- Add `data/__init__.py`
- Add `data/README.md` with usage instructions
- Update any scripts that reference these paths

---

### Phase 4: Migrate Experiment Scripts

**Rationale**: Experiments are first-class workflows deserving their own space

```bash
# Create experiments/ directory
mkdir -p experiments
mkdir -p experiments/configs

# Move experiment scripts
mv scripts/run_experiments.py experiments/
mv scripts/compare_graphrag_experiments.py experiments/compare_experiments.py

# Move config files if they exist
if [ -d "configs" ]; then
  mv configs/graphrag experiments/configs/
fi
```

**Updates Required**:
- Add `experiments/__init__.py`
- Add `experiments/README.md` with usage guide
- Update config file paths in scripts

**New Experiment Structure**:
```
experiments/
├── __init__.py
├── README.md
├── run_experiments.py
├── compare_experiments.py
├── configs/
│   ├── baseline.json
│   ├── high_quality.json
│   └── fast_test.json
└── results/
    └── experiment_results_YYYYMMDD.json
```

---

### Phase 5: Migrate Analysis Scripts

**Rationale**: Analysis scripts are tools for data quality and ontology development

```bash
# Create analysis/ directory structure
mkdir -p analysis/quality
mkdir -p analysis/ontology

# Move quality analysis
mv scripts/analyze_entity_types.py analysis/quality/
mv scripts/analyze_predicate_distribution.py analysis/quality/
mv scripts/compare_extraction_quality.py analysis/quality/

# Move ontology scripts
mv scripts/derive_ontology.py analysis/ontology/
mv scripts/build_predicate_map.py analysis/ontology/
```

**Updates Required**:
- Add `analysis/__init__.py`
- Add `analysis/README.md`
- Update output paths (reports/ directory)

**New Analysis Structure**:
```
analysis/
├── __init__.py
├── README.md
├── quality/
│   ├── __init__.py
│   ├── analyze_entity_types.py
│   ├── analyze_predicate_distribution.py
│   └── compare_extraction_quality.py
├── ontology/
│   ├── __init__.py
│   ├── derive_ontology.py
│   └── build_predicate_map.py
└── reports/
    ├── entity_type_distribution_*.md
    ├── predicate_distribution_*.md
    └── extraction_quality_*.md
```

---

### Phase 6: Migrate Maintenance Scripts

**Rationale**: Cleanup and maintenance scripts should be clearly separated

```bash
# Create maintenance/ directory
mkdir -p maintenance/cleanup
mkdir -p maintenance/archive

# Move cleanup scripts
mv scripts/clean_extraction_status.py maintenance/cleanup/
mv scripts/clean_graphrag_fields.py maintenance/cleanup/

# Move archive scripts
mv scripts/archive_plan.py maintenance/archive/
mv scripts/move_archive_files.py maintenance/archive/
```

**Updates Required**:
- Add `maintenance/__init__.py`
- Add `maintenance/README.md` with safety warnings

---

### Phase 7: Consolidate repositories/

**Rationale**: repositories/ is well-organized but has some redundancy

```bash
# Move root-level query scripts into queries/ subfolder
cd scripts/repositories/graphrag

mv query_entities.py queries/
mv query_relations.py queries/
mv query_communities.py queries/
mv query_graphrag_runs.py queries/
mv stats_summary.py queries/

# Add index/navigation
echo "See queries/ subfolder for all query utilities" > QUERIES.md
```

**Updates Required**:
- Update `repositories/README.md`
- Document query script usage

---

### Phase 8: Create tools/ for Dev Utilities

**Rationale**: Development convenience scripts

```bash
# Create tools/ directory
mkdir -p tools

# Move quick test script
mv scripts/quick_test.sh tools/

# Move pre-commit hook to git-hooks
mkdir -p .git-hooks
mv scripts/pre-commit-hook.sh .git-hooks/pre-commit
chmod +x .git-hooks/pre-commit

# Configure git to use custom hooks directory
git config core.hooksPath .git-hooks
```

---

## New Directory Structure

### Final Layout

```
GraphRAG/
├── app/
│   ├── graph_api/              ← Graph data API (port 8081)
│   ├── stages_api/             ← Pipeline API (port 8080)
│   └── scripts/                ← App-level utilities (unchanged)
│       ├── graphrag/           ← GraphRAG testing/analysis
│       └── utilities/          ← Database utilities
│
├── data/                       ← NEW: Data ingestion & setup
│   ├── ingestion/
│   │   ├── fetch_playlist_transcripts.py
│   │   ├── transcribe_missing.py
│   │   └── generate_db_with_raw_videos.py
│   └── setup/
│       ├── setup_validation_db.py
│       └── copy_chunks_to_validation_db.py
│
├── experiments/                ← NEW: Experiment orchestration
│   ├── run_experiments.py
│   ├── compare_experiments.py
│   ├── configs/
│   │   └── *.json
│   └── results/
│       └── *.json
│
├── analysis/                   ← NEW: Quality & ontology analysis
│   ├── quality/
│   │   ├── analyze_entity_types.py
│   │   ├── analyze_predicate_distribution.py
│   │   └── compare_extraction_quality.py
│   ├── ontology/
│   │   ├── derive_ontology.py
│   │   └── build_predicate_map.py
│   └── reports/
│       └── *.md, *.json
│
├── maintenance/                ← NEW: Cleanup & maintenance
│   ├── cleanup/
│   │   ├── clean_extraction_status.py
│   │   └── clean_graphraf_fields.py
│   └── archive/
│       ├── archive_plan.py
│       └── move_archive_files.py
│
├── tools/                      ← NEW: Development utilities
│   └── quick_test.sh
│
├── tests/                      ← Enhanced: All testing
│   ├── run_tests.py            ← Moved from scripts/
│   ├── quality/                ← NEW: Quality gates
│   │   ├── validate_imports.py
│   │   ├── audit_error_handling.py
│   │   └── validate_metrics.py
│   ├── api/
│   │   └── graph_api/          ← NEW: Graph API tests
│   │       ├── test_entities.sh
│   │       ├── test_communities.sh
│   │       └── ... (15 bash scripts)
│   ├── business/
│   │   └── validate_entity_resolution.py
│   └── ... (existing test structure)
│
├── scripts/                    ← Cleaned up: Only repositories/ remains
│   ├── SCRIPTS_INVENTORY.md   ← Updated with new structure
│   ├── MIGRATION_PLAN.md      ← This document
│   └── repositories/          ← Keep as research/query scripts
│       ├── graphrag/
│       │   ├── explain/       (7 files - keep)
│       │   └── queries/       (18 files - consolidated)
│       ├── monitoring/        (2 files - keep)
│       └── rag/               (1 file - keep)
│
└── .git-hooks/                 ← NEW: Git hooks
    └── pre-commit
```

---

## File-by-File Migration

### Root Scripts (25 files)

| # | Script | Current | Target | Category |
|---|--------|---------|--------|----------|
| 1 | `generate_db_with_raw_videos.py` | `scripts/` | `data/ingestion/` | Data |
| 2 | `fetch_playlist_transcripts.py` | `scripts/` | `data/ingestion/` | Data |
| 3 | `transcribe_missing.py` | `scripts/` | `data/ingestion/` | Data |
| 4 | `run_experiments.py` | `scripts/` | `experiments/` | Experiments |
| 5 | `compare_graphrag_experiments.py` | `scripts/` | `experiments/compare_experiments.py` | Experiments |
| 6 | `audit_error_handling.py` | `scripts/` | `tests/quality/` | Testing |
| 7 | `validate_metrics.py` | `scripts/` | `tests/quality/` | Testing |
| 8 | `validate_imports.py` | `scripts/` | `tests/quality/` | Testing |
| 9 | `run_tests.py` | `scripts/` | `tests/` | Testing |
| 10 | `validate_entity_resolution_test.py` | `scripts/` | `tests/business/` | Testing |
| 11 | `analyze_entity_types.py` | `scripts/` | `analysis/quality/` | Analysis |
| 12 | `analyze_predicate_distribution.py` | `scripts/` | `analysis/quality/` | Analysis |
| 13 | `compare_extraction_quality.py` | `scripts/` | `analysis/quality/` | Analysis |
| 14 | `derive_ontology.py` | `scripts/` | `analysis/ontology/` | Analysis |
| 15 | `build_predicate_map.py` | `scripts/` | `analysis/ontology/` | Analysis |
| 16 | `clean_extraction_status.py` | `scripts/` | `maintenance/cleanup/` | Maintenance |
| 17 | `clean_graphrag_fields.py` | `scripts/` | `maintenance/cleanup/` | Maintenance |
| 18 | `archive_plan.py` | `scripts/` | `maintenance/archive/` | Maintenance |
| 19 | `move_archive_files.py` | `scripts/` | `maintenance/archive/` | Maintenance |
| 20 | `setup_validation_db.py` | `scripts/` | `data/setup/` | Data |
| 21 | `copy_chunks_to_validation_db.py` | `scripts/` | `data/setup/` | Data |
| 22 | `pre-commit-hook.sh` | `scripts/` | `.git-hooks/` | Git |
| 23 | `quick_test.sh` | `scripts/` | `tools/` | Dev Tools |
| 24 | `SCRIPTS_INVENTORY.md` | `scripts/` | ✅ Keep | Documentation |
| 25 | `MIGRATION_PLAN.md` | `scripts/` | ✅ Keep | Documentation |

### test_api/ (15 bash scripts)

All `.sh` files → `tests/api/graph_api/`

### repositories/ (70+ files)

| Current | Target | Action |
|---------|--------|--------|
| `graphrag/explain/*` | ✅ Keep | Unique tools |
| `graphrag/queries/*` | ✅ Keep | Unique tools |
| `graphrag/*.py` (5 root) | `queries/` | Consolidate |
| `monitoring/*` | ✅ Keep | Unique tools |
| `rag/*` | ✅ Keep | Unique tools |

---

## API Enhancement Candidates

### Scripts That Could Become API Endpoints

Some script functionality is valuable enough to expose via API in the future:

#### 1. Connected Components Analysis

**Current**: Part of `app/scripts/graphrag/analyze_graph_structure.py`

**Proposed API**:
```
GET /api/statistics/components
```

**Response**:
```json
{
  "total_components": 45,
  "largest_component_size": 120,
  "isolated_nodes": 638,
  "component_size_distribution": [
    {"size": 1, "count": 638},
    {"size": 120, "count": 1}
  ]
}
```

**Implementation**:
- Extract logic from script
- Create `app/graph_api/handlers/components.py`
- Add route in `router.py`

**Priority**: 🟡 Medium - Nice-to-have for GraphDash

---

#### 2. Hub Entities (Most Connected)

**Current**: Part of `analyze_graph_structure.py`

**Proposed API**:
```
GET /api/entities/hubs?limit=10
```

**Response**:
```json
{
  "hubs": [
    {
      "entity_id": "ent_abc",
      "name": "Machine Learning",
      "type": "CONCEPT",
      "degree": 42,
      "relationships": {
        "incoming": 20,
        "outgoing": 22
      }
    }
  ]
}
```

**Priority**: 🟢 High - Useful for GraphDash visualization

---

#### 3. Graph Health Check

**Current**: Issue detection in `analyze_graph_structure.py`

**Proposed API**:
```
GET /api/statistics/health
```

**Response**:
```json
{
  "health_score": 0.65,
  "issues": [
    {
      "severity": "warning",
      "type": "low_density",
      "message": "Graph density is 0.0005 (< 0.01)",
      "recommendation": "Extract more relationships per chunk"
    }
  ],
  "metrics": {
    "density": 0.0005,
    "isolated_nodes_pct": 0.698,
    "avg_degree": 0.45
  }
}
```

**Priority**: 🟡 Medium - Useful for monitoring

---

#### 4. Clustering Metrics

**Current**: Part of `analyze_graph_structure.py`

**Proposed API**:
```
GET /api/statistics/clustering
```

**Response**:
```json
{
  "avg_clustering_coefficient": 0.42,
  "triangle_count": 120,
  "cohesion_score": 0.65,
  "local_clustering": {
    "min": 0.0,
    "max": 1.0,
    "avg": 0.42
  }
}
```

**Priority**: 🟡 Medium - Nice-to-have

---

#### 5. Query Resolution Decisions

**Current**: `repositories/graphrag/queries/query_resolution_decisions.py`

**Proposed API**:
```
GET /api/debug/resolution-decisions?entity_id={id}
```

**Response**:
```json
{
  "entity_id": "ent_abc",
  "canonical_name": "machine_learning",
  "merge_history": [
    {
      "timestamp": "2024-01-15T10:30:00Z",
      "merged_from": "ent_def",
      "reason": "high_similarity",
      "confidence": 0.92
    }
  ],
  "alternatives_considered": [
    {"entity_id": "ent_ghi", "similarity": 0.75, "rejected": true}
  ]
}
```

**Priority**: 🔴 Low - Debugging only, not for production UI

---

#### 6. Extraction Quality Metrics

**Current**: `compare_extraction_quality.py`

**Proposed API**:
```
GET /api/metrics/extraction-quality?run_id={id}
```

**Response**:
```json
{
  "run_id": "run_abc",
  "entities": {
    "total": 914,
    "avg_confidence": 0.87,
    "type_distribution": {...}
  },
  "relationships": {
    "total": 204,
    "avg_confidence": 0.82,
    "predicate_distribution": {...}
  },
  "quality_score": 0.85
}
```

**Priority**: 🟡 Medium - Useful for pipeline monitoring

---

## Implementation Steps

### Step 1: Backup

```bash
# Create backup of scripts/ folder
cd GraphRAG
tar -czf scripts_backup_$(date +%Y%m%d).tar.gz scripts/

# Verify backup
tar -tzf scripts_backup_*.tar.gz | head
```

---

### Step 2: Create Directory Structure

```bash
# Execute all mkdir commands from Phase 1
mkdir -p data/ingestion data/setup
mkdir -p experiments experiments/configs experiments/results
mkdir -p analysis/quality analysis/ontology analysis/reports
mkdir -p maintenance/cleanup maintenance/archive
mkdir -p tools
mkdir -p tests/quality tests/api/graph_api
```

---

### Step 3: Move Files in Batches

Execute moves by category (one phase at a time):

```bash
# Phase 1: Testing
git mv scripts/run_tests.py tests/
git mv scripts/validate_imports.py tests/quality/
git mv scripts/audit_error_handling.py tests/quality/
git mv scripts/validate_metrics.py tests/quality/
git mv scripts/validate_entity_resolution_test.py tests/business/validate_entity_resolution.py
git mv scripts/test_api/*.sh tests/api/graph_api/

# Phase 2: Data Ingestion
git mv scripts/generate_db_with_raw_videos.py data/ingestion/
git mv scripts/fetch_playlist_transcripts.py data/ingestion/
git mv scripts/transcribe_missing.py data/ingestion/
git mv scripts/setup_validation_db.py data/setup/
git mv scripts/copy_chunks_to_validation_db.py data/setup/

# Phase 3: Experiments
git mv scripts/run_experiments.py experiments/
git mv scripts/compare_graphrag_experiments.py experiments/compare_experiments.py

# Phase 4: Analysis
git mv scripts/analyze_entity_types.py analysis/quality/
git mv scripts/analyze_predicate_distribution.py analysis/quality/
git mv scripts/compare_extraction_quality.py analysis/quality/
git mv scripts/derive_ontology.py analysis/ontology/
git mv scripts/build_predicate_map.py analysis/ontology/

# Phase 5: Maintenance
git mv scripts/clean_extraction_status.py maintenance/cleanup/
git mv scripts/clean_graphrag_fields.py maintenance/cleanup/
git mv scripts/archive_plan.py maintenance/archive/
git mv scripts/move_archive_files.py maintenance/archive/

# Phase 6: Tools
git mv scripts/quick_test.sh tools/
git mv scripts/pre-commit-hook.sh .git-hooks/pre-commit
```

---

### Step 4: Create __init__.py and README.md Files

```bash
# Create __init__.py for Python packages
touch data/__init__.py
touch data/ingestion/__init__.py
touch data/setup/__init__.py
touch experiments/__init__.py
touch analysis/__init__.py
touch analysis/quality/__init__.py
touch analysis/ontology/__init__.py
touch maintenance/__init__.py
touch maintenance/cleanup/__init__.py
touch maintenance/archive/__init__.py

# Create README files
cat > data/README.md << 'EOF'
# Data Ingestion & Setup

Scripts for fetching and preparing data from external sources.

## Ingestion
- `fetch_playlist_transcripts.py` - YouTube playlist ingestion
- `transcribe_missing.py` - AWS Transcribe backfill
- `generate_db_with_raw_videos.py` - Database migration

## Setup
- `setup_validation_db.py` - Validation database setup
- `copy_chunks_to_validation_db.py` - Data copying
EOF

# (Repeat for other directories)
```

---

### Step 5: Update Import Paths

Scripts that import from other scripts need path updates:

```python
# Before
from scripts.compare_graphrag_experiments import get_experiment_stats

# After
from experiments.compare_experiments import get_experiment_stats
```

**Files Needing Updates**:
- Any script that imports other scripts
- `pre-commit-hook.sh` → Update paths to quality tests
- Documentation references

---

### Step 6: Update Documentation

Update these documents:
- `scripts/SCRIPTS_INVENTORY.md` - Reflect new structure
- `scripts/repositories/README.md` - Update paths
- `app/scripts/SCRIPTS_INVENTORY.md` - Cross-reference
- Any other docs mentioning script paths

---

### Step 7: Update CI/CD

If CI/CD pipelines reference scripts:
- Update paths in GitHub Actions
- Update paths in any shell scripts
- Test full CI/CD pipeline

---

### Step 8: Git Commit

```bash
# Stage all changes
git add -A

# Commit with descriptive message
git commit -m "refactor: reorganize scripts into logical categories

- Move testing scripts to tests/
- Move data ingestion to data/
- Move experiments to experiments/
- Move analysis to analysis/
- Move maintenance to maintenance/
- Move dev tools to tools/
- Consolidate repositories/graphrag queries
- Remove duplicate folders (testing/, repositories/graphrag/analysis/, repositories/utilities/)

Total: 25 scripts reorganized, 11 duplicates removed, ~62KB cleaned up"
```

---

## Benefits of Migration

### Developer Experience

**Before Migration**:
- ❌ 110+ files in flat/nested structure
- ❌ Unclear ownership (where does X belong?)
- ❌ Duplicates causing confusion
- ❌ Mixed purposes (tests, tools, data)

**After Migration**:
- ✅ Clear categories (data, experiments, analysis, tests, maintenance)
- ✅ Easy to find scripts (by purpose)
- ✅ No duplicates
- ✅ Single source of truth

---

### Maintainability

| Aspect | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Onboarding** | Find scripts by trial/error | Clear folder structure | 🟢 High |
| **Adding new scripts** | Unclear where to put | Obvious category | 🟢 High |
| **Removing scripts** | Fear of breaking things | Clear dependencies | 🟢 High |
| **Testing** | Tests scattered | Tests in tests/ | 🟢 High |
| **Documentation** | Multiple inventories | Single source | 🟢 Medium |

---

### Testing

| Aspect | Before | After |
|--------|--------|-------|
| Test location | `scripts/test_api/`, `scripts/`, `tests/` | All in `tests/` |
| Test runner location | `scripts/run_tests.py` | `tests/run_tests.py` |
| Quality gates | `scripts/` | `tests/quality/` |
| API tests | `scripts/test_api/` | `tests/api/graph_api/` |

---

## Migration Risks & Mitigation

### Risk 1: Breaking Imports

**Risk**: Other code imports from scripts

**Mitigation**:
- Search codebase for `from scripts.` imports before migration
- Update all imports
- Test all modules after migration

**Search Command**:
```bash
grep -r "from scripts\." --include="*.py" .
grep -r "import scripts\." --include="*.py" .
```

---

### Risk 2: Breaking CI/CD

**Risk**: CI pipelines reference old paths

**Mitigation**:
- Review `.github/workflows/` for script references
- Update all workflow files
- Test CI pipeline

---

### Risk 3: Documentation Drift

**Risk**: Documentation still references old paths

**Mitigation**:
- Update `SCRIPTS_INVENTORY.md`
- Update all README files
- Search for script path references in markdown

---

### Risk 4: User Confusion

**Risk**: Users have bookmarked old script paths

**Mitigation**:
- Add MIGRATION.md to old locations
- Create symlinks for transition period
- Announce in project documentation

---

## Transition Period

### Option 1: Hard Migration (Recommended)

- Move all files immediately
- Update all references
- Remove old directories
- Clean break, no confusion

**Duration**: 1-2 hours  
**Downside**: Requires updating all references at once

---

### Option 2: Soft Migration with Symlinks

- Move files to new locations
- Create symlinks at old locations
- Deprecation period (2-4 weeks)
- Remove symlinks after transition

```bash
# Example
mv scripts/run_tests.py tests/
ln -s ../tests/run_tests.py scripts/run_tests.py
```

**Duration**: 2-4 weeks  
**Downside**: Temporary complexity, two ways to access files

---

### Option 3: Gradual Migration

- Migrate one category at a time
- Week 1: Testing
- Week 2: Data & Experiments
- Week 3: Analysis & Maintenance
- Week 4: Cleanup & verification

**Duration**: 4 weeks  
**Downside**: Mixed state during transition

---

## Recommendation

**Use Option 1: Hard Migration**

**Rationale**:
- Project is in active development, easy to update
- No external users depending on script paths
- Clean break prevents confusion
- Can be done in one session

**Estimated Time**: 2-3 hours
- 30 min: Create directories and move files
- 30 min: Update import paths
- 30 min: Update documentation
- 30 min: Testing and verification
- 30 min: Buffer

---

## Post-Migration Verification

### Checklist

- [ ] All scripts moved to new locations
- [ ] Import paths updated (no `from scripts.` in codebase)
- [ ] Documentation updated
- [ ] Test runner works: `python tests/run_tests.py`
- [ ] Quality gates work: `python tests/quality/validate_imports.py`
- [ ] API tests work: `bash tests/api/graph_api/test_entities.sh`
- [ ] No broken imports: `python tests/quality/validate_imports.py business app core`
- [ ] Git hooks work: Test pre-commit hook
- [ ] CI/CD passes (if applicable)
- [ ] Old scripts/ folder only has repositories/ and docs

---

## Success Criteria

Migration is successful when:

1. ✅ All 25 root scripts moved to appropriate categories
2. ✅ No remaining duplicates
3. ✅ All tests pass
4. ✅ All imports work
5. ✅ Documentation updated
6. ✅ Clear structure: data/, experiments/, analysis/, tests/, maintenance/, tools/
7. ✅ scripts/ folder only contains repositories/ and documentation

---

## Future Enhancements

After migration is complete, consider:

1. **API Enhancements**: Add endpoints for high-value script functionality
2. **Tool Consolidation**: Merge similar analysis scripts
3. **Repository Cleanup**: Further organize repositories/ subfolder
4. **Documentation**: Create category-specific README files
5. **Automation**: Create orchestration scripts for common workflows

---

## Appendix: Command Reference

### Quick Migration Script

```bash
#!/bin/bash
# migrate_scripts.sh - Execute full migration

set -e  # Exit on error

echo "GraphRAG Scripts Migration"
echo "=========================="

# Backup
echo "Creating backup..."
tar -czf scripts_backup_$(date +%Y%m%d_%H%M%S).tar.gz scripts/

# Create structure
echo "Creating directory structure..."
mkdir -p data/ingestion data/setup
mkdir -p experiments experiments/configs
mkdir -p analysis/quality analysis/ontology
mkdir -p maintenance/cleanup maintenance/archive
mkdir -p tools
mkdir -p tests/quality tests/api/graph_api
mkdir -p .git-hooks

# Move files (using git mv for better history)
echo "Moving files..."

# Testing
git mv scripts/run_tests.py tests/
git mv scripts/validate_imports.py tests/quality/
git mv scripts/audit_error_handling.py tests/quality/
git mv scripts/validate_metrics.py tests/quality/
git mv scripts/validate_entity_resolution_test.py tests/business/validate_entity_resolution.py

# Data
git mv scripts/generate_db_with_raw_videos.py data/ingestion/
git mv scripts/fetch_playlist_transcripts.py data/ingestion/
git mv scripts/transcribe_missing.py data/ingestion/
git mv scripts/setup_validation_db.py data/setup/
git mv scripts/copy_chunks_to_validation_db.py data/setup/

# Experiments
git mv scripts/run_experiments.py experiments/
git mv scripts/compare_graphrag_experiments.py experiments/compare_experiments.py

# Analysis
git mv scripts/analyze_entity_types.py analysis/quality/
git mv scripts/analyze_predicate_distribution.py analysis/quality/
git mv scripts/compare_extraction_quality.py analysis/quality/
git mv scripts/derive_ontology.py analysis/ontology/
git mv scripts/build_predicate_map.py analysis/ontology/

# Maintenance
git mv scripts/clean_extraction_status.py maintenance/cleanup/
git mv scripts/clean_graphrag_fields.py maintenance/cleanup/
git mv scripts/archive_plan.py maintenance/archive/
git mv scripts/move_archive_files.py maintenance/archive/

# Tools
git mv scripts/quick_test.sh tools/
git mv scripts/pre-commit-hook.sh .git-hooks/pre-commit

# API tests
git mv scripts/test_api/*.sh tests/api/graph_api/

echo "✅ Migration complete!"
echo ""
echo "Next steps:"
echo "1. Update import paths in moved files"
echo "2. Update documentation"
echo "3. Test: python tests/run_tests.py"
echo "4. Commit: git commit -m 'refactor: reorganize scripts'"
```

---

**End of Migration Plan**

