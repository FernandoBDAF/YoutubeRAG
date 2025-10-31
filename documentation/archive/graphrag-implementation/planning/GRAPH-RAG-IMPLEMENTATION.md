# GraphRAG Implementation Documentation

## Overview

This document provides comprehensive documentation for the GraphRAG (Graph-based Retrieval-Augmented Generation) implementation in the YouTubeRAG project. GraphRAG enhances traditional RAG by creating a knowledge graph from video content and using graph-based retrieval to provide more contextual and comprehensive answers.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Core Components](#core-components)
3. [Data Model](#data-model)
4. [Pipeline Stages](#pipeline-stages)
5. [Query Processing](#query-processing)
6. [MongoDB Integration](#mongodb-integration)
7. [Performance Optimization](#performance-optimization)
8. [API Reference](#api-reference)
9. [Configuration](#configuration)
10. [Testing](#testing)
11. [Deployment](#deployment)
12. [Troubleshooting](#troubleshooting)

## Architecture Overview

The GraphRAG implementation follows a modular architecture with the following key components:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Ingestion │    │  GraphRAG       │    │   Query         │
│   & Processing   │───▶│  Pipeline       │───▶│   Processing    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   MongoDB       │
                       │   Knowledge     │
                       │   Graph         │
                       └─────────────────┘
```

### Key Features

- **Entity Extraction**: LLM-powered extraction of entities and relationships from video content
- **Entity Resolution**: Multi-strategy entity canonicalization and deduplication
- **Graph Construction**: Building knowledge graphs with confidence scoring
- **Community Detection**: Hierarchical community detection using Leiden algorithm
- **Hybrid Retrieval**: Combining vector search, keyword search, and graph traversal
- **MongoDB Integration**: Native MongoDB operations with optimized indexing
- **Performance Monitoring**: Comprehensive performance analysis and optimization

## Core Components

### 1. GraphRAG Models (`core/graphrag_models.py`)

Pydantic models for structured data representation:

```python
class EntityType(str, Enum):
    PERSON = "PERSON"
    ORGANIZATION = "ORGANIZATION"
    TECHNOLOGY = "TECHNOLOGY"
    CONCEPT = "CONCEPT"
    LOCATION = "LOCATION"
    EVENT = "EVENT"
    OTHER = "OTHER"

class EntityModel(BaseModel):
    name: str = Field(description="Name of the entity, capitalized")
    type: EntityType = Field(description="Type of the entity")
    description: str = Field(description="Comprehensive description")
    confidence: float = Field(description="Confidence score", default=0.0)
```

### 2. GraphRAG Configuration (`core/graphrag_config.py`)

Configuration classes for pipeline stages:

```python
@dataclass
class GraphExtractionConfig(BaseStageConfig):
    model_name: str = "gpt-4o-mini"
    max_entities_per_chunk: int = 10
    max_relationships_per_chunk: int = 15
    min_confidence_threshold: float = 0.5
```

### 3. GraphRAG Agents

#### Graph Extraction Agent (`agents/graph_extraction_agent.py`)

- Extracts entities and relationships from text chunks
- Uses OpenAI's structured output for consistent parsing
- Implements confidence scoring and validation

#### Entity Resolution Agent (`agents/entity_resolution_agent.py`)

- Multi-strategy entity canonicalization
- Handles lexical variations and synonyms
- Generates comprehensive entity summaries

#### Community Detection Agent (`agents/community_detection_agent.py`)

- Implements hierarchical Leiden algorithm
- Detects communities at multiple scales
- Generates community summaries using LLM

## Data Model

### MongoDB Collections

#### 1. Entities Collection

```json
{
  "_id": ObjectId,
  "name": "Machine Learning",
  "canonical_name": "machine_learning",
  "type": "CONCEPT",
  "description": "A subset of artificial intelligence...",
  "trust_score": 0.85,
  "centrality_score": 0.92,
  "source_chunks": ["chunk_1", "chunk_2"],
  "mentions": [
    {
      "chunk_id": "chunk_1",
      "context": "Machine learning algorithms...",
      "confidence": 0.9
    }
  ],
  "created_at": ISODate,
  "updated_at": ISODate
}
```

#### 2. Relations Collection

```json
{
  "_id": ObjectId,
  "source_id": "entity_1",
  "target_id": "entity_2",
  "relationship_type": "RELATED_TO",
  "description": "Machine learning is a subset of artificial intelligence",
  "confidence": 0.88,
  "source_chunks": ["chunk_1"],
  "created_at": ISODate
}
```

#### 3. Communities Collection

```json
{
  "_id": ObjectId,
  "entities": ["entity_1", "entity_2", "entity_3"],
  "level": 1,
  "coherence_score": 0.75,
  "summary": "AI and Machine Learning community...",
  "hierarchical_summary": "High-level AI concepts...",
  "created_at": ISODate
}
```

### Indexes

#### Entity Indexes

- Compound index: `(name, type, trust_score)`
- Text index: `(name, canonical_name)`
- Sparse index: `(centrality_score)`

#### Relation Indexes

- Bidirectional: `(source_id, target_id, confidence)`
- Type-based: `(relationship_type, confidence)`

#### Community Indexes

- Entity array: `(entities, level, coherence_score)`
- Text index: `(summary)`

## Pipeline Stages

### 1. Graph Extraction Stage (`app/stages/graph_extraction.py`)

**Purpose**: Extract entities and relationships from text chunks

**Process**:

1. Read processed chunks from database
2. Use GraphExtractionAgent to extract entities and relationships
3. Store raw extractions for resolution

**Configuration**:

```python
GraphExtractionConfig(
    max=None,
    llm=True,
    verbose=True,
    concurrency=15,
    model_name="gpt-4o-mini"
)
```

### 2. Entity Resolution Stage (`app/stages/entity_resolution.py`)

**Purpose**: Resolve and canonicalize entities across chunks

**Process**:

1. Read raw entity extractions
2. Group entities by similarity
3. Resolve conflicts and create canonical entities
4. Store resolved entities and entity mentions

### 3. Graph Construction Stage (`app/stages/graph_construction.py`)

**Purpose**: Build knowledge graph from resolved entities and relationships

**Process**:

1. Read resolved entities and relationships
2. Resolve relationship conflicts
3. Calculate relationship confidence scores
4. Store final knowledge graph

### 4. Community Detection Stage (`app/stages/community_detection.py`)

**Purpose**: Detect communities and generate hierarchical summaries

**Process**:

1. Build graph from entities and relationships
2. Apply hierarchical Leiden algorithm
3. Generate community summaries using LLM
4. Store community information

## Query Processing

### Query Types

#### 1. Entity Search

- Direct entity lookup by name or type
- Vector similarity search on entity descriptions
- Hybrid search combining text and vector

#### 2. Relationship Traversal

- Graph traversal from source entities
- Multi-hop relationship exploration
- Confidence-weighted path finding

#### 3. Community Retrieval

- Community-based context assembly
- Hierarchical summary retrieval
- Multi-scale context generation

### Query Pipeline

```python
def process_query_with_generation(query: str, db: Database) -> GraphRAGResponse:
    # 1. Extract entities from query
    entities = extract_query_entities(query)

    # 2. Search for entities
    found_entities = entity_search(db, entities)

    # 3. Traverse relationships
    related_entities = relationship_traversal(db, found_entities)

    # 4. Get community summaries
    communities = community_retrieval(db, related_entities)

    # 5. Generate answer
    answer = generate_answer(query, communities)

    return GraphRAGResponse(answer=answer, entities=found_entities, communities=communities)
```

## MongoDB Integration

### Enhanced Query Generation

The system includes advanced MongoDB query generation capabilities:

#### Natural Language to MongoDB Query Conversion

```python
class GraphRAGMongoDBQueryGenerator:
    def generate_entity_search_query(self, context: GraphRAGQueryContext) -> MongoDBQueryResult:
        # Uses LLM to generate optimized MongoDB queries
        # Includes schema awareness and performance optimization
```

#### Query Optimization

```python
class GraphRAGQueryOptimizer:
    def optimize_query(self, query: Dict[str, Any], collection_name: str) -> Dict[str, Any]:
        # Adds early filtering, result limiting, and projection
        # Includes query hints based on available indexes
```

### Index Management

```python
class GraphRAGIndexManager:
    def create_graphrag_indexes(self) -> Dict[str, Any]:
        # Creates all necessary indexes for GraphRAG operations
        # Includes compound, text, sparse, and partial indexes
```

## Performance Optimization

### Indexing Strategy

1. **Compound Indexes**: Multi-field queries
2. **Text Indexes**: Full-text search
3. **Sparse Indexes**: Optional fields
4. **Partial Indexes**: Filtered queries

### Query Optimization

1. **Early Filtering**: Reduce data processing
2. **Result Limiting**: Prevent large result sets
3. **Field Projection**: Limit returned data
4. **Query Hints**: Use appropriate indexes

### Performance Monitoring

```python
class GraphRAGQueryMonitor:
    def analyze_query_performance(self, collection_name: str, query: Dict[str, Any]) -> Dict[str, Any]:
        # Analyzes query execution statistics
        # Provides optimization suggestions
```

## API Reference

### Core Functions

#### `rag_graphrag_answer(query: str, **kwargs) -> Dict[str, Any]`

Generate answer using GraphRAG with optional traditional RAG integration.

**Parameters**:

- `query`: User's query
- `k`: Number of chunks to retrieve (default: 8)
- `filters`: Optional filters for retrieval
- `weights`: Optional weights for reranking
- `streaming`: Whether to stream the answer
- `session_id`: Optional session ID for logging
- `use_traditional_rag`: Whether to combine with traditional RAG results

**Returns**:

```json
{
  "answer": "Generated answer",
  "hits": [...],
  "graphrag_entities": [...],
  "graphrag_communities": [...],
  "confidence": 0.85,
  "processing_time": 1.2,
  "mode": "graphrag"
}
```

#### `rag_hybrid_graphrag_answer(query: str, **kwargs) -> Dict[str, Any]`

Generate answer using both traditional RAG and GraphRAG with weighted combination.

**Parameters**:

- `query`: User's query
- `graphrag_weight`: Weight for GraphRAG vs traditional RAG (0-1, default: 0.7)

#### `get_graphrag_status() -> Dict[str, Any]`

Get the current status of GraphRAG components.

### Pipeline Functions

#### `run_graphrag_pipeline()`

Run the complete GraphRAG pipeline to process all chunks.

#### `create_enhanced_graphrag_pipeline(**config) -> EnhancedGraphRAGPipeline`

Create an enhanced GraphRAG pipeline with advanced features.

## Configuration

### Environment Variables

```bash
# Required
MONGODB_URI=mongodb://localhost:27017
OPENAI_API_KEY=your_openai_api_key
DB_NAME=mongo_hack

# Optional
GRAPH_EXTRACTION_MODEL=gpt-4o-mini
ENTITY_RESOLUTION_MODEL=gpt-4o-mini
COMMUNITY_DETECTION_MODEL=gpt-4o-mini
MAX_CONCURRENT_EXTRACTIONS=15
MAX_CONCURRENT_RESOLUTIONS=10
```

### Configuration Classes

```python
@dataclass
class GraphExtractionConfig(BaseStageConfig):
    model_name: str = "gpt-4o-mini"
    max_entities_per_chunk: int = 10
    max_relationships_per_chunk: int = 15
    min_confidence_threshold: float = 0.5

@dataclass
class EntityResolutionConfig(BaseStageConfig):
    model_name: str = "gpt-4o-mini"
    similarity_threshold: float = 0.8
    max_entities_per_group: int = 50

@dataclass
class GraphConstructionConfig(BaseStageConfig):
    min_relationship_confidence: float = 0.6
    max_relationships_per_entity: int = 20

@dataclass
class CommunityDetectionConfig(BaseStageConfig):
    max_cluster_size: int = 10
    resolution_parameter: float = 1.0
    model_name: str = "gpt-4o-mini"
```

## Testing

### Test Suite

The comprehensive test suite (`test_graphrag_comprehensive.py`) includes:

1. **Pipeline Initialization Test**
2. **Infrastructure Setup Test**
3. **Entity Extraction Test**
4. **Entity Resolution Test**
5. **Graph Construction Test**
6. **Community Detection Test**
7. **Query Processing Test**
8. **MongoDB Query Generation Test**
9. **Performance Optimization Test**
10. **End-to-End Pipeline Test**

### Running Tests

```bash
# Set environment variables
export MONGODB_URI=mongodb://localhost:27017
export OPENAI_API_KEY=your_openai_api_key
export DB_NAME=mongo_hack

# Run comprehensive test suite
python test_graphrag_comprehensive.py
```

### Test Output

```
GraphRAG Comprehensive Test Suite
==================================================

Test Results:
------------------------------
Total Tests: 10
Successful: 10
Failed: 0
Success Rate: 100.00%
Total Execution Time: 45.32s
Average Execution Time: 4.53s

Overall Status: PASS

Recommendations:
--------------------
• All tests passed! GraphRAG implementation is ready for production.
```

## Deployment

### Prerequisites

1. **MongoDB**: Version 4.4+ with Atlas Search support
2. **Python**: Version 3.8+
3. **OpenAI API**: Valid API key with GPT-4 access
4. **Dependencies**: See `requirements.txt`

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run GraphRAG pipeline
python run_graphrag_pipeline.py
```

### Production Considerations

1. **Resource Requirements**:

   - Minimum 8GB RAM for processing
   - SSD storage for MongoDB
   - Stable internet connection for OpenAI API

2. **Scaling**:

   - Use connection pooling for MongoDB
   - Implement rate limiting for OpenAI API
   - Consider distributed processing for large datasets

3. **Monitoring**:
   - Monitor OpenAI API usage and costs
   - Track MongoDB performance metrics
   - Log GraphRAG processing times

## Troubleshooting

### Common Issues

#### 1. OpenAI API Errors

```
Error: OpenAI API rate limit exceeded
```

**Solution**: Implement exponential backoff and rate limiting

#### 2. MongoDB Connection Issues

```
Error: MongoDB connection failed
```

**Solution**: Check connection string and network connectivity

#### 3. Memory Issues

```
Error: Out of memory during processing
```

**Solution**: Reduce batch sizes and increase system memory

#### 4. Index Creation Failures

```
Error: Index creation failed
```

**Solution**: Check MongoDB permissions and disk space

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Performance Issues

1. **Slow Query Processing**:

   - Check index usage with `explain()`
   - Optimize aggregation pipelines
   - Consider query result caching

2. **High Memory Usage**:

   - Reduce batch sizes
   - Implement streaming processing
   - Monitor memory usage patterns

3. **Long Processing Times**:
   - Increase concurrency limits
   - Optimize LLM prompts
   - Use faster models for simple tasks

### Support

For additional support:

1. Check the comprehensive documentation in `GRAPH-RAG.md`
2. Review the test suite for usage examples
3. Monitor logs for detailed error information
4. Check MongoDB and OpenAI API status

## Future Enhancements

### Planned Features

1. **Incremental Updates**: Process new content without full reprocessing
2. **Multi-language Support**: Handle multiple languages in entity extraction
3. **Advanced Community Detection**: Implement more sophisticated algorithms
4. **Real-time Processing**: Stream processing for live content
5. **Graph Visualization**: Web interface for exploring the knowledge graph

### Performance Improvements

1. **Caching Layer**: Redis-based caching for frequent queries
2. **Parallel Processing**: Multi-threaded entity extraction
3. **Model Optimization**: Fine-tuned models for specific domains
4. **Query Optimization**: Advanced MongoDB query optimization

---

This documentation provides a comprehensive guide to the GraphRAG implementation. For specific implementation details, refer to the source code and inline documentation.
