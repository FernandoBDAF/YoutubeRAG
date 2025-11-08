# GraphRAG Query Scripts

Comprehensive suite of query scripts for analyzing GraphRAG pipeline data at every stage boundary. These scripts leverage the observability infrastructure (transformation logs + intermediate data collections) to enable deep analysis of entity resolution, relationship construction, and community detection.

## 📋 Overview

**Purpose**: Query and analyze GraphRAG data to answer "why" questions about transformations.

**Data Sources**:
- **Transformation Logs** (Achievement 0.1): Every transformation event with reasons
- **Intermediate Data Collections** (Achievement 0.2): Data snapshots at stage boundaries

**Use Cases**:
- Understand entity resolution decisions
- Analyze relationship construction
- Compare pipeline runs
- Identify quality issues
- Optimize configurations

---

## 📁 Scripts by Category

### Shared Infrastructure

**`query_utils.py`** - Common utilities for all query scripts
- MongoDB connection handling
- Output formatters (table, JSON, CSV)
- Common filters and helpers

### Extraction Queries (2 scripts)

**`query_raw_entities.py`** - Query entities before resolution
- Filter by type, confidence, chunk
- Show extraction details
- Use case: "What entities were extracted from chunk X?"

**`compare_extraction_runs.py`** - Compare extraction across runs
- Compare entity counts and type distributions
- Identify extraction quality differences
- Use case: "Did the new prompt extract more entities?"

### Resolution Queries (3 scripts)

**`query_resolution_decisions.py`** - Query merge decisions
- Show which entities merged and why
- Filter by merge reason (fuzzy/embedding/context)
- Use case: "Why did entity A merge with entity B?"

**`compare_before_after_resolution.py`** - Compare raw vs. resolved
- Calculate merge rate and type distribution changes
- Measure resolution effectiveness
- Use case: "How effective is entity resolution?"

**`find_resolution_errors.py`** - Identify potential errors
- Find high-confidence merges with low similarity
- Detect potential false positives
- Use case: "What resolution errors should I investigate?"

### Construction Queries (3 scripts)

**`query_raw_relationships.py`** - Query relationships before post-processing
- Filter by type, entities
- Show extraction details
- Use case: "What relationships were extracted?"

**`compare_before_after_construction.py`** - Compare raw vs. final
- Show post-processing impact
- Count contributions by method (co-occurrence, semantic, etc.)
- Use case: "How much did post-processing add?"

**`query_graph_evolution.py`** - Track graph metrics
- Show density evolution during construction
- Track relationship additions by method
- Use case: "How did the graph grow?"

### Detection Queries (2 scripts)

**`query_pre_detection_graph.py`** - Analyze graph before detection
- Show graph structure and connectivity
- Degree distribution analysis
- Use case: "What did the graph look like before communities?"

**`compare_detection_algorithms.py`** - Compare algorithms
- Compare Leiden vs. Louvain vs. Infomap
- Show modularity and community metrics
- Use case: "Which algorithm works best for my data?"

---

## 🚀 Quick Start

### Prerequisites

```bash
# MongoDB connection configured in .env
MONGODB_URI=mongodb://localhost:27017
DB_NAME=mongo_hack

# Python dependencies
pip install pymongo python-dotenv
```

### Basic Usage

```bash
# Query raw entities from a pipeline run
python query_raw_entities.py --trace-id abc123

# Compare resolution effectiveness
python compare_before_after_resolution.py --trace-id abc123

# Find potential resolution errors
python find_resolution_errors.py --trace-id abc123 --format csv --output errors.csv
```

---

## 📖 Common Patterns

### Pattern 1: Analyze a Single Pipeline Run

```bash
# Get trace_id from recent run
TRACE_ID="your-trace-id-here"

# 1. Check extraction quality
python query_raw_entities.py --trace-id $TRACE_ID --limit 50

# 2. Check resolution effectiveness
python compare_before_after_resolution.py --trace-id $TRACE_ID

# 3. Check for resolution errors
python find_resolution_errors.py --trace-id $TRACE_ID

# 4. Check construction impact
python compare_before_after_construction.py --trace-id $TRACE_ID

# 5. Check graph structure
python query_pre_detection_graph.py --trace-id $TRACE_ID
```

### Pattern 2: Compare Two Pipeline Runs

