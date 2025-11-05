# Plan: Ontology-Based Extraction & Quality Optimization

**Status**: Production Ready - Planning Quality Validation  
**Last Updated**: November 5, 2025  
**Archive Reference**: 
- `documentation/archive/ontology-implementation-nov-2025/` (to be created)
- `documentation/archive/extraction-optimization-nov-2025/` (to be created)

---

## 📍 Current State

### What We Built

**Ontology System** (Production Ready):
- ✅ Ontology loader with YAML validation
- ✅ Hybrid normalization (logic + LLM for ambiguous cases)
- ✅ Predicate canonicalization with mapping
- ✅ Type-pair constraint validation
- ✅ Symmetric relation handling
- ✅ Soft-keep mechanism for unknown predicates
- ✅ Dynamic prompt injection
- ✅ Comprehensive test coverage (9 tests, all passing)

**Extraction Improvements** (Production Ready):
- ✅ Quota error detection and handling
- ✅ Configurable models and max_tokens
- ✅ Accurate statistics logging
- ✅ Integration with ontology system

### Current Capabilities

**Extract with Ontology**:
```bash
python app/cli/graphrag.py extraction \
  --read-db mongo_hack \
  --write-db validation_db \
  --concurrency 300
```

**Test Ontology Features**:
```bash
python tests/test_ontology_extraction.py
```

### Gaps Identified

1. **No Quality Comparison with Old Data**
   - `validation_db` has old extraction data (pre-ontology)
   - No comparison scripts to measure improvement
   - Can't quantify ontology impact
   - No predicate distribution analysis

2. **Limited Ontology Coverage**
   - 34 canonical predicates (may need more)
   - Type constraints only for 3 predicates
   - Symmetric predicates list may be incomplete
   - No entity type mapping yet active

3. **No Quality Metrics**
   - No precision/recall measurements
   - No consistency metrics
   - No noise reduction quantification
   - No extraction time comparison

4. **Missing Validation Tools**
   - No predicate distribution analyzer
   - No entity type distribution analyzer
   - No relationship quality scorer
   - No extraction diff tool

5. **No Iterative Improvement Process**
   - Ontology files are static
   - No feedback loop from results to ontology
   - No automated ontology refinement
   - No A/B testing framework

---

## 🎯 Goals & Scope

### Primary Goals

1. **Validate Ontology Impact** - Measure quality improvement vs pre-ontology data
2. **Expand Ontology Coverage** - Identify and add missing canonical predicates
3. **Create Quality Metrics** - Quantify extraction quality improvements
4. **Establish Feedback Loop** - Use extraction results to improve ontology
5. **Document Best Practices** - Guide for ontology maintenance

### Out of Scope

- Manual entity/relationship annotation (too time-consuming)
- Real-time extraction quality monitoring (future enhancement)
- Ontology learning from scratch (start with manual curation)

---

## 📋 Implementation Plan

### Phase 1: Quality Comparison Scripts

**Goal**: Compare old (pre-ontology) vs new (ontology-based) extraction data

#### 1.1 Extraction Data Comparison Script

**Script**: `scripts/compare_extraction_quality.py`

**Functionality**:
```python
"""
Compare extraction quality between two databases (old vs new extraction).

Usage:
    python scripts/compare_extraction_quality.py \
        --old-db validation_db \
        --new-db ontology_extraction_db \
        --output comparison_report.md
"""
```

**Metrics to Compare**:

1. **Predicate Quality**:
   - Canonical predicate ratio: `canonical / total`
   - Unique predicate count (lower is better if canonical ratio high)
   - Noise ratio: `dropped / total`
   - Top 20 predicates distribution

2. **Entity Quality**:
   - Entity type distribution
   - Average entities per chunk
   - Entity confidence distribution
   - Unique entity count

3. **Relationship Quality**:
   - Average relationships per chunk
   - Relationship confidence distribution
   - Type-pair constraint violations (old vs new)
   - Symmetric relation consistency

4. **Coverage**:
   - Chunks with entities: `count / total_chunks`
   - Chunks with relationships: `count / total_chunks`
   - Failed extractions: `failed / total`

**Output**:
- Markdown report with tables and comparisons
- JSON file with raw metrics for further analysis
- Recommendations for ontology improvements

