# Plan: Experiment Infrastructure & Community Detection

**Status**: Production Ready - Planning Next Experiments  
**Last Updated**: November 5, 2025  
**Archive Reference**: `documentation/archive/experiment-infrastructure-nov-2025/` (to be created)

---

## 📍 Current State

### What We Built

**Experiment Infrastructure** (Production Ready):

- ✅ JSON-based configuration system
- ✅ CLI support for `--config` flag
- ✅ Experiment tracking in MongoDB
- ✅ Database isolation (read_db/write_db)
- ✅ Comparison script for multi-experiment analysis
- ✅ Three isolated pipelines: `import-youtube-data`, `etl`, `graphrag`

**Community Detection** (Production Ready):

- ✅ Louvain algorithm implementation
- ✅ Configurable resolution parameter
- ✅ 1000× performance improvement (batch updates)
- ✅ Thread-safe execution
- ✅ Algorithm selection (Louvain vs hierarchical_leiden)

### Current Capabilities

**Run Experiments**:

```bash
python app/cli/graphrag.py community-detection \
  --config configs/graphrag/louvain_resolution_1.0.json
```

**Compare Results**:

```bash
python scripts/compare_graphrag_experiments.py \
  mongo_hack graphrag_exp1 graphrag_exp2
```

**Track Progress**:

- `experiment_tracking` collection in MongoDB
- Metadata: config, start/end times, status, stage results

### Gaps Identified

1. **Limited Experiment Configurations**

   - Only 3 Louvain configs created (res: 0.8, 1.0, 1.5)
   - No configs for other stages (extraction, resolution, construction)
   - No multi-stage experiment configs
   - No configs for different model combinations

2. **Incomplete Comparison Metrics**

   - Only basic stats (counts, avg community size)
   - Missing quality metrics (modularity, coverage)
   - Missing cost comparison (tokens, API costs)
   - Missing performance comparison (time, throughput)

3. **No Automated Experiment Workflows**

   - Manual execution of each config
   - No batch experiment runner
   - No automated result collection
   - No statistical significance testing

4. **Missing Experiment Documentation**
   - No experiment log/journal
   - No hypothesis tracking
   - No results interpretation guide
   - No best practices discovered

---

## 🎯 Goals & Scope

### Primary Goals

1. **Expand Experiment Configurations** - Cover all stages, all parameters
2. **Enhance Comparison Tools** - Add quality, cost, performance metrics
3. **Document Experiments** - Track hypotheses, results, learnings
4. **Automate Workflows** - Batch execution, result collection, analysis

### Out of Scope

- Algorithm development (focus on configuration tuning)
- Database migration tools (use existing scripts)
- Real-time experiment monitoring (use logs)

---

## 📋 Implementation Plan

### Phase 1: Configuration Expansion

**Goal**: Create comprehensive experiment configurations for all stages

#### 1.1 Extraction Stage Configurations

**Parameters to Vary**:

- Model: `gpt-4o-mini`, `gpt-4o`, `gpt-4-turbo`
- Temperature: 0.0, 0.1, 0.3
- Max tokens: 4000, 8000, 16000
- Concurrency: 100, 300, 500
- Soft-keep unknown predicates: true/false

**Experiment Configs to Create**:

```json
// configs/graphrag/extraction/baseline.json
{
  "experiment_id": "extraction_baseline",
  "read_db": "mongo_hack",
  "write_db": "exp_extraction_baseline",
  "extraction": {
    "model": "gpt-4o-mini",
    "temperature": 0.1,
    "max_tokens": 4000,
    "concurrency": 300
  }
}

// configs/graphrag/extraction/high_quality.json
{
  "experiment_id": "extraction_high_quality",
  "read_db": "mongo_hack",
  "write_db": "exp_extraction_high_quality",
  "extraction": {
    "model": "gpt-4o",
    "temperature": 0.0,
    "max_tokens": 8000,
    "concurrency": 100
  }
}

// configs/graphrag/extraction/soft_keep_enabled.json
{
  "experiment_id": "extraction_soft_keep",
  "read_db": "mongo_hack",
  "write_db": "exp_extraction_soft_keep",
  "extraction": {
    "model": "gpt-4o-mini",
    "temperature": 0.1,
    "max_tokens": 4000,
    "concurrency": 300,
    "keep_unknown_predicates": true
  }
}
```

