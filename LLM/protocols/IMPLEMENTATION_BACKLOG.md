# Implementation Backlog

**Purpose**: Central repository for future implementation ideas discovered during work  
**Status**: Living Document - Continuously Updated  
**Last Updated**: November 7, 2025 (Pipeline Visualization Complete + 6 New Backlog Items)

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

### Pipeline Visualization Enhancements (November 7, 2025)

**Source**: PLAN_GRAPHRAG-PIPELINE-VISUALIZATION complete  
**Discovered When**: November 7, 2025

#### IMPL-010: Authentication & Authorization System

**Theme**: Security & Access Control  
**Effort**: Large (>24h)  
**Dependencies**: Pipeline visualization system (complete)  
**Discovered In**: Priority 8 completion, security considerations  
**Discovered When**: 2025-11-07  
**Priority**: High  
**Description**:

- Add authentication layer for all web UIs and API endpoints
- Implement role-based access control (admin, developer, viewer)
- API key management for programmatic access
- Session management and token-based auth

**Why High**:

- Production deployment requires access control
- Prevents unauthorized pipeline execution
- Protects sensitive graph data
- Industry-standard security requirement

**Related Documents**:

- PLAN: `documentation/archive/graphrag-pipeline-visualization-nov2025/planning/PLAN_GRAPHRAG-PIPELINE-VISUALIZATION.md`
- Guide: `documentation/guides/GRAPHRAG-VISUALIZATION-GUIDE.md`

#### IMPL-011: Advanced Graph Analytics

**Theme**: Graph Analysis & Algorithms  
**Effort**: Medium (8-24h)  
**Dependencies**: Graph visualization system (complete)  
**Discovered In**: Priority 7 completion  
**Discovered When**: 2025-11-07  
**Priority**: Medium  
**Description**:

- Centrality calculations (PageRank, Betweenness, Closeness)
- Path finding (shortest path between entities)
- Community overlap detection
- Anomaly detection in graph structure

**Why Medium**:

- Valuable for advanced analysis
- NetworkX provides most algorithms
- Not critical for basic operations

**Related Documents**:

- UI: `app/ui/graph_viewer.html`, `app/ui/graph_statistics.html`

#### IMPL-012: Mobile-Responsive UI Design

**Theme**: User Experience  
**Effort**: Medium (8-24h)  
**Dependencies**: All web UIs (complete)  
**Discovered In**: Priority 8 completion  
**Discovered When**: 2025-11-07  
**Priority**: Low  
**Description**:

- Adapt all 13 dashboards for mobile devices
- Responsive layouts for tablet and phone
- Touch-friendly controls

**Why Low**:

- Current desktop design works well
- Limited mobile use case for pipeline operations

**Related Documents**:

- UIs: All files in `app/ui/`

#### IMPL-013: Real-Time Graph Updates via WebSocket

**Theme**: Real-Time Collaboration  
**Effort**: Medium (8-24h)  
**Dependencies**: Graph visualization (complete)  
**Discovered In**: Priority 1 completion  
**Discovered When**: 2025-11-07  
**Priority**: Low  
**Description**:

- Replace SSE with WebSocket for bi-directional communication
- Stream graph updates during pipeline execution
- Multi-user collaboration features

**Why Low**:

- SSE works well for current use case
- Benefit primarily for collaborative scenarios

**Related Documents**:

- API: `app/api/pipeline_progress.py`

#### IMPL-014: Neo4j Cypher Export

**Theme**: External Tool Integration  
**Effort**: Small (<8h)  
**Dependencies**: Export API (complete)  
**Discovered In**: Priority 7 completion  
**Discovered When**: 2025-11-07  
**Priority**: Medium  
**Description**:

- Add Neo4j Cypher format to export options
- Generate CREATE statements for nodes and relationships
- Support batch import format

**Why Medium**:

- Valuable for Neo4j users
- Straightforward implementation
- Common request for graph exports

**Related Documents**:

- API: `app/api/export.py`

#### IMPL-015: API Rate Limiting & Throttling

**Theme**: Production Stability  
**Effort**: Small (<8h)  
**Dependencies**: All API endpoints (complete)  
**Discovered In**: Priority 8 completion  
**Discovered When**: 2025-11-07  
**Priority**: High  
**Description**:

- Implement rate limiting per IP address
- Configurable request limits (requests/minute)
- Throttling for expensive operations
- 429 Too Many Requests response

**Why High**:

- Production deployment requires rate limiting
- Prevents abuse and DoS attacks
- Industry-standard security practice

**Related Documents**:

- APIs: All files in `app/api/`

---

### Documentation Organization (November 6, 2025)

**Source**: Ongoing documentation growth needs structure  
**Discovered When**: November 6, 2025

#### IMPL-DOC-001: Documentation Folder Restructuring

**Theme**: Documentation / Organization  
**Effort**: Medium (4-6h)  
**Dependencies**: None  
**Priority**: Medium  
**Description**:

- Current documentation folder has grown organically (guides, architecture, context, planning, etc.)
- Need systematic organization with clear hierarchy
- Potential structure:
  - `documentation/methodology/` - START_POINT, END_POINT, RESUME, MULTIPLE-PLANS-PROTOCOL
  - `documentation/guides/` - User-facing guides (execution, deployment, testing)
  - `documentation/architecture/` - System architecture (AGENT, STAGE, PIPELINE)
  - `documentation/reference/` - API reference, configuration
  - `documentation/planning/` - Active planning docs (or keep in root)
  - `documentation/archive/` - Completed work (keep as is)
- Need update to all cross-references after restructuring
- Consider navigation/index improvements

**Value**:

- Easier to find documentation
- Clear purpose for each folder
- Better onboarding experience
- Cleaner organization

**Why Medium**:

- Not blocking current work
- Moderate effort (lots of files to review/move)
- Significant value for discoverability
- Should be done before documentation grows further

**Related Documents**:

- All documentation (needs review)
- DOCUMENTATION-PRINCIPLES-AND-PROCESS.md (may need update)

---

### Methodology - Multi-LLM Communication Protocol (November 6, 2025)

**Source**: Real-world need discovered during resume protocol implementation  
**Discovered When**: November 6, 2025  
**Discovered In**: HANDOFF_ENTITY-RESOLUTION-RESUME.md creation (good example, but violated naming convention)

#### IMPL-METHOD-001: Meta-PLAN Special Rules

**Theme**: Methodology / Process  
**Effort**: Small (2-3h)  
**Dependencies**: Multiple PLANS Protocol complete ✅  
**Discovered In**: Achievement 1.4.5 (Multiple PLANS Protocol) - user feedback  
**Discovered When**: November 6, 2025  
**Priority**: Medium  
**Status**: ✅ Complete (PLAN_LLM-V2-BACKLOG Achievement 1.2)  
**Description**:

- PLAN_STRUCTURED-LLM-DEVELOPMENT.md is a meta-PLAN (defines methodology for all other PLANs)
- Meta-PLANs have unique characteristics:
  - Changes affect all other PLANs (cascading updates needed)
  - No traditional dependencies (all PLANs depend on it)
  - Self-referential (uses methodology it defines)
  - Completion has project-wide impact
- Need special rules for:
  - When to update other PLANs after meta-PLAN changes
  - How to version/track methodology changes
  - Compliance auditing (ensure other PLANs stay current)
  - Breaking changes communication
- Consider: Methodology versioning, deprecation policy, migration guides

**Value**:

- Prevents methodology drift across PLANs
- Ensures consistency when methodology evolves
- Clear process for cascading updates
- Better change management

**Why Medium**:

- Affects project organization
- Need after methodology changes
- Not blocking current work
- Important for long-term consistency

**Related Documents**:

- PLAN: PLAN_STRUCTURED-LLM-DEVELOPMENT.md (the meta-PLAN)
- Protocol: MULTIPLE-PLANS-PROTOCOL.md (may need meta-PLAN section)

---

#### IMPL-METHOD-002: Multi-LLM Communication Protocol

**Theme**: Methodology / Process  
**Effort**: Medium (3-4h)  
**Dependencies**: Resume protocol (IMPLEMENTATION_RESUME.md) should be tested first  
**Priority**: Medium  
**Status**: ✅ Complete (PLAN_LLM-V2-BACKLOG Achievement 2.2)  
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