**Implementation**:
- [ ] Create script skeleton
- [ ] Implement metric calculations
- [ ] Add MongoDB queries for old/new data
- [ ] Generate markdown report
- [ ] Test with validation_db (old) and new extraction
- [ ] Document findings in experiment journal

#### 1.2 Predicate Distribution Analyzer

**Script**: `scripts/analyze_predicate_distribution.py`

**Functionality**:
```python
"""
Analyze predicate distributions and identify improvement opportunities.

Usage:
    python scripts/analyze_predicate_distribution.py \
        --db mongo_hack \
        --min-frequency 10 \
        --output predicate_analysis.md
"""
```

**Analysis**:
1. **Frequency Distribution**:
   - Top 50 predicates by frequency
   - Long tail analysis (predicates with <5 occurrences)
   - Canonical vs non-canonical ratio

2. **Quality Indicators**:
   - Predicates mapped to canonical forms
   - Predicates dropped as noise
   - Predicates soft-kept (unknown but high confidence)
   - Type constraint violations

3. **Improvement Opportunities**:
   - High-frequency predicates not in canonical list
   - Inconsistent predicate variations (e.g., "utilize" vs "utilizes" vs "utilization")
   - Potential new canonical predicates
   - Potential new mappings

**Output**:
- Predicate frequency table
- Canonical coverage report
- Recommendations for ontology updates
- Suggested predicate_map additions

**Implementation**:
- [ ] Create script
- [ ] MongoDB aggregation for predicate counts
- [ ] Identify canonical vs non-canonical
- [ ] Generate recommendations
- [ ] Test and document

#### 1.3 Entity Type Distribution Analyzer

**Script**: `scripts/analyze_entity_types.py`

**Functionality**:
```python
"""
Analyze entity type distributions and coverage.

Usage:
    python scripts/analyze_entity_types.py \
        --db mongo_hack \
        --output entity_type_analysis.md
"""
```

**Analysis**:
1. **Type Distribution**:
   - Count by entity type
   - Percentage breakdown
   - Entities using OTHER type (potential new types needed)

2. **Quality Indicators**:
   - Average confidence by type
   - Entities per chunk by type
   - Type consistency across chunk boundaries

3. **Improvement Opportunities**:
   - Overused OTHER category
   - Missing entity types
   - Type ambiguity cases

**Output**:
- Entity type distribution table
- OTHER category breakdown
- Recommendations for new types

**Implementation**:
- [ ] Create script
- [ ] MongoDB aggregation for type counts
- [ ] Analyze OTHER category
- [ ] Generate recommendations
- [ ] Test and document

---

### Phase 2: Ontology Expansion

**Goal**: Expand ontology coverage based on extraction data analysis

#### 2.1 Canonical Predicates Expansion

**Process**:
1. Run predicate distribution analyzer
2. Identify high-frequency non-canonical predicates
3. Review for semantic value
4. Add to `canonical_predicates.yml`
5. Add mappings to `predicate_map.yml`
6. Re-run extraction on test dataset
7. Validate improvement

**Target**:
- Canonical predicate ratio: >80% (from current ~70%)
- Add 10-20 new canonical predicates
- Add 20-30 new mappings

**Implementation**:
- [ ] Run analyzer on production data
- [ ] Review top 100 non-canonical predicates
- [ ] Curate new canonical list
- [ ] Update YAML files
- [ ] Test with sample dataset
- [ ] Commit and document changes

#### 2.2 Type Constraints Expansion

**Current**: Only 3 predicates have type constraints (is_a, part_of, member_of)

**Target**: Add constraints for 15-20 high-value predicates

**Candidates**:
- `teaches`: PERSON → COURSE, PERSON → CONCEPT
- `uses`: TECHNOLOGY → TECHNOLOGY, METHOD → TECHNOLOGY
- `developed_by`: TECHNOLOGY → ORGANIZATION, TECHNOLOGY → PERSON
- `works_at`: PERSON → ORGANIZATION
- `located_in`: ORGANIZATION → LOCATION, EVENT → LOCATION
- `evaluated_on`: MODEL → METRIC, ALGORITHM → METRIC
- `implements`: TECHNOLOGY → ALGORITHM, TECHNOLOGY → METHOD

**Process**:
1. Analyze relationship type pairs from extraction data
2. Identify common valid pairs
3. Define constraints
4. Test with validation dataset
5. Measure false positive reduction

