# PLAN: GraphRAG Pipeline & Visualization System

**Status**: Planning  
**Created**: 2025-11-06 23:15 UTC  
**Goal**: Transform the GraphRAG pipeline into a production-grade orchestration system with flexible execution, real-time metrics dashboards, stage contribution visualization, and interactive graph exploration  
**Priority**: HIGH - Critical for production operations, quality monitoring, and user experience

---

## 📖 Context for LLM Execution

**If you're an LLM reading this to execute work**:

1. **What This Plan Is**: Comprehensive refactor of GraphRAG pipeline orchestration, metrics collection, and visualization to enable production operations, quality monitoring, and interactive exploration

2. **Your Task**: Implement the achievements listed below (priority order)

3. **How to Proceed**:

   - Read the achievement you want to tackle
   - Check dependencies in "Related Plans" section (4 upstream plans)
   - Create a SUBPLAN with your specific approach
   - Create an EXECUTION_TASK to log your work
   - Follow the TDD workflow defined in IMPLEMENTATION_START_POINT.md

4. **What You'll Create**:

   - Flexible pipeline orchestration (partial runs, stage selection, resume)
   - Real-time metrics dashboard (Grafana/Prometheus integration)
   - Stage contribution visualization UI (how each stage builds the graph)
   - Interactive graph visualization (entities, relationships, communities)
   - API endpoints for monitoring and control
   - Comprehensive observability

5. **Where to Get Help**:
   - Read IMPLEMENTATION_START_POINT.md for methodology
   - Read documentation/guides/MULTIPLE-PLANS-PROTOCOL.md for managing dependencies
   - Review existing code:
     - `business/pipelines/graphrag.py` (pipeline orchestration)
     - `business/pipelines/runner.py` (stage runner)
     - `app/cli/graphrag.py` (CLI interface)
   - Check observability setup: `docker-compose.observability.yml`, `observability/` directory
   - Review related PLANs (see "Related Plans" section below)

**Self-Contained**: This PLAN contains everything you need to execute it.

**Dependencies**: This plan benefits from 4 upstream plans (see "Critical Dependencies" section). Can start in parallel but quality improves together.

---

## 🎯 Goal

Transform the GraphRAG pipeline from a batch-oriented sequential processor into a production-grade orchestration system with flexible execution modes (full/partial/resume), real-time metrics collection (Prometheus/Grafana integration), stage contribution visualization (how each stage builds the graph), interactive graph exploration UI, and comprehensive observability—enabling production operations, quality monitoring, experimentation, and user-friendly exploration of the knowledge graph.

---

## 📖 Problem Statement

**Current State - Functional But Limited**:

The GraphRAG pipeline is working with basic functionality:

- ✅ Four stages orchestrated: extraction → resolution → construction → detection
- ✅ Stage registry for flexible composition
- ✅ Basic stats methods per stage
- ✅ Experiment tracking in MongoDB
- ✅ JSON-based configuration
- ✅ Database isolation (read_db/write_db)
- ✅ Observability stack ready (Grafana, Prometheus, Loki)

**Critical Issues**:

**Issue 1: Inflexible Execution** ⚠️ HIGH

- Must run full pipeline or single stage (all-or-nothing)
- No partial runs (e.g., "extraction + resolution only")
- No resume capability ("run from stage 3")
- No stage skipping ("run all except extraction")
- **Impact**: Inefficient for debugging, experimentation, and iterative development

**Issue 2: No Real-Time Metrics** ⚠️ HIGH

- Metrics logged but not exposed for monitoring
- No Prometheus integration (observability stack unused)
- No dashboards (Grafana unused)
- Stats only available after completion
- **Impact**: No visibility during long runs, can't monitor health, can't debug performance

**Issue 3: No Stage Contribution Visibility** ⚠️ HIGH

- Can't see how each stage contributes to final graph
- No UI to visualize data flow (chunks → entities → relationships → communities)
- Stats exist but not visualized
- **Impact**: Hard to understand pipeline behavior, hard to debug quality issues

**Issue 4: No Graph Visualization** ⚠️ HIGH

- Knowledge graph exists but not explorable
- No UI to browse entities, relationships, communities
- Can't validate graph quality visually
- **Impact**: Black box system, hard to validate, hard to explain to users

**Missing Features**:

1. **No Flexible Pipeline Orchestration**:

   - Can't specify stage ranges
   - Can't skip stages
   - Can't resume from failure point
   - Can't run parallel experiments

2. **No Metrics Export**:

   - No Prometheus metrics
   - No custom Grafana dashboards
   - No real-time monitoring
   - No alerting

3. **No Stage Visualization**:

   - No UI showing stage outputs
   - No data flow visualization
   - No quality metrics per stage
   - No comparison across runs

4. **No Graph Exploration**:

   - No entity browser
   - No relationship viewer
   - No community explorer
   - No graph rendering

5. **No Pipeline API**:
   - No REST endpoints for status
   - No WebSocket for real-time updates
   - No remote control
   - No integration points