#### IMPL-TEST-001: Production-Grade Test Coverage

**Theme**: Testing Infrastructure  
**Effort**: Large (40-60h)  
**Dependencies**: None  
**Discovered In**: GrammaPlan Methodology Implementation  
**Discovered When**: November 7, 2025  
**Priority**: High  
**Description**:

- Comprehensive test suite targeting >80% code coverage
- Docker container for external test management (isolated environment)
- Integration with existing documentation and testing guides
- Test categories:
  - Unit tests for all core libraries
  - Integration tests for pipeline stages
  - End-to-end tests for full workflows
  - Performance/regression tests
- Test automation and CI/CD integration
- Coverage reporting and quality gates

**Value**:

- Production-ready code quality
- Confidence in refactoring and changes
- Catch regressions early
- Documentation through tests
- Faster development cycles

**Why High**:

- Critical for production deployment
- Foundation for all future work
- Prevents technical debt accumulation
- Industry standard practice
- Enables faster iteration

**Related Documents**:

- Plan: PLAN-LLM-TDD-AND-TESTING.md (test methodology)
- Guide: documentation/technical/TESTING.md
- Scripts: scripts/run_tests.py (existing)

---

#### IMPL-METHOD-003: Meta-PLAN Predefined Prompts

**Theme**: Methodology Enhancement  
**Effort**: Medium (8-12h)  
**Dependencies**: PLAN_STRUCTURED-LLM-DEVELOPMENT complete ✅  
**Discovered In**: GrammaPlan Methodology Implementation  
**Discovered When**: November 7, 2025  
**Priority**: High  
**Status**: ✅ Complete (PLAN_LLM-V2-BACKLOG Achievement 1.1)  
**Description**:

- Create standard prompts for LLM to execute entire methodology workflows
- Prompt categories:
  - "Create a new PLAN for [feature]" → walks through IMPLEMENTATION_START_POINT
  - "Resume PLAN_X" → follows IMPLEMENTATION_RESUME protocol
  - "Complete PLAN_X" → follows IMPLEMENTATION_END_POINT workflow
  - "Create GrammaPlan for [initiative]" → GrammaPlan creation workflow
  - "Analyze [code/plan] for [purpose]" → EXECUTION_ANALYSIS creation
- Integration with IMPLEMENTATION_START_POINT.md
- Prompt templates with placeholders
- Examples for each prompt type

**Value**:

- Faster methodology adoption
- Consistent execution across LLMs
- Lower barrier to entry
- Self-documenting processes
- Reduces human error

**Why High**:

- Directly improves methodology usability
- Enables autonomous LLM execution
- Critical for medium-context models
- High ROI (saves time on every PLAN)

**Related Documents**:

- Plan: PLAN_STRUCTURED-LLM-DEVELOPMENT.md
- Entry point: IMPLEMENTATION_START_POINT.md
- Exit point: IMPLEMENTATION_END_POINT.md

---

#### IMPL-METHOD-004: Meta-PLAN Reference Verification

**Theme**: Methodology Maintenance  
**Effort**: Small (3-4h)  
**Dependencies**: None  
**Discovered In**: GrammaPlan Methodology Implementation  
**Discovered When**: November 7, 2025  
**Priority**: High  
**Status**: ✅ In Progress (PLAN_LLM-V2-BACKLOG Achievement 0.1)  
**Description**:

- Audit all documentation referencing PLAN_STRUCTURED-LLM-DEVELOPMENT.md
- Identify documents with:
  - References to outdated sections
  - References to moved/renamed files
  - References to deprecated practices
  - Missing references to new features (GrammaPlan, MULTIPLE-PLANS-PROTOCOL)
- Fix broken/outdated references
- Update cross-references
- Create audit script for future verification

**Value**:

- Prevents confusion from outdated references
- Maintains documentation quality
- Ensures methodology consistency
- Catches documentation drift

**Why High**:

- Quick win (3-4 hours)
- High impact on usability
- Prevents wasted time from outdated docs
- Foundation for ongoing maintenance

**Related Documents**:

- Plan: PLAN_STRUCTURED-LLM-DEVELOPMENT.md (the meta-PLAN)
- All methodology documents (START_POINT, END_POINT, RESUME, etc.)

---

#### IMPL-PROTOCOL-001: GrammaPlan Implementation in Dependency System

**Theme**: Methodology Feature  
**Effort**: Medium (6-8h)  
**Dependencies**: GrammaPlan concept defined ✅  
**Discovered In**: GrammaPlan Methodology Implementation  
**Discovered When**: November 7, 2025  
**Priority**: High  
**Description**:

- Implement GrammaPlan tracking in MULTIPLE-PLANS-PROTOCOL.md
- Add GrammaPlan coordination section to protocol
- Update ACTIVE_PLANS.md dashboard with GrammaPlan format
- Create GRAMMAPLAN-TEMPLATE.md (structured template)
- Add GrammaPlan archiving guidance to IMPLEMENTATION_END_POINT.md
- Add GrammaPlan creation to IMPLEMENTATION_START_POINT.md
- Update PLAN_STRUCTURED-LLM-DEVELOPMENT.md with GrammaPlan achievement

**Value**:

- Enables large initiative management
- Better for medium-context models
- Supports parallel work streams
- Reduces cognitive load per PLAN

**Why High**:

- Core methodology feature
- Needed for current work (CODE-QUALITY could use it)
- High value for large projects
- Natural extension of existing methodology

**Related Documents**:

- Protocol: LLM/guides/MULTIPLE-PLANS-PROTOCOL.md
- Dashboard: ACTIVE_PLANS.md
- Plan: PLAN_STRUCTURED-LLM-DEVELOPMENT.md
- Guide: LLM/guides/GRAMMAPLAN-GUIDE.md ✅

---

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

#### IMPL-TOOLING-001: Code Quality Measurement Script

**Theme**: Code Quality / Metrics  
**Effort**: Medium (4-6h)  
**Dependencies**: None  
**Discovered In**: Legacy Planning Documents Review (PLAN-SESSIONS-AND-REFACTORING.md)  
**Discovered When**: November 7, 2025  
**Priority**: Medium  
**Description**:

- Create `scripts/measure_code_quality.py` to quantify code quality
- Metrics to track:
  - **Duplication**: Lines of duplicate code, number of duplicate blocks
  - **Complexity**: Average function length, max function length, functions >50 lines count
  - **Documentation**: Functions with docstrings (%), classes with docstrings (%)
  - **Test Coverage**: Files with tests (%), critical paths tested (%)
- Generate report showing trends over time
- Output formats: Markdown report, JSON data, summary statistics
- Integrate with weekly/monthly code quality reviews

**Value**:

- Quantifies code quality improvements objectively
- Identifies technical debt hotspots
- Tracks progress toward quality goals
- Enables data-driven refactoring decisions
- Provides baseline for measuring impact

**Why Medium**:

- Valuable for ongoing quality management
- Not urgent (manual reviews work for now)
- Moderate effort (script creation + testing)
- Foundation for quality tracking

**Related Documents**:

- Legacy: PLAN-SESSIONS-AND-REFACTORING.md Phase 2.3
- Analysis: EXECUTION_ANALYSIS_LEGACY-PLANS-REVIEW.md

---

#### IMPL-TOOLING-002: Validation Automation Scripts

**Theme**: Development Tools / Quality Assurance  
**Effort**: Small (2-3h)  
**Dependencies**: None  
**Discovered In**: Legacy Planning Documents Review (PROCESS-IMPROVEMENTS_METRICS-CHECKPOINT.md)  
**Discovered When**: November 7, 2025  
**Priority**: Medium  
**Description**:

- Create `scripts/validate_imports.py`:
  - Validate all Python files can be imported
  - Catch syntax errors and import issues
  - Fast validation for checkpoint workflows
  - Output: List of files that fail to import
- Create `scripts/validate_metrics.py`:
  - Verify metrics are registered in MetricRegistry
  - Check expected metric groups exist
  - Validate metric naming conventions
  - Output: List of missing/misconfigured metrics
- Integration with IMPLEMENTATION_MID_PLAN_REVIEW.md
- Fast validation (<1 minute total)

