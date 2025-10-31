# GraphRAG Quick Start Guide

## Overview

This guide will help you get started with the GraphRAG implementation in the YouTubeRAG project. GraphRAG enhances traditional RAG by creating a knowledge graph from video content and using graph-based retrieval for more comprehensive answers.

## Prerequisites

- Python 3.8+
- MongoDB 4.4+ (with Atlas Search support)
- OpenAI API key with GPT-4 access
- Processed video chunks in MongoDB

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
export MONGODB_URI="mongodb://localhost:27017"
export OPENAI_API_KEY="your_openai_api_key"
export DB_NAME="mongo_hack"
```

### 3. Verify MongoDB Connection

```python
from pymongo import MongoClient

client = MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("DB_NAME")]
print(f"Connected to database: {db.name}")
```

## Quick Start

### 1. Run GraphRAG Pipeline

Process your video chunks to build the knowledge graph:

```python
from app.pipelines.graphrag_pipeline import run_graphrag_pipeline

# Run the complete GraphRAG pipeline
run_graphrag_pipeline()
```

This will:

- Extract entities and relationships from chunks
- Resolve and canonicalize entities
- Build the knowledge graph
- Detect communities and generate summaries

### 2. Query with GraphRAG

Use GraphRAG to answer questions:

```python
from app.services.rag import rag_graphrag_answer

# Simple GraphRAG query
response = rag_graphrag_answer("What is machine learning?")
print(response["answer"])

# GraphRAG with traditional RAG integration
response = rag_graphrag_answer(
    "How are neural networks related to deep learning?",
    use_traditional_rag=True
)
print(response["answer"])
```

### 3. Hybrid GraphRAG Query

Combine GraphRAG and traditional RAG:

```python
from app.services.rag import rag_hybrid_graphrag_answer

response = rag_hybrid_graphrag_answer(
    "What are the main AI concepts discussed?",
    graphrag_weight=0.7  # 70% GraphRAG, 30% traditional RAG
)
print(response["answer"])
```

## Advanced Usage

### 1. Enhanced GraphRAG Pipeline

Use the enhanced pipeline with advanced features:

```python
from app.services.enhanced_graphrag_pipeline import create_enhanced_graphrag_pipeline

# Create enhanced pipeline
pipeline = create_enhanced_graphrag_pipeline(
    mongodb_uri=os.getenv("MONGODB_URI"),
    database_name=os.getenv("DB_NAME"),
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    enable_natural_language_queries=True,
    enable_query_optimization=True,
    enable_performance_monitoring=True
)

# Process query with enhanced features
response = pipeline.process_query_with_enhanced_generation(
    "What are the relationships between AI concepts?",
    use_natural_language_queries=True,
    include_performance_analysis=True
)

print(f"Answer: {response['answer']}")
print(f"Entities: {len(response['entities'])}")
print(f"Communities: {len(response['communities'])}")
print(f"Processing time: {response['total_processing_time']:.2f}s")
```

### 2. Custom Configuration

Customize the GraphRAG pipeline:

```python
from app.core.graphrag_config import (
    GraphExtractionConfig,
    EntityResolutionConfig,
    GraphConstructionConfig,
    CommunityDetectionConfig
)

# Custom configuration
extraction_config = GraphExtractionConfig(
    model_name="gpt-4o-mini",
    max_entities_per_chunk=15,
    max_relationships_per_chunk=20,
    min_confidence_threshold=0.6
)

resolution_config = EntityResolutionConfig(
    model_name="gpt-4o-mini",
    similarity_threshold=0.85,
    max_entities_per_group=100
)

# Use custom configuration in pipeline
# (Configuration is applied when running the pipeline)
```

### 3. MongoDB Query Generation

Use advanced MongoDB query generation:

```python
from app.services.graphrag_mongodb_query import (
    GraphRAGMongoDBQueryGenerator,
    GraphRAGQueryContext
)

# Initialize query generator
query_generator = GraphRAGMongoDBQueryGenerator(llm_client, db)

# Create query context
context = GraphRAGQueryContext(
    user_query="Find information about machine learning",
    extracted_entities=["machine learning", "ML"],
    query_intent="entity_search",
    collections_involved=["entities", "relations"],
    performance_requirements={"max_execution_time_ms": 5000}
)

# Generate optimized MongoDB query
query_result = query_generator.generate_entity_search_query(context)
print(f"Generated query: {query_result.query}")
print(f"Confidence: {query_result.confidence}")
print(f"Performance hints: {query_result.performance_hints}")
```

## Testing

### Run Comprehensive Tests

```bash
python test_graphrag_comprehensive.py
```

### Test Individual Components

```python
# Test entity extraction
from agents.graph_extraction_agent import GraphExtractionAgent

