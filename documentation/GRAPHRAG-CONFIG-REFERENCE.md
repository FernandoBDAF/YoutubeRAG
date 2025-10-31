# GraphRAG Configuration Reference

## Quick Reference

Essential environment variables for GraphRAG pipeline configuration.

---

## Graph Construction Post-Processing

### Semantic Similarity

```bash
# Minimum cosine similarity to create semantic similarity relationships
GRAPHRAG_SIMILARITY_THRESHOLD=0.92
```

**Range**: 0.0-1.0  
**Default**: 0.92  
**Recommended**: 0.90-0.95  
**Impact**: Higher = fewer, higher-quality similarity links

---

### Cross-Chunk Relationships

```bash
# Number of nearby chunks to connect (chunk proximity window)
# If NOT set, uses ADAPTIVE window based on video length (RECOMMENDED)
# GRAPHRAG_CROSS_CHUNK_WINDOW=3
```

**Adaptive Window (Default - Recommended)** ✅:

If `GRAPHRAG_CROSS_CHUNK_WINDOW` is NOT set (recommended), window size adapts per video:

| Video Length | Window | Rationale                               |
| ------------ | ------ | --------------------------------------- |
| ≤10 chunks   | 1      | Very short videos: only adjacent chunks |
| 11-25 chunks | 2      | Short videos                            |
| 26-50 chunks | 3      | Medium videos                           |
| >50 chunks   | 5      | Long videos                             |

**Manual Override**:

If `GRAPHRAG_CROSS_CHUNK_WINDOW` is set, uses that value for ALL videos:

**Range**: 0-20  
**Impact**:

- 0 = disabled
- 1-2 = very local context
- 3 = balanced for medium videos
- 5 = balanced for long videos
- 10+ = risks over-connection

**Recommendation**:

- ✅ **Leave unset** to use adaptive window (best for mixed video lengths)
- Set to specific value only if all videos are similar length

---

### Density Safeguards

```bash
# Maximum graph density before stopping post-processing
GRAPHRAG_MAX_DENSITY=0.3
```

**Range**: 0.0-1.0  
**Default**: 0.3  
**Recommended**: 0.2-0.4  
**Impact**:

- Lower = stops earlier, prevents over-connection
- Higher = allows denser graphs, more relationships

---

### Link Prediction

```bash
# Enable or disable link prediction
GRAPHRAG_ENABLE_LINK_PREDICTION=true

# Minimum confidence for predicted links
GRAPHRAG_LINK_PREDICTION_THRESHOLD=0.65

# Maximum predicted links per entity
GRAPHRAG_MAX_PREDICTIONS_PER_ENTITY=5
```

**GRAPHRAG_ENABLE_LINK_PREDICTION**:

- `true` = enabled (default)
- `false` = disabled (faster, fewer relationships)

**GRAPHRAG_LINK_PREDICTION_THRESHOLD**:

- Range: 0.0-1.0
- Default: 0.65
- Recommended: 0.60-0.75

**GRAPHRAG_MAX_PREDICTIONS_PER_ENTITY**:

- Range: 1-20
- Default: 5
- Recommended: 3-10

---

## Community Detection

### Cluster Size

```bash
# Maximum entities per community
GRAPHRAG_MAX_CLUSTER_SIZE=50

# Minimum entities per community (filters single-entity communities)
GRAPHRAG_MIN_CLUSTER_SIZE=2
```

**Note**: These are in `config/graphrag_config.py` as defaults, can be overridden via environment variables.

---

## Complete Configuration Template

Add to `.env`:

```bash
# ============================================================================
# GraphRAG Pipeline Configuration
# ============================================================================

# --- Post-Processing ---

# Semantic Similarity
GRAPHRAG_SIMILARITY_THRESHOLD=0.92          # Min cosine similarity (0.90-0.95)

# Cross-Chunk Relationships (ADAPTIVE by default - leave commented out)
# GRAPHRAG_CROSS_CHUNK_WINDOW=3             # Override adaptive window (0=disabled, 1-5=manual)

# Density Safeguards
GRAPHRAG_MAX_DENSITY=0.3                    # Max graph density (0.2-0.4)

# Link Prediction
GRAPHRAG_ENABLE_LINK_PREDICTION=true        # Enable/disable
GRAPHRAG_LINK_PREDICTION_THRESHOLD=0.65     # Min confidence (0.60-0.75)
GRAPHRAG_MAX_PREDICTIONS_PER_ENTITY=5       # Max per entity (3-10)

# --- Community Detection ---

# Cluster sizes (set in config/graphrag_config.py)
# Can override via environment if needed
# GRAPHRAG_MAX_CLUSTER_SIZE=50
# GRAPHRAG_MIN_CLUSTER_SIZE=2
```

