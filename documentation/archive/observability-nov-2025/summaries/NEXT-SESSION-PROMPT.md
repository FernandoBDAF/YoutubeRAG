# Next Session Prompt - Critical Tasks

**Copy this entire prompt to start the next session**

---

## Context

We've implemented 13 libraries (4 Tier 1 + 9 Tier 2) and refactored 6 GraphRAG agents. Critical review found:

- ⚠️ Tier 2 libraries have 0% test coverage
- ⚠️ Tier 2 libraries not applied to code yet (0 usages)
- ⚠️ Some libraries may be over-engineered

**Review Documents**:

- `DEEP-REVIEW-CRITICAL-FINDINGS.md` (over-engineering analysis)
- `TEST-COVERAGE-CRITICAL-GAP.md` (missing tests)

---

## Tasks for This Session (Priority Order)

### Task 1: Create Tests for Critical Tier 2 Libraries (2 hours) ⭐ HIGHEST PRIORITY

**Goal**: Validate the 3 most critical libraries before applying to code

**Files to Create** (in `tests/core/libraries/`):

**1. serialization/test_serialization.py** (30 min):

```python
# Test to_dict() with Pydantic models
# Test from_dict() back to Pydantic
# Test json_encoder() with ObjectId, datetime, Decimal128
# Use EntityModel, RelationshipModel from our codebase
```

**2. data_transform/test_data_transform.py** (30 min):

```python
# Test flatten() - various nesting levels
# Test group_by() - different groupings
# Test deduplicate() - duplicate detection
# Test merge_dicts() - shallow and deep merge
```

**3. database/test_database.py** (1 hour):

```python
# Test batch_insert() - success, partial failure, total failure
# Test batch_update() - same scenarios
# Mock MongoDB collection
# Verify error handling
```

**Success Criteria**: All tests pass, bugs found and fixed

---

### Task 2: Apply Tier 2 Libraries to Code with Usage Validation (3-4 hours)

**Goal**: Use libraries in actual code, mark unused features with TODO

**Strategy**: "Apply and Validate" (Option B from review)

- Use libraries as-is in code
- Track which features are actually used
- Mark unused features with `# TODO: Implement when needed`
- Simplify later based on actual usage

**Files to Update** (follow CODE-REVIEW-IMPLEMENTATION-PLAN.md):

**Domain 2: GraphRAG Stages** (4 files):

- Apply database library (batch_insert, batch_update) to entity_resolution, graph_construction
- Track: Are transactions needed? Is error handling sufficient?

**Domain 4: Services** (subset - 5 files):

- Apply caching to entity lookups (if applicable)
- Apply rate_limiting where needed
- Track: Is threading needed? Is TTL needed?

**After Application**:

- Document which library features are used
- Mark unused features: `# TODO: Implement threading when we go multi-threaded`
- Create issue list for simplification

---

### Task 3: Document Principles More Clearly (1 hour)

**Goal**: Make our development principles crystal clear to prevent future violations

**Update**: `documentation/DOCUMENTATION-PRINCIPLES-AND-PROCESS.md`

**Add Section**: "Library Development Principles"

````markdown
## Library Development Principles

### 1. Usage-Driven Development

**Rule**: Don't implement until you have 2+ real usage cases

**Process**:

1. Identify pattern repeated 3+ times
2. Extract to simple library (~50 lines)
3. Apply to the 3 cases
4. Enhance based on actual needs

**Anti-Pattern**: Implementing full-featured library before any usage

### 2. Simple First, Always

**Rule**: Start with minimal viable implementation

**Process**:

1. Implement core feature only (20-50 lines)
2. Add TODO comments for advanced features
3. Test basic functionality
4. Apply to code
5. Enhance when actually needed

**Example**:

```python
# Simple LRU cache (20 lines)
class LRUCache:
    def __init__(self, max_size=100):
        self._cache = OrderedDict()
        self.max_size = max_size

    def get(self, key, default=None): ...
    def set(self, key, value): ...

    # TODO: Add TTL support when we need expiring cache
    # TODO: Add threading when we go multi-threaded
    # TODO: Add statistics when we need metrics
```
````

### 3. Test Before Complete

**Rule**: No library is "complete" without tests

**Process**:

1. Implement library
2. Create test file immediately
3. Test all functions
4. Fix bugs found
5. THEN mark complete

