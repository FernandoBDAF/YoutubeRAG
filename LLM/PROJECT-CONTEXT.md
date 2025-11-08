# PROJECT CONTEXT

**Purpose**: This document provides essential project knowledge for LLMs starting new sessions. It covers project structure, domain knowledge, conventions, architecture, and related work to ensure LLMs have sufficient context for both functional and procedural correctness.

**Last Updated**: 2025-11-08  
**Maintained By**: Methodology team

---

## 📋 Project Overview

**Project Name**: YoutubeRAG  
**Purpose**: GraphRAG pipeline for YouTube video analysis and knowledge extraction  
**Core Technology Stack**:
- Python 3.x
- MongoDB (database)
- OpenAI API (LLM)
- GraphRAG (knowledge graph construction)
- Streamlit (UI)

**Main Use Cases**:
- Ingest YouTube videos (transcription, chunking)
- Extract entities and relationships (entity resolution)
- Build knowledge graph (GraphRAG)
- Query knowledge graph (RAG chat interface)
- Analyze video insights (statistics, quality metrics)

---

## 🏗️ Project Structure

### Key Directories

**`app/`**: Application layer (CLI, API, UI)
- `cli/`: Command-line interface
- `api/`: REST API endpoints
- `ui/`: Streamlit UI
- `scripts/`: Utility scripts

**`business/`**: Business logic layer
- `agents/`: Agent implementations (graphrag, ingestion, rag)
- `chat/`: Chat functionality (answering, memory, query rewriting, retrieval)
- `pipelines/`: Pipeline orchestration (graphrag, ingestion, runner)
- `queries/`: Query implementations (get, llm_question, vector_search, videos_insights)
- `services/`: Service layer (chat, graphrag, ingestion, rag)
- `stages/`: Pipeline stages (graphrag, ingestion)

**`core/`**: Core domain and infrastructure
- `base/`: Base classes (agent, stage)
- `config/`: Configuration (graphrag, paths, runtime)
- `domain/`: Domain models (compression, concurrency, enrichment, text)
- `libraries/`: Reusable libraries (caching, concurrency, configuration, context, data_transform, database, di, error_handling, feature_flags, health, llm, logging, metrics, rate_limiting, retry, serialization, tracing, validation)
- `models/`: Data models (config, graphrag)

**`dependencies/`**: External dependencies
- `database/`: MongoDB integration
- `external/`: External service integrations
- `llm/`: LLM integrations (OpenAI, rate limiting)
- `observability/`: Logging and observability

**`LLM/`**: LLM methodology and automation
- `protocols/`: Entry/exit protocols (START_POINT, END_POINT, RESUME, etc.)
- `templates/`: Document templates (PLAN, SUBPLAN, EXECUTION_TASK, PROMPTS)
- `guides/`: Methodology guides (FOCUS-RULES, GRAMMAPLAN-GUIDE, etc.)
- `scripts/`: Automation scripts organized by domain:
  - `validation/`: Validation scripts (check_plan_size, validate_achievement_completion, etc.)
  - `generation/`: Prompt generation scripts (generate_prompt, generate_pause_prompt, etc.)
  - `archiving/`: Archiving scripts (archive_completed.py)

**`documentation/`**: Project documentation
- `archive/`: Completed work archives
- `architecture/`: Architecture documentation
- `guides/`: User guides
- `examples/`: Code examples

**`tests/`**: Test suite
- Organized by layer (app/, business/, core/, dependencies/)

### File Organization Patterns

**Layered Architecture**: Code organized by layer (app → business → core → dependencies)

**Domain-Based Organization**: Business logic organized by domain (agents, chat, pipelines, queries, services, stages)

**Script Organization**: LLM scripts organized by domain (validation/, generation/, archiving/)

### Naming Conventions

**Files**:
- Python files: `snake_case.py`
- Markdown files: `kebab-case.md` (e.g., `PLAN_FILE-MOVING-OPTIMIZATION.md`)
- PLAN files: `PLAN_FEATURE-NAME.md`
- SUBPLAN files: `SUBPLAN_FEATURE-NAME_XX.md` (XX = achievement number)
- EXECUTION_TASK files: `EXECUTION_TASK_FEATURE-NAME_XX_YY.md` (XX = achievement, YY = execution number)

**Directories**:
- Lowercase with underscores: `business/`, `core/`, `dependencies/`
- Uppercase for methodology: `LLM/`

**Classes**:
- PascalCase: `GraphRAGAgent`, `IngestionPipeline`

**Functions/Variables**:
- snake_case: `extract_entities`, `build_knowledge_graph`

---

## 🧠 Domain Knowledge

### Core Domain Concepts

**GraphRAG**: Knowledge graph-based retrieval augmented generation. Builds a knowledge graph from video transcripts, then uses it for RAG queries.

**Entity Resolution**: Process of identifying and merging duplicate entities (people, places, concepts) across different video transcripts.

