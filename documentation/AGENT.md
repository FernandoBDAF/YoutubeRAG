# Agent Architecture and Implementation Guide

**Purpose**: Document all LLM-powered agents, focusing on GraphRAG agents and their prompts, algorithms, and design decisions.

---

## Agent Overview

### What is an Agent?

An **agent** is an LLM-powered component that performs intelligent operations:

- Entity and relationship extraction
- Text summarization and merging
- Entity resolution and canonicalization
- Community summarization
- Link prediction

### BaseAgent Pattern

Agents typically follow this pattern:

```python
class MyAgent:
    def __init__(self, llm_client, model_name="gpt-4o-mini", **kwargs):
        self.llm_client = llm_client
        self.model_name = model_name
        self.system_prompt = """..."""  # Core prompt design

    def process(self, input_data):
        """Main processing method."""
        response = self.llm_client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": format_input(input_data)}
            ]
        )
        return parse_response(response)
```

---

## GraphRAG Agents

### Graph Extraction Agent

**File**: `agents/graph_extraction_agent.py`

**Purpose**: Extract entities and relationships from text chunks using LLM with structured output (Pydantic).

**Key Innovation**: Uses OpenAI's `beta.chat.completions.parse()` for structured output.

```python
class GraphExtractionAgent:
    def __init__(self, llm_client, model_name="gpt-4o-mini", temperature=0.1):
        self.llm_client = llm_client
        self.model_name = model_name
        self.temperature = temperature
        self.system_prompt = """
        You are an expert at extracting entities and relationships from YouTube content.

        ## Instructions:

        1. **Entity Extraction**: Identify all entities and classify:
           - PERSON, ORGANIZATION, TECHNOLOGY, CONCEPT, LOCATION, EVENT, OTHER

        2. **Relationship Extraction**: Extract ALL relationship types:
           - **Multiple Types**: If A relates to B, extract ALL applicable relationships
             Example: "Algorithm uses Data Structure" → 'uses', 'applies_to', 'depends_on'
           - **Hierarchical**: Extract is_a, part_of, subtype_of relationships
           - **Bidirectional**: Consider reverse relationships

        **Goal**: Extract 2-5 relationship types per connected entity pair for rich connectivity.
        """

    def extract_from_chunk(self, chunk):
        """Extract knowledge from chunk."""
        response = self.llm_client.beta.chat.completions.parse(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Text: {chunk['chunk_text']}"}
            ],
            response_format=KnowledgeModel,  # Pydantic model
            temperature=self.temperature
        )

        return response.choices[0].message.parsed
```

**Prompt Evolution**:

**V1**: "Extract relationships between entities"

- Result: ~0.73 relationships per entity (sparse)

**V2** (Current): "Extract ALL relationship types between each entity pair"

- Result: ~1.5-2.0 relationships per entity (richer)
- Added hierarchical, bidirectional, semantic relationships

**Why It Matters**: Initial sparse extraction led to 46 disconnected components. Enhanced prompt improved connectivity.

**Cross-Reference**: See `GRAPH-RAG-CONSOLIDATED.md` Section 4.1

---

### Entity Resolution Agent

**File**: `agents/entity_resolution_agent.py`

**Purpose**: Resolve entities across chunks, merging descriptions for duplicates.

**Algorithm**:

1. Group entities by normalized name (lowercase, stripped)
2. For single occurrence: use as-is
3. For multiple occurrences:
   - Collect all descriptions
   - Use LLM to merge into comprehensive summary
   - Calculate aggregate confidence
   - Track all source chunks

```python
class EntityResolutionAgent:
    def __init__(self, llm_client, model_name="gpt-4o-mini"):
        self.llm_client = llm_client
        self.model_name = model_name
        self.resolution_prompt = """
        You are responsible for creating comprehensive entity summaries.

        Given multiple descriptions of the same entity, create a single summary that:
        - Combines all relevant information
        - Resolves contradictions (choose most accurate)
        - Maintains third-person perspective
        - Focuses on technical and educational aspects (YouTube context)

        Output only the resolved description.
        """

    def resolve_entities(self, extracted_data):
        """Resolve entities across extraction results."""
        # Group by name
        entity_groups = defaultdict(list)
        for data in extracted_data:
            for entity in data['entities']:
                name = entity.name.lower().strip()
                entity_groups[name].append(entity)

        resolved = []
        for name, entities in entity_groups.items():
            if len(entities) == 1:
                resolved_entity = self.create_entity_dict(entities[0])
            else:
                # Merge descriptions via LLM
                descriptions = [e.description for e in entities]
                merged_description = self.resolve_descriptions(descriptions, name)
                resolved_entity = self.create_resolved_entity(entities, merged_description)

            resolved.append(resolved_entity)

        return resolved
```

**Future Enhancements** (from `GRAPHRAG-ENHANCEMENTS.md`):

- Fuzzy string matching (Levenshtein distance)
- Embedding-based similarity
- Abbreviation/acronym handling
- External knowledge base lookup

**Current Limitations**:

- Only exact match (normalized)
- No handling of typos or variations
- No cross-language resolution