**Value**:

- Catches errors early (every 3-5 files in bulk changes)
- Reduces rework time by 50-70% (per legacy analysis)
- Automated validation prevents human error
- Faster than manual testing
- Confidence in every checkpoint

**Why Medium**:

- Quick to implement (2-3 hours)
- High value for bulk changes
- Prevents costly late-stage error discovery
- Should be used in all future large refactors

**Related Documents**:

- Legacy: PROCESS-IMPROVEMENTS_METRICS-CHECKPOINT.md Improvement #5
- Protocol: IMPLEMENTATION_MID_PLAN_REVIEW.md (validation checkpoints)
- Analysis: EXECUTION_ANALYSIS_LEGACY-PLANS-REVIEW.md

---

#### IMPL-DOC-004: Refactoring Patterns Library

**Theme**: Documentation / Code Quality  
**Effort**: Medium (6-8h)  
**Dependencies**: None (but benefits from having real refactoring examples)  
**Discovered In**: Legacy Planning Documents Review (PLAN-SESSIONS-AND-REFACTORING.md)  
**Discovered When**: November 7, 2025  
**Priority**: Medium  
**Description**:

- Create `documentation/technical/REFACTORING-PATTERNS.md`
- Document common refactoring patterns:
  - **Extract Function**: When to extract, how to name, parameter design
  - **Extract Class**: When classes make sense, responsibility design
  - **Move Code**: When to move, how to maintain imports, testing strategy
  - **Inline**: When to inline overly-abstracted code
- Include before/after examples from our codebase (real examples from CODE-QUALITY refactor)
- Define refactoring triggers:
  - **Duplication Trigger**: Same code in 3+ places → Extract to library
  - **Complexity Trigger**: Function >100 lines or complexity >10 → Split
  - **Test Trigger**: Code hard to test → Refactor for testability
  - **Bug Trigger**: Same bug in multiple places → Extract common logic
- Testing guidelines during refactoring (test before, during, after)
- Risks and mitigations for each pattern

**Value**:

- Systematic refactoring guidance
- Reusable patterns across team
- Reduces decision paralysis ("Should I refactor this?")
- Improves refactoring quality
- Teaches best practices

**Why Medium**:

- Valuable for ongoing code quality work
- Not urgent (we refactor successfully without it)
- Moderate effort (documentation + examples)
- Foundation for quality culture

**Related Documents**:

- Legacy: PLAN-SESSIONS-AND-REFACTORING.md Phases 5.2 & 5.3
- Archive: CODE-QUALITY refactor (source of real examples)
- Analysis: EXECUTION_ANALYSIS_LEGACY-PLANS-REVIEW.md

---

#### IMPL-DOC-002: Documentation Naming Convention Review

**Theme**: Documentation Organization  
**Effort**: Medium (6-8h)  
**Dependencies**: None  
**Discovered In**: GrammaPlan Methodology Implementation  
**Discovered When**: November 7, 2025  
**Priority**: Medium  
**Description**:

- Review entire documentation folder for naming patterns
- Analyze current naming conventions across all doc types:
  - Guides (documentation/guides/)
  - Architecture docs (documentation/architecture/)
  - Context docs (documentation/context/)
  - Planning docs (documentation/planning/)
  - Reference docs (documentation/reference/)
  - Technical docs (documentation/technical/)
- Identify inconsistencies and establish patterns
- Create documentation naming standard document
- Standardize file and folder naming conventions
- Update affected documents
- Create migration guide for future docs

**Value**:

- Consistent documentation structure
- Easier navigation and discovery
- Clear purpose from file names
- Better search/organization
- Scales as docs grow

**Why Medium**:

- Improves organization significantly
- Not blocking current work
- Moderate effort required
- Foundation for doc scaling

**Related Documents**:

- All documentation folders
- DOCUMENTATION-PRINCIPLES-AND-PROCESS.md (may need update)
- IMPL-DOC-001: Documentation Folder Restructuring (related)

---

#### IMPL-DOC-003: GraphRAG Documentation Knowledge Graph

