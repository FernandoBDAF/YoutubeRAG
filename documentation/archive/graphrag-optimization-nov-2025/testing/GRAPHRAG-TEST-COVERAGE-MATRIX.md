# GraphRAG Test Coverage Matrix

**Date**: November 3, 2025  
**Purpose**: Complete audit of GraphRAG functions and test coverage  
**Status**: Comprehensive analysis for test planning

---

## 📊 Agent Functions Coverage

### extraction.py Agent (4 functions after cleanup)

| Function                 | Type       | Has Test? | Used By | Action                       |
| ------------------------ | ---------- | --------- | ------- | ---------------------------- |
| `__init__`               | Init       | ❌        | Stage   | Integration tested           |
| `extract_from_chunk`     | Public     | ❌        | Stage   | ✅ Add test (critical)       |
| `_extract_with_llm`      | Private    | ❌        | Self    | Covered by retry lib test    |
| `_validate_and_enhance`  | Private    | ❌        | Self    | ✅ Add test (business logic) |
| ~~extract_batch~~        | ❌ Removed | -         | -       | ✅ Removed (dead code)       |
| ~~get_extraction_stats~~ | ❌ Removed | -         | -       | ✅ Removed (dead code)       |

**Status**: 2 critical functions need tests  
**Priority**: High (core extraction logic)

---

### entity_resolution.py Agent (13 functions)

| Function                              | Type    | Has Test? | Used By | Action                           |
| ------------------------------------- | ------- | --------- | ------- | -------------------------------- |
| `__init__`                            | Init    | ❌        | Stage   | Integration tested               |
| `resolve_entities`                    | Public  | ❌        | Stage   | ✅ Add test (critical)           |
| `_group_entities_by_name`             | Private | ❌        | Self    | Covered by resolve_entities      |
| `_normalize_entity_name`              | Private | ✅        | Self    | ✅ Already tested (this session) |
| `_resolve_entity_group`               | Private | ❌        | Self    | Covered by resolve_entities      |
| `_create_resolved_entity_from_single` | Private | ❌        | Self    | Covered by resolve_entities      |
| `_resolve_multiple_entities`          | Private | ❌        | Self    | Covered by resolve_entities      |
| `_determine_canonical_name`           | Private | ❌        | Self    | Unit test helpful                |
| `_determine_entity_type`              | Private | ❌        | Self    | Unit test helpful                |
| `_resolve_descriptions`               | Private | ❌        | Self    | Covered by retry test            |
| `_resolve_with_llm`                   | Private | ❌        | Self    | Covered by retry lib test        |
| `_calculate_overall_confidence`       | Private | ❌        | Self    | Unit test helpful                |
| `get_resolution_stats`                | Public  | ❌        | None    | Stats only, low priority         |

**Status**: 1 critical function + 3 helper functions could use tests  
**Priority**: Medium (main function tested via integration)

---

### relationship_resolution.py Agent (12 functions)

| Function                                    | Type    | Has Test? | Used By | Action                    |
| ------------------------------------------- | ------- | --------- | ------- | ------------------------- |
| `__init__`                                  | Init    | ❌        | Stage   | Integration tested        |
| `resolve_relationships`                     | Public  | ❌        | Stage   | ✅ Add test (critical)    |
| `_group_relationships_by_tuple`             | Private | ❌        | Self    | Covered by resolve        |
| `_resolve_relationship_group`               | Private | ❌        | Self    | Covered by resolve        |
| `_create_resolved_relationship_from_single` | Private | ❌        | Self    | Covered by resolve        |
| `_resolve_multiple_relationships`           | Private | ❌        | Self    | Covered by resolve        |
| `_lookup_entity_id`                         | Private | ❌        | Self    | Unit test helpful         |
| `_resolve_descriptions`                     | Private | ❌        | Self    | Covered by retry test     |
| `_resolve_with_llm`                         | Private | ❌        | Self    | Covered by retry lib test |
| `_calculate_overall_confidence`             | Private | ❌        | Self    | Unit test helpful         |
| `validate_entity_existence`                 | Public  | ❌        | Stage   | Unit test helpful         |
| `get_resolution_stats`                      | Public  | ❌        | None    | Stats only, low priority  |

