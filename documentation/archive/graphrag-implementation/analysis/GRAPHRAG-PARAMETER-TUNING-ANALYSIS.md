# hierarchical_leiden Parameter Tuning Analysis

## Current Implementation

### Code Analysis

**Location**: `agents/community_detection_agent.py`, lines 84-90

```python
communities = hierarchical_leiden(
    G,
    max_cluster_size=self.max_cluster_size,
)
```

**Current Parameters Used**:

- ✅ `max_cluster_size`: 10 (default)
- ❌ `resolution_parameter`: Defined in config but **not passed** to algorithm
- ❌ `max_iterations`: Defined in config but **not passed** to algorithm
- ❌ `max_levels`: Defined in config but **not passed** to algorithm

### Configuration Available

**Location**: `config/graphrag_config.py`, `CommunityDetectionConfig`

```python
max_cluster_size: int = 10
min_cluster_size: int = 2  # ⚠️ Not used by hierarchical_leiden
resolution_parameter: float = 1.0  # ⚠️ Not passed to algorithm
max_iterations: int = 100  # ⚠️ Not passed to algorithm
max_levels: int = 3  # ⚠️ Not passed to algorithm
```

## graspologic hierarchical_leiden API Investigation

### What We Know

1. **Current Behavior**: Only `max_cluster_size` is accepted
2. **Previous Errors**: `resolution_parameter` and `max_iterations` caused errors
3. **Documentation Gap**: No clear documentation on what parameters are actually supported

### Expected Parameters (Standard Leiden Algorithm)

Based on standard community detection algorithms, `hierarchical_leiden` should support:

1. **`max_cluster_size`** ✅ Currently used

   - **Purpose**: Maximum nodes per cluster
   - **Effect**: Larger values = larger communities
   - **Current**: 10
   - **Impact**: With sparse graphs, this may not help much

2. **`resolution_parameter`** ❓ Not supported (caused errors)

   - **Purpose**: Controls community granularity
   - **Effect**: Higher = smaller communities, Lower = larger communities
   - **Expected Range**: 0.1 - 2.0
   - **Default**: 1.0
   - **Why Not Working**: API may not expose this parameter

3. **`max_iterations`** ❓ Not supported (caused errors)

   - **Purpose**: Maximum algorithm iterations
   - **Effect**: More iterations = better convergence
   - **Current Config**: 100
   - **Why Not Working**: Algorithm may have fixed convergence criteria

4. **`max_levels`** ❓ Not investigated
   - **Purpose**: Maximum hierarchical levels
   - **Effect**: Controls depth of hierarchy
   - **Current Config**: 3
   - **Status**: Unknown if supported

## Parameter Tuning Strategy

### Strategy 1: Adjust `max_cluster_size` Only

**Current**: `max_cluster_size=10`

**Test Scenarios**:

1. **Increase `max_cluster_size`** (e.g., 20, 50, 100)

   - **Hypothesis**: Larger max size may allow more nodes to cluster together
   - **Risk**: May create too-large, incoherent communities
   - **Test**: `max_cluster_size=50` → Check if communities have 2+ entities

2. **Decrease `max_cluster_size`** (e.g., 5)
   - **Hypothesis**: Smaller max may force different clustering behavior
   - **Risk**: Will still create single-node communities for isolated nodes
   - **Test**: Unlikely to help with sparse graphs

**Expected Outcome**:

- **Limited impact** on sparse graphs with isolated nodes
- Isolated nodes will still get their own communities regardless of `max_cluster_size`

### Strategy 2: Pre-filter Isolated Nodes

**Approach**: Remove isolated nodes before running `hierarchical_leiden`

**Implementation**:

```python
# Remove isolated nodes (degree = 0)
isolated_nodes = [n for n in G.nodes() if G.degree(n) == 0]
G_filtered = G.copy()
G_filtered.remove_nodes_from(isolated_nodes)

# Run on filtered graph
communities = hierarchical_leiden(G_filtered, max_cluster_size=self.max_cluster_size)

# Handle isolated nodes separately (store in "orphans" collection or ignore)
```

**Pros**:

- ✅ Only processes connected nodes
- ✅ Reduces single-node communities
- ✅ Improves community quality

**Cons**:

- ⚠️ Loses 36 isolated entities (need alternative handling)
- ⚠️ Requires separate storage/processing for isolated entities

**Expected Outcome**:

- **Significant improvement** - from 90 communities → ~5-10 real communities
- Isolated nodes handled separately

### Strategy 3: Post-filter Single-Node Communities

**Approach**: Filter results after `hierarchical_leiden` runs

**Implementation**:

```python
communities = hierarchical_leiden(G, max_cluster_size=self.max_cluster_size)

# Filter based on min_cluster_size
filtered_communities = []
for comm in communities:
    if hasattr(comm, "nodes"):
        node_count = len(comm.nodes)
    else:
        node_count = 1  # Single node

    if node_count >= self.min_cluster_size:
        filtered_communities.append(comm)
```

**Pros**:

- ✅ Simple to implement
- ✅ Respects `min_cluster_size` config
- ✅ Keeps isolated entities (can handle separately)

**Cons**:

- ⚠️ Still processes isolated nodes (wasteful)
- ⚠️ Wastes algorithm time on nodes that will be filtered

