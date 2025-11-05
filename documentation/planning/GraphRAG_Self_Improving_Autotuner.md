# GraphRAG Self‑Improving Extraction & Ontology Autotuner
_Fernando-first edition • Nov 2025_

This document specifies a **self‑improving pipeline** that (1) **diagnoses** extraction/graph quality for a given set of sources (e.g., YouTube channels, PDF corpora), (2) **proposes & applies configuration changes** via YAML ontologies and stage configs, and (3) **iterates** until a target quality standard is achieved (or **drops** a source with poor data quality). It extends your existing GraphRAG setup (extraction → entity_resolution → graph_construction → community_detection) and the **Diagnostics Pack** you’ve built.

---

## 0) TL;DR — What this adds
- **Autotuner loop**: Diagnose → Propose → Apply → Re‑run → Evaluate → Stop/Rollback  
- **Ontology generators** that synthesize/patch: `canonical_predicates.yml`, `predicate_map.yml`, `types.yml`, and **new** `constraints.yml`, `stage_config.yml`, `quality_targets.yml`.
- **Action library** that converts metric deltas into **concrete changes** (thresholds, mappings, caps, symmetric predicates, link strategies).
- **Guardrails**: change budgets, canary mode, rollback, audit logs, reproducibility.

---

## 1) High‑level architecture

```
+-----------------------+        +---------------------------+
|  Source Selector      |        |  Quality Targets (YAML)   |
|  (videos, pdf sets)   |        |  quality_targets.yml      |
+-----------+-----------+        +------------+--------------+
            |                                 |
            v                                 v
+-----------------------+        +---------------------------+
|  Working Pipeline     |        |  Diagnostics Pack         |
|  (your 4 stages)      |        |  (metrics & reports)      |
|  Configurable via     |        +------------+--------------+
|  *-config YAMLs       |                     |
+-----------+-----------+                     v
            |                       +--------------------------+
            v                       |  Autotuner Orchestrator |
+-----------------------+           |  (policy + optimizer)    |
|  Snapshot Results     |-----------+--+-----------------------+
|  (DB + metrics blob)  |              |
+-----------+-----------+              v
            |                 +-------------------------------+
            |                 |  Action Library               |
            |                 |  (YAML Generators & Patches)  |
            |                 +-------------------------------+
            |                         |
            v                         v
      (Stop / Iterate)        New/Patched YAMLs → Pipeline Reload
```

---

## 2) YAMLs — schemas & responsibilities

### 2.1 `ontology/canonical_predicates.yml`
- **Purpose**: whitelist, symmetric, and **type-pair constraints**.
- **Schema (excerpt)**
```yaml
canonical_predicates:
  - related_to
  - uses
  - is_a
  # ... curated 40–120 items

symmetric_predicates:
  - similar_to
  - related_to
  - collaborates_with

predicate_type_constraints:
  uses:
    - [TECHNOLOGY, TECHNOLOGY]
    - [ALGORITHM, DATASTRUCTURE]
    - [PERSON, TECHNOLOGY]
  works_at:
    - [PERSON, ORGANIZATION]
  located_in:
    - [ORGANIZATION, LOCATION]
    - [EVENT, LOCATION]

stats:  # optional, for reference
  uses: {count: 3660, avg_conf: 0.83}
```

### 2.2 `ontology/predicate_map.yml`
- **Purpose**: string‑variant → canonical (or `__DROP__`).
- **Schema (excerpt)**
```yaml
# normalized_variant: canonical
utiliz: uses
applies_to: uses
requir: requires
compar: compared_to
ha: has_property
is_a_type_of: is_a

# noisy / generic verbs → drop
mention: __DROP__
discuss: __DROP__
cover: __DROP__
present: __DROP__
```
> _Tip_: keep “presentation verbs” out of the graph; they swamp semantics.