**Implementation**:
- [ ] Query relationship type pairs from database
- [ ] Analyze frequency distributions
- [ ] Define constraints for top predicates
- [ ] Update `canonical_predicates.yml`
- [ ] Test and validate
- [ ] Document in ontology README

#### 2.3 Symmetric Predicates Review

**Current**: 11 symmetric predicates

**Review**:
- Are all truly symmetric?
- Are there missing symmetric predicates?
- Should any be removed?

**Process**:
1. Analyze relationship directionality from data
2. Identify predicates that appear in both directions equally
3. Validate semantic symmetry
4. Update list

**Implementation**:
- [ ] Query bidirectional relationships
- [ ] Calculate direction ratios
- [ ] Review semantic symmetry
- [ ] Update list if needed
- [ ] Test and validate

---

### Phase 3: Pre/Post Ontology Comparison

**Goal**: Quantify ontology impact on extraction quality

#### 3.1 Re-extract Baseline Dataset

**Dataset**: 1000 chunks from `validation_db` (before ontology refactor)

**Steps**:
1. Copy chunks to new database: `ontology_comparison_db`
2. Extract WITHOUT ontology (disable loading)
3. Extract WITH ontology (current production)
4. Compare side-by-side

**Config Files**:

```json
// configs/comparison/without_ontology.json
{
  "experiment_id": "baseline_no_ontology",
  "read_db": "ontology_comparison_db",
  "write_db": "comparison_no_ontology",
  "extraction": {
    "disable_ontology": true,  // NEW flag needed
    "model": "gpt-4o-mini",
    "concurrency": 300
  }
}

// configs/comparison/with_ontology.json
{
  "experiment_id": "baseline_with_ontology",
  "read_db": "ontology_comparison_db",
  "write_db": "comparison_with_ontology",
  "extraction": {
    "model": "gpt-4o-mini",
    "concurrency": 300
  }
}
```

**Implementation**:
- [ ] Add `disable_ontology` flag to extraction config
- [ ] Create comparison configs
- [ ] Run both extractions
- [ ] Use comparison scripts
- [ ] Document results
- [ ] Calculate improvement percentage

#### 3.2 Quality Improvement Report

**Goal**: Comprehensive report on ontology impact

**Metrics**:
1. **Predicate Quality**:
   - Canonical ratio: before vs after
   - Noise reduction: % of predicates dropped
   - Consistency improvement: unique predicates reduction

2. **Entity Quality**:
   - Type distribution change
   - Confidence score changes
   - Extraction success rate

3. **Cost Impact**:
   - Token usage change
   - Cost change ($ per chunk)
   - Processing time change

4. **Downstream Impact**:
   - Graph construction success rate
   - Community detection quality
   - Query performance (if measurable)

**Implementation**:
- [ ] Run comparison experiments
- [ ] Calculate all metrics
- [ ] Generate comprehensive report
- [ ] Include visualizations
- [ ] Archive in `documentation/experiments/results/`
- [ ] Share key findings in technical handbook

---

### Phase 4: Ontology Maintenance & Improvement

**Goal**: Establish process for ongoing ontology improvement

#### 4.1 Ontology Feedback Loop

**Process**:
1. Run extraction on dataset
2. Analyze predicate distribution
3. Identify gaps (high-frequency non-canonical)
4. Review and curate additions
5. Update ontology files
6. Test on validation set
7. Deploy if quality improves
8. Document changes

**Automation Opportunities**:
- [ ] Script to suggest new canonical predicates (based on frequency)
- [ ] Script to suggest new mappings (based on clustering)
- [ ] Automated testing after ontology updates
- [ ] Changelog for ontology files

**Implementation**:
- [ ] Create `scripts/suggest_ontology_updates.py`
- [ ] Create `ontology/CHANGELOG.md`
- [ ] Document review process
- [ ] Set review schedule (monthly)

#### 4.2 Ontology Versioning

**Goal**: Track ontology changes and their impact

**Approach**:
- Version ontology files (v1.0, v1.1, etc.)
- Track which extraction used which version
- Compare extraction quality across versions
- Rollback if quality degrades

**Implementation**:
- [ ] Add version field to ontology files
- [ ] Track version in extraction metadata
- [ ] Create ontology version comparison tool
- [ ] Document versioning process

#### 4.3 Community Contributions

**Goal**: Enable team to contribute ontology improvements

**Process**:
- Guidelines for proposing new predicates
- Review criteria
- Testing requirements
- Approval process

