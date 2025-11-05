# Pipeline Restructuring Plan - Multi-Experiment Architecture

**Date**: November 4, 2025  
**Vision**: Isolate data import from processing to enable parallel experiments  
**Goal**: Run multiple GraphRAG configurations in parallel for comparative analysis

---

## 🎯 Vision: Experimental Pipeline Architecture

### Current Problem

- Single monolithic pipeline (ingest → clean → chunk → enrich → embed → graphrag)
- Can't easily test different configurations
- Can't compare results side-by-side
- Data import tied to processing

### Proposed Solution

**3 Independent Pipelines** with **1 source → N experiments** pattern:

```
┌─────────────────────────────────────────────────────────────┐
│ Pipeline 1: import-youtube-data                             │
│ ┌─────────┐    ┌──────────────────┐                       │
│ │ ingest  │ -> │ backfill_trans.  │ -> raw_videos (shared) │
│ └─────────┘    └──────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
                              ↓ (read once, use many times)
┌─────────────────────────────────────────────────────────────┐
│ Pipeline 2: etl (run multiple times with diff configs)     │
│                                                             │
│ Experiment A (config_a.json -> experiment_a_db):           │
│ raw_videos -> clean -> chunk -> enrich -> embed -> chunks_a│
│                                                             │
│ Experiment B (config_b.json -> experiment_b_db):           │
│ raw_videos -> clean -> chunk -> enrich -> embed -> chunks_b│
│                                                             │
│ Experiment C (config_c.json -> experiment_c_db):           │
│ raw_videos -> clean -> chunk -> enrich -> embed -> chunks_c│
└─────────────────────────────────────────────────────────────┘
                              ↓ (multiple chunk DBs)
┌─────────────────────────────────────────────────────────────┐
│ Pipeline 3: graphrag (run multiple times per ETL result)   │
│                                                             │
│ Experiment A1 (chunks_a + config_1 -> graphrag_a1_db):     │
│ chunks_a -> extraction -> resolution -> construction ->     │
│             communities -> graphrag_a1                      │
│                                                             │
│ Experiment A2 (chunks_a + config_2 -> graphrag_a2_db):     │
│ chunks_a -> extraction -> resolution -> construction ->     │
│             communities -> graphrag_a2                      │
│                                                             │
│ Experiment B1 (chunks_b + config_1 -> graphrag_b1_db):     │
│ chunks_b -> extraction -> resolution -> construction ->     │
│             communities -> graphrag_b1                      │
└─────────────────────────────────────────────────────────────┘
```

**Result**: Matrix of experiments for comparative analysis

---

## 📋 Pipeline 1: import-youtube-data

### Purpose

Import raw YouTube data ONCE, use for ALL experiments

### Stages

1. **ingest** - Fetch YouTube metadata and initial data
2. **backfill_transcripts** - Get transcripts from YouTube API

### Configuration

```json
{
  "pipeline": "import-youtube-data",
  "read_db": "mongo_hack", // Source of video IDs if continuing
  "write_db": "mongo_hack", // Always writes to shared DB
  "collections": {
    "output": "raw_videos" // Shared collection
  },
  "stages": {
    "ingest": {
      "max_videos": null, // All videos
      "source": "youtube_api"
    },
    "backfill_transcripts": {
      "max_videos": null,
      "skip_existing": true
    }
  }
}
```

### Output

- **Database**: `mongo_hack` (shared, read-only for experiments)
- **Collection**: `raw_videos` (source for all ETL experiments)

### Run Command

```bash
python -m app.cli.youtube_import \
  --config configs/import/default.json \
  --log-file logs/import/import_run_$(date +%Y%m%d_%H%M%S).log
```

---

## 📋 Pipeline 2: etl (Multi-Experiment)

### Purpose

Process raw videos with DIFFERENT configurations to create DIFFERENT chunk datasets

### Stages

1. **clean** - Transcript cleaning with configurable aggressiveness
2. **chunk** - Chunking with different sizes/strategies
3. **enrich** - Entity/concept extraction (optional: different prompts)
4. **embed** - Generate embeddings (optional: different models)

