# Metrics Library - Micro Implementation Plan

**Date**: November 3, 2025  
**Total Time**: 8-12 hours  
**Approach**: Small steps with review points  
**Goal**: Track stage progression, performance, and failures

---

## 🎯 Micro-Phase Breakdown

### Phase 1A: Metric Collectors (2 hours) ✋ REVIEW POINT

**What to Build**:

```python
# core/libraries/metrics/collectors.py
# - Counter (count events)
# - Gauge (current value)
# - Histogram (timing/distribution)
```

**Deliverable**:

- 1 file (~150 lines)
- 3 metric classes
- Simple in-memory storage

**Review**: Check if metric classes are flexible enough

---

### Phase 1B: Metric Registry (1 hour) ✋ REVIEW POINT

**What to Build**:

```python
# core/libraries/metrics/registry.py
# - MetricRegistry (singleton)
# - Register/retrieve metrics
# - Collect all for export
```

**Deliverable**:

- 1 file (~80 lines)
- Central registry
- Singleton pattern

**Review**: Verify registry design

---

### Phase 2A: Prometheus Exporter (2 hours) ✋ REVIEW POINT

**What to Build**:

```python
# core/libraries/metrics/exporters.py
# - export_prometheus() - Format metrics for Prometheus
# - Simple HTTP endpoint (TODO: full server later)
```

**Deliverable**:

- 1 file (~100 lines)
- Prometheus text format
- Basic exporter

**Review**: Check Prometheus format correctness

---

### Phase 2B: Package & Export (30 min) ✋ REVIEW POINT

**What to Build**:

```python
# core/libraries/metrics/__init__.py
# Clean exports, documentation
```

**Deliverable**:

- Public API defined
- Usage examples

**Review**: API clear and usable?

---

### Phase 3A: Apply to BaseStage (1.5 hours) ✋ REVIEW POINT

**What to Add**:

```python
# Track stage metrics:
# - stage_started
# - stage_completed
# - stage_failed
# - stage_duration
# - documents_processed
```

**Deliverable**:

- BaseStage enhanced with metrics
- All 13 stages inherit

**Review**: Verify metrics tracked correctly

---

### Phase 3B: Apply to Pipeline Runner (1 hour) ✋ REVIEW POINT

**What to Add**:

```python
# Track pipeline metrics:
# - pipeline_started
# - pipeline_completed
# - pipeline_stage_failures
```

**Deliverable**:

- Pipeline runner with metrics
- Complete pipeline visibility

**Review**: Sufficient pipeline metrics?

---

### Phase 4: Integration Test (1 hour) ✋ REVIEW POINT

**What to Test**:

```bash
# Run 1-chunk pipeline
# Check metrics collected
# Verify Prometheus export
```

**Deliverable**:

- Working metrics in real pipeline
- Export verified

**Review**: Metrics useful and accurate?

---

### Phase 5: Grafana Dashboard (2 hours) ✋ REVIEW POINT

**What to Create**:

```yaml
# Grafana dashboard JSON
# - Stage duration chart
# - Success/failure counts
# - Document processing rate
```

**Deliverable**:

- Working Grafana dashboard
- Visualizes metrics

**Review**: Dashboard shows useful information?

---

## ⏸️ Review Points Summary

**8 Review Points Total**:

1. ✋ Metric collectors design
2. ✋ Registry pattern
3. ✋ Prometheus exporter
4. ✋ Public API
5. ✋ BaseStage metrics
6. ✋ Pipeline metrics
7. ✋ Integration test
8. ✋ Grafana dashboard

**Time Between Reviews**: 30 min - 2 hours

---

## 🎯 Starting Point: Phase 1A

**I'll start with Phase 1A** (Metric Collectors, 2 hours):

**What I'll build**:

- Counter class (increment/get)
- Gauge class (set/get current value)
- Histogram class (observe values, get summary)
- Simple in-memory storage
- Label support

**Then show you for review before Phase 1B**

**Ready to start?**
