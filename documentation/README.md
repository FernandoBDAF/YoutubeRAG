# YoutubeRAG Documentation Index

**Project**: GraphRAG Knowledge Manager  
**Architecture**: 4-Layer Clean Architecture (APP/BUSINESS/CORE/DEPENDENCIES)  
**Last Updated**: October 31, 2025

---

## 📚 Quick Navigation

### For LLMs: Layer Context Files

Start here to understand the project structure:

- **[APP Layer](context/app-layer.md)** - External interface (CLIs, UIs, Scripts)
- **[BUSINESS Layer](context/business-layer.md)** - Implementation (Agents, Stages, Services)
- **[CORE Layer](context/core-layer.md)** - Definitions (Models, Base classes, Config)
- **[DEPENDENCIES Layer](context/dependencies-layer.md)** - Infrastructure (DB, LLM, External)

**Dependency Rule**: APP → BUSINESS → CORE → DEPENDENCIES  
(Each layer only depends on layers below)

---

### For Developers: Architecture Documentation

Detailed implementation patterns:

- **[PIPELINE](architecture/PIPELINE.md)** - Pipeline architecture and GraphRAG integration
- **[STAGE](architecture/STAGE.md)** - Stage patterns and lifecycle
- **[AGENT](architecture/AGENT.md)** - Agent patterns and prompts
- **[SERVICE](architecture/SERVICE.md)** - Service architecture
- **[CORE](architecture/CORE.md)** - Core utilities and models

---

### For Users: Guides

How to use and deploy:

- **[EXECUTION](guides/EXECUTION.md)** - Running pipelines and stages
- **[TESTING](guides/TESTING.md)** - Testing strategy and plans
- **[DEPLOYMENT](guides/DEPLOYMENT.md)** - Deployment planning
- **[MCP-SERVER](guides/MCP-SERVER.md)** - MCP server integration
- **[TRACING_LOGGING](guides/TRACING_LOGGING.md)** - Logging and tracing

---

## 🎯 Main Technical Documentation

### GraphRAG Implementation

**Primary Guide**: [GRAPH-RAG-CONSOLIDATED.md](GRAPH-RAG-CONSOLIDATED.md)  
**Length**: 1,447 lines  
**Sections**: 11 complete (Theoretical Foundation, Architecture, Data Model, Pipeline Stages, Post-Processing, Critical Design Decisions, Configuration, Testing, Performance, Utilities, References)

**LinkedIn Articles**: [GRAPHRAG-ARTICLE-GUIDE.md](GRAPHRAG-ARTICLE-GUIDE.md)  
**Length**: 965 lines  
**Articles**: 4 complete (Why GraphRAG, Complete Graph Problem, Random Chunk Testing, Community Detection)

**Configuration Reference**: [GRAPHRAG-CONFIG-REFERENCE.md](GRAPHRAG-CONFIG-REFERENCE.md)  
**Length**: 247 lines  
**Content**: All configuration options documented

---

### Project Documentation

**[PROJECT.md](PROJECT.md)** - Project overview and goals  
**[TECHNICAL-CONCEPTS.md](TECHNICAL-CONCEPTS.md)** - Core concepts explained  
**[USE-CASE.md](USE-CASE.md)** - Use cases and scenarios  
**[BACKLOG.md](BACKLOG.md)** - Project backlog and TODOs  
**[RECENT-UPDATES.md](RECENT-UPDATES.md)** - Recent changes summary

---

### Historical Context

**[REDUNDANCY.md](REDUNDANCY.md)** - Redundancy detection approach  
**[HYBRID-RETRIEVAL.md](HYBRID-RETRIEVAL.md)** - Hybrid search implementation  
**[ORCHESTRACTION-INTERFACE.md](ORCHESTRACTION-INTERFACE.md)** - Orchestration patterns  
**[PROMPTS.md](PROMPTS.md)** - Prompt engineering guide  
**[CHAT.md](CHAT.md)** - Chat interface documentation  
**[DEMO.md](DEMO.md)** - Demo and walkthrough  
**[MIGRATION.md](MIGRATION.md)** - Migration guide

