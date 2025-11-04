# Master Plan: Observability + Code Cleanup + Pending Work

**Date**: November 2, 2025  
**Context**: Post-refactor cleanup + observability implementation + holistic backlog  
**Goal**: Clean, observable, production-ready system with clear roadmap

---

## 🎯 Complete Scope Overview

### Part 1: Observability Implementation (HIGH PRIORITY)

- 4 Libraries: error_handling, metrics, retry, logging (enhance)
- Observability Stack: Grafana + Prometheus + Loki
- Integration with existing code

### Part 2: Code Cleanup (HIGH PRIORITY)

- Review all 69 code files
- Remove repetition
- Extract to libraries
- Improve readability

### Part 3: Documentation Consolidation (MEDIUM PRIORITY)

- Archive migration documents
- Keep only ongoing tasks + essentials in root
- Update documentation/ folder

### Part 4: Delayed Work Inventory (ONGOING)

- GraphRAG: Community detection fix, enhancements
- Testing: Comprehensive test suite
- MCP Server: Implementation
- Multi-source: PDF, HTML ingestion

---

## 📊 Part 1: Observability Implementation (Week 1-2)

### Phase 1.1: Error Handling Library (10-15 hours)

**Goal**: Never have empty error messages again

**What to Build**:

**1. Exception Hierarchy** (3 hours):

```python
# core/libraries/error_handling/exceptions.py

class ApplicationError(Exception):
    """Base exception with context support."""
    def __init__(self, message, context=None, cause=None):
        self.message = message
        self.context = context or {}
        self.cause = cause
        super().__init__(self._format_message())

    def _format_message(self):
        msg = self.message
        if self.context:
            ctx = ", ".join(f"{k}={v}" for k, v in self.context.items())
            msg += f" [Context: {ctx}]"
        if self.cause:
            msg += f" [Cause: {type(self.cause).__name__}: {self.cause}]"
        return msg

class StageError(ApplicationError):
    """Stage execution errors."""
    pass

class AgentError(ApplicationError):
    """Agent execution errors."""
    pass

class PipelineError(ApplicationError):
    """Pipeline orchestration errors."""
    pass

class ConfigurationError(ApplicationError):
    """Configuration validation errors."""
    pass
```

**2. Error Decorator** (4 hours):

```python
# core/libraries/error_handling/decorators.py

def handle_errors(
    fallback=None,
    log_traceback=True,
    capture_context=True,
    reraise=True
):
    """Decorator for comprehensive error handling."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # ALWAYS show exception type (prevents empty messages)
                error_type = type(e).__name__
                error_msg = str(e) or "(no message)"
                full_msg = f"{error_type}: {error_msg}"

                # Add function context
                if capture_context:
                    full_msg += f" [in {func.__module__}.{func.__name__}]"

                # Log with full traceback
                logger = logging.getLogger(func.__module__)
                if log_traceback:
                    logger.error(full_msg, exc_info=True)
                else:
                    logger.error(full_msg)

                if fallback is not None:
                    return fallback
                if reraise:
                    raise
        return wrapper
    return decorator
```

**3. Context Manager** (3 hours):

```python
# core/libraries/error_handling/context.py

class error_context:
    """Context manager for error enrichment."""
    def __init__(self, operation, **context):
        self.operation = operation
        self.context = context

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            msg = f"{exc_type.__name__} in {self.operation}: {exc_val or '(no message)'}"
            for k, v in self.context.items():
                msg += f"\n  {k}: {v}"
            logging.error(msg, exc_info=True)
        return False
```

**4. Integration** (2 hours):

- Apply to pipeline runner
- Apply to stage base class
- Test on 1 chunk

**Total**: 12 hours  
**Priority**: #1 CRITICAL

---

### Phase 1.2: Metrics Library (8-12 hours)

**Goal**: Track stage progression, performance, failures

**What to Build**:

**1. Metric Collectors** (4 hours):