### 2.3 `ontology/types.yml`
- **Purpose**: canonical types and merge map.
- **Schema (excerpt)**
```yaml
canonical_types: [
  "PERSON","ORGANIZATION","CONCEPT","METHOD","TECHNOLOGY","PROCESS","TASK",
  "THEORY","LAW","FORMULA","EXPERIMENT","DATASTRUCTURE","ALGORITHM","MODEL",
  "METRIC","COURSE","EVENT","LOCATION","MATERIAL","OTHER"
]

type_map:  # observed → canonical
  Class: COURSE
  Cpu: TECHNOLOGY
  Watch Calculator: TECHNOLOGY
  Mathematical Function: CONCEPT
  Functional Programming: METHOD
```

### 2.4 `ontology/constraints.yml`  **(new)**
- **Purpose**: **global policy** constraints beyond per‑predicate pairs.
```yaml
entity:
  min_confidence: 0.30
  min_length_chars: 2
  max_aliases: 10

relationship:
  min_confidence: 0.30
  max_predicates_per_pair: 3
  allow_symmetric_dedup: true
  allow_bidirectional_mirroring: false

graph:
  max_density: 0.25
  cap_out_degree_p95: 60
  drop_predicates: ["mention","discuss","cover","present"]
```

### 2.5 `configs/stage_config.yml`  **(new)**
- **Purpose**: knobs for **extraction & construction** (hot‑reloaded).
```yaml
extraction:
  llm_model: gpt-4o-mini
  temperature: 0.05
  max_tokens: 3500

  # soft hints to LLM
  preferred_predicates: ["uses","is_a","part_of","depends_on","implemented_in"]
  disallowed_predicates: ["mention","discuss","present","cover"]

  entity_filters:
    min_confidence: 0.30
    drop_types: ["OTHER"]  # optional, can be empty

  relationship_filters:
    min_confidence: 0.30
    keep_only_canonical: true

entity_resolution:
  canonicalize_case: true
  fuzzy_threshold: 0.92
  merge_by_aliases: true

graph_construction:
  edge_weighting:
    rule: "confidence_xidf"  # see §4.3
    lambda: 0.7
  link_strategies:
    cooccurrence:
      enabled: true
      window: "chunk"
      max_per_node: 5
    semantic_similarity:
      enabled: true
      model: "voyage-2"
      threshold: 0.92
      max_neighbors: 10
    cross_chunk:
      enabled: true
      policy: "same_video"
    bidirectional:
      enabled: true
      only_for: ["similar_to","is_equivalent_to"]
    link_prediction:
      enabled: false

community_detection:
  algorithm: "louvain"    # fallback if hierarchical-leiden underperforms
  resolution: 1.0
  min_cluster_size: 5
  max_levels: 3
```

### 2.6 `configs/quality_targets.yml`  **(new)**
- **Purpose**: stop/continue logic.
```yaml
targets:
  # Extraction
  entity_precision_proxy: {min: 0.80}      # from heuristic evals (§3.2)
  rel_canonical_coverage: {min: 0.85}      # % rels in canonical set
  dropped_ratio: {max: 0.35}               # % rels dropped by ontology
  type_purity_macro: {min: 0.80}           # purity @ entity type

  # Graph
  avg_degree: {min: 2.5, max: 18}
  giant_component_ratio: {min: 0.75}
  clustering_coef: {min: 0.05}
  degree_p95_cap_hits: {max: 0.10}

  # Community
  modularity: {min: 0.35}
  conductance_p50: {max: 0.55}
  label_coherence_llm: {min: 0.70}

stopping:
  consecutive_passes: 2
  max_iterations: 6
  canary_fraction: 0.1
  allow_rollback: true
  change_budget_per_iter:
    max_predicate_map_edits: 40
    max_constraint_additions: 20
    max_threshold_delta: 0.1
```

---

## 3) Diagnostics → Metrics (the “what to optimize”)

