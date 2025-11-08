# EXECUTION_ANALYSIS: Dashboard Features for Methodology Visibility (Beta)

**Category**: Planning & Strategy  
**Created**: 2025-11-08 21:00 UTC  
**Status**: Analysis Complete  
**Related**: `GRAMMAPLAN_UNIVERSAL-CLI-CORE-FOUNDATION.md`, `ACTIVE_PLANS.md`, `LLM-METHODOLOGY.md`

---

## 🎯 Objective

Analyze dashboard features for providing visibility on methodology entities (NORTH_STAR, GRAMMAPLAN, PLAN, SUBPLAN, EXECUTION_TASK, EXECUTION_ANALYSIS) as a beta test for the Universal CLI Core Foundation, identifying what features to implement in a simple first version.

**Goal**: Define MVP dashboard features that provide immediate value while testing the Core Engine and Terminal CLI infrastructure.

**Context**: User wants dashboards to "give more visibility on the state of the entities" and "organically improve it" - this aligns with beta testing the CLI foundation while providing real value.

---

## 📊 Current State Analysis

### Existing Visibility Mechanisms

**1. ACTIVE_PLANS.md** (Manual Dashboard):
- ✅ Tracks NORTH_STAR, GrammaPlans, PLANs
- ✅ Status, Priority, Completion, Last Updated
- ✅ Statistics (active/paused counts, achievements, time)
- ✅ Recently completed PLANs
- ❌ **Manual updates** (error-prone, time-consuming)
- ❌ **No real-time data** (static snapshot)
- ❌ **No drill-down** (can't see SUBPLAN/EXECUTION details)

**2. PLAN Internal Tracking**:
- ✅ "Subplan Tracking" section in each PLAN
- ✅ Statistics (SUBPLANs, EXECUTION_TASKs, iterations, time)
- ✅ Active components tracking
- ❌ **Scattered** (one per PLAN, no aggregate view)
- ❌ **Manual updates** (requires discipline)
- ❌ **No cross-PLAN visibility**

**3. File System Organization**:
- ✅ `work-space/plans/` - PLAN files
- ✅ `work-space/subplans/` - SUBPLAN files
- ✅ `work-space/execution/` - EXECUTION_TASK files
- ✅ `work-space/grammaplans/` - GrammaPlan files
- ✅ `work-space/north-stars/` - NORTH_STAR files
- ❌ **No automated discovery** (manual file scanning)
- ❌ **No metadata aggregation** (must read each file)

### What's Missing

**Visibility Gaps**:
1. **No Real-Time Status**: Manual updates mean stale data
2. **No Aggregate Views**: Can't see all entities at once
3. **No Drill-Down**: Can't navigate from GrammaPlan → PLAN → SUBPLAN → EXECUTION
4. **No Cross-Entity Analysis**: Can't compare PLANs, find patterns
5. **No Automated Statistics**: Manual calculation, error-prone

**Beta Test Opportunity**:
- Core Engine (PLAN 1) provides file discovery and data models
- Terminal CLI (PLAN 2) provides rich UI rendering
- Dashboard features test both components end-to-end

---

## 🎯 Dashboard Requirements

### Entity Types to Display

**1. NORTH_STAR**:
- Status (Active Vision, Evolving, Reference, Archived)
- Scope (what it coordinates)
- Created date
- Coordinates (GrammaPlans/PLANs)

**2. GRAMMAPLAN**:
- Status (Planning, Active, Paused, Complete)
- Priority (CRITICAL, HIGH, MEDIUM)
- Progress (X/Y PLANs complete, percentage)
- Child PLANs (list with status)
- Last updated
- Next action

**3. PLAN**:
- Status (Planning, Active, Paused, Complete)
- Priority (CRITICAL, HIGH, MEDIUM, LOW)
- Progress (X/Y achievements, percentage)
- Parent (GrammaPlan or None)
- Last updated
- Next achievement
- Statistics (SUBPLANs, EXECUTION_TASKs, time spent)

**4. SUBPLAN**:
- Status (Planning, In Progress, Complete)
- Parent PLAN and achievement
- Progress (EXECUTION_TASKs complete)
- Last updated
- Execution strategy (single/multiple, parallel/sequential)

**5. EXECUTION_TASK**:
- Status (Planning, Executing, Complete, Failed, Abandoned)
- Parent SUBPLAN
- Iterations count
- Time spent
- Last updated

**6. EXECUTION_ANALYSIS** (orphaned work):
- Category (Bug, Methodology, Implementation, Process, Planning)
- Status (Active, Complete, Archived)
- Related PLANs
- Created date

---

## 💡 Simple First Version Features

### Feature Set 1: Entity Discovery & Listing (MVP Core)

**Purpose**: Test Core Engine file discovery and data models

**Features**:

1. **List All Entities**:
   - `dashboard list --type [north-star|grammaplan|plan|subplan|execution|analysis]`
   - Shows all entities of type with basic info
   - Tests: File discovery, data model parsing

2. **Entity Count**:
   - `dashboard count`
   - Shows counts per entity type
   - Tests: Aggregation logic

3. **Status Summary**:
   - `dashboard status`
   - Shows status distribution (Active: 5, Paused: 3, Complete: 10)
   - Tests: Status parsing, aggregation

**Deliverables**:
- Core Engine: `list_entities()`, `count_entities()`, `get_status_summary()`
- CLI: `dashboard list`, `dashboard count`, `dashboard status`
- Rich tables using `rich` library

**Effort**: 2-3 hours (tests Core Engine + CLI integration)

---

### Feature Set 2: Hierarchy Navigation (MVP Enhancement)

**Purpose**: Test data model relationships and navigation

**Features**:

1. **Show Entity Details**:
   - `dashboard show <entity-id>`
   - Shows full details for one entity
   - Tests: Data model completeness

2. **Show Hierarchy**:
   - `dashboard hierarchy <grammaplan-id>`
   - Shows GrammaPlan → PLANs → SUBPLANs → EXECUTIONs
   - Tests: Relationship traversal

3. **Show Parent/Children**:
   - `dashboard children <plan-id>` (shows SUBPLANs)
   - `dashboard parent <subplan-id>` (shows PLAN)
   - Tests: Bidirectional relationships

**Deliverables**:
- Core Engine: `get_entity()`, `get_children()`, `get_parent()`, `get_hierarchy()`
- CLI: `dashboard show`, `dashboard hierarchy`, `dashboard children`, `dashboard parent`
- Tree visualization using `rich.tree`

**Effort**: 3-4 hours (tests relationship models)

---

### Feature Set 3: Progress Dashboard (MVP Value)

**Purpose**: Test statistics aggregation and progress calculation

**Features**:

1. **Progress Overview**:
   - `dashboard progress`
   - Shows progress for all active PLANs/GrammaPlans
   - Table: Entity | Status | Progress | Next Action
   - Tests: Progress calculation, status parsing

2. **Statistics Summary**:
   - `dashboard stats`
   - Shows aggregate statistics (total achievements, time spent, etc.)
   - Tests: Statistics aggregation

3. **Active Work**:
   - `dashboard active`
   - Shows all active entities (PLANs, SUBPLANs, EXECUTION_TASKs)
   - Tests: Status filtering

**Deliverables**:
- Core Engine: `calculate_progress()`, `aggregate_statistics()`, `get_active_entities()`
- CLI: `dashboard progress`, `dashboard stats`, `dashboard active`
- Rich tables with progress bars

**Effort**: 3-4 hours (tests statistics logic)

---

### Feature Set 4: Filtering & Search (MVP Enhancement)

**Purpose**: Test query capabilities and filtering

**Features**:

1. **Filter by Status**:
   - `dashboard list --status active`
   - Shows only active entities
   - Tests: Status filtering

2. **Filter by Priority**:
   - `dashboard list --priority critical`
   - Shows only CRITICAL entities
   - Tests: Priority filtering

3. **Search by Name**:
   - `dashboard search <query>`
   - Searches entity names/descriptions
   - Tests: Text search

**Deliverables**:
- Core Engine: `filter_entities()`, `search_entities()`
- CLI: `dashboard list --status`, `dashboard list --priority`, `dashboard search`
- Filter logic

**Effort**: 2-3 hours (tests query capabilities)

---

## 🎯 Recommended MVP Feature Set

### Phase 1: Core Discovery (Week 1) - 2-3 hours

**Features**:
1. ✅ `dashboard list` - List all entities by type
2. ✅ `dashboard count` - Entity counts
3. ✅ `dashboard status` - Status summary

**Why First**: Tests Core Engine file discovery and basic data models. Minimal complexity, maximum foundation validation.

**Beta Test Value**: Validates Core Engine (PLAN 1) file discovery and data model parsing.

---

### Phase 2: Navigation (Week 1-2) - 3-4 hours

**Features**:
4. ✅ `dashboard show <id>` - Entity details
5. ✅ `dashboard hierarchy <grammaplan-id>` - Show hierarchy tree
6. ✅ `dashboard children <id>` - Show children
7. ✅ `dashboard parent <id>` - Show parent

**Why Second**: Tests relationship models and navigation. Builds on Phase 1.

**Beta Test Value**: Validates Core Engine relationship traversal and CLI tree rendering.

---

### Phase 3: Progress & Statistics (Week 2) - 3-4 hours

**Features**:
8. ✅ `dashboard progress` - Progress overview table
9. ✅ `dashboard stats` - Aggregate statistics
10. ✅ `dashboard active` - Active work summary

**Why Third**: Tests statistics aggregation. Provides immediate value to users.

**Beta Test Value**: Validates Core Engine statistics calculation and CLI rich table rendering.

---

### Phase 4: Filtering (Week 2-3) - 2-3 hours

**Features**:
11. ✅ `dashboard list --status <status>` - Filter by status
12. ✅ `dashboard list --priority <priority>` - Filter by priority
13. ✅ `dashboard search <query>` - Search entities

**Why Fourth**: Tests query capabilities. Enhances usability.

**Beta Test Value**: Validates Core Engine filtering and CLI query interface.

---

**Total MVP Effort**: 10-14 hours (fits within PLAN 2 Terminal CLI scope)

---

## 📋 Detailed Feature Specifications

### Feature 1: `dashboard list`

**Command**: `llm-methodology-cli dashboard list [--type TYPE] [--format table|json]`

**Output** (Rich Table):
```
┌─────────────────────────────────────────────┬──────────┬──────────┬─────────────┐
│ Entity                                      │ Type     │ Status   │ Progress    │
├─────────────────────────────────────────────┼──────────┼──────────┼─────────────┤
│ GRAMMAPLAN_EXECUTION-WORK-SYSTEM-ENHANCEMENT │ GrammaPlan│ Planning │ 0/5 PLANs   │
│ PLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE       │ PLAN     │ Active   │ 0/21 (0%)   │
│ SUBPLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE_01 │ SUBPLAN  │ In Progress│ 1/6 EXECs │
└─────────────────────────────────────────────┴──────────┴──────────┴─────────────┘
```

**Implementation**:
- Core Engine: `list_entities(type_filter=None) -> List[Entity]`
- CLI: Parse command, call API, render table
- Tests: File discovery, data parsing, table rendering

**Beta Test**: Validates Core Engine file discovery and data model parsing

---

### Feature 2: `dashboard count`

**Command**: `llm-methodology-cli dashboard count`

**Output** (Rich Panel):
```
┌─────────────────────────────────────┐
│ Entity Counts                       │
├─────────────────────────────────────┤
│ NORTH_STAR:     1                    │
│ GrammaPlans:    5                    │
│ PLANs:         10 (2 active, 5 paused)│
│ SUBPLANs:      45                    │
│ EXECUTION_TASKs: 120                 │
│ EXECUTION_ANALYSIS: 25               │
└─────────────────────────────────────┘
```

**Implementation**:
- Core Engine: `count_entities() -> Dict[str, int]`
- CLI: Call API, render panel
- Tests: Aggregation logic

**Beta Test**: Validates Core Engine aggregation

---

### Feature 3: `dashboard status`

**Command**: `llm-methodology-cli dashboard status`

**Output** (Rich Table):
```
┌──────────────┬──────────┬──────────┬───────────┐
│ Entity Type  │ Active   │ Paused   │ Complete  │
├──────────────┼──────────┼──────────┼───────────┤
│ PLANs        │ 2        │ 5        │ 8         │
│ GrammaPlans  │ 1        │ 0        │ 0         │
│ SUBPLANs     │ 12       │ 0        │ 33        │
│ EXECUTIONs   │ 8        │ 0        │ 112       │
└──────────────┴──────────┴──────────┴───────────┘
```

**Implementation**:
- Core Engine: `get_status_summary() -> Dict[str, Dict[str, int]]`
- CLI: Call API, render table
- Tests: Status parsing, aggregation

**Beta Test**: Validates Core Engine status parsing

---

### Feature 4: `dashboard show <id>`

**Command**: `llm-methodology-cli dashboard show PLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE`

**Output** (Rich Panel):
```
┌─────────────────────────────────────────────────────────────┐
│ PLAN: GraphRAG Observability Excellence                     │
├─────────────────────────────────────────────────────────────┤
│ Status:        🚀 Active                                    │
│ Priority:      CRITICAL                                      │
│ Progress:      0/21 achievements (0%)                       │
│ Parent:        GRAMMAPLAN_GRAPHRAG-PIPELINE-EXCELLENCE       │
│ Last Updated:  2025-11-08 14:30 UTC                        │
│ Next:          Achievement 0.1: Transformation Logging      │
│                                                              │
│ Statistics:                                                  │
│   SUBPLANs:    1 (0 complete, 1 in progress)                │
│   EXECUTIONs:  1 (1 complete)                               │
│   Time Spent:  2.5h                                         │
└─────────────────────────────────────────────────────────────┘
```

**Implementation**:
- Core Engine: `get_entity(entity_id: str) -> Entity`
- CLI: Call API, render panel
- Tests: Entity retrieval, data model completeness

**Beta Test**: Validates Core Engine entity retrieval

---

### Feature 5: `dashboard hierarchy <grammaplan-id>`

**Command**: `llm-methodology-cli dashboard hierarchy GRAMMAPLAN_EXECUTION-WORK-SYSTEM-ENHANCEMENT`

**Output** (Rich Tree):
```
GRAMMAPLAN_EXECUTION-WORK-SYSTEM-ENHANCEMENT (Planning, 0/5 PLANs)
├── PLAN_EXECUTION-TAXONOMY-AND-WORKSPACE (Planning, 0% complete)
│   └── (No SUBPLANs yet)
├── PLAN_EXECUTION-PROMPT-SYSTEM (Planning, 0% complete)
│   └── (No SUBPLANs yet)
└── PLAN_EXECUTION-TEMPLATES-AND-TYPES (Planning, 0% complete)
    └── (No SUBPLANs yet)
```

**Implementation**:
- Core Engine: `get_hierarchy(root_id: str) -> HierarchyTree`
- CLI: Call API, render tree using `rich.tree`
- Tests: Relationship traversal, tree building

**Beta Test**: Validates Core Engine relationship models

---

### Feature 6: `dashboard progress`

**Command**: `llm-methodology-cli dashboard progress`

**Output** (Rich Table with Progress Bars):
```
┌─────────────────────────────────────────────┬──────────┬──────────────┬──────────────────┐
│ Entity                                      │ Status   │ Progress     │ Next Action      │
├─────────────────────────────────────────────┼──────────┼──────────────┼──────────────────┤
│ PLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE      │ Active   │ █░░░░░░░░░ 0%│ Achievement 0.1  │
│ PLAN_METHODOLOGY-V2-ENHANCEMENTS            │ Active   │ ████████░░ 85%│ Achievement 6.1  │
│ GRAMMAPLAN_EXECUTION-WORK-SYSTEM-ENHANCEMENT│ Planning │ ░░░░░░░░░░ 0%│ Create PLAN 1    │
└─────────────────────────────────────────────┴──────────┴──────────────┴──────────────────┘
```

**Implementation**:
- Core Engine: `calculate_progress(entity_id: str) -> float`, `get_active_entities() -> List[Entity]`
- CLI: Call API, render table with progress bars
- Tests: Progress calculation, progress bar rendering

**Beta Test**: Validates Core Engine progress calculation and CLI rich rendering

---

### Feature 7: `dashboard stats`

**Command**: `llm-methodology-cli dashboard stats`

**Output** (Rich Panels):
```
┌─────────────────────────┐  ┌─────────────────────────┐
│ Overall Statistics       │  │ Active Work Summary     │
├─────────────────────────┤  ├─────────────────────────┤
│ Total PLANs: 18         │  │ Active PLANs: 2         │
│ Complete: 8 (44%)        │  │ Active SUBPLANs: 12     │
│ Total Achievements: 157  │  │ Active EXECUTIONs: 8    │
│ Total Time: 223h         │  │ Paused PLANs: 5         │
│ Avg Completion: 57%      │  │                         │
└─────────────────────────┘  └─────────────────────────┘
```

**Implementation**:
- Core Engine: `aggregate_statistics() -> Statistics`
- CLI: Call API, render panels
- Tests: Statistics aggregation

**Beta Test**: Validates Core Engine statistics calculation

---

### Feature 8: `dashboard active`

**Command**: `llm-methodology-cli dashboard active`

**Output** (Rich Table):
```
┌─────────────────────────────────────────────┬──────────┬──────────────┬─────────────┐
│ Active Work                                 │ Type     │ Progress     │ Last Update │
├─────────────────────────────────────────────┼──────────┼──────────────┼─────────────┤
│ PLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE      │ PLAN     │ 0/21 (0%)    │ 2025-11-08  │
│   └─ SUBPLAN_01: Achievement 0.1            │ SUBPLAN  │ 1/6 EXECs    │ 2025-11-08  │
│       └─ EXECUTION_01_01: Complete ✅       │ EXECUTION│ Complete     │ 2025-11-08  │
└─────────────────────────────────────────────┴──────────┴──────────────┴─────────────┘
```

**Implementation**:
- Core Engine: `get_active_entities() -> List[Entity]`
- CLI: Call API, render hierarchical table
- Tests: Status filtering, hierarchy rendering

**Beta Test**: Validates Core Engine filtering and CLI hierarchical display

---

## 🔗 Integration with Core Foundation

### Core Engine (PLAN 1) Requirements

**API Methods Needed**:

```python
# Discovery
def list_entities(type_filter: Optional[str] = None) -> List[Entity]
def count_entities() -> Dict[str, int]
def get_status_summary() -> Dict[str, Dict[str, int]]

# Entity Retrieval
def get_entity(entity_id: str) -> Entity
def get_children(entity_id: str) -> List[Entity]
def get_parent(entity_id: str) -> Optional[Entity]
def get_hierarchy(root_id: str) -> HierarchyTree

# Statistics
def calculate_progress(entity_id: str) -> float
def aggregate_statistics() -> Statistics
def get_active_entities() -> List[Entity]

# Filtering
def filter_entities(filters: Dict[str, Any]) -> List[Entity]
def search_entities(query: str) -> List[Entity]
```

**Data Models Needed**:

```python
class Entity(Protocol):
    id: str
    type: str  # "north-star", "grammaplan", "plan", "subplan", "execution", "analysis"
    status: str
    progress: float
    last_updated: datetime
    # ... other fields

class Plan(Entity):
    priority: str
    achievements: List[Achievement]
    parent: Optional[str]  # GrammaPlan ID
    statistics: PlanStatistics

class HierarchyTree:
    root: Entity
    children: List[HierarchyTree]
```

**Beta Test Value**: Dashboard features drive Core Engine API design and validate data models.

---

### Terminal CLI (PLAN 2) Requirements

**CLI Commands**:

```python
@cli.command()
def dashboard():
    """Dashboard commands for methodology visibility"""
    pass

@dashboard.command()
def list(type: str = None, format: str = "table"):
    """List all entities"""
    entities = api.list_entities(type_filter=type)
    render_table(entities, format)

@dashboard.command()
def count():
    """Show entity counts"""
    counts = api.count_entities()
    render_panel(counts)

@dashboard.command()
def status():
    """Show status summary"""
    summary = api.get_status_summary()
    render_table(summary)

@dashboard.command()
def show(entity_id: str):
    """Show entity details"""
    entity = api.get_entity(entity_id)
    render_panel(entity)

@dashboard.command()
def hierarchy(root_id: str):
    """Show entity hierarchy"""
    tree = api.get_hierarchy(root_id)
    render_tree(tree)

@dashboard.command()
def progress():
    """Show progress overview"""
    entities = api.get_active_entities()
    render_progress_table(entities)

@dashboard.command()
def stats():
    """Show aggregate statistics"""
    stats = api.aggregate_statistics()
    render_panels(stats)

@dashboard.command()
def active():
    """Show active work"""
    entities = api.get_active_entities()
    render_hierarchical_table(entities)
```

**UI Components** (using `rich` library):
- Tables (`rich.table`)
- Panels (`rich.panel`)
- Trees (`rich.tree`)
- Progress bars (`rich.progress`)
- Colors and styling

**Beta Test Value**: Dashboard features test CLI rendering capabilities and user experience.

---

## 📊 Beta Test Strategy

### What We're Testing

**Core Engine (PLAN 1)**:
- ✅ File discovery performance (<10s for 1000 files)
- ✅ Data model parsing accuracy
- ✅ Relationship traversal correctness
- ✅ Statistics calculation accuracy
- ✅ Query/filter performance

**Terminal CLI (PLAN 2)**:
- ✅ Rich UI rendering (tables, trees, panels)
- ✅ Command parsing and routing
- ✅ User experience (intuitive, beautiful)
- ✅ Performance (commands <3s)

**Integration**:
- ✅ API contract stability
- ✅ End-to-end workflows
- ✅ Error handling
- ✅ Real-world usage patterns

### Success Metrics

**Functional**:
- ✅ All dashboard commands work
- ✅ Data accurate (matches ACTIVE_PLANS.md)
- ✅ Performance targets met (<3s per command)

**User Experience**:
- ✅ Commands intuitive
- ✅ Output beautiful and readable
- ✅ User feedback >4/5

**Beta Test Value**:
- ✅ Core Engine validated with real usage
- ✅ CLI validated with real workflows
- ✅ Identifies gaps for improvement

---

## 🎯 Feature Prioritization

### Must Have (MVP Core) - 5-7 hours

1. ✅ `dashboard list` - Basic entity listing
2. ✅ `dashboard count` - Entity counts
3. ✅ `dashboard status` - Status summary
4. ✅ `dashboard show <id>` - Entity details

**Why**: Tests Core Engine foundation, provides basic visibility

---

### Should Have (MVP Value) - 5-7 hours

5. ✅ `dashboard progress` - Progress overview
6. ✅ `dashboard stats` - Aggregate statistics
7. ✅ `dashboard active` - Active work summary

**Why**: Provides immediate value, tests statistics aggregation

---

### Nice to Have (MVP Enhancement) - 3-4 hours

8. ✅ `dashboard hierarchy <id>` - Hierarchy tree
9. ✅ `dashboard children <id>` - Show children
10. ✅ `dashboard parent <id>` - Show parent
11. ✅ `dashboard list --status <status>` - Filter by status
12. ✅ `dashboard list --priority <priority>` - Filter by priority
13. ✅ `dashboard search <query>` - Search entities

**Why**: Enhances usability, tests advanced features

---

**Total MVP**: 13-18 hours (fits within PLAN 2 Terminal CLI scope)

---

## 🔗 Dependencies & Integration

### Dependencies on Core Foundation

**PLAN 1 (Core Engine)**:
- ✅ File discovery engine (must exist)
- ✅ Data models (must exist)
- ✅ MethodologyAPI (must exist)
- ✅ Entity retrieval methods (dashboard drives API design)

**PLAN 2 (Terminal CLI)**:
- ✅ Rich UI library (`rich` installed)
- ✅ Command framework (`click` or similar)
- ✅ CLI entry point (`llm-methodology-cli` command)

**Integration Points**:
- Dashboard commands consume MethodologyAPI
- Dashboard features validate API completeness
- Dashboard usage informs API improvements

### Integration with Existing Tools

**ACTIVE_PLANS.md**:
- Dashboard can replace manual updates
- Dashboard can generate ACTIVE_PLANS.md automatically
- Dashboard provides real-time view (vs. static file)

**Prompt Generators**:
- Dashboard can show "next achievement" (replaces prompt generator logic)
- Dashboard can validate completion status
- Dashboard can suggest next work

**Validation Scripts**:
- Dashboard can show validation status
- Dashboard can highlight issues
- Dashboard can suggest fixes

---

## 📋 Implementation Plan

### Phase 1: Core Discovery (Week 1) - 2-3 hours

**After PLAN 1 Priority 0 (API Stable)**:

1. Implement Core Engine methods:
   - `list_entities()`
   - `count_entities()`
   - `get_status_summary()`
   - `get_entity()`

2. Implement CLI commands:
   - `dashboard list`
   - `dashboard count`
   - `dashboard status`
   - `dashboard show`

3. Test with real data:
   - Validate against ACTIVE_PLANS.md
   - Check performance (<3s per command)
   - Verify accuracy

**Deliverables**:
- Core Engine: 4 API methods
- CLI: 4 commands
- Tests: Basic functionality

---

### Phase 2: Progress & Statistics (Week 2) - 3-4 hours

**After Phase 1**:

1. Implement Core Engine methods:
   - `calculate_progress()`
   - `aggregate_statistics()`
   - `get_active_entities()`

2. Implement CLI commands:
   - `dashboard progress`
   - `dashboard stats`
   - `dashboard active`

3. Test statistics accuracy:
   - Compare with PLAN internal statistics
   - Validate progress calculations
   - Check aggregation logic

**Deliverables**:
- Core Engine: 3 API methods
- CLI: 3 commands
- Tests: Statistics accuracy

---

### Phase 3: Navigation (Week 2-3) - 3-4 hours

**After Phase 2**:

1. Implement Core Engine methods:
   - `get_children()`
   - `get_parent()`
   - `get_hierarchy()`

2. Implement CLI commands:
   - `dashboard hierarchy`
   - `dashboard children`
   - `dashboard parent`

3. Test relationship traversal:
   - Validate parent-child links
   - Check hierarchy correctness
   - Test tree rendering

**Deliverables**:
- Core Engine: 3 API methods
- CLI: 3 commands
- Tests: Relationship traversal

---

### Phase 4: Filtering (Week 3) - 2-3 hours

**After Phase 3**:

1. Implement Core Engine methods:
   - `filter_entities()`
   - `search_entities()`

2. Implement CLI commands:
   - `dashboard list --status`
   - `dashboard list --priority`
   - `dashboard search`

3. Test query capabilities:
   - Validate filtering logic
   - Check search accuracy
   - Test performance

**Deliverables**:
- Core Engine: 2 API methods
- CLI: 3 commands (with flags)
- Tests: Query capabilities

---

**Total**: 10-14 hours (fits within PLAN 2 Terminal CLI 10-15h scope)

---

## 🎯 Beta Test Success Criteria

### Functional Success

- [ ] All 13 dashboard commands work
- [ ] Data accurate (matches manual tracking)
- [ ] Performance targets met (<3s per command)
- [ ] Error handling graceful
- [ ] Commands intuitive and discoverable

### Integration Success

- [ ] Core Engine API stable and complete
- [ ] CLI rendering beautiful and readable
- [ ] End-to-end workflows validated
- [ ] Real-world usage patterns identified

### User Value Success

- [ ] Dashboard provides visibility not available manually
- [ ] Users prefer dashboard over ACTIVE_PLANS.md
- [ ] Dashboard identifies issues (stale data, missing updates)
- [ ] Dashboard suggests next work effectively

### Beta Test Value

- [ ] Core Engine validated with real usage
- [ ] CLI validated with real workflows
- [ ] Gaps identified for improvement
- [ ] Foundation ready for advanced features

---

## 🚨 Risks & Mitigation

### Risk 1: Performance Issues

**Impact**: HIGH - Dashboard commands slow, poor UX

**Mitigation**:
- File discovery caching (Core Engine)
- Lazy loading (only load what's needed)
- Performance benchmarks early
- Optimize hot paths

### Risk 2: Data Accuracy

**Impact**: MEDIUM - Dashboard shows wrong data, loses trust

**Mitigation**:
- Comprehensive tests (compare with manual tracking)
- Validation scripts (check data consistency)
- Error detection (flag inconsistencies)
- Manual verification initially

### Risk 3: API Instability

**Impact**: MEDIUM - Dashboard breaks as API changes

**Mitigation**:
- Dashboard drives API design (co-design)
- API versioning (if needed)
- Contract tests (validate API compliance)
- Early integration testing

### Risk 4: Scope Creep

**Impact**: LOW - Dashboard features expand beyond MVP

**Mitigation**:
- Strict MVP definition (13 features max)
- Defer advanced features (Phase 5+)
- Focus on beta test value
- Time-box each phase

---

## 📚 References

- `GRAMMAPLAN_UNIVERSAL-CLI-CORE-FOUNDATION.md` (foundation context)
- `ACTIVE_PLANS.md` (current manual tracking)
- `LLM-METHODOLOGY.md` (entity types and status)
- `LLM/templates/PLAN-TEMPLATE.md` (statistics tracking)
- `EXECUTION_ANALYSIS_SUBPLAN-TRACKING-GAP.md` (tracking requirements)

---

## 🎯 Conclusion

**MVP Dashboard Features**: 13 features across 4 phases (10-14 hours)

**Beta Test Value**: 
- Tests Core Engine file discovery, data models, relationships, statistics
- Tests Terminal CLI rich UI rendering, command parsing, user experience
- Provides real value (visibility) while validating foundation

**Recommended Approach**: Implement as part of PLAN 2 (Terminal CLI), using dashboard features to drive Core Engine API design and validate both components end-to-end.

**Success**: Dashboard provides visibility, Core Engine validated, CLI validated, foundation ready for advanced features.

---

**Status**: Analysis Complete  
**Next**: Integrate dashboard features into PLAN 2 (Terminal CLI) scope, or create separate PLAN for dashboard as beta test