```python
# core/libraries/metrics/collectors.py

class Counter:
    """Simple counter metric."""
    def __init__(self, name, description="", labels=None):
        self.name = name
        self.description = description
        self.labels = labels or []
        self._values = {}

    def inc(self, amount=1, labels=None):
        key = self._make_key(labels)
        self._values[key] = self._values.get(key, 0) + amount

    def get(self, labels=None):
        return self._values.get(self._make_key(labels), 0)

class Histogram:
    """Simple histogram for timing."""
    def __init__(self, name, description=""):
        self.name = name
        self.values = []

    def observe(self, value):
        self.values.append(value)

    def summary(self):
        if not self.values:
            return {}
        return {
            'count': len(self.values),
            'sum': sum(self.values),
            'min': min(self.values),
            'max': max(self.values),
            'avg': sum(self.values) / len(self.values)
        }
```

**2. Registry** (2 hours):

```python
# core/libraries/metrics/registry.py

class MetricRegistry:
    """Central metric registry."""
    _instance = None

    def __init__(self):
        self.metrics = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = MetricRegistry()
        return cls._instance

    def register(self, metric):
        self.metrics[metric.name] = metric

    def collect_all(self):
        """Collect all metrics for export."""
        return {name: metric for name, metric in self.metrics.items()}
```

**3. Prometheus Exporter** (4 hours):

```python
# core/libraries/metrics/exporters.py

def export_prometheus(metrics):
    """Export metrics in Prometheus format."""
    lines = []
    for name, metric in metrics.items():
        if isinstance(metric, Counter):
            lines.append(f"# TYPE {name} counter")
            for labels, value in metric._values.items():
                label_str = ",".join(f'{k}="{v}"' for k, v in labels.items())
                lines.append(f"{name}{{{label_str}}} {value}")
        # ... similar for Histogram
    return "\n".join(lines)

# Simple HTTP endpoint for Prometheus scraping
def start_metrics_server(port=9090):
    """Start HTTP server for Prometheus."""
    # TODO: Simple HTTP server serving /metrics endpoint
```

**4. Integration** (2 hours):

- Add to BaseStage
- Add to pipeline runner
- Track: stage_started, stage_completed, stage_failed, stage_duration

**Total**: 12 hours  
**Priority**: #2 CRITICAL

---

### Phase 1.3: Retry Library (5-8 hours)

**Goal**: Automatic retries for transient failures

**What to Build**:

**1. Retry Decorator** (3 hours):

```python
# core/libraries/retry/decorators.py

def with_retry(
    max_attempts=3,
    backoff='exponential',
    base_delay=1.0,
    max_delay=60.0,
    retry_on=(Exception,)
):
    """Decorator for automatic retries."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except retry_on as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        raise

                    # Calculate delay
                    if backoff == 'exponential':
                        delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
                    else:
                        delay = base_delay

                    logger.warning(f"Attempt {attempt} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
        return wrapper
    return decorator
```

**2. Retry Policies** (2 hours):

```python
# core/libraries/retry/policies.py

class RetryPolicy:
    """Simple retry policy."""
    def __init__(self, max_attempts=3, backoff_multiplier=2.0):
        self.max_attempts = max_attempts
        self.backoff_multiplier = backoff_multiplier

    def should_retry(self, attempt, exception):
        return attempt < self.max_attempts

    def get_delay(self, attempt):
        return self.backoff_multiplier ** attempt

# TODO: Circuit breaker pattern (implement when needed)
```

**3. Integration** (2 hours):

- Apply to LLM calls in agents
- Apply to MongoDB operations
- Test on failing operations

**Total**: 7 hours  
**Priority**: #3 HIGH

---

### Phase 1.4: Logging Enhancement (3-4 hours)

**Goal**: Better error messages, stage transitions

**What to Add**:

**1. Exception Logger** (1 hour):

```python
# core/libraries/logging/exceptions.py

def log_exception(logger, message, exception, context=None):
    """Log exception with guaranteed type and traceback."""
    exc_type = type(exception).__name__
    exc_msg = str(exception) or "(no message)"
    full_msg = f"{message}: {exc_type}: {exc_msg}"

    if context:
        full_msg += f" [Context: {context}]"

    logger.error(full_msg, exc_info=True)
```

