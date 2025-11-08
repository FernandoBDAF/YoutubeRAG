# PLAN: Entity Resolution Refactor & Quality Enhancement

**Status**: Planning  
**Created**: 2025-11-06 20:30 UTC  
**Goal**: Refactor entity resolution to fix critical issues, add cross-chunk resolution, implement fuzzy matching, and dramatically improve quality  
**Priority**: CRITICAL - Foundational for graph quality

---

## 📖 Context for LLM Execution

**If you're an LLM reading this to execute work**:

1. **What This Plan Is**: Comprehensive refactor of entity resolution stage to fix critical bugs and implement proper cross-chunk resolution
2. **Your Task**: Implement the achievements listed below (priority order)
3. **How to Proceed**:
   - Read the achievement you want to tackle
   - Create a SUBPLAN with your specific approach
   - Create an EXECUTION_TASK to log your work
   - Follow the TDD workflow defined in IMPLEMENTATION_START_POINT.md
4. **What You'll Create**:
   - Refactored entity resolution agent with fuzzy matching
   - Cross-chunk candidate lookup system
   - Atomic upsert operations with merge policies
   - LLM gating and description merge optimization
   - Comprehensive test suites
   - Performance optimizations (batching, caching)
   - Observability and quality metrics
5. **Where to Get Help**:

   - Read IMPLEMENTATION_START_POINT.md for methodology
   - Review existing code: `business/agents/graphrag/entity_resolution.py`, `business/stages/graphrag/entity_resolution.py`
   - Check PLAN_ENTITY-RESOLUTION-ANALYSIS.md (analysis plan, complementary)
   - Review QUALITY-IMPROVEMENTS-PLAN.md (context)

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

Refactor entity resolution to implement proper cross-chunk resolution with fuzzy matching, fix critical bugs (unused similarity threshold, canonical ID drift, LLM overuse), add blocking + candidate merge, implement atomic operations, and establish quality metrics - transforming it from a per-chunk deduplicator to a true cross-corpus entity resolution system.

---

## 📖 Problem Statement

**Current State - Critical Issues Identified**:

**Bug 1: NOT Resolving Across Chunks** ⚠️ CRITICAL

- `EntityResolutionStage.handle_doc()` sends only current chunk: `[extraction_data]`
- Each chunk creates its own entities independently
- Same entity mentioned in 100 chunks → 100 duplicate entities
- **Impact**: Graph is full of duplicates, communities are fragmented

**Bug 2: Similarity Threshold Unused** ⚠️ CRITICAL

- `similarity_threshold` parameter exists but never applied
- Resolution only groups by exact normalized string match
- No fuzzy matching, no near-duplicate merging
- **Impact**: "Jason Ku" and "J. Ku" are separate entities

**Bug 3: Canonical ID Drift** ⚠️ HIGH

- `entity_id = generate_entity_id(canonical_name)`
- Same entity gets different IDs if canonical name varies
- No stable ID across aliases
- **Impact**: Entity fragmentation, broken relationships

**Bug 4: LLM Overuse** ⚠️ HIGH

- LLM called for ANY entity with >1 description
- No checking if descriptions are near-duplicates
- Expensive, slow, unnecessary
- **Impact**: High costs, slow processing

**Missing Features**:

1. **No Cross-Chunk Candidate Lookup**: Can't find existing entities in DB
2. **No Fuzzy Matching**: No string similarity, no embedding comparison
3. **No Blocking Strategy**: Can't efficiently find candidates
4. **No Atomic Operations**: Race conditions in update/insert
5. **No Merge Policy**: Simple mean confidence, no weighted voting
6. **No Type Consistency**: Doesn't handle type conflicts properly
7. **No Caching**: Repeated DB lookups for same entities
8. **No Metrics**: Can't measure false merges, missed merges
9. **No Batching**: Processes one chunk at a time inefficiently
10. **No Provenance**: Can't audit merge decisions

**Impact**:

- Entity count inflated 10-100× (thousands of duplicates)
- Graph quality severely degraded
- Community detection sees fragments instead of unified entities
- High API costs from unnecessary LLM calls
- Slow processing from repeated DB queries
- Can't validate or improve quality without metrics

---

## 🎯 Success Criteria

### Must Have

- [ ] Cross-chunk resolution implemented (candidate lookup + merge)
- [ ] Similarity threshold actively used in fuzzy matching
- [ ] Stable entity IDs across aliases (UUIDv5 or deterministic hash)
- [ ] LLM gating implemented (only for divergent descriptions)
- [ ] Atomic upsert operations (no race conditions)
- [ ] String similarity matching (Jaro-Winkler or RapidFuzz)
- [ ] Type consistency rules implemented
- [ ] Blocking strategy for candidate search
- [ ] All existing tests passing + 20+ new tests
- [ ] Entity count reduced by 50%+ after refactor (proof of deduplication)

### Should Have

- [ ] Embedding-based similarity (optional, configurable)
- [ ] Weighted confidence model (source_count + agreement)
- [ ] Description similarity checking (Jaccard/cosine)
- [ ] Acronym/alias expansion rules
- [ ] Batching across chunks implemented
- [ ] LRU cache for recent decisions
- [ ] Provenance tracking (merge audit log)
- [ ] Unique indexes on normalized fields
- [ ] Metrics: false merge rate, missed merge rate, LLM call reduction
- [ ] Performance: 3-5× faster processing

### Nice to Have

