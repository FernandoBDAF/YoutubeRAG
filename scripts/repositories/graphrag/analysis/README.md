# GraphRAG Analysis Scripts

Advanced analysis scripts for examining GraphRAG knowledge graph structure, quality, and issues.

## Scripts

### analyze_graph_structure.py

Comprehensive graph structure analysis using NetworkX. Provides detailed insights into:
- Graph connectivity and components
- Node degree distribution
- Centrality measures
- Community structure
- Bottlenecks and hub nodes

**Usage**:
```bash
python scripts/repositories/graphrag/analysis/analyze_graph_structure.py
```

**Requirements**: `networkx`

---

### diagnose_communities.py

Diagnose community detection issues. Analyzes:
- Community size distribution
- Communities with/without relationships
- Relationship analysis
- Entity type distribution
- Potential issues

**Usage**:
```bash
python scripts/repositories/graphrag/analysis/diagnose_communities.py
```

---

### inspect_community_detection.py

Detailed inspection of community detection results. Shows:
- Community summaries
- Entity distributions
- Coherence scores
- Relationship patterns

**Usage**:
```bash
python scripts/repositories/graphrag/analysis/inspect_community_detection.py
```

---

### monitor_density.py

Monitor graph density metrics over time. Tracks:
- Node/edge counts
- Graph density
- Average degree
- Connected components

**Usage**:
```bash
python scripts/repositories/graphrag/analysis/monitor_density.py
```

---

## Purpose

These scripts provide deep insights into GraphRAG graph quality and help identify:
- Connectivity issues
- Community detection problems
- Data quality issues
- Graph structure anomalies

---

**Created**: November 7, 2025  
**Source**: Consolidated from app/scripts/graphrag/  
**Purpose**: Advanced GraphRAG analysis and diagnostics