**Implementation**:

- [ ] Create `configs/graphrag/extraction/` directory
- [ ] Create 5-7 extraction experiment configs
- [ ] Document each config's hypothesis in README
- [ ] Test each config with --max 10 chunks

#### 1.2 Entity Resolution Configurations

**Parameters to Vary**:

- Similarity threshold: 0.7, 0.8, 0.9
- Model: `gpt-4o-mini`, `gpt-4o`
- Concurrency: 100, 300, 500
- Min cluster size: 2, 5, 10

**Experiment Configs to Create**:

```json
// configs/graphrag/resolution/baseline.json
{
  "experiment_id": "resolution_baseline",
  "read_db": "mongo_hack",
  "write_db": "exp_resolution_baseline",
  "entity_resolution": {
    "similarity_threshold": 0.8,
    "model": "gpt-4o-mini",
    "concurrency": 300,
    "min_cluster_size": 2
  }
}

// configs/graphrag/resolution/strict.json
{
  "experiment_id": "resolution_strict",
  "read_db": "mongo_hack",
  "write_db": "exp_resolution_strict",
  "entity_resolution": {
    "similarity_threshold": 0.9,
    "model": "gpt-4o",
    "concurrency": 100,
    "min_cluster_size": 5
  }
}
```

**Implementation**:

- [ ] Create `configs/graphrag/resolution/` directory
- [ ] Create 4-5 resolution experiment configs
- [ ] Document hypotheses
- [ ] Test each config

#### 1.3 Graph Construction Configurations

**Parameters to Vary**:

- Relationship types enabled: all, semantic_only, structural_only
- Similarity threshold: 0.6, 0.7, 0.8
- Max cross-chunk distance: 3, 5, 10
- Bidirectional: true/false

**Experiment Configs to Create**:

```json
// configs/graphrag/construction/baseline.json
{
  "experiment_id": "construction_baseline",
  "read_db": "mongo_hack",
  "write_db": "exp_construction_baseline",
  "graph_construction": {
    "enable_semantic_similarity": true,
    "enable_cross_chunk": true,
    "enable_bidirectional": true,
    "enable_predicted_links": true,
    "similarity_threshold": 0.7,
    "max_cross_chunk_distance": 5
  }
}

// configs/graphrag/construction/minimal.json
{
  "experiment_id": "construction_minimal",
  "read_db": "mongo_hack",
  "write_db": "exp_construction_minimal",
  "graph_construction": {
    "enable_semantic_similarity": false,
    "enable_cross_chunk": false,
    "enable_bidirectional": true,
    "enable_predicted_links": false
  }
}
```

**Implementation**:

- [ ] Create `configs/graphrag/construction/` directory
- [ ] Create 4-5 construction experiment configs
- [ ] Document hypotheses
- [ ] Test each config

#### 1.4 Community Detection Configurations (Extended)

**Parameters to Vary**:

- Algorithm: louvain, hierarchical_leiden
- Resolution: 0.5, 0.8, 1.0, 1.2, 1.5, 2.0
- Min cluster size: 2, 5, 10, 20
- Max cluster size: 50, 100, 200

**Experiment Configs to Create**:

```json
// configs/graphrag/community/louvain_fine_grain.json
{
  "experiment_id": "community_louvain_fine",
  "read_db": "mongo_hack",
  "write_db": "exp_community_fine",
  "community_detection": {
    "algorithm": "louvain",
    "resolution": 0.5,
    "min_cluster_size": 2,
    "max_cluster_size": 200
  }
}

// configs/graphrag/community/louvain_coarse_grain.json
{
  "experiment_id": "community_louvain_coarse",
  "read_db": "mongo_hack",
  "write_db": "exp_community_coarse",
  "community_detection": {
    "algorithm": "louvain",
    "resolution": 2.0,
    "min_cluster_size": 10,
    "max_cluster_size": 50
  }
}
```