**Implementation**:
- [ ] Create `ontology/CONTRIBUTING.md`
- [ ] Template for predicate proposals
- [ ] Review checklist
- [ ] Document in team guide

---

### Phase 5: Advanced Quality Metrics

**Goal**: Beyond basic counts - measure extraction quality

#### 5.1 Consistency Metrics

**Metrics**:
1. **Cross-Chunk Consistency**:
   - Same entity mentioned in multiple chunks → same canonical name?
   - Same relationship mentioned → same canonical predicate?
   - Measure: consistency score = `matches / total_mentions`

2. **Type Consistency**:
   - Same entity → always same type?
   - Measure: type consistency score per entity

3. **Confidence Calibration**:
   - High confidence predictions → actually accurate?
   - Measure: precision by confidence bucket (0.3-0.5, 0.5-0.7, 0.7-0.9, 0.9-1.0)

**Implementation**:
- [ ] Create `scripts/measure_extraction_consistency.py`
- [ ] Query cross-chunk entity mentions
- [ ] Calculate consistency scores
- [ ] Generate quality report
- [ ] Set quality thresholds

#### 5.2 Coverage Metrics

**Metrics**:
1. **Semantic Coverage**:
   - % of important concepts extracted
   - % of relationships captured
   - Coverage gaps (where extraction misses info)

2. **Ontology Coverage**:
   - % of canonical predicates actually used
   - % of entity types actually used
   - Unused ontology elements (candidates for removal)

**Implementation**:
- [ ] Define "important concepts" (manual or LLM-based)
- [ ] Measure extraction vs ground truth
- [ ] Calculate coverage percentages
- [ ] Identify gaps
- [ ] Report and improve

#### 5.3 Noise Metrics

**Metrics**:
1. **Predicate Noise**:
   - % of predicates dropped by ontology
   - Top noisy predicates (frequently dropped)
   - False positive rate (good predicates incorrectly dropped)

2. **Entity Noise**:
   - Low-confidence entities (< 0.5)
   - Generic entities ("this", "it", "thing")
   - Duplicate entities (same concept, different names)

3. **Relationship Noise**:
   - Low-confidence relationships
   - Circular relationships (A→B, B→A with non-symmetric predicate)
   - Type constraint violations

**Implementation**:
- [ ] Create `scripts/measure_extraction_noise.py`
- [ ] Calculate noise metrics
- [ ] Identify patterns
- [ ] Tune filtering thresholds
- [ ] Document optimal settings

---

### Phase 6: Extraction Quality Experiments

**Goal**: Find optimal extraction configuration

#### 6.1 Model Selection Experiments

**Hypothesis**: `gpt-4o-mini` with ontology achieves 90% of `gpt-4o` quality at 10% cost

**Experiments**:
1. `gpt-4o` without ontology (high quality, high cost baseline)
2. `gpt-4o` with ontology (highest quality baseline)
3. `gpt-4o-mini` without ontology (low cost, low quality baseline)
4. `gpt-4o-mini` with ontology (target: good quality, low cost)

**Metrics**:
- Canonical predicate ratio
- Entity extraction rate
- Relationship extraction rate
- Cost per chunk
- Quality score (composite of above)

**Implementation**:
- [ ] Create 4 experiment configs
- [ ] Run on same 1000-chunk dataset
- [ ] Compare metrics
- [ ] Calculate quality/cost ratio
- [ ] Document findings
- [ ] Update default model if needed

#### 6.2 Soft-Keep Threshold Experiments

**Hypothesis**: Soft-keep threshold at 0.85 balances quality and coverage

**Experiments**:
1. Soft-keep disabled (baseline - strict filtering)
2. Soft-keep at 0.75 (lenient)
3. Soft-keep at 0.85 (current)
4. Soft-keep at 0.95 (strict)

**Metrics**:
- Predicate coverage (unique predicates kept)
- Canonical ratio
- Noise ratio (manual review sample)
- Downstream impact (graph construction success)

**Implementation**:
- [ ] Create soft-keep variation configs
- [ ] Run experiments
- [ ] Manually review samples of soft-kept predicates
- [ ] Measure downstream impact
- [ ] Document optimal threshold
- [ ] Update default if needed

#### 6.3 Temperature Experiments

**Hypothesis**: Lower temperature (0.0) improves consistency without hurting quality

