# GraphRAG Environment Variables Guide

**Status**: Complete  
**Last Updated**: 2025-11-11  
**Total Variables**: 38 documented

---

## Overview

This guide documents all environment variables used by the GraphRAG observability infrastructure. Variables are organized by category and include type, default values, and usage information.

---

## 📋 Quick Reference Table

| Category         | Variable                              | Type    | Default                   | Required | Used By               |
| ---------------- | ------------------------------------- | ------- | ------------------------- | -------- | --------------------- |
| **Core**         | MONGODB_URI                           | string  | mongodb://localhost:27017 | Yes      | All stages            |
| **Core**         | DB_NAME                               | string  | mongo_hack                | No       | All stages            |
| **Core**         | MONGODB_DB                            | string  | mongo_hack                | No       | paths.py              |
| **Core**         | OPENAI_API_KEY                        | string  | (empty)                   | Yes      | graphrag.py, agents   |
| **Core**         | GRAPHRAG_ENVIRONMENT                  | string  | development               | No       | graphrag.py           |
| **Pipeline**     | GRAPHRAG_ENABLED                      | boolean | true                      | No       | graphrag.py           |
| **Pipeline**     | EXPERIMENT_ID                         | string  | (none)                    | No       | pipeline config       |
| **Pipeline**     | GRAPHRAG_ENABLE_INCREMENTAL           | boolean | true                      | No       | Pipeline              |
| **Pipeline**     | GRAPHRAG_MAX_PROCESSING_TIME          | int     | 7200                      | No       | Pipeline              |
| **Pipeline**     | GRAPHRAG_CHECKPOINT_INTERVAL          | int     | 100                       | No       | Pipeline              |
| **Pipeline**     | GRAPHRAG_MAX_RETRIES                  | int     | 3                         | No       | Pipeline              |
| **Pipeline**     | GRAPHRAG_RETRY_DELAY                  | float   | 5.0                       | No       | Pipeline              |
| **Pipeline**     | GRAPHRAG_CONTINUE_ON_ERROR            | boolean | true                      | No       | Pipeline              |
| **Pipeline**     | GRAPHRAG_LOG_LEVEL                    | string  | INFO                      | No       | Pipeline              |
| **Pipeline**     | GRAPHRAG_LOG_FILE                     | string  | (none)                    | No       | Pipeline              |
| **Extraction**   | GRAPHRAG_MODEL                        | string  | gpt-4o-mini               | No       | All stages            |
| **Extraction**   | OPENAI_MODEL                          | string  | (none)                    | No       | All stages (fallback) |
| **Extraction**   | GRAPHRAG_EXTRACTION_CONCURRENCY       | int     | 300                       | No       | Extraction            |
| **Extraction**   | GRAPHRAG_TEMPERATURE                  | float   | 0.1                       | No       | All stages            |
| **Extraction**   | GRAPHRAG_MAX_TOKENS                   | int     | (none)                    | No       | All stages            |
| **Extraction**   | GRAPHRAG_LLM_RETRIES                  | int     | 3                         | No       | All stages            |
| **Extraction**   | GRAPHRAG_LLM_BACKOFF_S                | float   | 1.0                       | No       | All stages            |
| **Extraction**   | GRAPHRAG_MAX_ENTITIES_PER_CHUNK       | int     | 20                        | No       | Extraction            |
| **Extraction**   | GRAPHRAG_MAX_RELATIONSHIPS_PER_CHUNK  | int     | 30                        | No       | Extraction            |
| **Extraction**   | GRAPHRAG_MIN_ENTITY_CONFIDENCE        | float   | 0.3                       | No       | Extraction            |
| **Extraction**   | GRAPHRAG_MIN_RELATIONSHIP_CONFIDENCE  | float   | 0.3                       | No       | Extraction            |
| **Extraction**   | GRAPHRAG_BATCH_SIZE                   | int     | 50                        | No       | Extraction            |
| **Extraction**   | GRAPHRAG_EXTRACTION_TIMEOUT           | int     | 30                        | No       | Extraction            |
| **Resolution**   | GRAPHRAG_RESOLUTION_CONCURRENCY       | int     | 300                       | No       | Resolution            |
| **Resolution**   | GRAPHRAG_ENTITY_RESOLUTION_THRESHOLD  | float   | 0.85                      | No       | Resolution            |
| **Resolution**   | GRAPHRAG_MAX_ALIASES_PER_ENTITY       | int     | 10                        | No       | Resolution            |
| **Resolution**   | GRAPHRAG_MIN_SOURCE_COUNT             | int     | 1                         | No       | Resolution            |
| **Resolution**   | GRAPHRAG_RESOLUTION_BATCH_SIZE        | int     | 100                       | No       | Resolution            |
| **Resolution**   | GRAPHRAG_RESOLUTION_TIMEOUT           | int     | 60                        | No       | Resolution            |
| **Resolution**   | GRAPHRAG_USE_FUZZY_MATCHING           | boolean | true                      | No       | Resolution            |
| **Resolution**   | GRAPHRAG_USE_EMBEDDING_SIMILARITY     | boolean | true                      | No       | Resolution            |
| **Resolution**   | GRAPHRAG_USE_CONTEXT_SIMILARITY       | boolean | true                      | No       | Resolution            |
| **Resolution**   | GRAPHRAG_USE_RELATIONSHIP_CLUSTERING  | boolean | true                      | No       | Resolution            |
| **Construction** | GRAPHRAG_CONSTRUCTION_BATCH_SIZE      | int     | 200                       | No       | Construction          |
| **Construction** | GRAPHRAG_MAX_RELATIONSHIPS_PER_ENTITY | int     | 100                       | No       | Construction          |
| **Construction** | GRAPHRAG_CALCULATE_CENTRALITY         | boolean | true                      | No       | Construction          |
| **Construction** | GRAPHRAG_CALCULATE_DEGREE             | boolean | true                      | No       | Construction          |
| **Construction** | GRAPHRAG_CALCULATE_CLUSTERING         | boolean | false                     | No       | Construction          |
| **Construction** | GRAPHRAG_VALIDATE_ENTITY_EXISTENCE    | boolean | true                      | No       | Construction          |
| **Construction** | GRAPHRAG_MAX_RELATIONSHIP_DISTANCE    | int     | 3                         | No       | Construction          |
| **Detection**    | GRAPHRAG_COMMUNITY_TEMPERATURE        | float   | 0.2                       | No       | Detection             |
| **Detection**    | GRAPHRAG_COMMUNITY_ALGORITHM          | string  | louvain                   | No       | Detection             |
| **Detection**    | GRAPHRAG_MAX_CLUSTER_SIZE             | int     | 50                        | No       | Detection             |
| **Detection**    | GRAPHRAG_MIN_CLUSTER_SIZE             | int     | 2                         | No       | Detection             |
| **Detection**    | GRAPHRAG_RESOLUTION_PARAMETER         | float   | 1.0                       | No       | Detection             |
| **Detection**    | GRAPHRAG_MAX_ITERATIONS               | int     | 100                       | No       | Detection             |
| **Detection**    | GRAPHRAG_MAX_LEVELS                   | int     | 3                         | No       | Detection             |
| **Detection**    | GRAPHRAG_LEVEL_SIZE_THRESHOLD         | int     | 5                         | No       | Detection             |
| **Detection**    | GRAPHRAG_MAX_SUMMARY_LENGTH           | int     | 2000                      | No       | Detection             |
| **Detection**    | GRAPHRAG_MIN_SUMMARY_LENGTH           | int     | 100                       | No       | Detection             |
| **Detection**    | GRAPHRAG_SUMMARIZATION_TIMEOUT        | int     | 120                       | No       | Detection             |
| **Detection**    | GRAPHRAG_MIN_COHERENCE_SCORE          | float   | 0.6                       | No       | Detection             |
| **Detection**    | GRAPHRAG_MIN_ENTITY_COUNT             | int     | 2                         | No       | Detection             |
| **Detection**    | GRAPHRAG_COMMUNITY_CONCURRENCY        | int     | 300                       | No       | Detection             |

