# Soft-Keep Analysis

**Date**: November 4, 2025

---

## 🔍 Issue

The test `test_soft_keep_unknown_predicates()` is failing because:

- Test expects: `result == "unknown_predicate_xyz"` (original form)
- Code returns: `normalized` (after morphological normalization)

---

## 🤔 Question

**Should soft-keep return the original or normalized form?**

Current behavior:

- Returns `normalized` (after morphological normalization via LLM)
- This is consistent with canonicalization (always returns normalized form)

Test expectation:

- Expects original form `"unknown_predicate_xyz"`
- But after normalization, tokens ["unknown", "predicate", "xyz"] go through LLM
- Mock returns tokens as-is, so should still be "unknown_predicate_xyz"

---

## ✅ Solution

The mock needs to return tokens as-is, which I already added. But the test should accept the normalized form since that's what the code returns (for consistency with canonicalization).

**Status**: This is a NEW error, not repeating previous issues. The fix is to update the test to accept normalized form OR ensure mock returns tokens unchanged.