### 3.1 Extraction surface
- **Rel canonical coverage** = `#rels with canonical predicate / #rels total`
- **Drop ratio** = dropped by `predicate_map` or constraints
- **Predicate entropy** (balanced usage vs single‑verb dominance)
- **Type purity** per canonical type (from `types.yml`), macro‑averaged
- **Top noisy predicates** (by drop count & low confidence)
- **Span‑anchoring rate**: % entities with unambiguous spans (optional if you store spans)

### 3.2 Quality proxies using weak supervision
- **LLM sampling eval**: sample N extractions → score (0/1/0.5) for entity correctness, relation correctness, and type correctness. Calibrate a **precision proxy**.
- **Contrastive checks**: ask LLM to propose **counterfactual pairs** that should _not_ connect; measure spillover edges rejected by constraints.
- **Name collision rate**: same surface form across different canonical types.

### 3.3 Graph structure
- **Avg degree / degree p95**
- **Clustering coefficient**
- **Giant component ratio**
- **Edge weight distribution** (see §4.3) and **idf** skewness
- **Bridge edges** (edge betweenness p95) — watch for LLM hallucinated “hub” nodes.

### 3.4 Community quality
- **Modularity**, **conductance** (p50/p90)
- **LLM label coherence**: prompt to produce a 3–7‑word **community label** + score (0–1) given top‑k entity names and predicates.
- **Cross‑video purity**: share-of-community from a single source vs multi‑source (detect overfitting to one video).

---

## 4) Action Library (diagnosis → changes)

> Each iteration chooses a **small set of actions** (within **change budget**) that is predicted to improve metrics failing their targets.

### 4.1 Ontology actions
- **Map variants** with high freq & high confidence to canonical (edit `predicate_map.yml`).
- **Drop generic verbs** with poor type‑pair compatibility (→ `__DROP__`).  
  Examples in your stats: `mention`, `discuss`, `cover`, `present`, `featur`.
- **Add symmetric predicates** if observed bidirectional usage is high.
- **Tighten type-pair constraints** for promiscuous predicates (`related_to`, `associated_with`) to reduce noise.

### 4.2 Filters & thresholds
- Raise **rel min_confidence** from 0.3 → 0.4 if **drop ratio** is too high _and_ canonical coverage is low.
- Cap **max_predicates_per_pair** to 2–3 to prevent over‑production by the LLM prompt.
- Increase **fuzzy threshold** in entity resolution if **name collision rate** rises.

### 4.3 Edge weights & link strategies
- **Weights**: `w = confidence * idf(predicate)` or `confidence * log(1 + 1/freq(predicate))`  
  Helps suppress ubiquitous predicates like `related_to`.
- **Co-occurrence**: limit `max_per_node` and prefer **same_video** or **same_speaker** heuristic early on.
- **Semantic similarity**: raise `threshold` for high‑variance sources; lower for homogeneous courses.
- **Cap out-degree** at p95 via strongest weights; log cap hits.

### 4.4 Community algorithm switch
- If **hierarchical_leiden** yields singleton soup → switch to **Louvain** (your empirical win), keep **resolution sweeps** in `[0.8, 1.4]` and pick best modularity.
- Allow **max_levels=3**; collapse tiny communities `< min_cluster_size` into nearest neighbor by average edge weight.