- [ ] Multilingual normalization (accent folding)
- [ ] Entity disambiguation UI (for manual review)
- [ ] Incremental resolution (new chunks don't reprocess all)
- [ ] Resolution quality dashboard
- [ ] A/B testing framework for threshold tuning

---

## 📋 Scope Definition

### In Scope

1. **Critical Bug Fixes**:

   - Cross-chunk candidate lookup
   - Similarity threshold application
   - Stable entity IDs
   - LLM gating

2. **Core Algorithm Improvements**:

   - Blocking + candidate merge
   - Fuzzy string matching
   - Type consistency rules
   - Confidence weighting
   - Description similarity

3. **Data Model Enhancements**:

   - Atomic upsert operations
   - Normalized field indexes
   - Provenance tracking
   - Merge audit logs

4. **Performance Optimizations**:

   - Batching across chunks
   - LRU caching
   - Token estimation
   - Rate limiting improvements

5. **Quality & Observability**:
   - False merge detection
   - Missed merge detection
   - Resolution metrics
   - Test coverage expansion

### Out of Scope

- Machine learning-based entity linking (use rule-based + LLM)
- Real-time resolution monitoring dashboard (basic metrics only)
- Complete entity resolution algorithm redesign (incremental refactor)
- Graph construction changes (entity resolution only)
- Manual annotation UI (future enhancement)

---

## 📏 Size Limits

**⚠️ HARD LIMITS** (Must not exceed):

- **Lines**: 600 lines maximum
- **Estimated Effort**: 32 hours maximum

**Current**: ~1178 lines estimated, 7 priorities, 31 achievements - ⚠️ Exceeds line limit

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
- [ ] Work spans 3+ domains? **No** (single domain: entity resolution)
- [ ] Natural parallelism opportunities? **No** (sequential work)

**Decision**: **Single PLAN** (Note: This PLAN exceeds line limit but was created before strict enforcement. Should be converted to GrammaPlan if updated.)

**Rationale**:

- Focused scope (entity resolution refactor and quality)
- Sequential work (bugs → core → data model → performance → quality → advanced)
- Single domain (entity resolution)
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

### Priority 0: CRITICAL - Bug Fixes & Foundation

**Achievement 0.1**: Cross-Chunk Candidate Lookup Implemented

- Implement `_find_db_candidates(name, type, aliases)` in stage
- Query entities collection for matches on normalized names/aliases
- Use blocking keys: normalized name, alnum-only, acronym
- Return list of candidate entities for matching
- Test: Same entity in 2 chunks → should reuse existing entity
- Success: Entities found across chunks, not created as duplicates
- Effort: 3-4 hours

**Achievement 0.2**: Similarity Threshold Applied

- Implement `_string_score(a, b)` using RapidFuzz or Jaro-Winkler
- Add `_choose_match(name, candidates)` that applies threshold
- Only merge if similarity >= `similarity_threshold`
- Test: "Jason Ku" vs "J. Ku" → merge if score >= 0.85
- Success: Fuzzy matching working, threshold actively used
- Effort: 2-3 hours

**Achievement 0.3**: Stable Entity IDs Implemented

- Change from `generate_entity_id(canonical_name)` to deterministic ID
- Use UUIDv5 with namespace + normalized canonical + type
- Or use stable hash: `md5(normalized_name + "|" + type)`
- Ensure same entity gets same ID across chunks/runs
- Test: Same entity, different chunks → same entity_id
- Success: No more ID drift, stable IDs across corpus
- Effort: 2-3 hours

**Achievement 0.4**: LLM Gating Implemented

- Add description similarity check before LLM call
- Use Jaccard similarity on tokenized descriptions
- If similarity >= 0.8, do local merge (no LLM)
- Only call LLM if descriptions diverge significantly
- Test: 3 near-identical descriptions → no LLM call
- Success: LLM calls reduced by 70%+, costs down
- Effort: 2-3 hours

---

### Priority 1: CRITICAL - Core Resolution Algorithm

**Achievement 1.1**: Blocking Strategy Implemented

- Implement `_blocking_keys(name)` in agent
- Generate: normalized name, alnum-only, acronym, soundex (optional)
- Use blocking keys in candidate search query
- Test: "MIT" found when searching "Massachusetts Institute of Technology"
- Success: Efficient candidate retrieval, no full table scans
- Effort: 2-3 hours

**Achievement 1.2**: Fuzzy Matching Algorithm Implemented

- Implement multi-strategy scoring:
  - String similarity (Jaro-Winkler or RapidFuzz ratio)
  - Token overlap (Jaccard on stemmed tokens)
  - Optional: Embedding cosine similarity
- Combine scores: `final = 0.5*string + 0.3*token + 0.2*embedding`
- Apply threshold to final score
- Test: Various name pairs with known similarity
- Success: Accurate fuzzy matching, configurable weights
- Effort: 3-4 hours

**Achievement 1.3**: Type Consistency Rules Implemented

- Weighted type voting: `type_score = confidence × source_count`
- Prefer existing DB type for stability (tie-breaker)
- Flag type conflicts for review
- Never merge: PERSON vs ORG, PERSON vs TECHNOLOGY
- Test: "Python" (language) should not merge with "Python" (person)
- Success: Type conflicts handled properly
- Effort: 2-3 hours

**Achievement 1.4**: Weighted Confidence Model Implemented

- Replace simple mean with:
  - `confidence = clamp(μ + 0.1*log10(1+source_count) + 0.05*agreement, 0, 1)`
  - Where `agreement` = avg pairwise similarity of descriptions
- Reward multi-source agreement
- Test: High source_count → higher confidence
- Success: Better confidence estimates
- Effort: 2-3 hours

---

### Priority 2: HIGH - Data Model & Operations

**Achievement 2.1**: Atomic Upsert Operations Implemented

- Replace `_update_existing_entity` + `_insert_new_entity` with `_upsert_entity`
- Use `find_one_and_update(..., upsert=True)`
- Implement proper merge policy:
  - `$setOnInsert` for immutable fields (created_at, first_seen)
  - `$set` for updateable fields (description, updated_at)
  - `$inc` for counters (source_count)
  - `$addToSet` for arrays (aliases, source_chunks)
  - `$max` for confidence (keep highest)
- Test: Concurrent updates to same entity don't create duplicates
- Success: No race conditions, atomic operations
- Effort: 3-4 hours

**Achievement 2.2**: Normalized Fields & Indexes Added

- Add to entity document:
  - `canonical_name_normalized`: normalized string for matching
  - `aliases_normalized`: array of normalized aliases
- Create indexes:
  - `entity_id` (unique)
  - `canonical_name_normalized` (sparse)
  - `aliases_normalized` (multikey)
  - `(last_seen, -1)` for cleanup
- Test: Query performance on normalized fields
- Success: Fast lookups, proper indexing
- Effort: 2 hours

**Achievement 2.3**: Provenance Tracking Implemented

- Add `provenance` array to entity document:
  - `{video_id, chunk_id, method, timestamp}`
  - Capped at 50 entries (use `$push` with `$slice`)
- Add `resolution_log` for explainability:
  - `{decision, scores, llm_used, timestamp}`
  - Capped at 20 entries
- Test: Merge creates provenance entries
- Success: Can audit merge decisions
- Effort: 2-3 hours

---

### Priority 3: HIGH - Description Handling

**Achievement 3.1**: Description Similarity Checking Implemented

- Before LLM, check description similarity
- Tokenize descriptions, compute Jaccard similarity
- If avg pairwise similarity >= 0.8, skip LLM
- Test: 3 similar descriptions → local merge, no LLM
- Success: LLM calls reduced significantly
- Effort: 2 hours

**Achievement 3.2**: Local Description Merge Implemented

- For near-duplicate descriptions:
  - Deduplicate exact matches
  - Extract unique sentences
  - Concatenate up to 1200 chars
- Preserve key information without LLM
- Test: Merge ["Python is X", "Python is X and Y"] → "Python is X and Y"
- Success: Quality local merges, no LLM needed
- Effort: 2-3 hours

**Achievement 3.3**: Token Budget Management Implemented

- Before LLM call, estimate tokens
- Truncate concatenated descriptions to budget (e.g., 6000 tokens)
- Keep top sentences by novelty (MinHash or TF-IDF)
- Test: Long descriptions truncated properly
- Success: No token overflows, controlled costs
- Effort: 2-3 hours

---

### Priority 3.5: URGENT - Critical Data Integrity Fixes

**ADDED**: November 6, 2025 (Post-Production Validation)  
**Reason**: Production validation revealed 3 critical bugs affecting data integrity and downstream stages

**Achievement 3.5.1**: Entity Mention ID Mapping Fixed ⚠️ **CRITICAL**

- **Issue**: Mentions saved with wrong entity_id when entities merged via fuzzy matching
- **Evidence**: 9% of mentions (9,000+ out of 99,353) point to non-existent entities
- **Root Cause**: `_store_resolved_entities` changes entity_id but doesn't propagate to mentions
- **Fix**: Return id_map `{original_id → final_id}`, use in `_store_entity_mentions`
- **Impact**: Graph construction gets correct entity_ids, no orphaned mentions, no broken relationships
- **Downstream Impact**: Fixes graph construction stage (depends on valid entity_ids)
- **Test**: Verify fuzzy-matched entity's mentions use final entity_id
- **Success**: 0% orphaned mentions, all mentions reference existing entities
- **Effort**: 1-2 hours
- **Files**: `business/stages/graphrag/entity_resolution.py`

**Achievement 3.5.2**: Mention Deduplication & Idempotency Fixed ⚠️ **HIGH**

- **Issue**: Duplicate mentions created on reruns (no unique constraint)
- **Evidence**: Found duplicate mention groups in production data
- **Root Cause**: No unique index on (entity_id, chunk_id, position), batch_insert allows duplicates
- **Fix**: Add unique index, handle duplicate errors gracefully
- **Impact**: Reruns are idempotent, no duplicate data, cleaner database
- **Test**: Rerun same chunk → no new mentions created
- **Success**: No duplicate mentions in database
- **Effort**: 1 hour
- **Files**: `business/services/graphrag/indexes.py`

**Achievement 3.5.3**: source_count Accuracy Fixed ⚠️ **HIGH**

- **Issue**: source_count inflates on reruns, doesn't match actual mentions
- **Evidence**: `source_count=13` but `actual_mentions=9`, `source_count=2` but `actual_mentions=1`
- **Root Cause**: `$inc` increments source_count by entity_group size on every upsert, regardless of whether chunk already seen
- **Fix**: Only increment if chunk_id not already in source_chunks array
- **Impact**: Accurate entity importance, correct trust scoring, reliable metrics
- **Downstream Impact**: Trust scoring and centrality calculations use accurate source_count
- **Test**: Rerun same chunk → source_count unchanged
- **Success**: source_count == length of source_chunks array
- **Effort**: 1 hour
- **Files**: `business/stages/graphrag/entity_resolution.py` (\_upsert_entity method)

**Total Priority 3.5 Effort**: 3-4 hours

---

### Priority 4: MEDIUM - Performance Optimizations

**Achievement 4.1**: Batch Processing Implemented

- Collect N chunks in `process_batch()`
- Call `resolve_entities()` once with all extractions
- Agent groups across entire batch
- Still do DB candidate lookup per entity
- Test: 10 chunks with same entity → 1 entity created
- Success: More efficient, better cross-chunk merging
- Effort: 3-4 hours

**Achievement 4.2**: LRU Cache Implemented

- Cache recent decisions: `{normalized_name → entity_id}`
- Cache alias lookups: `{alias → entity_id}`
- LRU size: 1000-5000 entries
- Clear cache between batches or runs
- Test: Repeated entity lookups hit cache
- Success: Fewer DB queries, faster processing
- Effort: 2-3 hours

**Achievement 4.3**: Rate Limiting Enhanced

- Add exponential backoff for duplicate key errors
- Add jitter to avoid thundering herd
- Retry on Mongo connection errors
- Test: Handles concurrent updates gracefully
- Success: Robust under high concurrency
- Effort: 2 hours

---

### Priority 5: MEDIUM - Quality & Observability

**Achievement 5.1**: Resolution Metrics Implemented

- Track per-run metrics:
  - Merges per 100 mentions
  - LLM calls per entity
  - Average tokens per LLM call
  - Duplicate rate (before/after resolution)
  - False split/merge samples (flagged for review)
  - Latency per stage
- Store in stats dictionary
- Log at end of stage
- Success: Can measure resolution quality
- Effort: 3-4 hours

**Achievement 5.2**: False Merge Detection Implemented

- Heuristics to detect bad merges:
  - Same canonical → different types with high frequency
  - Same canonical → contradictory descriptions (low similarity)
  - Same canonical → different contexts (cross-domain)
- Flag suspected false merges in resolution_log
- Output review list at end of run
- Success: Can identify likely false merges
- Effort: 3-4 hours

**Achievement 5.3**: Missed Merge Detection Implemented

- Heuristics to detect missed merges:
  - Very similar names → different entity_ids
  - Same entity in same chunk → different entity_ids
  - High semantic similarity → not merged
- Flag suspected missed merges
- Output review list
- Success: Can identify likely missed merges
- Effort: 3-4 hours

---

### Priority 6: MEDIUM - Advanced Features

**Achievement 6.1**: Acronym/Alias Awareness Implemented

- Pattern rules:
  - "MIT" ↔ "Massachusetts Institute of Technology"
  - "Prof. X" ↔ "Professor X" ↔ "X"
  - Strip honorifics: Dr., Prof., Mr., Ms.
- Maintain alias pattern set
- Accumulate to aliases array
- Test: Acronym expansion works
- Success: Better matching of common aliases
- Effort: 2-3 hours

**Achievement 6.2**: Embedding-Based Similarity Added (Optional)

- Store 384-dim embedding (SBERT/MiniLM) per entity
- Compute on first insertion, update rarely
- Use in similarity scoring: `embedding_similarity = cosine(emb_a, emb_b)`
- Configurable: `use_embeddings` flag
- Test: Semantic similarity improves matching
- Success: Better matches on semantically similar entities
- Effort: 4-5 hours

**Achievement 6.3**: Multilingual Normalization Implemented

- Unicode normalization (NFKD)
- Accent folding (à → a, ñ → n)
- Case folding (language-aware)
- Punctuation stripping
- Test: "José" matches "Jose"
- Success: Better matching for non-ASCII names
- Effort: 2-3 hours

---

### Priority 7: LOW - Testing & Documentation

**Achievement 7.1**: Comprehensive Test Suite Created

- Unit tests for all new functions:
  - Blocking key generation
  - String similarity scoring
  - Type consistency rules
  - Confidence weighting
  - Description merging
- Integration tests:
  - Cross-chunk resolution
  - Fuzzy matching end-to-end
  - Atomic upsert operations
- Test cases:
  - Near-dup names ("Jason Ku" vs "J. Ku")
  - Org suffixes ("Apple Inc." vs "Apple")
  - Acronyms ("MIT" vs "Massachusetts Institute of Technology")
  - Cross-type conflicts ("Python" language vs person)
  - High/low threshold boundaries
  - Multilingual accents
- Success: >80% test coverage
- Effort: 6-8 hours

**Achievement 7.2**: Configuration Documentation Created

- Document all new config parameters:
  - `similarity_threshold` (default 0.85)
  - `use_embeddings` (default false)
  - `llm_gate_jaccard` (default 0.8)
  - `max_llm_tokens_per_entity` (default 6000)
  - `batch_size` (default 50)
  - `cache_size` (default 1000)
  - `provenance_cap` (default 50)
- Add to config class
- Document in README
- Success: All parameters documented and configurable
- Effort: 2 hours

**Achievement 7.3**: Refactor Documentation Created

- Document: `documentation/technical/ENTITY-RESOLUTION-REFACTOR.md`
- Include:
  - What was changed and why
  - Before/after comparison
  - Migration guide
  - Performance improvements
  - Quality improvements
  - Breaking changes (if any)
- Success: Comprehensive refactor documentation
- Effort: 3-4 hours

---

## 📋 Achievement Addition Log

**Dynamically Added Achievements** (if gaps discovered during execution):

### Priority 3.5: Critical Data Integrity Fixes

**Added**: November 6, 2025  
**Trigger**: ChatGPT feedback review + production data validation after Priority 0-3 completion  
**Source**: `documentation/archive/execution-analyses/implementation-review/2025-11/EXECUTION_ANALYSIS_ENTITY-RESOLUTION-BUGS.md`

**Analysis Process**:

1. **ChatGPT Feedback Review**: Received 10+ suggestions (high-impact fixes, performance, polish)
2. **Production Data Validation**: Database integrity checks revealed real issues
   - 9% orphaned mentions (9,000+ out of 99,353 point to non-existent entities)
   - Duplicate mentions found
   - source_count inaccuracies detected
3. **Systemic Impact Analysis**: Considered downstream effects on graph construction, communities, trust scoring
4. **Categorization**: Separated critical bugs (9% data corruption) from enhancements

**Decision Criteria**:

1. Does it affect data correctness? (Critical)
2. Does it affect downstream stages? (High)
3. Is it a bug or enhancement? (Bugs first - "fix bugs immediately" principle)
4. Can it be deferred? (Data corruption cannot)

**Achievements Added**:

- **Achievement 3.5.1**: Entity Mention ID Mapping Fixed (CRITICAL - 9% data corruption) - ✅ COMPLETE
- **Achievement 3.5.2**: Mention Deduplication & Idempotency Fixed (HIGH) - ✅ COMPLETE
- **Achievement 3.5.3**: source_count Accuracy Fixed (HIGH) - ✅ COMPLETE

**Completion Status**: All 3 achievements completed November 6, 2025

- SUBPLAN_34, SUBPLAN_35, SUBPLAN_36 all complete
- All tests passing (13 total tests)
- Ready for production validation

**Rationale**:

- Fixes critical bugs before building more features (Priorities 4-7)
- Small scope (3-4 hours total)
- Unblocks downstream stages (graph construction depends on valid entity_ids)
- Aligned with "fix bugs immediately" methodology principle
- Production evidence (not speculation) - 9% data corruption is unacceptable

**Non-Critical Items**: 6 enhancement items added to IMPLEMENTATION_BACKLOG.md (IMPL-ER-001 through IMPL-ER-006)

**See Also**: `documentation/archive/execution-analyses/implementation-review/2025-11/EXECUTION_ANALYSIS_ENTITY-RESOLUTION-BUGS.md` for complete analysis

---

## 🔄 Subplan Tracking (Updated During Execution)

**Subplans Created for This PLAN**:

- **SUBPLAN_01**: Achievement 0.1 (Cross-Chunk Candidate Lookup) - Status: ✅ COMPLETE
  └─ EXECUTION_TASK_01_01: Implementation complete - Status: ✅ COMPLETE

  - Implemented `_blocking_keys()` in EntityResolutionAgent
  - Implemented `_find_db_candidates()` in EntityResolutionStage
  - Implemented `_choose_match()` with exact matching
  - Integrated candidate lookup into `_store_resolved_entities()` flow
  - Added normalized fields to entity documents for efficient lookup
  - Created comprehensive test suite

- **SUBPLAN_02**: Achievement 0.2 (Similarity Threshold Applied) - Status: ✅ COMPLETE
  └─ EXECUTION_TASK_02_01: Implementation complete - Status: ✅ COMPLETE

  - Implemented `_string_score()` using RapidFuzz WRatio
  - Enhanced `_choose_match()` with fuzzy matching and threshold application
  - Similarity threshold now actively used to filter matches
  - Near-duplicates merge when similarity >= threshold
  - Fast path for exact matches, fuzzy path for near-duplicates
  - Comprehensive test suite for fuzzy matching

- **SUBPLAN_03**: Achievement 0.3 (Stable Entity IDs) - Status: ✅ COMPLETE
  └─ EXECUTION_TASK_03_01: Implementation complete - Status: ✅ COMPLETE

  - Enhanced `generate_entity_id()` to use normalized name + entity type
  - Deterministic ID generation prevents ID drift
  - Same entity always gets same ID across chunks and runs
  - Different types get different IDs (prevents collisions)
  - Backward compatible (works without type parameter)
  - All entity creation calls updated to pass entity type

- **SUBPLAN_04**: Achievement 0.4 (LLM Gating) - Status: ✅ COMPLETE
  └─ EXECUTION_TASK_04_01: Implementation complete - Status: ✅ COMPLETE

  - Implemented `_description_similarity()` using Jaccard similarity
  - Implemented `_merge_descriptions_locally()` for near-duplicate merging
  - Enhanced `_resolve_descriptions()` with LLM gating logic
  - LLM gate threshold: 0.8 Jaccard similarity (configurable)
  - Similar descriptions (>=0.8) → local merge, no LLM
  - Divergent descriptions (<0.8) → LLM call for proper resolution
  - Expected 70%+ reduction in LLM calls

- **SUBPLAN_11**: Achievement 1.1 (Blocking Strategy Enhancement) - Status: ✅ COMPLETE
  └─ EXECUTION_TASK_11_01: Implementation complete - Status: ✅ COMPLETE

  - Enhanced `_blocking_keys()` with optional Soundex/Metaphone phonetic keys
  - Graceful degradation if jellyfish unavailable
  - Phonetic keys generated for better matching of similar-sounding names

- **SUBPLAN_12**: Achievement 1.2 (Multi-Strategy Fuzzy Matching) - Status: ✅ COMPLETE
  └─ EXECUTION_TASK_12_01: Implementation complete - Status: ✅ COMPLETE

  - Implemented `_token_score()` using Jaccard similarity on tokenized names
  - Implemented `_multi_strategy_score()` combining string + token + optional embedding
  - Updated `_choose_match()` to use multi-strategy scoring
  - Weights: 0.6*string + 0.4*token (or 0.5*string + 0.3*token + 0.2\*embedding if embeddings enabled)
  - Embedding support stubbed for future enhancement

- **SUBPLAN_13**: Achievement 1.3 (Type Consistency Rules) - Status: ✅ COMPLETE
  └─ EXECUTION_TASK_13_01: Implementation complete - Status: ✅ COMPLETE

  - Enhanced `_determine_entity_type()` with weighted voting (confidence × source_count)
  - Added tie-breaker logic (prefer existing DB type for stability)
  - Implemented `_are_types_compatible()` for type conflict detection
  - Defined incompatible type pairs: PERSON vs ORG, PERSON vs TECHNOLOGY
  - Type conflicts logged for review

- **SUBPLAN_14**: Achievement 1.4 (Weighted Confidence Model) - Status: ✅ COMPLETE
  └─ EXECUTION_TASK_14_01: Implementation complete - Status: ✅ COMPLETE

  - Replaced simple mean with weighted confidence model
  - Formula: `clamp(μ + 0.1*log10(1+source_count) + 0.05*agreement, 0, 1)`
  - Rewards multi-source agreement and higher source counts
  - Uses description similarity for agreement metric

- **SUBPLAN_21**: Achievement 2.1 (Atomic Upsert Operations) - Status: ✅ COMPLETE
  └─ EXECUTION_TASK_21_01: Implementation complete - Status: ✅ COMPLETE

  - Replaced `_update_existing_entity` and `_insert_new_entity` with single `_upsert_entity` method
  - Implemented atomic upsert using `find_one_and_update(..., upsert=True)`
  - Proper merge policy: $setOnInsert, $set, $inc, $addToSet, $max
  - Eliminates race conditions on concurrent updates
  - Provenance tracking added (capped at 50 entries)

- **SUBPLAN_22**: Achievement 2.2 (Normalized Fields & Indexes) - Status: ✅ COMPLETE
  └─ EXECUTION_TASK_22_01: Implementation complete - Status: ✅ COMPLETE

  - Verified normalized fields already added (canonical_name_normalized, aliases_normalized)
  - Created sparse index for canonical_name_normalized
  - Created multikey index for aliases_normalized array
  - Created index for last_seen (cleanup queries)
  - Verified entity_id unique index exists

- **SUBPLAN_23**: Achievement 2.3 (Provenance Tracking) - Status: ✅ COMPLETE
  └─ EXECUTION_TASK_23_01: Implementation complete - Status: ✅ COMPLETE

  - Provenance array added to entity documents
  - Each entry: {video_id, chunk_id, method, at}
  - Capped at 50 entries using $push with $slice
  - Automatically tracked on every upsert operation

- **SUBPLAN_31**: Achievement 3.1 (Description Similarity Checking) - Status: ✅ COMPLETE
  └─ Already completed in Achievement 0.4 (LLM Gating)

  - Description similarity checking using Jaccard similarity
  - LLM gating based on similarity threshold (0.8)

- **SUBPLAN_32**: Achievement 3.2 (Local Description Merge) - Status: ✅ COMPLETE
  └─ Already completed in Achievement 0.4 (LLM Gating)

  - Local merge for near-duplicate descriptions
  - Extracts unique sentences, concatenates up to 1200 chars

- **SUBPLAN_33**: Achievement 3.3 (Token Budget Management) - Status: ✅ COMPLETE
  └─ EXECUTION_TASK_33_01: Implementation complete - Status: ✅ COMPLETE

  - Configurable token budget (disabled by default to preserve quality)
  - Smart truncation that prioritizes informative sentences
  - Token estimation using simple approximation (~4 chars per token)
  - Easy to tune via `max_input_tokens_per_entity` configuration
  - No quality loss when disabled (default for cheap models)

- **SUBPLAN_34**: Achievement 3.5.1 (Entity Mention ID Mapping Fixed) - Status: ✅ COMPLETE
  └─ EXECUTION_TASK_34_01: Implementation complete - Status: ✅ COMPLETE

  - Modified `_store_resolved_entities()` to return `Dict[str, str]` (id_map: original_id → final_id)
  - Modified `_store_entity_mentions()` to accept `id_map` and use final_id for mentions
  - Updated `handle_doc()` to pass id_map to `_store_entity_mentions()`
  - Ensures mentions use correct entity_id when entities are merged via fuzzy matching
  - Backward compatible (id_map=None defaults to using entity.entity_id)
  - All 4 tests passing

- **SUBPLAN_35**: Achievement 3.5.2 (Mention Deduplication & Idempotency Fixed) - Status: ✅ COMPLETE
  └─ EXECUTION_TASK_35_01: Implementation complete - Status: ✅ COMPLETE

  - Added unique index on (entity_id, chunk_id, position) in `_create_entity_mentions_indexes()`
  - Added DuplicateKeyError handling in `_store_entity_mentions()`
  - Ensures reruns are idempotent (no duplicate mentions)
  - Index creation is idempotent (can run multiple times)
  - All 5 tests passing

- **SUBPLAN_36**: Achievement 3.5.3 (source_count Accuracy Fixed) - Status: ✅ COMPLETE
  └─ EXECUTION_TASK_36_01: Implementation complete - Status: ✅ COMPLETE

  - Modified `_upsert_entity()` to check if chunk_id already in source_chunks
  - Conditional source_count increment (only if new chunk)
  - Added source_count = 1 to $setOnInsert for new entities
  - Prevents source_count inflation on reruns
  - source_count now accurately reflects len(source_chunks)
  - All 4 tests passing

**Production Validation Completed**: November 5, 2025

- 12,988 chunks processed successfully
- 0 errors, 0 warnings
- All refactored features working

**Priority 3.5 Added**: November 6, 2025

- Post-production validation revealed 3 critical data integrity bugs
- Must fix before continuing with Priorities 4-7
- See Priority 3.5 section for details

---

## 🔗 Constraints & Integration

### Technical Constraints

1. **Backward Compatibility**:

   - Existing entity_id format may change (migration needed)
   - New fields added to entity documents (graceful handling)
   - Existing tests must pass or be updated

2. **Database Changes**:

   - New indexes required (create if not exists)
   - New fields in entities collection (default values)
   - Migration script for existing entities (optional)

3. **Performance Requirements**:

   - Must handle 13k+ chunks efficiently
   - Batch processing should complete in <4 hours
   - No degradation vs current performance

4. **Integration with Other Plans**:
   - Complementary to PLAN_ENTITY-RESOLUTION-ANALYSIS.md (analysis provides data for tuning)
   - Feeds into PLAN-EXPERIMENT-INFRASTRUCTURE.md (experiments use refactored resolution)
   - Aligned with QUALITY-IMPROVEMENTS-PLAN.md (Phase 3 Improvement 3.4)

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
   - Migration guide if needed
   - Config changes documented

---

## 📚 References & Context

### Related Plans

**PLAN_ENTITY-RESOLUTION-ANALYSIS.md**:

- **Relationship**: Complementary
- **Focus**: Analysis and data collection
- **This plan uses**: Analysis results to validate improvements

**PLAN_EXTRACTION-QUALITY-ENHANCEMENT.md**:

- **Relationship**: Sequential
- **Focus**: Extraction stage quality
- **This plan depends on**: Good extraction quality

**PLAN-EXPERIMENT-INFRASTRUCTURE.md**:

- **Relationship**: Sequential
- **Focus**: Experiment framework
- **This plan feeds into**: Resolution experiments

**QUALITY-IMPROVEMENTS-PLAN.md**:

- **Relationship**: Parent plan
- **Focus**: Overall quality improvements
- **This plan implements**: Phase 3 Improvement 3.4 (Resolution Threshold Tuning)

### Code References

**Current Implementation**:

- `business/agents/graphrag/entity_resolution.py` - Agent to refactor
- `business/stages/graphrag/entity_resolution.py` - Stage to refactor
- `core/models/graphrag.py` - ResolvedEntity model

**Dependencies**:

- `core/libraries/retry.py` - Retry decorator
- `core/libraries/database.py` - Batch operations
- `core/libraries/logging.py` - Logging utilities

**Tests**:

- `tests/business/agents/graphrag/test_entity_resolution.py` (if exists)
- `tests/business/stages/graphrag/test_entity_resolution_stage.py` (if exists)

### External Dependencies

**New Dependencies to Add**:

- `rapidfuzz>=3.0.0` - Fast string similarity
- Or `jellyfish>=1.0.0` - String matching algorithms
- Optional: `sentence-transformers>=2.0.0` - For embeddings (if Achievement 6.2)

### ChatGPT Analysis Reference

**Critical Issues** (Priority 0):

1. Not resolving across chunks → Achievement 0.1
2. Similarity threshold unused → Achievement 0.2
3. Canonical ID drift → Achievement 0.3
4. LLM overuse → Achievement 0.4

**Algorithmic Upgrades** (Priority 1):

1. Blocking + candidate merge → Achievement 1.1
2. Fuzzy matching → Achievement 1.2
3. Type consistency → Achievement 1.3
4. Confidence model → Achievement 1.4

**Data Model** (Priority 2):

1. Atomic upsert → Achievement 2.1
2. Indexes → Achievement 2.2
3. Provenance → Achievement 2.3

**Performance** (Priority 4):

1. Batching → Achievement 4.1
2. Caching → Achievement 4.2
3. Rate limiting → Achievement 4.3

---

## ⏱️ Time Estimates

**Priority 0** (Critical Bug Fixes): 9-13 hours  
**Priority 1** (Core Algorithm): 9-13 hours  
**Priority 2** (Data Model): 7-9 hours  
**Priority 3** (Descriptions): 6-8 hours  
**Priority 4** (Performance): 7-9 hours  
**Priority 5** (Quality): 10-12 hours  
**Priority 6** (Advanced): 8-11 hours  
**Priority 7** (Testing/Docs): 11-14 hours

**Total**: 67-89 hours (if all priorities completed)

**Recommended Focus**: Priorities 0-3 (31-43 hours) for critical fixes and core improvements

---

## 📊 Success Metrics

### Bug Fixes (Priority 0)

- Cross-chunk resolution working: Target 100% entities found across chunks
- Fuzzy matching active: Target 50%+ merges from fuzzy matches
- Stable IDs: Target 0% ID drift for same entities
- LLM gating: Target 70%+ reduction in LLM calls

### Quality Improvements

- Entity count reduction: Target 50-80% fewer entities (deduplication proof)
- False merge rate: Target <5% (from analysis)
- Missed merge rate: Target <10% (from analysis)
- Type consistency: Target 95%+ correct type assignments

### Performance Improvements

- Processing time: Target 3-5× faster vs current
- LLM costs: Target 70%+ reduction in costs
- DB queries: Target 80%+ cache hit rate
- Throughput: Target 100+ entities/second

### Test Coverage

- Unit tests: Target 50+ test cases
- Integration tests: Target 15+ scenarios
- Coverage: Target >80% line coverage
- All tests passing: Target 100%

---

## 🚀 Immediate Next Steps

1. **Review This Plan** - Confirm scope, priorities, and approach

2. **Add Dependencies** - Add `rapidfuzz` or `jellyfish` to requirements.txt

3. **Create SUBPLAN_01**: Achievement 0.1 (Cross-Chunk Candidate Lookup)

   - Design candidate lookup strategy
   - Define blocking keys
   - Write tests first
   - Implement function

4. **Create SUBPLAN_02**: Achievement 0.2 (Similarity Threshold)

   - Choose similarity algorithm (RapidFuzz recommended)
   - Define scoring function
   - Write tests
   - Implement and integrate

5. **Continue**: Work through Priority 0 systematically, then proceed to Priority 1

---

## 📝 Current Status & Handoff (For Pause/Resume)

**Last Updated**: 2025-11-06 22:00 UTC  
**Status**: ✅ Priorities 0-3 and 3.5 Complete (Critical Data Integrity Fixes)

## 📦 Partial Completion Archive

**Date**: 2025-11-06 22:00 UTC  
**Reason**: Priorities 0-3 and 3.5 complete - Pausing before continuing with Priorities 4-7 (Performance Optimizations, Quality & Observability, Advanced Features, Testing & Documentation)

**Archive Location**: `documentation/archive/entity-resolution-refactor-nov2025/`

**What's Archived**:

- **Completed SUBPLANs**: 12 files (Priorities 0-3: 9 files, Priority 3.5: 3 files)
  - Priorities 0-3: SUBPLAN_01 through SUBPLAN_33
  - Priority 3.5: SUBPLAN_34, SUBPLAN_35, SUBPLAN_36
- **All EXECUTION_TASKs**: 15 files (Priorities 0-3: 12 files, Priority 3.5: 3 files)
  - Priorities 0-3: EXECUTION_TASK_01_01 through EXECUTION_TASK_33_01
  - Priority 3.5: EXECUTION_TASK_34_01, EXECUTION_TASK_35_01, EXECUTION_TASK_36_01
- **Partial summary**: `summary/ENTITY-RESOLUTION-REFACTOR-PARTIAL-COMPLETE.md`
- **Production validation**: 3 files in `validation/` (from Priorities 0-3 validation)

**Still in Root**: This PLAN (active work - Priorities 4-7 remaining)

**To Resume**:

1. Review this "Current Status & Handoff" section
2. Review "Remaining Work" section below
3. Select next achievement from Priority 4, 5, 6, or 7
4. Create SUBPLAN for selected achievement
5. Continue execution

---

## ✅ Completion Summary (Priorities 0-3 and 3.5)

**Achievements Completed**: 17/31 achievements (all critical and high priority, plus urgent data integrity fixes)

**Priority 0: Critical Bug Fixes** ✅ 4/4 complete

- ✅ Achievement 0.1: Cross-Chunk Candidate Lookup
- ✅ Achievement 0.2: Similarity Threshold Applied
- ✅ Achievement 0.3: Stable Entity IDs
- ✅ Achievement 0.4: LLM Gating

**Priority 1: Core Algorithm** ✅ 4/4 complete

- ✅ Achievement 1.1: Blocking Strategy Enhancement
- ✅ Achievement 1.2: Multi-Strategy Fuzzy Matching
- ✅ Achievement 1.3: Type Consistency Rules
- ✅ Achievement 1.4: Weighted Confidence Model

**Priority 2: Data Model** ✅ 3/3 complete

- ✅ Achievement 2.1: Atomic Upsert Operations
- ✅ Achievement 2.2: Normalized Fields & Indexes
- ✅ Achievement 2.3: Provenance Tracking

**Priority 3: Description Handling** ✅ 3/3 complete

- ✅ Achievement 3.1: Description Similarity (via 0.4)
- ✅ Achievement 3.2: Local Description Merge (via 0.4)
- ✅ Achievement 3.3: Token Budget Management

**Priority 3.5: Critical Data Integrity Fixes** ✅ 3/3 complete

- ✅ Achievement 3.5.1: Entity Mention ID Mapping Fixed (CRITICAL - fixes 9% orphaned mentions)
- ✅ Achievement 3.5.2: Mention Deduplication & Idempotency Fixed (HIGH - prevents duplicates on reruns)
- ✅ Achievement 3.5.3: source_count Accuracy Fixed (HIGH - prevents inflation on reruns)

**Production Validation**: ✅ Complete (Priorities 0-3)

- 12,988 chunks processed successfully
- 0 errors, 0 warnings
- All features validated and working

**Priority 3.5 Validation**: ⏳ Pending

- Code complete and all tests passing (13/13 tests)
- Ready for production validation to confirm:
  - 0% orphaned mentions
  - No duplicate mentions
  - source_count matches source_chunks length

---

## 📋 Remaining Work (Priorities 4-7)

**Priority 4: Performance Optimizations** (3 achievements)

- [ ] Achievement 4.1: Batch Processing (collect N chunks, resolve once)
- [ ] Achievement 4.2: LRU Cache (cache recent decisions)
- [ ] Achievement 4.3: Rate Limiting Enhanced (exponential backoff)

**Priority 5: Quality & Observability** (3 achievements)

- [ ] Achievement 5.1: Resolution Metrics (track merges, LLM calls, duplicates)
- [ ] Achievement 5.2: False Merge Detection (heuristics for bad merges)
- [ ] Achievement 5.3: Missed Merge Detection (heuristics for missed merges)

**Priority 6: Advanced Features** (3 achievements)

- [ ] Achievement 6.1: Acronym/Alias Awareness (pattern rules)
- [ ] Achievement 6.2: Embedding-Based Similarity (optional SBERT)
- [ ] Achievement 6.3: Multilingual Normalization (accent folding)

**Priority 7: Testing & Documentation** (3 achievements)

- [ ] Achievement 7.1: Comprehensive Test Suite (50+ test cases)
- [ ] Achievement 7.2: Configuration Documentation (all parameters)
- [ ] Achievement 7.3: Refactor Documentation (migration guide)

### Relationship to Other Plans

**PLAN_ENTITY-RESOLUTION-ANALYSIS.md**:

- **Timing**: Can run in parallel or after Priority 0-1
- **Data flow**: Analysis provides tuning data for this refactor
- **No conflicts**: Different focus areas

**PLAN_EXTRACTION-QUALITY-ENHANCEMENT.md**:

- **Status**: In Progress (Priority 0, 1.1, 1.2 complete)
- **Dependency**: Good extraction quality helps resolution quality
- **Timing**: Can start this plan now

**PLAN-EXPERIMENT-INFRASTRUCTURE.md**:

- **Timing**: After this refactor (uses improved resolution)
- **Experiments**: Will validate refactor improvements

### Critical Path

**Must Do First**: Priority 0 (all 4 achievements)

- These fix critical bugs that make current resolution nearly useless
- Every other priority depends on these fixes working

**High Value**: Priority 1-3

- Core algorithm improvements
- Significant quality gains
- Manageable scope

**Optional**: Priority 4-7

- Performance and observability enhancements
- Can be added incrementally

### If Starting Now

1. Read ChatGPT analysis in this PLAN's references
2. Review current code: `business/agents/graphrag/entity_resolution.py`
3. Create SUBPLAN_01 for Achievement 0.1
4. Write tests first (TDD)
5. Implement cross-chunk lookup

### If Pausing Here

**To Resume Later**:

1. Read Current Status & Handoff (this section)
2. Review Subplan Tracking (see what's done)
3. Review Achievement Addition Log (see what's pending)
4. Select next achievement based on priority
5. Create SUBPLAN and continue

**Context Preserved**: This section + Subplan Tracking + Achievement Log = full context

---

**Status**: PLAN Created and Ready  
**Next**: Review plan, add dependencies, create first SUBPLAN (Achievement 0.1)
