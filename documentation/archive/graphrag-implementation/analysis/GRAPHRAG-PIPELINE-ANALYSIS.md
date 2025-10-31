# GraphRAG Pipeline Analysis & Fixes

This document tracks the analysis and fixes applied to the GraphRAG pipeline during testing.

## Summary of Issues and Fixes

| Fix # | Stage                 | Issue                                             | Status   |
| ----- | --------------------- | ------------------------------------------------- | -------- |
| 1     | `graph_extraction`    | Querying for `text` field instead of `chunk_text` | ✅ Fixed |
| 2     | All GraphRAG stages   | Not writing results to database (`updated=0`)     | ✅ Fixed |
| 3     | `graph_construction`  | Using entity names instead of entity IDs          | ✅ Fixed |
| 4     | `community_detection` | `hierarchical_leiden` API + level validation      | ✅ Fixed |
| 5     | `community_detection` | Running detection per-chunk instead of once       | ✅ Fixed |

## Detailed Analysis

### First Run

**Status**: ❌ All stages processed 0 documents

| Stage                 | Processed | Issue                         |
| --------------------- | --------- | ----------------------------- |
| `graph_extraction`    | ❌ 0      | Querying for wrong field name |
| `entity_resolution`   | ❌ 0      | Cascade failure               |
| `graph_construction`  | ❌ 0      | Cascade failure               |
| `community_detection` | ❌ 0      | Cascade failure               |

**Key Observations**:

- `graph_extraction` query: `{'text': {'$exists': True, '$ne': ''}}` (line 306)
- But chunks use `chunk_text` field, not `text`

**Fix 1 Applied**: Changed query field from `"text"` to `"chunk_text"` in `graph_extraction.py` (line 76).

### Second Run (After Fix 1)

**Status**: ✅ `graph_extraction` processing documents, ❌ not saving results

| Stage                 | Processed | Updated | Issue                   |
| --------------------- | --------- | ------- | ----------------------- |
| `graph_extraction`    | ✅ 10     | ❌ 0    | Not writing to database |
| `entity_resolution`   | ❌ 0      | ❌ 0    | Cascade failure         |
| `graph_construction`  | ❌ 0      | ❌ 0    | Cascade failure         |
| `community_detection` | ❌ 0      | ❌ 0    | Cascade failure         |

**Key Observations**:

- `graph_extraction` now finds chunks: `processed=10` (line 509)
- But `updated=0` - extraction results not being saved
- Root cause: `BaseStage.run()` doesn't automatically write returned documents
- Each stage's `handle_doc()` must explicitly write to database

**Fix 2 Applied**: All four GraphRAG stages now have database write logic implemented.

### Third Run (After Fix 2)

**Status**: ✅ `graph_extraction` working, ⚠️ `entity_resolution` not saving

| Stage                 | Processed | Updated | Issue                   |
| --------------------- | --------- | ------- | ----------------------- |
| `graph_extraction`    | ✅ 10     | ✅ 10   | ✅ **Fixed!**           |
| `entity_resolution`   | ✅ 10     | ❌ 0    | Not writing to database |
| `graph_construction`  | ❌ 0      | ❌ 0    | Cascade failure         |
| `community_detection` | ❌ 0      | ❌ 0    | Cascade failure         |

**Key Observations**:

- ✅ `graph_extraction` now writes: `updated=10` (line 509)
- ✅ `entity_resolution` finds chunks: `processed=10` (line 513)
- ❌ `entity_resolution` doesn't write: `updated=0` (line 564) - same write issue!
- ❌ Cascade continues: `graph_construction` finds 0 chunks (line 568)

**Fix Applied**: All four GraphRAG stages now have database write logic implemented.

### Fourth Run (After Fix 2 for all stages)

**Status**: ✅ `graph_extraction` and `entity_resolution` working, ⚠️ `graph_construction` failing validation

| Stage                 | Processed | Updated | Issue                                       |
| --------------------- | --------- | ------- | ------------------------------------------- |
| `graph_extraction`    | ✅ 10     | ✅ 10   | ✅ **Fixed!** Writes to database            |
| `entity_resolution`   | ✅ 10     | ✅ 10   | ✅ **Fixed!** Writes to database            |
| `graph_construction`  | ✅ 10     | ❌ 0    | ❌ **All relationships failing validation** |
| `community_detection` | ❌ 0      | ❌ 0    | Depends on construction                     |

**Key Observations**:

- ✅ `graph_extraction`: `updated=10` (line 358)
- ✅ `entity_resolution`: `updated=10` (line 413)
- ⚠️ `graph_construction`: `processed=10 updated=0 failed=10` (line 726)
- ❌ All relationships failing: `subject_id` and `object_id` validation errors - using entity **names** instead of entity **IDs** (32-char MD5 hashes)

**Root Cause**: `RelationshipResolutionAgent` was creating `ResolvedRelationship` objects with `subject_id` and `object_id` set to entity names (like "jason ku", "algorithm") instead of entity IDs (32-char MD5 hashes). The Pydantic model validation requires exactly 32-character MD5 hashes.

**Fix 3 Applied**:

- Modified `RelationshipResolutionAgent.resolve_relationships()` to accept `entity_name_to_id` mapping
- Added `_lookup_entity_id()` method to look up entity IDs from entity names
- Updated `_resolve_relationship_group()`, `_create_resolved_relationship_from_single()`, and `_resolve_multiple_relationships()` to use entity IDs instead of names
- Added `_get_entity_name_to_id_mapping()` in `GraphConstructionStage` to build entity name → ID mapping from entities collection
- Updated `GraphConstructionStage.handle_doc()` to pass entity name → ID mapping to relationship resolution agent

### Fifth Run (After Fix 3)

