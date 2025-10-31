# Core Utilities and Models Guide

**Purpose**: Document core utilities, base classes, and models used throughout the system, with focus on GraphRAG models.

---

## Core Modules

### Base Classes

#### BaseStage

**File**: `core/base_stage.py`

**Purpose**: Abstract base for all pipeline stages.

**Key Methods**:

- `setup()`: Initialize stage
- `iter_docs()`: Provide documents
- `handle_doc(doc)`: Process single document
- `finalize()`: Post-processing and statistics
- `get_collection(name, io, db_name)`: Get collection handle
- `run(config)`: Main entry point

**Used By**: All stage implementations

**Cross-Reference**: See `documentation/STAGE.md` for stage patterns.

---

#### BaseAgent

**File**: `core/base_agent.py`

**Purpose**: Abstract base for LLM-powered agents.

**Provides**: Common LLM interaction patterns, error handling.

**Cross-Reference**: See `documentation/AGENT.md` for agent patterns.

---

### GraphRAG Models

**File**: `core/graphrag_models.py`

**Purpose**: Pydantic models for GraphRAG structured data.

#### Entity Types

```python
class EntityType(str, Enum):
    PERSON = "PERSON"
    ORGANIZATION = "ORGANIZATION"
    TECHNOLOGY = "TECHNOLOGY"
    CONCEPT = "CONCEPT"
    LOCATION = "LOCATION"
    EVENT = "EVENT"
    OTHER = "OTHER"
```

**Usage**: Classify extracted entities for type-aware processing.

---

#### EntityModel

```python
class EntityModel(BaseModel):
    """Entity extracted from text chunk."""
    name: str = Field(description="Name of the entity, capitalized", min_length=1, max_length=200)
    type: EntityType = Field(description="Type of the entity", default=EntityType.OTHER)
    description: str = Field(description="Comprehensive description", min_length=10, max_length=2000)
    confidence: float = Field(description="Confidence score", ge=0.0, le=1.0, default=0.0)

    @field_validator("name")
    @classmethod
    def capitalize_name(cls, value: str) -> str:
        """Ensure entity name is properly capitalized."""
        return value.strip().title()
```

**Used In**: LLM structured output for extraction.

**Validation**: Ensures names are capitalized, descriptions are meaningful, scores are valid.

---

#### RelationshipModel

```python
class RelationshipModel(BaseModel):
    """Relationship between two entities."""
    source_entity: EntityModel
    target_entity: EntityModel
    relation: str = Field(description="Relationship type", min_length=1, max_length=100)
    description: str = Field(description="Relationship explanation", min_length=10, max_length=1000)
    confidence: float = Field(description="Confidence score", ge=0.0, le=1.0, default=0.0)

    @field_validator("relation")
    @classmethod
    def validate_relation(cls, value: str) -> str:
        """Ensure relation is properly formatted."""
        return value.strip().lower()
```

**Used In**: LLM structured output for extraction.

**Validation**: Ensures relationships are well-formed, lowercase predicates.

---

#### KnowledgeModel

```python
class KnowledgeModel(BaseModel):
    """Complete knowledge extraction from chunk."""
    entities: List[EntityModel] = Field(description="All entities in chunk", default_factory=list)
    relationships: List[RelationshipModel] = Field(description="All relationships", default_factory=list)

    @field_validator("entities")
    @classmethod
    def validate_entities(cls, value: List[EntityModel]) -> List[EntityModel]:
        """Ensure at least one entity."""
        if not value:
            raise ValueError("At least one entity must be identified")
        return value
```

**Used In**: GraphExtractionAgent response format.

**Why**: Guarantees we always extract at least one entity per chunk.

---

#### ResolvedEntity

```python
class ResolvedEntity(BaseModel):
    """Canonicalized entity after resolution."""
    entity_id: str = Field(description="Unique ID (MD5 hash)", min_length=32, max_length=32)
    canonical_name: str = Field(description="Canonical name")
    name: str = Field(description="Primary name")
    type: EntityType
    description: str
    confidence: float
    source_count: int = Field(description="Number of source chunks", ge=1)
    resolution_methods: List[str] = Field(default_factory=list)
    aliases: List[str] = Field(default_factory=list)

    @classmethod
    def generate_entity_id(cls, canonical_name: str) -> str:
        """Generate MD5 hash for entity ID."""
        return hashlib.md5(canonical_name.lower().encode()).hexdigest()
```

**Used In**: Entity resolution and storage.

**Key Feature**: ID generation ensures consistency across runs.

**Why MD5**: Deterministic, consistent, collision-resistant for entity names.

---

#### ResolvedRelationship