**Implementation**:

- [ ] Expand `configs/graphrag/community/` directory
- [ ] Create 8-10 community detection configs
- [ ] Include hierarchical_leiden configs for comparison
- [ ] Document hypotheses
- [ ] Test each config

#### 1.5 Full Pipeline Configurations

**Goal**: Test complete pipeline variations

**Experiment Configs to Create**:

```json
// configs/graphrag/full_pipeline/high_quality.json
{
  "experiment_id": "pipeline_high_quality",
  "read_db": "mongo_hack",
  "write_db": "exp_pipeline_high_quality",
  "extraction": {
    "model": "gpt-4o",
    "temperature": 0.0,
    "concurrency": 100
  },
  "entity_resolution": {
    "similarity_threshold": 0.9,
    "model": "gpt-4o",
    "concurrency": 100
  },
  "graph_construction": {
    "enable_all": true,
    "similarity_threshold": 0.8
  },
  "community_detection": {
    "algorithm": "louvain",
    "resolution": 1.0
  }
}

// configs/graphrag/full_pipeline/cost_optimized.json
{
  "experiment_id": "pipeline_cost_optimized",
  "read_db": "mongo_hack",
  "write_db": "exp_pipeline_cost_optimized",
  "extraction": {
    "model": "gpt-4o-mini",
    "temperature": 0.1,
    "concurrency": 300,
    "keep_unknown_predicates": false
  },
  "entity_resolution": {
    "similarity_threshold": 0.8,
    "model": "gpt-4o-mini",
    "concurrency": 300
  },
  "graph_construction": {
    "enable_semantic_similarity": true,
    "enable_cross_chunk": false,
    "enable_predicted_links": false
  },
  "community_detection": {
    "algorithm": "louvain",
    "resolution": 1.0
  }
}
```

**Implementation**:

- [ ] Create `configs/graphrag/full_pipeline/` directory
- [ ] Create 5-7 full pipeline configs
- [ ] Document quality vs cost vs speed trade-offs
- [ ] Test each config end-to-end

---

### Phase 2: Enhanced Comparison & Analysis

**Goal**: Comprehensive experiment comparison beyond basic counts

#### 2.1 Extend Comparison Script

**Current Metrics**:

- Entity counts
- Relationship counts
- Community counts
- Average community size

**Add Metrics**:

1. **Quality Metrics**:

   - Modularity score (from logs or recompute)
   - Graph density
   - Average degree
   - Connected components count
   - Clustering coefficient

2. **Cost Metrics**:

   - Total tokens used (input + output)
   - Estimated cost ($)
   - Cost per entity
   - Cost per relationship

3. **Performance Metrics**:

   - Total runtime
   - Throughput (entities/sec, relationships/sec)
   - Stage-wise breakdown
   - TPM/RPM utilization

4. **Coverage Metrics**:
   - Chunks processed
   - Entities per chunk (avg/min/max)
   - Relationships per chunk (avg/min/max)
   - Failed chunks

**Implementation**:

- [ ] Extend `scripts/compare_graphrag_experiments.py`
- [ ] Add `--metrics` flag to select metric groups
- [ ] Add `--format` flag (markdown, json, csv)
- [ ] Add quality calculations
- [ ] Add cost calculations from logs
- [ ] Create visualization outputs (optional)

#### 2.2 Experiment Result Database

**Goal**: Store structured experiment results for analysis

**Schema**:

```python
{
  "experiment_id": str,
  "config": dict,
  "started_at": datetime,
  "completed_at": datetime,
  "metrics": {
    "quality": { "modularity": float, "density": float, ... },
    "cost": { "total_tokens": int, "estimated_cost": float, ... },
    "performance": { "runtime_seconds": float, "throughput": float, ... },
    "coverage": { "chunks_processed": int, "entities_extracted": int, ... }
  },
  "stage_results": {
    "extraction": { ... },
    "resolution": { ... },
    "construction": { ... },
    "community_detection": { ... }
  }
}
```