**Status**: 1 critical function + 3 helper functions could use tests  
**Priority**: Medium (main function tested via integration)

---

### community_summarization.py Agent (10 functions)

| Function                          | Type    | Has Test? | Used By | Action                     |
| --------------------------------- | ------- | --------- | ------- | -------------------------- |
| `__init__`                        | Init    | ❌        | Stage   | Integration tested         |
| `summarize_communities`           | Public  | ❌        | Stage   | ✅ Add test (critical)     |
| `_summarize_single_community`     | Private | ❌        | Self    | Covered by summarize       |
| `_generate_summary_text`          | Private | ❌        | Self    | Covered by retry test      |
| `_generate_with_llm`              | Private | ❌        | Self    | Covered by retry lib test  |
| `_extract_title`                  | Private | ❌        | Self    | Unit test helpful          |
| `summarize_large_community`       | Public  | ❌        | None?   | ⏳ Check if used or remove |
| `_select_important_entities`      | Private | ❌        | Self    | Unit test helpful          |
| `_select_important_relationships` | Private | ❌        | Self    | Unit test helpful          |
| `get_summarization_stats`         | Public  | ❌        | None    | Stats only, low priority   |

**Status**: 1-2 critical functions need tests  
**Priority**: Medium (LLM calls covered by retry)

---

### community_detection.py Agent (8 functions)

| Function                         | Type    | Has Test? | Used By | Action                   |
| -------------------------------- | ------- | --------- | ------- | ------------------------ |
| `__init__`                       | Init    | ❌        | Stage   | Integration tested       |
| `detect_communities`             | Public  | ❌        | Stage   | ✅ Add test (critical)   |
| `_create_networkx_graph`         | Private | ❌        | Self    | Unit test helpful        |
| `_fallback_community_detection`  | Private | ❌        | Self    | Unit test helpful        |
| `_organize_communities_by_level` | Private | ❌        | Self    | Covered by detect        |
| `_calculate_coherence_score`     | Private | ❌        | Self    | Unit test helpful        |
| `_calculate_community_quality`   | Private | ❌        | Self    | Covered by detect        |
| `get_community_statistics`       | Public  | ❌        | None    | Stats only, low priority |

**Status**: 1 critical function + 3 helper functions could use tests  
**Priority**: High (known issues in past)

---

### link_prediction.py Agent (6 functions)

| Function                        | Type    | Has Test? | Used By | Action             |
| ------------------------------- | ------- | --------- | ------- | ------------------ |
| `__init__`                      | Init    | ❌        | Stage   | Integration tested |
| `predict_missing_links`         | Public  | ❌        | Stage   | ✅ Add test        |
| `_predict_via_common_neighbors` | Private | ❌        | Self    | Unit test helpful  |
| `_predict_via_embeddings`       | Private | ❌        | Self    | Unit test helpful  |
| `_infer_predicate_from_types`   | Private | ❌        | Self    | Unit test helpful  |
| `_deduplicate_predictions`      | Private | ❌        | Self    | Unit test helpful  |

**Status**: 1 critical function + all helpers could use tests  
**Priority**: Medium (graph algorithm)

---

## 📊 Stage Functions Coverage

### extraction.py Stage (7 functions after cleanup)

| Function                     | Type       | Has Test? | Used By   | Action                 |
| ---------------------------- | ---------- | --------- | --------- | ---------------------- |
| `setup`                      | Lifecycle  | ❌        | BaseStage | Integration tested     |
| `iter_docs`                  | Lifecycle  | ❌        | BaseStage | Integration tested     |
| `handle_doc`                 | Lifecycle  | ❌        | BaseStage | Integration tested     |
| `_mark_extraction_failed`    | Private    | ❌        | Self      | Covered by handle_doc  |
| `get_processing_stats`       | Public     | ❌        | Pipeline  | ✅ Add test            |
| `cleanup_failed_extractions` | Public     | ❌        | CLI?      | ⏳ Check if used       |
| ~~process_batch~~            | ❌ Removed | -         | -         | ✅ Removed (dead code) |
| ~~get_extraction_summary~~   | ❌ Removed | -         | -         | ✅ Removed (dead code) |