**Experiments**:
1. Temperature 0.0 (deterministic)
2. Temperature 0.1 (current default)
3. Temperature 0.3 (creative)

**Metrics**:
- Cross-chunk consistency
- Entity/relationship counts
- Canonical predicate ratio
- Extraction diversity

**Implementation**:
- [ ] Create temperature variation configs
- [ ] Run on same dataset multiple times (test reproducibility)
- [ ] Measure consistency
- [ ] Document findings
- [ ] Set optimal temperature

---

### Phase 7: Validation Against Old Data

**Goal**: Direct comparison with `validation_db` (pre-ontology extraction)

#### 7.1 Setup Comparison Environment

**Steps**:
1. Identify common chunk subset in both databases
2. Ensure identical chunk texts
3. Load old extraction results
4. Re-run extraction with ontology on same chunks
5. Compare side-by-side

**Implementation**:
- [ ] Create `scripts/setup_comparison_dataset.py`
- [ ] Find common chunks in validation_db and mongo_hack
- [ ] Create comparison_chunks collection
- [ ] Document dataset characteristics

#### 7.2 Side-by-Side Comparison

**Script**: `scripts/compare_old_vs_new_extraction.py`

**Functionality**:
```python
"""
Compare old (pre-ontology) vs new (ontology-based) extraction on identical chunks.

Usage:
    python scripts/compare_old_vs_new_extraction.py \
        --chunks-db comparison_chunks \
        --old-db validation_db \
        --new-db ontology_extraction_db \
        --sample-size 100 \
        --output side_by_side_comparison.md
"""
```

**Comparison Categories**:

1. **Predicate Quality**:
   - Old: Count of raw predicates
   - New: Count of canonical predicates
   - Improvement: % reduction in unique predicates, % canonical

2. **Entity Quality**:
   - Old: Entity counts, type distribution
   - New: Entity counts, type distribution
   - Improvement: Type consistency, confidence scores

3. **Relationship Quality**:
   - Old: Relationship counts
   - New: Relationship counts (after filtering)
   - Improvement: Type constraint adherence, symmetric consistency

4. **Examples**:
   - Show 10-20 example chunks with before/after extraction
   - Highlight improvements (noise removed, predicates canonicalized)
   - Highlight regressions (valid data lost - if any)

**Implementation**:
- [ ] Create comparison script
- [ ] Query old and new extractions
- [ ] Match by chunk_id
- [ ] Calculate metrics
- [ ] Generate side-by-side examples
- [ ] Create comprehensive report
- [ ] Document in experiment journal

#### 7.3 Regression Testing

**Goal**: Ensure ontology doesn't lose valid extractions

**Process**:
1. Sample 100 chunks
2. Manually review old extraction results
3. Mark valid entities/relationships
4. Check if new extraction includes them
5. Calculate recall: `valid_kept / total_valid`

**Success Criteria**:
- Recall > 95% (we keep 95%+ of valid extractions)
- Precision improvement (measured by manual review)
- Net quality improvement

**Implementation**:
- [ ] Create manual review tool/script
- [ ] Sample and review
- [ ] Calculate recall
- [ ] Document any losses
- [ ] Adjust ontology if needed (e.g., add back dropped valid predicates)

---

### Phase 8: Ontology Refinement Tools

**Goal**: Tools to help maintain and improve ontology files

#### 8.1 Predicate Clustering Tool

**Goal**: Identify predicate variations that should be mapped

**Script**: `scripts/cluster_predicates.py`

**Functionality**:
- Extract all unique predicates from database
- Cluster by semantic similarity (embeddings)
- Identify clusters with >5 predicates
- Suggest canonical form and mappings

**Implementation**:
- [ ] Create script
- [ ] Use sentence embeddings for clustering
- [ ] Generate suggested mappings
- [ ] Human review and approval
- [ ] Update predicate_map.yml

#### 8.2 Ontology Validation Tool

**Goal**: Validate ontology files for consistency

**Script**: `scripts/validate_ontology.py`

**Checks**:
- All mappings point to canonical predicates
- All symmetric predicates are canonical
- All type constraints use valid types
- No circular mappings
- No orphaned entries

**Implementation**:
- [ ] Create validation script
- [ ] Run as pre-commit hook
- [ ] Add to CI/CD pipeline
- [ ] Document validation rules

#### 8.3 Ontology Impact Analyzer