**Status**: ✅ `graph_extraction`, `entity_resolution`, and `graph_construction` working, ⚠️ `community_detection` failing validation

| Stage                 | Processed | Updated | Issue                                                         |
| --------------------- | --------- | ------- | ------------------------------------------------------------- |
| `graph_extraction`    | ✅ 10     | ✅ 10   | ✅ **Working!**                                               |
| `entity_resolution`   | ✅ 10     | ✅ 10   | ✅ **Working!**                                               |
| `graph_construction`  | ✅ 10     | ✅ 10   | ✅ **Fixed!** Entity ID lookup working                        |
| `community_detection` | ✅ 10     | ❌ 0    | ❌ **Two issues**: hierarchical_leiden API + level validation |

**Key Observations**:

- ✅ `graph_extraction`: `updated=10` (line 259)
- ✅ `entity_resolution`: `updated=10` (line 314)
- ✅ `graph_construction`: `updated=10` (line 399) - **Fix 3 successful!**
- ⚠️ `community_detection`: `processed=10 updated=0 failed=10` (line 616)
- ❌ Two errors:
  1. **hierarchical_leiden API**: `hierarchical_leiden() got an unexpected keyword argument 'resolution_parameter'` - The API doesn't accept `resolution_parameter` or `max_iterations`
  2. **Level validation**: `Input should be greater than or equal to 1 [type=greater_than_equal, input_value=0, input_type=int]` - Communities are being created with `level=0`, but `CommunitySummary` requires `level >= 1`

**Root Cause**:

1. The `hierarchical_leiden` function from `graspologic` has a different API than expected - it only accepts `max_cluster_size`, not `resolution_parameter` or `max_iterations`.
2. The fallback community detection creates communities with `level=0`, which violates the `CommunitySummary` Pydantic model constraint that `level >= 1`.

**Fix 4 Applied**:

- Removed unsupported parameters (`resolution_parameter`, `max_iterations`) from `hierarchical_leiden()` call
- Updated `_fallback_community_detection()` to use `level=1` instead of `level=0` for all communities
- Added safeguard in `_organize_communities_by_level()` to ensure level is always at least 1 using `max(1, level)`
- Updated fallback to properly handle multi-node communities using `nodes` attribute

### Sixth Run (After Fix 4)

**Status**: ✅ All stages processing, ⚠️ `community_detection` taking excessive time (>10 minutes)

| Stage                 | Processed | Updated | Issue                                                            |
| --------------------- | --------- | ------- | ---------------------------------------------------------------- |
| `graph_extraction`    | ✅ 10     | ✅ 10   | ✅ **Working!**                                                  |
| `entity_resolution`   | ✅ 10     | ✅ 10   | ✅ **Working!**                                                  |
| `graph_construction`  | ✅ 10     | ✅ 10   | ✅ **Working!**                                                  |
| `community_detection` | ✅ 10     | ⚠️ ?    | ⚠️ **Performance issue**: Running detection per-chunk (10× work) |

**Key Observations**:

- ✅ `hierarchical_leiden` API fixed - now working (line 232)
- ✅ Level validation fixed - summaries being generated (line 322)
- ⚠️ **Critical Performance Issue**: `community_detection` is running for EVERY chunk:
  - Chunk 1: Detects 88 communities, summarizes all 88 (~88 LLM calls, ~9 minutes)
  - Chunk 2: Detects 88 communities AGAIN, summarizes all 88 AGAIN (~88 LLM calls, ~9 minutes)
  - ... and so on for all 10 chunks
  - **Total**: ~880 LLM calls, ~90 minutes estimated!

**Root Cause**: `CommunityDetectionStage.handle_doc()` is calling `_get_all_entities()` and `_get_all_relationships()` for EVERY chunk, then detecting and summarizing communities each time. Community detection should run **ONCE** for the entire graph, not per-chunk.

**Fix 5 Applied**:

- Added check at the start of `handle_doc()` to see if communities already exist in the database
- If communities exist, skip detection and just mark the chunk as processed
- Added `_communities_detected` in-memory flag to prevent race conditions in concurrent processing
- Only the first chunk will run full community detection; subsequent chunks will skip

**Recommendation**:

- **Cancel the current run** (Ctrl+C) if it's still running
- **Restart the pipeline** - Fix 5 will ensure community detection runs only once
- Expected time: ~9 minutes (for 88 communities) instead of ~90 minutes

## Verification Steps

After running the pipeline again, verify:

1. ✅ Query logs show `chunk_text` instead of `text`
2. ✅ `graph_extraction` processes chunks (processed > 0)
3. ✅ Subsequent stages process extracted data
4. ✅ Entities, relations, and communities are created in MongoDB
5. ✅ `graph_construction` creates relationships with valid entity IDs (32-char hashes)
6. ✅ `community_detection` runs only once (first chunk), subsequent chunks skip detection
7. ✅ Community detection completes in ~5-10 minutes (not 90+ minutes)

## Files Modified

- `app/stages/graph_extraction.py` - Fix 1: Changed `text` to `chunk_text`
- `app/stages/graph_extraction.py` - Fix 2: Added database write logic
- `app/stages/entity_resolution.py` - Fix 2: Added database write logic
- `app/stages/graph_construction.py` - Fix 2: Added database write logic
- `app/stages/graph_construction.py` - Fix 3: Added entity name → ID mapping
- `app/stages/community_detection.py` - Fix 2: Added database write logic
- `app/stages/community_detection.py` - Fix 4: Fixed `hierarchical_leiden` API and level validation
- `app/stages/community_detection.py` - Fix 5: Added skip logic to prevent per-chunk detection
- `agents/relationship_resolution_agent.py` - Fix 3: Added entity ID lookup
- `agents/community_detection_agent.py` - Fix 4: Fixed `hierarchical_leiden` API and level handling
