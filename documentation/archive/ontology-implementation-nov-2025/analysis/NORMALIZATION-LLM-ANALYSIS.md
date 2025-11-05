# Predicate Normalization - LLM Agent Analysis

**Date**: November 4, 2025  
**Status**: 🔍 **Analysis - Identifying Cases Requiring LLM**

---

## 🔍 Current Test Failures Analysis

### Failure 1: "teaches" → Expected "teach", Got "teache"
- **Pattern**: Ends with "ches" AND "es"
- **Current Behavior**: Matches "es" rule → removes "es" → "teache" ❌
- **Expected**: Should match "ches" rule → remove "s" → "teach" ✓
- **Root Cause**: "teaches" matches BOTH "ches" and "es" patterns, but "es" rule is checked first

### Failure 2: "includes" → Expected "include", Got "includ"
- **Pattern**: Ends with "ses" AND "es"
- **Current Behavior**: Matches "es" rule → removes "es" → "includ" ❌
- **Expected**: Should match "ses" rule → remove "s" → "include" ✓
- **Root Cause**: "includes" matches BOTH "ses" and "es" patterns, but "es" rule is checked first

### Failure 3: "classes" → Expected "classes", Got "classe"
- **Pattern**: Ends with "ses" AND in special list
- **Current Behavior**: Matches "ses" rule → removes "s" → "classe" ❌
- **Expected**: Should match special list → keep as-is → "classes" ✓
- **Root Cause**: "classes" matches "ses" rule BEFORE special list check (but we moved it...)

---

## 🔬 Root Cause Analysis

### The Core Problem: Overlapping Patterns

Many words match **multiple patterns simultaneously**:

| Word | Matches | Expected Rule | Current Rule |
|------|---------|---------------|--------------|
| `teaches` | `ches`, `es` | `ches` (remove "s") | `es` (remove "es") ❌ |
| `includes` | `ses`, `es` | `ses` (remove "s") | `es` (remove "es") ❌ |
| `classes` | `ses`, special list | special list (keep) | `ses` (remove "s") ❌ |

### Why Pure Logic Fails

1. **Overlapping Suffixes**: "ches" is a subset of "es", so any word ending in "ches" also ends in "es"
2. **Pattern Priority**: Current code checks longer patterns first, but "es" rule comes after "ches" rule
3. **Special Cases**: Exception lists can't cover all morphological variations

---

## 🎯 Cases Requiring LLM Agent

### Category 1: Ambiguous "es" Endings

**Problem**: Can't determine with pure logic whether to:
- Remove "es" (plural nouns: "boxes" → "box")
- Remove "s" from "es" (verbs: "teaches" → "teach", "includes" → "include")
- Keep as-is (special plurals: "classes" → "classes")

**Examples**:
- `teaches` → `teach` (verb, 3rd person)
- `includes` → `include` (verb, 3rd person)
- `boxes` → `box` (plural noun)
- `classes` → `classes` (special plural, keep)

**Solution**: LLM can determine word type (verb vs noun) and apply correct stemming

### Category 2: Overlapping Suffix Patterns

**Problem**: Words match multiple suffix patterns:
- `teaches` matches both `ches` and `es`
- `includes` matches both `ses` and `es`
- `classes` matches both `ses` and special list

**Solution**: LLM can determine which pattern is correct based on morphological analysis

### Category 3: Morphological Ambiguity

**Problem**: Same ending pattern, different morphological rules:
- `teaches` (verb) → `teach` (remove "s" from "ches")
- `reaches` (verb) → `reach` (remove "s" from "ches")
- `matches` (verb/noun) → `match` (remove "s" from "ches")
- But `classes` (noun) → `classes` (keep as-is)

**Solution**: LLM understands morphological context

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
   - Words matching multiple patterns
   - Words requiring morphological disambiguation

### LLM Agent Design:

```python
def _normalize_predicate_with_llm(self, predicate: str) -> str:
    """
    Use LLM to normalize ambiguous predicate forms.
    
    Only called for ambiguous cases where pure logic fails.
    Uses lightweight LLM call for morphological analysis.
    """
    # Cache check first
    if predicate in self._normalization_cache:
        return self._normalization_cache[predicate]
    
    # Ask LLM for base form
    prompt = f"""Normalize this English predicate to its base form.

Rules:
- For verbs ending in "es": remove just "s" (teaches → teach, includes → include)
- For plural nouns ending in "es": remove "es" (boxes → box)
- Keep special plurals as-is (classes → classes, phases → phases)
- For verbs ending in "ing": remove "ing" (teaching → teach)

Predicate: {predicate}
Base form (single word, no explanation):"""
    
    # Call LLM (lightweight, fast model)
    response = self.llm_client.chat.completions.create(
        model="gpt-4o-mini",  # Fast, cheap model
        messages=[
            {"role": "system", "content": "You are a linguistic normalization assistant. Return only the normalized word, no explanation."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=10,
        temperature=0.0
    )
    
    base_form = response.choices[0].message.content.strip().lower()
    
    # Cache result
    self._normalization_cache[predicate] = base_form
    
    return base_form
```

### Integration:

```python
def _normalize_predicate_string(self, predicate: str) -> str:
    """
    Normalize predicate with hybrid approach.
    """
    # ... existing pure logic ...
    
    # For each token, check if ambiguous
    for token in tokens:
        if self._is_ambiguous_token(token):
            # Use LLM for ambiguous cases
            normalized_token = self._normalize_predicate_with_llm(token)
            stemmed_tokens.append(normalized_token)
        else:
            # Use pure logic for clear cases
            stemmed_tokens.append(self._normalize_with_logic(token))
    
    return "_".join(stemmed_tokens)

def _is_ambiguous_token(self, token: str) -> bool:
    """
    Detect if token requires LLM normalization.
    
    Ambiguous cases:
    - Ends with "es" (could be verb or noun)
    - Matches multiple patterns
    - Not in special list but ends with "ses"/"ches"/etc.
    """
    if len(token) <= 3:
        return False
    
    # Clear cases handled by logic
    if token.endswith("ing") or token.endswith("ies"):
        return False
    
    if token in ["classes", "phases", "bases", "cases"]:
        return False
    
    # Ambiguous: ends with "es" but could be verb or noun
    if token.endswith("es") and len(token) > 4:
        # Check if it's a clear case
        if token.endswith("ses") or token.endswith("ches") or token.endswith("shes") or token.endswith("xes") or token.endswith("zes"):
            # Matches multiple patterns - ambiguous
            return True
    
    return False
```

---

## 📋 Implementation Plan

### Step 1: Identify Ambiguous Cases

Create detection function for ambiguous predicates.

### Step 2: Implement LLM Normalization Agent

Create lightweight LLM call for morphological analysis.

### Step 3: Add Caching

Cache LLM results to avoid repeated calls for same predicates.

### Step 4: Integrate Hybrid Approach

Update `_normalize_predicate_string` to use hybrid logic + LLM.

---

## ⚠️ Alternative: Fix Logic First

Before implementing LLM, we could try fixing the logic:

1. **Fix Pattern Order**: Check longer patterns (ches, ses) AFTER checking if word ends with "es"
2. **Fix Special List**: Ensure special list is checked before ALL suffix rules
3. **Add More Exceptions**: Expand exception lists

But given the user's feedback that fixes break other things, LLM approach may be more robust.

---

**Status**: ⏳ **AWAITING APPROVAL** - Should we implement LLM agent for ambiguous cases?