**2. Stage Lifecycle Logging** (2 hours):

```python
# core/libraries/logging/stages.py

def log_stage_lifecycle(stage_name):
    """Decorator for stage lifecycle logging."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.info(f"[STAGE] ▶ Starting {stage_name}")
            start = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start
                logger.info(f"[STAGE] ✓ {stage_name} completed in {duration:.1f}s")
                return result
            except Exception as e:
                duration = time.time() - start
                logger.error(f"[STAGE] ✗ {stage_name} failed after {duration:.1f}s", exc_info=True)
                raise
        return wrapper
    return decorator
```

**Total**: 3 hours  
**Priority**: #4 HIGH

---

### Phase 1.5: Observability Stack Setup (8-12 hours)

**Goal**: Grafana + Prometheus + Loki in Docker

**What to Build**:

**1. Docker Compose** (3 hours):

```yaml
# docker-compose.observability.yml
version: "3.8"

services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./observability/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - "--config.file=/etc/prometheus/prometheus.yml"
      - "--storage.tsdb.path=/prometheus"

  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    volumes:
      - ./observability/loki-config.yml:/etc/loki/local-config.yaml
      - loki-data:/loki

  promtail:
    image: grafana/promtail:latest
    volumes:
      - ./logs:/var/log/app
      - ./observability/promtail-config.yml:/etc/promtail/config.yml
    command: -config.file=/etc/promtail/config.yml

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
      - ./observability/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./observability/grafana/datasources:/etc/grafana/provisioning/datasources
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

volumes:
  prometheus-data:
  loki-data:
  grafana-data:
```

**2. Configuration Files** (3 hours):

- prometheus.yml (scrape configs)
- loki-config.yml (log ingestion)
- promtail-config.yml (log shipping)
- Grafana datasources (Prometheus + Loki)

**3. Grafana Dashboards** (4 hours):

- Pipeline execution dashboard
- Stage metrics (processed, failed, duration)
- Error rate by type
- Log viewer with filters

**4. Integration Guide** (2 hours):

- How to start stack
- How to view metrics
- How to query logs
- Dashboard usage

**Total**: 12 hours  
**Priority**: #5 HIGH

---

## 📊 Part 2: Code Review & Cleanup (Week 3-4)

### Phase 2.1: Code Review Methodology

**Scope**: All 69 files across 4 layers

**For Each File, Identify**:

1. Repeated patterns (extract to libraries)
2. Hard-coded values (move to config)
3. Complex functions (split into smaller)
4. Missing type hints (add)
5. Missing docstrings (add)
6. Error handling issues (apply library)
7. TODO comments (track)

**Output**: Cleanup report per domain

---

### Phase 2.2: Review by Domain (20-30 hours)

**GraphRAG Domain** (8-10 hours):

- 6 agents: extraction, entity_resolution, relationship_resolution, community_detection, community_summarization, link_prediction
- 4 stages: extraction, entity_resolution, graph_construction, community_detection
- 4 services: indexes, query, retrieval, generation

**Focus**:

- Agent initialization (use BaseAgent properly)
- Error handling (apply library)
- LLM calls (use retry library)
- Stats tracking (use metrics library)

---

**Ingestion Domain** (6-8 hours):

- 3 agents: clean, enrich, trust
- 9 stages: ingest, clean, chunk, enrich, embed, redundancy, trust, backfill, compress
- 2 services: transcripts, metadata

**Focus**:

- Collection access patterns (standardize)
- Configuration loading (use library when ready)
- Error handling
- Progress logging

---

**RAG Domain** (4-6 hours):

- 3 agents: reference_answer, topic_reference, planner
- 8 services: core, generation, retrieval, indexes, filters, feedback, persona_utils, profiles
- 4 queries: vector_search, llm_question, get, videos_insights

**Focus**:

- Service patterns
- Query optimization
- Error handling

---

**Chat Domain** (2-3 hours):

- 4 modules: memory, query_rewriter, retrieval, answering
- 3 services: filters, citations, export

**Focus**:

- Recently extracted, minimal cleanup
- Apply error handling
- Add type hints

---

