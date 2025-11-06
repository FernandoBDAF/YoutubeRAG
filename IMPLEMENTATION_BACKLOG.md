# Implementation Backlog

**Purpose**: Central repository for future implementation ideas discovered during work  
**Status**: Living Document - Continuously Updated  
**Last Updated**: November 6, 2025

---

## 📖 Usage Instructions

### What Goes Here

**Future Work Discovered**:

- Ideas noted during EXECUTION_TASK iterations ("nice to have", "out of scope now")
- Gaps identified during implementation ("should do this later")
- Improvements discovered during code review ("could optimize by X")
- Edge cases deferred ("low priority edge case Y")
- Refactoring opportunities identified but not addressed

### When to Add Items

**During Execution**:

- Note ideas in EXECUTION_TASK under "Future Work Discovered"
- Mark "Add to Backlog: Yes"

**During Completion** (IMPLEMENTATION_END_POINT process):

- Review all EXECUTION_TASKs for future work items
- Extract and add to this backlog
- Prioritize relative to existing items
- Format consistently

### When to Remove Items

- When creating a PLAN that addresses the item (mark as "In Progress")
- When item completed (move to "Done" section)
- When item obsolete (move to "Obsolete" section with rationale)

### Prioritization Scheme

**Critical**: Must do soon, blocks other work  
**High**: Important, significant value  
**Medium**: Valuable, but not urgent  
**Low**: Nice to have, low impact

---

## 📋 Backlog Items

### Methodology - Multi-LLM Communication Protocol (November 6, 2025)

**Source**: Real-world need discovered during resume protocol implementation  
**Discovered When**: November 6, 2025  
**Discovered In**: HANDOFF_ENTITY-RESOLUTION-RESUME.md creation (good example, but violated naming convention)

#### IMPL-METHOD-001: Multi-LLM Communication Protocol

**Theme**: Methodology / Process  
**Effort**: Medium (3-4h)  
**Dependencies**: Resume protocol (IMPLEMENTATION_RESUME.md) should be tested first  
**Priority**: Medium  
**Description**:

- Multiple LLM instances may work on same project simultaneously
- Need protocol for handoff/context sharing between LLMs
- HANDOFF_ENTITY-RESOLUTION-RESUME.md is good example but violates naming convention
- Need standardized format for:
  - Context updates (what changed while other LLM was working)
  - Handoff documents (how to resume after changes)
  - Multi-LLM coordination (who's working on what)
  - Conflict resolution (if both touch same files)

**Value**:

- Prevents context loss when multiple LLMs work on project
- Enables clean handoffs between sessions
- Prevents naming violations in handoff documents
- Reduces confusion about "duplication" or "conflicts"

**Naming Convention Question**:

- Should handoff documents follow EXECUTION*ANALYSIS* pattern?
- Or create new HANDOFF\_<TOPIC>.md pattern?
- Or should handoffs be sections in PLAN documents?

**Related Documents**:

- Example: HANDOFF_ENTITY-RESOLUTION-RESUME.md (good content, wrong naming)
- Protocol: IMPLEMENTATION_RESUME.md (single-LLM resume)
- Analysis: EXECUTION_ANALYSIS_RESUME-PROTOCOL-GAPS.md

**Why Medium**:

- Not blocking current work
- Resume protocol should be tested first
- Can be refined based on real multi-LLM scenarios
- Lower priority than core methodology

---

### Entity Resolution - Post-Production Feedback (November 6, 2025)

**Source**: ChatGPT review of entity_resolution.py after production run

#### IMPL-ER-001: Blocking Keys Persistence & Query Optimization

**Theme**: Entity Resolution / Performance  
**Effort**: Small (2-3h)  
**Dependencies**: None (Priority 3.5 fixes should be done first)  
**Discovered In**: ChatGPT feedback after production validation  
**Discovered When**: November 6, 2025  
**Description**:

- Blocking keys currently generated but never persisted or queried
- Keys include acronym, soundex, metaphone that never match DB fields
- Wasted computation generating keys that aren't used in candidate lookup
- **Fix**: Persist `blocking_keys` array on entities, add to query, index field
- **Value**: Better candidate recall (finds "MIT" when searching "Massachusetts Institute of Technology")

**Why Medium**:

- Performance optimization, not correctness issue
- Current approach works, just inefficient
- Low ROI (blocking already works via normalized fields)

**Related Documents**:

- PLAN: PLAN_ENTITY-RESOLUTION-REFACTOR.md
- Archive: documentation/archive/entity-resolution-refactor-nov2025/

---

#### IMPL-ER-002: Type Compatibility Enforcement on Merges

**Theme**: Entity Resolution / Data Quality  
**Effort**: Small (1-2h)  
**Dependencies**: None  
**Discovered In**: ChatGPT feedback  
**Discovered When**: November 6, 2025  
**Description**:

- `_are_types_compatible()` implemented but not called when merging with existing candidate
- Could merge PERSON ↔ ORGANIZATION or PERSON ↔ TECHNOLOGY
- **Fix**: Check compatibility before merging, create new entity if incompatible
- **Value**: Prevents cross-type false merges (edge case)

**Why Medium**:

- Edge case, rare in production (type voting usually prevents this)
- Not observed in production data validation
- Low impact (type conflicts are uncommon)

**Related Documents**:

- PLAN: PLAN_ENTITY-RESOLUTION-REFACTOR.md
- Code: business/stages/graphrag/entity_resolution.py (\_store_resolved_entities)

---

#### IMPL-ER-003: Per-Type Similarity Thresholds

**Theme**: Entity Resolution / Quality Enhancement  
**Effort**: Small (2-3h)  
**Dependencies**: None  
**Discovered In**: ChatGPT feedback  
**Discovered When**: November 6, 2025  
**Description**:

- All entity types use same similarity threshold (0.85)
- PERSON names are cleaner/more consistent than CONCEPT names
- Different thresholds could improve precision/recall per type
- **Fix**: Config per type: `similarity_threshold_person=0.9`, `similarity_threshold_concept=0.83`
- **Value**: Better matching quality per entity type

**Why Low**:

- Nice-to-have optimization
- Current single threshold works well (0.85)
- Would need tuning/validation per type
- Adds complexity to configuration

**Related Documents**:

- PLAN: PLAN_ENTITY-RESOLUTION-REFACTOR.md
- Config: core/config/graphrag.py

---

#### IMPL-ER-004: Agent Chunk/Video Provenance Enhancement

**Theme**: Entity Resolution / Data Quality  
**Effort**: Small (1h)  
**Dependencies**: None  
**Discovered In**: ChatGPT feedback  
**Discovered When**: November 6, 2025  
**Description**:

- Agent's `_group_entities_by_name` tries to record source_chunk but extraction_data doesn't have it
- Better provenance if agent receives chunk_id and video_id
- **Fix**: Add chunk_id and video_id to extraction_data before passing to agent
- **Value**: Better provenance tracking, entity-level source tracking

**Why Low**:

- Minor provenance enhancement
- Current provenance tracking works (tracked at stage level)
- Low impact on functionality

**Related Documents**:

- PLAN: PLAN_ENTITY-RESOLUTION-REFACTOR.md
- Code: business/stages/graphrag/entity_resolution.py (handle_doc)

---

#### IMPL-ER-005: Candidate Sorting by Recency

**Theme**: Entity Resolution / Performance  
**Effort**: Small (<1h)  
**Dependencies**: None  
**Discovered In**: ChatGPT feedback  
**Discovered When**: November 6, 2025  
**Description**:

- Candidate lookup uses `.limit(20)` but no sorting
- May return stale entities instead of recently updated ones
- **Fix**: Add `.sort("last_seen", -1)` before limit
- **Value**: Bias toward recent entities (minor quality improvement)

**Why Low**:

- Minor optimization
- Current approach works (20 candidates usually enough)
- Low impact on quality

**Related Documents**:

- PLAN: PLAN_ENTITY-RESOLUTION-REFACTOR.md
- Code: business/stages/graphrag/entity_resolution.py (\_find_db_candidates)

---

#### IMPL-ER-006: Batch Processing Success Logging Fix

**Theme**: Entity Resolution / Observability  
**Effort**: Small (<1h)  
**Dependencies**: None  
**Discovered In**: ChatGPT feedback  
**Discovered When**: November 6, 2025  
**Description**:

- `process_batch` counts `None` as failure, but `handle_doc()` returns `None` on success
- Logs "0 successful" even when all documents processed successfully
- **Fix**: Track success explicitly in loop instead of counting non-None results
- **Value**: Accurate logging for batch processing

**Why Low**:

- Logging issue only, no functional impact
- Current logs still show success (via other messages)
- Cosmetic fix

**Related Documents**:

- PLAN: PLAN_ENTITY-RESOLUTION-REFACTOR.md
- Code: business/stages/graphrag/entity_resolution.py (process_batch)

---

### Graph Construction - Post-ChatGPT Review (November 6, 2025)

**Source**: ChatGPT review of graph_construction agent and stage

#### IMPL-GC-001: Entity Name-to-ID Mapping Timing

**Theme**: Graph Construction / Data Quality  
**Effort**: Medium (4-6h)  
**Dependencies**: Entity resolution complete (stable IDs)  
**Discovered In**: ChatGPT feedback  
**Discovered When**: November 6, 2025  
**Description**:

- Agent groups relationships by (subject_name, object_name, predicate) before looking up IDs
- If entity names alias to different entities across chunks, could merge distinct entities
- **Fix**: Map names → IDs before grouping, or use (subject_id, object_id, predicate) as key
- **Value**: More accurate relationship grouping

**Why Medium**:

- Edge case, depends on entity resolution quality
- Entity resolution now creates stable IDs and handles aliases properly
- Low impact with current entity resolution improvements

**Related Documents**:

- PLAN: PLAN_GRAPH-CONSTRUCTION-REFACTOR.md
- Code: business/agents/graphrag/relationship_resolution.py

---

#### IMPL-GC-002: Time Ordering Robustness

**Theme**: Graph Construction / Robustness  
**Effort**: Small (1-2h)  
**Dependencies**: None  
**Discovered In**: ChatGPT feedback  
**Discovered When**: November 6, 2025  
**Description**:

- Cross-chunk relationships sort chunks by timestamp_start (string "HH:MM:SS")
- If missing or malformed, sort may be wrong (lexicographic relies on zero-padding)
- **Fix**: Normalize to seconds (parse), default missing timestamps to -1 or chunk index
- **Value**: More robust cross-chunk relationship creation

**Why Low**:

- Timestamps usually well-formed in production
- Rare edge case
- Low impact on most use cases

**Related Documents**:

- PLAN: PLAN_GRAPH-CONSTRUCTION-REFACTOR.md
- Code: business/stages/graphrag/graph_construction.py (\_add_cross_chunk_relationships)

---

#### IMPL-GC-003: Retry Safety for Graph Construction

**Theme**: Graph Construction / Robustness  
**Effort**: Small (2-3h)  
**Dependencies**: None  
**Discovered In**: ChatGPT feedback  
**Discovered When**: November 6, 2025  
**Description**:

- Synthetic edge writers use blind insert with `ordered=False`
- Could use upsert by relationship_id for safer retries
- **Fix**: Change to upsert pattern with `find_one_and_update`
- **Value**: Safer retries, better idempotency

**Why Medium**:

- Nice-to-have improvement
- Current approach works with unique index
- Low impact (duplicate key errors are already absorbed)

**Related Documents**:

- PLAN: PLAN_GRAPH-CONSTRUCTION-REFACTOR.md
- Code: business/stages/graphrag/graph_construction.py

---

### High Priority

#### IMPL-001: Weaker Model Compatibility Testing

**Theme**: Methodology Validation  
**Effort**: Small (1-2 hours)  
**Dependencies**: Foundation complete ✅  
**Discovered In**: PLAN_STRUCTURED-LLM-DEVELOPMENT Achievement 1.1.1  
**Discovered When**: 2025-11-05  
**Description**:

- Test IMPLEMENTATION_START_POINT.md with cursor auto mode
- Test templates with weaker LLMs
- Simplify language if needed
- Ensure methodology accessible to all models

**Why High**:

- Expands usability
- Validates accessibility
- Low effort, good value

**Related Documents**:

- PLAN: PLAN_STRUCTURED-LLM-DEVELOPMENT.md (in root - partial completion)
- Archive: documentation/archive/structured-llm-development-partial-nov-2025/

---

### Medium Priority

#### IMPL-002: Validation & Template Generation Tools

**Theme**: Methodology Tooling  
**Effort**: Medium (8-11 hours)  
**Dependencies**: Foundation complete ✅, Real-world usage feedback recommended  
**Discovered In**: PLAN_STRUCTURED-LLM-DEVELOPMENT Priority 2  
**Discovered When**: 2025-11-05  
**Description**:

- Achievement 2.1: Validation scripts (naming, structure, completeness)
- Achievement 2.2: Template generators (interactive creation)
- Achievement 2.3: Documentation aggregation (extract learnings)

**Why Medium**:

- Enhances methodology
- Not required for basic use
- Build based on real needs discovered during use

**Related Documents**:

- PLAN: PLAN_STRUCTURED-LLM-DEVELOPMENT.md
- Achievements: 2.1, 2.2, 2.3

#### IMPL-003: LLM-Assisted Process Improvement Automation

**Theme**: Methodology Enhancement  
**Effort**: Small (2 hours)  
**Dependencies**: Multiple PLAN executions for pattern detection  
**Discovered In**: PLAN_STRUCTURED-LLM-DEVELOPMENT Achievement 1.2.2  
**Discovered When**: 2025-11-05  
**Description**:

- Automate LLM analysis of EXECUTION_TASKs
- Generate improvement suggestions automatically
- Add to IMPLEMENTATION_END_POINT workflow
- Reduce manual analysis effort

**Why Medium**:

- Enhances self-improvement
- Useful after multiple PLANs executed
- Can be manual for now

**Related Documents**:

- PLAN: PLAN_STRUCTURED-LLM-DEVELOPMENT.md

---

### Medium Priority (Continued)

#### IMPL-004: Test Runner Enhancements

**Theme**: Testing Infrastructure  
**Effort**: Small to Medium (2-4 hours)  
**Dependencies**: Test runner infrastructure complete ✅  
**Discovered In**: PLAN_TEST-RUNNER-INFRASTRUCTURE.md  
**Discovered When**: 2025-11-06  
**Description**:

- Parallel test execution for faster test runs (especially for large test suites)
- Test result caching (skip unchanged tests, faster feedback)
- Watch mode for continuous testing during development
- Test result history/trending

**Why Medium**:

- Nice-to-have enhancements for better developer experience
- Not critical for basic functionality
- Can be added incrementally as needed

**Related Documents**:

- PLAN: PLAN_TEST-RUNNER-INFRASTRUCTURE.md (complete)
- Code: `scripts/run_tests.py`

---

#### IMPL-005: Ontology Enhancement Based on Data Analysis

**Theme**: GraphRAG Extraction Quality  
**Effort**: Medium (6-9 hours)  
**Dependencies**: Priority 0 & 1 of PLAN_EXTRACTION-QUALITY-ENHANCEMENT complete ✅  
**Discovered In**: PLAN_EXTRACTION-QUALITY-ENHANCEMENT (Priority 2)  
**Discovered When**: 2025-11-06  
**Description**:

Priority 2 achievements from the extraction quality enhancement plan:

- Achievement 2.1: Expand canonical predicates (10-20 new predicates, 20-30 mappings)
- Achievement 2.2: Expand type constraints (10-15 high-value predicates)
- Achievement 2.3: Validate symmetric predicates

**Analysis shows**: Current ontology is excellent (100% canonical ratio, 6.17% OTHER entity ratio), but could potentially add more predicates/constraints based on domain-specific needs.

**Why Medium**:

- Data-driven ontology enhancement
- Current ontology already performing well (100% canonical, excellent type coverage)
- May find additional value in expanding coverage
- Based on real extraction data analysis

**Related Documents**:

- PLAN: PLAN_EXTRACTION-QUALITY-ENHANCEMENT.md (in root - partial completion)
- Achievements: 2.1, 2.2, 2.3

#### IMPL-006: Advanced Quality Metrics & Testing

**Theme**: GraphRAG Extraction Quality  
**Effort**: Medium (8-11 hours)  
**Dependencies**: Priority 0 & 1 complete ✅  
**Discovered In**: PLAN_EXTRACTION-QUALITY-ENHANCEMENT (Priority 3)  
**Discovered When**: 2025-11-06  
**Description**:

Priority 3 achievements from the extraction quality enhancement plan:

- Achievement 3.1: Regression testing framework (ensure recall >95%)
- Achievement 3.2: Consistency metrics (cross-chunk consistency, type consistency)
- Achievement 3.3: Expand test coverage (edge cases, new features)

**Why Medium**:

- Enhances quality assurance
- Provides ongoing monitoring capabilities
- Current extraction is validated and working well
- Can be implemented when needed

**Related Documents**:

- PLAN: PLAN_EXTRACTION-QUALITY-ENHANCEMENT.md
- Achievements: 3.1, 3.2, 3.3

#### IMPL-007: Advanced Metrics & Ontology Tools

**Theme**: GraphRAG Extraction Quality  
**Effort**: Medium (7-10 hours)  
**Dependencies**: Priority 0-3 complete recommended  
**Discovered In**: PLAN_EXTRACTION-QUALITY-ENHANCEMENT (Priority 4)  
**Discovered When**: 2025-11-06  
**Description**:

Priority 4 achievements for advanced analysis:

- Achievement 4.1: Noise metrics (predicate/entity/relationship noise)
- Achievement 4.2: Coverage metrics (semantic/ontology coverage)
- Achievement 4.3: Ontology validation tool (YAML consistency checker)

**Why Medium**:

- Advanced analysis capabilities
- Useful for fine-tuning and optimization
- Not critical for current high-quality extraction

**Related Documents**:

- PLAN: PLAN_EXTRACTION-QUALITY-ENHANCEMENT.md
- Achievements: 4.1, 4.2, 4.3

---

### Low Priority

#### IMPL-008: Ontology Maintenance & Improvement Tools

**Theme**: GraphRAG Extraction Quality  
**Effort**: Medium (7-10 hours)  
**Dependencies**: Priority 0-4 complete recommended  
**Discovered In**: PLAN_EXTRACTION-QUALITY-ENHANCEMENT (Priority 5)  
**Discovered When**: 2025-11-06  
**Description**:

Priority 5 achievements for ontology maintenance:

- Achievement 5.1: Ontology impact analyzer (usage patterns, effectiveness)
- Achievement 5.2: Ontology suggestion tool (automated suggestions from data)
- Achievement 5.3: Enhanced ontology documentation

**Why Low**:

- Maintenance and automation tools
- Current manual process working well
- Can build based on ongoing needs

**Related Documents**:

- PLAN: PLAN_EXTRACTION-QUALITY-ENHANCEMENT.md
- Achievements: 5.1, 5.2, 5.3

#### IMPL-009: Experimental Optimization Studies

**Theme**: GraphRAG Extraction Quality  
**Effort**: Medium (8-12 hours)  
**Dependencies**: Baseline established ✅  
**Discovered In**: PLAN_EXTRACTION-QUALITY-ENHANCEMENT (Priority 6)  
**Discovered When**: 2025-11-06  
**Description**:

Priority 6 experimental optimizations:

- Achievement 6.1: Model selection experiments (gpt-4o vs gpt-4o-mini)
- Achievement 6.2: Soft-keep threshold experiments (0.75, 0.85, 0.95)
- Achievement 6.3: Temperature experiments (0.0, 0.1, 0.3)

**Why Low**:

- Experimental optimization
- Current system performing excellently
- Can test if cost/quality tradeoffs needed

**Related Documents**:

- PLAN: PLAN_EXTRACTION-QUALITY-ENHANCEMENT.md
- Achievements: 6.1, 6.2, 6.3

---

### Low Priority (Continued)

#### IMPL-004: Complete Methodology Example

**Theme**: Methodology Documentation  
**Effort**: Large (7-11 hours)  
**Dependencies**: Real feature implementation using methodology  
**Discovered In**: PLAN_STRUCTURED-LLM-DEVELOPMENT Achievement 3.1  
**Discovered When**: 2025-11-05  
**Description**:

- Full cycle example with code implementation
- Demonstrates methodology with real feature
- Shows circular debugging recovery
- Multiple EXECUTION_TASKs per SUBPLAN example

**Why Low**:

- Foundation itself IS an example
- Real usage will provide organic examples
- Formal example can wait

**Related Documents**:

- PLAN: PLAN_STRUCTURED-LLM-DEVELOPMENT.md

---

Items will be organized as:

```markdown
### [Priority] Priority

#### IMPL-XXX: [Title]

**Theme**: [Area of project]
**Effort**: Small (<8h) / Medium (8-24h) / Large (>24h)
**Dependencies**: [What must exist first]
**Discovered In**: [Which PLAN/SUBPLAN/EXECUTION_TASK]
**Discovered When**: [Date]
**Description**:

- [What to implement]
- [Why it's valuable]

**Why [Priority]**:

- [Rationale]

**Related Documents**:

- [Links]
```

---

## ✅ Completed Items

Items moved here when done, then archived monthly.

---

## 🗑️ Obsolete Items

Items no longer relevant, with rationale for why.

---

## 📊 Backlog Management

### Weekly Review

- Review new items
- Adjust priorities
- Identify items ready to become PLANs
- Group related items

### Monthly Archive

- Move completed items to archive
- Remove obsolete items
- Update statistics

---

**This backlog is populated through the IMPLEMENTATION_END_POINT process. Start empty, grow organically.**
