# Metadata Tags System

**Purpose**: Enable virtual organization of files by metadata rather than physical directory structure  
**Created**: 2025-01-27  
**Status**: Active  
**Related**: `LLM/index/FILE-INDEX.md`, `PLAN_FILE-MOVING-ADVANCED-OPTIMIZATION.md`

---

## 🎯 What This Is

A **metadata tag system** that enables organizing and finding files by their properties (type, status, plan, priority) rather than their physical location. This eliminates the need for physical file moves while maintaining logical organization.

**Key Concept**: **Virtual Organization**
- Files stay in root directory (no physical moves)
- Organized by metadata tags (type, status, plan, etc.)
- Search tool queries by tags (see advanced optimization plan)
- No reference updates needed when organizing

---

## 📊 Standard Tags

### Core Tags (All Files)

**type**: File type
- Values: `PLAN`, `SUBPLAN`, `EXECUTION_TASK`, `EXECUTION_ANALYSIS`, `GRAMMAPLAN`
- Required: Yes
- Example: `type: PLAN`

**status**: Current status
- Values: `active`, `complete`, `paused`, `archived`, `abandoned`
- Required: Yes
- Example: `status: active`

**created**: Creation date
- Format: `YYYY-MM-DD` or `YYYY-MM-DD HH:MM UTC`
- Required: Yes
- Example: `created: 2025-01-27`

### Plan-Specific Tags

**plan**: Parent PLAN name (for SUBPLAN, EXECUTION_TASK)
- Format: PLAN file name without extension
- Required: For SUBPLANs and EXECUTION_TASKs
- Example: `plan: FILE-MOVING-OPTIMIZATION`

**achievement**: Achievement number (for SUBPLAN, EXECUTION_TASK)
- Format: `X.Y` (priority.number)
- Required: For SUBPLANs and EXECUTION_TASKs
- Example: `achievement: 1.1`

**priority**: Achievement priority (for PLANs)
- Format: `0`, `1`, `2`, `3`, `4`
- Required: For PLANs
- Example: `priority: 0`

### Optional Tags

**completed**: Completion date
- Format: `YYYY-MM-DD` or `YYYY-MM-DD HH:MM UTC`
- Required: For completed work
- Example: `completed: 2025-01-27`

**archived**: Archive location
- Format: Path to archive directory
- Required: For archived files
- Example: `archived: documentation/archive/file-moving-optimization-nov2025/`

**category**: Category (for EXECUTION_ANALYSIS)
- Values: `bug-analysis`, `methodology-review`, `implementation-review`, `process-analysis`, `planning-strategy`
- Required: For EXECUTION_ANALYSIS files
- Example: `category: process-analysis`

**iteration**: Execution iteration (for EXECUTION_TASK)
- Format: Number (1, 2, 3, etc.)
- Required: For EXECUTION_TASKs
- Example: `iteration: 1`

---

## 📝 Tag Format

### YAML Frontmatter (Recommended)

```yaml
---
type: PLAN
status: active
priority: 0
created: 2025-01-27
plan: FILE-MOVING-OPTIMIZATION
---

# PLAN: File Moving Optimization
...
```

### Inline Tags (Alternative)

```markdown
**Type**: PLAN  
**Status**: Active  
**Priority**: 0  
**Created**: 2025-01-27  
**Plan**: FILE-MOVING-OPTIMIZATION

# PLAN: File Moving Optimization
...
```

**Recommendation**: Use inline tags for now (already present in templates). YAML frontmatter can be added later if search tool requires it.

---

## 💡 Usage Examples

### PLAN Example

```markdown
**Type**: PLAN  
**Status**: Active  
**Priority**: 0  
**Created**: 2025-01-27  
**Goal**: Implement file moving optimizations

# PLAN: File Moving Optimization
...
```

**Tags**:
- type: PLAN
- status: active
- priority: 0
- created: 2025-01-27

### SUBPLAN Example

```markdown
**Type**: SUBPLAN  
**Status**: Complete  
**Plan**: FILE-MOVING-OPTIMIZATION  
**Achievement**: 1.1  
**Created**: 2025-01-27  
**Completed**: 2025-01-27

# SUBPLAN: File Index System Creation
...
```

**Tags**:
- type: SUBPLAN
- status: complete
- plan: FILE-MOVING-OPTIMIZATION
- achievement: 1.1
- created: 2025-01-27
- completed: 2025-01-27

### EXECUTION_TASK Example