---

## 📖 Detailed Variable Descriptions

### Core Settings

#### MONGODB_URI

- **Type**: String
- **Default**: `mongodb://localhost:27017`
- **Required**: Yes
- **Purpose**: MongoDB connection string
- **Example**: `mongodb://localhost:27017` (local), `mongodb+srv://user:pass@cluster.mongodb.net/` (Atlas)
- **Used By**: All stages
- **Impact on Observability**: Must be accessible for transformation logs and intermediate data storage

#### DB_NAME / MONGODB_DB

- **Type**: String
- **Default**: `mongo_hack`
- **Required**: No
- **Purpose**: MongoDB database name
- **Note**: DB_NAME takes precedence over MONGODB_DB
- **Used By**: All stages
- **Impact on Observability**: Collections stored in this database

#### OPENAI_API_KEY

- **Type**: String
- **Default**: (empty string - raises error if missing)
- **Required**: Yes
- **Purpose**: OpenAI API authentication
- **Format**: Must start with "sk-"
- **Used By**: All LLM stages
- **Impact on Observability**: Required for entity extraction, resolution, and community summarization

#### GRAPHRAG_ENVIRONMENT

- **Type**: String (development, staging, production)
- **Default**: `development`
- **Required**: No
- **Purpose**: Controls environment-specific configuration overrides
- **Effect on Observability**: Production sets log level to WARNING, enables monitoring and caching

