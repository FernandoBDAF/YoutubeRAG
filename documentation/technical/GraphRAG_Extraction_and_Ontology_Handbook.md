# GraphRAG Extraction & Ontology Handbook

## 1. Overview

The **GraphRAG Extraction & Ontology System** transforms unstructured educational or technical text (e.g., YouTube transcripts, academic lectures, tutorials) into a **semantic graph** — a network of entities and relationships enriched with ontological structure.

This handbook serves as a **technical guide** for developers and researchers implementing, refining, or extending the extraction, normalization, and ontology stages of GraphRAG.

---

## 2. Architecture Overview

### 2.1 Core Stages

1. **Chunking** — Split source documents or transcripts into coherent, semantically-contained segments.
2. **Extraction** — Identify entities and relationships within each chunk using an LLM (structured output).
3. **Ontology Normalization** — Canonicalize predicates, enforce type constraints, and normalize symmetric relations.
4. **Embedding** — Convert structured knowledge into vector form for similarity search and clustering.
5. **Community Detection & Summarization** — Group semantically or topologically related nodes to derive higher-order concepts.

### 2.2 Component Layers

| Layer | Module | Responsibility |
|-------|---------|----------------|
| Agent | `GraphExtractionAgent` | LLM-based structured extraction |
| Loader | `ontology/loader.py` | Loads canonical predicates, mappings, and constraints |
| Stage | `GraphExtractionStage` | Batch orchestration, storage, and logging |
| Ontology Files | `.yml` | Define canonical predicates, symmetric predicates, and mappings |

---

## 3. Extraction Layer (LLM-driven)

### 3.1 LLM Responsibilities

The LLM performs two key subtasks:

- **Entity Extraction** → Detect distinct concepts, objects, people, or technologies.  
- **Relationship Extraction** → Describe directed or bidirectional links between entities.

### 3.2 Entity Schema

Each entity includes:

| Field | Type | Description |
|--------|------|-------------|
| `name` | string | Canonical name of entity |
| `type` | enum | One of PERSON, ORGANIZATION, TECHNOLOGY, CONCEPT, LOCATION, EVENT, METHOD, OTHER |
| `description` | string | Contextualized definition from text |
| `confidence` | float | Confidence score from 0–1 |

### 3.3 Relationship Schema

| Field | Type | Description |
|--------|------|-------------|
| `source_entity` | EntityModel | Origin entity |
| `target_entity` | EntityModel | Target entity |
| `relation` | string | Canonical predicate |
| `description` | string | Contextual phrase or justification |
| `confidence` | float | Confidence score |

---

## 4. Ontology System

### 4.1 Purpose

The ontology constrains and normalizes relationships, ensuring the extracted graph is **semantically stable** and **consistent across documents**.

### 4.2 Core Ontology Files

| File | Role |
|------|------|
| `canonical_predicates.yml` | High-confidence predicate list & symmetric relations |
| `predicate_map.yml` | Variant → canonical mappings |
| `types.yml` | Type normalization or aliases |

### 4.3 Canonicalization Flow

1. **Normalize string:** Lowercase, snake_case, basic lemmatization.  
2. **Map variant → canonical predicate** (via `predicate_map.yml`).  
3. **Enforce canonical predicate list.**  
4. **Apply type constraints** (via `predicate_type_constraints`).  
5. **Normalize symmetric relations** (sort endpoints alphabetically).  

If a predicate does not appear in either `predicate_map.yml` or `canonical_predicates.yml`, it is dropped (or optionally kept if an environment flag is set).

### 4.4 Type Constraints

Each predicate may define allowed (source_type, target_type) pairs:

```yaml
predicate_type_constraints:
  teaches:
    - [PERSON, CONCEPT]
    - [PERSON, COURSE]
  located_in:
    - [ORGANIZATION, LOCATION]
```

These help prevent illogical relations like `Concept located_in Algorithm`.

---

## 5. Data Study & Ontology Improvement

To improve graph quality, predicate coverage, and group naming, **empirical data analysis** is essential.

### 5.1 Frequency Analysis

Query extracted relationships and count predicates and entity types:

```python
db.video_chunks.aggregate([
  {{ "$unwind": "$graphrag_extraction.data.relationships" }},
  {{ "$group": { "_id": "$graphrag_extraction.data.relationships.relation", "count": {{ "$sum": 1 }} }}},
  {{ "$sort": { "count": -1 }}}
])
```

- Identify **dominant predicates** (e.g., “uses”, “applies_to”, “depends_on”).
- Detect **noisy predicates** (e.g., “is”, “does”, “exist”). Add them to `predicate_map.yml` → `__DROP__`.