**Ingestion Pipeline**: Multi-stage pipeline that processes YouTube videos:
1. Video download and transcription
2. Text chunking and compression
3. Entity and relationship extraction
4. Knowledge graph construction
5. Vector embedding generation

**RAG (Retrieval Augmented Generation)**: Query system that retrieves relevant context from knowledge graph and vector store, then generates answers using LLM.

### Key Terminology

**Entities**: People, places, organizations, concepts mentioned in videos

**Relationships**: Connections between entities (e.g., "person X works at company Y")

**Knowledge Graph**: Graph structure representing entities and relationships

**Vector Store**: Embedding-based search index for semantic similarity

**Chunking**: Breaking long text into smaller, manageable pieces

**Compression**: Reducing text size while preserving key information

### Business Logic Overview

**Pipeline Stages**:
1. **Ingestion**: Download videos, transcribe, chunk, compress
2. **Extraction**: Extract entities and relationships
3. **GraphRAG**: Build knowledge graph, generate embeddings
4. **Chat**: Query knowledge graph and vector store, generate answers

**Agent Pattern**: Agents orchestrate work across services and stages

**Service Pattern**: Services encapsulate business logic and coordinate with dependencies

**Stage Pattern**: Stages represent pipeline steps with clear inputs/outputs

---

## 📐 Conventions

### Code Style

**Python**:
- Follow PEP 8
- Type hints where helpful
- Docstrings for public functions/classes
- Use f-strings for string formatting

**Error Handling**:
- Use custom exception classes (in `core/libraries/error_handling/`)
- Log errors with context
- Provide actionable error messages

**Logging**:
- Use structured logging (in `core/libraries/logging/`)
- Include context (request ID, user ID, etc.)
- Log at appropriate levels (DEBUG, INFO, WARNING, ERROR)

### Documentation Standards

**Markdown**:
- Use clear headings and structure
- Include code examples where helpful
- Link to related documents

**Templates**:
- Follow templates in `LLM/templates/`
- Use consistent structure across documents
- Include required sections

**Comments**:
- Explain "why" not "what"
- Update comments when code changes
- Remove outdated comments

### Testing Approaches

**Unit Tests**:
- Test individual functions/classes
- Use mocks for external dependencies
- Aim for high coverage

**Integration Tests**:
- Test component interactions
- Use test database/LLM
- Verify end-to-end flows

**Test Organization**:
- Mirror source structure in `tests/`
- One test file per source file
- Clear test names

### Methodology Conventions (LLM-Specific)

**PLAN Documents**:
- One PLAN per feature/initiative
- Hard limit: 600 lines or 32 hours
- Must include: Achievements, Subplan Tracking, Current Status & Handoff, Archive Location

**SUBPLAN Documents**:
- One SUBPLAN per achievement
- Size: 200-400 lines
- Must include: Objective, Deliverables, Approach, Tests, Expected Results

**EXECUTION_TASK Documents**:
- One EXECUTION_TASK per execution attempt
- Hard limit: 200 lines
- Must include: Iteration Log, Learning Summary, Completion Status

**Archiving**:
- Archive location: `documentation/archive/FEATURE-NAME/`
- Archive structure: `subplans/` and `execution/` subdirectories
- Deferred archiving: Archive at achievement completion (not immediately)

**Validation**:
- Run validation scripts before marking complete
- Fix issues before proceeding
- Use blocking validation for critical checks

**Focus Rules**:
- Read only relevant sections (not full documents)
- Stay within context budget
- Follow focus rules in `LLM/guides/FOCUS-RULES.md`

---

## 🏛️ Architecture

### High-Level Architecture

**Layered Architecture**:
```
app/ (Presentation Layer)
  ↓
business/ (Business Logic Layer)
  ↓
core/ (Domain & Infrastructure Layer)
  ↓
dependencies/ (External Dependencies Layer)
```

**Key Principles**:
- Separation of concerns (each layer has clear responsibility)
- Dependency inversion (dependencies point inward)
- Domain-driven design (business logic in business/ layer)

### Key Components

**Agents** (`business/agents/`):
- Orchestrate work across services and stages
- Handle high-level workflows
- Coordinate pipeline execution

**Services** (`business/services/`):
- Encapsulate business logic
- Coordinate with dependencies
- Provide reusable functionality

**Stages** (`business/stages/`):
- Represent pipeline steps
- Have clear inputs/outputs
- Can be composed into pipelines

**Pipelines** (`business/pipelines/`):
- Compose stages into workflows
- Handle orchestration
- Manage state and errors

**Libraries** (`core/libraries/`):
- Reusable infrastructure
- Cross-cutting concerns (logging, metrics, caching, etc.)
- Domain-agnostic utilities

### Component Relationships

**Agent → Service → Stage → Pipeline**:
- Agents call services
- Services use stages
- Stages are composed into pipelines

