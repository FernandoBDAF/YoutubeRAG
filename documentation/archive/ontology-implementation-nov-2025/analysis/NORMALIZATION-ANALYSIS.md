# Predicate Normalization - Problem Analysis

**Date**: November 4, 2025  
**Status**: 🔍 **Analysis - Identifying Cases Requiring LLM**

---

## 🔍 Current Test Failures

### Failure 1: "teaches" → Expected "teach", Got "teache"

- **Pattern**: Ends with "es"
- **Issue**: Logic removes "es" → "teache" (wrong)
- **Expected**: Should become "teach" (remove "es" after "ch")
- **Root Cause**: "teaches" is a verb form, needs morphological understanding

### Failure 2: "includes" → Expected "include", Got "includ"

- **Pattern**: Ends with "ses"
- **Issue**: Logic removes "es" instead of "s"
- **Expected**: Should become "include" (remove just "s")
- **Root Cause**: "includes" ends with "ses" but the "ses" rule isn't matching correctly, or it's matching "es" rule first

### Failure 3: "classes" → Expected "classes", Got "classe"

- **Pattern**: Ends with "ses" + in special list
- **Issue**: Logic removes "s" even though it's in special list
- **Expected**: Should be kept as "classes"
- **Root Cause**: Special list check may not be working, or order issue

---

## 🧠 Morphological Complexity

### The Fundamental Problem

English morphology is **ambiguous** - the same ending pattern can mean different things:

| Word       | Ending | Pattern     | Expected Base | Morphological Type    |
| ---------- | ------ | ----------- | ------------- | --------------------- |
| `teaches`  | `es`   | `ch` + `es` | `teach`       | 3rd person verb       |
| `boxes`    | `es`   | `x` + `es`  | `box`         | Plural noun           |
| `phases`   | `es`   | `s` + `es`  | `phases`      | Special plural (keep) |
| `includes` | `es`   | `de` + `s`  | `include`     | 3rd person verb       |
| `classes`  | `es`   | `ss` + `es` | `classes`     | Special plural (keep) |
| `uses`     | `s`    | `e` + `s`   | `use`         | 3rd person verb       |

### Why Pure Logic Fails

1. **Ambiguous Endings**: "es" can be:

   - Third-person singular verb marker ("teaches" → "teach")
   - Plural noun marker ("boxes" → "box")
   - Special plural kept as-is ("classes" → "classes")

2. **Context-Dependent**: The same word can be:

   - Verb: "includes" → "include"
   - Noun: "includes" (as a noun, might be kept or different)

3. **Phonological Rules**: English has complex rules:
   - Words ending in "ch", "sh", "x", "z", "s" add "es" for plural/3rd person
   - But "ses" can be "s" + "es" or base ending in "s" + "s"

---

## 🎯 Cases Requiring LLM Agent

### Category 1: Ambiguous "es" Endings

**Problem**: Can't distinguish with pure logic:

- Third-person verbs: "teaches", "includes", "uses"
- Plural nouns: "boxes", "phases"
- Special plurals: "classes", "bases", "cases"

**Solution**: Use LLM to classify word type (verb vs noun) and determine correct stemming

### Category 2: Overlapping Patterns

**Problem**: Multiple rules could apply:

- "teaches" ends with both "es" AND "ches"
- "includes" ends with both "es" AND "ses"
- "classes" ends with "ses" AND is in special list

**Solution**: Use LLM to determine which rule applies based on morphological analysis

### Category 3: Special Cases

**Problem**: Exception lists can't cover all cases:

- "classes" is special, but "masses" might not be
- "phases" is special, but "phrases" might not be

**Solution**: Use LLM to identify if a word is a special plural/noun that should be kept

---

## 💡 Proposed Solution: Hybrid Approach

### Strategy:

1. **Simple Cases** (Pure Logic): Handle clear cases with deterministic rules

   - Words ending in "ing" → remove "ing"
   - Words ending in "ies" → convert to "y"
   - Short words (len <= 3) → keep as-is
   - Known special list → keep as-is

2. **Ambiguous Cases** (LLM Agent): Use LLM for complex morphology
   - Words ending in "es" that might be verbs
   - Words ending in "ses"/"ches"/"shes"/"xes"/"zes"
   - Words that match multiple patterns

### LLM Agent Design:

```python
def _normalize_predicate_with_llm(self, predicate: str) -> str:
    """
    Use LLM to normalize ambiguous predicate forms.

    Only called for ambiguous cases where pure logic fails.
    """
    # Ask LLM to determine base form
    prompt = f"""
    Normalize this English predicate to its base form.
    Rules:
    - Remove verb endings (3rd person: teaches → teach, includes → include)
    - Keep plural nouns as-is if they're special (classes, phases)
    - Remove plural endings for regular nouns (boxes → box)

    Predicate: {predicate}
    Base form:"""

    # Call LLM (lightweight, cached)
    base_form = self._call_llm_for_normalization(predicate)
    return base_form
```

### Implementation Strategy:

1. **Try Pure Logic First**: Fast path for clear cases
2. **Fallback to LLM**: Only for ambiguous cases
3. **Cache Results**: Cache LLM results to avoid repeated calls
4. **Batch Processing**: Process multiple ambiguous predicates in one LLM call

---

## 📋 Implementation Plan

### Step 1: Identify Ambiguous Cases

Create a function to detect ambiguous predicates:

```python
def _is_ambiguous_predicate(self, token: str) -> bool:
    """
    Detect if a predicate requires LLM normalization.

    Ambiguous cases:
    - Ends with "es" (could be verb or noun)
    - Ends with "ses"/"ches"/"shes"/"xes"/"zes" (overlapping patterns)
    - Matches multiple rules
    """
```

### Step 2: Implement LLM Normalization Agent

Create a lightweight LLM call for normalization:

```python
def _normalize_with_llm(self, predicate: str) -> str:
    """
    Use LLM to determine correct base form.

    This is a lightweight call - just normalization, not full extraction.
    """
```

### Step 3: Integrate Hybrid Approach

Update `_normalize_predicate_string`:

```python
def _normalize_predicate_string(self, predicate: str) -> str:
    # Try pure logic first
    result = self._normalize_with_logic(predicate)

    # If ambiguous, use LLM
    if self._is_ambiguous(result, predicate):
        result = self._normalize_with_llm(predicate)

    return result
```

---

## ⚠️ Alternative: Simplify Logic

If LLM approach is too complex, we could:

1. **Expand Special List**: Add more exceptions to special list
2. **Accept Imperfections**: Some edge cases will be wrong
3. **Use Predicate Map**: Map common variations in `predicate_map.yml`

---

**Status**: ⏳ **AWAITING DECISION** - Should we implement LLM agent for ambiguous cases, or simplify logic?
