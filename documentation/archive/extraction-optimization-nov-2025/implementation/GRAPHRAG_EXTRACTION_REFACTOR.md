extraction stage. Follow the prompt f# 🧠 GraphRAG Extraction Refactor — Ontology + Predicate Normalization

**Goal:**  
Refactor the GraphRAG pipeline to load canonical predicate definitions, normalize entities and relationships, and filter noisy edges before graph construction and community detection.  

This will make the graph more semantically coherent, reduce single-node communities, and improve downstream summarization.

---

## ✅ Deliverables

1. **Refactored extraction stage (`GraphExtractionAgent` or similar)**  
   - Loads ontology YAML files (`canonical_predicates.yml`, `predicate_map.yml`, `types.yml` optional)  
   - Canonicalizes and filters predicates  
   - Normalizes entity types (reduce “OTHER”)  
   - Enforces type-pair constraints  
   - Handles symmetric relations (de-duplication by sorting endpoints)

2. **Ontology folder structure**
   ```
   /ontology
     ├─ canonical_predicates.yml
     ├─ predicate_map.yml
     └─ types.yml               # optional future use
   ```

3. **New `.env` variable**
   ```
   GRAPHRAG_ONTOLOGY_DIR=ontology
   ```

4. **Automatic fallback** if files are missing (log warning, continue silently).

---

## 🧩 canonical_predicates.yml

```yaml
canonical_predicates:
  # Taxonomy / composition
  - is_a
  - part_of
  - member_of

  # Topical containment
  - focuses_on
  - includes

  # Usage / dependency
  - uses
  - requires
  - depends_on

  # Implementation / authorship / production
  - implemented_in
  - created_by
  - produced_by
  - used_by

  # Evaluation / training / measurement
  - trained_on
  - evaluated_on
  - measured_by
  - has_property

  # Causal / outcome / temporal
  - causes
  - results_in
  - precedes

  # Location / affiliation / hosting
  - located_in
  - works_at
  - hosted_on

  # Citation / reference
  - references

  # Comparatives / relations (symmetric)
  - related_to
  - similar_to
  - interacts_with
  - integrates_with
  - compatible_with
  - connected_to
  - compared_to
  - contrasts_with
  - equivalent_to
  - collaborates_with
  - partners_with

symmetric_predicates:
  - related_to
  - similar_to
  - interacts_with
  - integrates_with
  - compatible_with
  - connected_to
  - compared_to
  - contrasts_with
  - equivalent_to
  - collaborates_with
  - partners_with

predicate_type_constraints:
  is_a:
    - [ALGORITHM, CONCEPT]
    - [METHOD, CONCEPT]
    - [MODEL, CONCEPT]
    - [DATASTRUCTURE, CONCEPT]
    - [CONCEPT, CONCEPT]
```

---

## 🗺 predicate_map.yml

(see full mapping section in previous message)

---

## ⚙️ Code changes to implement

(see code sections in previous message)

---

## 🧾 Testing checklist

- [ ] All files load without error (`ontology/*.yml`)  
- [ ] Extraction logs show canonical predicate count (~40–60 total)  
- [ ] Edge count reduces by 20–40 % but graph modularity increases  
- [ ] `OTHER` type count drops; new types (DATASTRUCTURE, COURSE) appear  
- [ ] Community count stabilizes (~hundreds, not tens of thousands)  
- [ ] Sample graph inspection: `uses`, `requires`, `depends_on`, `is_a`, `part_of`, `related_to` dominate  

---

**End of document.**
