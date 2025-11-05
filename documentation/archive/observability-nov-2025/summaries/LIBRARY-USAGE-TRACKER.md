# Tier 2 Library Usage Tracker

**Purpose**: Track which library features are actually used in production code  
**Status**: In Progress - Applying libraries to code  
**Date**: November 3, 2025

---

## ✅ Libraries Applied to Code

### 1. database/ Library

**Applied To**:

- ✅ `business/stages/graphrag/entity_resolution.py` (line 19, 342)
- ✅ `business/stages/graphrag/graph_construction.py` (line 22, 458)

**Features Used**:

- ✅ `batch_insert()` - Used for entity mentions and co-occurrence relationships
  - `collection` parameter: ✅ Used
  - `documents` parameter: ✅ Used
  - `batch_size` parameter: ✅ Used (500-1000)
  - `ordered` parameter: ✅ Used (False for error tolerance)

**Features NOT Used** (mark with TODO):

- ⏳ `batch_update()` - Not yet applied (candidates exist)
- ⏳ `batch_delete()` - Not needed yet
- ⏳ `upsert` option in batch_update - Not needed yet

**Real-World Impact**:

- **Performance**: Batch inserts reduce DB roundtrips
- **Error Handling**: Get detailed statistics (inserted/failed counts)
- **Code Quality**: More maintainable than manual loops

**Evidence of Need**:

- entity_resolution: Inserting entity mentions (can be 10-100 per chunk)
- graph_construction: Inserting co-occurrence relationships (can be hundreds)

**Verdict**: ✅ **NEEDED** - Provides real value in production code

---

### 2. serialization/ Library

**Applied To**:

- Used indirectly by agents (EntityModel, RelationshipModel conversion)
- Direct usage pending in stages

**Features Used** (from agents):

- ✅ `to_dict()` - Converting Pydantic models to MongoDB docs
- ✅ `from_dict()` - Loading Pydantic models from MongoDB docs
- ✅ `json_encoder()` - Handling ObjectId, datetime, Decimal128

**Features Tested**:

- ✅ All features tested (12 tests passing)
- ✅ Bugs fixed (3 bugs caught by tests)

**Verdict**: ✅ **NEEDED** - Core functionality for MongoDB integration

---

### 3. data_transform/ Library

**Applied To**:

- Not yet applied to production code

**Features Available**:

- `flatten()` - Flatten nested dicts
- `group_by()` - Group list of dicts by key
- `deduplicate()` - Remove duplicates
- `merge_dicts()` - Merge dictionaries

**Features Tested**:

- ✅ All features tested (10 tests passing)
- ✅ Zero bugs found

**Potential Use Cases** (to investigate):

- entity_resolution: group_by() for grouping entities by name
- graph_construction: deduplicate() for removing duplicate relationships?

**Verdict**: ⏳ **PENDING** - Needs real usage to validate

---

### 4. concurrency/ Library

**Applied To**:

- Not yet applied

**Features Available**:

- `run_concurrent_with_limit()` - Parallel execution
- `run_concurrent_map()` - Map with error handling
- `run_llm_concurrent()` - LLM calls with retry + QPS

**Potential Use Cases**:

- Processing multiple chunks in parallel?
- Parallel LLM calls for entity resolution?

**Verdict**: ⏳ **UNCERTAIN** - Current code is sequential, need to validate if parallelism needed

**TODO**: Check if GraphRAG stages could benefit from parallel processing

---

### 5. rate_limiting/ Library

**Applied To**:

- Not yet applied

**Features Available**:

- `RateLimiter` - Token bucket rate limiter
- `rate_limit` decorator - Decorator pattern

**Potential Use Cases**:

- LLM API calls (already handled by retry library with backoff)
- External API calls?

**Verdict**: ⏳ **UNCERTAIN** - May not be needed (retry library handles LLM throttling)

**TODO**: Investigate if needed for external APIs

---

### 6. caching/ Library

**Applied To**:

- Not yet applied

**Features Available**:

- `LRUCache` - Manual cache
- `@cached` decorator - Automatic caching
- TTL support
- Statistics tracking

**Potential Use Cases**:

- Cache entity lookups in services?
- Cache repeated queries?

**Verdict**: ⏳ **UNCERTAIN** - Need to find real repeated queries first

**TODO**: Profile code to find caching opportunities

---

### 7. configuration/ Library

**Applied To**:

- Not yet applied

**Features Available**:

- `load_config()` - Load config with priority (args > env > defaults)
- Type conversion
- Pydantic/dataclass support

**Potential Use Cases**:

- GraphRAG stage config loading?
- Currently using Pydantic directly

**Verdict**: ⏳ **UNCERTAIN** - Current approach works, need to validate benefit

**TODO**: Check if current config loading could be simplified

---

### 8. validation/ Library

**Applied To**:

- Not yet applied

**Features Available**:

- `MinLength`, `MaxLength`, `Pattern`, `Range`, `NotEmpty`
- `Custom` validation rules
- Field and dict validation

**Potential Use Cases**:

- Validating user input in API endpoints?
- Pydantic already handles most model validation

**Verdict**: ⏳ **UNCERTAIN** - Pydantic covers most cases

**TODO**: Check for business rules that Pydantic can't handle

---

## 📊 Usage Summary

### Actually Used in Production ✅

1. **database.batch_insert()** - 2 files, real performance impact
2. **serialization (to_dict, from_dict, json_encoder)** - Core MongoDB integration

### Tested But Not Applied ⏳

3. **data_transform (all functions)** - Tested, awaiting real use case
4. **database.batch_update()** - Tested, candidates exist
5. **database.batch_delete()** - Tested, no current need

### Not Yet Used or Tested ❓

6. **concurrency (all functions)** - May not be needed (code is sequential)
7. **rate_limiting (all functions)** - May not be needed (retry handles throttling)
8. **caching (all functions)** - Need profiling to find use cases
9. **configuration (all functions)** - Current approach works
10. **validation (all functions)** - Pydantic covers most cases

---

## 🎓 Learnings

### What's Working

1. **batch_insert()** - Clear, immediate value
2. **Testing found bugs** - 3 bugs in serialization caught early

### Over-Engineering Concerns

1. **concurrency/** - Code is sequential, may not need parallel execution
2. **rate_limiting/** - retry library already handles LLM throttling
3. **caching/** - No evidence yet of repeated queries needing cache
4. **configuration/** - Current Pydantic config works fine
5. **validation/** - Pydantic handles model validation well

### Recommendations

1. ✅ **Keep**: database (batch\_\*), serialization (core need)
2. ⏳ **Validate**: data_transform (find real use cases)
3. ❓ **Simplify or Remove**: concurrency, rate_limiting, caching, configuration, validation

**Action**: Continue applying libraries to Services to gather more data

---

## 📝 Next Steps

1. Apply libraries to Services (5 files) - gather more usage data
2. Mark unused library features with `# TODO: Implement when needed`
3. Create simplification plan based on real usage
4. Consider removing or simplifying libraries with 0 usage

**Goal**: Evidence-based decision on which libraries provide real value
