# GraphRAG Scripts

All scripts for the GraphRAG project, organized by purpose.

## Directory Structure

```
app/scripts/
├── analysis/              # Quality & ontology analysis
│   ├── quality/           # Entity type, predicate, extraction analysis
│   └── ontology/          # Ontology derivation, predicate mapping
│
├── data/                  # Data ingestion & setup
│   ├── ingestion/         # YouTube, AWS Transcribe fetchers
│   └── setup/             # Database setup utilities
│
├── experiments/           # Experiment orchestration
│   ├── run_experiments.py
│   └── compare_experiments.py
│
├── graphrag/              # GraphRAG-specific utilities
│   ├── Testing scripts    # Pipeline testing
│   ├── Analysis scripts   # Graph structure analysis
│   └── Debugging scripts  # Community detection debugging
│
├── maintenance/           # Database cleanup
│   └── cleanup/           # Extraction status, field cleanup
│
├── repositories/          # Research & query scripts
│   ├── graphrag/
│   │   ├── explain/       # Debugging/explanation tools
│   │   └── queries/       # Query utilities
│   ├── monitoring/        # Error/metrics summary
│   └── rag/               # RAG-specific queries
│
├── tools/                 # Development utilities
│   ├── pre-commit         # Git pre-commit hook
│   └── quick_test.sh      # Quick test runner
│
└── utilities/             # Database utilities
    ├── check_data.py
    ├── full_cleanup.py
    └── seed/              # Index seeding
```

## Quick Reference

### Running Scripts

All scripts can be run from the GraphRAG root directory:

```bash
# Analysis
python -m app.scripts.analysis.quality.analyze_entity_types --db <database>

# Data ingestion
python -m app.scripts.data.ingestion.fetch_playlist_transcripts --playlist-id <id>

# Experiments
python -m app.scripts.experiments.run_experiments --config config.json

# Maintenance
python -m app.scripts.maintenance.cleanup.clean_graphrag_fields --db <database> --dry-run

# GraphRAG testing
python app/scripts/graphrag/test_random_chunks.py --num-chunks 12 --seed 42

# Utilities
python app/scripts/utilities/check_data.py --db <database>
```

### Development Tools

```bash
# Quick test for a module
./app/scripts/tools/quick_test.sh core

# Setup git hooks
git config core.hooksPath app/scripts/tools
```

## Documentation

- **[SCRIPTS_INVENTORY.md](./SCRIPTS_INVENTORY.md)** - Original app/scripts inventory
- **[SCRIPTS_INVENTORY_ROOT.md](./SCRIPTS_INVENTORY_ROOT.md)** - Migrated root scripts inventory  
- **[MIGRATION_PLAN.md](./MIGRATION_PLAN.md)** - Migration planning document

## Category Details

### analysis/

Quality analysis and ontology development scripts.

| Subfolder | Purpose |
|-----------|---------|
| `quality/` | Entity type distribution, predicate analysis, extraction comparison |
| `ontology/` | Automatic ontology derivation, predicate mapping |

### data/

Data fetching and database setup utilities.

| Subfolder | Purpose |
|-----------|---------|
| `ingestion/` | YouTube playlist fetching, AWS Transcribe backfill |
| `setup/` | Validation database setup, data copying |

### experiments/

GraphRAG experiment orchestration.

- `run_experiments.py` - Run experiments with different configurations
- `compare_experiments.py` - Compare experiment results

### graphrag/

GraphRAG-specific testing and debugging tools.

- Testing: Random chunk selection, community detection tests
- Analysis: Graph structure analysis, density monitoring
- Debugging: Community detection inspection, diagnostics

### maintenance/

Database cleanup scripts.

| Script | Purpose |
|--------|---------|
| `clean_extraction_status.py` | Reset extraction status fields |
| `clean_graphrag_fields.py` | Remove GraphRAG fields from documents |

### repositories/

Research and query scripts for development/debugging.

| Subfolder | Purpose |
|-----------|---------|
| `graphrag/explain/` | Debug why entities merged, relationships filtered |
| `graphrag/queries/` | Query raw entities, resolution decisions, compare states |
| `monitoring/` | Error and metrics summaries |
| `rag/` | RAG-specific chunk queries |

### tools/

Development convenience scripts.

- `pre-commit` - Git pre-commit hook for running tests
- `quick_test.sh` - Quick test runner for specific modules

### utilities/

General database utilities.

- `check_data.py` - Data inspection
- `full_cleanup.py` - Full database cleanup
- `seed/seed_indexes.py` - MongoDB index creation

## Environment Variables

All scripts use these common environment variables:

- `MONGODB_URI` - MongoDB connection string
- `MONGODB_DB` - Default database name
- `OPENAI_API_KEY` - OpenAI API key (for LLM operations)
- `YOUTUBE_API_KEY` - YouTube Data API key (for data ingestion)