---

## 📦 Archived Documentation

**Location**: [archive/graphrag-implementation/](archive/graphrag-implementation/)

**Purpose**: Historical GraphRAG implementation documentation (Oct 2025)

**Contents**:

- `planning/` - 11 planning and process docs
- `analysis/` - 12 analysis and diagnostic reports
- `testing/` - 3 testing guides and results
- `enhancements/` - 6 implementation details
- **[INDEX.md](archive/graphrag-implementation/INDEX.md)** - Complete archive guide

**Use For**: Understanding design evolution, historical context, problem analyses

**Do NOT Use For**: Current implementation (use GRAPH-RAG-CONSOLIDATED.md instead)

---

## 🗺️ Documentation Map

```
documentation/
├── README.md (this file)                    # Main index
│
├── context/                                 # For LLMs
│   ├── app-layer.md                         # APP layer guide
│   ├── business-layer.md                    # BUSINESS layer guide
│   ├── core-layer.md                        # CORE layer guide
│   └── dependencies-layer.md                # DEPENDENCIES layer guide
│
├── architecture/                            # For developers
│   ├── PIPELINE.md                          # Pipeline patterns
│   ├── STAGE.md                             # Stage patterns
│   ├── AGENT.md                             # Agent patterns
│   ├── SERVICE.md                           # Service patterns
│   └── CORE.md                              # Core utilities
│
├── guides/                                  # For users
│   ├── EXECUTION.md                         # Running the system
│   ├── TESTING.md                           # Testing strategy
│   ├── DEPLOYMENT.md                        # Deployment planning
│   ├── MCP-SERVER.md                        # MCP integration
│   └── TRACING_LOGGING.md                   # Logging guide
│
├── GRAPH-RAG-CONSOLIDATED.md                # Main GraphRAG guide
├── GRAPHRAG-ARTICLE-GUIDE.md                # LinkedIn articles
├── GRAPHRAG-CONFIG-REFERENCE.md             # Configuration reference
│
└── archive/                                 # Historical docs
    └── graphrag-implementation/
        ├── INDEX.md                         # Archive guide
        ├── planning/ (11 files)
        ├── analysis/ (12 files)
        ├── testing/ (3 files)
        └── enhancements/ (6 files)
```

---

## 🎯 How to Use This Documentation

### For New Developers

**1. Start Here**:

- [Main README.md](../README.md) - Project overview
- [PROJECT.md](PROJECT.md) - Goals and vision
- [TECHNICAL-CONCEPTS.md](TECHNICAL-CONCEPTS.md) - Core concepts

**2. Understand Architecture**:

- [context/app-layer.md](context/app-layer.md)
- [context/business-layer.md](context/business-layer.md)
- [context/core-layer.md](context/core-layer.md)
- [context/dependencies-layer.md](context/dependencies-layer.md)

**3. Dive Into Details**:

- [architecture/PIPELINE.md](architecture/PIPELINE.md) - Pipeline flow
- [architecture/STAGE.md](architecture/STAGE.md) - Stage implementation
- [GRAPH-RAG-CONSOLIDATED.md](GRAPH-RAG-CONSOLIDATED.md) - GraphRAG deep-dive

**4. Run the System**:

- [guides/EXECUTION.md](guides/EXECUTION.md) - How to run pipelines
- [../README.md](../README.md) - Quickstart commands

---

### For LLM Assistants

**Quick Layer Understanding**:

1. Read `context/*.md` files (4 files, ~3000 words total)
2. You now understand the entire architecture!

**Finding Code**:

- Need to know where agents are? → `context/business-layer.md`
- Need to understand base classes? → `context/core-layer.md`
- Need to see entry points? → `context/app-layer.md`
- Need database adapters? → `context/dependencies-layer.md`

**Updating Code**:

