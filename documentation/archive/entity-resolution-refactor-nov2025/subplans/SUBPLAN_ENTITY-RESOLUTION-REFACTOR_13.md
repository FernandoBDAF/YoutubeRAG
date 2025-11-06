# SUBPLAN: Type Consistency Rules

**Mother Plan**: PLAN_ENTITY-RESOLUTION-REFACTOR.md  
**Achievement Addressed**: Achievement 1.3 - Type Consistency Rules Implemented  
**Status**: In Progress  
**Created**: 2025-11-06 22:20 UTC  
**Estimated Effort**: 2-3 hours

---

## 🎯 Objective

Implement type consistency rules to handle type conflicts properly. Use weighted voting based on confidence and source count, prefer existing DB type for stability, flag conflicts for review, and prevent merging of incompatible types (PERSON vs ORG, PERSON vs TECHNOLOGY).

---

## 📋 What Needs to Be Created

### Files to Modify

1. **`business/agents/graphrag/entity_resolution.py`**:

   - Enhance `_determine_entity_type()` with weighted voting
   - Add type conflict detection
   - Add type compatibility checking
   - Prefer existing DB type when merging

2. **`business/stages/graphrag/entity_resolution.py`**:
   - Check type compatibility before merging
   - Flag type conflicts for review

---

## 🔧 Approach

### Step 1: Weighted Type Voting

- Calculate type score: `type_score = confidence × source_count`
- Select type with highest weighted score
- Handle ties by preferring existing DB type

### Step 2: Type Compatibility Rules

- Define incompatible type pairs:
  - PERSON vs ORG
  - PERSON vs TECHNOLOGY
  - (Add more as needed)
- Prevent merging if types are incompatible
- Flag for review

### Step 3: Integration

- Update `_determine_entity_type()` to use weighted voting
- Check type compatibility in `_choose_match()` or merge logic
- Log type conflicts for review

---

## ✅ Expected Results

- Better type assignment (weighted by confidence)
- Type conflicts detected and prevented
- Stable type selection (prefer existing)
- Flagged conflicts for manual review

---

**Status**: Ready to Execute  
**Next**: Implement weighted type voting and compatibility rules