```bash
# Compare extraction
python compare_extraction_runs.py --trace-ids run1 run2

# Compare detection algorithms
python compare_detection_algorithms.py --trace-ids run1 run2
```

### Pattern 3: Investigate Specific Entities

```bash
# Find raw entities for a specific entity
python query_raw_entities.py --trace-id $TRACE_ID --entity-type PERSON --limit 100

# Check merge decisions for those entities
python query_resolution_decisions.py --trace-id $TRACE_ID --merge-reason fuzzy

# Find relationships involving those entities
python query_raw_relationships.py --trace-id $TRACE_ID --source-entity "Einstein"
```

### Pattern 4: Export for Analysis

```bash
# Export all data for external analysis
python query_raw_entities.py --trace-id $TRACE_ID --format json --output entities.json
python query_resolution_decisions.py --trace-id $TRACE_ID --format json --output merges.json
python query_raw_relationships.py --trace-id $TRACE_ID --format json --output relationships.json

# Import into Jupyter notebook or spreadsheet for deeper analysis
```

---

## 🎯 Use Case Examples

### Use Case 1: Understanding Entity Resolution

**Question**: "Why are some entities merging incorrectly?"

**Approach**:
```bash
# 1. Find suspicious merges
python find_resolution_errors.py --trace-id $TRACE_ID --confidence-threshold 0.9 --similarity-threshold 0.7

# 2. Examine specific merge decisions
python query_resolution_decisions.py --trace-id $TRACE_ID --merge-reason fuzzy --limit 50

# 3. Compare before/after to see overall impact
python compare_before_after_resolution.py --trace-id $TRACE_ID
```

**What You Learn**:
- Which entities are merging incorrectly
- What confidence scores and similarity thresholds to adjust
- Whether to disable certain merge strategies

### Use Case 2: Optimizing Post-Processing

**Question**: "Which post-processing methods add the most value?"

**Approach**:
```bash
# 1. Check overall impact
python compare_before_after_construction.py --trace-id $TRACE_ID

# 2. Track evolution
python query_graph_evolution.py --trace-id $TRACE_ID --output evolution.json

# 3. Analyze final graph
python query_pre_detection_graph.py --trace-id $TRACE_ID
```

**What You Learn**:
- Which methods add most relationships (co-occurrence, semantic, etc.)
- How density evolves during construction
- Whether post-processing is over-connecting or under-connecting

### Use Case 3: Comparing Extraction Prompts

**Question**: "Did the new extraction prompt improve quality?"

**Approach**:
```bash
# Run pipeline with old prompt (trace_id: old_run)
# Run pipeline with new prompt (trace_id: new_run)

# Compare extraction
python compare_extraction_runs.py --trace-ids old_run new_run

# Compare resolution (did better extraction lead to better resolution?)
python compare_before_after_resolution.py --trace-id old_run
python compare_before_after_resolution.py --trace-id new_run
```

**What You Learn**:
- Entity count differences
- Type distribution changes
- Whether new prompt extracts more or higher-quality entities

### Use Case 4: Choosing Detection Algorithm

**Question**: "Should I use Leiden or Louvain?"

**Approach**:
```bash
# Run with Leiden (trace_id: leiden_run)
# Run with Louvain (trace_id: louvain_run)

# Compare
python compare_detection_algorithms.py --trace-ids leiden_run louvain_run
```

**What You Learn**:
- Which algorithm has higher modularity
- Community size distributions
- Singleton rates

---

## 📊 Output Formats

All scripts support three output formats:

### Table Format (Default)

```bash
python query_raw_entities.py --trace-id abc123 --format table
```

Human-readable table with aligned columns. Best for terminal viewing.

### JSON Format

```bash
python query_raw_entities.py --trace-id abc123 --format json --output entities.json
```

Structured JSON with metadata. Best for programmatic analysis or import into tools.

### CSV Format

```bash
python query_raw_entities.py --trace-id abc123 --format csv --output entities.csv
```

Comma-separated values. Best for spreadsheet analysis (Excel, Google Sheets).

---

## 🔧 Common Arguments

All scripts support these common arguments:

| Argument | Description | Example |
|----------|-------------|---------|
| `--trace-id` | Filter by pipeline run | `--trace-id abc123` |
| `--format` | Output format | `--format json` |
| `--output` | Output file path | `--output results.csv` |
| `--limit` | Maximum results | `--limit 50` |

---

## 🎓 Best Practices

