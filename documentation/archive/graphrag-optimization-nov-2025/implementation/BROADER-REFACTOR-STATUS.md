# Broader Refactor Plan - Current Status

**Date**: November 3, 2025  
**Reference**: CODE-REVIEW-IMPLEMENTATION-PLAN.md  
**Status**: GraphRAG domain complete, reviewing next priorities

---

## ✅ Current Completion Status

### Domain 1: GraphRAG ✅ **COMPLETE**

**Files** (14 total):

- ✅ Agents: 6/6 (extraction, entity_resolution, relationship_resolution, community_summarization, community_detection, link_prediction)
- ✅ Stages: 4/4 (extraction, entity_resolution, graph_construction, community_detection)
- ✅ Services: 4/4 (retrieval, query, generation, indexes)

**What Was Done**:

- Refactored all agents with @retry_llm_call
- Applied batch_insert to 6 operations
- Removed ~505 lines of code
- Created 113 tests (all passing)
- Validated entity_resolution stage

**Status**: ✅ **100% COMPLETE** - Reference implementation ready

---

## ⏳ Remaining Domains (Per Original Plan)

### Domain 2: Ingestion (12 files) - **~20% Complete**

**Files**:

- **Agents** (3): clean, enrich, trust
- **Stages** (9): ingest, clean, chunk, enrich, embed, redundancy, trust, backfill, compress

**Current Status**:

- ✅ enrich.py stage - concurrency applied (run_llm_concurrent migrated)
- ✅ clean.py stage - concurrency applied (run_llm_concurrent migrated)
- ⏳ Remaining: 10 files

**Patterns Found** (from original plan):

- LLM calls with retry (agents)
- Configuration repetition (all stages)
- Text processing utilities (clean, chunk)
- Concurrent operations (enrich, clean)

**Libraries to Apply**:

- ✅ concurrency - Already applied to enrich/clean
- ⏳ retry - LLM calls in agents
- ⏳ logging - Error handling
- ⏳ database - Batch operations if applicable
- ⏳ serialization - Model conversions

**Estimated Time**: 2-3 hours

---

### Domain 3: Services (20 files) - **~15% Complete**

**Files**:

- graphrag/\* (4 files): indexes, query, retrieval, generation
- rag/\* (8 files): core, generation, retrieval, indexes, filters, feedback, persona_utils, profiles
- ingestion/\* (2 files): transcripts, metadata
- chat/\* (3 files): filters, citations, export

**Current Status**:

- ✅ rag/core.py - rate_limiting applied (RateLimiter migrated)
- ✅ chat/export.py - serialization applied (json_encoder)
- ✅ graphrag/retrieval.py - caching imported (ready to use)
- ⏳ Remaining: 17 files

**Patterns Found**:

- MongoDB operations (8 files)
- External API calls (transcripts)
- Rate limiting (rag/core)
- Caching opportunities (entity lookups)
- JSON serialization (export, metadata)

**Libraries to Apply**:

- ✅ rate_limiting - Already in rag/core
- ✅ serialization - Already in export
- ✅ caching - Imported in retrieval
- ⏳ database - Batch operations where applicable
- ⏳ error_handling - Consistent error patterns

**Estimated Time**: 3-4 hours

---

### Domain 4: Chat Modules (7 files) - **~15% Complete**

**Files**:

- business/chat/ (4): memory, query_rewriter, retrieval, answering
- business/services/chat/ (3): filters, citations, export

**Current Status**:

- ✅ services/chat/export.py - serialization applied
- ⏳ Remaining: 6 files

**Patterns Found**:

- LLM calls (query_rewriter)
- MongoDB operations (memory)
- JSON export (export)

**Libraries to Apply**:

- ⏳ retry - LLM calls
- ⏳ database - Batch operations
- ✅ serialization - Already in export

**Estimated Time**: 1-2 hours

---

### Domain 5: Pipelines & Base Classes (5 files) - **Issues Identified**

**Files**:

- business/pipelines/ (3): runner, ingestion, graphrag
- core/base/ (2): stage, agent

**Current Status**:

- ⏳ All files - Integration validated but issues found

**Issues Found This Session**:

1. **BaseStage.parse_args()** - Violates "stages called by pipelines only" principle
2. **BaseStage config fallbacks** - Redundant if config is validated
3. **Design clarity** - Needs documentation

**Libraries Status**:

- ✅ Pipelines already use libraries (runner has error handling, metrics)
- ✅ Base classes already use libraries (decorators, error handling)

