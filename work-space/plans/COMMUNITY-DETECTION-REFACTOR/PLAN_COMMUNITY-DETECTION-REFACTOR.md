# PLAN: Community Detection & Summarization Refactor

**Status**: Planning  
**Created**: 2025-11-06 21:15 UTC  
**Goal**: Transform community detection and summarization into a production-grade, self-improving system with stable IDs, reproducible runs, ontology-aware weighting, and intelligent summarization  
**Priority**: HIGH - Critical for knowledge graph quality and retrieval

---

## 📖 Context for LLM Execution

**If you're an LLM reading this to execute work**:

1. **What This Plan Is**: Comprehensive refactor of community detection and summarization to address critical issues (ID stability, reproducibility, token management) and unlock advanced features (multi-resolution, ontology-aware weighting, self-improving loop)

2. **Your Task**: Implement the achievements listed below (priority order)

3. **How to Proceed**:

   - Read the achievement you want to tackle
   - Create a SUBPLAN with your specific approach
   - Create an EXECUTION_TASK to log your work
   - Follow the TDD workflow defined in IMPLEMENTATION_START_POINT.md

4. **What You'll Create**:

   - Stable, reproducible community detection with run metadata
   - Ontology-aware edge weighting for better partitions
   - Intelligent summarization with centrality-aware truncation
   - Multi-resolution communities for hierarchical navigation
   - Comprehensive metrics and quality gates
   - Self-improving parameter optimization loop
   - Alternative detector implementations and ensembles

5. **Where to Get Help**:

   - Read IMPLEMENTATION_START_POINT.md for methodology
   - Review existing code:
     - `business/agents/graphrag/community_detection.py`
     - `business/agents/graphrag/community_summarization.py`
     - `business/stages/graphrag/community_detection.py`
   - Check related PLANs:
     - `PLAN_EXTRACTION-QUALITY-ENHANCEMENT.md` (ontology quality)
     - `PLAN_ENTITY-RESOLUTION-REFACTOR.md` (entity quality)
     - `PLAN_GRAPH-CONSTRUCTION-REFACTOR.md` (graph quality)
   - Read technical references:
     - `documentation/technical/COMMUNITY-DETECTION.md`
     - `documentation/technical/COMMUNITY-DETECTION-ALGORITHMS.md`
     - `documentation/technical/SEMANTIC-ENTITIES-RELATIONSHIPS.md`

6. **Project Context**: For essential project knowledge (structure, domain, conventions, architecture), see `LLM/PROJECT-CONTEXT.md`
   - **When to Reference**: New sessions, unfamiliar domains, architecture questions, convention questions
   - **Automatic Injection**: The prompt generator (`generate_prompt.py`) automatically includes project context in generated prompts
   - **Manual Reference**: If you need more detail, read `LLM/PROJECT-CONTEXT.md` directly

**Self-Contained**: This PLAN contains everything you need to execute it.

---

## 📖 What to Read (Focus Rules)

**When working on this PLAN**, follow these focus rules to minimize context:

**✅ READ ONLY**:

- Current achievement section (50-100 lines)
- "Current Status & Handoff" section (30-50 lines)
- Active SUBPLANs (if any exist)
- Summary statistics (for metrics)

**❌ DO NOT READ**:

- Other achievements (unless reviewing)
- Completed achievements
- Full SUBPLAN content (unless creating one)
- Full EXECUTION_TASK content (unless creating one)
- Achievement Addition Log (unless adding achievement)

**Context Budget**: ~200 lines per achievement

**Why**: PLAN defines WHAT to achieve. Reading all achievements at once causes context overload. Focus on current achievement only.

**📖 See**: `LLM/guides/FOCUS-RULES.md` for complete focus rules and examples.

---

## 🎯 Goal

Transform community detection and summarization from a functional but brittle system into a production-grade, self-improving pipeline with: stable community IDs, reproducible runs with version control, ontology-aware graph weighting, intelligent multi-resolution detection, centrality-based summarization, comprehensive quality metrics, and automated parameter optimization—enabling reliable, high-quality topic clustering for GraphRAG retrieval.

---

## 📖 Problem Statement

**Current State - Working But Brittle**:

The community detection system is functional with recent improvements:

- ✅ Louvain algorithm working (switched from hierarchical_leiden)
- ✅ Good modularity scores (~0.63)
- ✅ Weighted edges by relationship type
- ✅ Conservative token management
- ✅ Concurrent summarization with TPM tracking
- ✅ Bulk chunk updates for performance

**Critical Issues**:

**Bug 1: Non-Deterministic Community IDs** ⚠️ CRITICAL

- IDs are index-based: `f"level_{level}_community_{i}"`
- Order-dependent, changes between runs
- **Impact**: Can't diff, can't cache, can't version, downstream references break

**Bug 2: No Run Provenance** ⚠️ CRITICAL

- No tracking of detection parameters (resolution, algorithm, seed, ontology version)
- Can't reproduce results
- Can't distinguish "already done" vs "done with different params"
- **Impact**: Can't validate changes, can't rollback, can't audit

**Bug 3: Graph Drift Undetected** ⚠️ HIGH

- If entities/relations change, communities become stale but chunks say "completed"
- No graph signature to detect drift
- **Impact**: Stale communities used for retrieval, degraded quality

**Bug 4: Token Estimation Inaccurate** ⚠️ HIGH

- Estimation is 8× off (actual: ~1600 tokens/entity, estimated: ~200)
- Conservative caps compensate but waste context
- **Impact**: Summaries truncate too aggressively, lose valuable context

