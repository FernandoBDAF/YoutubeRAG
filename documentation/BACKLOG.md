# Backlog

## ✅ Completed (Recent)

- GraphRAG Pipeline Fixes: Fixed critical bugs in `setup()`, `get_pipeline_status()`, and `cleanup_failed_stages()` methods
- Testing Strategy: Created comprehensive `documentation/TESTING.md` with detailed testing plans for all components
- Pipeline Unification: Unified on `PipelineRunner` pattern for consistent stage orchestration
- Code Cleanup: Removed unused functions and added TODO comments for future enhancements
- Development Focus: Removed premature production files (`deploy_graphrag.py`, `graphrag_production.py`) - focus on core functionality and testing first
- Deployment Strategy: Created comprehensive `documentation/DEPLOYMENT.md` with future implementation plan
- Testing Focus: Removed premature `test_graphrag_comprehensive.py` - extracted valuable patterns to `TESTING.md` for future implementation

## Clean stage

- Heuristic cleaner when LLM returns empty (strip cues, spacing, minimal detokenization)
- Optional speaker label stripping flag
- Tune CLEAN_CONCURRENCY, LLM_RETRIES, LLM_BACKOFF_S defaults; add jitter

## Enrich refinements

- Consider per-topic throttling and tag taxonomy mapping
- Add entity typing (PERSON/ORG/CONCEPT) or separate fields
- Lightweight cross-segment dedup/merge of near-identical segments

## Retrieval/Ranking

- Integrate feedback-based reranking weights deeper into segment scoring
- Add per-segment trust heuristics as fallback signals (if trust stage missing)
- Optionally penalize very high redundancy_score in retrieval, gated by env
- Auto‑apply persona weights to Q&A sliders on profile load (non-destructive)

## UI polish

- Toggle for showing/hiding stage cues
- Download cleaned/enriched transcripts as markdown/CSV
- Help tooltips across all tabs (post Q&A): Hybrid, Explore, Retrieval Lab, Compare, Unique, Summaries, Memory, Controller, Persona & Session
- Sidebar quick “Save preset” for profiles (optional)
- Pre-commit hook with ruff/black/autoflake (format changed files only)

## Pipelines & Infra

- Apply concurrency to trust.py, redundancy.py, and remaining parts of chunk_embed
- Add global QPS limiter and per-provider retry policies in core/concurrency
- Atlas Search index management: scripted filter updates and readiness checks per environment
- Implement retry logic in PipelineRunner (see TODO comments in GraphRAG pipeline)
- Implement comprehensive statistics aggregation for pipeline monitoring

## Testing Implementation (High Priority)

- Set up pytest configuration and test infrastructure
- Implement unit tests for core components (BaseStage, BaseAgent, BasePipeline)
- Create integration tests for MongoDB operations and API interactions
- Build end-to-end tests for complete pipeline workflows
- Implement performance and load testing
- Set up CI/CD pipeline with automated testing
- Create test data generators and mock services

## Trust (post-demo)

- Incorporate channel/video metrics in trust heuristic aggregation
- Add heuristic trigger: call LLM if heuristic trust is in a low band (e.g., 0.20–0.35)
- Document examples of trust interpretation in docs and UI tooltips
