# SUBPLAN: Metadata Tag System Documentation

**Mother Plan**: PLAN_FILE-MOVING-OPTIMIZATION.md  
**Achievement Addressed**: Achievement 1.2 (Metadata Tag System Documentation)  
**Status**: In Progress  
**Created**: 2025-01-27 22:30 UTC  
**Estimated Effort**: 1-2 hours

---

## 🎯 Objective

Document metadata tag system for virtual organization without physical file moves. This establishes the foundation for organizing files by metadata/tags rather than by physical directory structure, enabling future search tool to query files by metadata.

---

## 📋 What Needs to Be Created

### Files to Create

- `LLM/guides/METADATA-TAGS.md` - Metadata tag system documentation

### Files to Modify

- `LLM/templates/PLAN-TEMPLATE.md` - Add metadata section example
- `LLM/templates/SUBPLAN-TEMPLATE.md` - Add metadata section example
- `LLM/templates/EXECUTION_TASK-TEMPLATE.md` - Add metadata section example
- `LLM-METHODOLOGY.md` - Reference metadata system, explain virtual organization

---

## 🎯 Approach

### Step 1: Create METADATA-TAGS.md Guide

**Content Structure**:
1. **Purpose**: Why metadata tags exist (virtual organization)
2. **Tag Format**: YAML frontmatter or inline tags
3. **Standard Tags**: 
   - type (PLAN, SUBPLAN, EXECUTION_TASK, etc.)
   - status (active, complete, paused, archived)
   - plan (parent PLAN name)
   - achievement (achievement number)
   - priority (0-4)
   - created (date)
   - completed (date, if applicable)
4. **Tag Conventions**: Naming rules, value formats
5. **Usage Examples**: Sample files with metadata
6. **Update Process**: When to add/update tags
7. **Future**: How search tool will use tags

### Step 2: Update Templates with Metadata Examples

**PLAN-TEMPLATE.md**:
- Add metadata section at top of template
- Show example tags (type, status, priority, created)
- Explain which tags to use

**SUBPLAN-TEMPLATE.md**:
- Add metadata section
- Show example tags (type, status, plan, achievement, created)
- Link to METADATA-TAGS.md guide

**EXECUTION_TASK-TEMPLATE.md**:
- Add metadata section
- Show example tags (type, status, plan, achievement, iteration, created)
- Link to METADATA-TAGS.md guide

### Step 3: Integrate into LLM-METHODOLOGY.md

**Add Section**: "Metadata Tags and Virtual Organization"
- Explain concept of virtual organization
- Reference METADATA-TAGS.md guide
- Link to file index (works together)
- Note that full value realized with search tool (advanced plan)

### Step 4: Verify Integration

1. Check all deliverables exist
2. Verify metadata examples in templates
3. Ensure LLM-METHODOLOGY.md references system
4. Test that guidance is clear

---

## ✅ Expected Results

### Deliverables

1. **LLM/guides/METADATA-TAGS.md**:
   - Complete metadata tag documentation
   - Standard tags defined
   - Usage examples
   - Tag conventions

2. **Updated Templates**:
   - PLAN-TEMPLATE.md with metadata section
   - SUBPLAN-TEMPLATE.md with metadata section
   - EXECUTION_TASK-TEMPLATE.md with metadata section

3. **Updated LLM-METHODOLOGY.md**:
   - Metadata system referenced
   - Virtual organization concept explained
   - Links to METADATA-TAGS.md

### Success Criteria

- [ ] Metadata tag system documented
- [ ] Standard tags defined (type, status, plan, achievement, priority)
- [ ] Templates include metadata examples
- [ ] LLM-METHODOLOGY.md references system
- [ ] Guidance is clear and actionable

---

## 🧪 Tests

### Test 1: Guide Completeness

```bash
# Verify guide exists
ls -1 LLM/guides/METADATA-TAGS.md

# Check standard tags documented
grep -i "type\|status\|plan\|achievement\|priority" LLM/guides/METADATA-TAGS.md | wc -l
```

### Test 2: Template Updates

```bash
# Verify templates have metadata sections
grep -i "metadata" LLM/templates/PLAN-TEMPLATE.md
grep -i "metadata" LLM/templates/SUBPLAN-TEMPLATE.md
grep -i "metadata" LLM/templates/EXECUTION_TASK-TEMPLATE.md
```

### Test 3: Methodology Integration

```bash
# Verify LLM-METHODOLOGY.md references metadata
grep -i "metadata\|virtual organization" LLM-METHODOLOGY.md
```

---

## 📝 Notes

- **Note from PLAN**: Metadata tags are most useful when search tool exists (see advanced plan). This achievement documents the system; full value realized when search tool can query by tags.
- **Keep it simple**: Basic tag system is sufficient for quick wins. Advanced features can come with search tool.
- **Focus on standards**: Define standard tags that will be used across all files.

---

**Status**: Ready to Execute  
**Next**: Create EXECUTION_TASK and begin implementation