**Checklist**:

- [ ] Test file created in tests/core/libraries/[name]/
- [ ] All public functions tested
- [ ] Edge cases covered
- [ ] All tests passing

### 4. Apply Before Elaborate

**Rule**: Use in real code before adding features

**Process**:

1. Simple implementation
2. Test basic functionality
3. Apply to 1-2 real usage cases
4. Discover actual needs
5. Add features based on reality

**Anti-Pattern**: Adding features "we might need someday"

````

---

### Task 4: Root Directory Cleanup (5 minutes)

**Goal**: Restore documentation compliance (17 → 8 files)

**Archive these 9 completion docs**:
```bash
mv AGENT-REFACTOR-PATTERN-ESTABLISHED.md documentation/archive/observability-nov-2025/implementation/
mv AGENTS-REFACTOR-COMPLETE.md documentation/archive/observability-nov-2025/summaries/
mv AGENTS-REFACTOR-CONTINUE.md documentation/archive/observability-nov-2025/implementation/
mv FINAL-STATUS-ALL-COMPLETE.md documentation/archive/observability-nov-2025/summaries/
mv READY-FOR-CONTEXT-REFRESH.md documentation/archive/observability-nov-2025/summaries/
mv SESSION-COMPLETE-AGENTS-REFACTOR.md documentation/archive/observability-nov-2025/summaries/
mv SESSION-COMPLETE-TIER2-LIBRARIES.md documentation/archive/observability-nov-2025/summaries/
mv SESSION-END-SUMMARY.md documentation/archive/observability-nov-2025/summaries/
mv TIER2-LIBRARIES-COMPLETE.md documentation/archive/observability-nov-2025/implementation/
````

**Result**: Root has 8 files ✅ (compliant with our standards)

---

### Task 5: Update Documentation (1 hour)

**Goal**: Document Tier 2 libraries + findings

**1. Update `documentation/technical/LIBRARIES.md`**:

- Change Tier 2 status from "stub" to "implemented"
- Add note: "Tests pending, usage validation in progress"
- List actual features implemented

**2. Create `documentation/planning/LIBRARY-SIMPLIFICATION-PLAN.md`**:

- Document which features are used vs unused
- Plan for simplification (remove unused features)
- Track TODOs added during application

**3. Update `documentation/archive/observability-nov-2025/INDEX.md`**:

- Add new completion docs
- Update file counts

---

## Success Criteria

**After This Session**:

- [ ] 3 critical libraries have comprehensive tests ✅
- [ ] Tests passing, bugs fixed ✅
- [ ] Libraries applied to at least 5-10 code files ✅
- [ ] Unused features marked with TODO ✅
- [ ] Principles document enhanced ✅
- [ ] Root directory has 8 files ✅
- [ ] Documentation updated ✅

---

## Execution Order

**Hour 1**: Test serialization + data_transform (critical for agents)  
**Hour 2**: Test database (critical for stages)  
**Hour 3**: Apply libraries to GraphRAG stages (4 files)  
**Hour 4**: Apply libraries to Services (5 files), mark unused features  
**Hour 5**: Document principles + cleanup root + update docs

**Total**: 5 hours to validate, apply, and document properly

---

## Key Principles to Follow

**During Implementation**:

1. ✅ Test BEFORE marking complete
2. ✅ Apply BEFORE adding features
3. ✅ Simple FIRST, enhance later
4. ✅ Mark unused features with TODO
5. ✅ Archive completion docs immediately

**When in Doubt**:

- "Is this feature needed NOW?" → If no, add TODO
- "Can I test this easily?" → If no, simplify
- "Is this used anywhere?" → If no, defer

---

## Reference Files

**Review Findings**:

- `DEEP-REVIEW-CRITICAL-FINDINGS.md`
- `TEST-COVERAGE-CRITICAL-GAP.md`

**Implementation Plans**:

- `documentation/planning/CODE-REVIEW-IMPLEMENTATION-PLAN.md`
- `documentation/DOCUMENTATION-PRINCIPLES-AND-PROCESS.md`

**Pattern Examples**:

- Our Tier 1 libraries (tests/core/libraries/error_handling/, etc.)
- Refactored agents (business/agents/graphrag/extraction.py)

---

**Use this prompt to continue with proper testing, validation, and principle adherence!** 🚀