### 1. Always Use Trace IDs

```bash
# Good: Specific pipeline run
python query_raw_entities.py --trace-id abc123

# Avoid: All runs (slow, confusing)
python query_raw_entities.py
```

### 2. Start with Summaries

```bash
# Start with comparison scripts to get overview
python compare_before_after_resolution.py --trace-id $TRACE_ID
python compare_before_after_construction.py --trace-id $TRACE_ID

# Then drill down with specific queries
python query_resolution_decisions.py --trace-id $TRACE_ID
```

### 3. Export for Deep Analysis

```bash
# Export to JSON for Jupyter notebooks
python query_raw_entities.py --trace-id $TRACE_ID --format json --output entities.json

# Export to CSV for spreadsheets
python find_resolution_errors.py --trace-id $TRACE_ID --format csv --output errors.csv
```

### 4. Use Filters to Focus

```bash
# Filter by entity type
python query_raw_entities.py --trace-id $TRACE_ID --entity-type PERSON

# Filter by confidence
python query_resolution_decisions.py --trace-id $TRACE_ID --min-confidence 0.9

# Filter by merge reason
python query_resolution_decisions.py --trace-id $TRACE_ID --merge-reason fuzzy
```

---

## 🐛 Troubleshooting

### No Results Found

**Problem**: Script returns "No data found"

**Solutions**:
1. Verify trace_id exists: Check MongoDB `transformation_logs` or `entities_raw` collections
2. Check intermediate data is enabled: `GRAPHRAG_SAVE_INTERMEDIATE_DATA=true` in .env
3. Verify pipeline completed: Check `graphrag_runs` collection for run status

### Connection Errors

**Problem**: "MONGODB_URI not found"

**Solution**: Ensure `.env` file has `MONGODB_URI` and `DB_NAME` configured

### Slow Queries

**Problem**: Queries take too long

**Solutions**:
1. Use `--limit` to reduce result count
2. Add indexes to MongoDB collections (trace_id, timestamp)
3. Filter by specific criteria (entity_type, merge_reason, etc.)

---

## 📚 MongoDB Collections Reference

### From Achievement 0.1 (Transformation Logging)

**`transformation_logs`** - All transformation events
- `trace_id`: Pipeline run identifier
- `transformation_type`: entity_merge, relationship_create, relationship_augment, community_form, entity_cluster
- `details`: Transformation-specific data
- `timestamp`: When transformation occurred

### From Achievement 0.2 (Intermediate Data)

**`entities_raw`** - Entities before resolution
- `trace_id`: Pipeline run identifier
- `entity_id`: Unique entity identifier
- `name`: Entity name
- `entity_type`: Entity type (PERSON, ORGANIZATION, etc.)
- `confidence`: Extraction confidence score
- `chunk_id`: Source chunk

**`entities_resolved`** - Entities after resolution
- Same fields as `entities_raw` but after merging

**`relations_raw`** - Relationships before post-processing
- `trace_id`: Pipeline run identifier
- `source_entity_id`, `target_entity_id`: Connected entities
- `predicate`: Relationship type
- `confidence`: Extraction confidence

**`relations_final`** - Relationships after post-processing
- Same fields as `relations_raw` plus augmented relationships

**`graph_pre_detection`** - Graph snapshot before community detection
- `trace_id`: Pipeline run identifier
- `node_count`, `edge_count`: Graph size
- `density`, `average_degree`: Graph metrics
- `degree_distribution`: Connectivity distribution

---

## 🔗 Related Documentation

- **Achievement 0.1**: `documentation/guides/GRAPHRAG-TRANSFORMATION-LOGGING.md`
- **Achievement 0.2**: `documentation/guides/INTERMEDIATE-DATA-ANALYSIS.md`
- **Pipeline Architecture**: `business/pipelines/graphrag.py`
- **Stages**: `business/stages/graphrag/`

---

## 📝 Contributing

When adding new query scripts:

1. Follow the existing pattern (use `query_utils.py`)
2. Support all three output formats (table, JSON, CSV)
3. Add comprehensive `--help` text with examples
4. Document use cases in this README
5. Test with real pipeline data

---

**Created**: 2025-11-09  
**Achievement**: 0.3 (Stage Boundary Query Scripts)  
**Dependencies**: Achievement 0.1 (Transformation Logging), Achievement 0.2 (Intermediate Data Collections)