**Cross-Reference**: See `GRAPH-RAG-CONSOLIDATED.md` Section 4.2

---

### Relationship Resolution Agent

**File**: `agents/relationship_resolution_agent.py`

**Purpose**: Resolve duplicate relationships, merge descriptions, validate entity existence.

**Key Feature**: Accepts `entity_name_to_id` mapping to ensure relationship IDs are correct MD5 hashes.

```python
class RelationshipResolutionAgent:
    def resolve_relationships(self, extracted_data, entity_name_to_id=None):
        """Resolve relationships across chunks."""
        # Group by (subject, object, predicate) tuple
        relationship_groups = self._group_by_tuple(extracted_data)

        resolved = []
        for key, group in relationship_groups.items():
            if len(group) == 1:
                # Single relationship
                resolved_rel = self.create_from_single(group[0], entity_name_to_id)
            else:
                # Multiple - merge descriptions via LLM
                resolved_rel = self.resolve_multiple(group, entity_name_to_id)

            if resolved_rel:
                resolved.append(resolved_rel)

        return resolved
```

**Key Decision**: Uses entity_name_to_id mapping to convert entity names to their canonical IDs.

**Why**: Relationships must reference entities by their MD5 IDs, not names. This ensures graph integrity.

**Cross-Reference**: See `GRAPH-RAG-CONSOLIDATED.md` Section 4.3

---

### Community Detection Agent

**File**: `agents/community_detection_agent.py`

**Purpose**: Detect communities using graph algorithms.

**Current Algorithm**: hierarchical_leiden  
**Issue**: Creates single-entity communities for our graphs  
**Solution**: Switch to Louvain (Monday)

```python
class CommunityDetectionAgent:
    def detect_communities(self, entities, relationships):
        """Detect communities using Leiden algorithm."""
        # Build NetworkX graph with edge weights
        G = self._create_networkx_graph(entities, relationships)

        # Run algorithm
        try:
            communities = hierarchical_leiden(G, max_cluster_size=50)
        except:
            communities = self._fallback_community_detection(G)

        # Filter and organize
        organized = self._organize_by_level(communities, entities, relationships)

        return organized
```

**Edge Weights** (Critical feature):

```python
def _create_networkx_graph(self, entities, relationships):
    G = nx.Graph()

    for entity in entities:
        G.add_node(entity.entity_id, **entity.dict())

    for rel in relationships:
        # Calculate weight by type
        base_conf = rel.confidence
        rel_type = getattr(rel, "relationship_type", None)

        if rel_type == "co_occurrence":
            weight = base_conf  # 0.7
        elif rel_type == "semantic_similarity":
            weight = base_conf * 0.8  # Slight penalty
        elif rel_type == "cross_chunk":
            weight = base_conf * 0.5  # 50% penalty
        elif rel_type == "predicted":
            weight = base_conf * 0.4  # 60% penalty
        else:  # LLM-extracted
            weight = base_conf  # Full weight

        G.add_edge(rel.subject_id, rel.object_id, weight=weight)

    return G
```

**Why Edge Weights Matter**: Communities form around high-quality (LLM) relationships, not auto-generated noise.

**Cross-Reference**: See `GRAPH-RAG-CONSOLIDATED.md` Sections 4.4, 6.3

---

### Community Summarization Agent

**File**: `agents/community_summarization_agent.py`

**Purpose**: Generate LLM summaries for each community.

```python
class CommunitySummarizationAgent:
    def __init__(self, llm_client, model_name="gpt-4o-mini"):
        self.llm_client = llm_client
        self.system_prompt = """
        You are an expert at summarizing communities of related entities.

        Given entities and relationships, create a comprehensive summary that captures:
        - Main themes and concepts
        - Key relationships and interactions
        - Important details and context
        - Overall significance

        Be concise but thorough. Focus on the most important information.
        """

    def summarize_community(self, entities, relationships):
        """Generate summary for a community."""
        # Format entities and relationships
        entities_text = format_entities(entities)
        relationships_text = format_relationships(relationships)

        # Generate summary
        response = self.llm_client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Entities:\n{entities_text}\n\nRelationships:\n{relationships_text}"}
            ]
        )

        return response.choices[0].message.content
```

**Performance**: ~10-20 seconds per community (LLM call).

---

### Graph Link Prediction Agent

**File**: `agents/graph_link_prediction_agent.py`

**Purpose**: Predict missing relationships using graph structure and embeddings.

**Two Strategies**:

1. **Structural Prediction** (Adamic-Adar):

```python
def _predict_via_common_neighbors(self, G):
    """Predict links based on common neighbors."""
    non_edges = list(nx.non_edges(G))
    aa_scores = nx.adamic_adar_index(G, non_edges[:1000])

    predictions = []
    for u, v, score in aa_scores:
        if score > 0.5:
            confidence = min(0.9, score / 10)
            predicate = infer_predicate(u_type, v_type)
            predictions.append((u, v, predicate, confidence))

    return predictions
```

2. **Semantic Prediction** (Embeddings):