### Experiment Configurations

#### Experiment A: Conservative (High Quality, Lower Recall)

```json
{
  "experiment_id": "conservative_20241104",
  "read_db": "mongo_hack",
  "read_collection": "raw_videos",
  "write_db": "experiment_conservative",
  "write_collection": "video_chunks",
  "stages": {
    "clean": {
      "aggressiveness": "low", // Minimal cleaning
      "preserve_technical_terms": true
    },
    "chunk": {
      "chunk_size": 1500, // Larger chunks
      "chunk_overlap": 200,
      "strategy": "sentence_boundary"
    },
    "enrich": {
      "model": "gpt-4o", // Better model
      "temperature": 0.0, // More deterministic
      "concurrency": 10
    },
    "embed": {
      "model": "voyage-2",
      "batch_size": 100
    }
  }
}
```

#### Experiment B: Aggressive (Higher Recall, More Chunks)

```json
{
  "experiment_id": "aggressive_20241104",
  "read_db": "mongo_hack",
  "read_collection": "raw_videos",
  "write_db": "experiment_aggressive",
  "write_collection": "video_chunks",
  "stages": {
    "clean": {
      "aggressiveness": "high", // Aggressive cleaning
      "remove_filler_words": true
    },
    "chunk": {
      "chunk_size": 800, // Smaller chunks (more granular)
      "chunk_overlap": 100,
      "strategy": "semantic_boundary"
    },
    "enrich": {
      "model": "gpt-4o-mini", // Faster model
      "temperature": 0.2,
      "concurrency": 15
    },
    "embed": {
      "model": "voyage-2",
      "batch_size": 200
    }
  }
}
```

#### Experiment C: Baseline (Fast, Standard)

```json
{
  "experiment_id": "baseline_20241104",
  "read_db": "mongo_hack",
  "read_collection": "raw_videos",
  "write_db": "experiment_baseline",
  "write_collection": "video_chunks",
  "stages": {
    "clean": {
      "aggressiveness": "medium"
    },
    "chunk": {
      "chunk_size": 1000, // Standard
      "chunk_overlap": 150
    },
    "enrich": {
      "model": "gpt-4o-mini",
      "temperature": 0.1,
      "concurrency": 10
    },
    "embed": {
      "model": "voyage-2",
      "batch_size": 100
    }
  }
}
```

### Run Commands

```bash
# Experiment A
python -m app.cli.etl \
  --config configs/etl/conservative.json \
  --log-file logs/etl/conservative_run.log

# Experiment B
python -m app.cli.etl \
  --config configs/etl/aggressive.json \
  --log-file logs/etl/aggressive_run.log

# Experiment C
python -m app.cli.etl \
  --config configs/etl/baseline.json \
  --log-file logs/etl/baseline_run.log

# Can run in parallel!
```

### Output

- **experiment_conservative**: ~8,000-10,000 chunks (larger, fewer)
- **experiment_aggressive**: ~18,000-20,000 chunks (smaller, more)
- **experiment_baseline**: ~13,000 chunks (standard)

---

## 📋 Pipeline 3: graphrag (Multi-Experiment x Multi-Config)

### Purpose

Run GraphRAG with DIFFERENT configurations on EACH chunk dataset

### Matrix of Experiments

```
           │ Config 1        │ Config 2        │ Config 3
           │ (Louvain)       │ (Leiden)        │ (Label Prop)
───────────┼─────────────────┼─────────────────┼──────────────
Chunks A   │ graphrag_a1     │ graphrag_a2     │ graphrag_a3
(conserv.) │ (A+Louvain)     │ (A+Leiden)      │ (A+Label)
───────────┼─────────────────┼─────────────────┼──────────────
Chunks B   │ graphrag_b1     │ graphrag_b2     │ graphrag_b3
(aggress.) │ (B+Louvain)     │ (B+Leiden)      │ (B+Label)
───────────┼─────────────────┼─────────────────┼──────────────
Chunks C   │ graphrag_c1     │ graphrag_c2     │ graphrag_c3
(baseline) │ (C+Louvain)     │ (C+Leiden)      │ (C+Label)
```

