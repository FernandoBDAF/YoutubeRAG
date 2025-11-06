# SUBPLAN: Multi-Resolution Louvain Implementation

**Mother Plan**: PLAN_COMMUNITY-DETECTION-REFACTOR.md  
**Achievement Addressed**: Achievement 3.1 - Multi-Resolution Louvain Implemented  
**Status**: In Progress  
**Created**: 2025-11-06 22:35 UTC  
**Estimated Effort**: 4-5 hours

---

## 🎯 Objective

Implement multi-resolution Louvain detection to capture communities at different scales (macro themes and micro topics) by running Louvain at multiple resolution parameters and storing each as a separate level.

---

## 📋 What Needs to Be Created

### Files to Modify

1. **`business/agents/graphrag/community_detection.py`**:

   - Add multi-resolution detection logic
   - Run Louvain at multiple resolutions (default: 0.8, 1.0, 1.6)
   - Store each resolution as separate level
   - Allow entities to appear in multiple levels

2. **`business/stages/graphrag/community_detection.py`** (if needed):
   - Pass multi-resolution config to agent
   - Handle multi-level community results

### Files to Create

1. **`tests/business/agents/graphrag/test_community_detection_multires.py`**:
   - Test multi-resolution detection produces multiple levels
   - Test entities can appear in multiple levels
   - Test different resolutions produce different community scales

---

## 🔧 Approach

### Step 1: Add Multi-Resolution Configuration

- Read `GRAPHRAG_COMMUNITY_MULTIRES` environment variable
- Default: "1.0" (single resolution, backward compatible)
- Parse comma-separated resolutions (e.g., "0.8,1.0,1.6")
- Validate resolutions are positive floats

### Step 2: Implement Multi-Resolution Detection

- If multi-resolution enabled:
  1. Run Louvain at each resolution
  2. Store each resolution's communities as separate level
  3. Level 1 = first resolution, Level 2 = second resolution, etc.
  4. Allow entities to appear in multiple levels (multi-scale membership)
- If single resolution (default):
  - Use existing behavior (backward compatible)

### Step 3: Update Community Organization

- Modify `_organize_communities_by_level` to handle multi-resolution format
- Each resolution's communities stored at its level
- Entities can have multiple level memberships

### Step 4: Update Stage Integration

- Pass multi-resolution config from stage to agent
- Handle multi-level results in stage

---

## 🧪 Tests Required

### Unit Tests

1. **`test_multires_enabled_produces_multiple_levels`**:

   - Multi-resolution enabled → multiple levels in result
   - Each level has communities

2. **`test_multires_entities_appear_multiple_levels`**:

   - Same entity can appear in multiple levels
   - Multi-scale membership works

3. **`test_multires_different_scales`**:

   - Lower resolution (0.8) → larger communities
   - Higher resolution (1.6) → smaller communities

4. **`test_multires_single_resolution_backward_compatible`**:

   - Single resolution (1.0) → same behavior as before
   - Backward compatibility maintained

5. **`test_multires_configurable`**:
   - Custom resolutions via env var
   - Parsing works correctly

---

## ✅ Expected Results

### Functional Changes

- Multi-resolution detection enabled via config
- Multiple levels stored (one per resolution)
- Entities can appear in multiple levels
- Backward compatible (single resolution default)

### Observable Outcomes

- Running with multi-resolution → multiple levels in result
- Lower resolution → fewer, larger communities
- Higher resolution → more, smaller communities
- Same entity in multiple levels for hierarchical navigation

### Success Indicators

- All tests passing
- Multi-resolution produces 3 levels (for 0.8, 1.0, 1.6)
- Entities appear in multiple levels
- Backward compatibility maintained

---

## 🔗 Dependencies

- Achievement 0.1 (Stable Community IDs) - ✅ Complete
- Achievement 1.3 (Size Management) - ✅ Complete
- NetworkX Louvain algorithm - Available

---

## 📝 Execution Task Reference

- **EXECUTION_TASK_COMMUNITY-DETECTION-REFACTOR_03_01.md** - Implementation and testing

---

## 🎯 Notes

- Multi-resolution enables hierarchical navigation
- Lower resolution captures macro themes
- Higher resolution captures micro topics
- Entities can belong to multiple scales simultaneously
- Useful for different use cases (high-level overview vs detailed analysis)
