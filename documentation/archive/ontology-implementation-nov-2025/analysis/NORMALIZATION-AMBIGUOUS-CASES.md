# Predicate Normalization - Ambiguous Cases Requiring LLM

**Date**: November 4, 2025

---

## 🔍 Identified Ambiguous Cases

### Case 1: Overlapping Suffix Patterns

**Problem**: Words ending in longer patterns (ches, ses, shes, xes, zes) ALSO end in "es"

**Examples**:

- `teaches` → ends with `ches` AND `es`
- `includes` → ends with `ses` AND `es`
- `reaches` → ends with `ches` AND `es`
- `boxes` → ends with `xes` AND `es`

**Issue**: Current logic can't determine which pattern to apply:

- Should remove "s" from "ches" → "teach" (verb)?
- Should remove "es" → "teache" (wrong)?

**Requires LLM**: Yes - needs morphological disambiguation (verb vs noun)

---

### Case 2: Special Plural vs Verb Form

**Problem**: Words ending in "ses"/"ches" might be special plurals (keep) or verbs (normalize)

**Examples**:

- `classes` → special plural, keep as "classes"
- `masses` → verb form, normalize to "mass"?
- `phases` → special plural, keep as "phases"

**Issue**: Can't determine with pure logic if word is special plural or verb

**Requires LLM**: Yes - needs to identify special plurals

---

### Case 3: Morphological Ambiguity

**Problem**: Same ending pattern, different morphological rules

**Examples**:

- `teaches` (verb) → `teach` (remove "s" from "ches")
- `reaches` (verb) → `reach` (remove "s" from "ches")
- `boxes` (noun) → `box` (remove "es")
- `classes` (noun) → `classes` (keep as-is)

**Issue**: Pure logic can't distinguish verb from noun

**Requires LLM**: Yes - needs morphological analysis

---

## ✅ Implementation Summary

**Approach**: Hybrid (Logic + LLM)

- Pure logic for clear cases (fast)
- LLM for ambiguous cases (accurate)
- Caching for performance
- Fallback for reliability

**Status**: Ready to implement
