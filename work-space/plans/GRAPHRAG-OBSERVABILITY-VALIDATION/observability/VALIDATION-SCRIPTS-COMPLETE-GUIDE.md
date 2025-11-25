# GRAPHRAG Observability Validation - Complete Test Scripts Guide

## 📋 Overview

This directory contains **comprehensive automated test scripts** for validating all achievements in the GRAPHRAG Observability Validation plan. Each achievement that requires validation has a dedicated test script.

---

## 🗂️ Test Scripts Inventory

### Master Validation Script

| Script                         | Purpose                                                    | Achievements Covered                  |
| ------------------------------ | ---------------------------------------------------------- | ------------------------------------- |
| `validate-all-achievements.sh` | **Master script** - Runs all achievement tests in sequence | 0.1 through 3.2 (all 11 achievements) |

### Individual Achievement Test Scripts

| Achievement                           | Script                                       | Tests              | Status            |
| ------------------------------------- | -------------------------------------------- | ------------------ | ----------------- |
| **0.1** Collection Name Compatibility | N/A                                          | Configuration task | ✅ No test needed |
| **0.2** Configuration Compatibility   | N/A                                          | Audit task         | ✅ No test needed |
| **0.3** Environment Variables         | N/A                                          | Documentation task | ✅ No test needed |
| **1.1** Observability Stack Running   | `../../observability/04-e2e-test.sh`         | 6 tests            | ✅ Exists         |
| **1.2** Metrics Endpoint Validated    | `../../observability/09-validate-metrics.sh` | 6 tests            | ✅ Exists         |
| **1.3** Grafana Dashboards Configured | `test-achievement-1.3-dashboards.sh`         | 16 tests           | ✅ Created        |
| **2.1** Baseline Pipeline Run         | `test-achievement-2.1-baseline.sh`           | 16 tests           | ✅ Created        |
| **2.2** Observability Pipeline Run    | `test-achievement-2.2-observability.sh`      | 28 tests           | ✅ Created        |
| **2.3** Data Quality Validation       | N/A                                          | Redundant with 2.2 | ✅ No test needed |
| **3.1** Query Scripts Validated       | `test-all-query-scripts.sh`                  | 9 tests            | ✅ Exists         |
| **3.2** Explanation Tools Validated   | `test-all-explanation-tools.sh`              | 5 tests            | ✅ Exists         |

**Total Test Scripts**: 8 (3 new + 5 existing)  
**Total Automated Tests**: 86 tests across all achievements

---

## 🚀 Quick Start

### Option 1: Run All Validations (Recommended)

```bash
# Set required environment variables
export MONGODB_URI="mongodb+srv://user:pass@cluster.mongodb.net/validation_01"
export DB_NAME="validation_01"
export TRACE_ID="6088e6bd-e305-42d8-9210-e2d3f1dda035"

# Run master validation script
bash work-space/plans/GRAPHRAG-OBSERVABILITY-VALIDATION/observability/validate-all-achievements.sh
```

**Expected Output**:

- Summary of all 11 achievements
- Pass/Fail/Skip status for each
- Overall success rate
- Detailed results

**Duration**: ~5-10 minutes (depending on system)

---

### Option 2: Run Individual Achievement Tests

#### Infrastructure Tests (Phase 1)

```bash
# Achievement 1.1: Observability Stack
bash observability/04-e2e-test.sh

# Achievement 1.2: Metrics Endpoint
bash observability/09-validate-metrics.sh

# Achievement 1.3: Grafana Dashboards
bash work-space/plans/GRAPHRAG-OBSERVABILITY-VALIDATION/observability/test-achievement-1.3-dashboards.sh
```

#### Pipeline Tests (Phase 2)

```bash
# Achievement 2.1: Baseline Pipeline
export MONGODB_URI="..."
export DB_NAME="validation_01"
bash work-space/plans/GRAPHRAG-OBSERVABILITY-VALIDATION/observability/test-achievement-2.1-baseline.sh

# Achievement 2.2: Observability Pipeline
export MONGODB_URI="..."
export DB_NAME="validation_01"
export TRACE_ID="6088e6bd-e305-42d8-9210-e2d3f1dda035"
bash work-space/plans/GRAPHRAG-OBSERVABILITY-VALIDATION/observability/test-achievement-2.2-observability.sh
```