```python
class ResolvedRelationship(BaseModel):
    """Resolved relationship after canonicalization."""
    relationship_id: str = Field(min_length=32, max_length=32)
    subject_id: str = Field(description="Subject entity ID", min_length=32, max_length=32)
    object_id: str = Field(description="Object entity ID", min_length=32, max_length=32)
    predicate: str
    description: str
    confidence: float
    source_count: int = Field(ge=1)

    @classmethod
    def generate_relationship_id(cls, subject_id: str, object_id: str, predicate: str) -> str:
        """Generate MD5 hash for relationship ID."""
        content = f"{subject_id}:{object_id}:{predicate}".lower()
        return hashlib.md5(content.encode()).hexdigest()
```

**Used In**: Relationship resolution and storage.

**Key Feature**: Composite ID from subject + object + predicate prevents duplicates.

---

#### CommunitySummary

```python
class CommunitySummary(BaseModel):
    """Community summary after detection."""
    community_id: str
    level: int = Field(ge=1, le=10)
    title: str
    summary: str = Field(min_length=50, max_length=5000)
    entities: List[str] = Field(min_length=1)
    entity_count: int = Field(ge=1)
    relationship_count: int = Field(ge=0)
    coherence_score: float = Field(ge=0.0, le=1.0)
```

**Used In**: Community detection and storage.

**Validation**: Ensures level ≥ 1, at least one entity, meaningful summary.

---

### Utility Modules

#### Text Utils

**File**: `core/text_utils.py`

**Purpose**: Text processing utilities.

**Key Functions**:

- Text cleaning
- Normalization
- Tokenization

**Used By**: Clean stage, chunk stage.

---

#### Enrich Utils

**File**: `core/enrich_utils.py`

**Purpose**: Enrichment utilities and normalization.

**Key Functions**:

- `normalize_enrich_payload_for_chunk()`: Normalize enrichment data
- Entity and concept validation

**Used By**: Enrich stage.

---

#### Concurrency

**File**: `core/concurrency.py`

**Purpose**: Concurrency utilities for LLM calls.

**Key Functions**:

- Concurrent LLM processing
- Rate limiting
- Retry logic

**Used By**: Agents that need parallel LLM calls.

---

## GraphRAG Data Flow

```
Chunks (source)
    ↓
[Graph Extraction Stage]
    ↓ (uses core/graphrag_models.py)
Chunks with extraction metadata
    ↓
[Entity Resolution Stage]
    ↓ (generates entity_id via ResolvedEntity.generate_entity_id)
Entities + Entity Mentions collections
    ↓
[Graph Construction Stage]
    ↓ (generates relationship_id via ResolvedRelationship.generate_relationship_id)
Relations collection
    ↓
[Community Detection Stage]
    ↓ (uses CommunitySummary model)
Communities collection
```

**Key Points**:

- Models ensure type safety at each step
- ID generation ensures consistency
- Validation catches errors early

---

## Model Design Principles

### 1. Validation at Boundaries

**Pattern**:

```python
class MyModel(BaseModel):
    field: str = Field(min_length=1, max_length=100)
    score: float = Field(ge=0.0, le=1.0)

    @field_validator("field")
    @classmethod
    def validate_field(cls, value):
        if not value.strip():
            raise ValueError("Field cannot be empty")
        return value.strip()
```

**Why**: Catch bad data from LLM before storage.

---

### 2. Deterministic ID Generation

**Pattern**:

```python
@classmethod
def generate_id(cls, key_data: str) -> str:
    """Generate deterministic ID."""
    return hashlib.md5(key_data.lower().encode()).hexdigest()
```

**Why**: Same entity/relationship gets same ID across runs. Enables deduplication and updates.

---

### 3. Type Safety

**Pattern**: Use Pydantic models for all structured data.

**Benefit**:

- IDE autocomplete
- Type checking
- Validation
- Documentation (Field descriptions)

---

## Configuration Models

**File**: `config/stage_config.py`

**Base Configuration**:

```python
@dataclass
class BaseStageConfig:
    db_name: Optional[str] = None
    read_db_name: Optional[str] = None
    write_db_name: Optional[str] = None
    read_coll: Optional[str] = None
    write_coll: Optional[str] = None
    max: Optional[int] = None
    upsert_existing: bool = False
    video_id: Optional[str] = None
```

**GraphRAG Configs** extend this:

```python
@dataclass
class GraphExtractionConfig(BaseStageConfig):
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.1
    # ... GraphRAG-specific fields
```

**Cross-Reference**: See `config/graphrag_config.py` for all GraphRAG configs.

---

## Cross-Reference

**Main Documentation**: `documentation/GRAPH-RAG-CONSOLIDATED.md`  
**Stage Usage**: `documentation/STAGE.md`  
**Agent Usage**: `documentation/AGENT.md`  
**Service Integration**: `documentation/SERVICE.md`

---

**This document focuses on core utilities and models. For GraphRAG data schemas and validation, see GRAPH-RAG-CONSOLIDATED.md Section 3.**