### 4.5 Prompt shaping (minimal)
- Provide **preferred_predicates**/**disallowed_predicates** hints (see `stage_config.yml`), not hard constraints, to keep recall.

---

## 5) Autotuner Orchestrator

### 5.1 Loop policy (pseudo‑code)
```python
def autotune(sources, targets, max_iter=6):
    snap0 = run_pipeline(sources)                     # extraction → communities
    diag0 = diagnose(snap0)
    best = (score(diag0, targets), snap0, [])         # (score, snapshot, actions)

    for t in range(1, max_iter+1):
        actions = plan_actions(diag0, targets, budget=change_budget(t))
        if not actions: break

        patch_yaml(actions)                           # write YAML edits atomically
        snap_t = run_pipeline(sources, canary=targets.stopping.canary_fraction)
        diag_t = diagnose(snap_t)

        if passes(diag_t, targets, consecutive=targets.stopping.consecutive_passes):
            promote_canary_to_full()
            return {"status":"pass", "iterations":t, "actions":accumulated_actions()}

        score_t = score(diag_t, targets)
        if score_t > best[0]:
            best = (score_t, snap_t, accumulated_actions())

        if should_rollback(diag_t, prev=diag0):
            rollback_last_patch()
            break

        diag0 = diag_t

    return {"status":"fail", "best": best, "reason":"max_iter or poor data"}
```

### 5.2 Scoring & stopping
- **Score** = weighted sum of normalized gaps to targets; weight extraction > graph > community initially.
- **Stopping**: need `consecutive_passes` full passes (stability), and respect `change_budget_per_iter`.
- **Rollback**: if any metric regresses **> δ** (configurable), revert last patch (keep audit log).

---

## 6) CLI / API

### 6.1 Commands
```bash
# 1) Run once (no tuning)
python -m graphrag.autotune run \
  --sources yt:MIT_OCW,yt:3Blue1Brown,pdf:/data/papers \
  --configs configs/stage_config.yml \
  --ontology ontology \
  --out runs/2025-11-04__baseline

# 2) Autotune loop
python -m graphrag.autotune tune \
  --sources yt:MIT_OCW \
  --targets configs/quality_targets.yml \
  --max-iter 6 \
  --budget small \
  --log runs/2025-11-04__autotune
```

### 6.2 Outputs
- `runs/<stamp>/diagnostics.json` — all metrics
- `runs/<stamp>/actions.yml` — actions applied this iter
- `runs/<stamp>/patches/NNN-*.diff` — YAML diffs
- `runs/<stamp>/report.md` — human report (copyable to Notion)

---

## 7) Canary & rollout safety

- **Canary fraction** (e.g., 10% of sources/chunks) per iteration; full run only when targets pass.
- **Change budget** to avoid over‑fitting in one step.
- **Audit log** of patches with author = “autotuner” + git user.
- **Determinism**: pin LLM model, temperature, and set seed for any sampling.
- **Time/Cost guard**: upper bounds on tokens, batch sizes, and workers.

---

## 8) How to study data and craft better names/predicates

1) **Predicate cohorting**  
   - Group by canonical predicate → inspect top 200 edges by weight; compute **type‑pair histogram**.  
   - Flag predicates with **diffuse type pairs** → tighten constraints or split into more specific predicates.

2) **Community label mining**  
   - For each community, collect top‑k entities (by centrality) & top‑k predicates.  
   - Prompt LLM: _“Propose a 3–7 word label + confidence; list 3 defining predicates.”_  
   - Keep labels with confidence ≥ 0.7; store to `communities.title` and feed back as **hints** for resolution.

3) **N‑gram / keyphrase extraction** on entity descriptions & chunk text; merge into **alias lists** where appropriate.

4) **Outlier analysis**  
   - High‑degree nodes with generic names (e.g., “Class”, “Course”, “Algorithm”) → convert to **TYPE-only nodes** or drop from centrality calculations.  
   - Use **betweenness** to find suspicious bridges → sample and validate.

5) **Manual gold seeds**  
   - Maintain a tiny **seed sheet** of <100 gold edges and <100 gold entity types for your domain. Use as spot checks for precision tracking.

---

## 9) Advanced research directions

- **Edge‑type embedding**: encode `(src_type, predicate, tgt_type)` into a learned embedding; use **Mahalanobis** distance to detect atypical edges.
- **Edge weight learning**: shallow model on features: `confidence`, `idf(pred)`, `type_compat`, `text_overlap`, `cooccurrence`, `speaker_match` → learn a weight scalar against weak labels.
- **Consensus extraction**: run two extraction prompts (strict vs recall) and **intersect** relations (precision↑).
- **Active learning loop**: occasionally surface **uncertain** edges to a human micro‑UI for binary feedback; feed back into `predicate_map` and constraints.
- **Multi‑algo communities**: combine Louvain (macro) with **Leiden-refined** subgraphs on big clusters only (min-cut ≥ N), preserving hierarchy without singleton blow‑up.
- **Temporal graph**: add `published_at` into edges; penalize cross‑era links for “evolving tech” channels.

---

## 10) Minimal code hooks (pseudo)

### 10.1 Loader wires
```python
# core/libraries/ontology/loader.py already implemented
ontology = load_ontology()

# pass into agents/stages
extraction_agent = GraphExtractionAgent(..., ontology=ontology)
graph_builder = GraphBuilder(..., constraints=load_yaml("ontology/constraints.yml"))
stage_cfg = load_yaml("configs/stage_config.yml")
```

### 10.2 Action application
```python
def patch_yaml(path, edits):
    y = load_yaml(path)
    for op in edits:
        apply_op(y, op)  # add/remove/replace with jsonpatch-like syntax
    write_yaml_atomic(path, y)  # with .tmp + rename
```

### 10.3 Canary execution
```python
def run_pipeline(sources, canary=1.0):
    chosen = sample_sources(sources, frac=canary)
    return execute_stages(chosen, configs=stage_cfg, ontology=ontology)
```

---

## 11) Cursor tasks (copy/paste)

**Task A — Create YAMLs & validators**
```
Implement pydantic validators for:
- canonical_predicates.yml
- predicate_map.yml
- types.yml
- constraints.yml
- stage_config.yml
- quality_targets.yml
Add `scripts/validate_yaml.py` and a CI step to run it.
```

**Task B — Diagnostics Pack v2**
```
Extend diagnostics to compute all metrics in §3, emit JSON + Markdown report.
Add sampling-based LLM eval harness with budget controls.
```

**Task C — Autotuner Orchestrator**
```
Build `graphrag/autotune.py` with the loop in §5.1, including canary, budgets, rollback, and audit logs.
```

**Task D — Action Library**
```
Implement rule-based planners that map metric deltas to YAML edits (see §4).
Provide dry-run mode to preview diffs.
```

**Task E — Community Labeler**
```
Add LLM-based labeler producing 3–7 word titles + confidence, stored into communities.
```

---

## 12) Directory layout

```
ontology/
  canonical_predicates.yml
  predicate_map.yml
  types.yml
  constraints.yml
configs/
  stage_config.yml
  quality_targets.yml
scripts/
  derive_ontology.py
  build_predicate_map.py
  validate_yaml.py
graphrag/
  autotune.py
  diagnostics/
    __init__.py
    metrics.py
    report.py
```

---

## 13) Rollout plan
1. **Baseline** a known channel with current configs; store full run.
2. Turn on **Diagnostics v2** and verify metrics.
3. Enable autotuner in **dry‑run**; review patches.
4. Enable **canary 10%**; check targets; then promote.
5. Expand to new sources (new channels / PDFs) with per‑source runs and separate targets if needed.

---

### Appendix A — Example actions.yml (one iteration)
```yaml
actions:
  - type: map_predicate
    from: utiliz
    to: uses
  - type: drop_predicate
    variant: mention
  - type: add_symmetric
    predicate: similar_to
  - type: add_type_constraint
    predicate: uses
    allow: [ALGORITHM, DATASTRUCTURE]
  - type: set_threshold
    path: extraction.relationship_filters.min_confidence
    value: 0.35
  - type: set_param
    path: graph_construction.semantic_similarity.threshold
    value: 0.94
```

---

**You’re set.** This gives you a repeatable, audit‑able way to “teach” the system how to tune itself for each new data source while keeping precision under control.
