# PLAN: Stage Domain Refactor

**Status**: 🎯 ACTIVE  
**Created**: 2025-11-13  
**Goal**: Refactor Stage and Pipeline architecture to eliminate code duplication, improve type safety, separate concerns, and integrate core libraries  
**Priority**: HIGH - Foundation for all GraphRAG stages  
**Progress**: 0/24 achievements (0%)

---

## 📋 Achievement Index

**All Achievements in This Plan**:

**Priority 0: Foundation & Quick Wins**

- Achievement 0.1: GraphRAGBaseStage Extracted
- Achievement 0.2: Query Builder Helpers Added
- Achievement 0.3: Deprecated Code Removed

**Priority 1: Type Safety**

- Achievement 1.1: BaseStage Type Annotations Added
- Achievement 1.2: GraphRAGPipeline Type Annotations Added
- Achievement 1.3: Stage Config Type Safety Enhanced

**Priority 2: Library Integration (Ready Libraries)**

- Achievement 2.1: Retry Library Integrated
- Achievement 2.2: Validation Library Integrated
- Achievement 2.3: Configuration Library Integrated
- Achievement 2.4: Caching Library Integrated
- Achievement 2.5: Serialization Library Integrated
- Achievement 2.6: Data Transform Library Integrated

**Priority 3: Architecture Refactoring (Part 1)**

- Achievement 3.1: DatabaseContext Extracted
- Achievement 3.2: StageMetrics Extracted
- Achievement 3.3: BaseStage Simplified with DI

**Priority 4: Architecture Refactoring (Part 2)**

- Achievement 4.1: StageSelectionService Extracted
- Achievement 4.2: PipelineOrchestrator Created
- Achievement 4.3: GraphRAGPipeline Simplified

**Priority 5: Library Implementation (DI)**

- Achievement 5.1: DI Library Core Implemented
- Achievement 5.2: DI Library Integrated into Stages
- Achievement 5.3: DI Testing Infrastructure Added

**Priority 6: Library Implementation (Feature Flags)**

- Achievement 6.1: Feature Flags Library Implemented
- Achievement 6.2: Feature Flags Integrated into Stages

---

## 📖 Context for LLM Execution

**If you're an LLM reading this to execute work**:

1. **What This Plan Is**: Comprehensive refactoring of Stage and Pipeline architecture based on detailed analysis in `work-space/knowledge/stage-domain-refactor/`

2. **Why This Is Critical**: Recent observability validation work discovered **9 critical bugs**, 100% of which were in Stage domain code that this refactor addresses. See case study: `EXECUTION_CASE-STUDY_OBSERVABILITY-VALIDATION-LEARNINGS.md`

3. **Your Task**: Implement the achievements listed below (priority order)

4. **How to Proceed**:

   - Read the achievement you want to tackle
   - Review the knowledge base documents for context (especially the case study)
   - Create a SUBPLAN with your specific approach
   - Create an EXECUTION_TASK to log your work
   - Follow the TDD workflow (tests first)

5. **What You'll Create**:

   - GraphRAGBaseStage with common patterns
   - Comprehensive type annotations
   - Library integrations (retry, validation, caching, etc.)
   - Separated concerns (DatabaseContext, StageMetrics, etc.)
   - Dependency injection infrastructure
   - Feature flags system

6. **Where to Get Help**:
   - **Start here**: `work-space/knowledge/stage-domain-refactor/EXECUTION_CASE-STUDY_OBSERVABILITY-VALIDATION-LEARNINGS.md` (real-world validation)
   - Read knowledge base: `work-space/knowledge/stage-domain-refactor/INDEX.md`
   - Review existing code: `core/base/stage.py`, `business/pipelines/graphrag.py`
   - Check library implementations: `core/libraries/`
   - Follow methodology: `LLM-METHODOLOGY.md`

**Self-Contained**: This PLAN contains everything you need to execute it.

**Knowledge Base**: Detailed analysis and recommendations in `work-space/knowledge/stage-domain-refactor/`

**Real-World Validation**: Case study proves 100% of recent bugs would be prevented by this refactor

**⭐ NEW: Parallel Execution Strategy**: This plan has been analyzed for parallel execution opportunities. See: `work-space/case-studies/EXECUTION_CASE-STUDY_STAGE-DOMAIN-REFACTOR-PARALLEL-EXECUTION-STRATEGY.md`

**Key Parallelization Findings**:

- **75% of SUBPLANs** can use multi-executor pattern (18 of 24 achievements)
- **79% of achievements** within priorities can run in parallel
- **Priorities 1 + 2** can run in parallel (5h vs 18h sequential)
- **Total time reduction**: 50-65 hours → 22-28 hours (56-57% savings)

---

## 🎯 Goal

Refactor the Stage and Pipeline architecture to eliminate technical debt, improve code quality, and leverage existing library infrastructure. This includes:

1. **Eliminate code duplication** (~400 lines → <50 lines, -87%)
2. **Improve type safety** (~40% → >90% coverage, +125%)
3. **Separate concerns** (extract DatabaseContext, StageMetrics, services)
4. **Integrate libraries** (8 libraries: retry, validation, configuration, caching, serialization, data_transform, DI, feature_flags)
5. **Improve testability** (dependency injection, isolated concerns)
6. **Enhance maintainability** (single responsibility, clear architecture)

**Expected Impact**:

- Time to add new stage: 4h → 2h (-50%)
- Time to fix bug: 2h → 1h (-50%)
- Code review time: 1h → 30min (-50%)
- Onboarding time: 2 days → 1 day (-50%)

---

## 📖 Problem Statement

**Current State - Functional But Technical Debt**:

The GraphRAG Stage and Pipeline architecture is working but has significant technical debt:

**🔥 VALIDATED BY REAL BUGS**: Recent observability validation work (21.75 hours, 7 achievements) discovered **9 critical production bugs**, 100% of which were caused by the issues below. See: `work-space/knowledge/stage-domain-refactor/EXECUTION_CASE-STUDY_OBSERVABILITY-VALIDATION-LEARNINGS.md`

---

**Issue 1: Code Duplication** ⚠️ HIGH