### 5.2 Type Co-occurrence Analysis

Compute co-occurrence matrix between (source_type, target_type) pairs.  
This helps identify which type pairs dominate per predicate and whether constraints are too strict or too broad.

### 5.3 Cluster Analysis for Group Names

Once embeddings are created, run **community detection** (e.g., Louvain or Leiden) to group semantically similar nodes.

Then, study the **top terms** or **entity names** within each cluster:
- Use TF-IDF or embedding centroid similarity to suggest cluster names.
- Example heuristic: the top 3 entities by degree centrality → proposed group label.

### 5.4 Predicate Refinement Loop

1. Run extraction and embedding.  
2. Identify frequent predicates missing from canonical list.  
3. Review examples manually.  
4. Add canonical mappings or constraints.  
5. Re-run extraction on small batch to validate consistency.

---

## 6. Evaluation and Quality Metrics

### 6.1 Extraction Metrics

| Metric | Description |
|---------|-------------|
| Entity Count | Number of unique entities extracted |
| Relationship Count | Total relationships extracted |
| Confidence Distribution | Average LLM confidence |
| Predicate Diversity | Ratio of unique predicates to total predicates |
| Type Coverage | Fraction of entity types represented |

### 6.2 Ontology Metrics

| Metric | Description |
|---------|-------------|
| Canonicalization Rate | % of predicates successfully mapped |
| Constraint Violation Rate | % of relationships dropped by type constraints |
| Symmetry Rate | % of symmetric predicates correctly normalized |
| Unknown Predicate Rate | % of predicates dropped as unknown |

---

## 7. Advanced Topics & Research Directions

### 7.1 Embedding-Enhanced Canonicalization

Use sentence-transformer embeddings to cluster predicate phrases and auto-suggest canonical groupings:

```python
from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer('all-MiniLM-L6-v2')
similarity = util.cos_sim(model.encode('uses'), model.encode('utilizes'))
```

This can support semi-supervised ontology expansion.

### 7.2 Graph Neural Network (GNN) Fine-Tuning

Train GNNs or node2vec embeddings to learn graph structure and infer new relationships.

- **Goal:** Predict missing edges or cluster relationships beyond textual similarity.
- **Use Cases:** Topic expansion, knowledge enrichment, automatic ontology growth.

### 7.3 Contextual Canonicalization

In some corpora, predicate meaning changes by domain (e.g., “runs_on” differs between hardware and business contexts).  
Future improvement: context-aware canonicalization using **cross-encoder embeddings** or domain tags.

### 7.4 Community Detection Research

Compare algorithms for hierarchical grouping:
- **Louvain / Leiden** → modularity optimization
- **Infomap** → information flow
- **HDBSCAN** → density-based semantic clustering

Use metrics such as modularity Q, cluster cohesion, and semantic purity.

### 7.5 Ontology Evolution

Introduce **versioned ontologies**:
- Maintain `v1`, `v2`, `v3` YAMLs.  
- Compare diffs automatically with predicate usage stats.  
- Support automatic migration of stored relationships.

---

## 8. References & Further Reading

### Knowledge Graphs & Ontology Design
- Hogan et al. (2021). *Knowledge Graphs*. ACM Computing Surveys.  
- Lehmann et al. (2015). *DBpedia – A Large-scale, Multilingual Knowledge Base*.  
- Noy & McGuinness (2001). *Ontology Development 101*. Stanford Knowledge Systems Laboratory.

### Graph Algorithms
- Blondel et al. (2008). *Fast unfolding of communities in large networks (Louvain Method)*.  
- Traag et al. (2019). *From Louvain to Leiden: guaranteeing well-connected communities.*

### Semantic Extraction & NLP
- Honnibal & Montani (2017). *spaCy 2: Natural language understanding with Bloom embeddings*.  
- Schlichtkrull et al. (2018). *Modeling relational data with graph convolutional networks (R-GCN).*

### Embedding Models
- Reimers & Gurevych (2019). *Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks.*  
- Mikolov et al. (2013). *Efficient Estimation of Word Representations in Vector Space (word2vec).*

---

## 9. Next Steps

1. **Run a pilot extraction** on a small, mixed dataset (MIT OCW, tech talks, interviews).  
2. **Perform predicate frequency analysis** → update mappings.  
3. **Apply community detection** and manually review cluster names.  
4. **Iteratively refine** ontology files and normalization logic.  
5. **Document all changes** in `ONTOLOGY_CHANGELOG.md`.

---

**Author:** Fernando Barroso & AI Co‑research Partner  
**Project:** Sempre Fichas — Agentic Poker Magazine / GraphRAG Research  
**Last Updated:** 2025-11-04