**Pipeline & Base Classes** (4-6 hours):

- 3 pipelines: runner, ingestion, graphrag
- 2 base classes: BaseStage, BaseAgent

**Focus**:

- Integration with libraries
- Remove boilerplate
- Enhance with observability

---

**Total Review**: 24-33 hours across all domains

---

### Phase 2.3: Apply Libraries to Code (10-15 hours)

**After libraries are built, apply them**:

**1. BaseAgent Refactor** (3 hours):

```python
from core.libraries.logging import get_logger
from core.libraries.error_handling import handle_errors, AgentError
from core.libraries.retry import with_retry
from core.libraries.metrics import Counter

agent_calls = Counter('agent_llm_calls', labels=['agent_name'])
agent_errors = Counter('agent_errors', labels=['agent_name', 'error_type'])

class BaseAgent:
    def __init__(self, **kwargs):
        self.logger = get_logger(f"agents.{self.__class__.__name__}")
        self._setup(**kwargs)

    @with_retry(max_attempts=3)
    @handle_errors(log_traceback=True)
    def call_llm(self, prompt):
        agent_calls.inc(labels={'agent_name': self.__class__.__name__})
        # ... LLM call
```

**2. BaseStage Refactor** (3 hours):

```python
from core.libraries.logging import get_logger, set_log_context
from core.libraries.error_handling import handle_errors, StageError
from core.libraries.metrics import Counter, Histogram

stage_processed = Counter('stage_processed', labels=['stage_name'])
stage_duration = Histogram('stage_duration_seconds')

class BaseStage:
    def __init__(self):
        self.logger = get_logger(f"stages.{self.__class__.__name__}")

    @handle_errors(log_traceback=True)
    def run(self, config):
        set_log_context(stage=self.name)
        start = time.time()

        # ... existing run logic ...

        duration = time.time() - start
        stage_duration.observe(duration)
        stage_processed.inc(labels={'stage_name': self.name})
```

**3. Pipeline Runner Refactor** (2 hours):

```python
from core.libraries.logging import log_exception
from core.libraries.error_handling import error_context, PipelineError
from core.libraries.metrics import Counter

def run(self):
    for spec in self.specs:
        with error_context(
            f"pipeline_stage_{spec.stage}",
            stage=spec.stage,
            total_stages=len(self.specs)
        ):
            stage_cls = self._resolve_stage_class(spec.stage)
            stage = stage_cls()
            code = stage.run(config)
```

**4. All Agents** (2-3 hours):

- Remove manual initialization (use BaseAgent)
- Remove manual retry loops (use @with_retry)
- Apply @handle_errors where needed

**5. All Stages** (2-3 hours):

- Standardize error handling
- Add metrics tracking
- Verify logging

**6. Services** (2-3 hours):

- Apply error handling
- Add retry to DB operations
- Track metrics

**Total**: 14-17 hours

---

## 📊 Part 3: Documentation Consolidation (Week 2-3)

### Phase 3.1: Identify Documents to Archive (1 hour)

**Root-level docs to archive** (~15 files):

- All `MIGRATION-*.md` files
- All `FOLDER-STRUCTURE-*.md` files
- `REFACTOR-*.md` files
- `GRAPHRAG-PHASE*.md` files
- `SESSION-SUMMARY-*.md` files

**Keep in root**:

- README.md
- requirements.txt
- .env.example
- TODO.md
- BUGS.md
- CHANGELOG.md
- Ongoing: GRAPHRAG-13K-CORRECT-ANALYSIS.md, LIBRARY-IMPLEMENTATION-\*.md

---

### Phase 3.2: Consolidate & Archive (3-4 hours)

**Create**: `documentation/archive/refactor-oct-2025/`

**Structure**:

```
documentation/archive/refactor-oct-2025/
├── INDEX.md                    # Archive guide
├── planning/
│   ├── FOLDER-STRUCTURE-REFACTOR-*.md
│   └── VERTICAL-SEGMENTATION-*.md
├── migration/
│   ├── MIGRATION-*.md
│   └── CHAT-EXTRACTION-*.md
└── completion/
    ├── SESSION-SUMMARY-*.md
    └── REFACTOR-PROJECT-COMPLETE-*.md
```

