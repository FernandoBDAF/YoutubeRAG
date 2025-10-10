## Redundancy in Vector RAG: A Practical Guide

This doc explains, from first principles, what our redundancy stage does, why it matters, and the design choices we ship for a pragmatic demo setup.

### What is redundancy?

When we split long transcripts into chunks and embed them, adjacent chunks often overlap so retrieval stays coherent. Because of this overlap, many chunks are nearly identical. Redundancy detection identifies chunks that do not add new information and can be safely down‑weighted or filtered.

### How we detect redundancy

- We compute cosine similarity between a chunk and its nearest neighbors (same video first; can be extended cross‑video).
- If the best similarity is above a threshold (default 0.92), we flag the chunk as redundant and record:
  - `is_redundant: true`
  - `duplicate_of`: the canonical chunk id we keep
  - `redundancy_score`: the cosine similarity
  - `redundancy_method`: "cosine" or "llm"
  - `redundancy_reason`: "high_sim" or "borderline"

### Why thresholding works

Cosine similarity between good embeddings correlates with semantic sameness. For overlapping text windows, scores ≥0.92 typically indicate the second window largely repeats the first.

### Borderline LLM check

Some pairs hover near the threshold. We optionally call an LLM only for borderline cases to avoid cost while improving judgment:

- Env: `DEDUP_WITH_LLM=1` and `DEDUP_LLM_MARGIN=0.03`
- Trigger condition: `abs(best_score - DEDUP_THRESHOLD) <= DEDUP_LLM_MARGIN`
- If LLM says “redundant”, we keep the flag; otherwise we let it pass.

### Canonicalization (why A↔B becomes one primary)

Cosine alone can make pairs point to each other (A→B and B→A). We select a single canonical primary (lexicographically smallest `chunk_id`) and set all others to `duplicate_of` that primary. This stabilizes downstream analytics and UI.

### Adjacency guard (overlap noise)

Adjacent chunks share the largest overlap and frequently exceed the threshold, which produces long “chains”. To reduce noise, we can skip flagging duplicates when the best match is an immediate neighbor.

- Env: `DEDUP_SKIP_ADJACENT=true`
- Rule: If best match is the immediate neighbor in the same video (e.g., `:0007` vs `:0008`), do not mark as redundant.
- Non-adjacent fallback (optional): `DEDUP_NONADJ_FALLBACK=true` will pick the best non-adjacent candidate above threshold so we still catch real repeats a few chunks away.
- High-confidence override: if the adjacent score is extremely high (≥ `DEDUP_ADJ_OVERRIDE`, default 0.975), we will still mark it as redundant.

### Display text vs embedding text

We strip stage cues like `[APPLAUSE]` before embedding to improve vector quality. For UI friendliness, we also persist a `display_text` version without cues so what users see aligns with what we embed.

### Tradeoffs

- Precision vs recall: Higher threshold (e.g., 0.94–0.96) reduces false positives at the cost of a few true positives.
- Stability vs freshness: Canonicalization stabilizes identities across runs; if you change chunking, mappings may shift.
- Cost vs quality: Borderline LLM checks improve decisions but add latency/cost; margin keeps it bounded.
- Cohesion vs duplication: Overlap improves readability in RAG but creates more near‑duplicates; adjacency guard mitigates noise.

### Configuration

- `DEDUP_THRESHOLD` (default 0.92): cosine cutoff
- `DEDUP_LLM_MARGIN` (default 0.03): band around threshold for LLM checks
- `DEDUP_WITH_LLM` (0/1): enable LLM
- `DEDUP_SKIP_ADJACENT` (true/false): skip immediate-neighbor duplicates
- `DEDUP_NONADJ_FALLBACK` (true/false): prefer best non-adjacent when best is adjacent
- `DEDUP_ADJ_OVERRIDE` (float): if adjacent score ≥ this value, override the guard

### Example (from sample output)

- `0001` and `0002` with score 0.9687 → redundant; canonical is the lower `chunk_id`.
- Chains like `0003→0002`, `0004→0003` are typical from overlap; adjacency guard reduces this.

## Trust scoring (how it relates)

Trust aims to estimate how reliable a chunk is. The heuristic combines simple signals:

- Consensus: similarity to peers (redundancy_score/nearby chunks)
- Recency: `age_days` from published date
- Engagement: basic channel/video metrics (views/likes) if available
- Code presence: whether the segment includes code examples

In our demo, the default heuristic is intentionally simple and produces similar values across chunks of the same video when metadata is sparse. The LLM can be used to refine trust on demand:

- `TRUST_WITH_LLM=1` forces the LLM to score
- Or `TRUST_LLM_AUTO=true` triggers the LLM only in ambiguous cases, e.g. redundancy_score in a configured band, `code_present=true`, or very recent content (`age_days<30`). See env flags in `env.example`.

Relationship to redundancy:

- Redundancy detects near-duplicates; trust can down-weight highly redundant material when it adds little new value.
- In our setup, we DO NOT automatically lower trust when redundancy is high; instead, we allow the retrieval/ranking layer to use both signals (vector score + trust + recency). This keeps the pipeline simple and the demo predictable.
