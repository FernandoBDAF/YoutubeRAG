# GraphRAG Quality Improvements Plan

**Date**: November 4, 2025  
**Status**: Ready to begin  
**Context**: Community detection working, experiment infrastructure complete

---

## 🎯 Current Baseline

### What's Working

- ✅ **Extraction**: 300 workers, TPM tracking, concurrent processing
- ✅ **Entity Resolution**: Grouping similar entities, canonicalization
- ✅ **Graph Construction**: 5 relationship types, batch operations
- ✅ **Community Detection**: Louvain, 873 communities, modularity 0.6347
- ✅ **Performance**: Full pipeline runs efficiently

### Known Limitations

**Extraction**:

- ❓ Extraction quality unknown (need to validate sample results)
- ❓ Entity/relationship precision/recall unknown
- ⚠️ No validation of extraction accuracy

**Entity Resolution**:

- ⚠️ Similarity threshold (0.85) not validated
- ❓ Resolution accuracy unknown
- ⚠️ May be merging too aggressively or not enough

**Graph Construction**:

- ⚠️ 5 relationship types - some may be redundant
- ❓ Cross-chunk relationships effectiveness unknown
- ❓ Predicted links quality unknown

**Community Detection**:

- ⚠️ Heavy truncation (30 entities, 50 relationships for large communities)
- ⚠️ Largest community (4804 entities) only gets 15 entities in summary
- ❓ Summary quality for truncated communities unknown

---

## 📊 Quality Improvement Areas

### Phase 1: Assessment & Validation (2-3 hours)

**Goal**: Understand current quality before improving

#### Task 1.1: Sample Extraction Results (30 min)

```bash
# Query sample extractions
db.video_chunks.aggregate([
  { $match: { "graphrag_extraction.status": "completed" } },
  { $sample: { size: 10 } },
  { $project: {
      chunk_text: 1,
      "graphrag_extraction.data.entities": 1,
      "graphrag_extraction.data.relationships": 1
  }}
])
```

**Analyze**:

- Are entities relevant?
- Are relationships accurate?
- Any obvious misses?

#### Task 1.2: Sample Entity Resolution Results (30 min)

```bash
# Query entity groups
db.entities.aggregate([
  { $sample: { size: 20 } },
  { $lookup: {
      from: "entity_mentions",
      localField: "entity_id",
      foreignField: "resolved_entity_id",
      as: "mentions"
  }}
])
```

**Analyze**:

- Are similar entities properly merged?
- Any false merges (different entities merged incorrectly)?
- Any missed merges (similar entities not merged)?

#### Task 1.3: Sample Community Summaries (30 min)

```bash
# Query sample communities
db.communities.aggregate([
  { $sample: { size: 10 } },
  { $project: {
      community_id: 1,
      title: 1,
      summary: 1,
      entity_count: 1,
      entities: 1
  }}
])
```

**Analyze**:

- Are summaries coherent and relevant?
- Does truncation lose critical information?
- Are community titles accurate?

#### Task 1.4: Graph Structure Analysis (30 min)

```python
# Analyze graph connectivity
# - Degree distribution
# - Connected components
# - Clustering coefficient
# - Path lengths
```

**Questions**:

- Is graph too sparse or too dense?
- Are there disconnected components?
- Do relationship types add value?

---

### Phase 2: Quick Wins (2-4 hours)

**Priority**: High-impact, low-effort improvements

#### Improvement 2.1: Better Token Counting (30 min)

**Current**: Rough estimation (~200-300 tokens/item)  
**Actual**: ~1600 tokens/item (8× underestimate!)

**Fix**: Use tiktoken for accurate counting

```python
# In community_summarization.py
import tiktoken

def _estimate_tokens_for_community(self, entities, relationships):
    """Accurate token counting using tiktoken."""
    encoding = tiktoken.encoding_for_model(self.model_name)

    # Build actual input text
    text = self._build_input_text(entities, relationships)

    # Count tokens accurately
    tokens = len(encoding.encode(text))
    return tokens
```

**Impact**: Less aggressive truncation needed, better summaries

**Time**: 30 min

#### Improvement 2.2: Centrality-Based Entity Selection (1 hour)

**Current**: Select top-N entities by confidence  
**Better**: Select most important entities by graph centrality

```python
# In community_summarization.py
def _select_important_entities(self, entities, max_count):
    """Select most important entities using PageRank."""
    import networkx as nx

    # Build sub-graph for this community
    G = self._build_community_subgraph(entities, relationships)

    # Calculate PageRank
    pagerank = nx.pagerank(G, weight='weight')

    # Sort entities by importance
    ranked = sorted(entities, key=lambda e: pagerank.get(e.id, 0), reverse=True)

    # Return top N
    return ranked[:max_count]
```

**Impact**: Keep most important entities, lose peripheral ones

**Time**: 1 hour

#### Improvement 2.3: Extraction Quality Validation (1 hour)

**Add**: Validation step after extraction

```python
# In extraction agent
def validate_extraction(self, entities, relationships, text):
    """Validate extraction quality."""
    issues = []

    # Check: Are all entities mentioned in text?
    for entity in entities:
        if entity.name.lower() not in text.lower():
            issues.append(f"Entity '{entity.name}' not found in text")

    # Check: Do relationships reference valid entities?
    entity_ids = {e.id for e in entities}
    for rel in relationships:
        if rel.subject_id not in entity_ids:
            issues.append(f"Relationship subject '{rel.subject_id}' not in entities")

    return issues
```

**Impact**: Catch extraction errors early, improve quality

**Time**: 1 hour

#### Improvement 2.4: Add Extraction Confidence Filtering (30 min)

**Current**: All extractions kept  
**Better**: Filter low-confidence extractions

