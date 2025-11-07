# Repository Query Scripts

This directory contains professional database query scripts organized by domain for examining GraphRAG pipeline results and system data.

## Directory Structure

```
repositories/
├── graphrag/               # GraphRAG pipeline collections
│   ├── query_entities.py         # Query entities with filters
│   ├── query_relations.py        # Query relationships
│   ├── query_communities.py      # Query communities
│   ├── query_graphrag_runs.py    # Query run metadata
│   ├── stats_summary.py          # Overall statistics
│   └── analysis/                 # Advanced graph analysis
│       ├── analyze_graph_structure.py   # NetworkX graph analysis
│       ├── diagnose_communities.py      # Community diagnostics
│       ├── inspect_community_detection.py  # Community inspection
│       └── monitor_density.py           # Graph density monitoring
├── rag/                    # RAG collections
│   └── query_chunks.py            # Query video chunks
├── monitoring/             # Monitoring and metrics
│   ├── metrics_summary.py         # Metrics aggregation
│   └── error_summary.py           # Error analysis
└── utilities/              # Utility scripts
    ├── check_data.py              # Check data across databases
    ├── full_cleanup.py            # Full GraphRAG cleanup
    └── seed_indexes.py            # Seed database indexes
```

## Usage

All scripts follow a consistent pattern:

```bash
python scripts/repositories/<domain>/<script>.py [options]
```

### Common Options

- `--limit N`: Limit results to N items
- `--format json|table|csv`: Output format (default: table)
- `--output FILE`: Save output to file
- `--verbose`: Enable verbose logging

### Examples

**Query Scripts**:
```bash
# Query entities with filters
python scripts/repositories/graphrag/query_entities.py --entity-type PERSON --limit 10

# Get GraphRAG statistics
python scripts/repositories/graphrag/stats_summary.py --format json

# Query video chunks
python scripts/repositories/rag/query_chunks.py --video-id VIDEO123 --limit 20
```

**Analysis Scripts**:
```bash
# Analyze graph structure (requires networkx)
python scripts/repositories/graphrag/analysis/analyze_graph_structure.py

# Diagnose community detection issues
python scripts/repositories/graphrag/analysis/diagnose_communities.py

# Monitor graph density
python scripts/repositories/graphrag/analysis/monitor_density.py
```

**Utility Scripts**:
```bash
# Check data across all databases
python scripts/repositories/utilities/check_data.py

# Full GraphRAG cleanup (WARNING: destructive)
python scripts/repositories/utilities/full_cleanup.py

# Seed database indexes
python scripts/repositories/utilities/seed_indexes.py
```

## Script Standards

All scripts should:

- Use `argparse` for argument parsing
- Support multiple output formats (table, JSON, CSV)
- Use `@handle_errors` decorator for error handling
- Load MongoDB URI from `.env` file
- Provide formatted, professional output
- Include usage examples in docstrings

## Dependencies

- `pymongo`: MongoDB client
- `python-dotenv`: Environment variable loading
- `rich`: For formatted table output (optional)
- `core.libraries.error_handling`: Error handling decorators

---

**Created**: November 7, 2025  
**Purpose**: Professional database query tools for GraphRAG pipeline validation and monitoring
