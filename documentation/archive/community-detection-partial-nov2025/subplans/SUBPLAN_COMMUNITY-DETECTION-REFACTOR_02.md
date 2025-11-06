# SUBPLAN: Run Metadata & Provenance Implementation

**Mother Plan**: PLAN_COMMUNITY-DETECTION-REFACTOR.md  
**Achievement Addressed**: Achievement 0.2 - Run Metadata & Provenance Implemented  
**Status**: In Progress  
**Created**: 2025-11-06 21:50 UTC  
**Estimated Effort**: 3-4 hours

---

## 🎯 Objective

Implement run metadata and provenance system to track detection parameters, graph signatures, and enable reproducible runs. This allows skipping re-detection when parameters and graph haven't changed, and provides full audit trail for all detection runs.

---

## 📋 What Needs to Be Created

### Files to Create

1. **`business/services/graphrag/run_metadata.py`**:

   - `compute_params_hash(params_dict)` - Compute hash from sorted params
   - `compute_graph_signature(entities, relationships)` - Compute hash from graph structure
   - `create_run_document(stage, params_hash, graph_signature, ...)` - Create run doc
   - `find_existing_run(stage, params_hash, graph_signature)` - Find matching run
   - `update_run_document(run_id, status, metrics)` - Update run status

2. **`tests/business/services/graphrag/test_run_metadata.py`**:
   - Test params_hash computation (deterministic, different params → different hash)
   - Test graph_signature computation (same graph → same signature)
   - Test run document creation and retrieval
   - Test existing run detection

### Files to Modify

1. **`business/stages/graphrag/community_detection.py`**:

   - Import run_metadata service
   - Compute params_hash in `handle_doc()` before detection
   - Compute graph_signature from entities/relationships
   - Check for existing run (same params_hash + graph_signature)
   - Create run document before detection
   - Update run document after detection (status, metrics)
   - Stamp `run_id` and `params_hash` on all community documents
   - Stamp `run_id` and `params_hash` in chunk metadata

2. **`business/services/graphrag/indexes.py`** (if exists):
   - Add index on `graphrag_runs` collection: `(stage, params_hash, graph_signature)`

---

## 🔧 Approach

### Step 1: Create Run Metadata Service

- Create `business/services/graphrag/run_metadata.py`:
  - `compute_params_hash(params_dict)`:
    - Sort params dict by keys
    - JSON encode with sorted keys
    - SHA1 hash, return first 12 characters
  - `compute_graph_signature(entities, relationships)`:
    - Create sorted list of tuples: `(subject_id, object_id, predicate, round(confidence,2))`
    - Sort list
    - Join with comma, hash with SHA1
    - Return first 12 characters
  - `create_run_document(...)`: Create run document with all metadata
  - `find_existing_run(...)`: Query for matching run
  - `update_run_document(...)`: Update run status and metrics

### Step 2: Integrate into Community Detection Stage

- In `handle_doc()`, before detection:

  1. Collect all parameters into dict:
     - algorithm, resolution_parameter, min_cluster_size, max_cluster_size
     - seed (from env), ontology_version (from loader)
     - model_name, temperature, concurrency
  2. Compute `params_hash`
  3. Get entities and relationships
  4. Compute `graph_signature`
  5. Check for existing run: `find_existing_run("community_detection", params_hash, graph_signature)`
  6. If exists and completed: skip detection, use existing run_id
  7. If not exists: create run document with status="started"

- After detection:
  1. Update run document with status="completed"
  2. Add metrics: total_communities, modularity, coverage, etc.
  3. Stamp `run_id` and `params_hash` on all community documents in `_store_communities()`
  4. Stamp `run_id` and `params_hash` in chunk metadata

### Step 3: Load Ontology Version

- Import ontology loader
- Get ontology version from loader result
- Include in params_hash computation

### Step 4: Create Indexes

- Add index on `graphrag_runs` collection for efficient lookups
- Index: `(stage, params_hash, graph_signature)`

---

## 🧪 Tests Required

### Unit Tests

1. **`test_compute_params_hash_deterministic`**:

   - Same params → same hash
   - Different order → same hash (sorted keys)

2. **`test_compute_params_hash_different_params`**:

   - Different params → different hash

3. **`test_compute_graph_signature_deterministic`**:

   - Same graph → same signature
   - Different order → same signature (sorted)

4. **`test_compute_graph_signature_different_graphs`**:

   - Different graph → different signature

5. **`test_create_run_document`**:

   - Creates document with all required fields
   - Document structure correct

6. **`test_find_existing_run`**:

   - Finds run with matching params_hash + graph_signature
   - Returns None if no match

7. **`test_update_run_document`**:
   - Updates status and metrics correctly

### Integration Tests

1. **`test_community_detection_skips_existing_run`**:

   - Same params + graph → skips detection
   - Uses existing run_id

2. **`test_community_detection_creates_new_run`**:

   - Different params → creates new run
   - Different graph → creates new run

3. **`test_communities_stamped_with_run_id`**:
   - All stored communities have run_id and params_hash

---

## ✅ Expected Results

### Functional Changes

- `graphrag_runs` collection created and used
- Run metadata persisted before/after detection
- Existing runs detected and reused
- All communities stamped with run_id and params_hash
- Chunk metadata includes run_id and params_hash

### Observable Outcomes

- Running detection twice with same params/graph → skips re-detection
- Running with different params → creates new run
- Can query run history by params_hash
- Can reproduce results using run_id

### Success Indicators

- All tests passing
- Run documents created correctly
- Existing runs detected and reused
- Communities have run_id stamped
- No duplicate detection runs for same params/graph

---

## 🔗 Dependencies

- Achievement 0.1 (Stable Community IDs) - ✅ Complete
- Ontology loader (for version) - Available
- Database access (for graphrag_runs collection) - Available

---

## 📝 Execution Task Reference

- **EXECUTION_TASK_COMMUNITY-DETECTION-REFACTOR_02_01.md** - Implementation and testing

---

## 🎯 Notes

- Run metadata enables reproducibility and audit trail
- Graph signature detects when graph changes (entities/relations added/removed)
- Params hash detects when configuration changes
- Both must match to reuse existing run
- Run documents enable querying history and comparing runs
