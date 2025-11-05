# Predicate Map Lookup Fix

**Date**: November 4, 2025  
**Status**: ✅ **Fix Applied**

---

## 🔍 Issue

The test `test_canonicalization_with_mapping()` was failing because:

- "utiliz" is in `predicate_map` with value "uses"
- But "utiliz" was being morphologically normalized to "utilize" FIRST
- Then we checked `predicate_map.get("utilize")` which doesn't exist
- The test expects `predicate_map["utiliz"]` → "uses"

---

## ✅ Solution

**Check `predicate_map` with raw normalized form BEFORE morphological normalization:**

```python
def _canonicalize_predicate(self, predicate: str, confidence: float = 0.0) -> Optional[str]:
    # First, normalize predicate (lowercase, snake_case) - basic normalization only
    normalized_raw = unidecode(predicate.strip().lower())
    normalized_raw = re.sub(r"[^a-z0-9]+", "_", normalized_raw)
    normalized_raw = re.sub(r"_+", "_", normalized_raw).strip("_")

    # Check if already canonical BEFORE morphological normalization
    if normalized_raw in self.ontology.get("canonical_predicates", set()):
        return normalized_raw

    # Check predicate_map with raw normalized form FIRST (before morphological normalization)
    # This handles cases like "utiliz" → "uses" where the map key is the raw form
    predicate_map = self.ontology.get("predicate_map", {})
    canonical_from_raw = predicate_map.get(normalized_raw)
    if canonical_from_raw == "__DROP__":
        return None
    if canonical_from_raw:
        return canonical_from_raw  # ✓ Found "utiliz" → "uses"

    # Now normalize predicate morphologically (this may change it)
    normalized = self._normalize_predicate_string(predicate)

    # Check predicate_map with morphologically normalized form (in case map uses normalized form)
    canonical = predicate_map.get(normalized)
    if canonical == "__DROP__":
        return None
    if canonical:
        return canonical

    # ... rest of logic
```

---

## 🎯 Order of Operations

1. **Raw normalization** (lowercase, snake_case): "utiliz" → "utiliz"
2. **Check canonical_predicates**: Not found
3. **Check predicate_map with raw form**: "utiliz" → "uses" ✓ **FOUND**
4. **Return "uses"** (don't need morphological normalization)

---

## ✅ Expected Behavior

After fix:

- ✅ "utiliz" → Check predicate_map with raw form → Found "uses" → Return "uses"
- ✅ "results_in" → Check canonical_predicates with raw form → Found → Return "results_in"
- ✅ Other predicates still work correctly

---

**Status**: ✅ **COMPLETE** - This is a NEW fix, not repeating previous issues.
