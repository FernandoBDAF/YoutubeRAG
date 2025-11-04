# Code Review & Cleanup - Detailed Implementation Plan

**Created**: November 3, 2025  
**Scope**: Apply observability libraries + identify/implement Tier 2 libraries + systematic refactor  
**Approach**: Library-first, then code cleanup

---

## 🎯 Strategy

**Principle**: Implement needed libraries BEFORE refactoring code that depends on them

**Process Per Domain**:

1. Scan code for patterns
2. Identify library dependencies (Tier 2 libraries needed)
3. Implement those libraries (simple version)
4. Apply all libraries (Tier 1 + Tier 2) to code
5. Refactor and clean

---

## 📊 Domain Analysis & Library Dependencies

### Domain 1: GraphRAG Agents (6 files)

**Files**:

- business/agents/graphrag/extraction.py
- business/agents/graphrag/entity_resolution.py
- business/agents/graphrag/relationship_resolution.py
- business/agents/graphrag/community_detection.py
- business/agents/graphrag/community_summarization.py
- business/agents/graphrag/link_prediction.py

**Current Patterns Found**:

- Manual retry loops (all 6)
- Manual LLM client initialization (all 6)
- Manual error logging (all 6)
- Pydantic model validation (all 6)
- List/dict transformations (4 files)

**Tier 1 Libraries Needed**: ✅ Already available

- @retry_llm_call (from retry library)
- log_exception (from logging library)
- @handle_errors (from error_handling library)

**Tier 2 Libraries Needed**:

- ❌ serialization (Pydantic ↔ dict conversion)
- ❌ data_transform (list/dict helpers)

**Implementation Order**:

1. Implement serialization library (simple) - 1 hour
2. Implement data_transform library (simple) - 30 min
3. Apply all libraries to 6 agents - 2 hours
4. **Total**: 3.5 hours

---

### Domain 2: GraphRAG Stages (4 files)

**Files**:

- business/stages/graphrag/extraction.py
- business/stages/graphrag/entity_resolution.py
- business/stages/graphrag/graph_construction.py
- business/stages/graphrag/community_detection.py

**Current Patterns Found**:

- MongoDB batch operations (entity_resolution, graph_construction)
- Configuration loading (all 4)
- Collection access patterns (all 4)
- Complex nested operations (graph_construction)

**Tier 1 Libraries**: ✅ Already applied via BaseStage

**Tier 2 Libraries Needed**:

- ❌ database (batch inserts, transactions)
- ❌ configuration (centralized loading)

**Implementation Order**:

1. Implement database library (batch operations) - 1 hour
2. Implement configuration library (basic loader) - 30 min
3. Apply + refactor 4 stages - 2 hours
4. **Total**: 3.5 hours

---

### Domain 3: Ingestion Agents & Stages (12 files)

**Files**:

- 3 agents (clean, enrich, trust)
- 9 stages (ingest, clean, chunk, enrich, embed, redundancy, trust, backfill, compress)

**Patterns Found**:

- LLM calls with retry (agents)
- Configuration repetition (all stages)
- Text processing utilities (clean, chunk)
- Concurrent operations (enrich, clean)

**Tier 1 Libraries**: ✅ Already available/applied

**Tier 2 Libraries Needed**:

- ✅ concurrency (move from core/domain/) - just move!
- ❌ configuration (same as GraphRAG stages)

**Implementation Order**:

1. Move concurrency library (already exists) - 30 min
2. Configuration library (already planned above) - covered
3. Apply + refactor 12 files - 3 hours
4. **Total**: 3.5 hours

---

### Domain 4: Services (20 files)

**Files**:

- graphrag/ (4 files: indexes, query, retrieval, generation)
- rag/ (8 files: core, generation, retrieval, indexes, filters, feedback, persona_utils, profiles)
- ingestion/ (2 files: transcripts, metadata)
- chat/ (3 files: filters, citations, export)

**Patterns Found**:

- MongoDB operations (8 files)
- External API calls (transcripts)
- Rate limiting (rag/core)
- Caching opportunities (entity lookups)
- JSON serialization (export, metadata)

**Tier 1 Libraries**: Need to apply

- @with_retry (for DB + API calls)
- @handle_errors (error handling)
- log_exception (consistent errors)

