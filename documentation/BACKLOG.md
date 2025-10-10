# Backlog

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

## Trust (post-demo)

- Incorporate channel/video metrics in trust heuristic aggregation
- Add heuristic trigger: call LLM if heuristic trust is in a low band (e.g., 0.20–0.35)
- Document examples of trust interpretation in docs and UI tooltips