**Expected Outcome**:

- **Moderate improvement** - filters out single-node communities
- From 90 communities → ~5-10 real communities

### Strategy 4: Use Alternative Algorithm

**Options**:

1. **Louvain Algorithm** (via NetworkX)

   ```python
   import networkx.algorithms.community as nx_comm
   communities = nx_comm.louvain_communities(G, resolution=1.0, seed=42)
   ```

   - **Pros**: Supports `resolution` parameter, well-documented
   - **Cons**: Not hierarchical, may need post-processing

2. **Leiden Algorithm** (via `igraph` or `python-igraph`)

   ```python
   import igraph as ig
   g = ig.Graph.from_networkx(G)
   communities = g.community_leiden(resolution_parameter=1.0)
   ```

   - **Pros**: Full parameter control, supports resolution
   - **Cons**: Requires additional dependency (`python-igraph`)

3. **Connected Components** (Current fallback)
   - Already implemented in `_fallback_community_detection()`
   - **Pros**: Simple, guaranteed to find connected groups
   - **Cons**: May create too-large communities, no optimization

### Strategy 5: Multi-Stage Approach

**Combine Strategies**:

1. **Pre-filter** isolated nodes (Strategy 2)
2. **Run `hierarchical_leiden`** on connected graph (Strategy 1)
3. **Post-filter** small communities (Strategy 3)
4. **Handle isolated nodes** separately (orphan collection)

**Expected Outcome**:

- **Best results** - combines benefits of all strategies
- Most complex but most flexible

## Recommended Testing Plan

### Phase 1: Understand Current Behavior

**Test 1**: Current state baseline

```python
max_cluster_size = 10
# Expected: 90 communities (mostly single-node)
```

**Test 2**: Increase max_cluster_size

```python
max_cluster_size = 50
# Check: Does this reduce number of communities?
# Check: Do communities get larger?
```

**Test 3**: Increase max_cluster_size dramatically

```python
max_cluster_size = 200  # Larger than node count
# Check: Does this force all nodes into fewer communities?
```

### Phase 2: Pre-filtering Test

**Test 4**: Remove isolated nodes

```python
# Remove nodes with degree 0
# Expected: ~70 nodes (106 - 36 isolated)
# Check: How many communities detected?
```

### Phase 3: Post-filtering Test

**Test 5**: Filter single-node communities

```python
min_cluster_size = 2
# Filter communities with < 2 nodes
# Expected: ~5-10 real communities
```

### Phase 4: Combined Approach

**Test 6**: Pre-filter + Post-filter

```python
# Remove isolated nodes → Run algorithm → Filter small communities
# Expected: Best balance of community quality and coverage
```

## Parameter Impact Analysis

### `max_cluster_size` Impact on Sparse Graphs

**Key Insight**: With sparse graphs, `max_cluster_size` has **limited impact** on single-node communities.

**Why**:

- Isolated nodes (degree=0) cannot be merged into communities
- Weakly connected nodes may still form single-node communities
- Algorithm respects graph structure, not just max size

**Conclusion**: Parameter tuning alone won't solve single-node community problem.

### Expected Results Table

| Strategy         | Communities Detected | Single-Node Communities | Multi-Node Communities | Quality   |
| ---------------- | -------------------- | ----------------------- | ---------------------- | --------- |
| Current (max=10) | 90                   | 90                      | 0                      | ❌ Poor   |
| max=50           | ~90                  | ~85                     | ~5                     | ⚠️ Low    |
| max=200          | ~90                  | ~85                     | ~5                     | ⚠️ Low    |
| Pre-filter       | ~5-10                | 0                       | 5-10                   | ✅ Good   |
| Post-filter      | ~5-10                | 0                       | 5-10                   | ✅ Good   |
| Combined         | ~5-10                | 0                       | 5-10                   | ✅✅ Best |

## Recommendations

### Immediate Action

1. **Post-filter Implementation** (Strategy 3)

   - Quick win, respects existing config
   - Low risk, high impact
   - Filters single-node communities based on `min_cluster_size`

2. **Pre-filter Implementation** (Strategy 2)
   - Better algorithm efficiency
   - Cleaner communities
   - Requires isolated entity handling

### Future Enhancement

3. **Alternative Algorithm Investigation**
   - Test Louvain algorithm with `resolution` parameter
   - Compare results with `hierarchical_leiden`
   - May provide better control over community granularity

### Configuration Changes

**Recommended Config Values**:

```python
max_cluster_size: int = 50  # Increase to allow larger communities
min_cluster_size: int = 2   # ✅ Use for filtering
# Note: resolution_parameter, max_iterations not supported by current API
```

## Conclusion

**Key Finding**: `hierarchical_leiden` parameter tuning has **limited effectiveness** for sparse graphs with many isolated nodes. The algorithm correctly identifies that isolated nodes cannot be grouped, so parameter changes won't merge them.

**Best Approach**: **Post-filtering** combined with **pre-filtering** provides the most practical solution:

- Pre-filter: Remove isolated nodes before algorithm (efficiency)
- Post-filter: Remove single-node communities after algorithm (safety)
- Handle isolated entities separately (data preservation)

**Next Step**: Implement filtering strategies, then test with graph structure improvements (B) to see combined impact.