**Impact**:

- Inefficient development (must run full pipeline for testing)
- Poor observability (can't monitor long-running jobs)
- Hard to debug quality issues (no visual inspection)
- Bad user experience (no exploration UI)
- Difficult experimentation (inflexible execution)
- No production operations dashboard

---

## 🎯 Success Criteria

### Must Have

- [ ] Flexible pipeline execution (partial runs, stage ranges, resume capability)
- [ ] Prometheus metrics export (stage progress, throughput, errors, latency)
- [ ] Grafana dashboard (pipeline overview, stage details, alerts)
- [ ] Stage contribution UI (visualize chunk → entity → relationship → community flow)
- [ ] Basic graph visualization (entity/relationship browser)
- [ ] Pipeline API (status, control endpoints)
- [ ] Real-time monitoring (WebSocket or polling)
- [ ] All existing functionality preserved
- [ ] All tests passing + 15+ new tests

### Should Have

- [ ] Interactive graph explorer (filter, search, zoom)
- [ ] Community visualization (entity clusters, summaries)
- [ ] Enhanced experiment comparison UI (quality, cost, performance metrics)
- [ ] Batch experiment runner
- [ ] Experiment visualization (charts, plots)
- [ ] Experiment journal system
- [ ] Quality metrics dashboard (per-stage quality)
- [ ] Custom Grafana dashboards (per-stage insights)
- [ ] Pipeline control UI (start, stop, resume)
- [ ] Export capabilities (graph data, metrics)
- [ ] Documentation (API docs, dashboard guide, UI guide)

### Nice to Have

- [ ] 3D graph visualization (force-directed layout)
- [ ] Community summarization visualization (LLM summaries)
- [ ] Real-time graph updates (WebSocket streaming)
- [ ] Query builder UI (build GraphRAG queries)
- [ ] Pipeline scheduling (cron-like)
- [ ] Multi-user support (authentication, permissions)

---

## 📋 Scope Definition

### In Scope

1. **Pipeline Orchestration**:

   - Flexible stage selection
   - Partial pipeline runs
   - Resume from failure
   - Stage dependencies
   - Parallel stage execution (where possible)

2. **Metrics & Observability**:

   - Prometheus metrics exporter
   - Custom Grafana dashboards
   - Real-time progress monitoring
   - Alert rules for failures
   - Log aggregation (Loki integration)

3. **Stage Contribution Visualization**:

   - UI showing data flow per stage
   - Input/output counts per stage
   - Quality metrics per stage
   - Stage comparison view

4. **Graph Visualization**:

   - Entity browser (search, filter, details)
   - Relationship viewer (connections, predicates)
   - Community explorer (clusters, summaries)
   - Basic graph rendering (D3.js or similar)

5. **Pipeline API**:

   - REST endpoints (status, control, metrics)
   - WebSocket for real-time updates
   - OpenAPI documentation
   - Client library (Python)

6. **Testing & Documentation**:
   - Unit tests for new components
   - Integration tests for pipeline orchestration
   - API documentation
   - User guide for UI
   - Dashboard setup guide

### Out of Scope

- Advanced graph algorithms (centrality, path finding) - Focus on visualization
- Real-time ingestion pipeline - Batch processing only
- Multi-tenant system - Single deployment
- Graph editing UI - Read-only visualization
- ML model training UI - Use existing tools
- Custom query language - Use existing GraphRAG queries

---

## 🎯 Desirable Achievements (Priority Order)

**Important Note**: This PLAN lists achievements (WHAT to do), not subplans (HOW to do it).

**Process**:

- Review achievements
- Select one to work on
- Create SUBPLAN with your approach
- Create EXECUTION_TASK to log work
- Execute

---

### Priority 0: HIGH - Flexible Pipeline Orchestration

**Achievement 0.1**: Stage Selection & Partial Runs Implemented

- Add `--stages` flag to CLI: specify stage list or range
- Examples: `--stages extraction,resolution` or `--stages 1-3`
- Modify `GraphRAGPipeline` to accept stage list
- Validate stage dependencies (e.g., resolution needs extraction)
- Test: Can run partial pipeline, dependencies respected
- Success: Flexible stage execution working
- Effort: 3-4 hours
- Files: `business/pipelines/graphrag.py`, `app/cli/graphrag.py`

**Achievement 0.2**: Resume from Failure Implemented

- Store pipeline state (last completed stage, checkpoint)
- Add `--resume` flag to CLI
- Detect last successful stage from DB
- Skip completed stages, resume from next
- Test: Pipeline fails at stage 3 → resume skips 1-2
- Success: Resume capability working
- Effort: 3-4 hours
- Files: `business/pipelines/graphrag.py`

**Achievement 0.3**: Stage Dependency Validation Implemented

- Define explicit dependencies (resolution depends on extraction, etc.)
- Validate selected stages have dependencies met
- Warn if running out of order
- Auto-include dependencies if needed
- Test: Selecting resolution without extraction → error or auto-include
- Success: Safe stage execution
- Effort: 2-3 hours
- Files: `business/pipelines/graphrag.py`

---

### Priority 1: HIGH - Metrics & Observability

**Achievement 1.1**: Prometheus Metrics Export Implemented

- Create `business/services/observability/prometheus_metrics.py`
- Export metrics:
  - Pipeline status (running, completed, failed)
  - Stage progress (chunks_total, chunks_processed, chunks_failed per stage)
  - Throughput (entities/sec, relationships/sec, communities/sec)
  - Latency (stage duration, avg processing time per chunk)
  - Errors (count by stage, by error type)
- Use `prometheus_client` library
- Expose metrics endpoint on `:8000/metrics`
- Test: Metrics endpoint returns Prometheus format
- Success: Prometheus can scrape metrics
- Effort: 4-5 hours
- Files: New `business/services/observability/prometheus_metrics.py`, `app/api/metrics.py`

**Achievement 1.2**: Grafana Dashboard Created

- Create dashboard JSON: `observability/grafana/dashboards/graphrag-pipeline.json`
- Panels:
  - Pipeline overview (status, stages, duration)
  - Stage progress (processed/total per stage)
  - Throughput over time (entities/sec, relationships/sec)
  - Error rate (failures per stage)
  - Resource usage (memory, CPU if available)
- Alerts: Stage failures, slow processing, error spikes
- Test: Dashboard displays live pipeline metrics
- Success: Comprehensive monitoring dashboard
- Effort: 3-4 hours
- Files: `observability/grafana/dashboards/graphrag-pipeline.json`

**Achievement 1.3**: Real-Time Progress Monitoring Implemented

- WebSocket endpoint for pipeline progress
- Or: Server-sent events (SSE) for streaming updates
- Push updates: stage start/complete, progress %, errors
- Client: Simple web page showing live progress
- Test: Pipeline run streams progress to client
- Success: Real-time visibility during pipeline execution
- Effort: 4-5 hours
- Files: New `app/api/pipeline_progress.py`, `app/ui/pipeline_monitor.html`

---

### Priority 2: HIGH - Stage Contribution Visualization & Experiment Infrastructure

**Achievement 2.1**: Stage Stats API Implemented

- Create REST API: `/api/pipeline/stats`
- Return per-stage statistics:
  - Input: chunks available for stage
  - Output: entities/relationships/communities created
  - Quality: confidence distribution, canonical ratio, etc.
  - Performance: duration, throughput
- Aggregates from stage stats methods
- Test: API returns complete stats
- Success: Programmatic access to stage stats
- Effort: 3-4 hours
- Files: New `app/api/pipeline_stats.py`

**Achievement 2.2**: Stage Flow Visualization UI Created

- Web UI showing data flow through stages
- Sankey diagram or flow chart: chunks → entities → relationships → communities
- Show counts at each stage
- Color-code by status (completed, in-progress, failed)
- Click stage for detailed view
- Test: UI displays accurate flow
- Success: Visual understanding of pipeline
- Effort: 5-6 hours
- Files: New `app/ui/stage_flow.html`, `app/ui/static/stage_flow.js`

**Achievement 2.3**: Enhanced Experiment Comparison UI Created

- Compare multiple pipeline runs/experiments side-by-side
- Table view: experiment_id, config, stage outputs, quality metrics
- Enhanced metrics (beyond basic counts):
  - Quality: modularity, graph density, average degree, clustering coefficient
  - Cost: total tokens, estimated cost ($), cost per entity/relationship
  - Performance: runtime, throughput (entities/sec, relationships/sec), TPM/RPM utilization
  - Coverage: chunks processed, entities/chunk, relationships/chunk, failed chunks
- Charts: quality over time, cost comparison, performance trends
- Filter by experiment_id, date range, config parameters
- Export comparison report (markdown, CSV, JSON)
- Integration with existing `scripts/compare_graphrag_experiments.py` (enhance or replace)
- Test: Can compare 2+ experiments with comprehensive metrics
- Success: Easy experiment comparison with full metrics
- Effort: 5-6 hours
- Files: New `app/ui/experiment_comparison.html`, enhance `scripts/compare_graphrag_experiments.py`

**Achievement 2.4**: Batch Experiment Runner Implemented

- Script: `scripts/run_experiments.py` for batch execution
- Features:
  - Load multiple configs (glob patterns, batch config files)
  - Sequential or parallel execution
  - Progress tracking and status updates
  - Automatic result collection
  - Error handling and retry logic
  - Notifications on completion (optional)
- Integration with pipeline API (Achievement 5.1)
- Test: Can run batch of experiments automatically
- Success: Automated experiment workflows
- Effort: 4-5 hours
- Files: New `scripts/run_experiments.py`

**Achievement 2.5**: Experiment Visualization & Analysis Implemented

- Visual comparison of experiments:
  - Community size distributions (histograms)
  - Cost vs quality scatter plots
  - Performance over time (line charts)
  - Modularity comparisons (bar charts)
  - Resolution parameter effects (line charts)
- Integration with experiment comparison UI (Achievement 2.3)
- Export charts as images (PNG, SVG)
- Test: Can visualize experiment results
- Success: Visual experiment analysis
- Effort: 4-5 hours
- Files: Extend `app/ui/experiment_comparison.html` or new `app/ui/experiment_visualization.html`

**Achievement 2.6**: Experiment Journal & Documentation System

- Experiment journal: `documentation/experiments/JOURNAL-YYYY.md`
- Template for experiment entries:
  - Date, hypothesis, config link, results, analysis, next steps
- Link from experiment configs to journal entries
- Experiment results archive structure
- Integration with experiment tracking collection
- Test: Can track and document experiments systematically
- Success: Systematic experiment documentation
- Effort: 2-3 hours
- Files: New `documentation/experiments/JOURNAL-YYYY.md` template, enhance experiment tracking

---

### Priority 3: HIGH - Graph Visualization

**Achievement 3.1**: Entity Browser Implemented

- Web UI for browsing entities
- Features:
  - Search by name, type
  - Filter by confidence, source_count
  - Paginated list view
  - Entity detail view (aliases, mentions, relationships)
- REST API: `/api/entities/search`, `/api/entities/{entity_id}`
- Test: Can search and view entities
- Success: Entity exploration UI working
- Effort: 5-6 hours
- Files: New `app/api/entities.py`, `app/ui/entity_browser.html`

**Achievement 3.2**: Relationship Viewer Implemented

- Web UI for browsing relationships
- Features:
  - Filter by predicate, type, confidence
  - Show subject → predicate → object
  - Relationship details (source_chunks, created_by_stage)
  - Link to entity details
- REST API: `/api/relationships/search`
- Test: Can browse relationships
- Success: Relationship exploration UI working
- Effort: 4-5 hours
- Files: New `app/api/relationships.py`, `app/ui/relationship_viewer.html`

**Achievement 3.3**: Basic Graph Rendering Implemented

- Interactive graph visualization using D3.js or Cytoscape.js
- Features:
  - Show entities as nodes, relationships as edges
  - Color by entity type, edge by predicate
  - Zoom, pan, drag nodes
  - Click node/edge for details
  - Filter by type, predicate
- Start with small subgraphs (ego networks, communities)
- Test: Can render and interact with graph
- Success: Interactive graph visualization working
- Effort: 6-8 hours
- Files: New `app/ui/graph_viewer.html`, `app/ui/static/graph_viewer.js`

---

### Priority 4: MEDIUM - Community Visualization

**Achievement 4.1**: Community Explorer Implemented

- Web UI for browsing communities
- Features:
  - List communities by level
  - Sort by size, coherence_score
  - Community detail view (entities, relationships, summary)
  - Filter by level, size range
- REST API: `/api/communities/search`, `/api/communities/{community_id}`
- Test: Can browse and view communities
- Success: Community exploration UI working
- Effort: 4-5 hours
- Files: New `app/api/communities.py`, `app/ui/community_explorer.html`

**Achievement 4.2**: Community Graph Visualization Implemented

- Render community as subgraph
- Highlight entities in community
- Show internal relationships
- Display community summary
- Compare communities side-by-side
- Test: Community graph renders correctly
- Success: Visual community inspection
- Effort: 4-5 hours
- Files: Extend `app/ui/graph_viewer.html`

**Achievement 4.3**: Multi-Resolution Community Navigation Implemented

- UI for navigating community levels (from Achievement 3.1 in PLAN_COMMUNITY-DETECTION-REFACTOR.md)
- Show hierarchy: macro themes (level 1) → micro topics (level 3)
- Drill down/up between levels
- Show entity multi-scale membership
- Test: Can navigate between community resolutions
- Success: Hierarchical community exploration
- Effort: 3-4 hours
- Files: Extend `app/ui/community_explorer.html`

---

### Priority 5: MEDIUM - Pipeline Control & API

**Achievement 5.1**: Pipeline Control API Implemented

- REST endpoints:
  - `POST /api/pipeline/start` - Start pipeline with config
  - `GET /api/pipeline/status` - Current status
  - `POST /api/pipeline/pause` - Pause execution (if possible)
  - `POST /api/pipeline/resume` - Resume from last checkpoint
  - `POST /api/pipeline/cancel` - Cancel running pipeline
- Track pipeline state in Redis or MongoDB
- Test: Can control pipeline via API
- Success: Remote pipeline control
- Effort: 5-6 hours
- Files: New `app/api/pipeline_control.py`

**Achievement 5.2**: Pipeline Status UI Created

- Web UI for pipeline control
- Features:
  - View current pipeline status
  - Start new pipeline run (select stages, config)
  - Monitor progress (real-time)
  - View logs (tail -f style)
  - Cancel/resume controls
- Test: Can control pipeline from browser
- Success: Pipeline control UI working
- Effort: 5-6 hours
- Files: New `app/ui/pipeline_control.html`

**Achievement 5.3**: Pipeline History UI Created

- View past pipeline runs
- Table: timestamp, config, stages, status, duration
- Filter by status, experiment_id, date range
- Compare runs (link to Achievement 2.3)
- Export history (CSV, JSON)
- Test: Can browse pipeline history
- Success: Historical tracking UI
- Effort: 3-4 hours
- Files: New `app/ui/pipeline_history.html`

---

### Priority 6: MEDIUM - Advanced Visualization

**Achievement 6.1**: Quality Metrics Dashboard Created

- Per-stage quality metrics:
  - Extraction: canonical_ratio, entity_count, relationship_count
  - Resolution: merge_rate, llm_call_rate, duplicate_reduction
  - Construction: graph_density, relationship_types, edge_distribution
  - Detection: modularity, coverage, community_sizes
- Trends over time (quality improvements)
- Comparison across experiments
- Test: Dashboard shows accurate metrics
- Success: Quality monitoring dashboard
- Effort: 4-5 hours
- Files: New Grafana dashboard or web UI

**Achievement 6.2**: Graph Statistics Dashboard Created

- Graph-level statistics:
  - Node/edge counts over time
  - Degree distribution
  - Connected components
  - Clustering coefficient
  - Type/predicate distributions
- Interactive charts (drill down)
- Export capabilities
- Test: Dashboard displays graph stats
- Success: Graph analytics dashboard
- Effort: 4-5 hours
- Files: New `app/ui/graph_statistics.html`

**Achievement 6.3**: Performance Dashboard Created

- Pipeline performance metrics:
  - Stage duration over time
  - Throughput (chunks/sec, entities/sec)
  - API latency percentiles
  - Resource utilization (if available)
  - Cost tracking (LLM tokens, API calls)
- Identify bottlenecks
- Track optimizations impact
- Test: Dashboard shows performance metrics
- Success: Performance monitoring dashboard
- Effort: 4-5 hours
- Files: New Grafana dashboard

---

### Priority 7: LOW - Enhanced Features

**Achievement 7.1**: Ego Network Visualization Implemented

- Given entity, show N-hop neighborhood
- Configurable depth (1-hop, 2-hop, etc.)
- Highlight central entity
- Show relationship types
- Expand/collapse nodes
- Test: Ego network renders correctly
- Success: Entity-centric graph exploration
- Effort: 4-5 hours
- Files: Extend `app/ui/graph_viewer.html`

**Achievement 7.2**: Predicate Filtering & Analysis Implemented

- Filter graph by predicate types
- Show predicate distribution
- Highlight specific predicate paths
- Predicate statistics (frequency, confidence)
- Test: Can filter and analyze by predicate
- Success: Predicate-focused exploration
- Effort: 3-4 hours
- Files: Extend `app/ui/graph_viewer.html`

**Achievement 7.3**: Export & Integration Features Implemented

- Export graph formats: GraphML, GEXF, JSON, CSV
- Export subgraphs (communities, ego networks)
- REST API for bulk data access
- Integration with external tools (Gephi, Neo4j, etc.)
- Test: Can export and import graphs
- Success: Integration with external tools
- Effort: 4-5 hours
- Files: New `app/api/export.py`

---

### Priority 8: LOW - Testing & Documentation

**Achievement 8.1**: Comprehensive Test Suite Created

- Unit tests for all new components
- Integration tests for pipeline orchestration
- API tests (endpoints, validation)
- UI tests (if framework available)
- Performance tests (benchmark)
- Success: >70% test coverage
- Effort: 8-10 hours
- Files: New test files in `tests/`

**Achievement 8.2**: API Documentation Created

- OpenAPI/Swagger documentation
- Endpoint descriptions, examples
- Client library guide
- Authentication guide (if applicable)
- Test: API docs are accurate and complete
- Success: Comprehensive API docs
- Effort: 3-4 hours
- Files: New `documentation/api/GRAPHRAG-PIPELINE-API.md`

**Achievement 8.3**: User Guide Created

- Dashboard setup guide
- UI user guide (how to explore graph)
- Troubleshooting guide
- Best practices
- Test: User can set up and use system from docs
- Success: Complete user documentation
- Effort: 4-5 hours
- Files: New `documentation/guides/GRAPHRAG-VISUALIZATION-GUIDE.md`

---

## 📋 Achievement Addition Log

**Dynamically Added Achievements** (if gaps discovered during execution):

(Empty initially - will be populated as gaps are discovered)

---

## 🔄 Subplan Tracking (Updated During Execution)

**Subplans Created for This PLAN**:

(Will be updated as subplans are created)

---

## 🔗 Constraints & Integration

### Technical Constraints

1. **Backward Compatibility**:

   - Existing CLI interface must work
   - Existing pipeline execution must work
   - New features are additive
   - No breaking changes to API

2. **Performance Requirements**:

   - UI must be responsive (<2s page loads)
   - Real-time updates must be <500ms latency
   - Graph rendering must handle 1000+ nodes
   - API must handle 100+ req/sec

3. **Technology Stack**:

   - Backend: Python (FastAPI for API)
   - Frontend: HTML/JS (D3.js/Cytoscape.js for graphs)
   - Metrics: Prometheus + Grafana
   - Logs: Loki + Promtail
   - Database: MongoDB (existing)

4. **Security**:
   - Basic authentication for UI (if exposed)
   - API rate limiting
   - Input validation
   - No sensitive data exposure

### Process Constraints

1. **Test-First Always**:

   - Write tests before implementing
   - No cheating (fix implementation, not tests)
   - All tests must pass

2. **Incremental Development**:

   - Small, testable changes
   - Each achievement independently testable
   - Can pause/resume at achievement boundaries

3. **Documentation**:
   - All changes documented
   - API docs generated
   - User guides updated

---

## 📚 References & Context

### Related Plans

**PLAN_EXTRACTION-QUALITY-ENHANCEMENT.md**:

- **Type**: Soft Dependency (Data Quality)
- **Relationship**: Sequential (extraction → visualization)
- **Status**: Paused (Priority 0-1 complete - 4/13 achievements)
- **Dependency**: Better extraction quality → better graph visualization
- **Benefit**: Perfect canonical ratio (100%), excellent entity types → cleaner graph
- **Timing**: Can start this PLAN now, visualization improves as extraction improves
- **Integration**: Extraction metrics feed into stage contribution dashboard
- **Read Before Starting**: Review completed achievements (ontology impact validated)

**PLAN_ENTITY-RESOLUTION-REFACTOR.md**:

- **Type**: Soft Dependency (Data Quality)
- **Relationship**: Sequential (resolution → visualization)
- **Status**: Paused (Priority 0-3 and 3.5 complete - 17/31 achievements)
- **Dependency**: Better entity resolution → fewer duplicate entities → cleaner graph
- **Benefit**: Stable entity IDs, cross-chunk resolution → unified entities in visualization
- **Timing**: Can start this PLAN now, graph quality improves as resolution improves
- **Integration**: Resolution metrics feed into stage contribution dashboard
- **Read Before Starting**: Review completed achievements (fuzzy matching, stable IDs working)

**PLAN_GRAPH-CONSTRUCTION-REFACTOR.md**:

- **Type**: Soft Dependency (Data Quality)
- **Relationship**: Sequential (construction → visualization)
- **Status**: Paused (Priority 0-3 complete - 11/17 achievements)
- **Dependency**: Better graph construction → better relationships → richer graph
- **Benefit**: Multi-predicate support, accurate source_count → better graph structure
- **Timing**: Can start this PLAN now, visualization improves as graph improves
- **Integration**: Construction metrics feed into stage contribution dashboard
- **Read Before Starting**: Review completed achievements (critical bugs fixed, correctness improved)

**PLAN_COMMUNITY-DETECTION-REFACTOR.md**:

- **Type**: Soft Dependency (Feature Enhancement)
- **Relationship**: Sequential (detection → visualization)
- **Status**: Paused (Priority 0-3 complete - 14/23 achievements)
- **Dependency**: Better community detection → better clusters → better visualization
- **Benefit**: Stable community IDs, multi-resolution → hierarchical navigation in UI
- **Timing**: Can start this PLAN now, community visualization improves as detection improves
- **Integration**: Detection metrics, multi-resolution levels feed into community explorer
- **Read Before Starting**: Review completed achievements (stable IDs, multi-resolution, quality gates)
- **Special**: Multi-resolution communities (Achievement 3.1) enable hierarchical UI navigation

**PLAN_STRUCTURED-LLM-DEVELOPMENT.md**:

- **Type**: Meta (Methodology)
- **Relationship**: Meta (defines how to execute this PLAN)
- **Status**: Paused (Priority 1 complete + enhancements - 11/13 sub-achievements)
- **Dependency**: Use IMPLEMENTATION_START_POINT.md, IMPLEMENTATION_END_POINT.md, MULTIPLE-PLANS-PROTOCOL.md
- **Timing**: Methodology ready for use
- **Integration**: Follow structured development approach

**Note on Experiment Infrastructure**:

- **Existing Infrastructure**: Basic experiment infrastructure already exists:
  - ✅ JSON-based configuration system (`--config` flag)
  - ✅ Experiment tracking in MongoDB (`experiment_tracking` collection)
  - ✅ Database isolation (read_db/write_db)
  - ✅ Basic comparison script (`scripts/compare_graphrag_experiments.py`)
- **This PLAN Enhances**: Achievements 2.3-2.6 add enhanced comparison, batch runner, visualization, and journal
- **Integration**: Experiment features leverage flexible pipeline execution (Achievement 0.1) and metrics (Priority 1)

### Code References

**Current Implementation**:

- `business/pipelines/graphrag.py` - Pipeline orchestration (to enhance)
- `business/pipelines/runner.py` - Stage runner (to enhance)
- `app/cli/graphrag.py` - CLI interface (to extend)
- `app/ui/streamlit_app.py` - Existing UI (reference)

**Observability Stack**:

- `docker-compose.observability.yml` - Observability services
- `observability/prometheus/prometheus.yml` - Prometheus config
- `observability/grafana/` - Grafana setup
- `observability/loki/` - Loki log aggregation
- `observability/promtail/` - Log shipping

**Stage Implementations**:

- `business/stages/graphrag/extraction.py` - Extraction stage
- `business/stages/graphrag/entity_resolution.py` - Resolution stage
- `business/stages/graphrag/graph_construction.py` - Construction stage
- `business/stages/graphrag/community_detection.py` - Detection stage

**Dependencies** (to add):

- `prometheus_client>=0.18.0` - Prometheus metrics
- `fastapi>=0.104.0` - API framework
- `uvicorn>=0.24.0` - ASGI server
- `websockets>=12.0` - WebSocket support
- `plotly>=5.17.0` or `D3.js` (via CDN) - Graph visualization
- Optional: `streamlit>=1.28.0` - Quick UI prototyping

### External Dependencies

**New Dependencies to Add**:

- `prometheus_client>=0.18.0` - Metrics export
- `fastapi>=0.104.0` - API framework
- `uvicorn>=0.24.0` - ASGI server
- `websockets>=12.0` - Real-time updates
- Optional: `streamlit>=1.28.0` - Dashboard prototyping

**Frontend Libraries** (via CDN):

- D3.js v7 or Cytoscape.js - Graph visualization
- Chart.js or Plotly.js - Charts and dashboards
- Bootstrap or Tailwind CSS - UI styling

---

## ⏱️ Time Estimates

**Priority 0** (Flexible Pipeline): 8-11 hours  
**Priority 1** (Metrics & Observability): 11-14 hours  
**Priority 2** (Stage Visualization & Experiments): 20-26 hours  
**Priority 3** (Graph Visualization): 15-19 hours  
**Priority 4** (Community Visualization): 11-14 hours  
**Priority 5** (Pipeline Control): 13-16 hours  
**Priority 6** (Advanced Dashboards): 12-15 hours  
**Priority 7** (Enhanced Features): 11-14 hours  
**Priority 8** (Testing & Docs): 15-19 hours

**Total**: 116-145 hours (if all priorities completed)

**Recommended Focus**: Priorities 0-2 (39-50 hours) for flexible pipeline, metrics, stage visualization, and experiment infrastructure

---

## 📊 Success Metrics

### Pipeline Flexibility (Priority 0)

- Stage selection: Target 100% working (any stage combination)
- Resume capability: Target 100% working (resume from any stage)
- Dependency validation: Target 0 invalid stage combinations

### Observability (Priority 1)

- Metrics export: Target <1s latency for metrics endpoint
- Dashboard refresh: Target <2s for Grafana panels
- Real-time updates: Target <500ms latency for WebSocket

### Visualization (Priority 2-4)

- UI responsiveness: Target <2s page loads
- Graph rendering: Target 1000+ nodes without lag
- API performance: Target 100+ req/sec
- User satisfaction: Target intuitive, useful

### Production Readiness (Overall)

- Uptime: Target 99.9% (pipeline monitoring)
- Error visibility: Target 100% errors tracked
- Test coverage: Target >70% for new code
- Documentation: Target complete (API, user guide, setup)

---

## 🚀 Immediate Next Steps

1. **Review This Plan** - Confirm scope, priorities, dependencies

2. **Read Dependency PLANs** - Understand what's complete:

   - PLAN_EXTRACTION-QUALITY-ENHANCEMENT.md (Priority 0-1 complete)
   - PLAN_ENTITY-RESOLUTION-REFACTOR.md (Priority 0-3 and 3.5 complete)
   - PLAN_GRAPH-CONSTRUCTION-REFACTOR.md (Priority 0-3 complete)
   - PLAN_COMMUNITY-DETECTION-REFACTOR.md (Priority 0-3 complete)

3. **Update ACTIVE_PLANS.md** - Add this PLAN with dependencies

4. **Add Dependencies** - Add API and metrics libraries to requirements.txt

5. **Create SUBPLAN_01**: Achievement 0.1 (Stage Selection & Partial Runs)

   - Design stage selection interface
   - Write tests first
   - Implement flexible execution

6. **Continue**: Work through Priority 0 systematically, then Priority 1

---

## 📝 Current Status & Handoff (For Pause/Resume)

**Last Updated**: 2025-11-06 23:15 UTC  
**Status**: Planning - Not Started

**Completed Achievements**: 0/30+ (0%)

**Pending Achievements**: All (Priorities 0-8)

**Next Steps**:

1. Review related PLANs (4 upstream dependencies)
2. Add this PLAN to ACTIVE_PLANS.md
3. Start with Priority 0 (Flexible Pipeline)
4. Create SUBPLAN for Achievement 0.1

**When Resuming**:

1. Follow IMPLEMENTATION_RESUME.md protocol
2. Read "Current Status & Handoff" section (this section)
3. Review Subplan Tracking (see what's done)
4. Select next achievement based on priority
5. Create SUBPLAN and continue

**Context Preserved**: This section + Subplan Tracking + Achievement Log = full context

**Key Dependencies**: 4 upstream PLANs (all paused after completing critical priorities) - See "Related Plans" section for integration points

---

## ✅ Completion Criteria

**This PLAN is Complete When**:

1. [ ] Flexible pipeline execution working (stage selection, resume, partial runs)
2. [ ] Prometheus metrics exported and Grafana dashboard created
3. [ ] Stage contribution visualization UI complete
4. [ ] Basic graph visualization working (entity/relationship browser)
5. [ ] Community explorer UI complete
6. [ ] Pipeline control API implemented
7. [ ] All tests passing (existing + new)
8. [ ] Documentation complete (API docs, user guide, dashboard setup)
9. [ ] Production validation successful
10. [ ] Observability stack fully utilized (Prometheus, Grafana, Loki)

---

## 🎯 Expected Outcomes

### Short-term (After Priority 0-1)

- Flexible pipeline execution for efficient development
- Real-time metrics monitoring during pipeline runs
- Grafana dashboard showing pipeline health
- Production-grade observability

### Medium-term (After Priority 2-3)

- Visual understanding of stage contributions
- Interactive graph exploration
- Entity/relationship browsing
- Quality monitoring dashboards

### Long-term (After Priority 4-8)

- Complete GraphRAG visualization system
- Community exploration with multi-resolution navigation
- Production operations dashboard
- Comprehensive API for integration
- Export capabilities for external tools

---

## 🔥 Critical Dependencies

### Upstream PLANs (Soft Dependencies)

**All 4 PLANs are PAUSED after completing critical priorities**:

1. **PLAN_EXTRACTION-QUALITY-ENHANCEMENT.md** (4/13 complete):

   - Status: Priority 0-1 complete (extraction validated, quality tools created)
   - Impact: 100% canonical ratio → cleaner extraction metrics
   - Integration: Extraction quality metrics available for dashboard

2. **PLAN_ENTITY-RESOLUTION-REFACTOR.md** (17/31 complete):

   - Status: Priority 0-3 and 3.5 complete (cross-chunk resolution, fuzzy matching, data integrity fixed)
   - Impact: Fewer duplicate entities → cleaner graph visualization
   - Integration: Resolution metrics (merge rate, LLM usage) available for dashboard

3. **PLAN_GRAPH-CONSTRUCTION-REFACTOR.md** (11/17 complete):

   - Status: Priority 0-3 complete (critical bugs fixed, correctness improved, performance optimized)
   - Impact: Multi-predicate support, accurate metrics → richer graph structure
   - Integration: Graph construction metrics available for dashboard

4. **PLAN_COMMUNITY-DETECTION-REFACTOR.md** (14/23 complete):
   - Status: Priority 0-3 complete (stable IDs, ontology integration, multi-resolution)
   - Impact: Multi-resolution communities → hierarchical UI navigation
   - Integration: Detection quality metrics, multiple resolutions available

**None are blocking**: All critical foundations complete, can start this PLAN now

**All are beneficial**: This PLAN's visualizations improve as upstream PLANs improve

### Recommended Sequencing

1. **Start this PLAN Priority 0-1** (Pipeline flexibility + Metrics) - No blockers
2. **Parallel**: Continue any upstream PLAN's advanced features (Priorities 4-7)
3. **This PLAN Priority 2-3** (Stage & Graph Visualization) - Benefits from upstream improvements
4. **Coordinate**: If upstream plans add new metrics, integrate into dashboards

---

## 🚀 Why This Plan Now

**Motivation**:

1. **Production Operations**: Need monitoring and control for production deployments
2. **Quality Validation**: Need visualization to validate improvements from 4 upstream plans
3. **User Experience**: Need UI for exploring the knowledge graph
4. **Experimentation**: Need flexible execution for running experiments (PLAN-EXPERIMENT-INFRASTRUCTURE.md)
5. **Observability Gap**: Have observability stack but not integrated
6. **Foundation Ready**: 4 upstream plans have stable, production-ready foundations

**Impact of Completion**:

- Production-ready pipeline with monitoring and control
- Visual validation of graph quality
- User-friendly exploration of knowledge graph
- Flexible execution for development and experiments
- Comprehensive observability (metrics, logs, traces)
- Foundation for graph-powered applications

---

**Status**: PLAN Created and Ready  
**Next**: Review plan, update ACTIVE_PLANS.md, create first SUBPLAN (Achievement 0.1 - Stage Selection)
