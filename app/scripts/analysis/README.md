# Analysis

Scripts for analyzing graph quality and developing ontologies.

## Directory Structure

```
analysis/
├── quality/              # Quality analysis scripts
│   ├── analyze_entity_types.py         # Entity type distribution
│   ├── analyze_predicate_distribution.py  # Relationship predicate analysis
│   └── compare_extraction_quality.py   # Quality comparison across runs
├── ontology/             # Ontology development scripts
│   ├── derive_ontology.py              # Automatic ontology derivation
│   └── build_predicate_map.py          # Predicate mapping tool
└── reports/              # Generated analysis reports (gitignored)
    └── *.md, *.json
```

## Quality Analysis

### `analyze_entity_types.py`
Analyzes the distribution of entity types in the knowledge graph.

**Usage:**
```bash
python -m analysis.quality.analyze_entity_types --db <database>
```

**Output:** Entity type distribution report with:
- Count per type
- Percentage distribution
- Anomaly detection (unexpected types)

### `analyze_predicate_distribution.py`
Analyzes relationship predicates in the graph.

**Usage:**
```bash
python -m analysis.quality.analyze_predicate_distribution --db <database>
```

**Output:** Predicate distribution showing:
- Most common predicates
- Predicate co-occurrence patterns
- Potential duplicates (similar predicates)

### `compare_extraction_quality.py`
Compares extraction quality across different runs or configurations.

**Usage:**
```bash
python -m analysis.quality.compare_extraction_quality --run1 <id> --run2 <id>
```

**Output:** Comparison report including:
- Entity count differences
- Relationship density changes
- Quality score deltas

## Ontology Development

### `derive_ontology.py`
Automatically derives an ontology from existing graph data.

**Usage:**
```bash
python -m analysis.ontology.derive_ontology --db <database> --output ontology.json
```

**Output:** Derived ontology with:
- Entity type hierarchy
- Relationship type definitions
- Property schemas

### `build_predicate_map.py`
Creates a mapping of predicates for normalization.

**Usage:**
```bash
python -m analysis.ontology.build_predicate_map --db <database>
```

**Output:** Predicate mapping file for:
- Synonym grouping
- Canonical form selection
- Relationship standardization

## Reports

Analysis reports are generated in `reports/` directory:
- `entity_type_distribution_<timestamp>.md`
- `predicate_distribution_<timestamp>.md`
- `extraction_quality_<timestamp>.json`

## Environment Variables

- `MONGODB_URI` - MongoDB connection string
- `MONGODB_DB` - Database to analyze