**Also Update**:

- documentation/README.md (add refactor archive)
- Root README.md (clean structure overview)

**Total**: 4 hours

---

### Phase 3.3: Update Current Documentation (2-3 hours)

**Update**:

- documentation/architecture/\* (add library references)
- documentation/guides/EXECUTION.md (observability usage)
- Create: documentation/guides/OBSERVABILITY.md

**Total**: 3 hours

---

## 📊 Part 4: Complete Backlog Inventory

### From Previous Planning:

**GraphRAG Work**:

1. ⏳ Fix community detection (Louvain) - 15 min
2. ⏳ Re-run entity_resolution + graph_construction + community_detection - 6-8 hours
3. ⏳ Validate graph quality - 1 hour
4. ⏳ Fix link prediction validation error - 1 hour
5. ⏳ Enhanced entity resolution (fuzzy matching) - 8-10 hours (LATER)
6. ⏳ Graph visualization - 8-12 hours (LATER)
7. ⏳ Knowledge hole detection - 8-12 hours (LATER)

**Testing**: 8. ⏳ Unit tests for core - 15-20 hours 9. ⏳ Unit tests for agents - 8-10 hours 10. ⏳ Integration tests - 10-15 hours 11. ⏳ End-to-end tests - 5-10 hours

**MCP Server**: 12. ⏳ FastAPI setup - 3-4 hours 13. ⏳ Knowledge graph endpoints - 5-8 hours 14. ⏳ Query endpoints - 3-5 hours 15. ⏳ Chat endpoints - 2-3 hours 16. ⏳ Authentication - 2-3 hours 17. ⏳ Deployment - 5-8 hours

**Other Libraries** (Tier 2 from our 18): 18. ⏳ Validation - 3-4 hours 19. ⏳ Configuration - 2-3 hours 20. ⏳ Caching - 2-3 hours 21. ⏳ Database - 3-4 hours 22. ⏳ LLM - 3-4 hours 23. ⏳ Concurrency - 2-3 hours (move) 24. ⏳ Rate Limiting - 2-3 hours (move) 25. ⏳ Serialization - 3-4 hours 26. ⏳ Data Transform - 2-3 hours

**Content**: 27. ⏳ Publish 5 LinkedIn articles - 2-4 hours

---

## 🎯 Consolidated Master Plan

### Week 1 (Nov 4-8): Observability Foundation

**Monday** (8 hours):

- Error Handling library (full implementation)
- Apply to pipeline runner
- Test on 1 chunk - verify error visibility

**Tuesday** (8 hours):

- Metrics library (collectors, registry)
- Prometheus exporter
- Apply to BaseStage

**Wednesday** (8 hours):

- Retry library (decorator, policies)
- Apply to agents (LLM calls)
- Logging enhancements

**Thursday** (8 hours):

- Observability stack (Docker Compose)
- Prometheus + Loki + Grafana setup
- Basic dashboards

**Friday** (8 hours):

- Integration testing
- Apply libraries to all agents/stages
- Test 10-chunk run with full observability

**Total**: 40 hours  
**Outcome**: Complete observability, ready for GraphRAG recovery

---

### Week 2 (Nov 11-15): Code Cleanup + GraphRAG Recovery

**Monday-Tuesday** (12-16 hours):

- Code review: GraphRAG domain (8-10 hrs)
- Code review: Ingestion domain (6-8 hrs)
- Apply findings

**Wednesday** (8 hours):

- Code review: RAG + Chat domains (6-8 hrs)
- Code review: Pipelines + Base classes (4-6 hrs)

**Thursday** (4 hours):

- Documentation consolidation
- Archive migration docs
- Update current docs

**Friday** (8 hours):

- Install graspologic
- Fix community detection (Louvain)
- Re-run GraphRAG stages 2-4 on 13k data
- **Monitor with Grafana!**

**Total**: 40 hours  
**Outcome**: Clean code, complete graph data

---

### Week 3 (Nov 18-22): Testing Foundation

**Monday-Wednesday** (24 hours):