**Implementation**:

- [ ] Create `experiment_results` collection
- [ ] Update pipeline to store comprehensive results
- [ ] Create query scripts for analysis
- [ ] Add statistical comparison (t-tests, effect sizes)

#### 2.3 Experiment Journal

**Goal**: Track hypotheses, results, learnings

**Structure**:

```markdown
# Experiment Journal - [Month Year]

## Experiment 1: [Name]

**Date**: [Date]
**Hypothesis**: [What we expect]
**Config**: [Link to config file]
**Results**: [What happened]
**Analysis**: [Why it happened]
**Next Steps**: [What to try next]

## Experiment 2: [Name]

...
```

**Implementation**:

- [ ] Create `documentation/experiments/JOURNAL-2025.md`
- [ ] Template for experiment entries
- [ ] Link from experiment configs
- [ ] Update after each experiment

---

### Phase 3: Systematic Experimentation

**Goal**: Run comprehensive experiments to find optimal configurations

#### 3.1 Community Detection Parameter Sweep

**Hypothesis**: Different resolutions produce different community granularities

**Experiments**:

1. Louvain resolution sweep: 0.5, 0.8, 1.0, 1.2, 1.5, 2.0
2. Min/max cluster size variations
3. Hierarchical_leiden for comparison (1-2 configs)

**Success Criteria**:

- Modularity > 0.4
- Community count: 50-200 (sweet spot)
- Average size: 10-30 entities

**Implementation**:

- [ ] Run all Louvain configs
- [ ] Collect metrics
- [ ] Compare with hierarchical_leiden
- [ ] Document optimal parameters in journal
- [ ] Update default config if better found

#### 3.2 Extraction Quality Experiments

**Hypothesis**: Ontology filtering improves quality without excessive cost

**Experiments**:

1. Baseline (no ontology, current extraction)
2. Ontology with soft-keep disabled
3. Ontology with soft-keep enabled (confidence ≥ 0.85)
4. Ontology with strict filtering (drop all unknown)

**Success Criteria**:

- Higher canonical predicate ratio (>70%)
- Lower noisy predicate count (<10%)
- Cost increase <20% vs baseline
- Entity/relationship quality maintained

**Implementation**:

- [ ] Create baseline config (disable ontology)
- [ ] Create ontology configs (soft-keep variations)
- [ ] Run on same dataset (100-1000 chunks)
- [ ] Compare predicate distributions
- [ ] Calculate quality improvement metrics
- [ ] Document trade-offs

#### 3.3 Graph Construction Variations

**Hypothesis**: Different relationship types affect graph quality and community detection

**Experiments**:

1. All relationships enabled (baseline)
2. Semantic similarity only
3. Cross-chunk only
4. Bidirectional only
5. Minimal (co-occurrence + bidirectional only)

**Success Criteria**:

- Graph density: 0.01-0.05 (sweet spot)
- Connected components: <10
- Communities detectible (modularity > 0.3)

**Implementation**:

- [ ] Create relationship type variation configs
- [ ] Run community detection on each
- [ ] Compare graph statistics
- [ ] Identify optimal relationship mix
- [ ] Document findings

#### 3.4 Cost vs Quality Trade-offs

**Hypothesis**: `gpt-4o-mini` with ontology ≈ `gpt-4o` without ontology (quality), but 10× cheaper

**Experiments**:

1. `gpt-4o` without ontology
2. `gpt-4o-mini` with ontology
3. `gpt-4o` with ontology (high quality baseline)
4. `gpt-4o-mini` without ontology (low cost baseline)

**Success Criteria**:

- Identify cost-quality sweet spot
- Document when to use each model
- Create cost prediction model

**Implementation**:

- [ ] Create model variation configs
- [ ] Run on identical datasets
- [ ] Calculate cost per entity/relationship
- [ ] Compare quality metrics
- [ ] Create decision matrix (when to use what)

