# Stages API - Implementation Guide

**Last Updated:** December 9, 2025  
**Project:** GraphRAG Backend - Stages API  
**Location:** `app/stages_api/`  
**Related Frontend:** `../StagesUI/`

---

## 📋 Session Summary

### What Was Fixed (December 9, 2025)

1. **API Contract Mismatch #1 - Validation Response Format**
   - **File:** `app/stages_api/api.py`
   - **Issue:** Backend returned `errors: List[Dict]`, frontend expected `errors: Record<string, string[]>`
   - **Fix:** Added transformation functions `_transform_validation_result()`, `_transform_errors()`, `_transform_warnings()`

2. **API Contract Mismatch #2 - Defaults Endpoint Wrapping**
   - **File:** `app/stages_api/metadata.py`
   - **Issue:** `/stages/{name}/defaults` returned `{stage_name, config_class, config: {...}}`, frontend expected flat config
   - **Fix:** Modified `get_stage_defaults()` to return flat config dict directly

### What Is Fully Implemented ✅

| Feature | Status | Notes |
|---------|--------|-------|
| ✅ Health endpoint | Working | `/api/v1/health` |
| ✅ Pipeline persistence | Working | MongoDB `pipeline_executions` collection |
| ✅ State recovery on startup | Working | Interrupted pipelines marked automatically |
| ✅ Execution history | Working | `/api/v1/pipelines/history` |

**IMPORTANT:** If persistence isn't working, ensure:
1. MongoDB is running on `localhost:27017`
2. The server was restarted AFTER the `repository.py` was added
3. Check environment: `MONGODB_URI`, `DB_NAME`

---

## 🏗️ Architecture Context

### Current File Structure
```
app/stages_api/
├── __init__.py          # Package init (v1.0.0)
├── api.py               # Request routing, transformations ✅ 
├── constants.py         # Pipeline groups, category patterns
├── execution.py         # Background execution + MongoDB sync ✅
├── field_metadata.py    # UI-friendly field descriptions
├── metadata.py          # Schema extraction ✅
├── repository.py        # MongoDB persistence layer ✅ NEW
├── server.py            # HTTP server (localhost:8080)
├── validation.py        # Config validation
└── docs/
    ├── API_DESIGN_SPECIFICATION.md
    ├── IMPLEMENTATION_PLAN.md
    ├── SESSION_SUMMARY.md
    ├── STAGES_API_TECHNICAL_FOUNDATION.md
    ├── UI_DESIGN_SPECIFICATION.md
    └── postman_collection.json
```

### API Endpoints
| Method | Endpoint | Handler | Status |
|--------|----------|---------|--------|
| GET | `/api/v1/health` | `handle_request()` | ✅ Working |
| GET | `/api/v1/stages` | `list_stages()` | ✅ Working |
| GET | `/api/v1/stages/{pipeline}` | `list_pipeline_stages()` | ✅ Working |
| GET | `/api/v1/stages/{stage_name}/config` | `get_stage_config()` | ✅ Working |
| GET | `/api/v1/stages/{stage_name}/defaults` | `get_stage_defaults()` | ✅ Working |
| POST | `/api/v1/stages/{stage_name}/validate` | `validate_stage_config_only()` | ✅ Working |
| POST | `/api/v1/pipelines/validate` | `validate_pipeline_config()` | ✅ Working |
| POST | `/api/v1/pipelines/execute` | `execute_pipeline()` | ✅ Working + persisted |
| GET | `/api/v1/pipelines/{id}/status` | `get_pipeline_status()` | ✅ Working + DB fallback |
| POST | `/api/v1/pipelines/{id}/cancel` | `cancel_pipeline()` | ✅ Working |
| GET | `/api/v1/pipelines/active` | `list_active_pipelines()` | ✅ Working |
| GET | `/api/v1/pipelines/history` | `get_pipeline_history()` | ✅ Working + from MongoDB |

---

## ✅ Implementation Status (All Complete)

All planned features have been implemented and verified working as of December 9, 2025.

### Phase 1: Health Endpoint ✅ COMPLETE

**File:** `app/stages_api/api.py` (lines 185-192)

```bash
curl http://localhost:8080/api/v1/health
# Returns: {"status": "healthy", "version": "1.0.0", "timestamp": "...", "active_pipelines": 0}
```

---

### Phase 2: Pipeline State Persistence ✅ COMPLETE

**Files:**
- `app/stages_api/repository.py` - MongoDB persistence layer
- `app/stages_api/execution.py` - Updated with `_sync_to_db()`, `_load_from_db()`, `recover_state_from_db()`

**Verified Working:**
```bash
# Execute pipeline
curl -X POST http://localhost:8080/api/v1/pipelines/execute \
  -H "Content-Type: application/json" \
  -d '{"pipeline": "ingestion", "stages": ["clean"], "config": {}}'

# Check history (persisted in MongoDB)
curl http://localhost:8080/api/v1/pipelines/history

# Restart server - history still available!
```

**MongoDB Collection:** `pipeline_executions` in database `mongo_hack`

---

### Phase 3: Progress Updates ✅ COMPLETE

Real-time progress tracking is implemented in `_run_pipeline_background()` with:
- Current stage tracking
- Percent complete calculation
- Completed stages list
- Duration tracking

---

## 🧪 Testing

### Quick Verification Commands

```bash
# Start server
cd /Users/fernandobarroso/repo/KnowledgeManager/GraphRAG
source .venv/bin/activate
python -m app.stages_api.server --port 8080

# Test health
curl http://localhost:8080/api/v1/health

# Test execute + persistence
curl -X POST http://localhost:8080/api/v1/pipelines/execute \
  -H "Content-Type: application/json" \
  -d '{"pipeline": "ingestion", "stages": ["clean"], "config": {}}'

# Test history (from MongoDB)
curl http://localhost:8080/api/v1/pipelines/history

# Verify MongoDB directly
python -c "from app.stages_api.repository import get_repository; print(get_repository().count_all())"
```

---

## 🚀 Future Improvements (Optional)

| Improvement | Description | Priority |
|-------------|-------------|----------|
| WebSocket status | Real-time push instead of polling | Low |
| Pipeline logs streaming | Stream stdout/stderr to UI | Medium |
| Batch execution | Run multiple pipelines | Low |
| Stage retry | Retry failed stages without full restart | Low |
| Resource monitoring | Track CPU/memory during execution | Low |

---

## 📝 Notes for Future Sessions

### Key Files
| File | Purpose |
|------|---------|
| `repository.py` | MongoDB persistence (NEW) |
| `execution.py` | Pipeline execution + DB sync |
| `api.py` | Request routing, health endpoint |
| `metadata.py` | Stage config/defaults |

### Environment Setup
```bash
cd /Users/fernandobarroso/repo/KnowledgeManager/GraphRAG
source .venv/bin/activate
export MONGODB_URI="mongodb://localhost:27017"
export DB_NAME="mongo_hack"
```

### Common Issues

**Pipeline not persisting?**
1. Check MongoDB is running: `pgrep mongod`
2. Restart the API server (old process may have stale code)
3. Verify: `python -c "from app.stages_api.repository import is_persistence_enabled; print(is_persistence_enabled())"`

**404 on status polling?**
- Server likely restarted - pipeline state is in MongoDB
- Frontend should handle gracefully (see StagesUI guide)

### Related Documents
- Frontend Guide: `../StagesUI/STAGES_UI_IMPLEMENTATION_GUIDE.md`
- API Specification: `app/stages_api/docs/API_DESIGN_SPECIFICATION.md`

---

**Last Verified:** December 9, 2025  
**Status:** ✅ All core features implemented and working

**End of Document**