agent = GraphExtractionAgent(llm_client)
result = agent.extract_from_chunk({
    "text": "Machine learning is a subset of artificial intelligence.",
    "chunk_id": "test_chunk"
})
print(f"Extracted entities: {len(result.entities)}")
print(f"Extracted relationships: {len(result.relationships)}")

# Test entity resolution
from agents.entity_resolution_agent import EntityResolutionAgent

resolver = EntityResolutionAgent(llm_client)
resolved_entities = resolver.resolve_entities([result])
print(f"Resolved entities: {len(resolved_entities)}")
```

## Monitoring and Debugging

### 1. Check GraphRAG Status

```python
from app.services.rag import get_graphrag_status

status = get_graphrag_status()
print(f"GraphRAG enabled: {status['graphrag_enabled']}")
print(f"Collections: {status['collections']}")
print(f"Pipeline status: {status['pipeline_status']}")
```

### 2. Monitor Performance

```python
from app.services.graphrag_mongodb_query import GraphRAGQueryMonitor

monitor = GraphRAGQueryMonitor(db)
analysis = monitor.analyze_query_performance("entities", {"name": "machine learning"})
print(f"Execution time: {analysis['execution_time_ms']}ms")
print(f"Documents examined: {analysis['documents_examined']}")
print(f"Optimization suggestions: {analysis['optimization_suggestions']}")
```

### 3. Enable Debug Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Your GraphRAG code here
```

## Common Use Cases

### 1. Educational Content Analysis

```python
# Analyze educational content
response = rag_graphrag_answer(
    "What are the main concepts taught in this course?",
    filters={"video_category": "education"}
)
```

### 2. Technical Documentation

```python
# Technical documentation queries
response = rag_graphrag_answer(
    "How do I implement a neural network?",
    filters={"video_category": "tutorial"}
)
```

### 3. Research and Analysis

```python
# Research queries
response = rag_hybrid_graphrag_answer(
    "What are the latest trends in AI research?",
    graphrag_weight=0.8
)
```

## Troubleshooting

### Common Issues

1. **OpenAI API Rate Limits**

   ```python
   # Implement retry logic
   import time

   def query_with_retry(query_func, max_retries=3):
       for attempt in range(max_retries):
           try:
               return query_func()
           except Exception as e:
               if "rate limit" in str(e).lower():
                   time.sleep(2 ** attempt)  # Exponential backoff
                   continue
               raise
   ```

2. **MongoDB Connection Issues**

   ```python
   # Check connection
   from pymongo import MongoClient

   try:
       client = MongoClient(os.getenv("MONGODB_URI"), serverSelectionTimeoutMS=5000)
       client.server_info()
       print("MongoDB connection successful")
   except Exception as e:
       print(f"MongoDB connection failed: {e}")
   ```

3. **Memory Issues**
   ```python
   # Reduce batch sizes
   config = GraphExtractionConfig(
       max_entities_per_chunk=5,  # Reduce from default 10
       max_relationships_per_chunk=8  # Reduce from default 15
   )
   ```

### Performance Tips

1. **Optimize Indexes**

   ```python
   from app.services.graphrag_indexes import create_graphrag_indexes

   # Create optimized indexes
   create_graphrag_indexes(db)
   ```

2. **Use Caching**

   ```python
   # Cache frequent queries
   from functools import lru_cache

   @lru_cache(maxsize=100)
   def cached_entity_search(entity_name):
       return entity_search(db, [entity_name])
   ```

3. **Monitor Resource Usage**

   ```python
   import psutil

   def check_resources():
       print(f"CPU usage: {psutil.cpu_percent()}%")
       print(f"Memory usage: {psutil.virtual_memory().percent}%")
   ```

## Next Steps

1. **Explore the Knowledge Graph**: Use MongoDB queries to explore the generated knowledge graph
2. **Customize Extraction**: Modify entity extraction prompts for your specific domain
3. **Optimize Performance**: Monitor and optimize query performance based on your usage patterns
4. **Scale Up**: Consider distributed processing for large datasets
5. **Integrate**: Integrate GraphRAG into your existing applications

## Resources

- [Comprehensive Documentation](GRAPH-RAG-IMPLEMENTATION.md)
- [GraphRAG Research Paper](https://arxiv.org/abs/2401.15841)
- [MongoDB Atlas Search Documentation](https://docs.atlas.mongodb.com/atlas-search/)
- [OpenAI API Documentation](https://platform.openai.com/docs)

---

For more detailed information, refer to the comprehensive documentation in `GRAPH-RAG-IMPLEMENTATION.md`.
