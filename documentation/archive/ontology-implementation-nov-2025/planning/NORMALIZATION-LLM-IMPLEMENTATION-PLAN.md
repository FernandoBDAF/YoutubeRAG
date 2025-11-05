# Predicate Normalization - LLM Agent Implementation Plan

**Date**: November 4, 2025  
**Status**: 📋 **Plan for Approval**

---

## 🔍 Problem Identification

### Cases Where Pure Logic Fails:

1. **"teaches"** → Expected "teach", Got "teache"

   - Matches: `ches` AND `es` patterns
   - Logic removes "es" → "teache" ❌
   - Needs: Remove "s" from "ches" → "teach" ✓

2. **"includes"** → Expected "include", Got "includ"

   - Matches: `ses` AND `es` patterns
   - Logic removes "es" → "includ" ❌
   - Needs: Remove "s" from "ses" → "include" ✓

3. **"classes"** → Expected "classes", Got "classe"
   - Matches: `ses` pattern AND special list
   - Logic removes "s" → "classe" ❌
   - Needs: Keep as-is (special plural) ✓

### Root Cause:

**Overlapping suffix patterns** - Words ending in "ches", "ses", "shes", "xes", "zes" ALSO end in "es":

- "teaches".endswith("ches") = True
- "teaches".endswith("es") = True
- "includes".endswith("ses") = True
- "includes".endswith("es") = True

The current logic checks longer patterns first (ches, ses) but something is still wrong.

---

## 🎯 Cases Requiring LLM Agent

### Category 1: Ambiguous "es" Endings

**Detection**: Words ending in "es" that ALSO match longer patterns:

- Ends with "ches", "ses", "shes", "xes", "zes"
- NOT in special list
- Requires morphological disambiguation (verb vs noun)

**Examples**:

- `teaches` → `teach` (verb, remove "s" from "ches")
- `includes` → `include` (verb, remove "s" from "ses")
- `reaches` → `reach` (verb, remove "s" from "ches")
- `boxes` → `box` (noun, remove "es")

**LLM Decision**: Determine if word is verb (remove "s") or noun (remove "es")

### Category 2: Special Plural Ambiguity

**Detection**: Words ending in "ses"/"ches" that MIGHT be special plurals:

- Could be special plural (keep) or verb form (normalize)
- Not in current special list but might need to be

**Examples**:

- `classes` → `classes` (special plural, keep)
- `masses` → `mass` (verb, normalize) OR `masses` (plural, keep)?

**LLM Decision**: Determine if word is special plural or verb

---

## 💡 Implementation Strategy

### Hybrid Approach:

1. **Pure Logic First** (Fast Path):

   - Clear cases: "ing", "ies", short words, known special list
   - No LLM needed

2. **LLM for Ambiguous Cases** (Slow Path):
   - Words ending in "es" that match multiple patterns
   - Lightweight LLM call with caching

### LLM Agent Design:

```python
def _normalize_predicate_with_llm(self, token: str) -> str:
    """
    Use LLM to normalize ambiguous predicate token.

    Only called for ambiguous cases where pure logic fails.
    Uses lightweight, fast LLM call with caching.
    """
    # Check cache first
    cache_key = f"normalize:{token}"
    if hasattr(self, '_normalization_cache'):
        if cache_key in self._normalization_cache:
            return self._normalization_cache[cache_key]
    else:
        self._normalization_cache = {}

    # Lightweight LLM call
    prompt = f"""Normalize this English predicate to its base form.

Rules:
- For verbs ending in "es": remove just "s" (teaches → teach, includes → include)
- For plural nouns ending in "es": remove "es" (boxes → box)
- Keep special plurals as-is (classes → classes, phases → phases)

Predicate: {token}
Base form (single word only, no explanation):"""

    try:
        response = self.llm_client.chat.completions.create(
            model="gpt-4o-mini",  # Fast, cheap model
            messages=[
                {
                    "role": "system",
                    "content": "You are a linguistic normalization assistant. Return only the normalized word, no explanation."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0.0  # Deterministic
        )

        base_form = response.choices[0].message.content.strip().lower()

        # Cache result
        self._normalization_cache[cache_key] = base_form

        return base_form
    except Exception as e:
        logger.warning(f"LLM normalization failed for '{token}': {e}, falling back to logic")
        # Fallback to logic
        return self._normalize_with_fallback_logic(token)
```

### Integration:

```python
def _normalize_predicate_string(self, predicate: str) -> str:
    """
    Normalize predicate with hybrid approach (logic + LLM).
    """
    # ... existing preprocessing ...

    for token in tokens:
        if self._is_ambiguous_token(token):
            # Use LLM for ambiguous cases
            normalized_token = self._normalize_predicate_with_llm(token)
            stemmed_tokens.append(normalized_token)
        else:
            # Use pure logic for clear cases
            normalized_token = self._normalize_with_logic(token)
            stemmed_tokens.append(normalized_token)

    return "_".join(stemmed_tokens)

def _is_ambiguous_token(self, token: str) -> bool:
    """
    Detect if token requires LLM normalization.

    Ambiguous cases:
    - Ends with "es" AND matches longer pattern (ches, ses, etc.)
    - Not in special list
    - Requires morphological disambiguation
    """
    if len(token) <= 3:
        return False

    # Clear cases handled by logic
    if token.endswith("ing") or token.endswith("ies"):
        return False

    if token in ["classes", "phases", "bases", "cases"]:
        return False

    # Ambiguous: ends with "es" AND matches longer pattern
    if token.endswith("es") and len(token) > 4:
        # Check if it matches multiple patterns
        matches_longer = (
            token.endswith("ches") or
            token.endswith("ses") or
            token.endswith("shes") or
            token.endswith("xes") or
            token.endswith("zes")
        )

        if matches_longer:
            # Ambiguous - requires LLM
            return True

    return False
```

---

## 📋 Implementation Steps

### Step 1: Add Normalization Cache

- Initialize cache in `__init__`
- Use for LLM results

### Step 2: Implement LLM Normalization Method

- Lightweight LLM call
- Error handling with fallback
- Caching

### Step 3: Implement Ambiguity Detection

- Identify ambiguous tokens
- Check for overlapping patterns

### Step 4: Integrate Hybrid Approach

- Update `_normalize_predicate_string`
- Try logic first, LLM for ambiguous cases

### Step 5: Add Fallback Logic

- If LLM fails, use best-effort logic
- Prevent total failure

---

## ⚠️ Considerations

### Performance:

- LLM calls are slower than logic
- Caching mitigates repeated calls
- Only called for ambiguous cases (~10-20% of predicates)

### Cost:

- Lightweight calls (max_tokens=10)
- Cached results
- Only for ambiguous cases
- Estimated: ~$0.0001 per ambiguous predicate

### Reliability:

- Fallback to logic if LLM fails
- Error handling prevents crashes
- Caching ensures consistency

---

## ✅ Expected Outcome

After implementation:

- All test cases pass (including "teaches", "includes", "classes")
- Fast path for clear cases (no LLM)
- LLM handles ambiguous cases correctly
- Cached results ensure consistency

---

**Status**: ⏳ **AWAITING APPROVAL** - Ready to implement once approved.