**Status**: 1 function used by pipeline needs test  
**Priority**: Medium

---

### entity_resolution.py Stage (8 functions after cleanup)

| Function                     | Type       | Has Test? | Used By    | Action                 |
| ---------------------------- | ---------- | --------- | ---------- | ---------------------- |
| `setup`                      | Lifecycle  | ❌        | BaseStage  | Integration tested     |
| `iter_docs`                  | Lifecycle  | ❌        | BaseStage  | Integration tested     |
| `handle_doc`                 | Lifecycle  | ❌        | BaseStage  | Integration tested     |
| `_store_resolved_entities`   | Private    | ❌        | handle_doc | Covered by integration |
| `_update_existing_entity`    | Private    | ❌        | Self       | Covered by integration |
| `_insert_new_entity`         | Private    | ❌        | Self       | Covered by integration |
| `_store_entity_mentions`     | Private    | ❌        | handle_doc | ✅ Batch_insert tested |
| `_mark_resolution_failed`    | Private    | ❌        | Self       | Covered by handle_doc  |
| `get_resolution_stats`       | Public     | ❌        | Pipeline   | ✅ Add test            |
| `cleanup_failed_resolutions` | Public     | ❌        | CLI?       | ⏳ Check if used       |
| ~~process_batch~~            | ❌ Removed | -         | -          | ✅ Removed (dead code) |

**Status**: 1 function used by pipeline needs test  
**Priority**: Medium

---

### graph_construction.py Stage (22 functions)

| Function                                 | Type      | Has Test? | Used By    | Action                     |
| ---------------------------------------- | --------- | --------- | ---------- | -------------------------- |
| `setup`                                  | Lifecycle | ❌        | BaseStage  | Integration tested         |
| `iter_docs`                              | Lifecycle | ❌        | BaseStage  | Integration tested         |
| `handle_doc`                             | Lifecycle | ❌        | BaseStage  | Integration tested         |
| `_get_existing_entity_ids`               | Private   | ❌        | handle_doc | Covered by integration     |
| `_get_entity_name_to_id_mapping`         | Private   | ❌        | handle_doc | Covered by integration     |
| `_store_resolved_relationships`          | Private   | ❌        | handle_doc | Covered by integration     |
| `_update_existing_relationship`          | Private   | ❌        | Self       | Covered by integration     |
| `_insert_new_relationship`               | Private   | ❌        | Self       | Covered by integration     |
| `_add_co_occurrence_relationships`       | Private   | ❌        | finalize   | ✅ Batch_insert tested     |
| `_add_semantic_similarity_relationships` | Private   | ❌        | finalize   | ✅ Batch_insert tested     |
| `_add_cross_chunk_relationships`         | Private   | ❌        | finalize   | ✅ Batch_insert tested     |
| `_determine_cross_chunk_predicate`       | Private   | ❌        | Self       | Unit test helpful          |
| `_add_bidirectional_relationships`       | Private   | ❌        | finalize   | ✅ Batch_insert tested     |
| `_calculate_current_graph_density`       | Private   | ❌        | finalize   | Unit test helpful          |
| `_add_predicted_relationships`           | Private   | ❌        | finalize   | ✅ Batch_insert tested     |
| `_mark_construction_failed`              | Private   | ❌        | Self       | Covered by handle_doc      |
| `process_batch`                          | Public    | ❌        | None       | ⏳ Check if used or remove |
| `calculate_graph_metrics`                | Public    | ❌        | None?      | ⏳ Check if used           |
| `get_construction_stats`                 | Public    | ❌        | Pipeline   | ✅ Add test                |
| `cleanup_failed_constructions`           | Public    | ❌        | CLI?       | ⏳ Check if used           |
| `finalize`                               | Lifecycle | ❌        | BaseStage  | Integration tested         |