#### Validation Tests (Phase 3)

```bash
# Achievement 3.1: Query Scripts
export MONGODB_URI="..."
export DB_NAME="validation_01"
bash work-space/plans/GRAPHRAG-OBSERVABILITY-VALIDATION/observability/test-all-query-scripts.sh

# Achievement 3.2: Explanation Tools
export MONGODB_URI="..."
export DB_NAME="validation_01"
bash work-space/plans/GRAPHRAG-OBSERVABILITY-VALIDATION/observability/test-all-explanation-tools.sh
```

---

## 📊 Test Coverage by Achievement

### Achievement 1.3: Grafana Dashboards (16 tests)

**Phase 1: Service Health** (3 tests)

- Grafana container running
- HTTP endpoint accessible
- API health check

**Phase 2: Data Sources** (4 tests)

- Prometheus configured
- Loki configured
- Prometheus healthy
- Loki healthy

**Phase 3: Dashboard Provisioning** (3 tests)

- JSON file exists
- Provisioning config exists
- Dashboard accessible via API

**Phase 4: Structure Validation** (4 tests)

- Has title field
- Has panels
- Has datasource references
- Valid JSON syntax

**Phase 5: Panel Functionality** (2 tests)

- Sample Prometheus query works
- GraphRAG metrics query works

---

### Achievement 2.1: Baseline Pipeline (16 tests)

**Phase 1: Database Connectivity** (2 tests)

- MongoDB connection
- Database exists

**Phase 2: Legacy Collections** (4 tests)

- Entities collection exists
- Relations collection exists
- Communities collection exists
- Video chunks collection exists

**Phase 3: Data Presence** (3 tests)

- Entities populated
- Relations populated
- Communities populated

**Phase 4: Data Quality** (3 tests)

- Entities have entity_id
- Relations have source
- Communities have community_id

**Phase 5: Observability Disabled** (2 tests)

- No transformation_logs
- No entities_raw

**Phase 6: Performance Metrics** (2 tests)

- Entity count reasonable (> 100)
- Relation count reasonable (> 50)

---

### Achievement 2.2: Observability Pipeline (28 tests)

**Phase 1: Connectivity** (1 test)

- MongoDB connection

**Phase 2: Collections** (6 tests)

- All 6 observability collections exist

**Phase 3: Population** (6 tests)

- All collections populated with correct counts

**Phase 4: Trace ID Consistency** (2 tests)

- Single trace_id across collections
- Trace ID matches expected

**Phase 5: Schema Validation** (5 tests)

- All required fields present in each collection

**Phase 6: Data Quality** (3 tests)

- Confidence scores valid
- Timestamps present
- Entity linkage complete

**Phase 7: Legacy Collections** (3 tests)

- Legacy collections still exist

**Phase 8: Metrics Summary** (2 tests)

- Total document counts
- Quality metrics calculated

---

## 🔧 Prerequisites

### Required Environment Variables

```bash
# MongoDB connection (REQUIRED for all pipeline tests)
export MONGODB_URI="mongodb+srv://user:password@cluster.mongodb.net/database"

# Database name (REQUIRED for all pipeline tests)
export DB_NAME="validation_01"

# Trace ID (REQUIRED for Achievement 2.2, 3.1, 3.2)
export TRACE_ID="6088e6bd-e305-42d8-9210-e2d3f1dda035"
```

### Required Services

- **Docker** running (for Achievements 1.1, 1.2, 1.3)
- **Observability Stack** running (Prometheus, Grafana, Loki, Promtail)
- **MongoDB** accessible (for Achievements 2.1, 2.2, 3.1, 3.2)
- **Python 3.8+** with dependencies installed

### Required Data

- **Baseline pipeline run** completed (Achievement 2.1)
- **Observability pipeline run** completed (Achievement 2.2)
- **Trace ID** from Achievement 2.2 run

---

## 📝 Test Output Format

All test scripts follow a consistent output format:

```
╔═══════════════════════════════════════════════════════════╗
║  Achievement X.Y: [Achievement Name] Validation Test     ║
╚═══════════════════════════════════════════════════════════╝

════════════════════════════════════════════════════════════
Phase N: [Phase Name]
════════════════════════════════════════════════════════════

[TEST N] Test description
✅ PASS: Test description
  OR
❌ FAIL: Test description

════════════════════════════════════════════════════════════
Test Summary
════════════════════════════════════════════════════════════

Total Tests: N
Passed: N
Failed: N

╔═════════════════════════════════════════════╗
║  ✅ ALL TESTS PASSED                      ║
╚═════════════════════════════════════════════╝
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. MongoDB Connection Failures

**Symptom**: `ERROR: MONGODB_URI environment variable not set`

**Solution**:

```bash
export MONGODB_URI="mongodb+srv://user:pass@cluster.mongodb.net/database"
```

#### 2. Docker Services Not Running

**Symptom**: `Grafana container is not running`

**Solution**:

```bash
docker-compose -f docker-compose.observability.yml up -d
docker ps  # Verify all services running
```

#### 3. Missing Trace ID

**Symptom**: `No documents found for trace_id`

**Solution**:

- Verify Achievement 2.2 completed successfully
- Check trace_id in MongoDB:
  ```bash
  mongosh "$MONGODB_URI" --eval "db.transformation_logs.distinct('trace_id')"
  ```
- Export correct trace_id:
  ```bash
  export TRACE_ID="<actual-trace-id>"
  ```

#### 4. Permission Denied

**Symptom**: `Permission denied` when running scripts

**Solution**:

```bash
chmod +x work-space/plans/GRAPHRAG-OBSERVABILITY-VALIDATION/observability/*.sh
```

---

## 📈 Success Criteria

### Per-Achievement Success

Each achievement test must:

- ✅ Pass all critical tests (no failures in core functionality)
- ✅ Have < 10% test failures (if any non-critical tests fail)
- ✅ Complete within expected time (< 5 minutes per achievement)

### Overall Success

Master validation script succeeds when:

- ✅ All testable achievements pass (0 failures)
- ✅ Success rate = 100% (excluding skipped achievements)
- ✅ No critical infrastructure failures

---

## 🎯 Test Maintenance

### Adding New Tests

1. Create new test script: `test-achievement-X.Y-name.sh`
2. Follow existing script structure (phases, test functions, colors)
3. Make executable: `chmod +x test-achievement-X.Y-name.sh`
4. Add to `validate-all-achievements.sh`
5. Update this documentation

### Updating Existing Tests

1. Identify test script to update
2. Add new test cases to appropriate phase
3. Update test counters
4. Test locally before committing
5. Update documentation if test count changes

---

## 📚 Related Documentation

- **Achievement Execution Tasks**: `work-space/plans/GRAPHRAG-OBSERVABILITY-VALIDATION/execution/EXECUTION_TASK_*.md`
- **Test Scripts README**: `TEST-SCRIPTS-README.md` (Achievement 3.1 & 3.2 specific)
- **Validation Reports**: `documentation/*-Validation-Report.md`
- **Observability Guides**: `observability/*.md`

---

## ✅ Validation Status

| Phase                       | Achievements | Test Scripts        | Status      |
| --------------------------- | ------------ | ------------------- | ----------- |
| **Phase 0: Foundation**     | 0.1-0.3      | N/A (config tasks)  | ✅ Complete |
| **Phase 1: Infrastructure** | 1.1-1.3      | 3 scripts, 28 tests | ✅ Complete |
| **Phase 2: Pipeline**       | 2.1-2.3      | 2 scripts, 44 tests | ✅ Complete |
| **Phase 3: Validation**     | 3.1-3.2      | 2 scripts, 14 tests | ✅ Complete |

**Total**: 8 test scripts, 86 automated tests, 100% coverage of testable achievements

---

## 🎉 Summary

All achievements in the GRAPHRAG Observability Validation plan now have comprehensive automated test coverage. The master validation script (`validate-all-achievements.sh`) provides one-command validation of the entire observability infrastructure.

**Run the master script to validate everything**:

```bash
export MONGODB_URI="..."
export DB_NAME="validation_01"
export TRACE_ID="6088e6bd-e305-42d8-9210-e2d3f1dda035"

bash work-space/plans/GRAPHRAG-OBSERVABILITY-VALIDATION/observability/validate-all-achievements.sh
```

**Expected Result**: ✅ All testable achievements pass, observability infrastructure production-ready.
