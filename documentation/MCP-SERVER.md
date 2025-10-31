# MCP Server Implementation Guide

This document provides comprehensive documentation for the Model Context Protocol (MCP) server implementation in the GraphRAG Knowledge Manager MCP Server.

## Table of Contents

1. [MCP Server Overview](#mcp-server-overview)
2. [MCP Tools](#mcp-tools)
3. [MCP Resources](#mcp-resources)
4. [MCP Prompts](#mcp-prompts)
5. [Integration Guide](#integration-guide)
6. [Architecture](#architecture)

## MCP Server Overview

### What is the Model Context Protocol?

The Model Context Protocol (MCP) is a standardized protocol that enables AI assistants (like Claude) to interact with external systems and data sources. MCP servers expose:

- **Tools**: Functions that AI assistants can invoke
- **Resources**: Data that AI assistants can read and reference
- **Prompts**: Pre-defined prompt templates for common operations

### How This Server Implements MCP

The GraphRAG Knowledge Manager MCP Server exposes knowledge graph operations, document ingestion, and query processing capabilities via MCP. This allows AI assistants to:

- Query the knowledge graph for entities, relationships, and communities
- Ingest new documents and process them through pipelines
- Retrieve and analyze knowledge graph data
- Generate insights from the knowledge graph structure

### Architecture

```
AI Assistant (Claude, etc.)
    ↓ (MCP Protocol)
MCP Server Layer
    ↓
GraphRAG Pipeline ←→ Ingestion Pipeline
    ↓
MongoDB (Knowledge Graph + Processed Chunks)
```

**Current Status**: MCP server implementation is planned for future development. This document outlines the intended architecture and capabilities.

## MCP Tools

MCP tools are functions that AI assistants can call to interact with the knowledge graph and document processing system.

### Knowledge Graph Query Tools

#### `query_knowledge_graph`

Query the knowledge graph for entities, relationships, and communities.

**Parameters**:

- `query`: Natural language query (e.g., "What are the main topics in machine learning?")
- `query_type`: Type of query ("entity_search", "relationship_traversal", "community_search")
- `limit`: Maximum number of results to return

**Returns**: Entities, relationships, and communities matching the query

**Example**:

```json
{
  "name": "query_knowledge_graph",
  "input": {
    "query": "What entities are related to neural networks?",
    "query_type": "relationship_traversal",
    "limit": 10
  }
}
```

#### `get_entity_details`

Retrieve detailed information about a specific entity.

**Parameters**:

- `entity_id`: Unique identifier for the entity
- `include_relationships`: Whether to include connected entities
- `include_communities`: Whether to include community memberships

**Returns**: Entity details with relationships and community information

#### `get_community_summary`

Get summary and details for a community.

**Parameters**:

- `community_id`: Unique identifier for the community
- `level`: Hierarchy level for hierarchical communities

**Returns**: Community summary, member entities, and coherence metrics

### Document Ingestion Tools

#### `ingest_document`

Ingest a new document into the knowledge graph system.

**Parameters**:

- `source_type`: Document type ("youtube", "pdf", "html", etc.)
- `source_identifier`: Source-specific identifier (video_id, document_id, URL)
- `process_immediately`: Whether to process through ingestion pipeline immediately

**Returns**: Processing status and document identifier

**Example**:

```json
{
  "name": "ingest_document",
  "input": {
    "source_type": "youtube",
    "source_identifier": "dQw4w9WgXcQ",
    "process_immediately": true
  }
}
```

#### `process_document`

Process a document through the ingestion pipeline.

**Parameters**:

- `document_id`: Document identifier
- `stages`: Which stages to run (default: all)
- `options`: Stage-specific options

**Returns**: Processing status and results

### Entity and Relationship Management Tools

#### `create_entity`

Manually create or update an entity in the knowledge graph.

**Parameters**:

- `name`: Entity name
- `type`: Entity type (PERSON, ORGANIZATION, CONCEPT, etc.)
- `description`: Entity description
- `metadata`: Additional metadata

**Returns**: Created entity with ID

#### `create_relationship`

Manually create or update a relationship between entities.

**Parameters**:

- `subject_id`: Source entity ID
- `object_id`: Target entity ID
- `relation_type`: Type of relationship
- `description`: Relationship description
- `confidence`: Confidence score

**Returns**: Created relationship with ID

#### `merge_entities`

Merge multiple entities into a canonical entity.

**Parameters**:

- `entity_ids`: List of entity IDs to merge
- `canonical_name`: Name for the merged entity

**Returns**: Merged entity with ID

### Community Detection and Analysis Tools

#### `detect_communities`

Run community detection on the knowledge graph.

**Parameters**:

- `max_cluster_size`: Maximum size for communities
- `resolution_parameter`: Resolution parameter for Leiden algorithm
- `update_existing`: Whether to update existing communities

**Returns**: Detected communities with summaries

#### `analyze_community_structure`

Analyze the structure and properties of communities.

**Parameters**:

- `community_id`: Community to analyze (optional)
- `metrics`: Metrics to compute (coherence, centrality, etc.)

**Returns**: Analysis results with metrics

## MCP Resources

MCP resources are data sources that AI assistants can read and reference.

### Knowledge Graph Schema

**Resource**: `graphrag://schema/entities`

Schema definition for entities in the knowledge graph.

**Fields**:

- `entity_id`: Unique identifier
- `name`: Entity name
- `canonical_name`: Canonical name (for resolved entities)
- `type`: Entity type
- `description`: Entity description
- `trust_score`: Trust score from source chunks
- `centrality_score`: Graph centrality metric

### Entity Templates

**Resource**: `graphrag://templates/entity`

Template for creating new entities with required and optional fields.

### Relationship Templates

**Resource**: `graphrag://templates/relationship`

Template for creating new relationships with validation rules.

### Community Summaries

**Resource**: `graphrag://communities/{community_id}/summary`

Summary and details for a specific community, including:

- Community members
- Coherence score
- Hierarchical level
- Related communities

### Document Metadata

**Resource**: `graphrag://documents/{document_id}/metadata`

Metadata for processed documents, including:

- Source type and identifier
- Processing status
- Quality scores
- Chunk count

## MCP Prompts

MCP prompts are pre-defined prompt templates for common operations.

### Query Expansion Prompt

**Prompt**: `graphrag://prompts/expand_query`

Expands a user query into structured knowledge graph query components.

**Input**: Natural language query
**Output**: Extracted entities, query intent, suggested query types

**Example**:

```
User query: "What are the relationships between machine learning and deep learning?"
Expanded:
  - Entities: ["machine learning", "deep learning"]
  - Intent: "relationship_traversal"
  - Query type: "relationship_search"
```

### Entity Extraction Prompt

**Prompt**: `graphrag://prompts/extract_entities`

Extract entities from text using LLM with structured output.

**Input**: Text content
**Output**: List of entities with types and descriptions

### Relationship Inference Prompt

**Prompt**: `graphrag://prompts/infer_relationships`

Infer relationships between entities from context.

**Input**: Entity pairs and context
**Output**: Relationship types and descriptions with confidence scores

### Summary Generation Prompt

**Prompt**: `graphrag://prompts/generate_summary`

Generate community or entity summaries.

**Input**: Entity/community data
**Output**: Comprehensive summary text

## Integration Guide

### Connecting to the MCP Server

**From Claude Desktop**:

1. Configure MCP server in Claude Desktop settings
2. Add server endpoint and authentication
3. Restart Claude Desktop

**Configuration Example**:

```json
{
  "mcpServers": {
    "graphrag": {
      "command": "python",
      "args": ["-m", "app.mcp_server"],
      "env": {
        "MONGODB_URI": "...",
        "OPENAI_API_KEY": "..."
      }
    }
  }
}
```

### Using Tools from Claude

Once connected, Claude can use MCP tools directly:

```
User: "Ingest this YouTube video: dQw4w9WgXcQ and tell me about the main entities"
Claude: [Uses ingest_document tool, then queries knowledge graph]
```

### Authentication and Authorization

**Current**: No authentication (development mode)

**Future**:

- API key authentication
- Role-based access control
- Rate limiting per user/client

### Rate Limiting and Quotas

**Planned Limits**:

- Tools: 100 requests per minute
- Resources: 1000 reads per minute
- Prompts: 50 invocations per minute

**Configuration**: Via environment variables or server config

## Architecture

### Server Implementation Pattern

```python
class GraphRAGMCPServer:
    """MCP Server for GraphRAG Knowledge Manager."""

    def __init__(self, db: Database, config: MCPConfig):
        self.db = db
        self.config = config
        self.tools = self._register_tools()
        self.resources = self._register_resources()
        self.prompts = self._register_prompts()

    def _register_tools(self):
        return {
            "query_knowledge_graph": self._tool_query_graph,
            "ingest_document": self._tool_ingest_document,
            # ... more tools
        }

    def _register_resources(self):
        return {
            "graphrag://schema/entities": self._resource_entity_schema,
            # ... more resources
        }
```

### Integration with Pipelines

**Ingestion Pipeline Integration**:

- MCP tools can trigger ingestion pipeline
- Monitor pipeline status via MCP resources
- Retrieve processing results via tools

**GraphRAG Pipeline Integration**:

- Query operations use GraphRAG pipeline services
- Entity/relationship management updates GraphRAG collections
- Community detection triggers GraphRAG pipeline stages

### Error Handling

- **Tool Errors**: Return structured error responses
- **Pipeline Errors**: Surface pipeline errors through MCP
- **Validation Errors**: Validate inputs before processing

## Future Implementation

### Phase 1: Basic MCP Server (Planned)

- Implement MCP protocol handlers
- Register core tools (query, ingest)
- Expose basic resources (schemas)

### Phase 2: Advanced Tools (Planned)

- Entity/relationship management
- Community detection tools
- Advanced query capabilities

### Phase 3: Production Features (Planned)

- Authentication and authorization
- Rate limiting
- Monitoring and logging
- Performance optimization

## See Also

- `documentation/PIPELINE.md` - Pipeline architecture
- `documentation/GRAPH-RAG.md` - GraphRAG implementation
- `documentation/ORCHESTRACTION-INTERFACE.md` - Orchestration patterns