---

### Phase 4: Automation & Tooling

#### 4.1 Batch Experiment Runner

**Goal**: Run multiple experiments sequentially or in parallel

**Script**: `scripts/run_experiments.py`

```python
"""
Run multiple GraphRAG experiments from config files.

Usage:
    python scripts/run_experiments.py --configs configs/graphrag/extraction/*.json
    python scripts/run_experiments.py --batch configs/graphrag/batch_experiment.json
"""
```

**Features**:

- Load multiple configs
- Sequential or parallel execution
- Progress tracking
- Automatic result collection
- Error handling and retry
- Notifications on completion

**Implementation**:

- [ ] Create `scripts/run_experiments.py`
- [ ] Support config glob patterns
- [ ] Support batch config files
- [ ] Add progress bars
- [ ] Add email/slack notifications (optional)
- [ ] Test with small experiments

#### 4.2 Result Aggregation & Analysis

**Goal**: Automatically aggregate and analyze experiment results

**Script**: `scripts/analyze_experiments.py`

```python
"""
Analyze GraphRAG experiment results and generate reports.

Usage:
    python scripts/analyze_experiments.py --experiment-ids exp1 exp2 exp3
    python scripts/analyze_experiments.py --tag "resolution_sweep"
"""
```

**Features**:

- Load results from experiment_tracking
- Calculate statistical comparisons
- Generate markdown reports
- Identify best performers
- Highlight anomalies

**Implementation**:

- [ ] Create `scripts/analyze_experiments.py`
- [ ] Statistical analysis (mean, std, confidence intervals)
- [ ] Report generation (markdown, charts)
- [ ] Best config identification
- [ ] Anomaly detection

#### 4.3 Experiment Visualization

**Goal**: Visual comparison of experiments

**Tool**: Jupyter notebook or script generating plots

**Visualizations**:

- Community size distributions (histograms)
- Cost vs quality scatter plots
- Performance over time (line charts)
- Modularity comparisons (bar charts)
- Resolution parameter effects (line charts)

**Implementation**:

- [ ] Create `notebooks/experiment_analysis.ipynb` or `scripts/visualize_experiments.py`
- [ ] Use matplotlib/plotly for charts
- [ ] Generate HTML reports with embedded charts
- [ ] Save to `documentation/experiments/results/`

---

### Phase 5: Documentation & Best Practices

#### 5.1 Experiment Workflow Documentation

**Goal**: Complete guide for running and analyzing experiments

**Document**: `documentation/guides/EXPERIMENT-WORKFLOW.md` (update existing)

**Add Sections**:

- Configuration design patterns
- How to design good experiments
- Interpreting results
- Statistical significance
- Cost budgeting
- Troubleshooting common issues

**Implementation**:

- [ ] Review existing guide
- [ ] Add missing sections
- [ ] Include real examples from experiments
- [ ] Add troubleshooting section

#### 5.2 Configuration Best Practices

**Document**: `configs/graphrag/README.md` (update existing)

**Add Sections**:

- Parameter selection guide
- Trade-offs documentation
- Recommended starting points
- Cost estimation formulas
- Performance tuning guide

**Implementation**:

- [ ] Review existing README
- [ ] Document lessons learned
- [ ] Add parameter selection decision trees
- [ ] Include cost/performance tables

#### 5.3 Experiment Results Archive

**Goal**: Preserve experiment results for future reference

**Structure**:

```
documentation/experiments/
├── README.md (index of all experiments)
├── JOURNAL-2025.md (ongoing journal)
├── results/
│   ├── 2025-11/
│   │   ├── louvain_resolution_sweep.md
│   │   ├── extraction_quality_comparison.md
│   │   └── cost_vs_quality_analysis.md
│   └── charts/
│       ├── resolution_vs_modularity.png
│       └── cost_vs_quality.png
└── configs/
    └── (symlink to ../../configs/graphrag/)
```

**Implementation**:

