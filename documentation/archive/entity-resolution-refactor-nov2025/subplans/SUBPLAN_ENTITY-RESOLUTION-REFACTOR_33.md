# SUBPLAN: Token Budget Management

**Mother Plan**: PLAN_ENTITY-RESOLUTION-REFACTOR.md  
**Achievement Addressed**: Achievement 3.3 - Token Budget Management Implemented  
**Status**: In Progress  
**Created**: 2025-11-06 23:30 UTC  
**Estimated Effort**: 2-3 hours

---

## 🎯 Objective

Implement configurable token budget management for LLM input. Since we're using cheap models (gpt-4o-mini), this should be optional and disabled by default to preserve quality. When enabled, use smart truncation that prioritizes informative sentences rather than just cutting off.

---

## 📋 What Needs to Be Created

### Files to Modify

1. **`core/config/graphrag.py`**:
   - Add `max_input_tokens_per_entity` parameter (default: None/disabled)

2. **`business/agents/graphrag/entity_resolution.py`**:
   - Add `max_input_tokens` parameter to constructor
   - Implement `_estimate_tokens()` method
   - Implement `_truncate_descriptions_smartly()` method
   - Use smart truncation before LLM call if enabled

---

## 🔧 Approach

### Step 1: Add Configuration

- Add `max_input_tokens_per_entity` to EntityResolutionConfig (default: None)
- Pass to agent constructor

### Step 2: Token Estimation

- Simple estimation: ~4 characters per token (rough approximation)
- Or use tiktoken if available (more accurate)

### Step 3: Smart Truncation

- If token budget enabled and exceeded:
  - Split into sentences
  - Rank by informativeness (length, word count, unique terms)
  - Keep top sentences until within budget
  - Preserve sentence order when possible

### Step 4: Integration

- Truncate combined_descriptions before LLM call if budget enabled
- Log when truncation occurs for monitoring

---

## ✅ Expected Results

- Configurable token budget (disabled by default)
- Smart truncation preserves important information
- No quality loss when disabled (default)
- Easy to tune via configuration

---

**Status**: Ready to Execute  
**Next**: Implement configurable token budget with smart truncation

