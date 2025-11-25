# How to Run Explanation Tools Tests

**Achievement**: 3.2 - Explanation Tools Validated  
**Test Script**: `test-all-explanation-tools.sh`  
**Location**: `work-space/plans/GRAPHRAG-OBSERVABILITY-VALIDATION/observability/`

---

## Quick Start

Run all explanation tools tests with a single command:

```bash
cd /Users/fernandobarroso/Local\ Repo/YoutubeRAG-mongohack/YoutubeRAG

bash work-space/plans/GRAPHRAG-OBSERVABILITY-VALIDATION/observability/test-all-explanation-tools.sh
```

---

## What the Script Does

### Phase 1: Tool Discovery & Preparation
- Locates all 5 explanation tools
- Retrieves sample entity IDs from MongoDB
- Prepares test environment

### Phase 2: Entity Merge & Relationship Explainers
- Tests `explain_entity_merge.py`
- Tests `explain_relationship_filter.py`

### Phase 3: Community & Entity Journey Tools
- Tests `explain_community_formation.py`
- Tests `trace_entity_journey.py`

### Phase 4: Graph Evolution Visualizer
- Tests `visualize_graph_evolution.py`

### Phase 5: Test Summary
- Reports pass/fail statistics
- Displays sample outputs
- Saves all outputs to `explanation-outputs/` folder

---

## Output

### Console Output
- Colored test results (green for pass, red for fail)
- Test count and summary
- Sample outputs from each tool

### Output Files
All outputs saved to:
```
work-space/plans/GRAPHRAG-OBSERVABILITY-VALIDATION/observability/explanation-outputs/
```

Files created:
- `explain_entity_merge_output.txt`
- `explain_relationship_filter_output.txt`
- `explain_community_formation_output.txt`
- `trace_entity_journey_output.txt`
- `visualize_graph_evolution_output.txt`

---

## Environment Variables

The script automatically sets:
- `MONGODB_URI` - Connection to MongoDB cluster
- `DB_NAME` - Uses `validation_01` database

No manual configuration needed.

---

## Trace ID

Tests use the real trace ID from Achievement 2.2:
```
6088e6bd-e305-42d8-9210-e2d3f1dda035
```

This ensures validation with actual pipeline data.

---

## Expected Results

✅ **All 5 tools should pass**:
- explain_entity_merge.py ✅
- explain_relationship_filter.py ✅
- trace_entity_journey.py ✅
- explain_community_formation.py ✅ (may show "Community not found" error - expected)
- visualize_graph_evolution.py ✅

---

## Troubleshooting

### "MONGODB_URI not found"
The script sets this automatically. If it fails, ensure:
```bash
export MONGODB_URI="mongodb+srv://fernandobarrosomz_db_user:vkJV4cC8mx81wJyQ@cluster0.djtttp9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
export DB_NAME="validation_01"
```

### "Could not retrieve entity IDs"
Ensure:
1. MongoDB is accessible
2. `validation_01` database has data with the trace ID
3. You have network connectivity to the cluster

### Script Permission Denied
Make script executable:
```bash
chmod +x work-space/plans/GRAPHRAG-OBSERVABILITY-VALIDATION/observability/test-all-explanation-tools.sh
```

---

## Individual Tool Tests

If you want to run individual tools manually:

```bash
# Set environment
export MONGODB_URI="mongodb+srv://fernandobarrosomz_db_user:vkJV4cC8mx81wJyQ@cluster0.djtttp9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
export DB_NAME="validation_01"

# Get entity ID
ENTITY_ID=$(mongosh "mongodb+srv://fernandobarrosomz_db_user:vkJV4cC8mx81wJyQ@cluster0.djtttp9.mongodb.net/validation_01" --quiet --eval "db.entities_resolved.findOne({trace_id: '6088e6bd-e305-42d8-9210-e2d3f1dda035'}).entity_id")

# Test individual tools
python scripts/repositories/graphrag/explain/explain_entity_merge.py --entity-id-a $ENTITY_ID --entity-id-b $ENTITY_ID --trace-id 6088e6bd-e305-42d8-9210-e2d3f1dda035

python scripts/repositories/graphrag/explain/trace_entity_journey.py --entity-id $ENTITY_ID --trace-id 6088e6bd-e305-42d8-9210-e2d3f1dda035

python scripts/repositories/graphrag/explain/visualize_graph_evolution.py --trace-id 6088e6bd-e305-42d8-9210-e2d3f1dda035
```

---

## Documentation

For detailed results and findings, see:
- `documentation/Explanation-Tools-Validation-Report.md` - Comprehensive test results
- `documentation/Explanation-Tools-Summary.md` - Quick summary

---

**Created**: 2025-11-13  
**For**: Achievement 3.2 - Explanation Tools Validated

