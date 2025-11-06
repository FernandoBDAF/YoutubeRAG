# SUBPLAN: Extraction Stage Validation and Debugging

**Mother Plan**: PLAN_EXTRACTION-QUALITY-ENHANCEMENT.md  
**Achievement Addressed**: Achievement 0.1 (Extraction Stage Runs and Validated)  
**Status**: In Progress  
**Created**: 2025-11-05 22:45 UTC  
**Estimated Effort**: 2-4 hours

---

## 🎯 Objective

Validate that the graph_extraction stage runs successfully by:

1. Analyzing logs from extraction run
2. Identifying root causes of validation errors
3. Fixing issues iteratively
4. Ensuring extraction completes without critical errors

---

## 📋 What Needs to Be Done

### Issue Identified from Logs

**Primary Problem**: ValidationError - "At least one entity must be identified"

- Multiple chunks failing with empty entity lists
- LLM returning `entities: []` which violates KnowledgeModel constraint
- Retry logic attempting 3 times per chunk, all failing
- Pattern: ~10+ chunks failing in first batch

**Secondary Observations**:

- Ontology loads successfully (34 predicates, 122 mappings, 18 type constraints)
- Warning: `type_map` section not loaded (may affect filtering)
- Pipeline started correctly with 9477 documents, 300 workers
- Some chunks succeeding (HTTP 200 OK responses without errors)

### Analysis Steps

1. **Examine KnowledgeModel validation**:

   - Check if constraint is too strict
   - Determine if empty entities should be allowed for some chunks
   - Review validation logic in `core/models/graphrag.py`

2. **Investigate chunk content**:

   - Sample chunks that failed
   - Check if chunks have valid text content
   - Determine if chunks are too short/empty/noise

3. **Review extraction prompt**:

   - Check if prompt allows empty entities
   - Verify if prompt needs adjustment for edge cases
   - Review LLM response handling

4. **Fix strategy** (based on findings):
   - Option A: Relax validation (allow empty entities if chunk is truly empty)
   - Option B: Improve prompt to handle edge cases
   - Option C: Filter chunks before extraction (skip empty/low-quality)
   - Option D: Handle empty responses gracefully

---

## 📝 Approach

1. **Create EXECUTION_TASK** to log analysis and fixes
2. **Examine KnowledgeModel** - understand validation constraint
3. **Sample failed chunks** - query database for chunks that failed
4. **Analyze root cause** - why LLM returns empty entities
5. **Implement fix** - based on root cause
6. **Test with small batch** - validate fix works
7. **Re-run extraction** - verify complete run succeeds

---

## ✅ Expected Results

- Extraction runs without validation errors
- All chunks processed successfully (or gracefully skipped)
- Logs show successful processing
- No critical errors in extraction output
- Documentation of fix and rationale

---

## 🔗 Dependencies

- Access to `mongo_hack` database
- Ability to query failed chunks
- KnowledgeModel source code
- Extraction agent code

---

## 📚 References

- **Mother Plan**: PLAN_EXTRACTION-QUALITY-ENHANCEMENT.md
- **Code**: `core/models/graphrag.py` (KnowledgeModel)
- **Code**: `business/agents/graphrag/extraction.py` (extraction logic)
- **Logs**: `logs/pipeline/graphrag_graph_extraction_20251105_143246.log`

---

**Ready to Execute**: Yes
