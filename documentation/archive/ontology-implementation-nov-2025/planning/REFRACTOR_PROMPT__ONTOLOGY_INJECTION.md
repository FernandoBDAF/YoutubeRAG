# 🧠 Prompt: Refactor GraphExtractionAgent to Load and Inject Ontology Context

## Task
Refactor the `GraphExtractionAgent` class to dynamically **load ontology files** (`canonical_predicates.yml`, `predicate_map.yml`, and `types.yml`) and automatically inject a compact ontology summary into the `system_prompt` at runtime.

---

## 🎯 Goals
1. **Do NOT inline full YAML content** into the prompt — only load it dynamically.
2. **Summarize ontology data** into short contextual lists for the model:
   - 30–50 canonical predicates
   - All allowed entity types
3. **Inject the summary** into the system prompt dynamically when the agent initializes.
4. Preserve the existing LLM extraction logic, retry behavior, and structured output format (`KnowledgeModel`).
5. **Keep everything backward compatible** — if ontology files are missing, fall back to default behavior (no filtering).

---

## 🧱 Implementation Plan

### 1️⃣ Load Ontology Files
In `GraphExtractionAgent.__init__`, after initializing `self.llm_client`, load the ontology files:

```python
import yaml
from pathlib import Path

def _load_yaml(self, file_name: str):
    path = Path("ontology") / file_name
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
```

Then call:
```python
self.canonical_data = self._load_yaml("canonical_predicates.yml") or {}
self.predicate_map = self._load_yaml("predicate_map.yml") or {}
self.types_data = self._load_yaml("types.yml") or {}
```

---

### 2️⃣ Generate a Compact Ontology Summary
Add a helper method to prepare summarized text for the prompt:

```python
def _build_ontology_context(self) -> str:
    canonical_list = self.canonical_data.get("canonical_predicates", [])[:50]
    canonical_preview = ", ".join(canonical_list) + (", ..." if len(canonical_list) > 50 else "")
    types = self.types_data.get("types", []) or [
        "PERSON","ORGANIZATION","CONCEPT","METHOD","TECHNOLOGY","PROCESS","TASK",
        "THEORY","LAW","FORMULA","EXPERIMENT","DATASTRUCTURE","ALGORITHM","MODEL",
        "METRIC","COURSE","EVENT","LOCATION","MATERIAL","OTHER"
    ]
    type_preview = ", ".join(types)
    return f"""
### Ontology Context (auto-loaded)
Use only predicates from the canonical ontology (examples):
{canonical_preview}

Allowed entity types:
{type_preview}

If a new relation or type appears, choose the closest semantic match.
"""
```

---

### 3️⃣ Inject It into the System Prompt
Concatenate the ontology summary to your improved extraction prompt:

```python
self.system_prompt = f"""
{BASE_EXTRACTION_PROMPT}

{self._build_ontology_context()}
"""
```

`BASE_EXTRACTION_PROMPT` should contain the main extraction logic text (your improved prompt that defines how to extract entities and relationships).

---

### 4️⃣ Preserve Existing Functionality
- Keep `self._validate_and_enhance` unchanged (it will still use ontology filtering).
- Ensure `load_ontology()` continues to work as fallback when files are missing.
- The LLM now sees a compact ontology context before extraction begins, improving predicate alignment.

---

### 5️⃣ Optional Enhancement (Later)
If you want to centralize this across all agents:
- Move the YAML loading + summarization logic to `core.libraries.ontology.utils.py`
- Expose a `get_ontology_summary()` helper returning the formatted text block
- Each agent (Extraction, Enrichment, Embedding) can then append that to its own prompt dynamically

---

## ✅ Deliverables
- Updated `GraphExtractionAgent` class with:
  - Dynamic ontology loading
  - `_build_ontology_context()` helper
  - System prompt injection using live ontology summary
- Fully backward-compatible behavior
- Clean, maintainable code ready for Cursor autocompletion and testing

---

## 💡 Notes
- Do NOT hardcode the ontology lists — read them from disk at runtime.
- Ensure the file paths resolve from the project root or environment variable `GRAPHRAG_ONTOLOGY_DIR`.
- Log loaded counts (canonical predicates, type constraints, etc.) for debugging.
- The final system prompt should look like:

```
[Extraction Instructions...]
--- 
### Ontology Context (auto-loaded)
Use only predicates from the canonical ontology (examples):
uses, depends_on, integrates_with, teaches, applies_to, part_of, ...

Allowed entity types:
PERSON, ORGANIZATION, TECHNOLOGY, CONCEPT, METHOD, PROCESS, TASK, THEORY, ...
```

---

## 🧩 Output
When complete, the class should automatically adapt to ontology changes without modifying code or prompt text.  
Future updates to `.yml` files will instantly propagate to all extraction runs.