```python
# In extraction stage
MIN_ENTITY_CONFIDENCE = 0.7
MIN_RELATIONSHIP_CONFIDENCE = 0.6

# Filter low-confidence items
high_conf_entities = [e for e in entities if e.confidence >= MIN_ENTITY_CONFIDENCE]
high_conf_rels = [r for r in relationships if r.confidence >= MIN_RELATIONSHIP_CONFIDENCE]
```

**Impact**: Higher quality graph, less noise

**Time**: 30 min

---

### Phase 3: Medium Improvements (4-6 hours)

#### Improvement 3.1: Multi-Pass Summarization (2 hours)

**For huge communities**: Summarize in passes

```python
def summarize_huge_community(self, community, entities, relationships):
    """Multi-pass summarization for communities >1000 entities."""
    # Pass 1: Cluster into sub-communities
    sub_communities = self._cluster_entities(entities, target_clusters=10)

    # Pass 2: Summarize each sub-community
    sub_summaries = [self._summarize_single_community(sub) for sub in sub_communities]

    # Pass 3: Combine sub-summaries into final summary
    final_summary = self._combine_summaries(sub_summaries)

    return final_summary
```

**Impact**: Better quality for large communities, no truncation needed

**Time**: 2 hours

#### Improvement 3.2: Relationship Type Effectiveness Analysis (1 hour)

**Analyze**: Which relationship types add value?

```python
# Count usage of each relationship type
db.relationships.aggregate([
  { $group: { _id: "$relationship_type", count: { $sum: 1 } } }
])

# For each type, measure:
# - Count
# - Community inclusion rate
# - Query relevance contribution
```

**Decision**: Keep valuable types, remove noise

**Time**: 1 hour

#### Improvement 3.3: Entity Type Refinement (1 hour)

**Current**: 7 entity types (PERSON, ORG, TECH, CONCEPT, LOCATION, EVENT, OTHER)

**Analyze**:

- Distribution of types
- Accuracy of type assignment
- Types that add vs reduce value

**Possible**: Merge similar types or add new ones

**Time**: 1 hour

#### Improvement 3.4: Resolution Threshold Tuning (2 hours)

**Current**: Similarity threshold 0.85 (not validated)

**Test**:

- Run resolution with thresholds [0.75, 0.80, 0.85, 0.90, 0.95]
- Measure: Entity reduction, false merges, missed merges
- Find optimal threshold

**Time**: 2 hours (mostly compute time)

---

### Phase 4: Advanced Improvements (6-10 hours)

#### Improvement 4.1: Semantic Chunking (3 hours)

**Current**: Fixed-size chunks  
**Better**: Semantic boundary chunking

**Impact**: Better context preservation

#### Improvement 4.2: Adaptive Truncation (2 hours)

**Current**: Fixed caps (30/50)  
**Better**: Adaptive based on community characteristics

```python
# For dense communities: Keep more relationships
# For sparse communities: Keep more entities
# For hierarchical communities: Keep representative samples
```

#### Improvement 4.3: Summary Quality Scoring (2 hours)

**Add**: Quality metrics for summaries

```python
# Metrics:
# - Coverage: % of entities mentioned
# - Coherence: Semantic similarity of content
# - Relevance: Alignment with entity descriptions
```

#### Improvement 4.4: Iterative Refinement (3 hours)

**Add**: Self-correction loop

```python
# 1. Generate summary
# 2. Validate quality
# 3. If low quality: Regenerate with different approach
# 4. Keep best summary
```

---

## 🎯 Recommended Approach

### Week 1: Assessment + Quick Wins (Today + Tomorrow)

**Today (Remaining Time)**:

1. Sample extraction results validation
2. Sample community summaries validation
3. Identify obvious issues

**Tomorrow**:

1. Implement tiktoken counting
2. Implement centrality-based selection
3. Add extraction validation
4. Test and measure improvements

### Week 2: Medium Improvements

**Focus**: Relationship types, resolution tuning, multi-pass summarization

### Week 3: Advanced Improvements + Experiments

**Focus**: Run full experiment matrix, analyze, write articles

---

## 📊 Success Metrics

### Extraction Quality

- ✅ >90% entity precision (entities are real/relevant)
- ✅ >80% entity recall (important entities captured)
- ✅ >85% relationship accuracy

### Resolution Quality

- ✅ <5% false merges (different entities incorrectly merged)
- ✅ >90% true merges (similar entities correctly merged)

### Community Quality

- ✅ >95% multi-entity communities (filter noise)
- ✅ >0.6 modularity (strong community structure)
- ✅ Summary coherence >7/10 (human evaluation)

### Performance

- ✅ <4 hours total runtime for 13k chunks (current: varies)
- ✅ <$50 API cost per full run

---

## 🔍 Analysis Tools Needed

### Tool 1: Extraction Validator

```python
# scripts/validate_extraction_quality.py
# - Sample N extractions
# - Check for hallucinations
# - Check for misses
# - Generate quality report
```

### Tool 2: Resolution Analyzer

```python
# scripts/analyze_entity_resolution.py
# - Find entity groups
# - Check merge decisions
# - Flag suspicious merges
# - Report merge stats
```

### Tool 3: Community Quality Scorer

```python
# scripts/score_community_quality.py
# - Sample communities
# - Score summaries
# - Check coherence
# - Generate quality report
```

---

## 📝 Documentation Updates Needed

After improvements:

1. Update design decision comments with new approaches
2. Document quality metrics achieved
3. Update configuration recommendations
4. Create quality validation guide

---

**Plan Status**: ✅ Ready  
**Next Step**: Begin quality assessment and improvements  
**Estimated Time**: 1-2 weeks for comprehensive improvements