**Total**: 9 GraphRAG experiments (3 chunk sets × 3 configs)

### GraphRAG Configurations

#### Config 1: Louvain Community Detection

```json
{
  "experiment_id": "louvain_20241104",
  "read_db": "experiment_conservative", // Or aggressive, baseline
  "read_collection": "video_chunks",
  "write_db": "graphrag_conservative_louvain",
  "stages": {
    "extraction": {
      "model": "gpt-4o-mini",
      "temperature": 0.1,
      "concurrency": 10
    },
    "entity_resolution": {
      "similarity_threshold": 0.85,
      "concurrency": 5
    },
    "graph_construction": {
      "enable_finalize": true,
      "post_processing": [
        "co_occurrence",
        "semantic",
        "cross_chunk",
        "bidirectional",
        "predicted"
      ]
    },
    "community_detection": {
      "algorithm": "louvain", // PRIMARY DIFFERENCE
      "min_cluster_size": 2,
      "max_cluster_size": 50
    }
  }
}
```

#### Config 2: Hierarchical Leiden

```json
{
  "experiment_id": "leiden_20241104",
  "read_db": "experiment_conservative",
  "write_db": "graphrag_conservative_leiden",
  "stages": {
    "community_detection": {
      "algorithm": "hierarchical_leiden", // Test if works now
      "min_cluster_size": 2,
      "max_cluster_size": 50
    }
    // ... other settings same as config 1
  }
}
```

#### Config 3: Label Propagation

```json
{
  "experiment_id": "label_prop_20241104",
  "read_db": "experiment_conservative",
  "write_db": "graphrag_conservative_labelprop",
  "stages": {
    "community_detection": {
      "algorithm": "label_propagation", // Alternative
      "min_cluster_size": 2
    }
    // ... other settings same
  }
}
```

### Run Commands

```bash
# Conservative chunks + Louvain
python -m app.cli.graphrag \
  --config configs/graphrag/louvain.json \
  --source-db experiment_conservative \
  --target-db graphrag_conservative_louvain \
  --log-file logs/graphrag/conservative_louvain.log

# Aggressive chunks + Louvain
python -m app.cli.graphrag \
  --config configs/graphrag/louvain.json \
  --source-db experiment_aggressive \
  --target-db graphrag_aggressive_louvain \
  --log-file logs/graphrag/aggressive_louvain.log

# ... (9 total combinations)
```

---

## 📊 Comparative Analysis Framework

### Metrics to Compare

**ETL Experiments** (3 variants):

- Chunk count
- Average chunk size
- Entity count per chunk
- Relationship count per chunk
- Processing time
- Enrichment quality scores

**GraphRAG Experiments** (9 variants):

- Total entities resolved
- Total relationships
- Graph density
- Community count
- Average community size
- Multi-entity community %
- Query performance
- Retrieval quality

### Analysis Queries

```python
# Compare chunk strategies
SELECT experiment,
       COUNT(*) as chunk_count,
       AVG(length) as avg_length,
       AVG(entity_count) as avg_entities
FROM experiments
GROUP BY experiment

# Compare community algorithms
SELECT experiment,
       algorithm,
       COUNT(*) as community_count,
       AVG(entity_count) as avg_size,
       SUM(CASE WHEN entity_count > 1 THEN 1 ELSE 0 END) / COUNT(*) as multi_entity_pct
FROM communities
GROUP BY experiment, algorithm
```

---

## 🏗️ Implementation Plan

### Phase 1: Pipeline Separation (4-6 hours)

#### Step 1.1: Create Pipeline 1 - import-youtube-data (1 hour)

**New File**: `business/pipelines/youtube_import.py`

```python
class YouTubeImportPipeline:
    """
    Pipeline for importing raw YouTube data.

    Stages:
    1. ingest - Fetch video metadata
    2. backfill_transcripts - Get transcripts

    Output: raw_videos collection (shared source)
    """

    def __init__(self, config):
        self.config = config
        self.stages = [
            IngestStage(),
            BackfillTranscriptsStage()
        ]

    def run(self):
        # Always writes to mongo_hack.raw_videos
        for stage in self.stages:
            stage.run(...)
```