**Tier 2 Libraries Needed**:

- ✅ rate_limiting (move from dependencies/llm/) - just move!
- ❌ caching (for entity lookups, query results)
- ✅ serialization (already planned above)
- ✅ database (already planned above)

**Implementation Order**:

1. Move rate_limiting library - 30 min
2. Implement caching library (simple LRU) - 1 hour
3. Apply all libraries to 20 services - 4 hours
4. **Total**: 5.5 hours

---

### Domain 5: Chat Modules (7 files)

**Files**:

- business/chat/ (4 files: memory, query_rewriter, retrieval, answering)
- business/services/chat/ (3 files: filters, citations, export)

**Patterns Found**:

- LLM calls (query_rewriter)
- MongoDB operations (memory)
- JSON export (export)

**Tier 1 Libraries**: Need to apply

- @retry_llm_call (query_rewriter)
- @handle_errors (all)
- log_exception (all)

**Tier 2 Libraries Needed**:

- ✅ serialization (already planned)
- ✅ database (already planned)

**Implementation Order**:

1. Libraries already covered above
2. Apply to 7 chat files - 1.5 hours
3. **Total**: 1.5 hours

---

### Domain 6: Pipelines & Base Classes (5 files)

**Files**:

- business/pipelines/ (3 files: runner, ingestion, graphrag)
- core/base/ (2 files: stage, agent)

**Status**: ✅ Already enhanced with Tier 1 libraries

**Cleanup Needed**:

- Remove any remaining manual patterns
- Verify all using libraries correctly
- Add any missing metrics

**Total**: 1 hour

---

## 📋 Tier 2 Libraries Implementation Schedule

### Libraries Needed (7 total):

**1. serialization/** (1 hour)

- to_dict(), from_dict() helpers
- JSON encoder for MongoDB types
- Pydantic ↔ MongoDB conversion

**2. data_transform/** (30 min)

- flatten(), group_by(), deduplicate()
- Common list/dict operations

**3. database/** (1 hour)

- batch_insert(), batch_update()
- Transaction support (TODO for later)

**4. configuration/** (30 min)

- ConfigLoader.load()
- Centralized config loading

**5. concurrency/** (30 min)

- Move from core/domain/
- Enhance with better error handling

**6. rate_limiting/** (30 min)

- Move from dependencies/llm/
- Generalize for any operation

**7. caching/** (1 hour)

- Simple LRU cache
- @cached decorator

**Total**: 5.5 hours

---

## 🎯 Complete Implementation Plan

### Week 1: Tier 2 Libraries (Day 1-2, ~6 hours)

**Monday AM** (3 hours):

1. Implement serialization library (1 hr)
2. Implement data_transform library (30 min)
3. Implement database library (1 hr)
4. Test all 3 (30 min)

**Monday PM** (3 hours): 5. Implement configuration library (30 min) 6. Move concurrency library + enhance (30 min) 7. Move rate_limiting library + generalize (30 min) 8. Implement caching library (1 hr) 9. Test all (30 min)

**Deliverable**: 7 Tier 2 libraries ready for use

---

### Week 1: Code Cleanup (Day 3-5, ~18 hours)

**Tuesday** (8 hours):

- Apply libraries to GraphRAG agents (6 files) - 3.5 hrs
- Apply libraries to GraphRAG stages (4 files) - 2 hrs
- Apply libraries to Ingestion (12 files) - 2.5 hrs

**Wednesday** (6 hours):

- Apply libraries to Services (20 files) - 5 hrs
- Apply libraries to Chat (7 files) - 1 hr

**Thursday** (4 hours):

- Final cleanup: Pipelines + base classes - 1 hr
- Integration testing - 1 hr
- Run 10-chunk pipeline with all libraries - 1 hr
- Document changes - 1 hr

**Deliverable**: All 69 files using libraries, ~400 lines removed

---

### Summary

**Phase 1: Implement Tier 2 Libraries** (6 hrs)

- 7 libraries with simple implementations
- Tests for each

**Phase 2: Apply to All Code** (18 hrs)

- 69 files updated
- Observability throughout
- ~400 lines removed

**Total**: 24 hours for complete code cleanup with full library support

---

**Ready to start Monday with Tier 2 library implementation!**