**Status**: Many helper functions, batch operations tested via lib  
**Priority**: Check which public functions are actually used

---

### community_detection.py Stage (14 functions)

| Function                     | Type      | Has Test? | Used By    | Action                     |
| ---------------------------- | --------- | --------- | ---------- | -------------------------- |
| `setup`                      | Lifecycle | ❌        | BaseStage  | Integration tested         |
| `iter_docs`                  | Lifecycle | ❌        | BaseStage  | Integration tested         |
| `handle_doc`                 | Lifecycle | ❌        | BaseStage  | Integration tested         |
| `_get_all_entities`          | Private   | ❌        | handle_doc | Covered by integration     |
| `_get_all_relationships`     | Private   | ❌        | handle_doc | Covered by integration     |
| `_store_communities`         | Private   | ❌        | handle_doc | Covered by integration     |
| `_update_existing_community` | Private   | ❌        | Self       | Covered by integration     |
| `_insert_new_community`      | Private   | ❌        | Self       | Covered by integration     |
| `_update_entity_communities` | Private   | ❌        | handle_doc | Covered by integration     |
| `_mark_detection_failed`     | Private   | ❌        | Self       | Covered by handle_doc      |
| `process_batch`              | Public    | ❌        | None       | ⏳ Check if used or remove |
| `get_detection_stats`        | Public    | ❌        | Pipeline   | ✅ Add test                |
| `cleanup_failed_detections`  | Public    | ❌        | CLI?       | ⏳ Check if used           |

**Status**: More process_batch to check  
**Priority**: Focus on critical path

---

## 📊 Summary Statistics

### Agent Functions

| Agent                   | Total Functions | Public | Private | Need Tests | Priority |
| ----------------------- | --------------- | ------ | ------- | ---------- | -------- |
| extraction              | 4               | 1      | 3       | 2          | High     |
| entity_resolution       | 13              | 2      | 11      | 1-4        | Medium   |
| relationship_resolution | 12              | 3      | 9       | 1-4        | Medium   |
| community_summarization | 10              | 3      | 7       | 1-2        | Medium   |
| community_detection     | 8               | 2      | 6       | 1-4        | High     |
| link_prediction         | 6               | 1      | 5       | 1-6        | Medium   |
| **Total**               | **53**          | **12** | **41**  | **7-22**   | -        |

---

### Stage Functions

| Stage               | Total Functions | Public | Private | Need Tests | Priority |
| ------------------- | --------------- | ------ | ------- | ---------- | -------- |
| extraction          | 7               | 3      | 4       | 1-2        | Medium   |
| entity_resolution   | 8               | 3      | 5       | 1          | Medium   |
| graph_construction  | 22              | 6      | 16      | 1-3        | Medium   |
| community_detection | 14              | 4      | 10      | 1          | Medium   |
| **Total**           | **51**          | **16** | **35**  | **4-8**    | -        |

---

## 🎯 Test Priority Recommendations

### Critical (Must Test)

**Agent Public Functions** (6 functions):

1. ✅ `extraction.extract_from_chunk` - Core extraction logic
2. ✅ `entity_resolution.resolve_entities` - Core resolution logic
3. ✅ `relationship_resolution.resolve_relationships` - Core resolution logic
4. ✅ `community_summarization.summarize_communities` - Core summarization
5. ✅ `community_detection.detect_communities` - Core detection logic
6. ✅ `link_prediction.predict_missing_links` - Core prediction logic

**Rationale**: These are the main entry points used by stages

---

### High Priority (Should Test)

**Agent Business Logic** (5 functions):

1. `extraction._validate_and_enhance` - Entity/relationship filtering
2. `entity_resolution._determine_canonical_name` - Name selection logic
3. `entity_resolution._calculate_overall_confidence` - Confidence calculation
4. `relationship_resolution._lookup_entity_id` - ID mapping logic
5. `community_detection._calculate_coherence_score` - Quality metric