---

## Tuning Guide

### For Sparse Data (Few Entities/Relationships)

```bash
GRAPHRAG_SIMILARITY_THRESHOLD=0.88          # Lower to get more links
GRAPHRAG_CROSS_CHUNK_WINDOW=7               # Wider window
GRAPHRAG_MAX_DENSITY=0.4                    # Allow denser graphs
GRAPHRAG_ENABLE_LINK_PREDICTION=true        # Use prediction to fill gaps
```

### For Dense Data (Many Entities/Relationships)

```bash
GRAPHRAG_SIMILARITY_THRESHOLD=0.95          # Stricter similarity
GRAPHRAG_CROSS_CHUNK_WINDOW=3               # Narrower window
GRAPHRAG_MAX_DENSITY=0.2                    # Stop early
GRAPHRAG_ENABLE_LINK_PREDICTION=false       # Skip prediction
```

### For Fast Testing

```bash
GRAPHRAG_SIMILARITY_THRESHOLD=0.95          # Fewer similarity links
GRAPHRAG_CROSS_CHUNK_WINDOW=3               # Fewer cross-chunk
GRAPHRAG_MAX_DENSITY=0.15                   # Stop very early
GRAPHRAG_ENABLE_LINK_PREDICTION=false       # Skip expensive prediction
```

### For Quality Over Speed

```bash
GRAPHRAG_SIMILARITY_THRESHOLD=0.92          # Balanced
GRAPHRAG_CROSS_CHUNK_WINDOW=5               # Balanced
GRAPHRAG_MAX_DENSITY=0.3                    # Standard limit
GRAPHRAG_ENABLE_LINK_PREDICTION=true        # Use all features
```

---

## Monitoring

### Key Metrics to Watch

During pipeline execution, monitor these log messages:

```
✓ Added X co-occurrence relationships (density: 0.0123)
✓ Added Y semantic similarity relationships (threshold: 0.92, density: 0.0456)
✓ Added Z cross-chunk relationships (density: 0.1234)
```

**Watch for**:

- Density increasing gradually (good)
- Density jumping suddenly (bad - may need to reduce window/threshold)
- Early termination messages (density exceeded max)

### Warning Signs

🔴 **Stop and reconfigure if you see**:

- `Graph density (0.XXX) reached maximum (0.3)` before all steps complete
- Cross-chunk adding >1000 relationships for <100 chunks
- Semantic similarity adding >500 relationships
- Any density > 0.5 at any point

---

## Defaults Summary

| Parameter                           | Default  | Rationale                                          |
| ----------------------------------- | -------- | -------------------------------------------------- |
| GRAPHRAG_SIMILARITY_THRESHOLD       | 0.92     | Balance between coverage and precision             |
| GRAPHRAG_CROSS_CHUNK_WINDOW         | Adaptive | Auto-adjusts to video length (best for mixed data) |
| GRAPHRAG_MAX_DENSITY                | 0.3      | Prevents over-connection while allowing rich graph |
| GRAPHRAG_ENABLE_LINK_PREDICTION     | true     | Useful but can be disabled for speed               |
| GRAPHRAG_LINK_PREDICTION_THRESHOLD  | 0.65     | Moderate confidence for predictions                |
| GRAPHRAG_MAX_PREDICTIONS_PER_ENTITY | 5        | Limits complexity                                  |

**Note**: Adaptive window is the recommended default. It automatically uses window=1 for videos ≤10 chunks, window=2 for 11-25 chunks, window=3 for 26-50 chunks, and window=5 for >50 chunks.

These defaults are tuned based on the 12 and 25-chunk test analyses and are production-ready for datasets with mixed video lengths.