- Adding new agent? → Check `architecture/AGENT.md` for patterns
- Adding new stage? → Check `architecture/STAGE.md` for patterns
- Adding new service? → Check `architecture/SERVICE.md` for patterns

**GraphRAG Specifics**:

- Full technical guide: `GRAPH-RAG-CONSOLIDATED.md`
- Implementation stories: `GRAPHRAG-ARTICLE-GUIDE.md`
- Configuration options: `GRAPHRAG-CONFIG-REFERENCE.md`

---

### For Historical Context

**Problem Solving**:

- Complete graph problem → `archive/graphrag-implementation/analysis/GRAPHRAG-COMPLETE-GRAPH-ANALYSIS.md`
- Community detection issues → `archive/graphrag-implementation/analysis/GRAPHRAG-COMMUNITY-DIAGNOSIS.md`
- Testing methodology → `archive/graphrag-implementation/testing/RANDOM-CHUNK-TEST-GUIDE.md`

**Design Evolution**:

- See `archive/graphrag-implementation/INDEX.md` for complete timeline
- All 27 historical docs preserved and cataloged

---

## 📖 Documentation Principles

### 1. Layer Isolation

Each layer has its own context file explaining:

- What belongs there
- What doesn't belong there
- Import patterns
- Examples

### 2. Cross-References

- Architecture docs reference main docs
- Main docs reference architecture docs
- Context files reference detailed docs

### 3. LLM-Friendly

- Clear structure
- Standalone context files
- Code examples
- Update guides included

### 4. Preservation of History

- Historical docs archived, not deleted
- Design decisions documented
- Evolution tracked

---

## 🔍 Find Documentation By Topic

### GraphRAG:

- Technical guide → `GRAPH-RAG-CONSOLIDATED.md`
- Articles → `GRAPHRAG-ARTICLE-GUIDE.md`
- Configuration → `GRAPHRAG-CONFIG-REFERENCE.md`
- Historical → `archive/graphrag-implementation/`

### Architecture:

- Layers → `context/` (4 files)
- Components → `architecture/` (5 files)

### Running System:

- Execution → `guides/EXECUTION.md`
- Testing → `guides/TESTING.md`
- Deployment → `guides/DEPLOYMENT.md`

### Concepts:

- Technical concepts → `TECHNICAL-CONCEPTS.md`
- Redundancy → `REDUNDANCY.md`
- Hybrid retrieval → `HYBRID-RETRIEVAL.md`
- Prompts → `PROMPTS.md`

---

## 📝 Contributing to Documentation

### When Adding New Features:

**1. Update Layer Context**:

- Add to appropriate `context/*.md` file
- Update file counts and examples

**2. Update Architecture Docs**:

- Add patterns to `architecture/*.md`
- Include code examples

**3. Update Main Guides**:

- Add to GRAPH-RAG-CONSOLIDATED.md if GraphRAG-related
- Add to PROJECT.md if project-wide

**4. Maintain Cross-References**:

- Link from context → architecture
- Link from architecture → main docs
- Keep navigation clear

---

## 🚀 Quick Links

**Most Important**:

- [GRAPH-RAG-CONSOLIDATED.md](GRAPH-RAG-CONSOLIDATED.md) - Complete GraphRAG guide
- [context/business-layer.md](context/business-layer.md) - Where most code lives
- [guides/EXECUTION.md](guides/EXECUTION.md) - How to run things

**For Architecture Understanding**:

- Start: [context/](context/) - 4 layer guides
- Deep: [architecture/](architecture/) - 5 component guides
- Complete: [GRAPH-RAG-CONSOLIDATED.md](GRAPH-RAG-CONSOLIDATED.md)

**For Problem Solving**:

- Current issues → [BACKLOG.md](BACKLOG.md)
- Historical issues → [archive/graphrag-implementation/](archive/graphrag-implementation/)

---

**Last Updated**: October 31, 2025  
**Documentation Version**: Post-Refactor (4-Layer Architecture)
