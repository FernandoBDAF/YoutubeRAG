# Community Detection Algorithms - Comprehensive Guide

**Purpose**: Guide for selecting and implementing community detection algorithms in GraphRAG  
**Context**: Knowledge graph community detection for semantic clustering  
**Date**: November 2025

---

## Overview

Community detection algorithms identify clusters (communities) of nodes in a graph that are **more densely connected internally** than with the rest of the graph. This guide reviews common algorithms, especially those supporting **hierarchical community detection** (multi-level clustering).

---

## Algorithm Comparison Summary

| Algorithm             | Speed  | Scale    | Hierarchical | Quality    | Deterministic | Best For                       |
| --------------------- | ------ | -------- | ------------ | ---------- | ------------- | ------------------------------ |
| **Leiden**            | ⚡⚡⚡ | Millions | ✅ Yes       | ⭐⭐⭐⭐⭐ | ✅ Yes        | **Large graphs (RECOMMENDED)** |
| **Louvain**           | ⚡⚡⚡ | Millions | ✅ Yes       | ⭐⭐⭐⭐   | ⚠️ Mostly     | Large graphs, proven           |
| **Infomap**           | ⚡⚡   | 100k's   | ✅ Yes       | ⭐⭐⭐⭐   | ⚠️ Mostly     | Flow/directed graphs           |
| **Walktrap**          | ⚡     | 10k's    | ✅ Yes       | ⭐⭐⭐     | ✅ Yes        | Medium graphs, hierarchy       |
| **Girvan-Newman**     | ⚡     | <5k      | ✅ Yes       | ⭐⭐⭐     | ✅ Yes        | Small graphs only              |
| **Label Propagation** | ⚡⚡⚡ | Millions | ❌ No        | ⭐⭐       | ❌ No         | Quick first pass               |
| **Spectral**          | ⚡⚡   | 10k's    | ✅ Yes       | ⭐⭐⭐     | ✅ Yes        | Medium graphs                  |
| **Spinglass**         | ⚡     | <10k     | ❌ No        | ⭐⭐       | ❌ No         | Not recommended                |

---

## Detailed Algorithm Analysis

---

### 1. Leiden Algorithm ⭐ **RECOMMENDED**

**Type**: Modularity optimization (improved Louvain)  
**Hierarchical**: Yes (via recursive application)  
**Scale**: Millions of nodes

#### Description

The **Leiden algorithm** is an improved version of Louvain that addresses disconnected communities and quality issues. It:

- Optimizes modularity via node moves and community aggregation
- Adds **refinement phase** to ensure communities are well-connected
- Splits disconnected or sparse communities
- Randomizes node movements to escape local optima

#### ✅ Pros

1. **Best Quality**: Produces better-quality communities than Louvain
2. **Connected Communities**: Guarantees each community is internally contiguous
3. **Fast**: Faster than Louvain due to efficient node update rules
4. **Scalable**: Handles millions of nodes/edges
5. **Hierarchical**: Produces multiple levels via recursive application
6. **Higher Modularity**: Often achieves better modularity scores
7. **Mitigates Resolution Limit**: Finds finer-grained structure
8. **Deterministic**: Stable results

#### ⚠️ Cons

1. **Newer**: Introduced in 2019 (NetworkX 3.5+ support)
2. **Memory**: Slightly more memory-intensive during refinement
3. **Resolution Parameter**: Still sensitive to resolution tuning
4. **Sparse Graphs**: Can produce trivial communities on extremely sparse graphs

#### 🎯 Best For

- **GraphRAG pipelines** ✅
- Large knowledge graphs
- When quality matters
- When hierarchical structure needed

#### References

- Traag et al., "From Louvain to Leiden" (2019) - Scientific Reports 9, 5233
- Microsoft GraphRAG Documentation - Hierarchical Leiden

---

### 2. Louvain Algorithm ⭐⭐⭐⭐ **PROVEN ALTERNATIVE**

**Type**: Modularity optimization (greedy)  
**Hierarchical**: Yes (multi-level aggregation)  
**Scale**: Millions of nodes

#### Description

Popular **greedy modularity optimization** method that:

- Maximizes modularity (dense intra-community edges vs inter-community edges)
- Works in two alternating phases:
  1. Nodes move between communities to improve modularity
  2. Communities aggregate into super-nodes (creates hierarchy)
- Produces implicit multi-level hierarchy from fine to coarse

#### ✅ Pros

