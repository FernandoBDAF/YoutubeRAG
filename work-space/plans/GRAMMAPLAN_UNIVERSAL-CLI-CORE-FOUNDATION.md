# GRAMMAPLAN: Universal CLI Core Foundation

**Status**: 📋 Strategic Planning  
**Created**: 2025-11-08 18:00 UTC  
**Strategic Goal**: Build the foundational infrastructure for universal methodology management - core engine, terminal CLI, API server, and plugin system  
**Priority**: CRITICAL - Foundation for Entire Platform  
**Total Estimated Effort**: 40-60 hours (4 child PLANs)

**Parent North Star**: `NORTH_STAR_UNIVERSAL-METHODOLOGY-CLI.md` (strategic vision and principles)

---

## 📖 What is a GrammaPlan?

**For LLMs/Developers**: A GrammaPlan orchestrates multiple related PLANs working toward a unified strategic goal. This is a meta-document - the actual work happens in child PLANs.

**This GrammaPlan**: Coordinates development of the foundational platform infrastructure, enabling all future tool integrations. Breaks the 40-60 hour foundation into 4 coordinated child PLANs for optimal parallelism and focused execution.

**File Location**: `work-space/plans/GRAMMAPLAN_UNIVERSAL-CLI-CORE-FOUNDATION.md`

**Size**: 600-1,500 lines (strategic coordination needs space)

**Guided By**:

- `NORTH_STAR_UNIVERSAL-METHODOLOGY-CLI.md` (vision and principles)
- Analyses: Terminal CLI vision and tool integration architecture

---

## 🎯 Strategic Goal

Build the foundational infrastructure that enables universal methodology management across all tools - a production-ready core engine, beautiful terminal CLI, language-agnostic API server, and extensible plugin system that serve as the bedrock for all platform capabilities.

**Vision Alignment**:

This GrammaPlan implements the **foundation layer** of the NORTH_STAR vision, establishing:

- **Universal Access** (Principle #2): Core engine works everywhere
- **Developer Experience** (Principle #1): Rich terminal CLI delights users
- **Extensibility** (Principle #5): Plugin system enables ecosystem
- **Production Quality** (Principle #6): >90% tested, enterprise-grade

**Deliverables**: Working `llm-methodology-cli` command, stable MethodologyAPI, JSON-RPC server, plugin architecture - all ready for integration PLANs to build upon.

---

## 🌐 Project Context Reference

**For Essential Project Knowledge**: See `LLM/PROJECT-CONTEXT.md`

**Current Methodology State**:

- 5-tier hierarchy (NORTH_STAR → GRAMMAPLAN → PLAN → SUBPLAN → EXECUTION_TASK)
- 15+ methodology scripts (generation, validation, archiving)
- 200+ tests validating methodology workflows
- 10+ production PLANs with 0% circular debugging rate

**This GrammaPlan's Role**: Transform existing scripts into beautiful CLI platform with universal API

---

## 📖 What to Read (GrammaPlan Focus Rules)

**When working on this GRAMMAPLAN**, follow these strategic focus rules:

**✅ READ (Strategist Agent)**:

- This GrammaPlan (strategic coordination of foundation)
- Active child PLAN "Current Status & Handoff" (coordination point)
- Cross-PLAN API contract sections (integration requirements)
- NORTH_STAR principles #1, #2, #5, #6 (guiding this foundation)

**❌ DO NOT READ (Stay Strategic)**:

- Child PLAN achievement details (Planner handles)
- SUBPLANs (Designer's responsibility)
- EXECUTION_TASKs (Executor's work)
- Other GRAMMAPLAN details (Universal CLI parent coordination)

**Context Budget**: ~300 lines per coordination session

**Why**: Foundation GrammaPlan coordinates 4 child PLANs building core infrastructure. Focus on API contracts, dependencies, integration points - not implementation details.

---

## 📋 Child PLANs

### Overview

This GrammaPlan coordinates **4 child PLANs** using **Hybrid Decomposition** (Core → CLI → API → Plugins):

| Child PLAN                       | Status   | Priority | Effort | Progress | Dependencies |
| -------------------------------- | -------- | -------- | ------ | -------- | ------------ |
| PLAN_UNIVERSAL-CLI-CORE-ENGINE   | Planning | CRITICAL | 12-18h | 0%       | None         |
| PLAN_UNIVERSAL-CLI-TERMINAL-UI   | Planning | CRITICAL | 10-15h | 0%       | PLAN 1       |
| PLAN_UNIVERSAL-CLI-API-SERVER    | Planning | HIGH     | 8-12h  | 0%       | PLAN 1       |
| PLAN_UNIVERSAL-CLI-PLUGIN-SYSTEM | Planning | HIGH     | 10-15h | 0%       | PLAN 1       |

**Total**: 40-60 hours across 4 PLANs

**Pattern**: Hybrid - Core engine first (API foundation), then parallel work on CLI/API/Plugins

---

### PLAN 1: Core Engine (Foundation API) 🏗️

**Effort**: 12-18h | **Priority**: CRITICAL | **Status**: Planning

**Purpose**: Build the core methodology engine providing file discovery, context management, and action execution - the foundation API all other components consume

**Scope**:

**Core Components**:

- **File Discovery Engine**: Scan work-space/ and archive/, index methodology files, cache metadata
- **Context Manager**: Track loaded PLAN/SUBPLAN, provide context to commands, persist sessions
- **Action Executors**: Wrap existing scripts (generate*prompt.py, validate*_, archive\__)
- **MethodologyAPI**: Abstract interface for all operations (list_plans, load_plan, generate_prompt, etc.)
- **Data Models**: Plan, Subplan, ExecutionTask, PlanContext classes

**Dependencies**: None (foundational layer)

**Deliverables**:

- `LLM/cli/core/engine.py` - Core engine implementation
- `LLM/cli/core/discoverer.py` - File discovery and indexing
- `LLM/cli/core/context.py` - Context management
- `LLM/cli/core/executors.py` - Action executors
- `LLM/cli/core/api.py` - MethodologyAPI interface
- `LLM/cli/models/` - Data models
- Comprehensive tests (>90% coverage)

**Contributes To**:

- **Universal Access** (API works everywhere)
- **Production Quality** (well-tested, reliable core)
- Foundation for all 3 other child PLANs

**Success Metrics**:

- > 90% test coverage
- File discovery <10s for 1000 files
- Context operations <100ms
- Zero dependencies on UI (pure logic)

**Principles**: #6 (Production Quality), #4 (Context is King)

**Location**: `work-space/plans/PLAN_UNIVERSAL-CLI-CORE-ENGINE.md`

---

### PLAN 2: Terminal CLI (Rich User Interface) 🎨

**Effort**: 10-15h | **Priority**: CRITICAL | **Status**: Planning

**Purpose**: Build beautiful, interactive terminal CLI with rich UI providing delightful user experience for all methodology operations

**Scope**:

**CLI Components**:

- **Interactive REPL**: Persistent session with readline support
- **Command Parser**: Parse and route commands (plans, load, generate_prompt, etc.)
- **Rich UI**: Tables, colors, progress bars, interactive menus (`rich` library)
- **Auto-Completion**: Command and file path completion
- **Command History**: Persistent history with search
- **Output Formatter**: Consistent, beautiful output for all operations
- **Error Handler**: Helpful error messages (show attempts, suggest fixes)

**Dependencies**:

- **Hard**: PLAN 1 (consumes MethodologyAPI)
- **Soft**: None (pure UI layer)

**Deliverables**:

- `LLM/cli/main.py` - CLI entry point (`llm-methodology-cli` command)
- `LLM/cli/commands/` - Command implementations (discovery.py, context.py, actions.py, info.py)
- `LLM/cli/ui/renderer.py` - Rich UI rendering
- `LLM/cli/ui/formatters.py` - Output formatters
- `LLM/cli/utils/parser.py` - Command parser
- Integration tests (CLI workflows)
- PyPI package configuration

**Contributes To**:

- **Developer Experience** (beautiful, interactive CLI)
- **Progressive Disclosure** (simple commands, advanced features)
- Beta release deliverable

**Success Metrics**:

- Interactive session working
- All commands render beautifully
- Command history and auto-complete working
- User feedback >4.5/5 on UX

**Principles**: #1 (DX First), #3 (Progressive Disclosure), #7 (Learn from Giants)

**Location**: `work-space/plans/PLAN_UNIVERSAL-CLI-TERMINAL-UI.md`

---

### PLAN 3: JSON-RPC API Server (Integration Layer) 🔌

**Effort**: 8-12h | **Priority**: HIGH | **Status**: Planning

**Purpose**: Build JSON-RPC API server enabling language-agnostic integration with all tools (Cursor, VS Code, Claude Code, etc.)

**Scope**:

**API Server Components**:

- **JSON-RPC Server**: Implement JSON-RPC 2.0 protocol (port 8080)
- **API Methods**: list_plans, get_plan, load_plan, generate_prompt, pause_plan, resume_plan, verify_plan, archive_plan
- **Request Handler**: Parse JSON-RPC requests, route to MethodologyAPI
- **Response Formatter**: Format responses as JSON-RPC
- **Error Handling**: JSON-RPC error codes and messages
- **Authentication**: Basic auth for remote access (optional)
- **CORS Support**: For web-based clients

**Dependencies**:

- **Hard**: PLAN 1 (consumes MethodologyAPI)
- **Soft**: PLAN 2 (can use CLI for testing)

**Deliverables**:

- `LLM/cli/api/jsonrpc_server.py` - JSON-RPC server
- `LLM/cli/api/handlers.py` - Request handlers
- `LLM/cli/api/routes.py` - API routing
- API documentation (OpenRPC spec)
- Integration tests (API contract tests)
- Client library examples (TypeScript, Python)

**Contributes To**:

- **Universal Access** (enables all tool integrations)
- **Extensibility** (language-agnostic)
- All integration PLANs depend on this

**Success Metrics**:

- API response <500ms
- JSON-RPC 2.0 compliant
- Client examples in 2+ languages
- Integration tests >95% coverage

**Principles**: #2 (Universal Access), #6 (Production Quality)

**Location**: `work-space/plans/PLAN_UNIVERSAL-CLI-API-SERVER.md`

---

### PLAN 4: Plugin System (Extensibility Layer) 🧩

**Effort**: 10-15h | **Priority**: HIGH | **Status**: Planning

**Purpose**: Build extensible plugin architecture enabling third-party extensions, custom commands, and tool integrations

**Scope**:

**Plugin Components**:

- **Plugin Interface**: Abstract base class for plugins (MethodologyPlugin protocol)
- **Plugin Registry**: Discover, load, and manage plugins
- **Plugin Loader**: Dynamic loading from directories or packages
- **Command Registration**: Plugins register custom commands
- **Lifecycle Hooks**: Initialize, activate, deactivate plugins
- **Plugin Configuration**: Plugin-specific settings and preferences
- **Example Plugins**: Git integration, custom aliases, workflow automation

**Dependencies**:

- **Hard**: PLAN 1 (provides MethodologyAPI to plugins)
- **Soft**: PLAN 2 (CLI commands can be extended), PLAN 3 (plugins can expose APIs)

**Deliverables**:

- `LLM/cli/core/plugin.py` - Plugin interface and protocol
- `LLM/cli/core/registry.py` - Plugin registry
- `LLM/cli/core/loader.py` - Plugin loader
- `LLM/cli/plugins/` - Example plugins (git, aliases)
- Plugin developer guide
- Plugin tests (>90% coverage)

**Contributes To**:

- **Extensibility** (third-party ecosystem)
- **Platform vs. Tool** (enables community contributions)
- Future advanced features (PLAN 6)

**Success Metrics**:

- 2+ example plugins working
- Plugin developer guide complete
- Plugin loading <500ms
- Third-party plugin creation enabled

**Principles**: #5 (Extensibility), #8 (Automation with Control)

**Location**: `work-space/plans/PLAN_UNIVERSAL-CLI-PLUGIN-SYSTEM.md`

---

## 🔗 Dependencies Between Children

### Foundation Dependency (Critical Path)

**PLAN 1 (Core Engine) is HARD dependency for all others**:

```
PLAN 1: Core Engine (MethodologyAPI)
├─→ PLAN 2: Terminal CLI (consumes API for commands)
├─→ PLAN 3: JSON-RPC Server (wraps API for remote access)
└─→ PLAN 4: Plugin System (provides API to plugins)
```

**Coordination**: PLAN 1 must complete **Priority 0** (MethodologyAPI stable) before others start

**Critical Path**: PLAN 1 (12-18h) → PLAN 2 (longest of parallel, 10-15h) = 22-33h minimum

### Parallel Opportunities

**After PLAN 1 Priority 0 (API Stable)**:

```
Phase 1: Core Engine (Sequential)
└── PLAN 1: Complete MethodologyAPI and data models

Phase 2: Foundation Components (Parallel)
├── PLAN 2: Terminal CLI
├── PLAN 3: JSON-RPC Server
└── PLAN 4: Plugin System
```

**Parallel Impact**:

- **Sequential**: 40-60h total
- **With Parallelism**: 12-18h (PLAN 1) + 10-15h (longest parallel) = 22-33h
- **Speedup**: ~2x faster with parallelism

### Cross-PLAN Coordination

**API Contract** (Managed by PLAN 1):

```python
class MethodologyAPI(Protocol):
    """Universal API - all children consume this"""

    # Discovery
    def list_plans(filters: dict) -> List[Plan]
    def list_subplans(plan_id: str) -> List[Subplan]
    def list_executions(subplan_id: str) -> List[ExecutionTask]
    def list_analyses(filters: dict) -> List[Analysis]

    # Context Management
    def load_plan(plan_id: str) -> PlanContext
    def get_context() -> Optional[PlanContext]
    def clear_context() -> None

    # Actions
    def generate_prompt(context: PlanContext) -> str
    def pause_plan(plan_id: str, reason: str) -> None
    def resume_plan(plan_id: str) -> None
    def verify_plan(plan_id: str) -> ValidationResult
    def archive_plan(plan_id: str) -> ArchiveResult
```

**All Other PLANs**: Consume this API, propose changes via coordination protocol

**PLAN 2 → PLAN 3 Integration**:

- CLI can test JSON-RPC server locally
- CLI provides reference implementation for API usage
- **Type**: Soft dependency (helps testing, not blocking)

**PLAN 4 → PLAN 2, 3 Integration**:

- Plugins can register CLI commands (PLAN 2)
- Plugins can expose API methods (PLAN 3)
- **Type**: Soft dependency (enhances but not blocking)

---

## 🔄 Cross-Cutting Concerns

### 1. Core API Contract (Critical for All)

**Provided By**: PLAN 1

**Components**:

- MethodologyAPI protocol (abstract interface)
- Data models (Plan, Subplan, ExecutionTask, PlanContext, ValidationResult)
- Error types (MethodologyException, ValidationError, etc.)

**Used By**: PLAN 2, 3, 4 all consume this API

**Integration**: Stable API contract enables parallel work after PLAN 1 Priority 0

**Coordination**: API changes require cross-PLAN review, breaking changes need versioning

### 2. Testing Infrastructure (Quality Assurance)

**Applies To**: All 4 child PLANs

**Requirements**:

- Unit tests: >90% coverage for all code
- Integration tests: Cross-module workflows
- API contract tests: Validate API compliance
- Performance tests: Discovery <10s, actions <3s
- Test fixtures: Shared test data and utilities

**Provided By**: PLAN 1 (test infrastructure and fixtures)

**Coordination**: PLAN 1 establishes patterns, others follow

### 3. File Structure (Package Organization)

**Structure**:

```
LLM/cli/
├── __init__.py
├── main.py                  # PLAN 2: CLI entry point
├── core/                    # PLAN 1: Core engine
│   ├── engine.py           # Main engine
│   ├── discoverer.py       # File discovery
│   ├── context.py          # Context manager
│   ├── executors.py        # Action executors
│   ├── api.py              # MethodologyAPI protocol
│   ├── plugin.py           # PLAN 4: Plugin interface
│   ├── registry.py         # PLAN 4: Plugin registry
│   └── loader.py           # PLAN 4: Plugin loader
├── api/                     # PLAN 3: API server
│   ├── jsonrpc_server.py   # JSON-RPC implementation
│   ├── handlers.py         # Request handlers
│   └── routes.py           # API routing
├── commands/                # PLAN 2: Command implementations
│   ├── discovery.py        # plans, subplans, etc.
│   ├── context.py          # load, context, clear
│   ├── actions.py          # generate_prompt, pause, etc.
│   └── info.py             # status, stats, help
├── ui/                      # PLAN 2: UI components
│   ├── renderer.py         # Rich UI rendering
│   └── formatters.py       # Output formatting
├── models/                  # PLAN 1: Data models
│   ├── plan.py
│   ├── context.py
│   └── validation.py
├── plugins/                 # PLAN 4: Example plugins
│   ├── git_integration.py
│   └── aliases.py
└── utils/                   # Shared utilities
    └── parser.py
```

**Coordination**: PLAN 1 establishes structure, others follow conventions

### 4. Documentation Strategy

**Structure**:

```
LLM/cli/
├── README.md               # Platform overview
├── QUICK-START.md          # 5-minute guide
├── USER-GUIDE.md           # Complete user docs
├── API-REFERENCE.md        # API documentation
├── PLUGIN-GUIDE.md         # Plugin development
└── ARCHITECTURE.md         # Technical architecture
```

**Contributed By**:

- PLAN 1: Architecture, API reference
- PLAN 2: User guide, quick start
- PLAN 3: API reference (JSON-RPC)
- PLAN 4: Plugin guide

**Coordination**: Each PLAN documents its component, integrated at end

---

## ✅ Success Criteria

### Must Have (Foundation Complete)

- [ ] **PLAN 1 Complete**: Core engine, MethodologyAPI stable, >90% tested
- [ ] **PLAN 2 Complete**: Terminal CLI working, beautiful UX, all commands functional
- [ ] **PLAN 3 Complete**: JSON-RPC server working, API documented, client examples
- [ ] **PLAN 4 Complete**: Plugin system working, 2+ example plugins, developer guide
- [ ] **Integration Validated**: All components work together seamlessly
- [ ] **Beta Deployable**: `llm-methodology-cli` ready for internal team

### Should Have (Excellence)

- [ ] **Performance**: All operations meet targets (<10s discovery, <3s actions)
- [ ] **Documentation**: Complete user guide, API reference, plugin guide
- [ ] **Test Coverage**: >95% across all 4 PLANs
- [ ] **User Feedback**: Internal team validates UX (>4.5/5)

### Nice to Have (Future)

- [ ] **REST API**: Additional API protocol (besides JSON-RPC)
- [ ] **Web Dashboard**: Simple web UI for methodology status
- [ ] **Advanced Plugins**: More example plugins demonstrating capabilities

**Foundation Success**: All 4 PLANs complete, Beta deployed, internal team using daily

---

## 📊 Progress Tracking

### Overall Progress Formula

```
Foundation GrammaPlan Progress =
    (PLAN_1_Progress * 15h +     # Core Engine
     PLAN_2_Progress * 12.5h +   # Terminal CLI
     PLAN_3_Progress * 10h +     # API Server
     PLAN_4_Progress * 12.5h)    # Plugin System
    /
    50h (total)

Current: 0% (0h / 50h)
```

### Child PLAN Status Summary

| Child PLAN      | Status      | Progress | Effort  | Next Milestone    |
| --------------- | ----------- | -------- | ------- | ----------------- |
| PLAN 1: Engine  | ⏳ Planning | 0%       | 0/15h   | Create PLAN 1     |
| PLAN 2: CLI     | ⏳ Pending  | 0%       | 0/12.5h | Awaits PLAN 1 API |
| PLAN 3: API     | ⏳ Pending  | 0%       | 0/10h   | Awaits PLAN 1 API |
| PLAN 4: Plugins | ⏳ Pending  | 0%       | 0/12.5h | Awaits PLAN 1 API |

**Recommended Next**: Create PLAN 1 (Core Engine) - Establishes foundation API

---

## 📝 Current Status & Handoff (For Pause/Resume)

**Last Updated**: 2025-11-08 18:00 UTC  
**Status**: 📋 Planning Complete (Ready for Execution)

**Phase**: Pre-Execution (GrammaPlan created, child PLANs not yet created)

**Completed**:

- ✅ Foundation GrammaPlan defined
- ✅ 4 child PLANs scoped
- ✅ Dependencies mapped (Core → All others)
- ✅ Parallelism strategy identified (2x speedup)
- ✅ API contract defined
- ✅ Success criteria established

**Pending**: All 4 child PLANs (awaiting PLAN 1 creation)

**Next Steps**:

1. **Create PLAN 1** (Core Engine) using IMPLEMENTATION_START_POINT.md
2. **Execute PLAN 1**: Build MethodologyAPI, core engine, data models
3. **After PLAN 1 Priority 0**: Create PLAN 2, 3, 4 (can work in parallel)
4. **Coordinate**: Weekly syncs to manage API contract, share learnings

**When Resuming**:

1. Read this "Current Status & Handoff" section
2. Review Child PLAN Status Summary
3. Check which PLANs completed (update dependencies)
4. Follow IMPLEMENTATION_RESUME.md for active child PLAN

**Context Preserved**: This GrammaPlan + NORTH_STAR + Analyses = complete context

---

## 🔗 Decomposition Pattern: Hybrid (Core → Components)

**Pattern**: Hybrid Decomposition

**Structure**:

```
Phase 1: Core API (Sequential - Must Complete First)
└── PLAN 1: Core Engine (MethodologyAPI + data models)

Phase 2: Foundation Components (Parallel - After API Stable)
├── PLAN 2: Terminal CLI (rich UI layer)
├── PLAN 3: JSON-RPC Server (remote API layer)
└── PLAN 4: Plugin System (extensibility layer)
```

**Why Hybrid**:

- **Core First**: API must stabilize before components (API dependency)
- **Components Parallel**: CLI, API Server, Plugins are independent (maximize speed)

**Benefits**:

- API stability before integration (prevents rework)
- 2x speedup via parallelism (Phase 2 parallel work)
- Clear boundaries (each component isolated)
- Learning transfer (API patterns inform all components)

**Alternative Considered**: Pure Phase Decomposition (Discovery → Context → Actions → Server → Plugins)

**Why Not**: Forces sequential work where parallelism possible (CLI and API Server could build simultaneously)

---

## ⚠️ Constraints

### Technical Constraints

**Platform**:

- Python 3.8+ required (for core engine)
- Cross-platform: macOS, Linux, Windows
- Dependencies: `rich` (terminal UI), `jsonrpc` (API server), `click` (CLI framework)

**Performance**:

- File discovery: <10s for 1000 files
- Context operations: <100ms
- API response: <500ms
- CLI commands: <3s end-to-end

**API Stability**:

- MethodologyAPI must be stable before PLAN 2-4 complete
- Breaking changes require versioning + migration guide

### Process Constraints

**Sequential Foundation**:

- PLAN 1 Priority 0 must complete before others start Priority 1
- API stability critical (prevents rework in PLAN 2-4)

**Quality Gates**:

- > 90% test coverage per PLAN
- Integration tests required
- Performance benchmarks must pass

**Coordination**:

- Weekly syncs (if multiple PLANs active)
- API change proposals reviewed by all leads
- Breaking changes need coordinator approval

### Resource Constraints

**Timeline**: 3 weeks total

- Week 1: PLAN 1 (Core Engine)
- Weeks 2-3: PLAN 2, 3, 4 (parallel)

**Development**:

- Single developer: Can do light parallelism (work on multiple PLANs, but focus on one at a time)
- Small team (2-3): Full parallelism possible

---

## 🚨 Key Risks & Mitigation

| Risk                         | Impact | Probability | Mitigation                                              | Owner                  |
| ---------------------------- | ------ | ----------- | ------------------------------------------------------- | ---------------------- |
| **API Instability**          | High   | Medium      | Careful design, versioning, comprehensive tests         | PLAN 1 Lead            |
| **Performance Issues**       | Medium | Low         | Early benchmarking, profiling, optimization focus       | PLAN 1 Lead            |
| **Plugin System Complexity** | Medium | Medium      | Start simple, iterate based on needs                    | PLAN 4 Lead            |
| **Integration Failures**     | High   | Low         | Contract tests, integration tests, early testing        | GrammaPlan Coordinator |
| **Timeline Slippage**        | Medium | Medium      | Realistic estimates, buffer time, prioritize ruthlessly | GrammaPlan Coordinator |

### Risk Details

**Risk 1: API Instability**

**Scenario**: MethodologyAPI changes frequently, breaking PLAN 2-4

**Prevention**:

- Design API carefully in PLAN 1 Priority 0
- Comprehensive tests (>95% coverage on API)
- Contract tests that PLAN 2-4 run
- Early validation with prototype integrations

**Response**: Emergency sync, impact assessment, versioning, migration guide

**Risk 2: Integration Failures**

**Scenario**: Components don't work together when integrated

**Prevention**:

- Early integration testing (prototype early)
- Contract tests (each PLAN validates API contract)
- Continuous integration (CI runs all tests)
- Integration milestones (partial integration before completion)

**Response**: Integration debugging session, identify misalignment, fix in relevant PLAN

---

## 📋 Coordination Protocols

### Weekly Sync Meeting (If Multiple Active)

**Attendees**: Active PLAN leads + coordinator

**Agenda** (30 minutes):

1. Progress updates (5 min each)
2. API contract review (any proposed changes?)
3. Dependency status (is PLAN 1 API ready?)
4. Integration testing (any failures?)
5. Next week priorities

**Output**: Updated status, coordinated dependencies, action items

### API Change Protocol

**Process**:

1. Proposer documents change + rationale
2. All PLAN leads review (24h)
3. Sync meeting discusses if needed
4. Coordinator decides
5. If breaking: Version bump + migration guide

**Coordination**: API contract is sacred - changes need strong justification

### Integration Testing Protocol

**When**: Weekly during Phase 2, before any PLAN marks complete

**Process**:

1. PLAN 1 provides test harness
2. Each child runs API contract tests
3. Integration tests (CLI calls engine, server wraps engine, plugins use engine)
4. Performance benchmarks
5. Coordinator validates results

**Milestone**: Integration checkpoint before Beta release

---

## 🎓 Learning & Evolution

### Shared Learnings

**Document**: `work-space/FOUNDATION-LEARNINGS.md`

**Categories**:

- **API Design**: Patterns that worked/didn't
- **Performance**: Optimization techniques
- **Testing**: Effective test patterns
- **Integration**: Cross-component insights

**Process**: Add after significant discovery → Weekly review → Apply to pending PLANs

**Example**:

```markdown
### Learning: Async API Design

**Source**: PLAN 1, Achievement 1.2
**Pattern**: Use async/await for file operations (10x speedup)
**Applies To**: PLAN 2 (CLI can be async), PLAN 3 (API server async)
**Impact**: Better performance, non-blocking operations
```

### Methodology Feedback

**What**: Learnings from foundation development inform methodology

**Process**:

1. Identify methodology patterns (GrammaPlan coordination, child sizing)
2. Document in completion summary
3. Feed back to PLAN_STRUCTURED-LLM-DEVELOPMENT.md

**Frequency**: After foundation complete (Week 3)

**Examples**:

- GrammaPlan sizing (did 4 children at 10-15h each work well?)
- API-first approach (did it enable parallelism as expected?)
- Testing patterns (did contract tests prevent integration issues?)

---

## ⏱️ Time Estimates

### Per Child PLAN

- **PLAN 1: Core Engine**: 12-18h (API design + implementation + extensive testing)
- **PLAN 2: Terminal CLI**: 10-15h (UI implementation + command handlers)
- **PLAN 3: JSON-RPC Server**: 8-12h (server + API wrapping)
- **PLAN 4: Plugin System**: 10-15h (plugin architecture + examples)

**Total**: 40-60h (midpoint: 50h)

### Breakdown by Priority

- **Critical** (PLAN 1, 2): 22-33h (must complete for Beta)
- **High** (PLAN 3, 4): 18-27h (nice to have for Beta, required for v1.0)

### Sequencing Impact

**Sequential** (one at a time):

- Total: 40-60h
- Timeline: 3 weeks (conservative, 15h/week)

**With Parallelism** (realistic):

- Phase 1: PLAN 1 (12-18h, Week 1)
- Phase 2: PLAN 2, 3, 4 parallel (max 10-15h, Weeks 2-3)
- Total: 22-33h effective
- Timeline: 3 weeks (accelerated)

**Recommended**: Light parallelism (PLAN 1 Week 1, focus on PLAN 2 Week 2 with PLAN 3-4 started, finish all Week 3)

---

## 📦 Archiving Plan

**When This GrammaPlan Is Complete**:

Archive as part of parent: `documentation/archive/grammaplan-universal-cli-YYYY-MM/foundation/`

**Structure**:

```
foundation/
├── GRAMMAPLAN_UNIVERSAL-CLI-CORE-FOUNDATION.md (this doc)
├── planning/
│   ├── PLAN_UNIVERSAL-CLI-CORE-ENGINE.md
│   ├── PLAN_UNIVERSAL-CLI-TERMINAL-UI.md
│   ├── PLAN_UNIVERSAL-CLI-API-SERVER.md
│   └── PLAN_UNIVERSAL-CLI-PLUGIN-SYSTEM.md
├── subplans/
│   └── ... (all SUBPLANs from all 4 children)
├── execution/
│   └── ... (all EXECUTION_TASKs from all 4 children)
└── summary/
    └── FOUNDATION-COMPLETE.md
```

**Note**: Archive foundation GrammaPlan with parent GrammaPlan when platform complete

---

## ✅ Completion Criteria

**This Foundation GrammaPlan is Complete When**:

### Required

1. [ ] **All 4 child PLANs complete** (100% each)
2. [ ] **Integration validated** (all components work together)
3. [ ] **Beta deployable** (`llm-methodology-cli` command working)
4. [ ] **Quality verified** (>90% test coverage, performance targets met)
5. [ ] **Documentation complete** (user guide, API reference)

### Process

1. Mark PLAN 4 complete (last child)
2. Run integration tests (full workflow validation)
3. Performance benchmarks (all targets met)
4. Internal beta test (team uses CLI for 1 week)
5. Fix critical issues (if any)
6. Update foundation GrammaPlan status to "Complete"
7. Beta release deployed
8. Hand off to parent GrammaPlan (ready for integration PLANs)

---

## 🎯 Expected Outcomes

**Week 1** (After PLAN 1): Core API stable, data models complete, test infrastructure ready

**Week 2** (After PLAN 2-4 start): CLI showing signs of life, API server prototype, plugin example

**Week 3** (After All Complete): Beta release - working `llm-methodology-cli` with rich UI, API ready for integrations, plugin system extensible

**Impact**: Internal team 5x faster methodology operations, foundation ready for Cursor/VS Code/Claude Code integrations

---

## 📋 Immediate Next Steps

1. **Create PLAN 1** (Core Engine)

   - Follow: IMPLEMENTATION_START_POINT.md
   - Template: LLM/templates/PLAN-TEMPLATE.md
   - Reference: NORTH_STAR Principle #6 (Production Quality), Principle #4 (Context is King)
   - Focus: MethodologyAPI design, file discovery, context management

2. **Setup Project**

   - Repository: `llm-methodology-cli` on GitHub
   - Structure: Python package with `LLM/cli/` directory
   - CI/CD: GitHub Actions (pytest, black, mypy, coverage)
   - Package: pyproject.toml, setup.py for PyPI

3. **Execute PLAN 1**

   - Priority 0: MethodologyAPI interface stable
   - Priority 1: Core engine implementation
   - Priority 2: Test infrastructure
   - Milestone: API contract stable for PLAN 2-4

4. **Prepare Phase 2**
   - Draft PLAN 2, 3, 4 (can prepare while PLAN 1 executes)
   - Design CLI command structure
   - Research JSON-RPC libraries
   - Design plugin interface

---

## 🌟 Foundation Philosophy

**"Build the Foundation Right, Build It Once"**

The foundation is the most critical piece - every line of code in PLAN 2-6 will depend on it. A shaky foundation means rebuilding everything. A solid foundation enables speed.

**What "Right" Means**:

- **Clean API**: Simple, predictable, well-documented
- **Tested Thoroughly**: >95% coverage on core (not just >90%)
- **Performance First**: Fast file discovery, instant context operations
- **Extensible**: Plugin system designed for growth

**What "Once" Means**:

- **No Refactors**: Get it right in PLAN 1, don't revisit in PLAN 5
- **Stable Contract**: API doesn't change, integrations don't break
- **Quality Investment**: Spend time on foundation quality, save time later

**Aligns With**: NORTH_STAR Principle #6 (Production-Ready Quality)

---

**Status**: 📋 Planning Complete - Ready for Phase 1 (Core Engine)  
**Next**: Create PLAN 1 following PLAN-TEMPLATE.md  
**Guided By**: NORTH_STAR_UNIVERSAL-METHODOLOGY-CLI.md principles  
**Timeline**: 3 weeks → Beta release

---

**GrammaPlan Coordinator**: TBD  
**Start Date**: TBD  
**Target**: Week 3 (Beta deployable foundation)  
**Lines**: ~580 (within 600-1,500 GrammaPlan range)