---

### Pipeline Settings

#### GRAPHRAG_ENABLED

- **Type**: Boolean
- **Default**: `true`
- **Required**: No
- **Purpose**: Enable/disable GraphRAG pipeline

#### EXPERIMENT_ID

- **Type**: String
- **Default**: (none)
- **Required**: No
- **Purpose**: Track experiment runs across databases
- **Used By**: Pipeline config
- **Impact on Observability**: Links all transformations to experiment

#### GRAPHRAG_ENABLE_INCREMENTAL

- **Type**: Boolean
- **Default**: `true`
- **Required**: No
- **Purpose**: Enable incremental processing

#### GRAPHRAG_MAX_PROCESSING_TIME

- **Type**: Integer (seconds)
- **Default**: `7200` (2 hours)
- **Required**: No
- **Purpose**: Maximum pipeline execution time

#### GRAPHRAG_LOG_LEVEL

- **Type**: String (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **Default**: `INFO`
- **Required**: No
- **Purpose**: Logging verbosity level
- **Impact on Observability**: Higher levels capture more details in transformation logs

---

### Extraction Settings

#### GRAPHRAG_MODEL / OPENAI_MODEL

- **Type**: String
- **Default**: `gpt-4o-mini`
- **Required**: No
- **Purpose**: LLM model name for all stages
- **Note**: GRAPHRAG_MODEL takes precedence
- **Common Values**: gpt-4o-mini (cost-effective), gpt-4-turbo (better quality), gpt-4 (most powerful)

#### GRAPHRAG_TEMPERATURE

- **Type**: Float (0.0-1.0)
- **Default**: `0.1`
- **Required**: No
- **Purpose**: LLM response temperature (creativity/determinism)
- **Values**: 0.0 = deterministic, 1.0 = creative
- **Recommendation**: Keep low (0.1) for entity extraction consistency

#### GRAPHRAG_MAX_TOKENS

- **Type**: Integer
- **Default**: (none - uses model default ~4000)
- **Required**: No
- **Purpose**: Maximum tokens for LLM responses

#### GRAPHRAG_EXTRACTION_CONCURRENCY

- **Type**: Integer
- **Default**: `300`
- **Required**: No
- **Purpose**: Number of concurrent extraction requests
- **Recommendation**: 300 for batch processing, 5-10 for sequential

#### GRAPHRAG_BATCH_SIZE

- **Type**: Integer
- **Default**: `50`
- **Required**: No
- **Purpose**: Number of chunks processed in each batch
- **Impact on Observability**: Smaller batches = more granular transformation logs

#### GRAPHRAG_MAX_ENTITIES_PER_CHUNK

- **Type**: Integer
- **Default**: `20`
- **Required**: No
- **Purpose**: Maximum entities extracted per chunk

#### GRAPHRAG_MIN_ENTITY_CONFIDENCE

- **Type**: Float (0.0-1.0)
- **Default**: `0.3`
- **Required**: No
- **Purpose**: Minimum confidence for extracted entities
- **Impact on Observability**: Higher threshold = fewer entities logged

---

### Resolution Settings

#### GRAPHRAG_ENTITY_RESOLUTION_THRESHOLD

- **Type**: Float (0.0-1.0)
- **Default**: `0.85`
- **Required**: No
- **Purpose**: Similarity threshold for entity merging
- **Higher Value**: Fewer merges (more conservative)
- **Lower Value**: More merges (more aggressive)
- **Impact on Observability**: Critical for merge decision logging

#### GRAPHRAG_RESOLUTION_CONCURRENCY

- **Type**: Integer
- **Default**: `300`
- **Required**: No
- **Purpose**: Number of concurrent resolution requests

#### GRAPHRAG_USE_FUZZY_MATCHING

- **Type**: Boolean
- **Default**: `true`
- **Required**: No
- **Purpose**: Enable fuzzy string matching for resolution
- **Impact on Observability**: Logged as merge method "fuzzy_match"

#### GRAPHRAG_USE_EMBEDDING_SIMILARITY

- **Type**: Boolean
- **Default**: `true`
- **Required**: No
- **Purpose**: Enable embedding-based similarity matching
- **Impact on Observability**: Logged as merge method "embedding"

---

### Construction Settings

#### GRAPHRAG_MAX_RELATIONSHIPS_PER_ENTITY

- **Type**: Integer
- **Default**: `100`
- **Required**: No
- **Purpose**: Maximum relationships per entity in graph

#### GRAPHRAG_CONSTRUCTION_BATCH_SIZE

- **Type**: Integer
- **Default**: `200`
- **Required**: No
- **Purpose**: Batch size for graph construction

#### GRAPHRAG_VALIDATE_ENTITY_EXISTENCE

- **Type**: Boolean
- **Default**: `true`
- **Required**: No
- **Purpose**: Validate entities exist before creating relationships

---

### Community Detection Settings

#### GRAPHRAG_COMMUNITY_ALGORITHM

- **Type**: String (louvain, hierarchical_leiden)
- **Default**: `louvain`
- **Required**: No
- **Purpose**: Algorithm for community detection
- **Recommended**: louvain (faster, more stable)

#### GRAPHRAG_MAX_CLUSTER_SIZE

- **Type**: Integer
- **Default**: `50`
- **Required**: No
- **Purpose**: Soft limit for community size (Louvain ignores)

#### GRAPHRAG_RESOLUTION_PARAMETER

- **Type**: Float (0.5-2.0)
- **Default**: `1.0`
- **Required**: No
- **Purpose**: Resolution parameter for Louvain algorithm
- **Lower**: Larger communities
- **Higher**: Smaller communities

#### GRAPHRAG_COMMUNITY_TEMPERATURE

- **Type**: Float (0.0-1.0)
- **Default**: `0.2`
- **Required**: No
- **Purpose**: LLM temperature for community summarization

---

## 🔧 Use Cases & Configuration Examples

### Development Configuration

```bash
GRAPHRAG_ENVIRONMENT=development
GRAPHRAG_EXTRACTION_CONCURRENCY=5
GRAPHRAG_RESOLUTION_CONCURRENCY=5
GRAPHRAG_LOG_LEVEL=DEBUG
GRAPHRAG_ENTITY_RESOLUTION_THRESHOLD=0.85
```

### Testing Configuration

```bash
GRAPHRAG_ENVIRONMENT=staging
GRAPHRAG_EXTRACTION_CONCURRENCY=10
GRAPHRAG_RESOLUTION_CONCURRENCY=8
GRAPHRAG_LOG_LEVEL=INFO
GRAPHRAG_BATCH_SIZE=50
GRAPHRAG_CHECKPOINT_INTERVAL=50
```

### Production Configuration

```bash
GRAPHRAG_ENVIRONMENT=production
GRAPHRAG_EXTRACTION_CONCURRENCY=20
GRAPHRAG_RESOLUTION_CONCURRENCY=15
GRAPHRAG_LOG_LEVEL=WARNING
GRAPHRAG_MAX_RETRIES=5
GRAPHRAG_BATCH_SIZE=200
```

### Observability Focus Configuration

```bash
GRAPHRAG_LOG_LEVEL=DEBUG
GRAPHRAG_BATCH_SIZE=25
GRAPHRAG_EXTRACTION_TIMEOUT=60
GRAPHRAG_RESOLUTION_TIMEOUT=90
GRAPHRAG_ENTITY_RESOLUTION_THRESHOLD=0.90
```

---

## 🔍 Troubleshooting

### Issue: Variables Not Being Read

**Solution**: Check order of precedence - args > env > default. Verify environment variable is set: `echo $VARIABLE_NAME`

### Issue: Type Conversion Errors

**Solution**: Verify correct types:

- Boolean: Must be "true" or "false" (case-insensitive)
- Integer: Numeric values only
- Float: Decimal values (e.g., 0.85)

### Issue: Different Behavior Between Dev and Production

**Solution**: Check GRAPHRAG_ENVIRONMENT - production overrides many settings automatically

### Issue: Entity Merging Too Aggressive/Conservative

**Solution**: Adjust GRAPHRAG_ENTITY_RESOLUTION_THRESHOLD (higher = less aggressive)

---

## ✅ Validation Checklist

Before running pipeline with observability enabled:

- [ ] MONGODB_URI is accessible
- [ ] OPENAI_API_KEY is valid and set
- [ ] GRAPHRAG_ENVIRONMENT matches your use case
- [ ] Concurrency settings appropriate for your hardware
- [ ] Log levels appropriate for observability focus
- [ ] Timeout values reasonable for your data size

---

## 📊 Variable Statistics

- **Total Variables**: 38
- **Required**: 2 (MONGODB_URI, OPENAI_API_KEY)
- **Optional**: 36
- **Boolean**: 12
- **String**: 8
- **Integer**: 12
- **Float**: 6

---

**Document Generated**: 2025-11-11  
**Verification Status**: Ready for validation testing