1. **Fast**: One of the fastest algorithms, scales to millions of nodes
2. **Proven**: Best-performing in comparative studies
3. **Automatic**: Determines number of communities automatically
4. **High Modularity**: Usually yields high-modularity partitions
5. **Hierarchical**: Multi-level analysis via aggregation phases
6. **Widely Used**: Go-to choice for many applications
7. **Simple**: Easy to understand and implement

#### ⚠️ Cons

1. **Local Optima**: Can get stuck in local optima
2. **Resolution Limit**: May fail to separate small communities in very large graphs
3. **Disconnected Communities**: Can produce poorly connected communities
4. **Non-Deterministic**: Results may vary slightly with node order/seed
5. **Arbitrary Merges**: Greedy merging can be suboptimal

#### 🎯 Best For

- Large graphs where speed matters
- When Leiden is not available
- Proven, production-ready solutions
- Initial clustering or baseline

#### References

- Nature Communications - Comparative algorithm studies
- Microsoft GraphRAG - Alternative to hierarchical_leiden

---

### 3. Infomap Algorithm ⭐⭐⭐ **FLOW-BASED**

**Type**: Information-theoretic (random walks)  
**Hierarchical**: Yes (via Map Equation)  
**Scale**: Hundreds of thousands of nodes

#### Description

**Information-theoretic approach** using random walks:

- Optimizes the **Map Equation** (compression of walker's trajectory)
- Finds communities where random walker stays longer
- Minimizes description length of walker's path
- Groups nodes with many intra-cluster paths

#### ✅ Pros

1. **Flow Structure**: Captures real flow structures in networks
2. **Stable**: Robust and consistent results
3. **Directed/Weighted**: Handles asymmetric and weighted relationships well
4. **Different Perspective**: Sometimes captures structure modularity methods miss
5. **Hierarchical**: Two-level solution with sub-communities
6. **Efficient**: Reasonable efficiency (100k's of nodes)

#### ⚠️ Cons

1. **Slower**: Slower than Louvain/Leiden on very large graphs
2. **Memory**: More memory for dense graphs
3. **Non-Deterministic**: Relies on random seed
4. **Random Graphs**: May return single community on graphs without structure
5. **Complex**: More complex math and implementation

#### 🎯 Best For

- Directed graphs
- Flow/transportation networks
- Citation networks, web graphs
- Validation/comparison with modularity methods

---

### 4. Walktrap Algorithm ⭐⭐⭐ **HIERARCHICAL**

**Type**: Random walks + agglomerative clustering  
**Hierarchical**: Yes (full dendrogram)  
**Scale**: Thousands of nodes

#### Description

**Agglomerative hierarchical** method based on random walks:

- Short random walks (3-5 steps) compute node distances
- Communities with similar random-walk patterns merge
- Bottom-up merging produces full dendrogram
- Uses Ward's method for merge criterion

#### ✅ Pros

1. **Full Hierarchy**: Complete dendrogram from fine to coarse
2. **Walk-Based Distance**: Captures multi-hop neighborhood structure
3. **Small Communities**: Detects tightly-knit communities accurately
4. **Flexible**: Cut dendrogram at any level (e.g., max modularity)
5. **Deterministic**: Reproducible given same walk length and seed
6. **No Preset**: Doesn't require number of clusters

#### ⚠️ Cons

1. **Slow**: O(n²) or O(n·m) complexity
2. **Scale Limit**: Struggles with millions of nodes
3. **Walk Length**: Must choose appropriate walk length (typically 4-5)
4. **Hierarchy Interpretation**: Requires selecting the right level/cut
5. **Arbitrary Merges**: Can be arbitrary on fuzzy structure

#### 🎯 Best For

- Medium-sized graphs (<10k nodes)
- When full hierarchy is important
- Detailed multi-level analysis

---

### 5. Girvan-Newman Algorithm ⭐⭐ **CLASSIC**

**Type**: Divisive hierarchical (edge betweenness)  
**Hierarchical**: Yes (full dendrogram)  
**Scale**: <5,000 nodes

#### Description

**Classic divisive method**:

- Repeatedly removes edge with highest betweenness centrality
- Targets "bridges" between communities
- Network splits into communities as critical edges removed
- Produces full dendrogram (top-down)

#### ✅ Pros

1. **Full Hierarchy**: Complete dendrogram
2. **Intuitive**: Focuses on inter-community bridges
3. **No Parameters**: No prior parameter requirements
4. **Meaningful Splits**: Often yields intuitive divisions

#### ⚠️ Cons

1. **Extremely Slow**: Recalculating betweenness after each removal
2. **Poor Scaling**: Impractical beyond a few thousand nodes
3. **Single-Node Communities**: May break off many isolated nodes
4. **Limited Use**: Generally for demonstration/small networks only

#### 🎯 Best For

- Small networks (<1,000 nodes)
- Educational/demonstration purposes
- **NOT for production**

---

### 6. Label Propagation ⭐⭐ **FAST BUT UNSTABLE**

**Type**: Label diffusion  
**Hierarchical**: No (flat partition only)  
**Scale**: Millions of nodes

#### Description

**Simple, fast propagation**:

- Each node starts with unique label
- Nodes update to most frequent neighbor label
- Iterates until convergence (no changes)
- Near-linear time complexity

#### ✅ Pros

1. **Extremely Fast**: Near-linear time, feasible for millions of nodes
2. **Simple**: Easy to implement
3. **No Parameters**: Completely data-driven
4. **Anytime**: Valid partition even if stopped early
5. **Scalable**: Minimal computational resources

#### ⚠️ Cons

1. **Non-Deterministic**: Results vary with node order
2. **Unstable**: May need multiple runs + voting
3. **Giant Communities**: Can yield one giant community
4. **No Hierarchy**: Flat partition only
5. **Random on Homogeneous Graphs**: All nodes may get same label
6. **Quality Issues**: Lacks global objective (like modularity)

#### 🎯 Best For

- Quick first pass on huge graphs
- Initial clustering baseline
- **NOT for final analysis**

---

### 7. Spectral Methods (Leading Eigenvector) ⭐⭐⭐

**Type**: Linear algebra (eigenvector-based)  
**Hierarchical**: Yes (recursive bipartitioning)  
**Scale**: Tens of thousands of nodes

#### Description

**Eigenvector-based clustering**:

- Uses eigenvectors of modularity matrix or graph Laplacian
- Leading eigenvector splits network into two communities
- Recursive splits maximize modularity gain
- Produces binary tree hierarchy

#### ✅ Pros

1. **Analytical**: Grounded in linear algebra
2. **Deterministic**: Stable results
3. **Good Modularity**: Often achieves good modularity scores
4. **Flexible**: Can use different matrices for different objectives
5. **Hierarchical**: Binary tree of communities

#### ⚠️ Cons

1. **Eigenvector Computation**: Heavy for very large graphs
2. **Binary Splits**: May not capture multi-way natural divisions
3. **Scale Limit**: ~10k-100k nodes practical limit
4. **Stop Criterion**: Must decide when to stop splitting
5. **Supplanted**: Louvain/Leiden often preferred in practice

#### 🎯 Best For

- Medium graphs
- When deterministic results needed
- Theoretical analysis

---

### 8. Spinglass (Potts Model) ⭐ **NOT RECOMMENDED**

**Type**: Physics-based (simulated annealing)  
**Hierarchical**: No (single partition)  
**Scale**: <10,000 nodes

#### Description

**Spin-glass model optimization**:

- Treats nodes as atoms with spin states (communities)
- Optimizes Hamiltonian (energy) via simulated annealing
- Explores partitions globally

#### ✅ Pros

1. **Global Optimization**: Can escape local optima
2. **Flexible**: Can specify number of communities or resolution
3. **Theoretical Framework**: Physics-based foundation

#### ⚠️ Cons

1. **Very Slow**: Simulated annealing requires many iterations
2. **Unreliable**: Analytics Vidhya found inconsistent results
3. **Non-Deterministic**: Variable results without long runs
4. **Parameter Tuning**: Requires temperature schedule, γ, etc.
5. **Impractical**: Faster algorithms match or exceed quality
6. **Not Hierarchical**: Usually yields one partition

#### 🎯 Best For

- **Generally not recommended**
- Small graphs with specific needs
- Research/experimental use only

---

## Algorithm Selection Guide

### By Graph Size

#### **Small Graphs** (<1,000 nodes):

- **Girvan-Newman**: Full hierarchical dendrogram
- **Walktrap**: Good hierarchy with random walks
- **Spectral**: Analytical approach

#### **Medium Graphs** (1k-100k nodes):

- **Leiden**: Best overall ✅
- **Louvain**: Proven alternative
- **Walktrap**: If hierarchy is critical
- **Infomap**: For directed/flow graphs

#### **Large Graphs** (100k-1M+ nodes):

- **Leiden**: Best choice ⭐
- **Louvain**: Proven at scale
- **Infomap**: For directed graphs
- **Label Propagation**: Quick first pass only

---

### By Requirements

#### **Need Hierarchical Structure**:

1. **Leiden** - Recursive application ⭐
2. **Louvain** - Multi-level aggregation
3. **Walktrap** - Full dendrogram (medium graphs)
4. **Infomap** - Two-level solution

#### **Need Maximum Speed**:

1. **Label Propagation** - Fastest (but unstable)
2. **Louvain** - Fast + good quality
3. **Leiden** - Fast + best quality ⭐

#### **Need Deterministic Results**:

1. **Leiden** - Stable ⭐
2. **Walktrap** - Reproducible
3. **Spectral** - Deterministic
4. **Girvan-Newman** - Deterministic (but slow)

#### **Need High Quality**:

1. **Leiden** - Best quality ⭐
2. **Louvain** - High modularity
3. **Infomap** - Different quality metric
4. **Walktrap** - Good for medium graphs

---

## For GraphRAG Pipelines

### **Primary Recommendation**: Leiden Algorithm

**Why Leiden for GraphRAG**:

- ✅ Handles large knowledge graphs (thousands of entities)
- ✅ Hierarchical structure for multi-level topic clustering
- ✅ Best quality guarantees (connected communities)
- ✅ Fast and scalable
- ✅ High modularity scores
- ✅ Proven in Microsoft GraphRAG implementation

**Implementation**:

```python
# NetworkX 3.5+ (recommended)
from networkx.algorithms import community
communities = community.leiden_communities(G, resolution=1.0)

# Hierarchical Leiden (recursive)
def hierarchical_leiden(G, max_levels=3):
    # Level 1: Initial communities
    level1 = community.leiden_communities(G)

    # Level 2: Cluster communities
    # Build super-graph of communities...
    level2 = community.leiden_communities(super_graph)

    # Continue recursively...
```

---

### **Fallback Recommendation**: Louvain Algorithm

**When to Use Louvain**:

- ⚠️ Leiden fails or produces trivial communities
- ⚠️ Leiden not available (NetworkX <3.5)
- ✅ Need proven, battle-tested solution
- ✅ GraphRAG sparse graph issues

**Why Louvain as Fallback**:

- ✅ Proven on GraphRAG-like graphs
- ✅ Handles sparse, diverse entity graphs
- ✅ Fast and reliable
- ✅ Good modularity (as seen in tests: ~6 communities)
- ✅ Widely available (NetworkX, igraph, etc.)

**Implementation**:

```python
from networkx.algorithms import community
communities = community.louvain_communities(G, resolution=1.0)
```

---

### **GraphRAG-Specific Considerations**

#### Graph Characteristics:

- **Sparse**: Knowledge graphs often have low edge density
- **Diverse**: Many entity types with varying connectivity
- **Scale**: Thousands of entities, tens of thousands of relationships
- **Hierarchical Need**: Topics → Subtopics → Concepts

#### Common Issues:

**Problem**: hierarchical_leiden produces single-entity communities

- **Cause**: Sparse graph, algorithm repeatedly splits until trivial
- **Solution**: Switch to Louvain or tune resolution parameter

**Problem**: Too many small communities

- **Cause**: Resolution parameter too high
- **Solution**: Lower resolution (0.5-1.0 range)

**Problem**: One giant community

- **Cause**: Graph too sparse, no clear structure
- **Solution**: Add more relationship types or use lower resolution

---

## Implementation Examples

### Example 1: Leiden (Recommended)

```python
import networkx as nx
from networkx.algorithms import community

# Build graph
G = nx.Graph()
G.add_edges_from(relationships)

# Run Leiden
communities = community.leiden_communities(G, resolution=1.0)

# Hierarchical version
def hierarchical_leiden(G, min_community_size=5, max_levels=3):
    """Apply Leiden recursively for hierarchy."""
    results = []

    for level in range(max_levels):
        if level == 0:
            # Level 0: Cluster full graph
            communities = community.leiden_communities(G, resolution=1.0)
        else:
            # Higher levels: Cluster previous communities
            super_graph = build_super_graph(communities)
            communities = community.leiden_communities(super_graph)

        # Stop if communities too small
        if all(len(c) < min_community_size for c in communities):
            break

        results.append(communities)

    return results
```

### Example 2: Louvain (Fallback)

```python
import networkx as nx
from networkx.algorithms import community

# Build graph
G = nx.Graph()
G.add_edges_from(relationships)

# Run Louvain
communities = community.louvain_communities(G, resolution=1.0, seed=42)

# Access modularity score
modularity = community.modularity(G, communities)
print(f"Modularity: {modularity:.4f}")
```

---

## Resolution Parameter Guide

### What is Resolution?

The **resolution parameter** controls community size:

- **Higher resolution** (>1.0): More, smaller communities
- **Lower resolution** (<1.0): Fewer, larger communities
- **Default** (1.0): Standard modularity

### Recommended Values:

| Graph Type                    | Resolution | Expected Communities |
| ----------------------------- | ---------- | -------------------- |
| **Sparse** (low density)      | 0.5-0.8    | Fewer, larger        |
| **Moderate** (medium density) | 0.8-1.2    | Balanced             |
| **Dense** (high density)      | 1.2-2.0    | More, smaller        |

### For GraphRAG:

- **Start**: 1.0 (standard)
- **If too many tiny communities**: Lower to 0.7-0.8
- **If one giant community**: Raise to 1.2-1.5

---

## Troubleshooting

### Issue: Single-Entity Communities

**Symptoms**:

- Every entity is its own community
- No meaningful grouping

**Causes**:

- Resolution parameter too high
- Graph too sparse
- Algorithm splitting recursively

**Solutions**:

1. Lower resolution to 0.5-0.8
2. Switch from hierarchical_leiden to Louvain
3. Add more relationship types to increase density
4. Stop recursion earlier (min_community_size threshold)

---

### Issue: One Giant Community

**Symptoms**:

- All entities in single community
- No structure detected

**Causes**:

- Graph has no clear community structure
- Resolution parameter too low
- Insufficient edges

**Solutions**:

1. Increase resolution to 1.2-1.5
2. Check graph density (may be too sparse)
3. Validate relationship extraction quality
4. Try alternative algorithm (Infomap)

---

### Issue: Inconsistent Results

**Symptoms**:

- Different results on each run
- Communities change

**Causes**:

- Non-deterministic algorithm (Louvain, Label Propagation)
- Random seed not set

**Solutions**:

1. Set random seed for reproducibility
2. Run multiple times and take consensus
3. Switch to deterministic algorithm (Leiden with seed)

---

## Recommendations for GraphRAG

### **Production Setup** (Recommended):

```python
# Try Leiden first (best quality)
try:
    communities = community.leiden_communities(G, resolution=1.0, seed=42)
    if len(communities) > 1 and all(len(c) > 1 for c in communities):
        # Leiden succeeded with meaningful communities
        return communities
except:
    pass

# Fallback to Louvain (proven reliable)
communities = community.louvain_communities(G, resolution=0.8, seed=42)
return communities
```

### **Validation** (Always):

```python
# Calculate modularity
mod = community.modularity(G, communities)
print(f"Modularity: {mod:.4f}")  # Higher is better (>0.3 is good)

# Check community sizes
sizes = [len(c) for c in communities]
print(f"Communities: {len(communities)}")
print(f"Size range: {min(sizes)}-{max(sizes)}")
print(f"Average size: {sum(sizes)/len(sizes):.1f}")
```

---

## References

### Academic Papers:

- **Leiden Algorithm**: Traag et al., "From Louvain to Leiden: guaranteeing well-connected communities," Scientific Reports 9, 5233 (2019)
- **Algorithm Comparison**: Analytics Vidhya, "Comparative Analysis of Community Detection Algorithms" (2022)

### Documentation:

- **Microsoft GraphRAG**: Hierarchical Leiden documentation
- **NetworkX**: Community detection module
- **Hypermode Blog**: "Top Community Detection Algorithms Compared" (2025)

### Practical Guides:

- **Memgraph**: "Community Detection Algorithms with NetworkX"
- **OmicsAnalyst Forum**: Module detection algorithm explanations

---

## Summary

**For GraphRAG Knowledge Graphs**:

1. **Start with**: Leiden (resolution=1.0) ⭐
2. **Fallback to**: Louvain (resolution=0.8) if Leiden fails
3. **Validate**: Check modularity score and community sizes
4. **Tune**: Adjust resolution based on results
5. **Avoid**: Label Propagation, Spinglass, Girvan-Newman for production

**Expected Results**:

- 5-20 meaningful communities at top level
- Hierarchical structure for navigation
- Modularity >0.3 indicates good community structure

---

**Recommended**: **Leiden** (or Louvain if issues)  
**Resolution**: Start at 1.0, tune to 0.7-1.5 range  
**Validation**: Always check modularity and sizes  
**Production**: Use try/except with Leiden → Louvain fallback