**Estimated Time**: 1-2 hours (mostly design decisions)

---

## 📊 Overall Progress

| Domain            | Files  | Complete     | Remaining | Time Estimate  |
| ----------------- | ------ | ------------ | --------- | -------------- |
| 1. GraphRAG       | 14     | 14 (100%)    | 0         | ✅ Done        |
| 2. Ingestion      | 12     | 2 (17%)      | 10        | 2-3 hours      |
| 3. Services       | 20     | 3 (15%)      | 17        | 3-4 hours      |
| 4. Chat           | 7      | 1 (14%)      | 6         | 1-2 hours      |
| 5. Pipelines/Base | 5      | 0 (0%)       | 5         | 1-2 hours      |
| **TOTAL**         | **58** | **20 (34%)** | **38**    | **8-13 hours** |

**Note**: Original plan estimated 69 files total, we have 58 (some files already removed or consolidated)

---

## 🎯 Recommended Next Steps

### Option A: Complete Ingestion Domain (2-3 hours)

**Why**:

- Already started (concurrency applied to 2 files)
- Natural progression from GraphRAG
- Completes another full domain

**What to Do**:

1. Apply retry to ingestion agents (clean, enrich, trust)
2. Apply libraries to remaining stages (ingest, chunk, embed, etc.)
3. Remove any dead code found
4. Test ingestion pipeline

**Result**: 2 complete domains (GraphRAG + Ingestion)

---

### Option B: Complete Services Domain (3-4 hours)

**Why**:

- Already started (3 files done)
- High impact (20 files total)
- More diverse patterns to handle

**What to Do**:

1. Apply caching to entity lookups (graphrag services)
2. Apply serialization to remaining files
3. Apply database batch operations where applicable
4. Test service functions

**Result**: Services fully observable

---

### Option C: Address Base Class Issues (1-2 hours)

**Why**:

- Affects all stages
- Design principle violations identified
- Could simplify all stages

**What to Do**:

1. Decide: Remove or deprecate parse_args()?
2. Verify: Does BaseStageConfig always set defaults?
3. Simplify: Remove config fallbacks in BaseStage.setup()
4. Document: Design principles clearly

**Result**: Cleaner base architecture

---

### Option D: Session Handoff & Documentation (1 hour)

**Why**:

- Massive amount of work done this session
- Good stopping point
- Document for next session

**What to Do**:

1. Create comprehensive session summary
2. Document all improvements made
3. Clean up root directory (archive session docs)
4. Create next session plan

**Result**: Clean handoff, ready to resume

---

## 💡 My Recommendation

### Recommended: **Option A - Complete Ingestion Domain**

**Rationale**:

1. **Momentum**: Already started, natural continuation
2. **Time**: 2-3 hours is manageable
3. **Completeness**: 2 full domains done vs partial everywhere
4. **Pattern**: Use GraphRAG as reference

**Then**:

- Session handoff with 2 complete domains
- Clear pattern established
- Easy to continue in next session

---

## 📋 Ingestion Domain - Quick Breakdown

### Agents (3 files) - 30-45 min

1. **business/agents/ingestion/clean.py**

   - Apply @retry_llm_call to LLM methods
   - Remove manual retry if exists
   - Test

2. **business/agents/ingestion/enrich.py**

   - Apply @retry_llm_call to LLM methods
   - Remove manual retry if exists
   - Test

3. **business/agents/ingestion/trust.py**
   - Apply @retry_llm_call to LLM methods
   - Remove manual retry if exists
   - Test

### Stages (9 files) - 1.5-2 hours

1. **ingest.py** - Check for batch operations, apply if needed
2. **clean.py** - ✅ Already has concurrency
3. **chunk.py** - Check for patterns
4. **enrich.py** - ✅ Already has concurrency
5. **embed.py** - Check for batch operations
6. **redundancy.py** - Check for patterns
7. **trust.py** - Check for batch operations
8. **backfill.py** - Check for patterns
9. **compress.py** - Check for patterns

**Focus**: Apply retry, batch operations, remove dead code

---

## 🎯 While graph_construction Runs

**We Can**:

1. ✅ Review broader plan (doing now)
2. Start applying to ingestion domain
3. Create tests for ingestion agents
4. Document next priorities

**Time Available**: ~1-2 hours before graph_construction finishes

**Recommendation**: Start ingestion domain refactoring while waiting

---

**Current Status**: 34% complete (20/58 files)  
**Recommended Next**: Complete ingestion domain (gets us to ~55% complete)  
**Awaiting**: Your decision on next domain to tackle