**Rationale**: Complex business logic that could have bugs

---

### Medium Priority (Nice to Have)

**Stage Stats Functions** (4 functions):

1. `extraction.get_processing_stats` - Used by pipeline
2. `entity_resolution.get_resolution_stats` - Used by pipeline
3. `graph_construction.get_construction_stats` - Used by pipeline
4. `community_detection.get_detection_stats` - Used by pipeline

**Rationale**: Used but straightforward DB queries

---

### Low Priority or Remove

**Functions to Verify Usage** (7+ functions):

1. ⏳ `extraction.cleanup_failed_extractions` - Check CLI usage
2. ⏳ `entity_resolution.cleanup_failed_resolutions` - Check CLI usage
3. ⏳ `graph_construction.process_batch` - Likely unused
4. ⏳ `graph_construction.calculate_graph_metrics` - Likely unused
5. ⏳ `graph_construction.cleanup_failed_constructions` - Check CLI usage
6. ⏳ `community_detection.process_batch` - Likely unused
7. ⏳ `community_summarization.summarize_large_community` - Check if used

**Action**: Search for usage, remove if unused

---

## 📋 Proposed Test Implementation Plan

### Phase 1: Critical Agent Tests (2-3 hours)

**Create 6 test files** for agent public functions:

- `tests/business/agents/graphrag/test_extraction.py`
- `tests/business/agents/graphrag/test_entity_resolution.py`
- `tests/business/agents/graphrag/test_relationship_resolution.py`
- `tests/business/agents/graphrag/test_community_summarization.py`
- `tests/business/agents/graphrag/test_community_detection.py`
- `tests/business/agents/graphrag/test_link_prediction.py`

**Each test file** should test:

- Main public function with mocked LLM
- Critical business logic functions
- Edge cases

**Estimated**: 3-4 tests per agent × 6 agents = 18-24 tests

---

### Phase 2: Remove Unused Functions (1 hour)

**Search and verify**:

```bash
# Check cleanup functions
grep -r "cleanup_failed" app/ business/pipelines/

# Check other suspected unused
grep -r "calculate_graph_metrics\|summarize_large_community" app/ business/

# Check process_batch
grep -r "process_batch" app/ business/pipelines/
```

**Remove** if not found  
**Document** if used

**Estimated**: 30-50 more lines to remove

---

### Phase 3: Helper Function Tests (optional, 1-2 hours)

**Add tests for critical helpers**:

- Entity normalization (already done ✅)
- Confidence calculations
- ID lookups
- Coherence scoring

**Estimated**: 10-15 tests

---

## ✅ Recommended Immediate Actions

### Before Moving to Graph Construction Validation

**1. Quick Cleanup** (15 min):

- Search for `process_batch` usage in all stages
- Search for `cleanup_failed_*` usage
- Remove if not used

**2. Critical Test Priority** (decide):

- Option A: Add agent tests FIRST (2-3 hours)
- Option B: Validate stages FIRST, then add tests (current plan)
- Option C: Integration tests sufficient, skip unit tests

**3. Document Decision**:

- Which functions MUST have tests
- Which are covered by integration
- Which to remove

---

## 🎯 My Recommendation

### Recommended Approach

**Next 1 Hour**:

1. Quick search for unused functions (15 min)
2. Remove any additional dead code (15 min)
3. Validate graph_construction stage (15 min)
4. Validate community_detection stage (15 min)

**Then Decide**:

- If validation shows issues → Add tests for those areas
- If validation passes → Integration testing may be sufficient
- Document test strategy

**Benefit**: Evidence-based test decisions (like with libraries)

---

**Matrix Complete**: 104 total functions audited  
**Dead Code**: Already removed 210 lines, more to find  
**Test Priority**: 6 critical + 5 high priority = 11 core tests needed  
**Awaiting**: Your decision on next step