**Theme**: Documentation Enhancement / Innovation  
**Effort**: Medium (12-16h)  
**Dependencies**: GraphRAG pipeline working ✅  
**Discovered In**: GrammaPlan Methodology Implementation  
**Discovered When**: November 7, 2025  
**Priority**: Medium  
**Description**:

- Create GraphRAG instance using current methodology documentation as corpus
- Extract entities, relationships, and communities from documentation
- Enable semantic search over methodology docs
- Use cases:
  - "Find all documents about testing"
  - "What's the relationship between PLAN and SUBPLAN?"
  - "Show me examples of EXECUTION_TASK creation"
- Integration with documentation system
- Auto-update as docs change
- Query interface (CLI or web)
- Extract insights from documentation structure:
  - Most referenced documents
  - Documentation gaps (orphaned concepts)
  - Redundant information
  - Relationship patterns

**Value**:

- Advanced documentation search
- Understanding doc relationships
- Identifying gaps and redundancies
- Innovation showcase (dogfooding)
- Better onboarding experience

**Why Medium**:

- Nice-to-have enhancement
- Demonstrates GraphRAG capabilities
- Not critical for current work
- Moderate complexity

**Related Documents**:

- All methodology documentation
- GraphRAG pipeline implementation
- Documentation organization plans

---

#### IMPL-METHOD-005: Meta-PLAN Dependent Documentation Review

**Theme**: Methodology Improvement  
**Effort**: Medium (6-8h)  
**Dependencies**: Multiple PLANs executed with methodology  
**Discovered In**: GrammaPlan Methodology Implementation  
**Discovered When**: November 7, 2025  
**Priority**: Medium  
**Status**: ✅ Complete (PLAN_LLM-V2-BACKLOG Achievement 2.1)  
**Description**:

- Extract all documents that depend on PLAN_STRUCTURED-LLM-DEVELOPMENT.md methodology
- Review for:
  - Real-world usage patterns
  - Common pain points
  - Methodology gaps
  - Improvement opportunities
  - Success patterns
- Documents to review:
  - All active/paused PLANs
  - All SUBPLANs
  - All EXECUTION_TASKs
  - EXECUTION_ANALYSIS documents
  - Archived plans
- Mine for insights:
  - What works well?
  - What's confusing?
  - What's missing?
  - What should change?
- Create improvement recommendations document
- Prioritize improvements
- Feed into future meta-PLAN updates

**Value**:

- Data-driven methodology improvement
- Real usage insights
- Identifies gaps
- Continuous improvement
- Better methodology quality

**Why Medium**:

- Valuable but not urgent
- Need sufficient usage data first
- Moderate analysis effort
- Long-term quality improvement

**Related Documents**:

- Plan: PLAN_STRUCTURED-LLM-DEVELOPMENT.md
- All PLANs, SUBPLANs, EXECUTION_TASKs
- Archives with methodology usage

---

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

#### IMPL-TOOLING-003: Velocity Tracking Script

**Theme**: Process Metrics  
**Effort**: Small (3-4h)  
**Dependencies**: None  
**Discovered In**: Legacy Planning Documents Review (PLAN-SESSIONS-AND-REFACTORING.md)  
**Discovered When**: November 7, 2025  
**Priority**: Low  
**Description**:

- Create `scripts/measure_velocity.py`
- Track development velocity metrics:
  - Features completed per week (from CHANGELOG.md)
  - Tests created per week (from git commits to tests/)
  - Bugs fixed per week (from BUGS.md or git commits)
  - Documentation pages created per week (from git commits to documentation/)
- Analyze git history for trends
- Generate weekly velocity report showing:
  - Current week stats
  - 4-week rolling average
  - Trend (increasing/decreasing/stable)
- Output formats: Markdown report, JSON data, charts (optional)

**Value**:

- Measure development velocity trends
- Improve planning accuracy (estimate based on historical velocity)
- Identify productivity patterns (what weeks are productive, what slows us down)
- Celebrate progress (visualize accomplishments)

**Why Low**:

- Nice-to-have optimization
- Planning currently works without it
- Low impact on development quality
- Can be done manually if needed

**Related Documents**:

- Legacy: PLAN-SESSIONS-AND-REFACTORING.md Phase 4.2
- Dashboard: ACTIVE_PLANS.md (manual velocity tracking)
- Analysis: EXECUTION_ANALYSIS_LEGACY-PLANS-REVIEW.md

---

#### IMPL-DOC-005: Code Comment Guidelines

**Theme**: Documentation / Best Practices  
**Effort**: Small (1-2h)  
**Dependencies**: None  
**Discovered In**: Legacy Planning Documents Review (PLAN-SESSIONS-AND-REFACTORING.md)  
**Discovered When**: November 7, 2025  
**Priority**: Low  
**Description**:

- Create `documentation/guides/CODE-COMMENTING-GUIDE.md`
- Document the **LEARNED** pattern for capturing iteration learnings:
  ```python
  # LEARNED (2025-11-06): Must validate before processing (iteration 2)
  if not is_valid(data):
      raise ValueError("Invalid data")
  ```
- Document the **IMPLEMENTATION NOTES** pattern for complex functions:

  ```python
  \"\"\"
  IMPLEMENTATION NOTES:
  - Initially tried X (iteration 1), failed because Y
  - Current approach Z works because...
  - Edge cases handled: A, B, C

  FUTURE IMPROVEMENTS:
  - Could optimize by doing X (low priority)
  \"\"\"
  ```

- Include real examples from codebase
- Guidelines for when to use each pattern
- Integration with code review process

**Value**:

- Captures context and rationale in code
- Helps future developers understand why decisions were made
- Prevents re-solving already-solved problems
- Improves code maintainability

**Why Low**:

- Nice-to-have documentation
- We already use similar patterns informally
- Low effort to formalize
- Can be done incrementally

**Related Documents**:

- Legacy: PLAN-SESSIONS-AND-REFACTORING.md Phase 3.2
- Analysis: EXECUTION_ANALYSIS_LEGACY-PLANS-REVIEW.md

---

#### IMPL-PROCESS-001: Process Quality Scorecard

**Theme**: Process Metrics  
**Effort**: Medium (4-6h)  
**Dependencies**: Multiple PLANs executed (need historical data)  
**Discovered In**: Legacy Planning Documents Review (PROCESS-IMPROVEMENTS_METRICS-CHECKPOINT.md)  
**Discovered When**: November 7, 2025  
**Priority**: Low  
**Description**:

- Track methodology quality metrics across plans:
  - **TDD Adherence**: % of changes with tests first
  - **Checkpoint Usage**: % of bulk changes with checkpoints
  - **Plan Accuracy**: % of achievements with accurate status
  - **Assumption Validation**: % of assumptions verified before marking complete
  - **Error Rate**: Syntax errors per 100 lines changed
  - **Circular Debugging**: % of SUBPLANs requiring multiple EXECUTION_TASKs
  - **Archive Quality**: % of plans with complete archives
- Add scorecard section to IMPLEMENTATION_END_POINT.md
- Generate scorecard per plan at completion
- Track trends across plans
- Set quality goals and measure progress

**Value**:

- Measures and improves methodology quality
- Data-driven process improvement
- Identifies methodology gaps
- Proves methodology effectiveness

**Why Low**:

- Valuable but not urgent
- Need more PLAN data first (currently 7 plans)
- Moderate effort
- Manual scoring works for now

**Related Documents**:

- Legacy: PROCESS-IMPROVEMENTS_METRICS-CHECKPOINT.md Improvement #6
- Protocol: IMPLEMENTATION_END_POINT.md (would add scorecard here)
- Plan: PLAN_STRUCTURED-LLM-DEVELOPMENT.md (meta-PLAN)
- Analysis: EXECUTION_ANALYSIS_LEGACY-PLANS-REVIEW.md

---

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

### Code Quality Refactor - Future Work (November 7, 2025)

**Source**: PLAN_CODE-QUALITY-REFACTOR.md completion  
**Discovered When**: November 7, 2025

#### IMPL-QUALITY-001: Expand Test Coverage for Metrics Integration

**Theme**: Testing / Code Quality  
**Effort**: Medium (8-12h)  
**Dependencies**: None  
**Priority**: Medium  
**Discovered In**: EXECUTION_TASK_CODE-QUALITY-REFACTOR_03_01.md, CHECKPOINT_PLAN-CODE-QUALITY-REFACTOR.md  
**Description**:

- Only 1 test file created (`test_core_metrics.py`) for metrics integration
- Need comprehensive test coverage for all 22 service/chat files with metrics
- Should test both structural (metric registration) and functional (metric incrementing) aspects
- Include error path testing (verify error metrics increment correctly)
- Test edge cases and boundary conditions

**Why Medium**:

- Not blocking current functionality
- Important for long-term maintainability
- Moderate effort (create test files for each service group)
- Should be done before next major refactor

**Related Documents**:

- PLAN_CODE-QUALITY-REFACTOR.md
- tests/business/services/rag/test_core_metrics.py
- CHECKPOINT_PLAN-CODE-QUALITY-REFACTOR.md

---

#### IMPL-QUALITY-002: Complete Remaining Type Hints (5% Gap)

**Theme**: Code Quality / Type Safety  
**Effort**: Small (2-4h)  
**Dependencies**: None  
**Priority**: Low  
**Discovered In**: PLAN_CODE-QUALITY-REFACTOR.md completion  
**Description**:

- Current coverage: 95.2% (158/166 functions)
- ~8 functions remaining without type hints
- Mostly in GraphRAG agents (2 functions) and some edge cases
- Should complete to 100% for full type safety

**Why Low**:

- Already at 95.2% (exceeds 90% target)
- Remaining functions are likely edge cases or private methods
- Low impact (already very high coverage)
- Can be done incrementally

**Related Documents**:

- PLAN_CODE-QUALITY-REFACTOR.md
- business/agents/graphrag/\*.py

---

#### IMPL-QUALITY-003: Enhance Docstring Coverage

**Theme**: Documentation / Code Quality  
**Effort**: Medium (6-10h)  
**Dependencies**: None  
**Priority**: Medium  
**Discovered In**: PLAN_CODE-QUALITY-REFACTOR.md Achievement 8.2  
**Description**:

- Key functions have docstrings, but comprehensive coverage not achieved
- Should add docstrings to all public functions following Google/NumPy style
- Include parameter descriptions, return types, examples where helpful
- Focus on service functions, agent methods, stage methods

**Why Medium**:

- Improves code maintainability and developer experience
- Not urgent (key functions already documented)
- Moderate effort (systematic review and addition)
- Should be done before next major feature development

**Related Documents**:

- PLAN_CODE-QUALITY-REFACTOR.md
- All service/agent/stage files

---

#### IMPL-QUALITY-004: Apply Clean Code Principles Systematically

**Theme**: Code Quality / Refactoring  
**Effort**: Large (20-30h)  
**Dependencies**: None  
**Priority**: Low  
**Discovered In**: PLAN_CODE-QUALITY-REFACTOR.md Achievement 8.3  
**Description**:

- Clean code principles applied via library patterns, but not systematically
- Should review function length (target: <50 lines), cyclomatic complexity (target: <10)
- Refactor complex functions into smaller, focused functions
- Apply SOLID principles where applicable
- Improve naming consistency

**Why Low**:

- Code is already functional and maintainable
- Large effort for incremental improvement
- Not blocking current work
- Can be done incrementally during future refactors

**Related Documents**:

- PLAN_CODE-QUALITY-REFACTOR.md
- All business/ and app/ files

---

#### IMPL-QUALITY-005: Expand Error Handling Coverage to 100%

**Theme**: Error Handling / Code Quality  
**Effort**: Small (3-5h)  
**Dependencies**: None  
**Priority**: Low  
**Discovered In**: PLAN_CODE-QUALITY-REFACTOR.md Achievement 9.2  
**Description**:

- Current coverage: 87% (via @handle_errors decorator)
- ~13% of functions still need error handling
- Should identify remaining functions and apply @handle_errors
- Target: 100% coverage for all public functions

**Why Low**:

- Already at 87% (good coverage)
- Remaining functions likely low-risk or already have try/except
- Low impact (most critical paths covered)
- Can be done incrementally

**Related Documents**:

- PLAN_CODE-QUALITY-REFACTOR.md
- scripts/audit_error_handling.py

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