- ~400 lines of repeated code across 4 stages
- Setup patterns duplicated 4x (LLM client, observability, collections)
- Query patterns duplicated 4x (iter_docs logic)
- **Impact**: Maintenance burden, inconsistency risk, hard to update
- **Real Bug**: Missing argument error occurred in 2 locations (Bug #5 in case study)

**Issue 2: Incomplete Type Safety** ⚠️ HIGH

- Only ~40% type coverage
- Many `# type: ignore` comments
- No types for database handles, collections, stats
- **Impact**: IDE support degraded, runtime errors, refactoring risk
- **Real Bug**: AttributeError after 30 minutes of processing - `entity.original_id` didn't exist (Bug #3 in case study)

**Issue 3: Mixed Concerns** ⚠️ HIGH

- BaseStage has 11+ responsibilities (God object)
- GraphRAGPipeline has 15+ methods (933 lines)
- Database, metrics, logging all mixed together
- **Impact**: Hard to test, extend, maintain
- **Real Bugs**: 3 database race condition bugs due to complex operations in stage code (Bugs #2, #4 in case study)

**Issue 4: Underutilized Libraries** ⚠️ MEDIUM

- 12 of 20 libraries (60%) not used in Stage domain
- Reinventing wheels (manual retry, validation, config parsing)
- Inconsistent patterns across stages
- **Impact**: Missed opportunities, inconsistency
- **Real Bug**: Decorator syntax error (`@handle_errors` vs `@handle_errors()`) caused 400 chunk failures (Bug #1 in case study)

**Issue 5: Poor Testability** ⚠️ MEDIUM

- Hardcoded dependencies (can't inject mocks)
- Tightly coupled components
- No dependency injection
- **Impact**: Hard to unit test, slow test execution
- **Real Bug**: NetworkX integration failure due to inability to mock external library (Bug #6 in case study)

**Missing Features**:

1. **No common base for GraphRAG stages** - Each stage reimplements setup
2. **No query builder helpers** - Each stage reimplements query logic
3. **No retry on LLM failures** - Manual error handling everywhere
4. **No config validation** - Invalid configs cause runtime errors
5. **No caching** - Expensive operations repeated
6. **No dependency injection** - Can't inject mocks for testing
7. **No feature flags** - Can't toggle features dynamically

**Time Impact**: 28% of observability validation time (6 of 21.75 hours) was spent debugging issues this refactor will prevent.

---

## 🎯 Success Criteria

### Must Have

- [ ] GraphRAGBaseStage extracted with common patterns
- [ ] Query builder helpers reduce duplication
- [ ] Comprehensive type annotations (>90% coverage)
- [ ] Retry library integrated for LLM calls
- [ ] Validation library integrated for configs
- [ ] Configuration library integrated for env vars
- [ ] DatabaseContext and StageMetrics extracted
- [ ] Dependency injection implemented and integrated
- [ ] All existing tests passing
- [ ] 20+ new tests for refactored components

### Should Have

- [ ] Caching library integrated for LLM responses
- [ ] Serialization library integrated for models
- [ ] Data transform library integrated for stage transitions
- [ ] Feature flags library implemented and integrated
- [ ] Pipeline split into focused services
- [ ] Documentation for new architecture
- [ ] Migration guide for future stages

### Nice to Have

- [ ] Performance benchmarks (before/after)
- [ ] Architecture decision records (ADRs)
- [ ] Developer onboarding guide
- [ ] Code quality metrics dashboard

---

## 📋 Scope Definition

### In Scope

1. **Code Duplication Elimination**:

   - Extract GraphRAGBaseStage
   - Add query builder helpers
   - Consolidate setup patterns

2. **Type Safety Enhancement**:

   - Add type annotations to BaseStage
   - Add type annotations to GraphRAGPipeline
   - Create TypedDicts for stats, configs

3. **Library Integration** (8 libraries):

   - Retry library (LLM call retry)
   - Validation library (config validation)
   - Configuration library (env var parsing)
   - Caching library (LLM response caching)
   - Serialization library (model serialization)
   - Data transform library (stage transitions)
   - DI library (dependency injection) - **IMPLEMENT**
   - Feature flags library (dynamic toggling) - **IMPLEMENT**

4. **Architecture Refactoring**:

   - Extract DatabaseContext
   - Extract StageMetrics
   - Simplify BaseStage with DI
   - Split GraphRAGPipeline into services

5. **Testing & Documentation**:
   - Unit tests for new components
   - Integration tests for refactored stages
   - Documentation for new architecture
   - Migration guide

### Out of Scope

- Changing stage business logic (only architecture)
- Implementing new stages (only refactoring existing)
- Performance optimization (only maintainability)
- Adding new features (only refactoring)
- Implementing libraries 9-20 (future work)

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

### Priority 0: Foundation & Quick Wins (HIGH IMPACT, LOW EFFORT)

**Achievement 0.1**: GraphRAGBaseStage Extracted

**Why Critical**: Prevents Bug #5 (missing argument error in 2 locations) - see case study Finding 4

- Create `core/base/graphrag_stage.py` with `GraphRAGBaseStage` class
- Extract common setup methods: `_setup_llm_client()`, `_setup_graphrag_collections()`, `_setup_observability()`
- Add `_env_bool()` helper for environment variable parsing
- Refactor 4 stages to inherit from `GraphRAGBaseStage`
- Test: All 4 stages still work correctly
- **Success**: ~120 lines of duplication eliminated
- **Effort**: 2-3 hours
- **Case Study Reference**: Finding 4 - Inconsistent Error Handling Patterns
- **Deliverables**:
  - `core/base/graphrag_stage.py` (new file)
  - Updated: `business/stages/graphrag/extraction.py`
  - Updated: `business/stages/graphrag/entity_resolution.py`
  - Updated: `business/stages/graphrag/graph_construction.py`
  - Updated: `business/stages/graphrag/community_detection.py`
  - `tests/core/base/test_graphrag_stage.py` (new test file)

**Achievement 0.2**: Query Builder Helpers Added

- Add `_build_stage_query()` method to `GraphRAGBaseStage`
- Add `_get_stage_cursor()` method to `GraphRAGBaseStage`
- Refactor `iter_docs()` in all 4 stages to use helpers
- Test: Query logic unchanged, all stages work
- **Success**: ~80 lines of duplication eliminated
- **Effort**: 1-2 hours
- **Deliverables**:
  - Updated: `core/base/graphrag_stage.py`
  - Updated: 4 stage files (simplified `iter_docs()`)
  - Updated: `tests/core/base/test_graphrag_stage.py`

**Achievement 0.3**: Deprecated Code Removed

- Remove `build_parser()` from `BaseStage`
- Remove `parse_args()` from `BaseStage`
- Update documentation to reflect pipeline-only execution
- Test: All stages still work via pipeline
- **Success**: ~30 lines of dead code removed
- **Effort**: 1 hour
- **Deliverables**:
  - Updated: `core/base/stage.py`
  - Updated: Documentation (if any references exist)
  - Updated: `tests/core/base/test_stage.py`

---

### Priority 1: Type Safety (HIGH IMPACT, MEDIUM EFFORT)

**Achievement 1.1**: BaseStage Type Annotations Added

**Why Critical**: Prevents Bug #3 (AttributeError: `entity.original_id` didn't exist) - see case study Finding 3

- Add type annotations for all attributes (`client`, `db`, `db_read`, `db_write`, `stats`)
- Create `StageStats` TypedDict for stats dictionary
- Add return type annotations for all methods
- Add parameter type annotations
- Test: Run mypy/pyright, verify no type errors
- **Success**: BaseStage fully typed
- **Effort**: 2 hours
- **Case Study Reference**: Finding 3 - Missing Type Safety Catches Bugs Late
- **Deliverables**:
  - Updated: `core/base/stage.py`
  - New: `core/models/stage.py` (for `StageStats` TypedDict)
  - Updated: `tests/core/base/test_stage.py`

**Achievement 1.2**: GraphRAGPipeline Type Annotations Added

- Add type annotations for all attributes (`specs`, `runner`, `client`, `db`)
- Add return type annotations for all methods
- Add parameter type annotations
- Test: Run mypy/pyright, verify no type errors
- **Success**: GraphRAGPipeline fully typed
- **Effort**: 1-2 hours
- **Deliverables**:
  - Updated: `business/pipelines/graphrag.py`
  - Updated: `tests/business/pipelines/test_graphrag.py`

**Achievement 1.3**: Stage Config Type Safety Enhanced

- Add validation to all stage config classes
- Add type annotations to config attributes
- Create config validators
- Test: Invalid configs rejected with clear errors
- **Success**: All stage configs fully typed and validated
- **Effort**: 1-2 hours
- **Deliverables**:
  - Updated: `core/config/graphrag.py`
  - Updated: All stage config classes
  - Updated: `tests/core/config/test_graphrag.py`

---

### Priority 2: Library Integration (Ready Libraries)

**Achievement 2.1**: Retry Library Integrated

**Why Critical**: Prevents Bug #1 (decorator syntax error caused 400 chunk failures) - see case study Finding 1

- Add `@with_retry` decorator to LLM calls in all agents
- Configure exponential backoff for transient errors
- Add retry logging
- Test: Verify retry behavior on simulated failures
- **Success**: LLM calls automatically retry on transient errors
- **Effort**: 2 hours
- **Case Study Reference**: Finding 1 - Decorator Pattern Issues
- **Real Impact**: Bug #1 caused ALL 400 chunks to fail, required full pipeline re-run (2+ hours lost)
- **Deliverables**:
  - Updated: `business/agents/graphrag/extraction.py`
  - Updated: `business/agents/graphrag/entity_resolution.py`
  - Updated: `business/agents/graphrag/relationship_resolution.py`
  - Updated: `business/agents/graphrag/community_summarization.py`
  - Updated: `tests/business/agents/graphrag/test_extraction.py` (retry tests)

**Achievement 2.2**: Validation Library Integrated

- Add validation rules to all stage configs
- Add `validate()` method to config classes
- Add validation in stage `setup()` methods
- Test: Invalid configs rejected with clear errors
- **Success**: All stage configs validated before use
- **Effort**: 3 hours
- **Deliverables**:
  - Updated: `core/config/graphrag.py` (add validation rules)
  - Updated: All stage `setup()` methods
  - Updated: `tests/core/config/test_graphrag.py` (validation tests)

**Achievement 2.3**: Configuration Library Integrated

- Create `ObservabilityConfig` schema
- Refactor environment variable parsing to use `ConfigLoader`
- Update `GraphRAGBaseStage._setup_observability()` to use config loader
- Test: Config loading from environment works
- **Success**: Centralized config loading
- **Effort**: 2 hours
- **Deliverables**:
  - New: `core/config/observability.py` (config schema)
  - Updated: `core/base/graphrag_stage.py`
  - Updated: `tests/core/config/test_observability.py`

**Achievement 2.4**: Caching Library Integrated

- Add `@cache_result` decorator to LLM calls (optional, configurable)
- Implement cache key generation (hash of input text)
- Add cache configuration (TTL, backend)
- Test: Verify cache hit/miss rates
- **Success**: LLM calls cached (optional)
- **Effort**: 2 hours
- **Deliverables**:
  - Updated: Agent files (add caching decorator)
  - New: `core/config/caching.py` (cache config)
  - Updated: Agent tests (cache tests)

**Achievement 2.5**: Serialization Library Integrated

- Refactor manual serialization in extraction stage
- Use `Serializer.to_dict()` and `from_dict()`
- Refactor serialization in resolution stage
- Test: Verify serialization correctness
- **Success**: Automatic model serialization
- **Effort**: 3 hours
- **Deliverables**:
  - Updated: `business/stages/graphrag/extraction.py`
  - Updated: `business/stages/graphrag/entity_resolution.py`
  - Updated: Stage tests (serialization tests)

**Achievement 2.6**: Data Transform Library Integrated

- Define field mappings for stage transitions
- Refactor manual transformations in resolution stage
- Use `DataTransformer.map_fields()`
- Test: Verify transformations correct
- **Success**: Declarative data transformations
- **Effort**: 2 hours
- **Deliverables**:
  - New: `core/config/field_mappings.py`
  - Updated: `business/stages/graphrag/entity_resolution.py`
  - Updated: Stage tests (transformation tests)

---

### Priority 3: Architecture Refactoring (Part 1)

**Achievement 3.1**: DatabaseContext Extracted

**Why Critical**: Prevents Bugs #2, #4 (3 database race condition bugs) - see case study Finding 2

- Create `core/context/database.py` with `DatabaseContext` class
- Extract database setup logic from `BaseStage`
- Add `get_collection()` method to `DatabaseContext`
- **Add tested upsert patterns** (prevents race conditions)
- Refactor `BaseStage` to use `DatabaseContext`
- Test: All stages work with new context, concurrent operations handled correctly
- **Success**: Database concern separated, race conditions prevented
- **Effort**: 3-4 hours
- **Case Study Reference**: Finding 2 - Database Operation Race Conditions
- **Real Impact**: 3 bugs, 4+ hours debugging, data inconsistency (lost entity mentions)
- **Deliverables**:
  - New: `core/context/database.py`
  - Updated: `core/base/stage.py`
  - Updated: `tests/core/context/test_database.py` (include concurrent operation tests)
  - Updated: `tests/core/base/test_stage.py`

**Achievement 3.2**: StageMetrics Extracted

- Create `core/metrics/stage_metrics.py` with `StageMetrics` class
- Extract metrics logic from `BaseStage`
- Add `increment()`, `finalize()` methods
- Refactor `BaseStage` to use `StageMetrics`
- Test: Metrics still collected correctly
- **Success**: Metrics concern separated
- **Effort**: 2-3 hours
- **Deliverables**:
  - New: `core/metrics/stage_metrics.py`
  - Updated: `core/base/stage.py`
  - Updated: `tests/core/metrics/test_stage_metrics.py`
  - Updated: `tests/core/base/test_stage.py`

**Achievement 3.3**: BaseStage Simplified with DI

**Why Critical**: Prevents Bug #6 (NetworkX integration failure) - see case study Finding 5

- Add dependency injection support to `BaseStage.__init__()`
- Accept `DatabaseContext` and `StageMetrics` as optional parameters
- Update `setup()` to create dependencies if not injected
- Test: Stages work with and without DI, can mock external libraries
- **Success**: BaseStage supports dependency injection, improved testability
- **Effort**: 3-4 hours
- **Case Study Reference**: Finding 5 - NetworkX Integration Issues
- **Real Impact**: Intermittent failures, 2+ hours debugging, dependent on graph structure
- **Deliverables**:
  - Updated: `core/base/stage.py`
  - Updated: All stage `__init__()` methods
  - Updated: `tests/core/base/test_stage.py` (DI tests, mock injection examples)

---

### Priority 4: Architecture Refactoring (Part 2)

**Achievement 4.1**: StageSelectionService Extracted

- Create `business/services/pipeline/stage_selection.py`
- Extract stage selection logic from `GraphRAGPipeline`
- Add `parse_selection()`, `resolve_dependencies()`, `validate_selection()` methods
- Test: Stage selection logic unchanged
- **Success**: Stage selection concern separated
- **Effort**: 2-3 hours
- **Deliverables**:
  - New: `business/services/pipeline/stage_selection.py`
  - Updated: `business/pipelines/graphrag.py`
  - Updated: `tests/business/services/pipeline/test_stage_selection.py`

**Achievement 4.2**: PipelineOrchestrator Created

- Create `business/services/pipeline/orchestrator.py`
- Extract pipeline execution logic from `GraphRAGPipeline`
- Add `execute()`, `resume()` methods
- Test: Pipeline execution unchanged
- **Success**: Orchestration concern separated
- **Effort**: 2-3 hours
- **Deliverables**:
  - New: `business/services/pipeline/orchestrator.py`
  - Updated: `business/pipelines/graphrag.py`
  - Updated: `tests/business/services/pipeline/test_orchestrator.py`

**Achievement 4.3**: GraphRAGPipeline Simplified

- Refactor `GraphRAGPipeline` to compose services
- Use `StageSelectionService` and `PipelineOrchestrator`
- Simplify `__init__()` and `run_*()` methods
- Test: All pipeline functionality works
- **Success**: GraphRAGPipeline simplified (933 lines → ~300 lines)
- **Effort**: 2-3 hours
- **Deliverables**:
  - Updated: `business/pipelines/graphrag.py`
  - Updated: `tests/business/pipelines/test_graphrag.py`

---

### Priority 5: Library Implementation (DI)

**Achievement 5.1**: DI Library Core Implemented

- Create `core/libraries/di/container.py` with `Container` class
- Implement dependency registration (`register()`)
- Implement dependency resolution (`resolve()`)
- Add lifecycle support (singleton, transient, scoped)
- Test: Container works correctly
- **Success**: DI container functional
- **Effort**: 4-5 hours
- **Deliverables**:
  - New: `core/libraries/di/container.py`
  - New: `core/libraries/di/decorators.py` (`@inject` decorator)
  - New: `core/libraries/di/exceptions.py`
  - Updated: `core/libraries/di/__init__.py`
  - New: `tests/core/libraries/di/test_container.py`

**Achievement 5.2**: DI Library Integrated into Stages

- Setup DI container for GraphRAG pipeline
- Register dependencies (OpenAI client, DatabaseContext, StageMetrics, agents)
- Refactor stages to use `@inject` decorator
- Test: Stages work with DI
- **Success**: All stages use dependency injection
- **Effort**: 3-4 hours
- **Deliverables**:
  - New: `business/pipelines/di_setup.py` (container setup)
  - Updated: All stage `__init__()` methods
  - Updated: `business/pipelines/graphrag.py`
  - Updated: Stage tests (use DI for mocking)

**Achievement 5.3**: DI Testing Infrastructure Added

- Create test fixtures for DI container
- Add mock injection helpers
- Update all stage tests to use DI
- Test: All tests pass with DI
- **Success**: Testing with DI is easy
- **Effort**: 2-3 hours
- **Deliverables**:
  - New: `tests/fixtures/di_fixtures.py`
  - Updated: All stage test files
  - New: `tests/core/libraries/di/test_integration.py`

---

### Priority 6: Library Implementation (Feature Flags)

**Achievement 6.1**: Feature Flags Library Implemented

- Create `core/libraries/feature_flags/flags.py` with `FeatureFlags` class
- Implement flag checking (`feature_enabled()`)
- Add support for environment variables
- Add support for config files (optional)
- Test: Feature flags work correctly
- **Success**: Feature flags functional
- **Effort**: 3-4 hours
- **Deliverables**:
  - New: `core/libraries/feature_flags/flags.py`
  - New: `core/libraries/feature_flags/decorators.py`
  - Updated: `core/libraries/feature_flags/__init__.py`
  - New: `tests/core/libraries/feature_flags/test_flags.py`

**Achievement 6.2**: Feature Flags Integrated into Stages

- Replace environment variable checks with feature flags
- Update `GraphRAGBaseStage._setup_observability()` to use flags
- Add feature flag configuration
- Test: Feature toggling works
- **Success**: Features can be toggled dynamically
- **Effort**: 2-3 hours
- **Deliverables**:
  - Updated: `core/base/graphrag_stage.py`
  - New: `core/config/feature_flags.py`
  - Updated: Stage tests (feature flag tests)

---

## 📋 Achievement Addition Log

**Dynamically Added Achievements** (if gaps discovered during execution):

(Empty initially - will be populated as gaps are discovered)

---

## 🔄 Subplan Tracking (Updated During Execution)

**Subplans Created for This PLAN**:

(Empty initially - will be populated as SUBPLANs are created)

**Summary Statistics** (updated as work progresses):

- Total SUBPLANs: 0
- Total EXECUTION_TASKs: 0
- Achievements Complete: 0/24 (0%)
- Total Time Spent: 0 hours

---

## 🔗 Constraints & Integration

### Technical Constraints

1. **Backward Compatibility**:

   - All existing stages must continue to work
   - No breaking changes to stage interface
   - Pipeline execution unchanged from user perspective
   - Gradual migration (old and new patterns coexist)

2. **Testing Requirements**:

   - All existing tests must pass
   - > 90% test coverage for new code
   - Unit tests for all new components
   - Integration tests for refactored stages

3. **Performance Requirements**:

   - No performance degradation
   - Refactoring should not slow down pipeline
   - DI overhead must be minimal (<1ms per stage)

4. **Code Quality**:
   - Follow existing code style
   - Comprehensive type annotations
   - Clear documentation
   - No linter errors

### Process Constraints

1. **Test-First Always**:

   - Write tests before implementing
   - No cheating (fix implementation, not tests)
   - All tests must pass

2. **Incremental Development**:

   - Small, testable changes
   - Each achievement independently testable
   - Can pause/resume at achievement boundaries

3. **Documentation**:
   - All changes documented
   - Architecture decision records (ADRs)
   - Migration guide for future stages

---

## 📚 References & Context

### Knowledge Base

**Primary Reference**: `work-space/knowledge/stage-domain-refactor/`

**⭐ START HERE**: `EXECUTION_CASE-STUDY_OBSERVABILITY-VALIDATION-LEARNINGS.md` - **Real-world validation** (9 bugs, 100% in Stage domain)

- `INDEX.md` - Quick reference and navigation
- `EXECUTION_CASE-STUDY_OBSERVABILITY-VALIDATION-LEARNINGS.md` - Real-world bugs validate refactoring need (~700 lines)
- `EXECUTION_ANALYSIS_STAGE-PIPELINE-ARCHITECTURE-STUDY.md` - Architecture analysis (6 findings, 4-phase roadmap)
- `EXECUTION_ANALYSIS_LIBRARY-INTEGRATION-OPPORTUNITIES.md` - Library integration (20 libraries, 9 integrations)

**Why the Case Study Matters**:

- **9 critical bugs** discovered in 21.75 hours of real work
- **100% of bugs** were in Stage domain code
- **28% of time** (6 hours) spent debugging preventable issues
- **All bugs addressed** by this refactor plan
- **Expected ROI**: 15% time savings, 50% bug reduction

### Code References

**Current Implementation**:

- `core/base/stage.py` - BaseStage (525 lines, 11+ responsibilities)
- `business/pipelines/graphrag.py` - GraphRAGPipeline (933 lines, 15+ methods)
- `business/stages/graphrag/extraction.py` - Extraction stage (620 lines)
- `business/stages/graphrag/entity_resolution.py` - Resolution stage (892 lines)
- `business/stages/graphrag/graph_construction.py` - Construction stage (1874 lines)
- `business/stages/graphrag/community_detection.py` - Detection stage (~1500 lines)

**Library Infrastructure**:

- `core/libraries/__init__.py` - 20 library modules
- `core/libraries/retry/` - Retry library (ready)
- `core/libraries/validation/` - Validation library (ready)
- `core/libraries/configuration/` - Configuration library (ready)
- `core/libraries/caching/` - Caching library (ready)
- `core/libraries/serialization/` - Serialization library (ready)
- `core/libraries/data_transform/` - Data transform library (ready)
- `core/libraries/di/` - DI library (stub - needs implementation)
- `core/libraries/feature_flags/` - Feature flags library (stub - needs implementation)

### External Dependencies

**No New Dependencies**: All libraries already exist in `core/libraries/`

---

## ⏱️ Time Estimates

**Priority 0** (Foundation): 4-6 hours  
**Priority 1** (Type Safety): 4-6 hours  
**Priority 2** (Library Integration): 14 hours  
**Priority 3** (Architecture Part 1): 8-11 hours  
**Priority 4** (Architecture Part 2): 6-9 hours  
**Priority 5** (DI Implementation): 9-12 hours  
**Priority 6** (Feature Flags Implementation): 5-7 hours

**Total**: 50-65 hours (if all priorities completed)

**Testing**: +11 hours  
**Documentation**: +6 hours

**Grand Total**: 67-82 hours

**Recommended Focus**: Priorities 0-2 (22-26 hours) for quick wins and library integration

---

## 🚀 Parallel Execution Strategy

**Source**: `work-space/case-studies/EXECUTION_CASE-STUDY_STAGE-DOMAIN-REFACTOR-PARALLEL-EXECUTION-STRATEGY.md`

This plan has been analyzed for parallel execution opportunities at **4 levels**:

### Level 1: Execution-Level (Multi-Executor SUBPLANs)

**Finding**: **18 of 24 achievements (75%)** can use multi-executor pattern

**Examples**:

- Achievement 0.1: 3 parallel executors (1.5h vs 2-3h) = 0.5-1.5h savings
- Achievement 2.1: 3 parallel executors (45min vs 2h) = 1.25h savings
- Achievement 2.5: 2 parallel executors (1.5h vs 3h) = 1.5h savings

**Total Savings**: 10-15 hours (15-18% reduction)

**How to Apply**:

- When creating SUBPLAN, identify if work can be split into 2-5 independent chunks
- Use multi-executor pattern for achievements with multiple independent files
- Coordinate merge of parallel work

---

### Level 2: SUBPLAN-Level (Parallel Achievements)

**Finding**: **19 of 24 achievements (79%)** can run in parallel within priorities

**Examples**:

- **Priority 0**: 0.1 + 0.3 in parallel (2-3h vs 4-6h) = 2-3h savings
- **Priority 1**: ALL 3 achievements in parallel (2h vs 4-6h) = 2-4h savings
- **Priority 2**: 2 phases with 3 parallel executors each (5h vs 14h) = 9h savings

**Total Savings**: 25-35 hours (37-43% reduction)

**How to Apply**:

- Identify achievements within a priority that modify different files
- Run achievements in parallel when no code dependencies exist
- Coordinate integration testing after parallel work completes

---

### Level 3: Priority-Level (Parallel Priorities)

**Finding**: **Priorities 1 + 2** can run in parallel after Priority 0

**Parallel Strategy**:

```
Phase 1: Priority 0 (Sequential - 3-5 hours)
└─ Foundation work (creates GraphRAGBaseStage)

Phase 2: Priority 1 + 2 (PARALLEL - 5 hours)
├─ Priority 1: Type Safety → Team A (2 hours)
└─ Priority 2: Library Integration → Team B (5 hours)
Max time: 5 hours (vs 18 hours sequential)
Savings: 13 hours (72% reduction)

Phase 3: Priority 3 + 4 (Sequential - 10-14 hours)
└─ Architecture refactoring (dependencies)

Phase 4: Priority 5 + 6 (PARALLEL - 9-12 hours)
├─ Priority 5: DI Implementation → Team A (9-12 hours)
└─ Priority 6: Feature Flags → Team B (5-7 hours)
Max time: 9-12 hours (vs 14-19 hours sequential)
Savings: 5-7 hours (36-37% reduction)
```

**Total Savings**: 23-29 hours (46-45% reduction)

**How to Apply**:

- Complete Priority 0 first (foundation)
- Run Priorities 1 + 2 in parallel (different concerns)
- Run Priorities 5 + 6 in parallel (independent libraries)

---

### Level 4: Cross-Plan (Parallel with OBSERVABILITY)

**Finding**: Can run **REFACTOR 0-2** + **OBSERVABILITY 3-7** in parallel

**Balanced Strategy (Recommended)**:

```
Phase 1: OBSERVABILITY Priority 2 (Already done)
Phase 2: OBSERVABILITY 3-7 + REFACTOR 0-2 (PARALLEL - 15-20 hours)
├─ OBSERVABILITY Priorities 3-7 → Team A
└─ REFACTOR Priorities 0-2 → Team B
Phase 3: REFACTOR 3-6 (Sequential - 15-21 hours)

Total: 30-41 hours (vs 65-85 hours sequential)
Savings: 35-44 hours (54-52% reduction)
```

**How to Apply**:

- Use separate branches for each plan
- Coordinate merge of stage/pipeline changes
- Integration testing after both complete

---

### Optimized Execution Timeline

**Sequential Approach**: 50-65 hours  
**Parallel Approach (All Levels)**: 22-28 hours  
**Total Savings**: 28-37 hours (56-57% reduction)

**Recommended 4-Phase Strategy**:

1. **Phase 1: Foundation** (3-5h) - Priority 0 sequential
2. **Phase 2: Type + Libraries** (5h) - Priorities 1 + 2 parallel
3. **Phase 3: Architecture** (10-14h) - Priorities 3 + 4 sequential
4. **Phase 4: Libraries** (9-12h) - Priorities 5 + 6 parallel

**Total**: 27-36 hours (vs 50-65 hours sequential)

---

### Key Parallelization Principles

**1. Multi-Executor Pattern** (Level 1)

- Split work into 2-5 independent chunks
- Each chunk modifies different files
- Merge results without conflicts
- Example: 4 stage files updated in parallel

**2. Parallel Achievements** (Level 2)

- Identify achievements with no shared files
- Run in parallel within same priority
- Coordinate integration testing
- Example: Priority 1 - all 3 achievements parallel

**3. Parallel Priorities** (Level 3)

- Analyze cross-priority dependencies
- Run independent priorities in parallel
- Foundation work must complete first
- Example: Priorities 1 + 2 after Priority 0

**4. Cross-Plan Parallelization** (Level 4)

- Use separate branches
- Coordinate merge of shared files
- Integration testing after completion
- Example: REFACTOR + OBSERVABILITY parallel

---

### Implementation Guidelines

**When Creating SUBPLANs**:

1. ✅ Identify if multi-executor pattern applies (Level 1)
2. ✅ Note which achievements can run in parallel (Level 2)
3. ✅ Document file dependencies and merge strategy
4. ✅ Specify coordination requirements

**When Executing**:

1. ✅ Use separate branches for parallel work
2. ✅ Coordinate merge of shared files (e.g., stage.py)
3. ✅ Run integration tests after parallel work completes
4. ✅ Document actual time savings vs estimates

**Coordination Requirements**:

- **Branch Management**: Separate branches for parallel executors
- **Merge Strategy**: Coordinate changes to shared files
- **Integration Testing**: Test after parallel work completes
- **Progress Tracking**: Monitor parallel execution progress

---

## 📊 Success Metrics

### Code Quality Metrics

- **Code Duplication**: Reduce from ~400 lines to <50 lines (-87%)
- **Type Coverage**: Increase from ~40% to >90% (+125%)
- **Library Utilization**: Increase from 40% to 80% (+100%)
- **Cyclomatic Complexity**: Reduce BaseStage from 25 to <10 (-60%)
- **Test Coverage**: Increase from ~60% to >80% (+33%)

### Developer Experience Metrics

- **Time to Add New Stage**: Reduce from 4 hours to 2 hours (-50%)
- **Time to Fix Bug**: Reduce from 2 hours to 1 hour (-50%)
- **Code Review Time**: Reduce from 1 hour to 30 minutes (-50%)
- **Onboarding Time**: Reduce from 2 days to 1 day (-50%)

### Architecture Metrics

- **BaseStage Responsibilities**: Reduce from 11+ to 3-4 (-70%)
- **GraphRAGPipeline Lines**: Reduce from 933 to ~300 (-68%)
- **Setup Method Lines**: Reduce from ~40 to ~10 per stage (-75%)
- **Query Method Lines**: Reduce from ~30 to ~5 per stage (-83%)

### Real-World Validation Metrics (from Case Study)

**Baseline** (Observability Validation, 21.75 hours):

- **Bugs Found**: 9 critical bugs
- **Debugging Time**: 28% (6 hours)
- **Bug Rate**: 0.41 bugs/hour

**Expected After Refactor**:

- **Bugs Found**: 4-5 bugs (50% reduction)
- **Debugging Time**: 14% (50% reduction)
- **Bug Rate**: 0.20 bugs/hour (50% reduction)
- **Time Savings**: 15% overall

**Validation Method**: Run observability validation again after refactor, compare metrics

---

## 🚀 Immediate Next Steps

1. **Review This Plan** - Confirm scope, priorities, achievements

2. **Read Knowledge Base** - Understand context (in this order):

   - **⭐ START HERE**: `EXECUTION_CASE-STUDY_OBSERVABILITY-VALIDATION-LEARNINGS.md` (30-40 min read)
     - Understand real bugs this refactor prevents
     - See quantitative analysis (9 bugs, 28% debugging time)
     - Review critical recommendations
   - **⭐ NEW**: `EXECUTION_CASE-STUDY_STAGE-DOMAIN-REFACTOR-PARALLEL-EXECUTION-STRATEGY.md` (20-30 min read)
     - Understand 4-level parallelization strategy
     - See time savings analysis (56-57% reduction)
     - Review parallel execution guidelines
   - `INDEX.md` - Quick reference
   - `EXECUTION_ANALYSIS_STAGE-PIPELINE-ARCHITECTURE-STUDY.md` - Architecture details
   - `EXECUTION_ANALYSIS_LIBRARY-INTEGRATION-OPPORTUNITIES.md` - Library details

3. **Apply Case Study Learnings**:

   - ✅ Keep achievement scope small (<4 hours, <3 deliverables)
   - ✅ Budget 25% time for debugging (not just 15%)
   - ✅ Create debug log for EVERY bug
   - ✅ Create APPROVED_XX.md for EVERY achievement
   - ✅ Pause after each priority to assess

4. **⭐ NEW: Apply Parallel Execution Strategy**:

   - ✅ **Level 1**: Identify if SUBPLAN can use multi-executor pattern (75% can)
   - ✅ **Level 2**: Note which achievements can run in parallel within priority
   - ✅ **Level 3**: Plan to run Priorities 1 + 2 in parallel after Priority 0
   - ✅ **Level 4**: Consider cross-plan parallelization with OBSERVABILITY

5. **Create SUBPLAN_01**: Achievement 0.1 (GraphRAGBaseStage Extraction)

   - Reference case study Finding 4 (Inconsistent Error Handling)
   - **⭐ NEW**: Apply multi-executor pattern (3 parallel executors after foundation)
   - Design extraction strategy with parallelization in mind
   - Write tests first (TDD)
   - Implement extraction with coordinated merge

6. **Execute Priority 0 with Parallelization**:

   - **Phase 1**: Run 0.1 + 0.3 in parallel (2-3h vs 4-6h) = 2-3h savings
   - **Phase 2**: Run 0.2 sequential (depends on 0.1)
   - **Total**: 3-5h (vs 4-6h sequential)

7. **Continue with Parallel Strategy**: After Priority 0, run Priorities 1 + 2 in parallel

**Critical Recommendations**:

- **From Observability Case Study**: Complete Priorities 0-3 together (19-24 hours) - prevents 89% of bugs found
- **⭐ NEW From Parallel Execution Study**: Use 4-phase parallel strategy (27-36h vs 50-65h) - saves 28-37 hours

---

## 📝 Current Status & Handoff (For Pause/Resume)

**Last Updated**: 2025-11-13 (Updated with Parallel Execution Strategy)  
**Status**: 🎯 READY TO START

**Completed Achievements**: 0/24 (0%)

**Next Achievement**: 0.1 (GraphRAGBaseStage Extraction)

**⭐ NEW: Execution Mode**: PARALLEL (4-phase strategy)

**Context**:

- Knowledge base complete with detailed analysis
- 6 major findings documented
- 24 achievements defined across 7 priorities
- **⭐ NEW**: Parallel execution strategy analyzed (4 levels)
- **⭐ NEW**: Time estimate updated: 27-36h (vs 50-65h sequential)
- Ready to begin implementation with parallelization

**⭐ NEW: Parallel Execution Plan**:

**Phase 1: Foundation** (3-5h) - NEXT

- Achievement 0.1 + 0.3 in parallel
- Achievement 0.2 sequential (depends on 0.1)

**Phase 2: Type + Libraries** (5h) - AFTER PHASE 1

- Priority 1 + 2 in parallel (2 teams)

**Phase 3: Architecture** (10-14h) - AFTER PHASE 2

- Priorities 3 + 4 sequential

**Phase 4: Libraries** (9-12h) - AFTER PHASE 3

- Priorities 5 + 6 in parallel (2 teams)

**When Resuming**:

1. Follow IMPLEMENTATION_RESUME.md protocol
2. Read "Current Status & Handoff" section (this section)
3. Review Subplan Tracking (see what's done)
4. **⭐ NEW**: Check current phase and parallel execution status
5. **⭐ NEW**: Identify if multi-executor pattern applies
6. Select next achievement based on priority and phase
7. Create SUBPLAN with parallelization strategy
8. Continue with coordinated execution

**Context Preserved**: This section + Subplan Tracking + Achievement Log + Parallel Execution Strategy = full context

**Key Dependencies**: None - this is a foundational refactoring

**⭐ NEW: Parallelization References**:

- Case Study: `work-space/case-studies/EXECUTION_CASE-STUDY_STAGE-DOMAIN-REFACTOR-PARALLEL-EXECUTION-STRATEGY.md`
- See "Parallel Execution Strategy" section above for detailed guidelines

---

## ✅ Completion Criteria

**This PLAN is Complete When**:

1. [ ] All 24 achievements complete (or consciously deferred)
2. [ ] Code duplication reduced by >80%
3. [ ] Type coverage increased to >90%
4. [ ] 8 libraries integrated (retry, validation, configuration, caching, serialization, data_transform, DI, feature_flags)
5. [ ] DatabaseContext and StageMetrics extracted
6. [ ] BaseStage simplified with DI
7. [ ] GraphRAGPipeline split into services
8. [ ] All existing tests passing
9. [ ] 20+ new tests added
10. [ ] Documentation complete (architecture guide, migration guide)
11. [ ] Success metrics achieved (see Success Metrics section)
12. [ ] Knowledge base updated with learnings

---

## 🎯 Expected Outcomes

### Short-term (After Priority 0-1, 8-12 hours)

- GraphRAGBaseStage eliminates ~200 lines of duplication
- Query builder helpers eliminate ~80 lines of duplication
- Comprehensive type annotations improve IDE support
- Deprecated code removed (cleaner codebase)

### Medium-term (After Priority 2-3, 30-37 hours)

- 6 libraries integrated (retry, validation, configuration, caching, serialization, data_transform)
- DatabaseContext and StageMetrics extracted
- BaseStage simplified with dependency injection
- Improved testability (can inject mocks)

### Long-term (After Priority 4-6, 67-82 hours)

- Complete architecture refactoring
- DI library implemented and integrated
- Feature flags library implemented and integrated
- GraphRAGPipeline simplified (933 → ~300 lines)
- All success metrics achieved

---

## 🎓 Case Study Insights & Recommendations

**Source**: `EXECUTION_CASE-STUDY_OBSERVABILITY-VALIDATION-LEARNINGS.md`

### Key Findings from Real-World Validation

**9 Critical Bugs Discovered** (21.75 hours of work):

| Bug Type                 | Count | Severity | Addressed By                        |
| ------------------------ | ----- | -------- | ----------------------------------- |
| Decorator Patterns       | 1     | Critical | Achievement 2.1 (Retry)             |
| Database Race Conditions | 3     | Critical | Achievement 3.1 (DatabaseContext)   |
| Type Safety              | 1     | Critical | Priority 1 (Type Safety)            |
| Error Handling           | 1     | High     | Achievement 0.1 (GraphRAGBaseStage) |
| External Libraries       | 1     | Medium   | Achievement 3.3 (DI)                |
| Configuration            | 2     | Minor    | Achievement 2.3 (Configuration)     |

**100% of bugs** were in Stage domain code that this refactor addresses.

### Critical Recommendations

**1. Prioritize Priorities 0-3 First** (19-24 hours)

- Prevents **8 of 9 bugs (89%)**
- Foundation + Architecture
- **Highest ROI**

**2. Keep Achievement Scope Small**

- Small achievements (0.1-1.3): 0-2 bugs
- Large achievement (2.1): 6 bugs
- **Rule**: <4 hours, <3 deliverables

**3. Budget 25% Time for Debugging**

- Observability validation: 28% debugging
- After refactor: Expected 14% debugging
- **Plan accordingly**

**4. Use Hybrid Model for Complex Work**

- Recommended for: DI (Priority 5), Feature Flags (Priority 6)
- AI creates automation + guides
- Human executes with validation

**5. Document Everything**

- Create debug log for EVERY bug
- Create APPROVED_XX.md for EVERY achievement
- Prevents rework, saves 15-20% time

### Expected Outcomes

**If Refactor Succeeds**:

- ✅ 50% reduction in bugs (9 bugs/20h → 4-5 bugs/20h)
- ✅ 15% time savings (28% debugging → 14%)
- ✅ 50% faster new stage development (4h → 2h)
- ✅ 100% type coverage (40% → 90%+)

**Validation**: Run observability validation again after refactor, compare to baseline

---

## 🔥 Critical Notes

### Libraries 9-20 (Future Work)

**Note**: This PLAN implements libraries 1-8 as requested. Libraries 9-20 will be implemented in future work:

**Not Implemented in This PLAN**:

- Library 9: Tracing (distributed tracing)
- Library 10: Health (health checks)
- Library 11: Context (execution context)
- Libraries 12-20: Various other libraries

**Rationale**: Focus on high-impact libraries first (retry, validation, DI, etc.). Libraries 9-20 can be implemented as needed in future PLANs.

**Future PLAN**: Consider creating `PLAN_STAGE-DOMAIN-LIBRARIES-PHASE-2.md` for libraries 9-20.

### Achievement Scope

**Note**: Achievements are intentionally broken into smaller scopes to:

- Enable incremental progress
- Reduce risk per achievement
- Allow for easier pause/resume
- Improve testability

**Example**: Architecture refactoring split into:

- Priority 3: Part 1 (DatabaseContext, StageMetrics, BaseStage)
- Priority 4: Part 2 (StageSelectionService, PipelineOrchestrator, GraphRAGPipeline)

This allows pausing after Priority 3 if needed.

---

**Status**: PLAN Created and Ready  
**Next**: Create SUBPLAN_01 for Achievement 0.1 (GraphRAGBaseStage Extraction)  
**Knowledge Base**: `work-space/knowledge/stage-domain-refactor/`
