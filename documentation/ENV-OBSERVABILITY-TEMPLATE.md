# Environment Configuration Template for GraphRAG Observability

This document serves as a template for creating your `.env.observability` or `.env` file.

Copy the content below and save as `.env.observability` in your project root, then customize values for your environment.

---

```bash
# GraphRAG Observability Configuration Template
# Copy this content to .env.observability in project root and customize

# ═══════════════════════════════════════════════════════════════════════════════
# CORE SETTINGS (REQUIRED)
# ═══════════════════════════════════════════════════════════════════════════════

# MongoDB connection string (REQUIRED)
MONGODB_URI=mongodb://localhost:27017

# MongoDB database name
DB_NAME=mongo_hack

# OpenAI API Key (REQUIRED)
OPENAI_API_KEY=sk-your-key-here

# Environment
GRAPHRAG_ENVIRONMENT=development

# ═══════════════════════════════════════════════════════════════════════════════
# PIPELINE SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

GRAPHRAG_ENABLED=true
GRAPHRAG_ENABLE_INCREMENTAL=true
GRAPHRAG_MAX_PROCESSING_TIME=7200
GRAPHRAG_CHECKPOINT_INTERVAL=100
GRAPHRAG_MAX_RETRIES=3
GRAPHRAG_RETRY_DELAY=5.0
GRAPHRAG_CONTINUE_ON_ERROR=true
GRAPHRAG_LOG_LEVEL=DEBUG

# ═══════════════════════════════════════════════════════════════════════════════
# LLM SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

GRAPHRAG_MODEL=gpt-4o-mini
GRAPHRAG_TEMPERATURE=0.1
GRAPHRAG_LLM_RETRIES=3
GRAPHRAG_LLM_BACKOFF_S=1.0

# ═══════════════════════════════════════════════════════════════════════════════
# EXTRACTION SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

GRAPHRAG_EXTRACTION_CONCURRENCY=5
GRAPHRAG_MAX_ENTITIES_PER_CHUNK=20
GRAPHRAG_MAX_RELATIONSHIPS_PER_CHUNK=30
GRAPHRAG_MIN_ENTITY_CONFIDENCE=0.3
GRAPHRAG_BATCH_SIZE=25
GRAPHRAG_EXTRACTION_TIMEOUT=60

# ═══════════════════════════════════════════════════════════════════════════════
# ENTITY RESOLUTION SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

GRAPHRAG_RESOLUTION_CONCURRENCY=5
GRAPHRAG_ENTITY_RESOLUTION_THRESHOLD=0.85
GRAPHRAG_RESOLUTION_BATCH_SIZE=100
GRAPHRAG_RESOLUTION_TIMEOUT=90
GRAPHRAG_USE_FUZZY_MATCHING=true
GRAPHRAG_USE_EMBEDDING_SIMILARITY=true

# ═══════════════════════════════════════════════════════════════════════════════
# GRAPH CONSTRUCTION SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

GRAPHRAG_CONSTRUCTION_BATCH_SIZE=200
GRAPHRAG_MAX_RELATIONSHIPS_PER_ENTITY=100
GRAPHRAG_CALCULATE_CENTRALITY=true
GRAPHRAG_CALCULATE_DEGREE=true

# ═══════════════════════════════════════════════════════════════════════════════
# COMMUNITY DETECTION SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

GRAPHRAG_COMMUNITY_TEMPERATURE=0.2
GRAPHRAG_COMMUNITY_ALGORITHM=louvain
GRAPHRAG_MAX_CLUSTER_SIZE=50
GRAPHRAG_RESOLUTION_PARAMETER=1.0
GRAPHRAG_COMMUNITY_CONCURRENCY=5
```

---

## How to Use This Template

1. **Copy the template**:

   ```bash
   cp documentation/ENV-OBSERVABILITY-TEMPLATE.md .env.observability
   # OR
   cp documentation/ENV-OBSERVABILITY-TEMPLATE.md .env
   ```

2. **Edit the file** and set:

   - `MONGODB_URI` - your MongoDB connection string
   - `OPENAI_API_KEY` - your OpenAI API key
   - Other variables as needed for your use case

3. **Load the environment**:

   ```bash
   # Using direnv (if installed)
   direnv allow

   # OR manually
   source .env.observability

   # OR for python scripts, they automatically read from .env
   python your_script.py
   ```

4. **Verify configuration**:
   ```bash
   # Check that variables are loaded
   echo $MONGODB_URI
   echo $OPENAI_API_KEY
   ```

---

## Configuration Profiles

### Development Profile (Observability Focus)

```bash
GRAPHRAG_ENVIRONMENT=development
GRAPHRAG_LOG_LEVEL=DEBUG
GRAPHRAG_BATCH_SIZE=25
GRAPHRAG_EXTRACTION_CONCURRENCY=5
GRAPHRAG_RESOLUTION_CONCURRENCY=5
GRAPHRAG_COMMUNITY_CONCURRENCY=5
```

### Production Profile

```bash
GRAPHRAG_ENVIRONMENT=production
GRAPHRAG_LOG_LEVEL=WARNING
GRAPHRAG_BATCH_SIZE=200
GRAPHRAG_EXTRACTION_CONCURRENCY=300
GRAPHRAG_RESOLUTION_CONCURRENCY=300
GRAPHRAG_COMMUNITY_CONCURRENCY=300
```

### Testing Profile

```bash
GRAPHRAG_ENVIRONMENT=staging
GRAPHRAG_LOG_LEVEL=INFO
GRAPHRAG_BATCH_SIZE=50
GRAPHRAG_EXTRACTION_CONCURRENCY=10
GRAPHRAG_RESOLUTION_CONCURRENCY=8
```

---

## Required vs. Optional

**REQUIRED (must set):**

- `MONGODB_URI` - MongoDB connection string
- `OPENAI_API_KEY` - OpenAI API key

**OPTIONAL (all have sensible defaults):**

- Everything else - use defaults or customize as needed

---

## Validation Checklist

Before running pipeline, verify:

- [ ] MONGODB_URI is accessible
- [ ] OPENAI_API_KEY is valid
- [ ] Environment variables are loaded: `echo $MONGODB_URI`
- [ ] No typos in variable names (case-sensitive)
- [ ] Boolean values are "true" or "false"
- [ ] Numeric values are valid numbers

---

**Template Generated**: 2025-11-11  
**Total Variables**: 38  
**Last Updated**: 2025-11-11