**Service → Dependency**:
- Services depend on external dependencies (database, LLM, etc.)
- Dependencies are injected (dependency inversion)

**Library → All Layers**:
- Libraries used across all layers
- Provide cross-cutting functionality

### Data Flow Patterns

**Ingestion Flow**:
```
Video → Transcription → Chunking → Compression → Extraction → GraphRAG → Storage
```

**Query Flow**:
```
Query → Query Rewriter → Vector Search → Graph Search → Context Assembly → LLM → Answer
```

**Pipeline Pattern**:
- Sequential stages with clear inputs/outputs
- Error handling at each stage
- State passed between stages

---

## 🔗 Related Work

### Active/Paused PLANs

**Active**:
- `PLAN_METHODOLOGY-VALIDATION.md`: Validating LLM development methodology
- `PLAN_NEW-SESSION-CONTEXT-ENHANCEMENT.md`: Enhancing context system for new sessions
- `PLAN_FILE-MOVING-OPTIMIZATION.md`: Optimizing file moving operations

**Paused**:
- `PLAN_METHODOLOGY-V2-ENHANCEMENTS.md`: Methodology improvements (paused at Achievement 6.1)
- `PLAN_API-REVIEW-AND-TESTING.md`: API review and testing (paused at Achievement 3.3)

### Recent Major Changes

**Methodology Enhancements** (Nov 2025):
- Plan size limits (600 lines / 32 hours)
- EXECUTION_TASK size limits (200 lines)
- Tree hierarchy focus rules
- Deferred archiving policy
- Component registration system
- Session entry points
- Automated prompt generation

**Context Gap Fixes** (Nov 2025):
- Enhanced PLAN context sections
- Created PROJECT-CONTEXT.md (this document)
- Updated prompt generator with project context injection

### Important Analysis Documents

**Methodology Analysis**:
- `EXECUTION_ANALYSIS_METHODOLOGY-GAP-ANALYSIS.md`: Gaps in methodology implementation
- `EXECUTION_ANALYSIS_FILE-MOVING-PERFORMANCE.md`: File moving performance analysis
- `EXECUTION_ANALYSIS_NEW-SESSION-CONTEXT-GAP.md`: New session context gap analysis

**Implementation Analysis**:
- `EXECUTION_ANALYSIS_PROMPT-GENERATOR-0.1-BUG.md`: Prompt generator bug analysis
- `EXECUTION_ANALYSIS_NEW-SESSION-WORK-REVIEW.md`: New session work review

### Key Methodology Documents

**Guides**:
- `LLM-METHODOLOGY.md`: Main methodology reference
- `LLM/guides/FOCUS-RULES.md`: Focus rules for context management
- `LLM/guides/GRAMMAPLAN-GUIDE.md`: Guide for GrammaPlan decisions

**Protocols**:
- `LLM/protocols/IMPLEMENTATION_START_POINT.md`: Starting new work
- `LLM/protocols/IMPLEMENTATION_END_POINT.md`: Completing work
- `LLM/protocols/IMPLEMENTATION_RESUME.md`: Resuming paused work

**Templates**:
- `LLM/templates/PLAN-TEMPLATE.md`: PLAN document template
- `LLM/templates/SUBPLAN-TEMPLATE.md`: SUBPLAN document template
- `LLM/templates/EXECUTION_TASK-TEMPLATE.md`: EXECUTION_TASK document template

---

## 📚 Quick Reference

### Where to Find Things

**Methodology Files**: `LLM/` directory
**Project Code**: `app/`, `business/`, `core/`, `dependencies/`
**Documentation**: `documentation/` directory
**Archives**: `documentation/archive/`
**Tests**: `tests/` directory

### Common Tasks

**Starting New Work**:
1. Read `LLM-METHODOLOGY.md`
2. Read `LLM/protocols/IMPLEMENTATION_START_POINT.md`
3. Create PLAN following `LLM/templates/PLAN-TEMPLATE.md`

**Resuming Work**:
1. Read PLAN "Current Status & Handoff" section
2. Read `LLM/protocols/IMPLEMENTATION_RESUME.md`
3. Generate resume prompt using `generate_resume_prompt.py`

**Completing Work**:
1. Verify all deliverables exist
2. Run validation scripts
3. Archive SUBPLANs and EXECUTION_TASKs
4. Update PLAN statistics
5. Read `LLM/protocols/IMPLEMENTATION_END_POINT.md`

**Generating Prompts**:
- Use `LLM/scripts/generation/generate_prompt.py` for execution prompts
- Use `LLM/scripts/generation/generate_pause_prompt.py` for pause prompts
- Use `LLM/scripts/generation/generate_resume_prompt.py` for resume prompts
- Use `LLM/scripts/generation/generate_verify_prompt.py` for verification prompts

---

**Last Updated**: 2025-11-08  
**Version**: 1.0


