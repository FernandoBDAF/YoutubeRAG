# NORTH_STAR: Universal Methodology CLI Platform

**Status**: 🌟 Strategic Vision  
**Created**: 2025-11-08 16:30 UTC  
**Strategic Purpose**: Illuminate the vision for universal, developer-centric methodology management tooling that transforms how humans and LLMs collaborate on complex software development  
**Scope**: Guides CLI platform development, tool integrations, and methodology tooling ecosystem evolution

**File Location**: `work-space/north-stars/NORTH_STAR_UNIVERSAL-METHODOLOGY-CLI.md`

---

## 🌟 What is a NORTH_STAR?

**For LLMs/Developers**: A NORTH_STAR document provides strategic vision and guiding principles for a domain or initiative. It "floats above the funnel, illuminating it" - providing direction without prescribing tactics.

**This NORTH_STAR**: Defines the vision, principles, and philosophy for building a universal methodology management platform that empowers developers to work efficiently across any tool while maintaining structured, high-quality LLM-assisted development.

**Key Characteristics**:

- **Strategic** (not tactical): WHY and WHAT, not HOW
- **Vision-driven**: Future state of methodology tooling
- **Principle-based**: 8 core principles guiding development
- **Coordinating**: Guides GrammaPlan and PLANs implementing this vision
- **Living**: Evolves as we learn from building and using the platform

**Size**: 800-2,000 lines (comprehensive vision + principles)

**Hierarchy**: Top tier, illuminating all methodology tooling work

```
       ⭐ NORTH_STAR (this document)
      "Floats above, illuminates"
              ↓
     📋 GRAMMAPLAN_UNIVERSAL-CLI
       (coordinates 6 PLANs)
              ↓
          6 PLANs
       (execute work)
```

---

## 🎯 Strategic Vision: The Future of Methodology Tooling

### Where We're Going

**Vision**: A world where managing LLM-assisted development workflows is as natural and powerful as using `git` for version control - universal, intuitive, and indispensable.

Imagine a developer starting their day:

- Opens their favorite tool (Cursor, VS Code, Claude Code - doesn't matter)
- Types `methodology plans` or clicks sidebar icon
- Sees all active work at a glance with visual progress indicators
- Loads context with `load PL02` or single click
- Generates prompts with one command or button
- Starts working immediately - zero friction, zero context switching

**This is the future we're building**: Methodology management so seamless it becomes invisible, so powerful it becomes essential.

### Why This Matters

**The Current Reality** (Pain Points):

LLM-assisted development is exploding - GitHub Copilot (1.3M+ users), ChatGPT (100M+), Cursor (rapid growth) - but **methodology management is still stone-age**:

- Long terminal commands: `python LLM/scripts/generation/generate_prompt.py @work-space/plans/PLAN_VERY-LONG-NAME.md`
- Manual tracking: Open 5 files to understand plan status
- Constant context switching: Terminal → Editor → Browser → Back
- No visual overview: "Which plans are active again?"
- Workflow repetition: Same 7-step process every time

**The Desired Future** (This Vision):

Methodology management that feels like **modern developer tools** - intuitive, fast, beautiful:

- **10x faster**: `load PL02` → `generate_prompt` → Done (30s vs. 5min)
- **Universal**: Works in terminal, Cursor, VS Code, Claude Code, everywhere
- **Visual**: Rich UI showing all work at a glance
- **Context-aware**: AI assistants understand methodology state
- **Zero friction**: Single commands replace multi-step workflows

**Strategic Impact**:

- **Category Creation**: Establish "methodology management tooling" as first-class category
- **Adoption Enabler**: Make structured LLM development accessible to all developers
- **Ecosystem Foundation**: Platform other tools can build upon
- **Methodology Excellence**: Tooling that makes quality the default path

**Result**: Transform LLM development from ad-hoc to excellent through superior tooling

---

## 💎 Core Principles

**These 8 principles guide all decisions in building this platform:**

### Principle 1: Developer Experience First

**Statement**: Optimize for developer delight, not just functionality.

**Explanation**: The best tool is the one developers love to use. Every command, every integration, every piece of UI should feel intuitive, fast, and delightful. Beautiful terminal output isn't "nice to have" - it's essential. Interactive selection isn't "extra" - it's expected. If developers don't enjoy using the tool, they won't use it, and the methodology won't be followed.

This principle guides us to invest heavily in UX: rich terminal UI with colors and tables, interactive menus, smart suggestions, helpful error messages, and consistent patterns. We study modern CLI tools (`gh`, `cargo`, `kubectl`) and learn from their UX excellence.

**Anti-Pattern**: Functional but ugly CLI, confusing commands, unhelpful errors, inconsistent output

**Example**: Choosing `rich` library for terminal UI, designing `plans` command with visual tables instead of plain text lists

### Principle 2: Universal Access Over Platform Lock-In

**Statement**: Work everywhere developers work, never force tool choice.

**Explanation**: Developers love their tools - Cursor, VS Code, Neovim, JetBrains, Claude Code - and won't change for methodology tooling. Universal means the platform works natively in ALL tools, providing consistent experience without dictating choices.

This principle guides us to build universal API first (JSON-RPC), then integrate with all major tools. No "best experienced in Tool X" - every tool is first-class. The terminal CLI ensures everyone can use it, even via SSH or CI/CD.

**Anti-Pattern**: "Works best in VS Code", "Cursor-only features", forcing developers to switch tools

**Example**: Building JSON-RPC API enabling language-agnostic integration, starting with terminal CLI that works everywhere

### Principle 3: Progressive Disclosure

**Statement**: Simple to start, power features discoverable when needed.

**Explanation**: New users should accomplish basic tasks immediately without reading docs. Power users should discover advanced features naturally through exploration. This balance - easy entry, deep capability - defines great tools.

This principle guides command design: `plans` just works (no options needed), but `plans --status active --priority high` provides power. Help text is concise but points to detailed docs. Interactive menus guide new users; shortcuts empower experts.

**Anti-Pattern**: Requiring docs to do anything basic, hiding power features too deeply, overwhelming new users

**Example**: `plans` shows all plans with simple table, `plans --help` reveals filters, interactive mode guides through options

### Principle 4: Context is King

**Statement**: Intelligently manage context so developers never repeat themselves.

**Explanation**: Modern developers work across multiple plans, tools, and sessions. Smart context management - loading a plan once and using it everywhere - dramatically reduces cognitive load. Context should persist across commands, sync across tools, and intelligently suggest next actions.

This principle guides context manager design, cross-tool state synchronization, and AI context injection. Once you `load PL02` in terminal, VS Code sidebar reflects it, Cursor AI knows it, Claude Code understands it.

**Anti-Pattern**: Requiring plan ID for every command, lost context between tools, repeating information

**Example**: `load PL02` once, then `generate_prompt`, `pause`, `status` all use that context automatically

### Principle 5: Extensibility Through Plugins

**Statement**: Build a platform, not just a tool - enable ecosystem.

**Explanation**: We can't anticipate every need, support every tool, or implement every feature. A plugin system enables community to extend platform for their needs. This transforms product into platform, tool into ecosystem.

This principle guides architecture decisions: plugin interface from day 1, well-documented APIs, example plugins, registry system. Make it trivial to add new integrations, custom commands, or workflow automation.

**Anti-Pattern**: Monolithic design, hardcoded integrations, no extension points, "we'll add that" instead of "you can add that"

**Example**: Plugin system allowing third-party Git integration, custom commands, alternative AI assistants

### Principle 6: Production-Ready Quality

**Statement**: Never compromise on quality - tests, docs, performance, reliability.

**Explanation**: Methodology tooling is infrastructure. Developers depend on it daily. Bugs waste time, poor performance frustrates, missing docs blocks adoption, unreliable tools erode trust. Production-ready from start, not "we'll fix it later."

This principle guides development: >90% test coverage required, comprehensive documentation, performance targets enforced, error handling comprehensive, graceful degradation always. Quality gates at every phase, no shortcuts.

**Anti-Pattern**: "Ship fast, fix later", untested code, minimal docs, performance issues ignored

**Example**: >90% test coverage requirement for all 6 PLANs, performance target <5s for discovery operations

### Principle 7: Learn from the Giants

**Statement**: Study great CLI tools, don't reinvent proven patterns.

**Explanation**: Modern CLI UX has matured through decades of evolution. Git's porcelain/plumbing separation, kubectl's context management, docker's visual output, cargo's helpful errors - these patterns work. Learn, adapt, apply. Standing on giants' shoulders reaches higher than starting from scratch.

This principle guides design research: study `git`, `kubectl`, `docker`, `gh`, `cargo` before implementing. Adopt proven patterns, avoid solved problems, innovate where needed but not elsewhere.

**Anti-Pattern**: Ignoring existing tools, reinventing command structures, custom patterns for no reason

**Example**: Adopting `git`-style command structure, `kubectl`-style context management, `cargo`-style error messages

### Principle 8: Automation with Human Control

**Statement**: Automate repetitive work, humans control strategic decisions.

**Explanation**: This aligns with LLM methodology core principle #4. Platform should automate mechanics (prompt generation, validation, state updates), but humans decide strategy (which plan to work on, when to pause, when to release). Right balance: speed without loss of control.

This principle guides feature design: automatic validation (automate), but manual archive (control); auto-generate prompts (automate), but user decides which achievement (control); smart suggestions (automate), but user chooses action (control).

**Anti-Pattern**: Forcing automatic workflows, removing human decision points, "magic" that can't be controlled

**Example**: Auto-generate prompts but don't auto-send, auto-detect completion but don't auto-archive, suggest next achievement but don't auto-start

---

## 🌐 Project Context Reference

**For Essential Project Knowledge**: See `LLM/PROJECT-CONTEXT.md`

**What You Need to Know**:

- **Current Methodology**: 5-tier hierarchy (NORTH_STAR → GRAMMAPLAN → PLAN → SUBPLAN → EXECUTION_TASK)
- **Multi-Agent Model**: Strategist, Planner, Designer, Executor roles with funnel-based context management
- **Validation Infrastructure**: 15+ validation scripts, 200+ tests, automated enforcement
- **Production Validated**: 10+ PLANs, 200+ achievements, 200+ hours real usage, 0% circular debugging rate

**When to Reference**: Architecture questions, convention questions, domain understanding

**Automatic Injection**: Prompt generator includes project context automatically

---

## 📖 What to Read (North Star Focus)

**When working under this NORTH_STAR**, follow these strategic focus rules:

**✅ READ**:

- This NORTH_STAR (vision and principles) - Strategic direction
- Relevant principle when making decision - Guiding wisdom
- Current State section - Reality check
- Coordinating initiative status (if making decisions affecting multiple)

**❌ DO NOT READ (Too Tactical for Strategic Vision)**:

- PLAN achievement details (PLANs handle execution)
- SUBPLANs (way too tactical)
- EXECUTION_TASKs (implementation details)
- Full GrammaPlan execution details (coordination mechanics)

**Context Budget**: ~400 lines per strategic session

**Why**: NORTH_STAR provides vision and principles, not tactical plans. When making decisions, consult relevant principles. When planning work, ensure alignment with vision. Strategic thinking requires elevation above tactical details.

**📖 See**: `LLM/guides/NORTH-STAR-GUIDE.md` for complete guidance

---

## 👥 Target Users & Key Workflows

**Primary Users**: Solo developers, team leads, power users

**Core Workflows**:

- Quick discovery: `plans` → `load PL02` → `generate_prompt --copy` (30s vs. 3-5min)
- IDE integration: Click plan in sidebar → Generate prompt → Start work (10s vs. 2min)
- Pause/Resume: `pause --reason X` → Later: `resume PL04` (20s vs. 5min)

**Impact**: 10x faster navigation, zero context switching, visual clarity

**Detailed personas**: See PLAN 1 for complete user research and workflows

---

## 📋 Scope Definition

### In Scope (This GrammaPlan)

**Product Development**:

- Terminal CLI with rich interactive UX (colors, tables, progress bars, interactive selection)
- Core engine with universal API (language-agnostic, extensible)
- Integration SDKs for 6+ major tools (Cursor, Claude Code, VS Code, Copilot, JetBrains, Neovim)
- Plugin architecture (extensible by third parties)
- Comprehensive documentation (guides, tutorials, API docs)
- Production-ready quality (>90% test coverage, error handling, performance)

**User Experience**:

- Progressive disclosure (simple to start, power features discoverable)
- Real-time feedback (confirmations, progress indicators, smart suggestions)
- Consistent interface (uniform commands, outputs, error messages)
- Accessibility (keyboard navigation, screen reader support)
- Comprehensive help (inline help, examples, troubleshooting)

**Infrastructure**:

- JSON-RPC API server (language-agnostic integration)
- REST API (web-based tools)
- State synchronization (cross-tool coordination)
- Plugin registry (third-party extensions)
- Configuration management (user preferences, tool-specific configs)

### Out of Scope

**Not in This Initiative**:

- Methodology changes (handled by PLAN_STRUCTURED-LLM-DEVELOPMENT.md)
- Core validation script rewrites (already working, just wrap them)
- Web-based management UI (future consideration, not MVP)
- Mobile apps (not target platform)
- Cloud hosting (self-hosted only in v1.0)
- Multi-tenancy (single-user focus)

**Rationale**: Focused scope ensures delivery. Advanced features via plugin system or future versions.

---

## 📏 Size Validation

**Estimated Total Effort**: 210-290 hours (6 child PLANs)

**GrammaPlan Decision Criteria**:

- [x] **> 80 hours?** → YES (210-290 hours) ⚠️ **MANDATORY**
- [x] **> 800 lines if single PLAN?** → YES (estimated 2,500+ lines) ⚠️ **MANDATORY**
- [x] **3+ domains?** → YES (6 domains: CLI, APIs, 4 integrations) ✅ **STRONG INDICATOR**
- [x] **Natural parallelism?** → YES (integrations can work in parallel) ✅ **STRONG INDICATOR**

**Decision**: **GrammaPlan REQUIRED** - Exceeds all mandatory criteria + 2 strong indicators

**Rationale**:

- Massive scope (210-290 hours across 12-16 weeks)
- Multiple distinct domains (CLI, API, extensions for 6 different tools)
- Clear boundaries enable parallel work (integrations independent after foundation)
- Strategic coordination essential (API contract, cross-tool state, release planning)

**See**: `LLM/guides/GRAMMAPLAN-GUIDE.md` for complete decision criteria

---

## 🔗 Coordinating Initiatives (Strategic Alignment)

### Overview

This NORTH_STAR guides implementation through **1 GrammaPlan** coordinating **6 PLANs**, all aligned with vision and principles:

**GrammaPlan**: `GRAMMAPLAN_UNIVERSAL-METHODOLOGY-CLI.md` (coordinates tactical execution)

| Initiative (PLAN)              | Effort | Serves Principle                 | Alignment with Vision                |
| ------------------------------ | ------ | -------------------------------- | ------------------------------------ |
| PLAN_UNIVERSAL-CLI-CORE        | 40-60h | #1 (DX First), #6 (Quality)      | Foundation enabling universal access |
| PLAN_CURSOR-CLI-INTEGRATION    | 20-30h | #2 (Universal), #4 (Context)     | Seamless Cursor integration          |
| PLAN_CLAUDE-CODE-EXTENSION     | 30-40h | #2 (Universal), #1 (DX)          | Native AI tool integration           |
| PLAN_VSCODE-EXTENSION          | 40-50h | #2 (Universal), #3 (Progressive) | Largest user base support            |
| PLAN_AI-ASSISTANTS-INTEGRATION | 20-30h | #4 (Context), #5 (Extensibility) | AI ecosystem integration             |
| PLAN_EXTENDED-TOOLS-FEATURES   | 60-80h | #5 (Plugins), #7 (Giants)        | Ecosystem expansion                  |

**Total**: 210-290 hours | **Timeline**: 12-16 weeks | **Coordination**: Via GrammaPlan

---

### PLAN 1: Universal CLI Core (Foundation) 🏗️

**Effort**: 40-60h | **Priority**: CRITICAL | **Progress**: 0%

**Purpose**: Core engine + rich terminal CLI providing foundation for all integrations

**Scope**: Core API, terminal CLI (`rich` library), JSON-RPC server, plugin system, discovery/context/action commands

**Dependencies**: None (foundation)

**Deliverables**: `llm-methodology-cli` command, MethodologyAPI, JSON-RPC server, plugin interface, >90% tests

**Contributes To**: Universal Access & Superior UX - Foundation enabling all integrations

**Metrics**: 70% step reduction, <5s discovery, interactive session, >90% coverage

**Location**: `work-space/plans/PLAN_UNIVERSAL-CLI-CORE.md`

---

### PLAN 2: Cursor CLI Integration 🎯

**Effort**: 20-30h | **Priority**: HIGH | **Progress**: 0%

**Purpose**: Native Cursor commands with context-aware AI integration

**Scope**: Command registration, context provider, AI injection, file watcher, terminal integration

**Dependencies**: PLAN 1 (API + JSON-RPC)

**Deliverables**: `cursor-commands.json`, context provider, AI hooks, Cursor docs, integration tests

**Contributes To**: Seamless Workflow - Cursor users never leave editor

**Metrics**: Zero context switching, AI uses PLAN context, commands auto-complete

**Related**: PLAN 4 (similar extension patterns)

**Location**: `work-space/plans/PLAN_CURSOR-CLI-INTEGRATION.md`

---

### PLAN 3: Claude Code Extension 🤖

**Effort**: 30-40h | **Priority**: HIGH | **Progress**: 0%

**Purpose**: Full Claude Code extension with sidebar and native AI integration

**Scope**: Sidebar panel, command palette, Claude AI integration, one-click prompts, workflow automation, marketplace packaging

**Dependencies**: PLAN 1 (API + JSON-RPC), soft: PLAN 2 (patterns)

**Deliverables**: Extension package, sidebar UI, AI provider, marketplace submission, docs

**Contributes To**: Context-Aware Assistance - Claude AI understands methodology

**Metrics**: One-click prompts, visual explorer, AI suggestions, published to marketplace

**Related**: PLAN 4 (similar IDE integration)

**Location**: `work-space/plans/PLAN_CLAUDE-CODE-EXTENSION.md`

---

### PLAN 4: VS Code Extension 💻

**Effort**: 40-50h | **Priority**: HIGH | **Progress**: 0%

**Purpose**: Comprehensive VS Code extension with full IDE integration

**Scope**: Explorer tree view, status bar, command palette, code lens, hover info, settings, terminal integration, marketplace

**Dependencies**: PLAN 1 (API + JSON-RPC), soft: PLAN 2, 3 (patterns)

**Deliverables**: Extension package, tree view, status bar, commands, lens/hover providers, settings, publication, docs

**Contributes To**: Superior UX + Universal Access - VS Code full IDE experience

**Metrics**: Tree view working, status bar displays context, published, >1,000 installs in 3 months

**Related**: PLAN 3 (IDE patterns), PLAN 2 (command patterns)

**Location**: `work-space/plans/PLAN_VSCODE-EXTENSION.md`

---

### PLAN 5: AI Assistants Integration 🧠

**Status**: Planning  
**Estimated Effort**: 20-30 hours  
**Progress**: 0% complete  
**Priority**: MEDIUM (Expanding AI ecosystem support)

**Purpose**: Build extensible AI assistant framework with GitHub Copilot as first implementation, enabling methodology-aware code suggestions and chat integration

**Scope**:

- **GitHub Copilot Plugin**: Context injection into Copilot suggestions
- **Copilot Chat Integration**: Prompt generation in chat interface
- **Code Suggestion Enhancement**: Methodology-compliant patterns in suggestions
- **Extensible Framework**: Abstract interface for any AI assistant
- **Context Provider**: Methodology context → AI assistant bridge
- **Future AI Support**: Architecture supports Claude, ChatGPT, other assistants

**Dependencies**:

- **Hard**: PLAN 1 (needs core API)
- **Soft**: PLAN 3 (Claude Code AI integration learnings)

**Key Deliverables**:

- GitHub Copilot plugin (`copilot-methodology-plugin/`)
- Abstract AI assistant interface
- Context injection system
- Copilot-specific implementation
- Framework documentation
- Extension guide for other AI tools

**Contributes To**: Context-Aware Assistance goal - AI assistants understand methodology context

**Success Metrics**:

- Copilot chat shows methodology context
- Code suggestions follow methodology patterns
- Framework supports 2+ AI assistants
- Documentation enables third-party AI integrations

**Related Sections**: PLAN 3 (Claude Code) for AI integration patterns

**Location**: `work-space/plans/PLAN_AI-ASSISTANTS-INTEGRATION.md`

---

### PLAN 6: Extended Tools & Advanced Features 🚀

**Status**: Planning  
**Estimated Effort**: 60-80 hours  
**Progress**: 0% complete  
**Priority**: MEDIUM (Nice-to-have, ecosystem expansion)

**Purpose**: Expand platform to additional development tools and implement advanced features for power users

**Scope**:

**Additional Tools**:

- **JetBrains Plugin**: IntelliJ, PyCharm, WebStorm support
- **Neovim Plugin**: Terminal-first developer support
- **Emacs Package**: Emacs user support
- **Browser Extension**: GitHub Codespaces, GitPod, web IDE support

**Advanced Features**:

- **Cross-Tool Synchronization**: State sync across all tools
- **Cloud Sync**: Remote state backup and team collaboration
- **Analytics Dashboard**: Usage patterns, efficiency metrics
- **Multi-User Collaboration**: Lock achievements, see who's working on what
- **Batch Operations**: Archive multiple plans, generate multiple prompts
- **Custom Aliases**: User-defined command shortcuts

**Dependencies**:

- **Hard**: PLAN 1 (needs core API, plugin system)
- **Soft**: PLAN 2-5 (learnings from other integrations)

**Key Deliverables**:

- JetBrains plugin
- Neovim plugin
- Emacs package
- Browser extension
- Cross-tool sync system
- Cloud sync implementation
- Analytics dashboard
- Collaboration features
- Comprehensive integration guide

**Contributes To**: Universal Access + Extensibility goals - Platform works everywhere

**Success Metrics**:

- 6+ tools supported
- State synchronized across tools
- Analytics provide actionable insights
- Third-party plugins created

**Related Sections**: All previous PLANs (leverages learnings from all integrations)

**Location**: `work-space/plans/PLAN_EXTENDED-TOOLS-FEATURES.md`

---

## 🔗 Dependencies Between Children

### Foundation Dependency (Critical Path)

**PLAN 1 (Core) is HARD dependency for ALL others**:

```
PLAN 1: Universal CLI Core (Foundation)
└─→ PLAN 2: Cursor Integration    (Depends on: Core API, JSON-RPC)
└─→ PLAN 3: Claude Code Extension (Depends on: Core API, JSON-RPC)
└─→ PLAN 4: VS Code Extension     (Depends on: Core API, JSON-RPC)
└─→ PLAN 5: AI Assistants         (Depends on: Core API)
└─→ PLAN 6: Extended Tools        (Depends on: Core API, Plugin System)
```

**Coordination**: PLAN 1 must complete **Priority 0-1** (Core API + JSON-RPC stable) before others start Priority 1

### Parallel Opportunities (Maximum Efficiency)

**After PLAN 1 Priority 0-1 Complete**:

```
Phase 2: Parallel Work (High-Impact Integrations)
├─→ PLAN 2: Cursor     ┐
└─→ PLAN 4: VS Code    ├─→ Work simultaneously (independent tools)
                       ┘

Phase 3: Parallel Work (AI & Specialized)
├─→ PLAN 3: Claude Code ┐
└─→ PLAN 5: AI Assistants ├─→ Work simultaneously (different APIs)
                         ┘

Phase 4: Can Start Early
└─→ PLAN 6: Extended Tools (start JetBrains/Neovim while Phase 3 ongoing)
```

**Timeline Impact**:

- **Sequential**: 210-290 hours (5-7 months @ 40h/month)
- **Parallel** (ideal): 40-60h (foundation) + 40-50h (max parallel phase) = ~100-110 hours (2.5-3 months)
- **Realistic** (partial parallel): 130-180 hours (3-4.5 months)

### Soft Dependencies (Learning Transfer)

**PLAN 2 → PLAN 3, 4**:

- **Type**: Learning (extension patterns, configuration patterns)
- **Relationship**: Cursor integration learnings inform other IDE integrations
- **Status**: Can proceed without, but benefits from
- **Timing**: Share learnings in weekly sync

**PLAN 3 → PLAN 5**:

- **Type**: Learning (AI context injection patterns)
- **Relationship**: Claude Code AI integration informs Copilot integration
- **Status**: Can proceed without, but benefits from
- **Timing**: Review PLAN 3 patterns before PLAN 5 Priority 1

**PLAN 2, 3, 4 → PLAN 6**:

- **Type**: Learning (all integration patterns)
- **Relationship**: Extension learnings inform additional tools
- **Status**: Can proceed early, refine based on learnings
- **Timing**: PLAN 6 can start JetBrains work while PLAN 3-5 ongoing

### API Contract (Cross-Child Coordination)

**PLAN 1 Owns**: Core API definition

**API Surface**:

```python
class MethodologyAPI(Protocol):
    def list_plans(filters: dict) -> List[Plan]
    def get_plan(plan_id: str) -> Plan
    def load_plan(plan_id: str) -> PlanContext
    def generate_prompt(context: PlanContext) -> str
    def pause_plan(plan_id: str, reason: str) -> None
    def resume_plan(plan_id: str) -> None
    def verify_plan(plan_id: str) -> dict
    def archive_plan(plan_id: str) -> None
```

**All Other PLANs**: Consume this API (no modifications without cross-PLAN review)

**Coordination**: Weekly sync reviews any API change proposals, GrammaPlan coordinator approves breaking changes

---

## 🔄 Cross-Cutting Concerns

### 1. Core Engine (Infrastructure Layer)

**Provided By**: PLAN 1 (Universal CLI Core)

**Components**:

- **File Discovery Engine**: Scans work-space/ and archive/, indexes methodology files
- **Context Manager**: Tracks loaded PLAN/SUBPLAN, provides context to commands
- **Action Executors**: Wraps existing scripts (generate_prompt.py, etc.)
- **Plugin Registry**: Manages plugins, loads extensions
- **State Manager**: Persists context across sessions

**Used By**: All child PLANs (PLAN 2-6)

**Integration**: JSON-RPC API provides access, plugin system enables extensions

### 2. User Experience Patterns (Design System)

**Shared Across All Tools**:

**Visual Language**:

- ✅ Green = success/completed
- ⚠️ Yellow = warnings/pending
- ❌ Red = errors/failed
- 🔵 Blue = info/active
- 🌟 Gold = special status

**Command Structure**:

- Discovery: `<type>s` (plans, subplans, executions)
- Context: `load <id>`, `context`, `clear`
- Actions: `<action>` (generate_prompt, pause, resume)
- Info: `status`, `stats`, `help <command>`

**Error Messages**:

- Always actionable
- Show what was tried
- Suggest next steps
- Link to documentation

**Coordination**: PLAN 1 defines patterns, PLAN 2-6 implement consistently

### 3. Testing Strategy (Quality Assurance)

**Applies To**: All child PLANs

**Requirements**:

- Unit tests: >90% coverage (all new code)
- Integration tests: Cross-module workflows
- End-to-end tests: Full user workflows
- Performance tests: <5s response time for discovery
- Accessibility tests: Screen reader compatibility

**Coordination**: PLAN 1 provides test infrastructure, others follow patterns

### 4. Documentation Architecture (Knowledge Management)

**Structure**:

```
LLM/cli/
├── README.md (Platform overview)
├── QUICK-START.md (5-minute getting started)
├── USER-GUIDE.md (Complete user documentation)
├── DEVELOPER-GUIDE.md (Plugin development guide)
├── API-REFERENCE.md (API documentation)
└── INTEGRATION-GUIDES/
    ├── CURSOR.md
    ├── CLAUDE-CODE.md
    ├── VSCODE.md
    └── ... (one per tool)
```

**Coordination**: Each PLAN contributes its documentation, PLAN 1 provides structure

### 5. Release & Distribution (Go-to-Market)

**Release Strategy**:

- **Beta** (Phase 1): CLI only, internal validation
- **v1.0** (Phase 2): CLI + top 2 integrations (Cursor, VS Code)
- **v1.5** (Phase 3): + Claude Code + Copilot
- **v2.0** (Phase 4): Full platform with extended tools

**Distribution Channels**:

- PyPI: `pip install llm-methodology-cli`
- Homebrew: `brew install llm-methodology-cli`
- Cursor Marketplace: Native extension
- Claude Code Marketplace: Native extension
- VS Code Marketplace: Extension
- GitHub: Source code, releases, documentation

**Coordination**: Each PLAN prepares its distribution, PLAN 1 coordinates releases

---

## 📊 Strategic Execution Model

**Implementation Approach**: Foundation → Integrations → Ecosystem (Hybrid pattern)

**Phase 1** (Foundation): Core engine + CLI establishes API and UX patterns  
**Phase 2** (High-Impact): Cursor + VS Code reach majority of users  
**Phase 3** (AI Ecosystem): Claude Code + Copilot integrate AI assistants  
**Phase 4** (Extended): Additional tools + advanced features complete platform

**Parallelism Strategy**: Foundation sequential (API stability), integrations parallel (independent tools), enables 2x speedup

**Timeline**: 12-16 weeks with strategic milestones at Weeks 3 (Beta), 7 (v1.0), 11 (v1.5), 16 (v2.0)

**Detailed execution**: See GRAMMAPLAN_UNIVERSAL-METHODOLOGY-CLI.md for tactical coordination

---

## 🎯 Success Criteria

### Must Have (Product Launch)

- [x] **PLAN 1 Complete**: Core engine and CLI working (foundation)
- [ ] **PLAN 2 Complete**: Cursor integration published
- [ ] **PLAN 4 Complete**: VS Code extension published
- [ ] **Beta → v1.0**: Two releases successfully deployed
- [ ] **User Adoption**: >50 active users within first month
- [ ] **Quality**: >90% test coverage across all PLANs
- [ ] **Documentation**: Complete user guide and API reference

### Should Have (Product Excellence)

- [ ] **PLAN 3 Complete**: Claude Code extension published
- [ ] **PLAN 5 Complete**: AI assistants integrated
- [ ] **v1.5 Release**: AI ecosystem integrated
- [ ] **User Satisfaction**: >4.5/5 stars in feedback
- [ ] **Performance**: <5s response for all operations
- [ ] **Accessibility**: Screen reader compatible

### Nice to Have (Ecosystem Leadership)

- [ ] **PLAN 6 Complete**: Extended tools supported
- [ ] **v2.0 Release**: Full platform deployed
- [ ] **Third-Party Plugins**: 3+ community plugins created
- [ ] **Market Leadership**: Recognized as category standard
- [ ] **Open Source**: 100+ GitHub stars

---

## 📊 Progress Tracking

### Overall Progress Formula

```
GrammaPlan Progress =
    (PLAN_1_Progress * 50h +     # Core foundation
     PLAN_2_Progress * 25h +     # Cursor
     PLAN_3_Progress * 35h +     # Claude Code
     PLAN_4_Progress * 45h +     # VS Code
     PLAN_5_Progress * 25h +     # AI Assistants
     PLAN_6_Progress * 70h)      # Extended
    /
    250h (total)

Current: 0% (0h / 250h)
```

### Child PLAN Status Summary

| Child PLAN            | Status      | Progress | Effort | Next Milestone           |
| --------------------- | ----------- | -------- | ------ | ------------------------ |
| PLAN 1: CLI Core      | ⏳ Planning | 0%       | 0/50h  | Create PLAN 1            |
| PLAN 2: Cursor        | ⏳ Pending  | 0%       | 0/25h  | Awaits PLAN 1 Priority 1 |
| PLAN 3: Claude Code   | ⏳ Pending  | 0%       | 0/35h  | Awaits PLAN 1 Priority 1 |
| PLAN 4: VS Code       | ⏳ Pending  | 0%       | 0/45h  | Awaits PLAN 1 Priority 1 |
| PLAN 5: AI Assistants | ⏳ Pending  | 0%       | 0/25h  | Awaits PLAN 1 Priority 1 |
| PLAN 6: Extended      | ⏳ Pending  | 0%       | 0/70h  | Awaits PLAN 1 Priority 2 |

**Recommended Next**: Create PLAN 1 (Universal CLI Core) - Foundation for entire initiative

---

## 📝 Current Status & Handoff (For Pause/Resume)

**Last Updated**: 2025-11-08 16:30 UTC  
**Status**: 📋 Strategic Planning (GrammaPlan created, ready for execution)

**Completed Children**: None (just starting)

**In Progress Children**: None yet

**Pending Children**: All 6 PLANs (awaiting PLAN 1 creation)

**Next Steps**:

1. **Immediate**: Create PLAN 1 (Universal CLI Core) using IMPLEMENTATION_START_POINT.md
2. **Reference**: Use PLAN-TEMPLATE.md for structure
3. **Detail**: Expand on specifications from EXECUTION_ANALYSIS_TERMINAL-INTERACTIVE-METHODOLOGY-CONTROL.md
4. **Start**: Begin Phase 1 (Foundation) execution

**When Resuming** (if paused):

1. Read this "Current Status & Handoff" section
2. Review Child PLAN Status Summary table
3. Check Cross-PLAN Dependencies (is foundation ready?)
4. Follow IMPLEMENTATION_RESUME.md for active child PLAN
5. Coordinate with other active children (if multiple in progress)

**Strategic Context Preserved**: This GrammaPlan + 2 analyses + North Star PLANs = full strategic context

---

## 🔗 Decomposition Pattern Used

**Pattern**: **Hybrid Decomposition** (Foundation → Integrations → Extensions)

**Rationale**:

Work has both **phase dimension** (foundation must complete first) and **domain dimension** (different tools are independent). Hybrid approach combines both:

- **Phase 1**: Foundation (PLAN 1) - Must complete before others
- **Phases 2-3**: Integrations (PLAN 2-5) - Can parallelize by tool
- **Phase 4**: Extensions (PLAN 6) - Builds on all learnings

**Why Not Domain-Only**: Foundation dependency requires phase approach

**Why Not Phase-Only**: Integrations have no inter-dependencies, pure parallelism possible

**Result**: Optimal parallelism (Phase 2-3 can run 2 PLANs simultaneously) while respecting foundation dependency

**See**: `LLM/guides/GRAMMAPLAN-GUIDE.md` - Hybrid Decomposition pattern

---

## ⚠️ Constraints

### Technical Constraints

**Platform Requirements**:

- Python 3.8+ (for core engine)
- Node.js 18+ (for extensions)
- Platform support: macOS, Linux, Windows

**Tool API Limitations**:

- Cursor: Extension API may be limited (research needed in PLAN 2)
- Claude Code: Extension capabilities TBD (research needed in PLAN 3)
- VS Code: Mature extension API (well-documented)
- Copilot: Limited plugin API (workarounds may be needed in PLAN 5)

**Performance Requirements**:

- Discovery operations: <5 seconds
- Prompt generation: <3 seconds
- File indexing: <10 seconds for 1000 files

### Process Constraints

**Sequential Foundation**:

- PLAN 1 must stabilize API before PLAN 2-6 can complete
- API breaking changes require cross-PLAN review and versioning
- Only PLAN 1 Priority 0-1 needs sequential execution

**Quality Gates**:

- > 90% test coverage required for each PLAN
- Integration tests required before PLAN marked complete
- User acceptance testing required before releases

**Coordination**:

- Weekly sync meetings (all active PLAN leads)
- API changes require 24h review period
- Breaking changes need GrammaPlan coordinator approval

### Resource Constraints

**Development**:

- Single developer → Sequential or light parallelism
- Small team (2-3) → Can parallelize Phase 2-3
- Methodology focus → Can't compromise other work

**Timeline**:

- Target: 12-16 weeks from start
- Flexible: Can extend if quality needs more time
- Milestone-based: Each phase must complete before next

---

## 🚨 Key Risks & Mitigation

| Risk                          | Impact | Probability | Mitigation                                                          | Owner                  |
| ----------------------------- | ------ | ----------- | ------------------------------------------------------------------- | ---------------------- |
| **API Instability**           | High   | Medium      | Versioning from day 1, comprehensive tests, change protocol         | PLAN 1 Lead            |
| **Tool-Specific Limitations** | Medium | High        | Early capability research, graceful degradation, fallbacks          | Integration Leads      |
| **Scope Creep**               | High   | High        | Strict boundaries per PLAN, backlog for features, approval required | GrammaPlan Coordinator |
| **Cross-PLAN Coordination**   | High   | Low         | Weekly syncs, shared API contract, integration tests                | GrammaPlan Coordinator |
| **User Adoption Low**         | High   | Medium      | Beta testing, user feedback loop, iterative UX improvements         | Product Owner          |
| **Performance Issues**        | Medium | Low         | Performance tests, profiling, optimization focus in PLAN 1          | PLAN 1 Lead            |

### Risk Details

**Risk 1: API Instability**

**Scenario**: Core API changes frequently, breaking all integrations

**Prevention**:

- Design API carefully in PLAN 1 Priority 0
- Comprehensive API tests (>95% coverage)
- Versioning strategy from start
- Breaking change protocol

**Response** (if occurs):

- Emergency sync meeting
- Evaluate impact across PLANs
- Version bump + migration guide
- Update all integrations

**Risk 2: Tool-Specific Limitations**

**Scenario**: IDE capabilities insufficient for full integration

**Prevention**:

- Research tool APIs early (in PLAN planning phase)
- Design with graceful degradation
- Multiple integration approaches

**Response** (if occurs):

- Implement fallback approach
- Document limitations
- Set user expectations
- Consider alternative tools

---

## 📋 Coordination Protocols

### Weekly Sync Meeting

**Attendees**: All active PLAN leads + GrammaPlan coordinator

**Agenda** (60 minutes):

1. Progress updates (5 min per active PLAN)
2. API change proposals review
3. Dependency coordination (blockers, handoffs)
4. Risk review and mitigation
5. Next week priorities and coordination

**Output**: Sync notes, updated GrammaPlan status, action items

### API Change Protocol

**When**: Any PLAN proposes API modification

**Process**:

1. Proposer documents change in shared doc
2. All PLAN leads review (24h async)
3. Discussion in sync meeting if needed
4. GrammaPlan coordinator decides
5. If breaking change: version bump + migration guide
6. All impacted PLANs updated

**Approval**: Coordinator has final say, considers all input

### Integration Testing Protocol

**When**: Before any child PLAN marks complete

**Process**:

1. Child PLAN runs internal tests (>90% coverage)
2. Integration tests with PLAN 1 (API contract validated)
3. Cross-PLAN smoke tests (if dependencies exist)
4. User acceptance testing (workflow validation)
5. GrammaPlan coordinator approves completion

**Coordination**: PLAN 1 provides test harness, all children use it

### Release Coordination

**When**: Preparing any release (Beta, v1.0, v1.5, v2.0)

**Process**:

1. All required PLANs for release complete
2. Integration testing passed
3. Documentation complete and reviewed
4. Release notes drafted
5. Deployment tested in staging
6. GrammaPlan coordinator approves release
7. Deploy to production
8. Monitor for issues
9. Gather user feedback

**Coordination**: All PLAN leads involved in release planning

---

## 🎓 Learning & Evolution

### Cross-PLAN Learning Mechanism

**Shared Learnings Document**: `work-space/GRAMMAPLAN-LEARNINGS_UNIVERSAL-CLI.md`

**Updated**: After each child PLAN completes achievement

**Content**:

- **API Design Patterns**: What worked, what didn't in API design
- **Integration Challenges**: Tool-specific gotchas and solutions
- **UX Insights**: User feedback and improvements
- **Performance Patterns**: Optimization techniques that worked
- **Testing Strategies**: Effective test approaches

**Process**:

1. PLAN lead documents learning in shared doc
2. Weekly sync discusses significant learnings
3. Learnings applied to pending children
4. Patterns extracted to guidelines

### Methodology Improvement Feedback Loop

**Process**: Learnings feed back to meta-PLANs

**Coordination**:

1. PLAN leads identify methodology patterns (what worked/didn't)
2. GrammaPlan coordinator synthesizes quarterly
3. Propose updates to PLAN_STRUCTURED-LLM-DEVELOPMENT.md
4. Meta-PLAN owner reviews and incorporates

**Frequency**: End of each phase (4 times total)

**Examples**:

- If GrammaPlan coordination overhead >10%, methodology needs improvement
- If cross-PLAN coordination fails, protocols need enhancement
- If testing patterns emerge, testing guide needs update

---

## 🚀 Release & Delivery Strategy

### Beta Release (Post-Phase 1)

**Target**: Week 3  
**Scope**: Terminal CLI only  
**Audience**: Internal methodology users (5-10 people)

**Goal**: Validate core experience

**Success Criteria**:

- All core commands working
- > 90% test coverage
- User feedback collected
- Major bugs fixed

**Distribution**: GitHub release, internal documentation

---

### v1.0 Release (Post-Phase 2)

**Target**: Week 7  
**Scope**: CLI + Cursor + VS Code  
**Audience**: Early adopters (50-100 people)

**Goal**: Validate integrations

**Success Criteria**:

- 2 IDE integrations working
- Extensions published to marketplaces
- User onboarding complete
- Documentation comprehensive

**Distribution**: PyPI, Homebrew, Cursor Marketplace, VS Code Marketplace

---

### v1.5 Release (Post-Phase 3)

**Target**: Week 11  
**Scope**: + Claude Code + Copilot  
**Audience**: Broader community (500+ people)

**Goal**: Expand AI ecosystem

**Success Criteria**:

- AI integrations working
- Context-aware assistance validated
- User satisfaction >4.5/5
- Community forming

**Distribution**: All Phase 2 channels + Claude Code Marketplace

---

### v2.0 Release (Post-Phase 4)

**Target**: Week 16  
**Scope**: Full platform  
**Audience**: General availability (open to all)

**Goal**: Establish as category standard

**Success Criteria**:

- 6+ tools supported
- Advanced features working
- Third-party plugins emerging
- Market recognition as standard

**Distribution**: All previous channels + blog posts, social media campaign

---

## 📊 Success Metrics (GrammaPlan Level)

### Product Adoption Metrics

**User Growth**:

- Beta: 5-10 users (internal)
- v1.0: 50-100 users (early adopters)
- v1.5: 500+ users (community)
- v2.0: 2,000+ users (general availability)

**Engagement**:

- CLI usage vs. manual scripts: Target 80% CLI adoption
- Daily active users: Target 50% of registered users
- Commands per session: Target 10+ (indicates active usage)
- Return rate: Target 80% users return after 1 week

### Technical Excellence Metrics

**Quality**:

- Test coverage: >90% across all 6 PLANs
- Error rate: <1% of operations
- Performance: <5 seconds for discovery, <3 seconds for prompts
- Uptime: >99.9% (JSON-RPC server)

**Code Health**:

- Technical debt ratio: <5%
- Code duplication: <3%
- Documentation coverage: 100% of public APIs
- Linter issues: 0

### Ecosystem Growth Metrics

**Integration Adoption**:

- Tool integrations: 6+ supported
- Marketplace listings: 4+ (Cursor, Claude Code, VS Code, + 1)
- Extension downloads: 1,000+ total
- Third-party plugins: 3+ community-created

**API Usage**:

- API calls per day: 1,000+ (indicates active integration)
- Plugin registrations: 10+ (ecosystem forming)
- API versions: 1.x (stability, backward compatibility)

### Business Impact Metrics

**Efficiency Improvements**:

- Time saved per operation: 70% reduction
- Workflow completion rate: 90% (users complete intended workflows)
- Context switching: 80% reduction
- Cognitive load: Measured via user surveys, target "much easier"

**User Satisfaction**:

- Overall rating: >4.5/5 stars
- Net Promoter Score: >50
- Support tickets: <5 per 100 users per month
- Feature requests: Collected and prioritized

---

## 🎯 Strategic Decision Log

### Decision 1: Hybrid vs. Phase-Only Decomposition

**Date**: 2025-11-08  
**Context**: Choosing decomposition pattern

**Options Considered**:

- **Phase-Only**: Foundation → Integrations → Extensions (purely sequential)
- **Domain-Only**: By tool (Cursor, VS Code, etc.) - ignores foundation dependency
- **Hybrid**: Foundation phase, then parallel integrations

**Decision**: **Hybrid Decomposition**

**Rationale**:

- Foundation must complete first (API stability critical)
- Integrations are independent after foundation (maximize parallelism)
- Extensions build on all learnings (naturally last)

**Impact**: Enables 2x parallelism in Phase 2-3, reduces timeline by 4-6 weeks

---

### Decision 2: CLI-First vs. Extension-First

**Date**: 2025-11-08  
**Context**: What to build first

**Options Considered**:

- **Extension-First**: Build VS Code extension, then extract CLI
- **CLI-First**: Build terminal CLI, then add integrations
- **Parallel**: Build both simultaneously

**Decision**: **CLI-First** (PLAN 1 is terminal CLI + core engine)

**Rationale**:

- CLI provides universal access (works everywhere)
- Core engine abstracts methodology operations (reusable)
- Terminal CLI provides test harness for integrations
- Enables beta release faster (no marketplace approval delays)

**Impact**: Beta release 2-3 weeks earlier, better foundation for integrations

---

### Decision 3: JSON-RPC vs. REST vs. gRPC

**Date**: 2025-11-08  
**Context**: API protocol selection

**Options Considered**:

- **JSON-RPC**: Simple, language-agnostic, standard
- **REST**: Web-friendly, widely understood
- **gRPC**: High-performance, typed
- **All Three**: Maximum flexibility

**Decision**: **JSON-RPC primary, REST secondary** (in PLAN 1)

**Rationale**:

- JSON-RPC: Simple, perfect for tool integrations
- REST: Add for web-based tools (GitHub Codespaces, etc.)
- gRPC: Overkill for this use case (premature optimization)

**Impact**: Simpler implementation, faster delivery, sufficient for all use cases

---

## ⚠️ Integration Strategy & Validation

### Integration Points

**API Contract** (Managed by PLAN 1):

```typescript
// All integrations consume this API
interface MethodologyAPI {
  listPlans(filters: object): Plan[];
  getPlan(planId: string): Plan;
  loadPlan(planId: string): PlanContext;
  generatePrompt(context: PlanContext): string;
  pausePlan(planId: string, reason: string): void;
  resumePlan(planId: string): void;
  verifyPlan(planId: string): ValidationResult;
  archivePlan(planId: string): void;
}
```

**Integration Testing** (Cross-PLAN):

1. **API Contract Tests**: PLAN 1 provides test suite, all children run it
2. **Smoke Tests**: Basic workflow in each integration
3. **Integration Tests**: Cross-tool workflows (load in CLI, resume in VS Code)
4. **UAT**: Real users test complete workflows

### Validation Before Completion

**Each Child PLAN Must**:

1. Run `validate_plan_completion.py` (all achievements complete)
2. Run API contract tests (if integration PLAN)
3. Complete integration testing
4. Obtain GrammaPlan coordinator approval
5. Update this GrammaPlan status

**GrammaPlan Completion Requires**:

1. All required children complete (PLAN 1-4 required, PLAN 5-6 optional)
2. Cross-PLAN integration validated
3. v1.0 or v2.0 successfully released
4. User adoption metrics met

---

## ⏱️ Time Estimates

### Per Child PLAN

- **PLAN 1: Universal CLI Core**: 40-60 hours (foundation complexity)
- **PLAN 2: Cursor Integration**: 20-30 hours (simpler integration)
- **PLAN 3: Claude Code Extension**: 30-40 hours (full extension development)
- **PLAN 4: VS Code Extension**: 40-50 hours (comprehensive IDE integration)
- **PLAN 5: AI Assistants**: 20-30 hours (framework + Copilot)
- **PLAN 6: Extended Tools**: 60-80 hours (multiple tools + advanced features)

**Total Estimated**: 210-290 hours

### Breakdown by Priority

- **Critical** (PLAN 1): 40-60 hours
- **High** (PLAN 2-4): 90-120 hours
- **Medium** (PLAN 5-6): 80-110 hours

### Sequencing Impact

**If Sequential** (one at a time):

- Total: 210-290 hours
- Timeline: 5-7 months @ 40h/month
- **Not recommended**: Wastes parallelism opportunities

**If Fully Parallel** (ideal, unrealistic):

- Critical path: PLAN 1 (40-60h) + PLAN 4 (40-50h) = 80-110 hours
- Timeline: 2-3 months @ 40h/month
- **Not realistic**: Requires 6 developers

**Realistic** (partial parallelism):

- Phase 1: PLAN 1 (40-60h)
- Phase 2: PLAN 2 + PLAN 4 in parallel (max 40-50h)
- Phase 3: PLAN 3 + PLAN 5 in parallel (max 30-40h)
- Phase 4: PLAN 6 (60-80h, can start early)
- Total: 130-180 hours effective
- Timeline: 3-4.5 months @ 40h/month

---

## 🎯 Governance & Decision Authority

**Strategic Owner**: Methodology Team (Product)

**GrammaPlan Coordinator**: TBD (assigns at execution start)

**Decision Authority Matrix**:

| Decision Type            | Authority                  | Process                              |
| ------------------------ | -------------------------- | ------------------------------------ |
| **Scope Changes**        | GrammaPlan Coordinator     | Proposal → Review → Approve          |
| **API Changes**          | All PLAN Leads (consensus) | Propose → 24h review → Consensus     |
| **Breaking API Changes** | GrammaPlan Coordinator     | Propose → Review → Approve + Version |
| **Timeline Changes**     | Phase Lead → Coordinator   | Propose → Justify → Approve          |
| **Risk Escalation**      | Immediate to Coordinator   | Escalate → Assess → Mitigate         |
| **Feature Additions**    | To Backlog (not in-scope)  | Document → Backlog → Future          |
| **Release Approval**     | GrammaPlan Coordinator     | Criteria → Validate → Release        |

**Communication Channels**:

- **Weekly Sync**: Scheduled coordination (all PLAN leads)
- **Async Docs**: Shared GrammaPlan learnings doc
- **Urgent**: Dedicated Slack/Discord channel
- **API Changes**: GitHub issues + shared doc

---

## 🎓 Learning & Evolution

### Cross-PLAN Learning Mechanism

**Shared Document**: `work-space/GRAMMAPLAN-LEARNINGS_UNIVERSAL-CLI.md`

**Update Frequency**: After each child PLAN achievement completion

**Categories**:

- **API Design**: Patterns, anti-patterns, versioning learnings
- **Integration Challenges**: Tool-specific gotchas, workarounds, solutions
- **UX Insights**: User feedback, usability improvements, workflow optimizations
- **Performance**: Optimization techniques, profiling insights, bottlenecks
- **Testing**: Effective patterns, test infrastructure, coverage strategies

**Process**:

1. PLAN lead adds learning after significant discovery
2. Weekly sync reviews new learnings
3. Pending children adopt applicable patterns
4. Patterns extracted to guidelines (if recurring)

**Example Learning**:

```markdown
### Learning: Extension Command Registration Pattern

**Source**: PLAN 2 (Cursor Integration), Achievement 1.2
**Date**: 2025-11-XX
**Pattern**: Use declarative JSON config instead of imperative registration
**Applies To**: PLAN 3, 4 (all IDE extensions)
**Impact**: 30% less boilerplate code, easier to maintain
```

### Methodology Improvement Feedback Loop

**What**: Learnings from this GrammaPlan improve the methodology itself

**Process**:

1. **Identify**: PLAN leads identify methodology patterns during work
2. **Document**: Note patterns in completion summaries
3. **Synthesize**: GrammaPlan coordinator reviews at phase end
4. **Propose**: Draft updates to PLAN_STRUCTURED-LLM-DEVELOPMENT.md
5. **Review**: Meta-PLAN owner evaluates proposals
6. **Apply**: Incorporate into methodology if valuable

**Frequency**: End of each phase (4 review points)

**Examples of Improvable**:

- GrammaPlan coordination patterns (if we discover better approaches)
- Child PLAN sizing guidelines (if our estimates were off)
- Integration protocols (if we find better coordination methods)
- Testing requirements (if coverage needs adjustment)

---

## 📦 Release & Distribution Strategy

| Release  | Week | Scope           | Audience                | Goal                  |
| -------- | ---- | --------------- | ----------------------- | --------------------- |
| **Beta** | 3    | CLI only        | Internal (5-10)         | Validate core UX      |
| **v1.0** | 7    | +Cursor+VS Code | Early adopters (50-100) | Validate integrations |
| **v1.5** | 11   | +Claude+Copilot | Community (500+)        | AI ecosystem          |
| **v2.0** | 16   | Full platform   | General (2,000+)        | Category standard     |

**Distribution**: PyPI, Homebrew, IDE marketplaces (Cursor, Claude Code, VS Code, JetBrains)

**Marketing**: Blog posts, social media, community Discord/Slack, plugin showcase

**Detailed go-to-market**: See PLAN 6 for complete marketing and distribution strategy

---

## ✅ GrammaPlan Completion Criteria

**This GRAMMAPLAN is Complete When**:

### Required (Must Complete)

1. [ ] **PLAN 1 Complete**: Universal CLI Core (100%, all tests passing)
2. [ ] **PLAN 2 Complete**: Cursor CLI Integration (100%, published)
3. [ ] **PLAN 4 Complete**: VS Code Extension (100%, published)
4. [ ] **v1.0 Released**: CLI + 2 integrations deployed successfully
5. [ ] **User Adoption**: >50 active users, >80% satisfaction
6. [ ] **Quality Validated**: >90% test coverage, <1% error rate
7. [ ] **Documentation Complete**: User guide, API reference, tutorials

### Optional (Should Complete for Excellence)

8. [ ] **PLAN 3 Complete**: Claude Code Extension (100%, published)
9. [ ] **PLAN 5 Complete**: AI Assistants Integration (100%, working)
10. [ ] **v1.5 Released**: AI ecosystem integrated
11. [ ] **Community Forming**: >500 users, active discussions

### Nice to Have (Future Versions)

12. [ ] **PLAN 6 Complete**: Extended tools (100%, 6+ tools)
13. [ ] **v2.0 Released**: Full platform deployed
14. [ ] **Third-Party Ecosystem**: 3+ community plugins
15. [ ] **Market Recognition**: Industry acknowledgment as standard

### Dynamic Completion Note

- Child PLANs may add achievements during execution (standard methodology)
- Cross-PLAN dependencies may evolve (coordination adapts)
- GrammaPlan complete when strategic goals achieved (may exceed 100% of initial plan)
- Release strategy flexible based on user feedback

---

## 📊 Current State (Progress Toward Vision)

**Last Updated**: 2025-11-08 16:30 UTC  
**Vision Status**: 🌟 Articulated and Ready

### Where We Are Today

**Vision Defined** ✅:

- Strategic vision articulated (desired future state)
- 8 core principles established (guiding all decisions)
- Implementation path clear (GrammaPlan + 6 PLANs)
- Success criteria defined (product, technical, ecosystem)

**Implementation Status**: Pre-Execution (vision complete, execution starting)

**Current Reality**:

- **Manual workflows**: Developers use long terminal commands (slow, error-prone)
- **No tool integration**: Each tool used separately (context switching)
- **Scripts exist**: 15+ methodology scripts work but lack UX
- **Foundation strong**: Methodology validated (10+ PLANs, 200+ achievements, 0% circular debugging)

**Gap Between Current and Vision**:

- **No CLI**: Scripts work but poor UX
- **No integrations**: Tools work separately
- **No context management**: Manual tracking
- **No visual experience**: Text-only interfaces

**This NORTH_STAR Provides**: Clear path from current (functional scripts) to future (universal platform)

### Progress Toward Vision

**Strategic Milestones**:

- [x] Vision articulated (this document)
- [x] Principles defined (8 core principles)
- [ ] Foundation built (PLAN 1)
- [ ] First integrations (PLAN 2, 4)
- [ ] Platform launched (v1.0)
- [ ] Ecosystem forming (v2.0 + plugins)

**Current Phase**: Vision → Execution transition

**Next**: Create GRAMMAPLAN (tactical coordination), then create PLAN 1 (foundation implementation)

### Challenges Ahead

**Technical Challenges**:

- API stability (must avoid breaking changes)
- Tool API limitations (some IDEs have limited extension capabilities)
- Cross-tool state sync (maintaining consistency)
- Performance at scale (1000+ methodology files)

**Strategic Challenges**:

- Adoption inertia (developers used to manual scripts)
- Quality vs. speed (temptation to ship fast, sacrifice quality)
- Scope creep (many feature requests expected)
- Coordination overhead (6 PLANs need synchronization)

**Mitigation**: Principles guide us (#6 Production-Ready Quality, #3 Progressive Disclosure, #8 Automation with Control)

---

## 🔗 Decomposition Pattern: Hybrid (Foundation → Integrations → Extensions)

**Pattern Choice**: Hybrid Decomposition

**Structure**:

```
Phase 1: Foundation (Sequential - Must Complete First)
└── PLAN 1: Universal CLI Core

Phase 2: High-Impact Integrations (Parallel - After Foundation)
├── PLAN 2: Cursor CLI
└── PLAN 4: VS Code Extension

Phase 3: AI & Specialized (Parallel - After Foundation)
├── PLAN 3: Claude Code
└── PLAN 5: AI Assistants

Phase 4: Extended (Can Start Early, Finish Last)
└── PLAN 6: Extended Tools & Features
```

**Why Hybrid**:

- **Foundation Phase**: API must stabilize before integrations (phase dependency)
- **Integration Phase**: Tools are independent (domain parallelism)
- **Extension Phase**: Builds on all learnings (natural progression)

**Benefits**:

- Respects technical dependencies (foundation first)
- Maximizes parallelism (integrations work simultaneously)
- Enables early delivery (v1.0 after Phase 2, not waiting for all 6)
- Allows learning transfer (early integrations inform later ones)

**Alternative Considered**: Pure Phase Decomposition (Foundation → All Integrations → All Extensions)

**Why Not**: Would force sequential work where parallelism possible, extending timeline unnecessarily

---

## 📚 References & Resources

### Foundation Documents

**Methodology**:

- `LLM-METHODOLOGY.md` - Core 5-tier hierarchy, protocols, templates
- `LLM/guides/GRAMMAPLAN-GUIDE.md` - GrammaPlan creation and coordination
- `LLM/guides/MULTIPLE-PLANS-PROTOCOL.md` - Child PLAN coordination patterns
- `LLM/protocols/IMPLEMENTATION_START_POINT.md` - How to start child PLANs
- `LLM/protocols/IMPLEMENTATION_RESUME.md` - How to resume paused children
- `LLM/protocols/IMPLEMENTATION_END_POINT.md` - How to complete and archive

### North Star PLANs (Strategic Alignment)

**Meta-PLAN**:

- `work-space/plans/PLAN_STRUCTURED-LLM-DEVELOPMENT.md` (2,099 lines)
  - Defines methodology excellence vision
  - Core principles: TDD-inspired, Document to Learn, Fail/Improve Pipeline, Automation with Control
  - Status: 88% complete (15/17 achievements)
  - Alignment: This GrammaPlan implements tooling to achieve methodology excellence

**Multi-Agent Coordination**:

- `work-space/plans/PLAN_METHODOLOGY-V2-ENHANCEMENTS.md` (1,025 lines)
  - Defines funnel-based context management
  - Agent roles: Strategist, Planner, Designer, Executor
  - Status: 85% complete (11/13 achievements)
  - Alignment: This GrammaPlan implements tooling for multi-agent workflows

### Vision Analyses (Detailed Requirements)

**Terminal CLI Vision**:

- `documentation/archive/execution-analyses/planning-strategy/2025-11/EXECUTION_ANALYSIS_TERMINAL-INTERACTIVE-METHODOLOGY-CONTROL.md` (942 lines)
  - Details terminal CLI UX vision
  - Command specifications, visual experience, workflows
  - Implementation phases, technical architecture
  - Use this as primary reference for PLAN 1

**Tool Integration Architecture**:

- `documentation/archive/execution-analyses/planning-strategy/2025-11/EXECUTION_ANALYSIS_TERMINAL-CLI-TOOL-INTEGRATIONS.md` (1,591 lines)
  - Details integration architecture for all tools
  - Cursor, Claude Code, VS Code, Copilot, JetBrains, Neovim, Emacs
  - Universal API design, communication protocols, plugin system
  - Use this as primary reference for PLAN 2-6

### Technical References

**Existing Methodology Scripts** (To Wrap/Integrate):

- `LLM/scripts/generation/generate_prompt.py` - Prompt generation
- `LLM/scripts/generation/generate_pause_prompt.py` - Pause prompts
- `LLM/scripts/generation/generate_resume_prompt.py` - Resume prompts
- `LLM/scripts/generation/generate_verify_prompt.py` - Verification prompts
- `LLM/scripts/validation/validate_plan_completion.py` - Completion validation
- `LLM/scripts/archiving/manual_archive.py` - Archiving automation

**Inspiration** (CLI UX Best Practices):

- **Git CLI**: Command structure, context management, porcelain vs. plumbing commands
- **Kubectl**: Context switching, resource management, declarative commands
- **Docker CLI**: Visual output, status indicators, workflow patterns
- **gh** (GitHub CLI): Modern UX, interactive prompts, rich output
- **cargo** (Rust): Helpful error messages, project structure, command clarity

---

## 🎯 Expected Outcomes

**Short-term** (Week 3): Beta deployed, CLI working, internal validation, integration-ready API  
**Medium-term** (Week 7): v1.0 deployed, 50-100 users, 2 integrations, product-market fit validated  
**Long-term** (Week 16): v2.0 deployed, 2,000+ users, 6+ tools, category-defining product, ecosystem forming

---

## 📋 Immediate Next Steps

**To Start Execution**:

1. **Create PLAN 1** (Universal CLI Core)

   - Follow: `LLM/protocols/IMPLEMENTATION_START_POINT.md`
   - Template: `LLM/templates/PLAN-TEMPLATE.md`
   - Reference: `EXECUTION_ANALYSIS_TERMINAL-INTERACTIVE-METHODOLOGY-CONTROL.md` (detailed requirements)
   - Prompt: Use `LLM/templates/PROMPTS.md` → "Create New PLAN" prompt

2. **Setup Project Infrastructure**

   - Repository: Create `llm-methodology-cli` GitHub repo
   - Structure: Python package with CLI entry point
   - CI/CD: GitHub Actions for tests, linting, releases
   - Documentation: Docs site skeleton

3. **Register in ACTIVE_PLANS.md**

   - Add PLAN 1 to Active Plans section
   - Link from this GrammaPlan
   - Track progress

4. **Begin Execution**

   - Execute PLAN 1 Priority 0 (Foundation)
   - Weekly updates to this GrammaPlan
   - Coordinate via established protocols

5. **Prepare for Phase 2**
   - Draft PLAN 2 and PLAN 4 (can prepare while PLAN 1 executes)
   - Research tool APIs and capabilities
   - Identify integration patterns from PLAN 1 learnings

---

## 🌟 Product Vision Statement

**"Universal Methodology Management for the AI-Assisted Development Era"**

This platform establishes the **methodology management tooling category**, providing developers with a unified, powerful interface to manage LLM-assisted development workflows across any tool, any environment, any scale.

By combining:

- **Rich terminal experience** (beautiful CLI with modern UX)
- **Seamless tool integration** (native in Cursor, Claude Code, VS Code, Copilot, and more)
- **Intelligent context management** (load once, use everywhere)
- **Production-ready quality** (>90% coverage, enterprise reliability)

We enable developers to:

- **Focus on building** (platform handles methodology mechanics)
- **Work in their favorite tools** (zero context switching)
- **Navigate 10x faster** (single commands replace complex workflows)
- **Achieve methodology excellence** (quality and structure as default path)

**The Result**: LLM-assisted development that's structured, traceable, high-quality, and effortless.

---

**Status**: 📋 Strategic Planning Complete - Ready for Phase 1 Execution  
**Next**: Create PLAN 1 (Universal CLI Core) following IMPLEMENTATION_START_POINT.md  
**Archive Location**: `documentation/archive/grammaplan-universal-cli-YYYY-MM/` (when complete)

---

## 🔄 Evolution History

### Version 1.0 - 2025-11-08

**Vision at This Time**: Universal methodology CLI platform with seamless tool integration

**Context**: Created from comprehensive analyses exploring terminal CLI vision and tool integration architecture. Two analyses (942 and 1,591 lines) provided detailed foundation.

**Key Insights**:

- Modern CLI UX patterns from industry research
- Integration architecture spanning 6+ development tools
- Universal API design enabling cross-tool coordination
- Product vision aligned with methodology North Star PLANs

**Status**: ✅ Current

**Learnings**:

- Vision emerged from analyzing user pain points (long commands, context switching, manual tracking)
- 8 principles extracted from studying modern CLI tools and methodology experience
- Hybrid decomposition pattern chosen for optimal parallelism
- North Star format chosen over GrammaPlan (document naturally 1,850+ lines, vision and principles heavy)

---

## 🎯 How to Use This North Star

**For Developers Creating PLANs**:

- Consult principles when making design decisions
- Ensure features align with vision (universal access, superior UX)
- Reference user personas and workflows
- Check coordinating initiatives for dependencies

**For LLMs Executing Work**:

- Read vision to understand strategic context
- Apply principles to implementation decisions (e.g., Principle #1 guides UX choices)
- Align tactical work with strategic goals
- Propose principle-driven solutions

**For Strategists Planning**:

- Ensure new initiatives align with this vision
- Reference principles when evaluating proposals
- Update this North Star as understanding deepens
- Coordinate with GrammaPlan for tactical execution

**For Product Decisions**:

- Vision guides "what to build" (universal, delightful, production-ready)
- Principles guide "how to build" (progressive disclosure, extensibility, quality)
- Current State identifies gaps (what's missing)
- Success Criteria measures achievement (are we there yet?)

---

## 🔄 Maintenance

**Review Frequency**: Quarterly (every 3 months) + after each phase completion

**Review Questions**:

- [ ] Does vision still inspire? (Are we excited about the future state?)
- [ ] Are principles still relevant? (Do they guide real decisions?)
- [ ] Has understanding shifted? (Have we learned something fundamental?)
- [ ] Do current initiatives align? (Are PLANs serving the vision?)
- [ ] Should vision evolve? (Is there a better future state?)

**Update Triggers**:

- Major learnings from implementation (e.g., "CLI UX should be X not Y")
- Shift in strategic context (e.g., new competing tools emerge)
- New principles discovered (patterns from building the platform)
- Vision no longer inspiring (need to articulate better future)
- Misalignment detected (PLANs drifting from vision)

**Evolution Process**:

1. Identify need for evolution (trigger or scheduled review)
2. Draft updated vision/principles (preserve old in history)
3. Review with methodology team
4. Update this North Star document
5. Add new version to Evolution History
6. Communicate changes to all active PLANs
7. Ensure GrammaPlan and child PLANs align

---

**Status**: 🌟 Strategic Vision Active - Illuminating Implementation  
**Next**: Create GRAMMAPLAN for tactical coordination, then execute Phase 1  
**Maintenance**: Quarterly reviews + phase-end updates

---

**Total Lines**: ~1,783 (within 800-2,000 NORTH_STAR range)  
**Validation**: NORTH_STAR format appropriate for strategic vision + principles document  
**Template**: Based on `LLM/templates/NORTH_STAR-TEMPLATE.md`  
**Guide**: Follows `LLM/guides/NORTH-STAR-GUIDE.md`  
**Archive Location** (when superseded): `documentation/archive/north-stars/universal-methodology-cli-YYYY-MM/`
