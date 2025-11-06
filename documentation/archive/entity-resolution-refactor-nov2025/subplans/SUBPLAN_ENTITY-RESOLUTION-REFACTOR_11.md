# SUBPLAN: Blocking Strategy Enhancement

**Mother Plan**: PLAN_ENTITY-RESOLUTION-REFACTOR.md  
**Achievement Addressed**: Achievement 1.1 - Blocking Strategy Implemented  
**Status**: In Progress  
**Created**: 2025-11-06 22:00 UTC  
**Estimated Effort**: 2-3 hours

---

## 🎯 Objective

Enhance the existing blocking strategy (from Achievement 0.1) by adding optional phonetic keys (Soundex/Metaphone) for better matching of names with different spellings. The current blocking keys (normalized, alnum-only, acronym) are already implemented, but phonetic keys can improve recall for names like "Smith" and "Smyth".

---

## 📋 What Needs to Be Created

### Files to Modify

1. **`business/agents/graphrag/entity_resolution.py`**:
   - Enhance `_blocking_keys()` to optionally add Soundex/Metaphone keys
   - Use `jellyfish` library if available (already in requirements for metaphone)

### Dependencies

- `jellyfish` library (already in requirements.txt from predicate mapping)

---

## 🔧 Approach

### Step 1: Add Phonetic Key Generation

- Add Soundex/Metaphone support to `_blocking_keys()`
- Use `jellyfish` library if available (graceful degradation if not)
- Add phonetic keys to blocking keys list
- Test with names like "Smith" vs "Smyth"

### Step 2: Update Candidate Search

- Ensure candidate search can use phonetic keys
- Update `_find_db_candidates()` if needed (should work with existing query)

---

## 🧪 Tests Required

1. **`test_blocking_keys_with_phonetic`**:
   - "Smith" should generate Soundex key
   - "Smyth" should generate same Soundex key as "Smith"
   - Test Metaphone if available

---

## ✅ Expected Results

- Enhanced blocking with phonetic keys
- Better recall for phonetically similar names
- Graceful degradation if phonetic libraries unavailable
- No regression in existing functionality

---

**Status**: Ready to Execute  
**Next**: Enhance \_blocking_keys() with phonetic support
