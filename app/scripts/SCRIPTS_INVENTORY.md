# GraphRAG Scripts Inventory & Analysis

**Location**: `app/scripts/`  
**Date**: December 9, 2025  
**Purpose**: Categorize and document all utility scripts, identifying API overlaps and unique functionality

---

## Executive Summary

The `app/scripts/` folder contains **11 utility scripts** organized into two categories:
1. **GraphRAG Testing & Analysis** (8 scripts in `graphrag/`)
2. **Database Utilities** (3 scripts in `utilities/`)

**Key Findings**:
- ✅ **No API duplication concerns** - Scripts provide unique functionality or enhanced CLI workflows
- ✅ **All scripts are valuable** for development, testing, and debugging
- ⚠️ **Some overlap with Statistics API** - But scripts provide more detailed analysis and continuous monitoring
- 📌 **None are required for UI implementation** - GraphDash should use Graph API endpoints exclusively

---

## Table of Contents

1. [Scripts Categorization](#scripts-categorization)
2. [GraphRAG Testing & Analysis Scripts](#graphrag-testing--analysis-scripts)
3. [Database Utility Scripts](#database-utility-scripts)
4. [API Overlap Analysis](#api-overlap-analysis)
5. [Recommendations](#recommendations)

---

## Scripts Categorization

### By Purpose

| Script | Category | API Overlap | Status | UI Relevant |
|--------|----------|-------------|--------|-------------|
| `test_random_chunks.py` | Testing | None | ✅ Keep | No |
| `run_random_chunk_test.py` | Testing | None | ✅ Keep | No |
| `analyze_graph_structure.py` | Analysis | Partial | ✅ Keep | No |
| `monitor_density.py` | Monitoring | Partial | ✅ Keep | No |
| `test_community_detection.py` | Testing | None | ✅ Keep | No |
| `inspect_community_detection.py` | Debugging | None | ✅ Keep | No |
| `diagnose_communities.py` | Debugging | None | ✅ Keep | No |
| `sample_graph_data.py` | Inspection | Partial | ✅ Keep | No |
| `check_data.py` | Inspection | None | ✅ Keep | No |
| `full_cleanup.py` | Maintenance | None | ✅ Keep | No |
| `seed_indexes.py` | Initialization | None | ✅ Keep | No |

### By Functionality

```
scripts/
├── graphrag/                    # GraphRAG-specific scripts
│   ├── Testing (4)              # Pipeline testing utilities
│   ├── Analysis (2)             # Graph structure analysis
│   └── Debugging (2)            # Community detection debugging
└── utilities/                   # General database utilities
    ├── Inspection (1)           # Data inspection
    ├── Maintenance (1)          # Database cleanup
    └── seed/
        └── Initialization (1)   # Index creation
```

---

## GraphRAG Testing & Analysis Scripts

### 1. test_random_chunks.py

**Purpose**: Select random chunks from different videos for realistic GraphRAG testing.

**Key Features**:
- Random chunk selection with configurable seed
- Cross-video diversity analysis
- Metadata clearing for selected chunks
- Expected results prediction

**Functionality**:
```python
def get_random_chunks(collection_name, num_chunks, seed)
def clear_graphrag_metadata(chunk_ids)
def print_run_command(num_chunks)
```

**API Overlap**: ❌ None - This is a testing utility

**Unique Value**:
- Ensures test diversity across videos
- Prevents single-video bias in testing
- Provides reproducible test scenarios

**Usage**:
```bash
python app/scripts/graphrag/test_random_chunks.py --num-chunks 12 --seed 42 --clear
```

**Keep?**: ✅ Yes - Essential for testing pipeline with diverse data

---

### 2. run_random_chunk_test.py

**Purpose**: Complete test orchestration - select chunks, clean DB, mark for processing.

**Key Features**:
- One chunk per video selection (maximizes diversity)
- Full GraphRAG cleanup
- Test chunk marking (`_test_exclude` flag)
- Automated test setup

**Functionality**:
```python
# Selects chunks from different videos
# Drops all GraphRAG collections
# Marks only selected chunks for processing
# Provides run instructions
```

**API Overlap**: ❌ None - Test orchestration utility

**Unique Value**:
- Automated test setup workflow
- Ensures clean test environment
- Prevents test interference

**Usage**:
```bash
python app/scripts/graphrag/run_random_chunk_test.py
```

**Keep?**: ✅ Yes - Streamlines testing workflow

---

### 3. analyze_graph_structure.py

**Purpose**: Deep graph structure analysis using NetworkX.

**Key Features**:
- NetworkX graph building from MongoDB
- Connectivity analysis (degree distribution, isolated nodes, components)
- Relationship type analysis
- Hub identification (most connected entities)
- Path analysis (shortest path, diameter)
- Clustering coefficient calculation
- Issue identification with recommendations

**Functionality**:
```python
def analyze_graph_structure():
    # 1. Build NetworkX graph
    # 2. Connectivity analysis
    # 3. Relationship type distribution
    # 4. Entity type analysis
    # 5. Hub analysis
    # 6. Path analysis (diameter, avg path length)
    # 7. Clustering coefficient
    # 8. Issue identification
    # 9. Recommendations
```

**API Overlap**: ⚠️ Partial overlap with `/api/statistics`

**Comparison with Statistics API**:

| Feature | Script | API | Notes |
|---------|--------|-----|-------|
| Total entities/relationships | ✅ | ✅ | Both provide |
| Graph density | ✅ | ✅ | Both provide |
| Degree distribution | ✅ | ✅ | Both provide |
| Type distribution | ✅ | ✅ | Both provide |
| **Connected components** | ✅ | ❌ | **Script only** |
| **Isolated nodes** | ✅ | ✅ | Both provide |
| **Path analysis** | ✅ | ❌ | **Script only** (diameter, avg path) |
| **Clustering coefficient** | ✅ | ❌ | **Script only** |
| **Hub identification** | ✅ | ❌ | **Script only** (top 10 entities) |
| **Issue detection** | ✅ | ❌ | **Script only** |
| **Recommendations** | ✅ | ❌ | **Script only** |

**Unique Value**:
- **More comprehensive** than Statistics API
- Provides **actionable recommendations**
- Uses **NetworkX** for advanced graph algorithms
- Identifies specific problems (low density, fragmentation, etc.)

**Usage**:
```bash
python app/scripts/graphrag/analyze_graph_structure.py
```

**Keep?**: ✅ Yes - Provides deeper analysis than API for debugging and optimization

---

### 4. monitor_density.py

**Purpose**: Real-time graph density monitoring during pipeline execution.

**Key Features**:
- Current density calculation
- Relationship type breakdown
- Status indicators (EXCELLENT, GOOD, WARNING, CRITICAL)
- Continuous monitoring mode with auto-refresh

**Functionality**:
```python
def calculate_density()  # Returns density, entity_count, relation_count
def get_relationship_breakdown()  # Returns type distribution
def monitor_once()  # Single snapshot
def monitor_continuous(interval)  # Continuous polling
```

**API Overlap**: ⚠️ Partial overlap with `/api/statistics`

**Comparison**:

| Feature | Script | API |
|---------|--------|-----|
| Graph density | ✅ | ✅ |
| Relationship breakdown | ✅ | ✅ |
| **Continuous monitoring** | ✅ | ❌ |
| **Status indicators** | ✅ | ❌ |
| **Auto-refresh** | ✅ | ❌ |

**Unique Value**:
- **Live monitoring** during pipeline execution
- User-friendly status indicators
- Watch mode for debugging

**Usage**:
```bash
# Single check
python app/scripts/graphrag/monitor_density.py

# Continuous monitoring
python app/scripts/graphrag/monitor_density.py --watch 10
```

**Keep?**: ✅ Yes - Provides real-time monitoring that API cannot

---

### 5. test_community_detection.py

**Purpose**: Test community detection algorithms on current graph data.

**Key Features**:
- Builds NetworkX graph from MongoDB
- Tests hierarchical Leiden algorithm
- Fallback to Louvain/connected components
- Community size distribution analysis
- Success/failure indicators

**Functionality**:
```python
# Builds NetworkX graph
# Runs hierarchical_leiden()
# Analyzes community sizes
# Falls back to nx.connected_components or Louvain
```

**API Overlap**: ❌ None - Testing utility, not query functionality

**Unique Value**:
- Tests algorithm behavior directly
- Validates community detection logic
- Helps debug community issues

**Usage**:
```bash
python app/scripts/graphrag/test_community_detection.py
```

**Keep?**: ✅ Yes - Essential for algorithm validation

---

### 6. inspect_community_detection.py

**Purpose**: Deep inspection of hierarchical Leiden algorithm output to debug single-entity communities.

**Key Features**:
- Detailed algorithm output inspection
- Object attribute introspection
- Cluster structure analysis
- Agent processing verification
- Quality metrics validation

**Functionality**:
```python
def inspect_hierarchical_leiden_output():
    # 1. Load data
    # 2. Convert to model objects
    # 3. Build NetworkX graph
    # 4. Run hierarchical_leiden
    # 5. Inspect returned objects (type, attributes)
    # 6. Analyze cluster structure
    # 7. Test agent processing
    # 8. Compare quality metrics
```

**API Overlap**: ❌ None - Debugging utility

**Unique Value**:
- **Critical for algorithm debugging**
- Reveals why single-entity communities occur
- Tests agent processing logic
- Provides diagnosis output

**Usage**:
```bash
python app/scripts/graphrag/inspect_community_detection.py
```

**Keep?**: ✅ Yes - Critical debugging tool for community detection issues

---

### 7. diagnose_communities.py

**Purpose**: Diagnose why communities have issues (single entities, no relationships).

**Key Features**:
- Collection counts validation
- Community size distribution
- Relationship coverage analysis
- Extraction status checks
- Root cause identification
- Actionable recommendations

**Functionality**:
```python
def analyze_graphrag_data():
    # 1. Collection counts
    # 2. Community size distribution
    # 3. Relationship analysis (coverage, isolated entities)
    # 4. Extraction status (chunks with entities/relationships)
    # 5. Graph construction status
    # 6. Entity resolution status
    # 7. Issue identification
    # 8. Recommended actions
```

**API Overlap**: ❌ None - Diagnostic utility

**Unique Value**:
- **Root cause analysis** for data quality issues
- Identifies pipeline stage failures
- Provides specific fix recommendations
- Validates data at each stage

**Usage**:
```bash
python app/scripts/graphrag/diagnose_communities.py
```

**Keep?**: ✅ Yes - Essential diagnostic tool

---

### 8. sample_graph_data.py

**Purpose**: Sample and display graph data with relationship distribution.

**Key Features**:
- Samples entities with details
- Shows relationships by type
- High-confidence LLM relationships
- Cross-chunk relationship samples
- Relationship type distribution

**Functionality**:
```python
# Samples 5 entities with full details
# Samples relationships by specific types
# Shows relationship type distribution
# Displays high-confidence LLM relationships
# Shows cross-chunk relationships
```

**API Overlap**: ⚠️ Partial - Could use API but provides formatted CLI output

**Comparison**:

| Feature | Script | API Equivalent |
|---------|--------|----------------|
| Sample entities | ✅ | `GET /api/entities/search?limit=5` |
| Sample relationships | ✅ | `GET /api/relationships/search?limit=5` |
| Type distribution | ✅ | `GET /api/statistics` |
| **Formatted CLI output** | ✅ | ❌ |
| **Specific type sampling** | ✅ | ❌ |

**Unique Value**:
- **Quick data inspection** from command line
- Formatted output for human reading
- Specific relationship type sampling

**Usage**:
```bash
python app/scripts/graphrag/sample_graph_data.py
```

**Keep?**: ✅ Yes - Convenient CLI inspection tool

---

## Database Utility Scripts

### 9. check_data.py

**Purpose**: Check GraphRAG data across all MongoDB databases.

**Key Features**:
- Scans all databases in MongoDB instance
- Counts GraphRAG collections
- Identifies where data exists
- Useful for multi-database environments

**Functionality**:
```python
# Iterates through all databases
# Checks for GraphRAG collections
# Reports counts for: entities, relations, mentions, communities
```

**API Overlap**: ❌ None - Database inspection utility

**Unique Value**:
- Multi-database scanning
- Quick data location
- Environment verification

**Usage**:
```bash
python app/scripts/utilities/check_data.py
```

**Keep?**: ✅ Yes - Useful for multi-DB environments

---

### 10. full_cleanup.py

**Purpose**: Complete GraphRAG data cleanup - drops collections and clears metadata.

**Key Features**:
- Drops all GraphRAG collections
- Clears chunk metadata
- Verification output
- Fast reset for testing

**Functionality**:
```python
# 1. Drop collections: entities, relations, communities, entity_mentions
# 2. Clear chunk metadata: graphrag_extraction, graphrag_resolution, etc.
# 3. Verify cleanup
```

**API Overlap**: ❌ None - Maintenance utility

**Unique Value**:
- **One-command full reset**
- Essential for testing clean slate
- Faster than manual cleanup

**Usage**:
```bash
python app/scripts/utilities/full_cleanup.py
```

**Keep?**: ✅ Yes - Essential for testing and troubleshooting

---

### 11. seed_indexes.py

**Purpose**: Initialize required MongoDB collections and indexes.

**Key Features**:
- Creates required collections if missing
- Sets up vector search indexes
- Creates feedback indexes
- Safe to run multiple times (idempotent)

**Functionality**:
```python
def ensure_collections_and_indexes(db):
    # Creates: raw_videos, video_chunks, cleaned_transcripts, 
    #          enriched_transcripts, memory_logs, video_feedback, chunk_feedback
    # Creates indexes: video_feedback, chunk_feedback
    # Ensures vector search index
```

**API Overlap**: ❌ None - Database initialization

**Unique Value**:
- **First-time setup automation**
- Index creation
- Environment bootstrapping

**Usage**:
```python
from app.scripts.utilities.seed.seed_indexes import ensure_collections_and_indexes
ensure_collections_and_indexes(db)
```

**Keep?**: ✅ Yes - Required for initial setup

---

## API Overlap Analysis

### Category 1: No Overlap (8 scripts)

These scripts provide unique functionality NOT available in any API:

| Script | Unique Functionality |
|--------|---------------------|
| `test_random_chunks.py` | Test chunk selection with diversity |
| `run_random_chunk_test.py` | Test orchestration and setup |
| `test_community_detection.py` | Algorithm testing |
| `inspect_community_detection.py` | Algorithm debugging |
| `diagnose_communities.py` | Root cause diagnosis |
| `check_data.py` | Multi-database scanning |
| `full_cleanup.py` | Database reset |
| `seed_indexes.py` | Index initialization |

**Recommendation**: ✅ Keep all - No duplication concerns

---

### Category 2: Partial Overlap (3 scripts)

These scripts overlap with API but provide **enhanced functionality**:

#### analyze_graph_structure.py vs GET /api/statistics

**Statistics API Provides**:
```json
{
  "total_entities": 914,
  "total_relationships": 204,
  "graph_density": 0.0005,
  "avg_degree": 0.45,
  "type_distribution": [...],
  "predicate_distribution": [...],
  "degree_distribution": [...]
}
```

**Script Provides (ADDITIONAL)**:
- ✅ Connected components analysis
- ✅ Shortest path analysis (diameter, avg path length)
- ✅ Clustering coefficient
- ✅ Hub identification (top 10 most connected entities)
- ✅ Entity type connectivity breakdown
- ✅ **Issue detection** (low density, fragmentation, etc.)
- ✅ **Actionable recommendations**

**Verdict**: ✅ Keep - Script provides **significantly more analysis** than API

---

#### monitor_density.py vs GET /api/statistics

**Statistics API Provides**:
- One-time snapshot of graph density

**Script Provides (ADDITIONAL)**:
- ✅ **Continuous monitoring** with auto-refresh
- ✅ **Status indicators** (EXCELLENT, GOOD, WARNING, CRITICAL)
- ✅ **Real-time updates** during pipeline execution
- ✅ Relationship breakdown by type

**Verdict**: ✅ Keep - Script provides **real-time monitoring** that API cannot

---

#### sample_graph_data.py vs API Endpoints

**API Provides**:
```bash
GET /api/entities/search?limit=5
GET /api/relationships/search?limit=5
GET /api/statistics  # type distribution
```

**Script Provides (ADDITIONAL)**:
- ✅ **Formatted CLI output** (human-readable)
- ✅ **Specific type sampling** (samples known predicates)
- ✅ **Cross-chunk relationship filtering**
- ✅ **Quick inspection** without API calls

**Verdict**: ✅ Keep - Script provides **convenient CLI inspection**

---

## Functionality Matrix

### What APIs Provide vs What Scripts Provide

| Functionality | Graph API | Scripts | Notes |
|---------------|-----------|---------|-------|
| **Query Data** |
| Search entities | ✅ | ✅ | API for UI, scripts for CLI |
| Get entity details | ✅ | ✅ | API for UI, scripts for CLI |
| Search communities | ✅ | ✅ | API for UI, scripts for CLI |
| Get ego network | ✅ | ❌ | API only |
| Export graph | ✅ | ❌ | API only |
| **Statistics** |
| Basic stats | ✅ | ✅ | Both provide |
| Degree distribution | ✅ | ✅ | Both provide |
| Type distribution | ✅ | ✅ | Both provide |
| Connected components | ❌ | ✅ | **Scripts only** |
| Path analysis | ❌ | ✅ | **Scripts only** (diameter, avg path) |
| Clustering coefficient | ❌ | ✅ | **Scripts only** |
| Hub identification | ❌ | ✅ | **Scripts only** |
| **Testing & Debugging** |
| Test data selection | ❌ | ✅ | **Scripts only** |
| Algorithm testing | ❌ | ✅ | **Scripts only** |
| Issue diagnosis | ❌ | ✅ | **Scripts only** |
| Real-time monitoring | ❌ | ✅ | **Scripts only** |
| **Maintenance** |
| Database cleanup | ❌ | ✅ | **Scripts only** |
| Index initialization | ❌ | ✅ | **Scripts only** |

---

## Recommendations

### For GraphDash UI Implementation

**Use Graph API endpoints exclusively:**
- ✅ `GET /api/entities/search` - Entity search
- ✅ `GET /api/communities/search` - Community browsing
- ✅ `GET /api/ego/network/{id}` - Ego network visualization
- ✅ `GET /api/statistics` - Dashboard statistics
- ✅ `GET /api/export/{format}` - Data export

**DO NOT use scripts from UI:**
- ❌ Scripts are for CLI/development only
- ❌ Scripts have direct database access (not scalable)
- ❌ Scripts are not designed for HTTP/web integration

---

### Script Organization Recommendations

#### Keep All Scripts

**Rationale**:
1. **No problematic duplication** - Scripts provide unique value
2. **Essential for development** - Testing, debugging, monitoring
3. **Different use cases** - CLI vs API (programmatic)
4. **Complementary functionality** - Scripts extend beyond API capabilities

#### Potential Enhancements

If you want to expose script functionality via API in the future:

**High-Value Additions to Graph API**:

1. **Connected Components Endpoint**
   ```
   GET /api/statistics/components
   → Returns: component sizes, isolated nodes, fragmentation metrics
   ```

2. **Hub Entities Endpoint**
   ```
   GET /api/entities/hubs?limit=10
   → Returns: Most connected entities
   ```

3. **Graph Health Endpoint**
   ```
   GET /api/statistics/health
   → Returns: Issues detected, recommendations, health score
   ```

4. **Clustering Metrics Endpoint**
   ```
   GET /api/statistics/clustering
   → Returns: Clustering coefficient, triangle count, cohesion metrics
   ```

**Priority**: 🟡 Medium - Current API is sufficient for UI, these are nice-to-have

---

## Usage Guide

### For Developers

**Before Running Pipeline**:
```bash
# 1. Check existing data across databases
python app/scripts/utilities/check_data.py

# 2. Clean slate if needed
python app/scripts/utilities/full_cleanup.py

# 3. Set up indexes (first time only)
python -c "from app.scripts.utilities.seed.seed_indexes import ensure_collections_and_indexes; from pymongo import MongoClient; import os; ensure_collections_and_indexes(MongoClient(os.getenv('MONGODB_URI'))[os.getenv('MONGODB_DB')])"
```

**During Pipeline Testing**:
```bash
# Monitor density in real-time
python app/scripts/graphrag/monitor_density.py --watch 5
```

**After Pipeline Completion**:
```bash
# Analyze graph structure
python app/scripts/graphrag/analyze_graph_structure.py

# Test community detection
python app/scripts/graphrag/test_community_detection.py

# Diagnose issues if any
python app/scripts/graphrag/diagnose_communities.py

# Sample data
python app/scripts/graphrag/sample_graph_data.py
```

**For Controlled Testing**:
```bash
# Test with random chunks from different videos
python app/scripts/graphrag/test_random_chunks.py --num-chunks 12 --clear

# Or automated test setup
python app/scripts/graphrag/run_random_chunk_test.py
```

---

### For UI Developers

**DO**:
- ✅ Use Graph API endpoints (`http://localhost:8081/api/*`)
- ✅ Reference `GRAPH_API_TECHNICAL_REFERENCE.md`
- ✅ Use TypeScript interfaces from API docs
- ✅ Test with Postman collection

**DON'T**:
- ❌ Import or call script functions from UI
- ❌ Use scripts for data fetching
- ❌ Expose scripts via UI

**If You Need Functionality from Scripts**:
- Request API endpoint addition
- Scripts can inform API design
- API team can expose functionality properly

---

## Script Dependencies

### External Dependencies

```python
# From scripts
import networkx as nx           # Graph algorithms
from graspologic.partition import hierarchical_leiden  # Community detection
from pymongo import MongoClient  # Direct DB access
```

### Internal Dependencies

```python
# From project
from dependencies.database.mongodb import get_mongo_client
from business.services.graphrag.indexes import get_graphrag_collections
from core.config.paths import DB_NAME
from agents.community_detection_agent import CommunityDetectionAgent
from core.models.graphrag import ResolvedEntity, ResolvedRelationship
```

**Note**: Scripts have **direct database access** - not suitable for production API exposure without refactoring.

---

## Maintenance Notes

### When to Update Scripts

1. **Database schema changes**: Update model parsing in scripts
2. **New collection added**: Update `check_data.py` and `full_cleanup.py`
3. **Algorithm changes**: Update detection/analysis scripts
4. **New relationship types**: Update `monitor_density.py` breakdown

### When to Deprecate Scripts

Scripts can be deprecated if:
- ✅ Functionality is fully available via API
- ✅ No unique CLI value remains
- ✅ No testing/debugging value

**Currently**: All scripts should be kept.

---

## Conclusion

### Summary

- **11 scripts total** in `app/scripts/`
- **0 scripts with problematic duplication** - All provide unique value
- **3 scripts with partial API overlap** - But provide enhanced CLI functionality
- **8 scripts with zero API overlap** - Unique testing/debugging utilities

### Recommendations

1. ✅ **Keep all scripts** - No duplication issues, all provide value
2. ✅ **Use Graph API for UI** - Scripts are not designed for web integration
3. 🟡 **Consider API enhancements** - Add components, hubs, health endpoints in future
4. ✅ **Document usage patterns** - This document serves that purpose

### For GraphDash Implementation

**Primary Reference**: `GRAPH_API_TECHNICAL_REFERENCE.md`

**Data Source**: Graph API endpoints at `http://localhost:8081/api`

**Scripts Role**: Development and debugging only, not for UI integration

---

**End of Document**