```python
def _predict_via_embeddings(self, entities, G):
    """Predict links based on entity embedding similarity."""
    for entity in entities:
        # Find most similar entities without existing connections
        existing_neighbors = set(G.neighbors(entity.entity_id))

        similarities = []
        for other_entity in entities:
            if other_entity.entity_id in existing_neighbors:
                continue

            similarity = cosine_similarity(entity.embedding, other_entity.embedding)
            if similarity >= threshold:
                similarities.append((other_entity.entity_id, similarity))

        # Top N predictions per entity
        top_similar = sorted(similarities, reverse=True)[:max_predictions]
        # ... create predictions
```

**Current Issue**: Predictions have `source_count=0`, fails MongoDB validation (requires ≥1).

**Fix Needed**: Set `source_count=1` instead of `0`.

**Cross-Reference**: See `GRAPH-RAG-CONSOLIDATED.md` Section 5.5, 10.2

---

## Non-GraphRAG Agents (Brief Reference)

### Clean Agent

**File**: `agents/clean_agent.py`  
**Purpose**: LLM-powered transcript cleaning  
**Used In**: Ingestion pipeline

### Enrich Agent

**File**: `agents/enrich_agent.py`  
**Purpose**: Entity/concept extraction, tag generation  
**Used In**: Ingestion pipeline  
**Note**: Redundant with GraphRAG extraction but provides initial signals

### Trust Agent

**File**: `agents/trust_agent.py`  
**Purpose**: LLM validation for borderline trust cases  
**Used In**: Trust stage  
**GraphRAG Integration**: Trust scores propagate to graph entities

---

## Prompt Engineering Patterns

### Structured Output (GraphRAG)

**Use**: When you need predictable, parseable output

**Pattern**:

```python
from pydantic import BaseModel

class MyModel(BaseModel):
    field1: str
    field2: List[str]

response = llm_client.beta.chat.completions.parse(
    model="gpt-4o-mini",
    messages=[...],
    response_format=MyModel
)

result = response.choices[0].message.parsed  # Validated Pydantic object
```

**Used In**: GraphExtractionAgent (KnowledgeModel)

**Why**: Eliminates parsing errors, type-safe, validation built-in.

---

### Free-Form Text (Summarization)

**Use**: When you need natural language output

**Pattern**:

```python
response = llm_client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
)

text = response.choices[0].message.content
```

**Used In**: EntityResolutionAgent, CommunitySummarizationAgent

**Why**: Flexible, natural, good for descriptions and summaries.

---

## Prompt Design Principles

### 1. Be Specific About Output Format

**Bad**:

```
Extract entities from the text.
```

**Good**:

```
Extract all entities and classify them into these types:
- PERSON: People, individuals, characters
- TECHNOLOGY: Software, tools, frameworks
...

For each entity, provide:
- Name (capitalized)
- Type (from list above)
- Comprehensive description (2-3 sentences)
- Confidence score (0.0-1.0)
```

### 2. Encourage Thoroughness

GraphRAG extraction prompt:

```
Extract ALL relationship types between each entity pair.
Goal: Extract 2-5 relationship types per connected entity pair.
```

**Why**: Initial prompt only extracted primary relationships. Enhanced prompt increased from 0.73 to ~1.5-2.0 relationships per entity.

### 3. Provide Context

For YouTube-specific content:

```
4. **YouTube Content Considerations**:
   - Focus on technical content, tutorials, and educational material
   - Extract technology stacks, programming concepts, and tools
   - Identify people mentioned (instructors, developers, experts)
```

**Why**: Tailors extraction to domain, improves quality.

---

## Agent Configuration

Agents are typically configured via stage configs:

```python
@dataclass
class GraphExtractionConfig(BaseStageConfig):
    model_name: str = "gpt-4o-mini"  # Agent uses this
    temperature: float = 0.1          # Agent uses this
    max_retries: int = 3              # Agent retry logic
    retry_delay: float = 1.0          # Backoff between retries
```

Agents receive these via constructor:

```python
agent = GraphExtractionAgent(
    llm_client=llm_client,
    model_name=config.model_name,
    temperature=config.temperature,
    max_retries=config.llm_retries
)
```

---

## Error Handling

Agents implement retry logic:

```python
for attempt in range(max_retries):
    try:
        response = self.llm_client.chat.completions.create(...)
        return response.choices[0].message.parsed
    except Exception as e:
        logger.error(f"Attempt {attempt + 1} failed: {e}")
        if attempt < max_retries - 1:
            time.sleep(retry_delay)
        else:
            raise
```

**Why**: LLM calls can fail (rate limits, timeouts, API errors). Retries make agents resilient.

---

## Cross-Reference

**Main Documentation**: `documentation/GRAPH-RAG-CONSOLIDATED.md`  
**Stage Integration**: `documentation/STAGE.md`  
**Models**: `documentation/CORE.md`  
**Configuration**: `config/graphrag_config.py`

---

**This document focuses on agent architecture. For GraphRAG implementation details and prompt evolution stories, see GRAPH-RAG-CONSOLIDATED.md Sections 4-6.**
