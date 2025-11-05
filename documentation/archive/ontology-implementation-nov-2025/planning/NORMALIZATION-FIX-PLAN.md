# Predicate Normalization Fix - Analysis & Plan

**Date**: November 4, 2025  
**Status**: 🔍 **Analysis Complete - Awaiting Approval**

---

## 🔍 Problem Analysis

### Test Failures Observed:

1. **First Failure**: `"includes"` → Expected: `"include"`, Got: `"includ"`

   - **Issue**: Removed "es" (2 chars) instead of just "s" (1 char)
   - **Root Cause**: "includes" matches "es" rule before "ses" rule, or "ses" rule not working correctly

2. **Second Failure**: `"classes"` → Expected: `"classes"`, Got: `"classe"`
   - **Issue**: Removed "s" when it should be kept as-is (special plural)
   - **Root Cause**: "classes" matches "ses" rule BEFORE checking special list

---

## 🔬 Current Logic Flow (PROBLEMATIC)

```
For each token:
1. If len <= 3: keep as-is
2. If ends with "ing": remove "ing"
3. If ends with "ies": convert to "y"
4. If ends with "ses"/"xes"/"zes"/"ches"/"shes": remove "s"  ⚠️ PROBLEM: Catches "classes"
5. If ends with "es": check special list, else remove "es"  ⚠️ PROBLEM: Too late for "classes"
6. If ends with "s": remove "s"
```

### Issues:

1. **Order Problem**: "classes" ends with "ses", so it matches step 4 and removes "s" → "classe"

   - The special list check happens in step 5, but it's too late
   - "classes" is already processed by step 4

2. **Overlapping Patterns**: "includes" ends with both "ses" AND "es"
   - Current code checks "ses" first, which should work
   - But test shows it's removing "es" instead, suggesting the "ses" check isn't working

---

## 🎯 Expected Behavior

### Test Cases:

```python
("uses", "use"),          # Remove "s" → "use"
("has", "has"),           # Keep as-is (short word, in exception list)
("applies_to", "apply_to"),  # Remove "ing" → "apply", then "ies" → "y" → "apply"
("classes", "classes"),  # Keep as-is (special plural)
("teaches", "teach"),     # Remove "ing" → "teach"
("includes", "include"), # Remove "s" → "include"
```

### Word Endings Analysis:

| Word       | Ends With | Length | Special List? | Expected Result        |
| ---------- | --------- | ------ | ------------- | ---------------------- |
| `uses`     | `s`       | 4      | No            | `use` (remove "s")     |
| `has`      | `s`       | 3      | Exception     | `has` (keep)           |
| `applies`  | `ies`     | 7      | No            | `apply` (ies→y)        |
| `classes`  | `ses`     | 7      | **YES**       | `classes` (keep)       |
| `teaches`  | `ing`     | 7      | No            | `teach` (remove "ing") |
| `includes` | `ses`     | 8      | No            | `include` (remove "s") |

---

## 💡 Solution Plan

### New Logic Flow (CORRECT):

```
For each token:
1. If len <= 3: keep as-is
2. If ends with "ing" and len > 4: remove "ing"
3. If ends with "ies" and len > 4: convert to "y"
4. ⭐ CHECK SPECIAL PLURALS FIRST (before any suffix rules)
   - If in ["classes", "phases", "bases", "cases"]: keep as-is
5. If ends with "ses"/"xes"/"zes"/"ches"/"shes" and len > 4: remove "s"
6. If ends with "es" and len > 4: remove "es"
7. If ends with "s" and len > 2: remove "s" (unless in exception list)
```

### Key Changes:

1. **Move Special List Check First**: Check if token is in special list BEFORE any suffix matching

   - This prevents "classes" from being caught by "ses" rule
   - Place it right after length check, before any suffix rules

2. **Verify "ses" Rule Logic**: Ensure "includes" correctly matches "ses" rule

   - "includes".endswith("ses") should be True
   - Should remove just "s" → "include"

3. **Handle Edge Cases**:
   - "uses" has length 4, so "es" rule (len > 4) won't match → will match "s" rule ✓
   - "classes" in special list → keep as-is ✓
   - "includes" ends with "ses" → remove "s" → "include" ✓

---

## 📋 Implementation Plan

### Step 1: Reorder Checks

```python
for token in tokens:
    if len(token) <= 3:
        stemmed_tokens.append(token)
    elif token.endswith("ing") and len(token) > 4:
        stemmed_tokens.append(token[:-3])
    elif token.endswith("ies") and len(token) > 4:
        stemmed_tokens.append(token[:-3] + "y")
    # ⭐ MOVE SPECIAL LIST CHECK HERE (before "ses" rule)
    elif token in ["classes", "phases", "bases", "cases"]:
        stemmed_tokens.append(token)  # Keep as-is
    elif (token.endswith("ses") or token.endswith("xes") or
          token.endswith("zes") or token.endswith("ches") or
          token.endswith("shes")) and len(token) > 4:
        if token not in ["has", "is", "was", "as"]:
            stemmed_tokens.append(token[:-1])  # Remove "s"
        else:
            stemmed_tokens.append(token)
    elif token.endswith("es") and len(token) > 4:
        stemmed_tokens.append(token[:-2])  # Remove "es"
    elif token.endswith("s") and len(token) > 2:
        if token not in ["has", "is", "was", "as"]:
            stemmed_tokens.append(token[:-1])  # Remove "s"
        else:
            stemmed_tokens.append(token)
    else:
        stemmed_tokens.append(token)
```

### Step 2: Verify Test Cases

After implementation, verify:

- ✅ "uses" → "use"
- ✅ "has" → "has"
- ✅ "applies_to" → "apply_to" (token "applies" → "apply")
- ✅ "classes" → "classes"
- ✅ "teaches" → "teach"
- ✅ "includes" → "include"

---

## ⚠️ Potential Issues to Watch

1. **"uses" Length**: Has length 4, so "es" rule (len > 4) won't match

   - Should match "s" rule → remove "s" → "use" ✓
   - This is correct behavior

2. **"applies_to"**: Multi-token predicate

   - Token "applies" ends with "ies" → "apply"
   - Token "to" → "to"
   - Result: "apply_to" ✓

3. **Special Plurals**: Must be checked BEFORE any suffix rules
   - Otherwise "classes" gets caught by "ses" rule

---

## ✅ Expected Outcome

After fix:

- All 6 test cases should pass
- "classes" kept as-is (special plural)
- "includes" → "include" (remove "s" via "ses" rule)
- No over-stemming or bad stems

---

## 🎯 Approval Request

**Proposed Solution**: Move special plurals check to occur BEFORE the "ses" rule, ensuring "classes" is kept as-is while "includes" still correctly removes "s".

**Risks**: Low - only reordering existing checks, no new logic.

**Testing**: Run `python tests/test_ontology_extraction.py` to verify all tests pass.

---

**Status**: ⏳ **AWAITING APPROVAL** - Ready to implement once approved.