**New CLI**: `app/cli/youtube_import.py`

**Time**: 1 hour

---

#### Step 1.2: Create Pipeline 2 - etl (2 hours)

**New File**: `business/pipelines/etl.py`

```python
class ETLPipeline:
    """
    Pipeline for ETL processing with experiment support.

    Reads from: raw_videos (shared)
    Writes to: Configurable DB (per experiment)

    Stages:
    1. clean - Transcript cleaning
    2. chunk - Text chunking
    3. enrich - Entity/concept extraction
    4. embed - Generate embeddings

    Output: video_chunks collection in experiment DB
    """

    def __init__(self, experiment_config):
        self.experiment_id = experiment_config['experiment_id']
        self.read_db = experiment_config['read_db']  # mongo_hack
        self.write_db = experiment_config['write_db']  # experiment_X
        self.stages = [
            CleanStage(config=experiment_config['stages']['clean']),
            ChunkStage(config=experiment_config['stages']['chunk']),
            EnrichStage(config=experiment_config['stages']['enrich']),
            EmbedStage(config=experiment_config['stages']['embed'])
        ]

    def run(self):
        # Read from shared raw_videos
        # Write to experiment-specific DB
        for stage in self.stages:
            stage.run(
                read_db=self.read_db,
                write_db=self.write_db
            )
```

**New CLI**: `app/cli/etl.py`

**Time**: 2 hours

---

#### Step 1.3: Refactor Pipeline 3 - graphrag (1 hour)

**Modify**: `business/pipelines/graphrag.py`

**Changes**:

- Remove ingest/clean/chunk/enrich/embed stages
- Focus ONLY on GraphRAG stages
- Support experiment configuration
- Enable algorithm selection for community detection

```python
class GraphRAGPipeline:
    """
    Pipeline for GraphRAG processing with experiment support.

    Reads from: video_chunks (from ETL experiment)
    Writes to: Configurable DB (per GraphRAG experiment)

    Stages:
    1. graph_extraction
    2. entity_resolution
    3. graph_construction
    4. community_detection (configurable algorithm)

    Output: entities, relations, communities in experiment DB
    """

    def __init__(self, experiment_config):
        self.experiment_id = experiment_config['experiment_id']
        self.source_db = experiment_config['source_db']  // ETL output
        self.target_db = experiment_config['target_db']  // GraphRAG output
        self.algorithm = experiment_config['stages']['community_detection']['algorithm']

    def run(self):
        # Read chunks from ETL experiment DB
        # Write GraphRAG results to separate DB
        ...
```

**Time**: 1 hour

---

### Phase 2: Configuration System (2-3 hours)

#### Step 2.1: Config File Structure (30 min)

**Directory Structure**:

```
configs/
├── import/
│   └── default.json
├── etl/
│   ├── conservative.json
│   ├── aggressive.json
│   └── baseline.json
└── graphrag/
    ├── louvain.json
    ├── leiden.json
    └── label_propagation.json
```

#### Step 2.2: Config Loader (1 hour)

**New File**: `core/config/experiment_config.py`

```python
class ExperimentConfig:
    """Configuration for multi-experiment architecture."""

    @staticmethod
    def load(config_file: str) -> Dict:
        """Load experiment configuration from JSON."""
        with open(config_file) as f:
            return json.load(f)

    @staticmethod
    def validate(config: Dict) -> bool:
        """Validate experiment configuration."""
        required = ['experiment_id', 'read_db', 'write_db', 'stages']
        return all(k in config for k in required)
```

#### Step 2.3: Experiment Manager (1 hour)

**New File**: `business/experiments/manager.py`

```python
class ExperimentManager:
    """Manage multiple experiments and comparisons."""

    def list_experiments(self):
        """List all experiment databases."""
        # Scan for experiment_* databases
        ...

    def compare_experiments(self, exp_ids: List[str]):
        """Compare results across experiments."""
        # Generate comparison metrics
        ...

    def export_comparison(self, output_file: str):
        """Export comparison to markdown/JSON."""
        ...
```

---

