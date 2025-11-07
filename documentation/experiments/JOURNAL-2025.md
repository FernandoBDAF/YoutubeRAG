# GraphRAG Experiment Journal - 2025

**Purpose**: Track hypotheses, results, and learnings from GraphRAG experiments systematically.

**How to Use**:
1. Create a new entry for each experiment or experiment series
2. Link to experiment config files and results
3. Document hypotheses, findings, and next steps
4. Use this journal to inform future experiments

---

## Entry Template

```markdown
### Experiment: [Experiment ID]

**Date**: YYYY-MM-DD  
**Experiment ID**: [experiment_id]  
**Config**: `configs/graphrag/[config_file].json`  
**Database**: [write_db_name]

#### Hypothesis
- [What we're testing]
- [Expected outcome]

#### Configuration
- Algorithm: [louvain/leiden/label_propagation]
- Resolution: [value]
- Other key parameters: [list]

#### Results
- **Coverage**: [chunks, entities, relationships, communities]
- **Quality**: [modularity, graph density, avg degree]
- **Performance**: [runtime, throughput]
- **Cost**: [tokens, estimated cost]

#### Analysis
- [What worked well]
- [What didn't work]
- [Surprises or unexpected findings]

#### Next Steps
- [What to try next]
- [Follow-up experiments]
- [Parameter adjustments]
```

---

## Experiments

### Experiment: baseline_louvain_res10

**Date**: 2025-11-06  
**Experiment ID**: baseline_louvain_res10  
**Config**: `configs/graphrag/louvain_default.json`  
**Database**: graphrag_baseline

#### Hypothesis
- Louvain with resolution=1.0 provides a good baseline for community detection
- Expected to find balanced community sizes (5-50 entities per community)

#### Configuration
- Algorithm: louvain
- Resolution: 1.0
- Min cluster size: 2
- Max cluster size: 50

#### Results
- **Coverage**: [To be filled after experiment]
- **Quality**: [To be filled after experiment]
- **Performance**: [To be filled after experiment]
- **Cost**: [To be filled after experiment]

#### Analysis
- [To be filled after experiment]

#### Next Steps
- Compare with resolution=0.8 (fewer, larger communities)
- Compare with resolution=1.5 (more, smaller communities)

---

## Archive

Experiments older than 1 year should be moved to `documentation/archive/experiments/YYYY/`

---

**Last Updated**: 2025-11-07