```markdown
**Type**: EXECUTION_TASK  
**Status**: Complete  
**Plan**: FILE-MOVING-OPTIMIZATION  
**Achievement**: 1.1  
**Iteration**: 1  
**Created**: 2025-01-27  
**Completed**: 2025-01-27

# EXECUTION_TASK: File Index System Creation
...
```

**Tags**:
- type: EXECUTION_TASK
- status: complete
- plan: FILE-MOVING-OPTIMIZATION
- achievement: 1.1
- iteration: 1
- created: 2025-01-27
- completed: 2025-01-27

### EXECUTION_ANALYSIS Example

```markdown
**Type**: EXECUTION_ANALYSIS  
**Status**: Active  
**Category**: process-analysis  
**Created**: 2025-01-27

# EXECUTION_ANALYSIS: File Moving Performance Analysis
...
```

**Tags**:
- type: EXECUTION_ANALYSIS
- status: active
- category: process-analysis
- created: 2025-01-27

---

## 🔍 Virtual Organization Concept

### Traditional Organization (Physical)

```
Root/
├── active-plans/
│   └── PLAN_FILE-MOVING-OPTIMIZATION.md
├── archived-plans/
│   └── PLAN_OLD-FEATURE.md
└── subplans/
    └── SUBPLAN_FILE-MOVING-OPTIMIZATION_11.md
```

**Issues**:
- Requires physical file moves
- Reference updates needed when moving
- Directory structure is rigid
- Hard to reorganize

### Virtual Organization (Metadata)

```
Root/
├── PLAN_FILE-MOVING-OPTIMIZATION.md (status: active)
├── PLAN_OLD-FEATURE.md (status: archived)
└── SUBPLAN_FILE-MOVING-OPTIMIZATION_11.md (status: active, plan: FILE-MOVING-OPTIMIZATION)
```

**Benefits**:
- No physical file moves
- No reference updates
- Flexible organization (query by any tag)
- Easy to reorganize (just change tag values)

### How It Works

1. **Add Metadata Tags**: Each file has metadata (type, status, plan, etc.)
2. **Query by Tags**: Search tool finds files matching criteria
3. **No Physical Moves**: Files stay in root, organized virtually
4. **Change Organization**: Just update tags, no file moves

**Example Queries** (with future search tool):
- Find all active PLANs: `search --type PLAN --status active`
- Find all SUBPLANs for FILE-MOVING-OPTIMIZATION: `search --type SUBPLAN --plan FILE-MOVING-OPTIMIZATION`
- Find completed work: `search --status complete`

---

## 🔄 Tag Update Process

### When to Add Tags

- **At creation**: Add type, status, created tags
- **At completion**: Add completed tag, update status to complete
- **At archiving**: Add archived tag, update status to archived
- **When organizing**: Update tags as needed (no file moves)

### How to Update Tags

**Manual** (for quick wins):
1. Open file
2. Update metadata section at top
3. Save file
4. Tags updated (no physical moves)

**Automated** (with search tool, see advanced plan):
- Search tool reads tags automatically
- No manual index update needed
- Tags are source of truth

---

## 📖 Integration with File Index

**File Index** (`LLM/index/FILE-INDEX.md`):
- Catalog of files organized by type
- Manual maintenance (for quick wins)

**Metadata Tags**:
- Tags on files themselves
- Virtual organization
- No maintenance needed (tags are in files)

**Together**:
- File index: Quick discovery by type
- Metadata tags: Rich organization by any property
- Search tool (future): Query files by tags, makes index obsolete

---

## 🚀 Future: Search Tool

**Planned** (see `PLAN_FILE-MOVING-ADVANCED-OPTIMIZATION.md`):

```bash
# Search by type
python LLM/scripts/index/search_files.py --type PLAN

# Search by status
python LLM/scripts/index/search_files.py --status active

# Search by plan
python LLM/scripts/index/search_files.py --plan FILE-MOVING-OPTIMIZATION

# Combined search
python LLM/scripts/index/search_files.py --type SUBPLAN --plan FILE-MOVING-OPTIMIZATION --status complete
```

**Current**: Manual tagging establishes the foundation. Search tool will read these tags automatically.

---

## 📖 Related Documentation

- `LLM/index/FILE-INDEX.md` - File index for discovery
- `LLM-METHODOLOGY.md` - Methodology reference
- `PLAN_FILE-MOVING-ADVANCED-OPTIMIZATION.md` - Search tool implementation

---

**Version**: 1.0  
**Status**: Active  
**Next**: Search tool implementation (advanced plan)


