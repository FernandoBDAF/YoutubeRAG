# GraphRAG Extraction + Ontology Review — Feedback & Fixes

You are a senior SWE reviewing a GraphRAG extraction pipeline that now adds ontology-based predicate canonicalization and filtering.

## Context (what exists now)

- **Loader**: `core/libraries/ontology/loader.py`  
  - Loads: `ontology/canonical_predicates.yml`, `ontology/predicate_map.yml`, and `ontology/types.yml` (or `entity_types.yml`)
  - Provides: `canonical_predicates`, `symmetric_predicates`, `predicate_map`, `predicate_type_constraints`, `type_map`
- **Agent**: `business/agents/graphrag/extraction.py`  
  - Uses loader; normalizes predicates; canonicalizes + validates type-pairs; normalizes symmetric edges.
  - New `_normalize_predicate_string` should avoid bad stems like `us`, `ha`, `appli_*`.
- **Stage**: `business/stages/graphrag/extraction.py`  
  - Writes results to DB; logs `updated/failed/skipped`; supports concurrency.

## What I want you to do

### 1) Sanity check filenames, imports, and path assumptions
- Confirm these files exist and imports match:
  - `core/libraries/ontology/loader.py`
  - `business/agents/graphrag/extraction.py`
  - `business/stages/graphrag/extraction.py`
- Verify the loader’s repo-root resolution (parents of `loader.py`) correctly finds the `ontology/` directory at the project root. If not, fix with a robust base-dir resolver.
- Ensure `requirements` include **Unidecode** and **PyYAML** (and they’re imported where used).

### 2) Predicate normalization quality
- Inspect `_normalize_predicate_string`:
  - Confirm token-wise stemming and guards are implemented so:
    - `uses` → `use` (not `us`)
    - `applies_to` → `apply_to`
    - `teaches` → `teach`
    - `has` stays `has`
    - `classes` remains `classes` (no over-stemming)
- If this isn’t true, **patch the function** (show a diff) and add a unit test with these exact cases.

### 3) Canonicalization + filtering behavior
- In `_canonicalize_predicate`:
  - Confirm the order: normalize → check `predicate_map.yml` (`__DROP__` respected) → allow if already canonical → else drop (or soft-keep if an env flag like `GRAPHRAG_KEEP_UNKNOWN_PREDICATES=true` is on).
- If the “soft-keep unknown” env flag isn’t implemented, add it behind `GRAPHRAG_KEEP_UNKNOWN_PREDICATES` (default: false).  
  - When enabled, keep unknown **if** confidence ≥ 0.85 **and** predicate length ≥ 4.

### 4) Type-pair constraints
- Verify `predicate_type_constraints` is consulted.  
  - If a canonical predicate has constraints and the (src_type, tgt_type) pair is not allowed, the relationship is dropped with a clear debug log.  
  - Add a quick unit test that demonstrates a violation being correctly filtered.

### 5) Symmetric predicates normalization
- Confirm that for `symmetric_predicates`, endpoints are sorted lexicographically by **lowercased names** and the relation is preserved.  
- Add a unit test: the same (A,B) and (B,A) normalize to one canonical direction.

### 6) Stage logging and counters
- Ensure `process_batch` logs **`updated/failed/skipped`** from `self.stats` (not counting `None` returns).  
- Confirm error paths increment `failed` and successes increment `updated`.

### 7) YAML contract checks
- Loader should accept **both** `types.yml` and `entity_types.yml`. If only one is supported, add the other as a fallback.
- Validate YAML structures at load time:
  - `canonical_predicates`: List[str]
  - `symmetric_predicates`: List[str]
  - `predicate_map`: Dict[str, str]
  - `predicate_type_constraints`: Dict[str, List[List[str]]] with each inner list length == 2
- If invalid, log a warning and continue (backward compatible), but surface a summary of which sections were unusable.

### 8) Smoke tests (add minimal tests)
Create a tiny test module (or script) with:
- Loader smoke test: asserts sets/dicts exist; prints counts.
- Normalization test: the five examples above.
- Canonicalization test:  
  - A predicate in predicate_map → mapped to canonical  
  - `__DROP__` case → returns `None`  
  - Known canonical → retained
- Symmetric test: (A,B) and (B,A) coalesce.
- Type constraint test: one allowed, one rejected.

### 9) One-chunk dry-run
- Run extraction on a **single known chunk** (the MIT OCW sample) and print:
  - total entities, total relationships
  - top 10 predicates by frequency in that chunk
  - confirm **no** `us`, `ha`, `appli_*` predicates remain
- If any leak remains, fix normalization or update `predicate_map.yml`.

## Output format I expect from you

1. **Summary** (1–2 paragraphs): What you checked and overall status.  
2. **Findings**: Bullet list grouped by sections 1–9 above, each with ✅/⚠️/❌.  
3. **Patches**: Unified diffs for any necessary code changes.  
4. **Tests**: New/updated test files (or test snippets) with instructions to run.  
5. **Follow-ups**: Any improvements to add after initial validation (e.g., caching metrics, auto-rebuilding predicate maps, adding telemetry).

## Acceptance criteria

- No corrupted stems (`us`, `ha`, `appli_*`) in normalized predicates.
- Unknown predicates are either dropped or guarded by the env-flag behavior.
- Type-pair constraints enforced where provided.
- Symmetric predicates produce a single normalized edge form.
- Stage logs accurate updated/failed/skipped counts.
- Loader tolerates missing/invalid YAML gracefully and reports what was used.
- A single-chunk dry-run shows clean canonical predicates only.

**Now perform the review and produce the requested output. If changes are needed, include diffs and tests.**
