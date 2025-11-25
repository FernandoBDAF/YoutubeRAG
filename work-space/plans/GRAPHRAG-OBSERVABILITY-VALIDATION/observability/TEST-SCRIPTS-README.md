# GraphRAG Observability Validation - Test Scripts

**Location**: `work-space/plans/GRAPHRAG-OBSERVABILITY-VALIDATION/observability/`

Three automated test scripts are available to validate Achievement 3.1 and 3.2:

---

## 1. Master Test Runner (Recommended)

**File**: `run-all-tests.sh`  
**Purpose**: Run all validation tests (3.1 & 3.2) in sequence  
**Estimated Time**: 20-30 minutes

### Usage

```bash
cd /Users/fernandobarroso/Local\ Repo/YoutubeRAG-mongohack/YoutubeRAG

bash work-space/plans/GRAPHRAG-OBSERVABILITY-VALIDATION/observability/run-all-tests.sh
```

### Output

Runs both test suites and provides:

- ✅ Pass/fail status for each suite
- 📊 Overall summary statistics
- 📁 All detailed outputs saved to separate folders

### Best For

- **Full validation** of all observability tools
- **Comprehensive testing** with complete reporting
- **CI/CD pipelines** that need automated validation

---

## 2. Query Scripts Test (Achievement 3.1)

**File**: `test-all-query-scripts.sh`  
**Purpose**: Validate all 11 query scripts  
**Estimated Time**: 10-15 minutes

### Usage

```bash
cd /Users/fernandobarroso/Local\ Repo/YoutubeRAG-mongohack/YoutubeRAG

bash work-space/plans/GRAPHRAG-OBSERVABILITY-VALIDATION/observability/test-all-query-scripts.sh
```

### Scripts Tested

✅ **Working Scripts** (9/11):

1. `query_raw_entities.py`
2. `compare_extraction_runs.py`
3. `query_resolution_decisions.py`
4. `compare_before_after_resolution.py` (bug fix included)
5. `find_resolution_errors.py`
6. `query_raw_relationships.py`
7. `compare_before_after_construction.py`
8. `query_graph_evolution.py`
9. `query_pre_detection_graph.py`

⏭️ **Skipped** (2/11 - require 2 trace IDs):

- `compare_extraction_runs.py` (if 2+ trace IDs available)
- `compare_detection_algorithms.py` (if 2+ trace IDs available)

### Output

Saved to: `query-outputs/`

- Individual output files for each script
- Summary statistics
- Pass/fail results

### Documentation

- `documentation/Query-Scripts-Validation-Report.md`
- `documentation/Query-Scripts-Example-Outputs.md`
- `documentation/Query-Scripts-No-Data-Analysis.md`
- `documentation/Query-Scripts-Bug-Log.md`
- `documentation/Query-Scripts-Documentation-Updates.md`

---

## 3. Explanation Tools Test (Achievement 3.2)

**File**: `test-all-explanation-tools.sh`  
**Purpose**: Validate all 5 explanation tools  
**Estimated Time**: 5-10 minutes

### Usage

```bash
cd /Users/fernandobarroso/Local\ Repo/YoutubeRAG-mongohack/YoutubeRAG

bash work-space/plans/GRAPHRAG-OBSERVABILITY-VALIDATION/observability/test-all-explanation-tools.sh
```

### Tools Tested

✅ **All 5 Tools Pass** (100% success rate):

1. `explain_entity_merge.py` - Explain entity merges
2. `explain_relationship_filter.py` - Explain relationship filtering
3. `trace_entity_journey.py` - Trace entity through pipeline
4. `explain_community_formation.py` - Explain communities
5. `visualize_graph_evolution.py` - Visualize graph evolution

### Output

Saved to: `explanation-outputs/`

- Individual output files for each tool
- Sample outputs displayed in console
- Pass/fail results

### Documentation

- `documentation/Explanation-Tools-Validation-Report.md`
- `documentation/Explanation-Tools-Summary.md`

---

## Test Data

All tests use real pipeline data from Achievement 2.2:

- **Trace ID**: `6088e6bd-e305-42d8-9210-e2d3f1dda035`
- **Database**: `validation_01`
- **Entities**: 373 raw, 373 resolved
- **Relationships**: 68 raw, 0 final
- **Communities**: 0 (collection empty)

---

## Environment Configuration

All scripts automatically configure:

```bash
export MONGODB_URI="mongodb+srv://fernandobarrosomz_db_user:vkJV4cC8mx81wJyQ@cluster0.djtttp9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
export DB_NAME="validation_01"
```

No manual setup required.

---

## Expected Results

### Achievement 3.1 (Query Scripts)

- ✅ 9/11 scripts tested successfully
- ✅ 1 bug found and fixed (TypeError)
- ✅ All output formats validated
- ✅ Error handling tested
- 📝 Documentation created

### Achievement 3.2 (Explanation Tools)

- ✅ 5/5 tools tested successfully
- ✅ 0 bugs found
- ✅ All output formats valid
- ✅ Error handling works correctly
- 📝 Documentation created

---

## Troubleshooting

### "mongosh: command not found"

Install MongoDB Shell:

```bash
brew install mongosh  # macOS
```

### "Permission denied"

Make scripts executable:

```bash
chmod +x work-space/plans/GRAPHRAG-OBSERVABILITY-VALIDATION/observability/*.sh
```

### "MONGODB_URI not found"

Verify environment variables are set:

```bash
echo $MONGODB_URI
echo $DB_NAME
```

If not set, scripts will configure them automatically.

### "Could not retrieve entity IDs"

1. Verify MongoDB connectivity
2. Check database `validation_01` has data
3. Ensure network access to MongoDB cluster

### Output Directory Already Exists

Scripts will append to existing output files. To clean:

```bash
rm -rf work-space/plans/GRAPHRAG-OBSERVABILITY-VALIDATION/observability/{query-outputs,explanation-outputs}
```

---

## Individual Tool Testing

To test individual tools manually:

### Query Scripts

```bash
export MONGODB_URI="mongodb+srv://fernandobarrosomz_db_user:vkJV4cC8mx81wJyQ@cluster0.djtttp9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
export DB_NAME="validation_01"

python scripts/repositories/graphrag/queries/query_raw_entities.py \
  --trace-id 6088e6bd-e305-42d8-9210-e2d3f1dda035 --limit 10
```

### Explanation Tools

```bash
export MONGODB_URI="mongodb+srv://fernandobarrosomz_db_user:vkJV4cC8mx81wJyQ@cluster0.djtttp9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
export DB_NAME="validation_01"

# Get entity ID first
ENTITY_ID=$(mongosh "mongodb+srv://fernandobarrosomz_db_user:vkJV4cC8mx81wJyQ@cluster0.djtttp9.mongodb.net/validation_01" --quiet --eval "db.entities_resolved.findOne({trace_id: '6088e6bd-e305-42d8-9210-e2d3f1dda035'}).entity_id")

# Test tool
python scripts/repositories/graphrag/explain/trace_entity_journey.py \
  --entity-id $ENTITY_ID --trace-id 6088e6bd-e305-42d8-9210-e2d3f1dda035
```

---

## Integration with CI/CD

For automated testing:

```bash
#!/bin/bash
set -e

cd /path/to/YoutubeRAG

# Run all tests
bash work-space/plans/GRAPHRAG-OBSERVABILITY-VALIDATION/observability/run-all-tests.sh

# Check exit code
if [ $? -eq 0 ]; then
    echo "✅ All observability tools validated"
    exit 0
else
    echo "❌ Validation failed"
    exit 1
fi
```

---

## Documentation Files

All test results and findings documented in:

**Achievement 3.1 Documentation**:

- `Query-Scripts-Validation-Report.md` - Comprehensive test results
- `Query-Scripts-Example-Outputs.md` - Real output examples
- `Query-Scripts-Bug-Log.md` - Bug analysis and fixes
- `Query-Scripts-Documentation-Updates.md` - Documentation improvements
- `Query-Scripts-No-Data-Analysis.md` - Root cause analysis

**Achievement 3.2 Documentation**:

- `Explanation-Tools-Validation-Report.md` - Comprehensive test results
- `Explanation-Tools-Summary.md` - Quick summary

All in: `documentation/`

---

## Quick Reference

| Task                        | Command                              |
| --------------------------- | ------------------------------------ |
| Run all tests               | `bash run-all-tests.sh`              |
| Test query scripts only     | `bash test-all-query-scripts.sh`     |
| Test explanation tools only | `bash test-all-explanation-tools.sh` |
| See quick start             | `cat RUN-EXPLANATION-TOOLS-TESTS.md` |

---

**Created**: 2025-11-13  
**For**: Achievement 3.1 & 3.2 Validation  
**Status**: ✅ Ready for Use
