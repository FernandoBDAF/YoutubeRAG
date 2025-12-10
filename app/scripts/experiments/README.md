# Experiments

Scripts for running and comparing GraphRAG experiments.

## Directory Structure

```
experiments/
├── run_experiments.py      # Experiment runner
├── compare_experiments.py  # Experiment comparison tool
├── configs/                # Experiment configuration files
│   └── *.json
└── results/                # Experiment results (gitignored)
    └── *.json
```

## Scripts

### `run_experiments.py`
Runs GraphRAG experiments with different configurations.

**Usage:**
```bash
# Run with default config
python -m experiments.run_experiments

# Run with specific config
python -m experiments.run_experiments --config experiments/configs/high_quality.json

# Run with custom parameters
python -m experiments.run_experiments --max-docs 100 --extraction-model gpt-4
```

### `compare_experiments.py`
Compares results from multiple experiment runs.

**Usage:**
```bash
# Compare two experiments
python -m experiments.compare_experiments --run1 <id1> --run2 <id2>

# Generate comparison report
python -m experiments.compare_experiments --all --output report.md
```

## Configuration Files

Example configuration (`configs/baseline.json`):
```json
{
  "name": "baseline",
  "description": "Baseline experiment configuration",
  "extraction": {
    "model": "gpt-4o-mini",
    "max_entities_per_chunk": 20
  },
  "resolution": {
    "threshold": 0.85,
    "algorithm": "greedy"
  },
  "construction": {
    "min_edge_weight": 0.5
  }
}
```

## Results

Experiment results are stored in `results/` with the format:
```
experiment_<name>_<timestamp>.json
```

Each result file contains:
- Experiment configuration
- Execution timestamps
- Quality metrics (entity count, relationship density, etc.)
- Performance metrics (time per stage, API calls, etc.)

## Environment Variables

- `MONGODB_URI` - MongoDB connection string
- `MONGODB_DB` - Database for experiments
- `OPENAI_API_KEY` - OpenAI API key for LLM operations