### Phase 3: Community Detection Algorithms (2-3 hours)

#### Step 3.1: Algorithm Abstraction (1 hour)

**Modify**: `business/agents/graphrag/community_detection.py`

```python
class CommunityDetectionAgent:
    def __init__(self, algorithm='louvain', **kwargs):
        self.algorithm = algorithm
        # ... existing init

    def detect_communities(self, entities, relationships):
        # Build graph
        G = self._create_networkx_graph(entities, relationships)

        # Select algorithm
        if self.algorithm == 'louvain':
            return self._detect_with_louvain(G)
        elif self.algorithm == 'hierarchical_leiden':
            return self._detect_with_leiden(G)
        elif self.algorithm == 'label_propagation':
            return self._detect_with_label_propagation(G)
        else:
            return self._fallback_community_detection(G)

    def _detect_with_louvain(self, G):
        """Louvain modularity-based detection."""
        import networkx.algorithms.community as nx_comm
        communities = list(nx_comm.greedy_modularity_communities(G))
        return self._format_communities(communities)

    def _detect_with_leiden(self, G):
        """Hierarchical Leiden (original)."""
        from graspologic.partition import hierarchical_leiden
        communities = hierarchical_leiden(G, max_cluster_size=self.max_cluster_size)
        return self._format_communities(communities)

    def _detect_with_label_propagation(self, G):
        """Label propagation algorithm."""
        import networkx.algorithms.community as nx_comm
        communities = list(nx_comm.label_propagation_communities(G))
        return self._format_communities(communities)

    def _format_communities(self, raw_communities):
        """Convert algorithm output to standard format."""
        # Standardize different algorithm outputs
        ...
```

**Time**: 1 hour

#### Step 3.2: Test Each Algorithm (1-2 hours)

**Create**: `scripts/test_community_algorithms.py`

```python
"""
Test all 3 community detection algorithms on same graph.

Generates comparison report:
- Louvain: 6 communities (sizes: 22, 20, 15, 12, 9, 6)
- Leiden: 88 communities (sizes: all 1)
- Label Prop: 8 communities (sizes: ...)
"""
```

**Time**: 1-2 hours

---

### Phase 4: Experiment Tracking (2 hours)

#### Step 4.1: Experiment Metadata Collection (1 hour)

**New Collection**: `experiment_metadata`

```json
{
  "experiment_id": "conservative_louvain_20241104",
  "type": "graphrag",
  "source_experiment": "conservative_20241104",
  "configuration": {
    "etl": {
      /* etl config */
    },
    "graphrag": {
      /* graphrag config */
    }
  },
  "results": {
    "chunks_processed": 9500,
    "entities_extracted": 25000,
    "relationships": 150000,
    "communities": 45,
    "multi_entity_communities": 42,
    "avg_community_size": 8.5
  },
  "performance": {
    "extraction_time": "2.5 hours",
    "total_time": "8 hours",
    "cost_usd": 45.5
  },
  "created_at": "2024-11-04T13:00:00Z"
}
```

#### Step 4.2: Comparison Dashboard (1 hour)

**Script**: `scripts/compare_experiments.py`

```python
"""
Generate comparative analysis across experiments.

Output:
- Markdown report
- Charts (matplotlib)
- CSV data for analysis
"""
```

---

## 📊 Analysis & Article Content

### Article 1: "Optimizing Chunk Strategies for RAG"

**Data**: ETL experiments (Conservative vs Aggressive vs Baseline)

**Metrics**:

- Retrieval accuracy by chunk size
- Query response quality
- Processing time vs quality tradeoff
- Entity extraction quality

**Conclusion**: Which chunk strategy performs best?

---

### Article 2: "Community Detection Algorithms for Knowledge Graphs"

**Data**: GraphRAG experiments (Louvain vs Leiden vs Label Propagation)

**Metrics**:

- Community quality (coherence, modularity)
- Multi-entity community percentage
- Query performance (community-based retrieval)
- Computational cost

**Conclusion**: Which algorithm works best for YouTube content graphs?

---

### Article 3: "Full RAG Pipeline Optimization"

**Data**: Full matrix (9 experiments)