**Goal**: Measure impact of each ontology rule

**Script**: `scripts/analyze_ontology_impact.py`

**Analysis**:
- Which canonical predicates are most used?
- Which mappings are most effective?
- Which type constraints catch the most violations?
- Which symmetric predicates are most common?

**Output**:
- Ontology usage report
- Effectiveness scores for each rule
- Recommendations for pruning unused rules

**Implementation**:
- [ ] Create impact analyzer
- [ ] Query extraction data
- [ ] Calculate usage statistics
- [ ] Generate report
- [ ] Use for ontology cleanup

---

## 🔍 Identified Gaps & Solutions

### Gap 1: No Extraction Quality Dashboard

**Problem**: Can't easily monitor extraction quality over time

**Solution**:
- [ ] Create `scripts/extraction_quality_dashboard.py`
- [ ] Track metrics: canonical ratio, noise ratio, entity/rel counts
- [ ] Generate daily/weekly reports
- [ ] Store in time-series format
- [ ] Visualize trends

### Gap 2: No LLM Normalization Cost Tracking

**Problem**: Don't know how much LLM normalization costs

**Solution**:
- [ ] Add token tracking for normalization calls
- [ ] Log normalization cache hit rate
- [ ] Calculate cost savings from caching
- [ ] Document in cost analysis

### Gap 3: No Extraction Error Analysis

**Problem**: Don't analyze why extractions fail

**Solution**:
- [ ] Create `scripts/analyze_extraction_failures.py`
- [ ] Categorize failure types (quota, parsing, validation, timeout)
- [ ] Identify patterns (chunk length, complexity)
- [ ] Generate failure report
- [ ] Use to improve retry logic

### Gap 4: No Ontology Documentation Beyond README

**Problem**: Ontology files lack comprehensive documentation

**Solution**:
- [ ] Create `documentation/reference/ONTOLOGY-REFERENCE.md`
- [ ] Document all canonical predicates with examples
- [ ] Document all type constraints with rationale
- [ ] Document symmetric predicates with usage
- [ ] Include maintenance guide

---

## 📊 Success Criteria

### Phase 1 Complete When:
- ✅ 3 comparison scripts created and tested
- ✅ Comparison report generated for validation_db vs new extraction
- ✅ Improvement metrics documented

### Phase 2 Complete When:
- ✅ Canonical predicates expanded to 50+ entries
- ✅ Type constraints for 15-20 predicates
- ✅ Symmetric predicates reviewed and validated
- ✅ Canonical predicate ratio > 80%

### Phase 3 Complete When:
- ✅ Pre/post ontology comparison complete
- ✅ Quality improvement quantified
- ✅ Regression testing shows recall > 95%
- ✅ Findings documented

### Phase 4 Complete When:
- ✅ 3 ontology maintenance tools created
- ✅ Validation tool integrated into workflow
- ✅ Impact analyzer producing insights
- ✅ Feedback loop established

---

## ⏱️ Time Estimates

**Phase 1** (Comparison Scripts): 6-8 hours  
**Phase 2** (Ontology Expansion): 4-6 hours  
**Phase 3** (Pre/Post Comparison): 5-7 hours  
**Phase 4** (Refinement Tools): 6-8 hours

**Total**: 21-29 hours

---

## 🚀 Immediate Next Steps

1. **Archive old documentation** - Execute archiving plan
2. **Create Phase 1 scripts** - Start with comparison tools
3. **Run validation_db comparison** - Quantify ontology impact
4. **Document findings** - Update experiment journal
5. **Plan Phase 2** - Based on Phase 1 results

---

## 📚 References

**Archives** (post-archiving):
- `documentation/archive/ontology-implementation-nov-2025/`
- `documentation/archive/extraction-optimization-nov-2025/`

**Current Docs**:
- `documentation/technical/GraphRAG_Extraction_and_Ontology_Handbook.md`
- `ontology/README.md`
- `documentation/guides/EXPERIMENT-WORKFLOW.md`

**Code**:
- `core/libraries/ontology/loader.py` - Ontology loader
- `business/agents/graphrag/extraction.py` - Extraction agent with ontology
- `business/stages/graphrag/extraction.py` - Extraction stage

**Tests**:
- `tests/test_ontology_extraction.py` - 9 tests, all passing

---

**Status**: Ready for execution after archiving  
**Priority**: High - Foundational for quality improvements