- [ ] Create `documentation/experiments/` directory
- [ ] Create README with experiment index
- [ ] Create JOURNAL template
- [ ] Set up results/ structure
- [ ] Link from main documentation

---

## 🔍 Identified Gaps & Solutions

### Gap 1: No Validation Against Ground Truth

**Problem**: We can compare experiments but don't know which is "best" without ground truth

**Solution**:

- [ ] Create small ground-truth dataset (100 chunks, manually verified)
- [ ] Metrics: precision, recall, F1 for entities/relationships
- [ ] Compare against ground truth
- [ ] Document in `documentation/experiments/ground_truth.md`

### Gap 2: No Cost Prediction

**Problem**: Can't estimate cost before running experiments

**Solution**:

- [ ] Create cost estimation script
- [ ] Based on: model, chunk count, avg chunk size, concurrency
- [ ] Formula: `cost = (chunks * avg_tokens * model_price) / 1M`
- [ ] Add `--dry-run --estimate-cost` flag to CLI

### Gap 3: No Experiment Reproducibility Validation

**Problem**: Can't verify experiments are reproducible

**Solution**:

- [ ] Add random seed configuration
- [ ] Document seed in experiment_tracking
- [ ] Add `--reproduce` flag to rerun with same seed
- [ ] Validate results match (within tolerance)

### Gap 4: No Multi-Stage Experiment Coordination

**Problem**: Can't easily run experiments that vary multiple stages

**Solution**:

- [ ] Support full pipeline configs (already started)
- [ ] Add stage dependencies in config
- [ ] Add `--stages` flag to run subset
- [ ] Document in experiment workflow guide

---

## 📊 Success Criteria

### Phase 1 Complete When:

- ✅ 20-30 experiment configs created
- ✅ All stages covered
- ✅ Hypotheses documented
- ✅ All configs tested

### Phase 2 Complete When:

- ✅ Comparison script has quality + cost + performance metrics
- ✅ Results stored in structured format
- ✅ Experiment journal established
- ✅ Visualization tools created

### Phase 3 Complete When:

- ✅ Community detection parameters optimized
- ✅ Extraction quality validated
- ✅ Graph construction variations tested
- ✅ Cost vs quality trade-offs documented

### Phase 4 Complete When:

- ✅ Batch experiment runner working
- ✅ Result aggregation automated
- ✅ Visualization pipeline established

### Phase 5 Complete When:

- ✅ All documentation updated
- ✅ Best practices documented
- ✅ Experiment results archived
- ✅ Reproducibility validated

---

## ⏱️ Time Estimates

**Phase 1**: 3-4 hours (config creation + testing)  
**Phase 2**: 4-5 hours (tool enhancement + database schema)  
**Phase 3**: 10-15 hours (experiments + analysis)  
**Phase 4**: 3-4 hours (automation scripts)  
**Phase 5**: 2-3 hours (documentation)

**Total**: 22-31 hours

---

## 🚀 Immediate Next Steps

1. **Review this plan** - Confirm scope and priorities
2. **Archive old docs** - Execute `DOCUMENTATION-ARCHIVING-PLAN.md`
3. **Create config structure** - Set up `configs/graphrag/` subdirectories
4. **Start Phase 1** - Create first batch of experiment configs
5. **Document as we go** - Update experiment journal

---

## 📚 References

**Archive**: `documentation/archive/experiment-infrastructure-nov-2025/` (post-archiving)  
**Current Docs**:

- `documentation/guides/EXPERIMENT-WORKFLOW.md`
- `configs/graphrag/README.md`
- `documentation/technical/COMMUNITY-DETECTION.md`

**Code**:

- `app/cli/graphrag.py` - CLI interface
- `business/pipelines/graphrag.py` - Pipeline orchestration
- `scripts/compare_graphrag_experiments.py` - Comparison tool
- `business/agents/graphrag/community_detection.py` - Louvain implementation

**Tests**: N/A (infrastructure, manual validation)

---

**Status**: Ready for review and execution  
**Priority**: High - Foundation for all quality improvements