**Metrics**:

- End-to-end quality
- Best combination (chunk strategy + community algorithm)
- Cost-benefit analysis
- Production recommendations

**Conclusion**: Optimal configuration for YouTube RAG system

---

## 🎯 Implementation Timeline

### Week 1: Pipeline Restructuring (8-10 hours)

- **Day 1 AM** (4 hours): Create 3 pipelines + CLIs
- **Day 1 PM** (4 hours): Config system + community algorithms
- **Day 2** (2 hours): Testing & validation

### Week 2: Run Experiments (20-30 hours of compute)

- **Day 3**: Run ETL experiments (3 parallel, ~6 hours each)
- **Day 4-5**: Run GraphRAG experiments (9 total, ~8 hours each with current speed)

### Week 3: Analysis & Articles (10-15 hours)

- **Day 6**: Data analysis & comparison
- **Day 7**: Article writing
- **Day 8**: Review & publish

**Total**: 18-25 hours of work + 20-30 hours compute time

---

## 📋 Immediate Next Steps (After Current Runs)

### Step 1: Validate Current Work (today)

- ✅ Wait for extraction concurrent to finish
- ✅ Validate results in validation_db
- ✅ Validate graph_construction finalize()
- ✅ Test community_detection

### Step 2: Implement Pipeline Restructuring (1-2 days)

- Create 3 separate pipelines
- Implement config system
- Add community detection algorithms
- Test with small dataset

### Step 3: Run Experiment Matrix (3-4 days of compute)

- 3 ETL experiments (parallel)
- 9 GraphRAG experiments (can parallelize)
- Collect all metrics

### Step 4: Analysis & Articles (2-3 days)

- Generate comparison reports
- Create visualizations
- Write articles
- Document findings

---

## 💡 Key Benefits

### Scientific Rigor

- Controlled experiments
- Reproducible results
- Comparative analysis
- Evidence-based conclusions

### Flexibility

- Easy to add new experiments
- Can re-run with different configs
- Isolated failures (one exp doesn't affect others)
- Parallel execution

### Content Generation

- Multiple articles from same work
- Data-driven insights
- Impressive technical content
- Community value

---

## ⚠️ Considerations

### Resource Requirements

- **Disk Space**: 9 databases × ~10GB each = ~90GB
- **Compute Time**: ~30 hours total (can parallelize to ~10 hours)
- **API Costs**: 9 full runs × $50 each = ~$450
- **Management**: Tracking 9 experiments

### Mitigation

- Start with 2×2 matrix (4 experiments) instead of 3×3
- Use smaller dataset for validation
- Archive old experiments
- Careful cost monitoring

---

## 🎯 Recommended Approach

### Minimal Viable Experiment (MVP)

**2 ETL Variants**:

- Conservative (large chunks)
- Aggressive (small chunks)

**2 GraphRAG Variants**:

- Louvain community detection
- Hierarchical Leiden

**Total**: 4 experiments (2×2 matrix)

**Benefits**:

- Proves the architecture works
- Still enables comparison
- Lower cost (~$200 vs $450)
- Faster to implement & run

### Then Expand

- Add more chunk strategies
- Add more community algorithms
- Add more variations

---

## 📝 Deliverables

### Code

- 3 independent pipelines
- Config-driven experiment system
- Multiple community detection algorithms
- Comparison tools

### Documentation

- Architecture diagrams
- Configuration guide
- Experiment runbook
- Analysis methodology

### Articles

- "Optimizing RAG Chunk Strategies"
- "Community Detection for Knowledge Graphs"
- "Building Production RAG Systems"

---

## ✅ Approval Checklist

**Before implementing, confirm**:

- [ ] MVP (2×2) or Full (3×3) matrix?
- [ ] Disk space available (~50-100GB)?
- [ ] API budget approved (~$200-450)?
- [ ] Timeline acceptable (2-3 weeks)?
- [ ] Priority over other refactoring?

---

**Plan Status**: ✅ Detailed and ready  
**Awaiting**: Your approval to proceed (after current validations complete)  
**Estimated**: 2-3 weeks for full implementation + experiments + articles
