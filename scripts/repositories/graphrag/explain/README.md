# GraphRAG Explanation Tools

**Achievement 1.1**: Transformation Explanation Tools  
**Version**: 1.0  
**Last Updated**: 2025-11-10

Interactive CLI tools for explaining GraphRAG pipeline transformations. These tools answer "why" questions about entity merges, relationship filtering, community formation, entity journeys, and graph evolution.

---

## Table of Contents

1. [Overview](#overview)
2. [Tools](#tools)
3. [Installation](#installation)
4. [Usage Examples](#usage-examples)
5. [Common Use Cases](#common-use-cases)
6. [Troubleshooting](#troubleshooting)

---

## Overview

The GraphRAG explanation tools provide interactive ways to understand pipeline decisions by querying transformation logs and intermediate data. Each tool focuses on a specific "why" question:

- **Why were these entities merged?** → `explain_entity_merge.py`
- **Why was this relationship kept/dropped?** → `explain_relationship_filter.py`
- **Why were these entities clustered?** → `explain_community_formation.py`
- **What happened to this entity?** → `trace_entity_journey.py`
- **How did the graph evolve?** → `visualize_graph_evolution.py`

**Key Features**:
- Interactive CLI interface
- JSON output for programmatic use
- Trace ID filtering for specific pipeline runs
- Built on transformation logs and intermediate data

---

## Tools

### 1. Entity Merge Explainer

**File**: `explain_entity_merge.py`

**Purpose**: Explains why two entities were merged (or not merged) during entity resolution.

**What it shows**:
- Merge decision (merged/not merged)
- Similarity score
- Merge method (fuzzy match, exact match, semantic)
- Confidence score
- Original entity details (names, types, chunks)
- Merge reasoning from transformation logs

**Usage**:
```bash
python explain_entity_merge.py --entity-a "Barack Obama" --entity-b "President Obama"
python explain_entity_merge.py --entity-id-a abc123 --entity-id-b def456 --trace-id xyz
python explain_entity_merge.py --entity-a "Apple" --entity-b "Apple Inc" --format json
```

---

### 2. Relationship Filter Explainer

**File**: `explain_relationship_filter.py`

**Purpose**: Explains why a relationship between two entities was kept or dropped during graph construction.

**What it shows**:
- All extraction attempts for the entity pair
- Filtering decisions (kept/dropped, why)
- Confidence scores and thresholds
- Predicate information
- Final relationship (if kept)

**Usage**:
```bash
python explain_relationship_filter.py --source "Apple" --target "iPhone"
python explain_relationship_filter.py --source-id abc123 --target-id def456 --trace-id xyz
python explain_relationship_filter.py --source "Google" --target "Android" --format json
```

---

### 3. Community Formation Explainer

**File**: `explain_community_formation.py`

**Purpose**: Explains why entities were clustered into a specific community during community detection.

**What it shows**:
- Community members (entities)
- Relationships within community
- Coherence score and factors
- Algorithm used and parameters
- Modularity contribution

**Usage**:
```bash
python explain_community_formation.py --community-id comm_123
python explain_community_formation.py --community-id comm_456 --trace-id xyz
python explain_community_formation.py --community-id comm_789 --format json
```

---

### 4. Entity Journey Tracer

**File**: `trace_entity_journey.py`

**Purpose**: Traces the complete transformation journey of an entity through all pipeline stages.

**What it shows**:
- **Stage 1: Extraction** - Which chunks, confidence, type
- **Stage 2: Resolution** - Merge decisions, method, final ID
- **Stage 3: Graph Construction** - Relationships, types, sources
- **Stage 4: Community Detection** - Community assignment, role

**Usage**:
```bash
python trace_entity_journey.py --entity "Barack Obama"
python trace_entity_journey.py --entity-id abc123 --trace-id xyz
python trace_entity_journey.py --entity "Apple Inc" --format json
```

---

### 5. Graph Evolution Visualizer

**File**: `visualize_graph_evolution.py`

**Purpose**: Visualizes how the graph structure evolves through the construction stage.

**What it shows**:
- Step-by-step addition of relationships
- Graph density at each step
- Average degree at each step
- Breakdown by relationship source (LLM, co-occurrence, semantic, cross-chunk)

**Usage**:
```bash
python visualize_graph_evolution.py --trace-id xyz
python visualize_graph_evolution.py --trace-id xyz --format json
python visualize_graph_evolution.py --trace-id xyz --output graph_evolution.json
```

---

## Installation

### Prerequisites

- Python 3.8+
- MongoDB with GraphRAG data
- Environment variables configured (MONGODB_URI, DB_NAME)

### Setup

1. Ensure you're in the project root:
```bash
cd /path/to/YoutubeRAG
```

2. Set environment variables (if not already set):
```bash
export MONGODB_URI="mongodb://localhost:27017"
export DB_NAME="mongo_hack"
```

3. Verify installation:
```bash
python scripts/repositories/graphrag/explain/explain_entity_merge.py --help
```

---

## 📊 Real-World Examples from Validation Run

**Trace ID**: `6088e6bd-e305-42d8-9210-e2d3f1dda035`

### Example: Entity Merge Explanation from Validation

```
═══════════════════════════════════════════════════════════
   ENTITY MERGE EXPLANATION
═══════════════════════════════════════════════════════════

Trace ID: 6088e6bd-e305-42d8-9210-e2d3f1dda035

Entity 1:
  Raw ID: raw_entity_0
  Name: GraphRAG
  Type: TECHNOLOGY
  Confidence: 0.95

Entity 2:
  Raw ID: raw_entity_5  
  Name: Graph RAG
  Type: TECHNOLOGY
  Confidence: 0.92

Merge Decision: ✅ MERGED
  Method: Fuzzy Matching
  Similarity: 0.89
  Final Confidence: 0.96

Canonical Result: resolved_entity_0 (GraphRAG System)
```

---

## Usage Examples

### Example 1: Investigate Entity Merge

**Scenario**: Two entities seem similar but weren't merged. Why?

**Using real trace_id from validation**:

```bash
python scripts/repositories/graphrag/explain/explain_entity_merge.py \
  --entity-a "GraphRAG" \
  --entity-b "Graph RAG" \
  --trace-id 6088e6bd-e305-42d8-9210-e2d3f1dda035

# Output shows:
# - Merge Decision: ✅ MERGED
# - Similarity Score: 0.89
# - Method: fuzzy_match
# - Reason: High name similarity, same type
```

### Example 2: Debug Relationship Filtering

**Scenario**: Expected relationship between entities but it's missing. Why?

```bash
# Check relationship status
python scripts/repositories/graphrag/explain/explain_relationship_filter.py \
  --source "Apple" \
  --target "iPhone" \
  --trace-id abc-123

# Output shows:
# - Final Status: ❌ DROPPED
# - Reason: Low confidence (0.45 < threshold 0.7)
# - Extraction Attempts: 3
```

### Example 3: Understand Community Structure

**Scenario**: Why are these specific entities in the same community?

```bash
# Explain community formation
python scripts/repositories/graphrag/explain/explain_community_formation.py \
  --community-id comm_5 \
  --trace-id abc-123

# Output shows:
# - Size: 25 entities
# - Coherence Score: 0.78
# - Relationships Within: 45
# - Algorithm: leiden (resolution=1.0)
```

### Example 4: Track Entity Through Pipeline

**Scenario**: What happened to a specific entity at each stage?

```bash
# Trace entity journey
python scripts/repositories/graphrag/explain/trace_entity_journey.py \
  --entity "Barack Obama" \
  --trace-id abc-123

# Output shows complete lifecycle:
# Stage 1: Extracted from 5 chunks
# Stage 2: Merged 2 mentions → 1 entity
# Stage 3: Connected to 12 entities
# Stage 4: Assigned to community comm_5 (hub role)
```

### Example 5: Analyze Graph Evolution

**Scenario**: How did the graph grow during construction?

```bash
# Visualize evolution
python scripts/repositories/graphrag/explain/visualize_graph_evolution.py \
  --trace-id abc-123

# Output shows step-by-step:
# Step 1: LLM Relationships (200 edges, density=0.05)
# Step 2: + Co-occurrence (350 edges, density=0.09)
# Step 3: + Semantic Similarity (420 edges, density=0.11)
# Step 4: + Cross-chunk (450 edges, density=0.12)
```

---

## Common Use Cases

### Use Case 1: Quality Investigation

**Problem**: Merge rate is too high (over-merging)

**Workflow**:
1. Run quality metrics to identify high merge rate
2. Use `explain_entity_merge.py` to examine specific merges
3. Look for low similarity scores with high confidence
4. Adjust similarity threshold in entity resolution

### Use Case 2: Missing Relationships

**Problem**: Expected relationships not appearing in graph

**Workflow**:
1. Use `explain_relationship_filter.py` to check entity pair
2. Check if relationship was extracted but filtered
3. Review filtering reason (low confidence, density safeguard)
4. Adjust extraction prompts or filtering thresholds

### Use Case 3: Community Quality

**Problem**: Communities seem incoherent or too fragmented

**Workflow**:
1. Use `explain_community_formation.py` to examine communities
2. Check coherence scores and relationship density
3. Review algorithm parameters (resolution, min_cluster_size)
4. Adjust community detection parameters

### Use Case 4: Entity Debugging

**Problem**: Entity not behaving as expected

**Workflow**:
1. Use `trace_entity_journey.py` to see complete lifecycle
2. Check extraction confidence and chunk coverage
3. Review merge decisions in resolution
4. Verify relationships in graph construction
5. Confirm community assignment

### Use Case 5: Pipeline Optimization

**Problem**: Want to understand pipeline behavior for optimization

**Workflow**:
1. Use `visualize_graph_evolution.py` to see graph growth
2. Identify which methods contribute most relationships
3. Analyze density evolution
4. Optimize post-processing methods based on contribution

---

## Troubleshooting

### Issue 1: "Entity not found"

**Problem**: Tool can't find the entity you're looking for

**Solutions**:
- Check entity name spelling (case-insensitive search)
- Try using entity ID instead of name
- Verify trace_id is correct
- Check if entity exists in `entities_resolved` collection

### Issue 2: "Trace ID not found"

**Problem**: Specified trace_id doesn't exist

**Solutions**:
- Verify trace_id from recent pipeline run
- Check `transformation_logs` collection for valid trace IDs
- Run pipeline with transformation logging enabled
- Omit trace_id to search across all runs

### Issue 3: "No merge logs found"

**Problem**: Can't find merge information for entities

**Solutions**:
- Entities may not have been merged
- Check if entities are from same trace_id
- Verify transformation logging was enabled during pipeline run
- Check `transformation_logs` collection for entity_merge operations

### Issue 4: "MONGODB_URI not found"

**Problem**: Environment variable not set

**Solutions**:
```bash
# Set environment variable
export MONGODB_URI="mongodb://localhost:27017"
export DB_NAME="mongo_hack"

# Or create .env file in project root
echo "MONGODB_URI=mongodb://localhost:27017" > .env
echo "DB_NAME=mongo_hack" >> .env
```

### Issue 5: "Import error"

**Problem**: Can't import explain_utils

**Solutions**:
- Ensure you're running from project root or scripts are in PYTHONPATH
- Check that `__init__.py` exists in explain/ folder
- Verify Python path includes project root

---

## Output Formats

### Text Format (default)

Human-readable output with sections, headers, and formatting:
```
═══════════════════════════════════════════════════════════
   ENTITY MERGE EXPLANATION
═══════════════════════════════════════════════════════════

Trace ID: abc-123-def
Merge Decision: ✅ MERGED

Entity A:
  Name: Barack Obama
  Type: person
  Confidence: 0.920
  ...
```

### JSON Format (--format json)

Machine-readable JSON for programmatic use:
```json
{
  "trace_id": "abc-123-def",
  "merge_decision": "merged",
  "entity_a": {
    "entity_id": "ent_123",
    "name": "Barack Obama",
    "type": "person",
    "confidence": 0.92
  },
  ...
}
```

---

## Integration with Other Tools

### With Query Scripts

Explanation tools complement query scripts from Achievement 0.3:

```bash
# First, query to find entities
python scripts/repositories/graphrag/queries/query_raw_entities.py --trace-id xyz

# Then, explain specific entity
python scripts/repositories/graphrag/explain/trace_entity_journey.py --entity-id abc123 --trace-id xyz
```

### With Quality Metrics

Use quality metrics to identify issues, then explain with these tools:

```bash
# Check quality metrics
curl "http://localhost:8000/api/quality/run?trace_id=xyz"

# If merge_rate is high, investigate merges
python scripts/repositories/graphrag/explain/explain_entity_merge.py --entity-a "..." --entity-b "..." --trace-id xyz
```

---

## Best Practices

1. **Always use trace_id**: Filter by trace_id for specific pipeline runs to avoid confusion

2. **Start with entity journey**: Use `trace_entity_journey.py` first to get overview, then dive into specific stages

3. **Use JSON for automation**: Use `--format json` when integrating with other tools or scripts

4. **Save evolution data**: Use `--output` with `visualize_graph_evolution.py` to save data for later analysis

5. **Combine tools**: Use multiple tools together to build complete understanding of pipeline behavior

---

## 🎨 Using Color Formatting (Achievement 7.1)

The explanation tools can now leverage enhanced color formatting from `query_utils` for improved readability.

### Available Utilities

All tools can import and use these utilities:

```python
from query_utils import Colors, format_color_value
```

### Color Formatting in Explanation Tools

**Example: Highlight merge decisions**:
```python
# In explain_entity_merge.py
if merge_decision == "merged":
    status = format_color_value("✅ MERGED", "success")
else:
    status = format_color_value("❌ NOT MERGED", "error")

print(f"Merge Decision: {status}")
```

**Example: Color-code confidence scores**:
```python
# High confidence → green, low confidence → yellow/red
confidence_type = "success" if confidence > 0.8 else ("warning" if confidence > 0.6 else "error")
print(f"Confidence: {format_color_value(f'{confidence:.2f}', confidence_type)}")
```

**Example: Highlight similarity scores**:
```python
# Show similarity with appropriate color
similarity_type = "success" if similarity > 0.7 else "warning"
print(f"Similarity: {format_color_value(f'{similarity:.2f}', similarity_type)}")
```

### Color Types Reference

| Type | Color | Use Case in Explanation Tools |
|------|-------|-------------------------------|
| `success` | Green | Successful merges, high confidence, good metrics |
| `warning` | Yellow | Borderline confidence, medium similarity, caution |
| `error` | Red | Failed merges, low confidence, errors |
| `info` | Blue | Neutral information, IDs, timestamps |
| `text` | None | Default text |

### Complete Example: Enhanced Entity Merge Explanation

```python
#!/usr/bin/env python3
from query_utils import Colors, format_color_value

def explain_merge(entity_a, entity_b, merge_data):
    """Explain entity merge with color formatting."""
    
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}   ENTITY MERGE EXPLANATION{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")
    
    # Entity details
    print(f"Entity A:")
    print(f"  Name: {format_color_value(entity_a['name'], 'info')}")
    print(f"  Type: {entity_a['type']}")
    conf_type = "success" if entity_a['confidence'] > 0.8 else "warning"
    print(f"  Confidence: {format_color_value(f\"{entity_a['confidence']:.2f}\", conf_type)}")
    
    print(f"\nEntity B:")
    print(f"  Name: {format_color_value(entity_b['name'], 'info')}")
    print(f"  Type: {entity_b['type']}")
    conf_type = "success" if entity_b['confidence'] > 0.8 else "warning"
    print(f"  Confidence: {format_color_value(f\"{entity_b['confidence']:.2f}\", conf_type)}")
    
    # Merge decision
    print(f"\n{Colors.BOLD}Merge Decision:{Colors.RESET}")
    if merge_data['merged']:
        status = format_color_value("✅ MERGED", "success")
        print(f"  Status: {status}")
        print(f"  Method: {format_color_value(merge_data['method'], 'info')}")
        
        sim_type = "success" if merge_data['similarity'] > 0.7 else "warning"
        print(f"  Similarity: {format_color_value(f\"{merge_data['similarity']:.2f}\", sim_type)}")
    else:
        status = format_color_value("❌ NOT MERGED", "error")
        print(f"  Status: {status}")
        print(f"  Reason: {format_color_value(merge_data['reason'], 'warning')}")
```

### Benefits of Color Formatting

✅ **Improved Readability**: Visual cues help identify important information quickly  
✅ **Better UX**: Users can scan outputs faster with color-coded values  
✅ **Emphasis**: Highlights warnings, errors, and successes appropriately  
✅ **Professional Output**: Modern CLI tools use colors for better user experience  
✅ **Piping Safe**: Colors automatically disabled when output is piped to files

### Migration to Color Formatting

To add colors to existing explanation tools:

1. **Import utilities**:
```python
from query_utils import Colors, format_color_value
```

2. **Replace plain text with colored text**:
```python
# Before
print(f"Confidence: {confidence:.2f}")

# After
conf_type = "success" if confidence > 0.8 else "warning"
print(f"Confidence: {format_color_value(f'{confidence:.2f}', conf_type)}")
```

3. **Add section headers with bold**:
```python
print(f"{Colors.BOLD}{'='*60}{Colors.RESET}")
print(f"{Colors.BOLD}   SECTION TITLE{Colors.RESET}")
print(f"{Colors.BOLD}{'='*60}{Colors.RESET}")
```

### See Also

- **Tool Enhancement Report**: `documentation/Tool-Enhancement-Report.md`
- **Query Utils Documentation**: `scripts/repositories/graphrag/queries/README.md#new-utility-functions`

---

## Conclusion

The GraphRAG explanation tools provide comprehensive visibility into pipeline decisions, enabling:
- Understanding of "why" questions
- Debugging of quality issues
- Optimization of pipeline parameters
- Validation of pipeline behavior

For more information:
- Transformation Logging: `documentation/guides/GRAPHRAG-TRANSFORMATION-LOGGING.md`
- Intermediate Data: `documentation/guides/INTERMEDIATE-DATA-ANALYSIS.md`
- Quality Metrics: `documentation/guides/QUALITY-METRICS.md`