- Unit tests for core models (8 hrs)
- Unit tests for domain utilities (6 hrs)
- Unit tests for libraries (10 hrs)

**Thursday-Friday** (16 hours):

- Unit tests for agents (8 hrs)
- Unit tests for services (8 hrs)

**Total**: 40 hours  
**Outcome**: Test foundation

---

### Week 4 (Nov 25-29): Integration Tests + Tier 2 Libraries

**Monday-Tuesday** (16 hours):

- Integration tests for stages (8 hrs)
- Integration tests for pipelines (8 hrs)

**Wednesday-Friday** (24 hours):

- Move Concurrency library (2 hrs)
- Move Rate Limiting library (2 hrs)
- Validation library (3 hrs)
- Configuration library (2 hrs)
- Serialization library (3 hrs)
- Database library (3 hrs)
- LLM library (3 hrs)
- Caching library (2 hrs)
- Data Transform library (2 hrs)
- Integration testing (2 hrs)

**Total**: 40 hours  
**Outcome**: All Tier 2 libraries, comprehensive tests

---

### Month 2 (December): MCP Server + Advanced Features

**Week 1-2** (80 hours):

- MCP Server implementation (20-30 hrs)
- Graph-aware queries (15-20 hrs)
- Enhanced features per needs (20-30 hrs)

---

## 📈 Effort Summary

| Phase       | Focus                            | Effort      | Timeline       |
| ----------- | -------------------------------- | ----------- | -------------- |
| **Week 1**  | Observability (4 libs + stack)   | 40 hrs      | Nov 4-8        |
| **Week 2**  | Code cleanup + GraphRAG recovery | 40 hrs      | Nov 11-15      |
| **Week 3**  | Testing foundation               | 40 hrs      | Nov 18-22      |
| **Week 4**  | Integration tests + Tier 2 libs  | 40 hrs      | Nov 25-29      |
| **Month 2** | MCP Server + features            | 80 hrs      | December       |
| **Total**   | **Complete System**              | **240 hrs** | **2.5 months** |

**Pace**: 40 hours/week (full-time) OR 20 hours/week (half-time) = 5 months

---

## 🎯 Detailed Week 1 Plan (Observability)

### Monday (Error Handling - 8 hours)

**Morning** (4 hours):

1. Create exception hierarchy (ApplicationError, StageError, AgentError, etc.)
2. Implement error decorator (@handle_errors)
3. Create error context manager
4. Write tests

**Afternoon** (4 hours): 5. Apply to app/cli/graphrag.py (pipeline entry point) 6. Apply to business/pipelines/runner.py (stage execution) 7. Apply to business/pipelines/graphrag.py (pipeline logic) 8. Test on 1 chunk - verify error messages visible

**Deliverable**: Never have empty error messages  
**Verification**: Re-create the failure, see full error message

---

### Tuesday (Metrics - 8 hours)

**Morning** (4 hours):

1. Implement Counter, Histogram classes
2. Create MetricRegistry
3. Implement Prometheus exporter
4. Write tests

**Afternoon** (4 hours): 5. Add to BaseStage (track processed, failed, duration) 6. Add to pipeline runner (track stage progression) 7. Create /metrics HTTP endpoint 8. Test metrics export

**Deliverable**: Stage progression visible  
**Verification**: See metrics in /metrics endpoint

---

### Wednesday (Retry + Logging - 8 hours)

**Morning** (4 hours):

1. Implement @with_retry decorator
2. Create RetryPolicy classes
3. Write tests
4. Apply to agents (LLM calls)

**Afternoon** (4 hours): 5. Add log_exception helper to logging library 6. Add stage lifecycle logging 7. Apply to pipeline runner 8. Test on failing operation

**Deliverable**: Auto-retry + better logs  
**Verification**: See retry attempts, stage lifecycle in logs

---

### Thursday (Observability Stack - 8 hours)

**Morning** (4 hours):

1. Create docker-compose.observability.yml
2. Create Prometheus config (scrape /metrics)
3. Create Loki config (ingest logs)
4. Create Promtail config (ship logs)