**Missing Features**:

1. **No Ontology Integration**: Edge weights don't use canonical predicate information

   - Canonical predicates should boost weight (+10-20%)
   - Soft-kept/unknown predicates should penalize (-10-20%)
   - **Impact**: Suboptimal partitions, ontology work not leveraged

2. **No Community Size Management**: Single-entity communities filtered, but:

   - Oversized communities (4804 entities) not split
   - Micro-communities (<5) not merged
   - **Impact**: Poor quality for very large/small communities

3. **No Salience-Aware Summarization**:

   - Truncation by count, not importance
   - Most important entities may be excluded
   - **Impact**: Summaries miss key entities, waste tokens on peripheral ones

4. **No Multi-Resolution Structure**:

   - Single resolution (1.0) may not fit all community scales
   - No macro/micro topic layers
   - **Impact**: Either too coarse or too granular, never both

5. **No Quality Metrics Persistence**:

   - Metrics logged but not stored
   - Can't track quality over time
   - Can't optimize parameters systematically
   - **Impact**: No self-improvement loop, manual parameter tuning

6. **No Alternative Detectors**:

   - Louvain only, no Leiden/Infomap/Label Propagation
   - Can't compare or ensemble
   - **Impact**: Stuck with one algorithm's weaknesses

7. **Leiden Fallback Silent**:
   - Falls back to Louvain if graspologic missing
   - Doesn't warn about parameter mismatches (max_cluster_size ignored)
   - **Impact**: Confusing behavior, unmet expectations

**Impact**:

- Community detection works but isn't reproducible or versionable
- Parameter changes can't be validated or rolled back
- Ontology improvements don't propagate to community quality
- Very large communities get poor summaries
- No way to measure or improve quality systematically
- Manual tuning required, no automation
- Production deployments risky (can't guarantee same results)

---

## 🎯 Success Criteria

### Must Have

- [ ] Stable community IDs (hash-based, deterministic)
- [ ] Run metadata persisted (params_hash, graph_signature, all config)
- [ ] Graph drift detection (signature comparison)
- [ ] Ontology-aware edge weighting (+/- for canonical/soft-kept predicates)
- [ ] source_count accuracy (same fix as entity resolution/graph construction)
- [ ] Oversized community splitting (recursive Louvain for >1000 entities)
- [ ] Centrality-aware summarization truncation (PageRank × confidence)
- [ ] Exact token counting (tiktoken integration)
- [ ] Quality metrics persistence (graphrag_metrics collection)
- [ ] All existing functionality preserved
- [ ] All tests passing + 20+ new tests

### Should Have

- [ ] Multi-resolution detection (3 resolutions: 0.8, 1.0, 1.6)
- [ ] Micro-community merging (<5 entities)
- [ ] Predicate profile in summarization prompt
- [ ] Determinism validation (same graph+params → same communities)
- [ ] Leiden detector implementation (proper graspologic integration)
- [ ] Label Propagation detector (fast baseline)
- [ ] Versioned community storage (archive old, track changes)
- [ ] Configuration documentation (all parameters)
- [ ] Quality gates for parameter validation

### Nice to Have

- [ ] Infomap detector implementation
- [ ] Ensemble detection (Louvain + Infomap, NMI-based agreement)
- [ ] Incremental updates (ego-net localized detection)
- [ ] Embedding-guided community refinement
- [ ] Predicate-topic sub-communities
- [ ] Community title generation with contrastive prompts
- [ ] Human-in-the-loop UI for manual refinement
- [ ] Self-improving parameter optimization loop
- [ ] Metrics dashboard

---

## 📋 Scope Definition

### In Scope

1. **Critical Bug Fixes**:

   - Stable community IDs (hash-based)
   - Run metadata and provenance
   - Graph drift detection
   - Token estimation accuracy
   - source_count inflation fix

2. **Ontology Integration**:

   - Load canonical_predicates for edge weighting
   - Boost canonical predicates (+10-20%)
   - Penalize soft-kept/unknown (-10-20%)
   - Type-pair validity bonuses

3. **Community Size Management**:

   - Split oversized communities (>1000)
   - Merge micro-communities (<5)
   - Configurable thresholds

4. **Intelligent Summarization**:

   - Centrality-aware entity/edge selection
   - Exact token counting with tiktoken
   - Predicate profile in prompts
   - Refined truncation strategy

5. **Quality & Observability**:

   - Metrics persistence (graphrag_metrics collection)
   - Quality gates for validation
   - Determinism testing
   - Comprehensive configuration

6. **Multi-Resolution & Alternatives**:
   - Multi-resolution Louvain
   - Leiden detector (proper)
   - Label Propagation baseline
   - Optional: Infomap, ensembles

### Out of Scope

- Complete algorithm redesign (incremental improvement)
- Manual annotation UI implementation (prototype only)
- Real-time incremental detection (foundation only)
- Multi-layer graph support (defer to future)
- Full self-improving loop automation (manual first)
- Graph visualization tools (separate work)
- Community evolution tracking over time (future)

---

## 📏 Size Limits

**⚠️ HARD LIMITS** (Must not exceed):

- **Lines**: 600 lines maximum
- **Estimated Effort**: 32 hours maximum

**Current**: ~1048 lines estimated, 7 priorities, 23 achievements - ⚠️ Exceeds line limit

**If your PLAN exceeds these limits**:

- **MUST** convert to GrammaPlan (not optional)
- See `LLM/guides/GRAMMAPLAN-GUIDE.md` for guidance
- Run `python LLM/scripts/validation/check_plan_size.py @PLAN_FILE.md` to validate

**Validation**:

- Script will **BLOCK** (exit code 1) if limits exceeded
- Warning at 400 lines: "Consider GrammaPlan"
- Error at 600 lines: "MUST convert to GrammaPlan"

---

## 🌳 GrammaPlan Consideration

**Was GrammaPlan considered?**: Yes

**Decision Criteria Checked**:

- [x] Plan would exceed 600 lines? **Yes** ⚠️ **HARD LIMIT**
- [ ] Estimated effort > 32 hours? **No** (estimated ~25-30 hours)
- [ ] Work spans 3+ domains? **No** (single domain: community detection)
- [ ] Natural parallelism opportunities? **No** (sequential work)

**Decision**: **Single PLAN** (Note: This PLAN exceeds line limit but was created before strict enforcement. Should be converted to GrammaPlan if updated.)

**Rationale**:

- Focused scope (community detection and summarization)
- Sequential work (stability → ontology → quality → advanced)
- Single domain (graph analysis)
- **Note**: Line count exceeds limit - consider splitting if major updates needed

**See**: `LLM/guides/GRAMMAPLAN-GUIDE.md` for complete criteria and guidance

---

## 🎯 Desirable Achievements (Priority Order)

**Important Note**: This PLAN lists achievements (WHAT to do), not subplans (HOW to do it).

**Process**:

- Review achievements
- Select one to work on
- Create SUBPLAN with your approach
- Create EXECUTION_TASK to log work
- Execute

---

### Priority 0: CRITICAL - Stability & Reproducibility

**Achievement 0.1**: Stable Community IDs Implemented

- Replace index-based IDs with hash-based: `sha1(sorted(node_ids))[:12]`
- Format: `level_{level}_{hash}` or `lvl{level}-{hash}`
- Ensures same nodes → same ID across runs
- Enables diffs, caching, versioning, stable references
- Test: Same graph twice → identical community IDs
- Success: Community IDs deterministic and stable
- Effort: 2-3 hours
- Files: `business/agents/graphrag/community_detection.py`

**Achievement 0.2**: Run Metadata & Provenance Implemented

- Create `graphrag_runs` collection for run tracking
- Store: `run_id`, `stage`, `params_hash`, `graph_signature`, `ontology_version`, all config
- Compute `params_hash = sha1(json.dumps(params, sort_keys=True))[:12]`
- Check before detection: same params_hash + graph_signature → skip rerun
- Stamp `run_id` and `params_hash` on all community documents
- Test: Same params → skip detection, different params → re-run
- Success: Full run provenance, reproducible results
- Effort: 3-4 hours
- Files: `business/stages/graphrag/community_detection.py`, new `business/services/graphrag/run_metadata.py`

**Achievement 0.3**: Graph Signature & Drift Detection Implemented

- Compute graph signature: hash of sorted `(subject_id, object_id, predicate, round(confidence,2))`
- Store with run metadata
- Compare signature before reusing communities
- If drift detected: re-run detection, mark old run as stale
- Test: Entity/relation changes → graph signature changes → triggers re-detection
- Success: Stale communities never used
- Effort: 2-3 hours
- Files: `business/stages/graphrag/community_detection.py`

**Achievement 0.4**: source_count Accuracy Fixed (Community Context)

- Apply same pattern as entity resolution (Achievement 3.5.3) and graph construction (Achievement 0.2)
- Only increment if chunk_id not in source_chunks
- Check if applicable to community updates (may not be relevant)
- Review and document
- Test: Reruns don't inflate source_count (if applicable)
- Success: Accurate counts or confirmed not applicable
- Effort: 1-2 hours
- Files: Review `business/stages/graphrag/community_detection.py`

---

### Priority 1: HIGH - Ontology Integration & Quality

**Achievement 1.1**: Ontology-Aware Edge Weighting Implemented

- Load canonical_predicates and predicate_map in community detection agent
- Apply weight multipliers:
  - Canonical predicates: +15% weight (multiply by 1.15)
  - Non-canonical but mapped: 0% (neutral, multiply by 1.0)
  - Soft-kept/unknown: -15% weight (multiply by 0.85)
  - Co-occurrence without LLM corroboration: additional -10% (multiply by 0.9)
- Combine with existing relationship_type multipliers
- Clamp final weight to [0.1, 1.0]
- Test: Canonical predicates get higher weight → affect partitions
- Success: Ontology quality improvements propagate to communities
- Effort: 3-4 hours
- Files: `business/agents/graphrag/community_detection.py`, `core/libraries/ontology/loader.py`

**Achievement 1.2**: Type-Pair Validity Bonuses Implemented

- For each edge, check if type-pair is valid for predicate (from ontology constraints)
- Valid type-pairs: +10% weight bonus (multiply by 1.1)
- Invalid type-pairs: -20% penalty (multiply by 0.8)
- Examples: `works_at: PERSON→ORGANIZATION` gets bonus, `works_at: CONCEPT→CONCEPT` gets penalty
- Test: Type-valid edges weighted higher
- Success: Type-aware community formation
- Effort: 2-3 hours
- Files: `business/agents/graphrag/community_detection.py`

**Achievement 1.3**: Community Size Management Implemented

- **Split oversized**: If community size > split_threshold (default 1000):
  - Extract subgraph
  - Run Louvain with higher resolution (1.5-2.0)
  - Create sub-communities with parent lineage
  - Community IDs: `{parent_id}-p{n}` for partitions
- **Merge micro**: If community size < merge_threshold (default 5):
  - Find nearest neighbor by shared edges
  - Merge if cut density acceptable
  - Or keep as separate if highly coherent
- Configurable via `GRAPHRAG_COMMUNITY_SPLIT_THRESHOLD` and `GRAPHRAG_COMMUNITY_MERGE_THRESHOLD`
- Test: 4804-entity community splits into sub-communities, <5 entity communities merge or are filtered
- Success: Balanced community sizes (5-1000 range)
- Effort: 4-6 hours
- Files: `business/agents/graphrag/community_detection.py`

**Achievement 1.4**: Quality Metrics Persistence Implemented

- Create `graphrag_metrics` collection
- Store per-run metrics:
  - Graph: nodes, edges, density, edge-to-node ratio
  - Detection: modularity, total_communities, size distribution (histogram), coverage
  - Quality: mean/median/min/max coherence, percentile bands (p25, p50, p75)
  - Summarization: total summaries, avg/min/max length, truncation rate, error rate
  - Config: params_hash, ontology_version, algorithm, resolution, all env vars
- Key by `run_id`
- Enable trend analysis and quality gates
- Test: Detection run → metrics persisted to DB
- Success: Can query historical quality metrics
- Effort: 3-4 hours
- Files: `business/stages/graphrag/community_detection.py`, new `business/services/graphrag/metrics.py`

---

### Priority 2: HIGH - Intelligent Summarization

**Achievement 2.1**: Exact Token Counting Implemented

- Integrate `tiktoken` library for accurate token counting
- Replace estimation with exact pre-call counting
- Log `estimated_tokens` vs `actual_tokens` (if accessible from response)
- Refine estimation model based on actual usage
- Adjust truncation thresholds based on accurate counting
- Test: Token count accuracy within 5% of actual
- Success: No more 8× estimation errors, optimal context usage
- Effort: 2-3 hours
- Files: `business/agents/graphrag/community_summarization.py`

**Achievement 2.2**: Centrality-Aware Summarization Selection

- Before truncation, compute node centrality in community subgraph:
  - PageRank or betweenness centrality
  - Or degree centrality (simpler)
- Score entities: `centrality × entity.confidence × entity.source_count`
- Score relationships: `(subject_score + object_score) / 2 × rel.confidence × rel.source_count`
- Select top-K entities and top-M relationships by score, not arbitrary count
- Test: Important entities (high centrality + confidence) always included
- Success: Better summaries with fewer tokens, key information preserved
- Effort: 3-4 hours
- Files: `business/agents/graphrag/community_summarization.py`

**Achievement 2.3**: Predicate Profile Enhancement

- For each community, compute predicate distribution (top 5-10 by frequency/weight)
- Include predicate profile in summarization prompt:
  - "This community focuses on: teaches, uses, located_in, implements (top relations)"
- Steers LLM to emphasize dominant relationship types
- Test: Summaries better reflect community's relationship patterns
- Success: More coherent, focused summaries
- Effort: 2-3 hours
- Files: `business/agents/graphrag/community_summarization.py`

---

### Priority 3: HIGH - Multi-Resolution & Detection Improvements

**Achievement 3.1**: Multi-Resolution Louvain Implemented

- Run Louvain at multiple resolutions (default: 0.8, 1.0, 1.6)
- Store each resolution as separate level (level 1, 2, 3)
- Allow entities to appear in multiple levels (multi-scale membership)
- Configurable via `GRAPHRAG_COMMUNITY_MULTIRES` (comma-separated)
- Capture macro themes (0.8) and micro topics (1.6)
- Test: Three resolution runs produce different community scales
- Success: Hierarchical navigation via multiple resolution layers
- Effort: 4-5 hours
- Files: `business/agents/graphrag/community_detection.py`, `business/stages/graphrag/community_detection.py`

**Achievement 3.2**: Leiden Detector Implemented (Proper)

- Implement Leiden via NetworkX or graspologic (proper integration)
- Handle graspologic dependency gracefully (optional dependency)
- If graspologic available: use hierarchical_leiden with proper params
- If NetworkX 3.5+: use `leiden_communities`
- Fallback to Louvain if neither available
- Warn clearly about algorithm and parameter constraints
- Configurable via `GRAPHRAG_COMMUNITY_ALGO=leiden`
- Test: Leiden detection works, produces better communities (connected, higher modularity)
- Success: Leiden as primary, Louvain as proven fallback
- Effort: 3-4 hours
- Files: `business/agents/graphrag/community_detection.py`

**Achievement 3.3**: Label Propagation Baseline Implemented

- Implement fast Label Propagation detector
- Use for quick first-pass or very large graphs
- Configurable via `GRAPHRAG_COMMUNITY_ALGO=label_prop`
- Non-deterministic: run 3 times, take consensus (if needed for quality)
- Document limitations (flat partition, unstable)
- Test: Label Propagation runs fast, produces reasonable partition
- Success: Fast baseline available for comparison
- Effort: 2-3 hours
- Files: `business/agents/graphrag/community_detection.py`

**Achievement 3.4**: Quality Gates Implemented

- Before accepting detection results, validate quality:
  - Modularity > threshold (default 0.3)
  - Coverage > threshold (default 0.7)
  - No giant communities (max size check)
  - No excessive singleton communities
- If quality gates fail: try alternative params or log warning
- Configurable thresholds
- Test: Poor detection (low modularity) triggers quality gate failure
- Success: Bad runs prevented automatically
- Effort: 2-3 hours
- Files: `business/stages/graphrag/community_detection.py`

---

### Priority 4: MEDIUM - Advanced Detection Features

**Achievement 4.1**: Infomap Detector Implemented

- Implement Infomap detector (information-theoretic)
- Good for flow-based/directed graphs
- Different community perspective than modularity methods
- Configurable via `GRAPHRAG_COMMUNITY_ALGO=infomap`
- Use for validation/comparison with Louvain
- Test: Infomap produces different but reasonable communities
- Success: Alternative detector for validation
- Effort: 3-4 hours
- Files: `business/agents/graphrag/community_detection.py`

**Achievement 4.2**: Ensemble Detection Implemented

- Run two detectors (e.g., Louvain + Infomap)
- Compute Normalized Mutual Information (NMI) between partitions
- Keep communities where both agree (high-precision core)
- For contested regions: prefer partition with higher intra-community edge weight
- Configurable via `GRAPHRAG_COMMUNITY_ENSEMBLE=louvain,infomap`
- Test: Ensemble produces more stable communities
- Success: Robustness improvement via ensembling
- Effort: 4-5 hours
- Files: New `business/agents/graphrag/community_ensemble.py`

**Achievement 4.3**: Incremental Community Updates Implemented

- When new entities/relations added:
  - Localize to affected ego-nets (2-hop neighborhood)
  - Run Louvain only on affected subgraph
  - Preserve run_id lineage, mark affected communities as `version+1`
  - Propagate updates to chunk assignments
- Enables near-real-time detection for continuous ingestion
- Configurable via `GRAPHRAG_COMMUNITY_INCREMENTAL=true`
- Test: New entity → only affected communities re-detected
- Success: Efficient updates for continuous ingestion
- Effort: 5-6 hours
- Files: `business/stages/graphrag/community_detection.py`

---

### Priority 5: MEDIUM - Advanced Summarization

**Achievement 5.1**: Embedding-Guided Community Refinement

- For each community, compute entity embeddings (name + description)
- Run HDBSCAN or k-means on embeddings within community
- If clustering improves cohesion (silhouette score) and edge density maintains:
  - Split community along embedding clusters
  - Create sub-communities
- Optional feature (default off)
- Test: Diffuse community splits into coherent sub-topics
- Success: Better topic purity
- Effort: 4-5 hours
- Files: `business/agents/graphrag/community_detection.py`

**Achievement 5.2**: Predicate-Topic Sub-Communities

- Within large community, cluster edges by predicate family
- Families: pedagogical (teaches, explains), technical (uses, implements, depends_on), organizational (works_at, part_of)
- If predicate families separate cleanly: split community by role
- Test: Community with mixed pedagogical + technical content splits cleanly
- Success: Role-consistent sub-communities
- Effort: 3-4 hours
- Files: `business/agents/graphrag/community_detection.py`

**Achievement 5.3**: Community Title Generation

- Generate candidate titles using:
  - Entity/type histogram (most common types)
  - Predicate profile (dominant relationships)
  - Top central entities (PageRank top-3)
- Use LLM with contrastive prompt to select best title
- Or: Template-based title generation (faster)
- Store `title_candidates`, `selected_title`, `title_features`
- Test: Communities get descriptive, non-generic titles
- Success: Human-readable community names
- Effort: 3-4 hours
- Files: `business/agents/graphrag/community_summarization.py`

---

### Priority 6: MEDIUM - Self-Improving Loop (Foundation)

**Achievement 6.1**: Parameter Optimization Framework

- Define parameter search space:
  - Resolution: [0.5, 0.7, 0.8, 1.0, 1.2, 1.5, 1.8, 2.0]
  - Algorithm: [leiden, louvain, infomap, label_prop]
  - Split threshold: [500, 1000, 2000]
  - Ontology weighting: [off, conservative, aggressive]
- Run detection with each configuration
- Record metrics (modularity, coverage, coherence)
- Rank by quality score
- Store results for offline analysis
- Test: Grid search finds optimal parameters
- Success: Can systematically evaluate parameter combinations
- Effort: 4-5 hours
- Files: New `scripts/optimize_community_params.py`

**Achievement 6.2**: Quality Gates & Validation

- Define acceptable quality ranges:
  - Modularity: > 0.3 (good structure)
  - Coverage: > 0.7 (most nodes in communities)
  - Coherence: > 0.4 (internally connected)
  - Stability: NMI > 0.9 (deterministic within tolerance)
- Before accepting run: validate against gates
- If fail: try next parameter set or warn
- Configurable thresholds
- Test: Poor run rejected by quality gates
- Success: Automated quality validation
- Effort: 2-3 hours
- Files: `business/stages/graphrag/community_detection.py`

**Achievement 6.3**: Self-Improving Loop (Manual Orchestration)

- Script to orchestrate improvement:
  1. Run baseline detection, capture metrics
  2. Try parameter variations
  3. Compare metrics vs baseline
  4. Select best (highest modularity × coverage × coherence)
  5. Promote best run_id as "current"
  6. Document learnings
- Manual for now (automated in future)
- Test: Script finds better parameters than default
- Success: Repeatable improvement process
- Effort: 3-4 hours
- Files: New `scripts/self_improve_communities.py`

---

### Priority 7: LOW - Testing & Documentation

**Achievement 7.1**: Comprehensive Test Suite Created

- Unit tests for all new functions:
  - Stable ID generation
  - Params hash computation
  - Graph signature calculation
  - Ontology weight application
  - Centrality scoring
  - Token counting accuracy
  - Quality gate validation
- Integration tests:
  - Full detection pipeline
  - Multi-resolution detection
  - Oversized community splitting
  - Ensemble detection
- Test cases:
  - Same graph → same IDs
  - Parameter changes → re-detection
  - Graph drift → re-detection
  - Quality gates → rejection
  - Large communities → splitting
- Success: >75% test coverage
- Effort: 6-8 hours
- Files: New `tests/business/agents/graphrag/test_community_detection.py`, `tests/business/stages/graphrag/test_community_detection_stage.py`

**Achievement 7.2**: Configuration Documentation Created

- Document all parameters:
  - `GRAPHRAG_COMMUNITY_ALGO` (leiden/louvain/infomap/label_prop)
  - `GRAPHRAG_RESOLUTION` (default 1.0)
  - `GRAPHRAG_COMMUNITY_MIN_SIZE` (default 2)
  - `GRAPHRAG_COMMUNITY_MAX_SIZE` (default 50, soft limit)
  - `GRAPHRAG_COMMUNITY_SPLIT_THRESHOLD` (default 1000)
  - `GRAPHRAG_COMMUNITY_MERGE_THRESHOLD` (default 5)
  - `GRAPHRAG_COMMUNITY_USE_ONTOLOGY_WEIGHTS` (default true)
  - `GRAPHRAG_COMMUNITY_MULTIRES` (default "1.0", or "0.8,1.0,1.6")
  - `GRAPHRAG_RANDOM_SEED` (default 42)
  - `GRAPHRAG_MAX_DENSITY` (from graph construction)
  - All summarization params (TPM, RPM, model, max_context_tokens)
- Add to configuration guide
- Document in README
- Success: All parameters documented and configurable
- Effort: 2-3 hours
- Files: `documentation/guides/COMMUNITY-DETECTION-CONFIG.md`

**Achievement 7.3**: Refactor Documentation Created

- Document: `documentation/technical/COMMUNITY-DETECTION-REFACTOR.md`
- Include:
  - What was changed and why
  - Before/after comparison
  - Migration guide (how to update existing deployments)
  - Performance improvements
  - Quality improvements
  - Breaking changes (community ID format change)
  - Reproducibility guarantees
- Success: Comprehensive refactor documentation
- Effort: 3-4 hours
- Files: New `documentation/technical/COMMUNITY-DETECTION-REFACTOR.md`

---

## 📋 Achievement Addition Log

**Dynamically Added Achievements** (if gaps discovered during execution):

(Empty initially - will be populated as gaps are discovered)

---

## 🔄 Subplan Tracking (Updated During Execution)

**Subplans Created for This PLAN**:

(Will be updated as subplans are created and completed)

---

## 🔗 Constraints & Integration

### Technical Constraints

1. **Backward Compatibility**:

   - Community ID format change is **breaking**
   - Migration path required for existing systems
   - Must document upgrade process
   - Can provide migration script

2. **Database Changes**:

   - New collections: `graphrag_runs`, `graphrag_metrics`
   - New fields on `communities` documents
   - New indexes required
   - Migration for existing communities (optional)

3. **Dependency on Other PLANs**:

   - **PLAN_GRAPH-CONSTRUCTION-REFACTOR.md**: Graph quality affects community quality
   - **PLAN_ENTITY-RESOLUTION-REFACTOR.md**: Entity quality affects graph structure
   - **PLAN_EXTRACTION-QUALITY-ENHANCEMENT.md**: Ontology quality affects edge weighting
   - Can start this PLAN now, but benefits increase as other plans complete

4. **Performance Requirements**:
   - Must handle 50k+ entities efficiently
   - Summarization must complete in reasonable time (<30min for all communities)
   - Multi-resolution shouldn't exceed 3× baseline time
   - Incremental updates should be <5% of full detection time

### Process Constraints

1. **Test-First Always**:

   - Write tests before implementing changes
   - No cheating (fix implementation, not tests)
   - All tests must pass before marking achievement complete

2. **Incremental Refactor**:

   - Small, testable changes
   - Each achievement independently testable
   - Can pause/resume at achievement boundaries

3. **Documentation**:
   - All changes documented
   - Migration guide for breaking changes
   - Config changes documented

---

## 📚 References & Context

### Related Plans

**PLAN_GRAPH-CONSTRUCTION-REFACTOR.md**:

- **Status**: Planning (not started)
- **Relationship**: Sequential (graph construction → community detection)
- **Dependency**: Better graph quality → better communities
- **Similar Fixes**: source_count inflation, ontology integration
- **Timing**: Can start this PLAN in parallel, but validates together

**PLAN_ENTITY-RESOLUTION-REFACTOR.md**:

- **Status**: Paused (Priorities 0-3 and 3.5 complete)
- **Relationship**: Upstream (entity quality → graph quality → community quality)
- **Dependency**: Stable entity IDs, accurate source_count feed into communities
- **Timing**: Entity resolution foundational work complete

**PLAN_EXTRACTION-QUALITY-ENHANCEMENT.md**:

- **Status**: Paused (Priority 0-1 complete)
- **Relationship**: Upstream (extraction quality → all downstream stages)
- **Dependency**: Ontology canonical predicates used for edge weighting
- **Timing**: Ontology validated and excellent (100% canonical ratio)

**PLAN_STRUCTURED-LLM-DEVELOPMENT.md**:

- **Status**: Paused (foundation complete)
- **Relationship**: Meta (methodology for this PLAN)
- **Dependency**: Use IMPLEMENTATION_START_POINT.md, IMPLEMENTATION_END_POINT.md, IMPLEMENTATION_RESUME.md
- **Timing**: Methodology ready, resume protocol tested with this PLAN

### Code References

**Current Implementation**:

- `business/agents/graphrag/community_detection.py` - Detection agent to refactor
- `business/agents/graphrag/community_summarization.py` - Summarization agent to refactor
- `business/stages/graphrag/community_detection.py` - Stage orchestration to refactor
- `core/models/graphrag.py` - CommunitySummary model

**Dependencies**:

- `core/libraries/ontology/loader.py` - Load canonical predicates for weighting
- `core/libraries/concurrency.py` - TPM tracking for summarization
- `business/services/graphrag/indexes.py` - Index management
- `core/libraries/database.py` - Batch operations

**Tests**:

- `tests/business/agents/graphrag/test_community_detection.py` (if exists, else create)
- `tests/business/stages/graphrag/test_community_detection_stage.py` (if exists, else create)

**Technical References** (READ THESE):

- `documentation/technical/COMMUNITY-DETECTION.md` - Algorithm guide (comprehensive)
- `documentation/technical/COMMUNITY-DETECTION-ALGORITHMS.md` - Algorithm comparison
- `documentation/technical/SEMANTIC-ENTITIES-RELATIONSHIPS.md` - Graph density best practices

### External Dependencies

**New Dependencies to Add**:

- `tiktoken>=0.5.0` - Exact token counting
- `graspologic>=3.0.0` (optional) - Proper hierarchical Leiden
- Optional: `hdbscan>=0.8.0` - For embedding-guided refinement
- Optional: `scikit-learn>=1.3.0` - For NMI, k-means

### ChatGPT Analysis Reference

**Source**: ChatGPT review of community_detection.py and community_summarization.py (November 6, 2025)

**Critical Issues** (Priority 0):

1. Non-deterministic IDs → Achievement 0.1
2. No run provenance → Achievement 0.2
3. Graph drift undetected → Achievement 0.3
4. Token estimation inaccurate → Achievement 2.1

**High-Value Improvements** (Priority 1-2):

1. Ontology-aware weighting → Achievement 1.1, 1.2
2. Size management → Achievement 1.3
3. Quality metrics → Achievement 1.4
4. Centrality-aware summarization → Achievement 2.2
5. Predicate profiles → Achievement 2.3

**Advanced Features** (Priority 3-6):

1. Multi-resolution → Achievement 3.1
2. Alternative detectors → Achievement 3.2, 3.3, 4.1
3. Ensemble → Achievement 4.2
4. Incremental updates → Achievement 4.3
5. Self-improving loop → Achievement 6.1, 6.2, 6.3

---

## 📦 Archive Location

**Archive Location**: `documentation/archive/community-detection-partial-nov2025/`

**Archive Structure**:

```
documentation/archive/community-detection-partial-nov2025/
├── planning/
│   └── PLAN_COMMUNITY-DETECTION-REFACTOR.md
├── subplans/
│   └── (SUBPLANs will be archived here)
└── execution/
    └── (EXECUTION_TASKs will be archived here)
```

---

## ⏱️ Time Estimates

**Priority 0** (Stability & Reproducibility): 8-12 hours  
**Priority 1** (Ontology & Quality): 12-17 hours  
**Priority 2** (Intelligent Summarization): 7-10 hours  
**Priority 3** (Multi-Resolution & Detection): 9-14 hours  
**Priority 4** (Advanced Detection): 12-15 hours  
**Priority 5** (Advanced Summarization): 10-13 hours  
**Priority 6** (Self-Improving Loop): 9-12 hours  
**Priority 7** (Testing & Documentation): 11-15 hours

**Total**: 78-108 hours (if all priorities completed)

**Recommended Focus**: Priorities 0-2 (27-39 hours) for critical fixes, ontology integration, and intelligent summarization

---

## 📊 Success Metrics

### Bug Fixes (Priority 0)

- Community ID stability: Target 100% same graph → same IDs
- Run reproducibility: Target 100% same params → same communities (or skip)
- Graph drift detection: Target 100% detection of entity/relation changes
- Token estimation accuracy: Target <10% error (from current ~700% error)

### Quality Improvements (Priority 1)

- Ontology impact: Target measurable improvement in modularity/coherence
- Community size distribution: Target 5-1000 entity range (no giants, no micro)
- Quality metrics: Target modularity >0.4, coverage >0.8, coherence >0.5
- Summary quality: Target key entities always included, better coherence

### Advanced Features (Priority 3-6)

- Multi-resolution: Target 3 scales working, meaningful hierarchy
- Alternative detectors: Target Leiden, Infomap, Label Prop all functional
- Ensemble: Target NMI-based agreement improving stability
- Self-improving loop: Target automated parameter optimization reducing manual tuning

### Test Coverage

- Unit tests: Target 50+ test cases
- Integration tests: Target 15+ scenarios
- Coverage: Target >75% line coverage
- All tests passing: Target 100%

---

## 🚀 Immediate Next Steps

1. **Review This Plan** - Confirm scope, priorities, and approach

2. **Read Technical References** - Understand algorithms and best practices:

   - `documentation/technical/COMMUNITY-DETECTION.md`
   - `documentation/technical/COMMUNITY-DETECTION-ALGORITHMS.md`
   - `documentation/technical/SEMANTIC-ENTITIES-RELATIONSHIPS.md`

3. **Add Dependencies** - Add `tiktoken`, optionally `graspologic` to requirements.txt

4. **Create SUBPLAN_01**: Achievement 0.1 (Stable Community IDs)

   - Design hash-based ID generation
   - Write tests first (same graph → same IDs)
   - Implement ID generator

5. **Create SUBPLAN_02**: Achievement 0.2 (Run Metadata)

   - Design run metadata schema
   - Create graphrag_runs collection
   - Implement params_hash computation
   - Write tests

6. **Continue**: Work through Priority 0 systematically, then proceed to Priority 1

---

## 📝 Current Status & Handoff (For Pause/Resume)

**Last Updated**: 2025-11-06 21:15 UTC  
**Status**: Planning Complete - Ready to Start

**To Start Work**:

1. **Read IMPLEMENTATION_START_POINT.md** - Refresh on methodology
2. **Review this PLAN** completely
3. **Read technical references** (COMMUNITY-DETECTION\*.md files)
4. **Select Achievement 0.1** (highest priority)
5. **Create work-space/subplans/SUBPLAN_COMMUNITY-DETECTION-REFACTOR_01.md**
6. **Create work-space/execution/EXECUTION_TASK_COMMUNITY-DETECTION-REFACTOR_01_01.md**
7. **Follow TDD workflow**

**If Resuming Later**:

1. **Follow IMPLEMENTATION_RESUME.md** - Complete resume protocol (mandatory)
2. Read "Current Status & Handoff" section (this section)
3. Review Subplan Tracking (see what's done)
4. Review Achievement Addition Log (see what's pending)
5. Select next achievement based on priority
6. Create SUBPLAN and continue

**Context Preserved**: This section + Subplan Tracking + Achievement Log = full context

---

## ✅ Completion Criteria

**This PLAN is Complete When**:

1. [ ] Stable community IDs implemented and tested
2. [ ] Run metadata and provenance system working
3. [ ] Graph drift detection preventing stale communities
4. [ ] Ontology-aware edge weighting improving partitions
5. [ ] Community size management (split/merge) working
6. [ ] Quality metrics persisted and queryable
7. [ ] Exact token counting integrated
8. [ ] Centrality-aware summarization producing better results
9. [ ] Multi-resolution detection providing hierarchical navigation
10. [ ] At least one alternative detector (Leiden or Infomap) working
11. [ ] Quality gates preventing bad runs
12. [ ] All tests passing (existing + new)
13. [ ] Documentation complete (config guide, refactor guide)
14. [ ] Production validation successful
15. [ ] No regression in community quality

**Partial Completion Option**:

- Priority 0-1 complete: Foundation solid (stable, reproducible, ontology-aware)
- Priority 0-2 complete: Intelligent system (+ better summarization)
- Priority 0-3 complete: Production-ready (+ multi-resolution, alternatives)
- Priority 0-6 complete: Advanced system (+ self-improving loop)

---

## 🎯 Expected Outcomes

### Short-term (After Priority 0)

- Reproducible community detection
- Stable community IDs
- Graph drift detection
- No more 8× token estimation errors
- Confidence in results

### Medium-term (After Priority 1-2)

- Ontology improvements propagate to communities
- Optimal community sizes (5-1000 range)
- Better summaries with less token waste
- Quality metrics for continuous improvement
- Production-ready system

### Long-term (After Priority 3-6)

- Multi-resolution hierarchical communities
- Multiple detection algorithms for validation
- Self-improving parameter optimization
- Ensemble methods for robustness
- Incremental updates for real-time systems
- Comprehensive metrics dashboard

---

## 🔥 Critical Dependencies

**Blocking**:

- None - Can start immediately

**Benefits from** (better inputs):

- PLAN_GRAPH-CONSTRUCTION-REFACTOR.md Priority 0-1: Better graph quality → better communities
- PLAN_ENTITY-RESOLUTION-REFACTOR.md Priorities 0-3: Stable entities → stable graph
- PLAN_EXTRACTION-QUALITY-ENHANCEMENT.md Priority 1: Ontology for edge weighting

**Recommended Sequencing**:

1. Start PLAN_COMMUNITY-DETECTION-REFACTOR.md Priority 0 (stability, reproducibility)
2. Parallel: Complete PLAN_GRAPH-CONSTRUCTION-REFACTOR.md Priority 0 (critical bugs)
3. Continue PLAN_COMMUNITY-DETECTION-REFACTOR.md Priority 1 (ontology integration)
4. Complete both together for end-to-end validation

---

## 🚀 Why This Plan Now

**Motivation**:

1. **Stability**: Current system works but IDs are unstable → can't version or cache
2. **Reproducibility**: Can't reproduce runs → risky for production
3. **Ontology Gap**: Not leveraging canonical predicates → missing quality improvements
4. **Token Waste**: 8× estimation error → truncating too aggressively
5. **Quality Unknown**: No metrics → can't measure or improve
6. **Dependencies Ready**: Entity resolution and extraction are solid

**Impact of Completion**:

- Production-ready community detection with guarantees
- Ontology improvements finally propagate to end results
- Intelligent resource usage (tokens, compute)
- Measurable quality with improvement path
- Foundation for self-improving system

---

**Status**: PLAN Created and Ready  
**Next**: Review plan, read technical references, create first SUBPLAN (Achievement 0.1 - Stable Community IDs)
