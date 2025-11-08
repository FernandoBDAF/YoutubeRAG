"""Sample PLAN file fixtures for testing LLM scripts."""


def get_sample_plan_content():
    """Return sample PLAN content with standard structure."""
    return """# PLAN: Test Feature

**Status**: In Progress  
**Created**: 2025-01-27 12:00 UTC  
**Goal**: Test feature implementation  
**Priority**: High

---

## 📝 Current Status & Handoff (For Pause/Resume)

**Last Updated**: 2025-01-27 12:00 UTC  
**Status**: In Progress

**Completed Achievements**: 2/5 (40%)

**Summary**:
- ✅ Achievement 0.1 Complete
- ✅ Achievement 0.2 Complete
- ⏳ Next: Achievement 1.1 (Next Task)

**When Resuming**:
1. Follow protocol
2. Read this section
3. Continue with Achievement 1.1

---

## 🎯 Desirable Achievements

### Priority 0: HIGH

**Achievement 0.1**: First Achievement
- Goal: First task
- Status: Complete

**Achievement 0.2**: Second Achievement
- Goal: Second task
- Status: Complete

### Priority 1: HIGH

**Achievement 1.1**: Next Task
- Goal: Next task to complete
- Status: Not Started

---

**Archive Location**: `documentation/archive/test-feature/`
"""


def get_minimal_plan_content():
    """Return minimal valid PLAN content."""
    return """# PLAN: Minimal Feature

**Status**: Planning  
**Created**: 2025-01-27 12:00 UTC  
**Goal**: Minimal feature  
**Priority**: Medium

---

## 🎯 Desirable Achievements

### Priority 0: HIGH

**Achievement 0.1**: First Task
- Goal: Complete first task

---

**Archive Location**: `documentation/archive/minimal-feature/`
"""


def get_plan_with_achievements():
    """Return PLAN content with multiple achievements."""
    return """# PLAN: Multi Achievement Feature

**Status**: In Progress  
**Created**: 2025-01-27 12:00 UTC  
**Goal**: Feature with multiple achievements  
**Priority**: High

---

## 📝 Current Status & Handoff (For Pause/Resume)

**Last Updated**: 2025-01-27 12:00 UTC  
**Status**: In Progress

**Completed Achievements**: 3/10 (30%)

**Summary**:
- ✅ Achievement 0.1 Complete
- ✅ Achievement 0.2 Complete
- ✅ Achievement 1.1 Complete
- ⏳ Next: Achievement 1.2 (Fourth Task)

---

## 🎯 Desirable Achievements

### Priority 0: HIGH

**Achievement 0.1**: First Achievement ✅
**Achievement 0.2**: Second Achievement ✅

### Priority 1: HIGH

**Achievement 1.1**: Third Achievement ✅
**Achievement 1.2**: Fourth Task
**Achievement 1.3**: Fifth Task

### Priority 2: MEDIUM

**Achievement 2.1**: Sixth Task
**Achievement 2.2**: Seventh Task

---

**Archive Location**: `documentation/archive/multi-achievement-feature/`
"""


def get_plan_with_handoff():
    """Return PLAN content with detailed handoff section."""
    return """# PLAN: Handoff Feature

**Status**: In Progress  
**Created**: 2025-01-27 12:00 UTC  
**Goal**: Feature with detailed handoff  
**Priority**: High

---

## 📝 Current Status & Handoff (For Pause/Resume)

**Last Updated**: 2025-01-27 14:00 UTC  
**Status**: In Progress

**Completed Achievements**: 5/8 (63%)

**Summary**:
- ✅ Achievement 0.1 Complete: First task done
- ✅ Achievement 0.2 Complete: Second task done
- ✅ Achievement 1.1 Complete: Third task done
- ✅ Achievement 1.2 Complete: Fourth task done
- ✅ Achievement 2.1 Complete: Fifth task done
- ⏳ Next: Achievement 2.2 (Sixth Task)

**When Resuming**:
1. Read this section
2. Review Subplan Tracking
3. Continue with Achievement 2.2
4. Create SUBPLAN for Achievement 2.2

**Context Preserved**: This section + Subplan Tracking = full context

---

## 🎯 Desirable Achievements

### Priority 0: HIGH

**Achievement 0.1**: First Task ✅
**Achievement 0.2**: Second Task ✅

### Priority 1: HIGH

**Achievement 1.1**: Third Task ✅
**Achievement 1.2**: Fourth Task ✅

### Priority 2: MEDIUM

**Achievement 2.1**: Fifth Task ✅
**Achievement 2.2**: Sixth Task
**Achievement 2.3**: Seventh Task

---

**Archive Location**: `documentation/archive/handoff-feature/`
"""