**Afternoon** (4 hours): 5. Create Grafana datasources 6. Create basic dashboard (stage metrics) 7. Test: Start stack, see metrics, see logs 8. Document usage

**Deliverable**: Grafana dashboard showing metrics + logs  
**Verification**: docker-compose up, visit localhost:3000

---

### Friday (Integration + Validation - 8 hours)

**Morning** (4 hours):

1. Apply error handling to all agents
2. Apply metrics to all stages
3. Apply retry to all services
4. Enhanced logging everywhere

**Afternoon** (4 hours): 5. Test 10-chunk run 6. Watch Grafana dashboard 7. Verify all metrics appearing 8. Verify logs in Loki 9. Validate error messages clear 10. Document findings

**Deliverable**: Fully observable system  
**Verification**: 10 chunks processed, all visible in Grafana

---

## 📋 Success Criteria

### Week 1 Complete When:

- ✅ Error messages show type + traceback
- ✅ Metrics track all stages
- ✅ Retry works for transient failures
- ✅ Grafana shows pipeline execution
- ✅ Loki shows all logs
- ✅ 10-chunk test run fully observable

### Code Cleanup Complete When:

- ✅ All 69 files reviewed
- ✅ Repetition extracted to libraries
- ✅ Error handling applied everywhere
- ✅ Type hints added
- ✅ Docstrings complete

### Ready for Production When:

- ✅ Observability complete
- ✅ Code clean
- ✅ Tests passing (unit + integration)
- ✅ GraphRAG validated (after recovery)
- ✅ Documentation current

---

## 🎊 Final Structure After All Work

```
app/ (14 files)
business/
  ├── domains/ (if reorganized)
  │   ├── graphrag/
  │   ├── ingestion/
  │   ├── rag/
  │   └── chat/
  └── shared/
core/
  ├── models/
  ├── base/ (enhanced with libraries)
  ├── domain/
  ├── config/
  └── libraries/ (18 total)
      ├── logging/ ✅ DONE
      ├── error_handling/ ← Week 1
      ├── metrics/ ← Week 1
      ├── retry/ ← Week 1
      └── [14 others] ← Later
dependencies/
observability/ (NEW)
  ├── docker-compose.yml
  ├── prometheus.yml
  ├── loki-config.yml
  ├── promtail-config.yml
  └── grafana/
      ├── dashboards/
      └── datasources/
tests/ (comprehensive)
documentation/ (clean)
```

---

## 🎯 What This Plan Delivers

### Immediate (Week 1):

✅ Never be blind to errors again  
✅ See pipeline execution in real-time  
✅ Track metrics and performance  
✅ Automatic retries for failures

### Short-term (Month 1):

✅ Clean, readable code  
✅ GraphRAG data recovered  
✅ Comprehensive tests  
✅ All Tier 2 libraries implemented

### Long-term (Month 2+):

✅ MCP Server  
✅ Production deployment  
✅ Advanced features

---

## 📊 Total Effort Breakdown

| Category                       | Effort      | Priority |
| ------------------------------ | ----------- | -------- |
| Observability (4 libs + stack) | 40 hrs      | CRITICAL |
| Code cleanup (all files)       | 30 hrs      | HIGH     |
| Documentation consolidation    | 7 hrs       | MEDIUM   |
| GraphRAG recovery              | 8 hrs       | HIGH     |
| Testing foundation             | 80 hrs      | HIGH     |
| Tier 2 libraries               | 24 hrs      | MEDIUM   |
| MCP Server                     | 80 hrs      | MEDIUM   |
| **Total Identified**           | **269 hrs** | -        |

**Timeline**: 2-3 months @ 40 hrs/week OR 5-6 months @ 20 hrs/week

---

## 🚀 Decision Point

**This plan is comprehensive and achievable. Ready for your approval to proceed with**:

**Week 1: Observability Implementation**

- Error Handling library (Monday)
- Metrics library (Tuesday)
- Retry library + Logging enhance (Wednesday)
- Observability stack (Thursday)
- Integration + Testing (Friday)

**Shall I start with Error Handling library implementation on Monday?**
