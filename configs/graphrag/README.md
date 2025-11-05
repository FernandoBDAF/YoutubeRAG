# GraphRAG Experiment Configurations

This directory contains JSON configuration files for GraphRAG experiments.

## Configuration File Format

```json
{
  "experiment_id": "unique_experiment_identifier",
  "read_db": "source_database_name",
  "write_db": "target_database_name",
  "concurrency": 300,
  "community_detection": {
    "algorithm": "louvain",
    "resolution": 1.0,
    "min_cluster_size": 2,
    "max_cluster_size": 50
  }
}
```

## Available Configurations

### `louvain_default.json`

- **Purpose**: Baseline Louvain with standard settings
- **Algorithm**: Louvain
- **Resolution**: 1.0 (default)
- **Use case**: Standard community detection

### `louvain_resolution_08.json`

- **Purpose**: Test fewer, larger communities
- **Algorithm**: Louvain
- **Resolution**: 0.8 (lower → fewer communities)
- **Use case**: High-level topic clustering

### `louvain_resolution_15.json`

- **Purpose**: Test more, smaller communities
- **Algorithm**: Louvain
- **Resolution**: 1.5 (higher → more communities)
- **Use case**: Fine-grained topic clustering

## Usage

### Run with config file:

```bash
python -m app.cli.graphrag \
  --config configs/graphrag/louvain_resolution_08.json \
  --stage community_detection
```

### Override config file with CLI flags:

```bash
python -m app.cli.graphrag \
  --config configs/graphrag/louvain_default.json \
  --write-db graphrag_custom_experiment \
  --stage community_detection
```

**CLI flags always override config file values.**

## Creating New Experiments

1. Copy an existing config file
2. Change `experiment_id` to unique identifier
3. Update `write_db` to avoid conflicts
4. Modify algorithm/parameters as needed
5. Run and compare results

## Comparison

Compare multiple experiments:

```bash
python scripts/compare_graphrag_experiments.py \
  mongo_hack graphrag_exp_louvain_res08 graphrag_exp_louvain_res15
```
