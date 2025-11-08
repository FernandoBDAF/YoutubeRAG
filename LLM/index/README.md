# File Index System

**Purpose**: Fast file discovery for methodology files without knowing exact location  
**Created**: 2025-01-27  
**Status**: Active

---

## 🎯 What This Is

A centralized catalog of all methodology files (PLANs, SUBPLANs, scripts, templates, protocols, guides) organized by type for quick discovery.

**Problem Solved**: Instead of searching through directories or grepping for files, check the index to quickly locate any methodology file.

---

## 📖 How to Use

### Quick Discovery

1. Open `FILE-INDEX.md`
2. Use Cmd+F (Mac) or Ctrl+F (Windows/Linux) to search for:
   - File name (e.g., "START_POINT")
   - File type (e.g., "protocol", "template", "script")
   - Purpose (e.g., "validation", "archiving", "generation")
3. Navigate to file location shown in index

### Common Queries

**"Where is the START_POINT protocol?"**
→ Search "START_POINT" in FILE-INDEX.md
→ Find: `LLM/protocols/IMPLEMENTATION_START_POINT.md`

**"What validation scripts exist?"**
→ Search "validation" in FILE-INDEX.md
→ Find: All validation scripts in `LLM/scripts/validation/`

**"Where are the templates?"**
→ Look in "Templates" section
→ Find: `LLM/templates/`

---

## 🔄 Update Process

**When to Update**:
- New files added to LLM/ directory
- Files moved or renamed
- New scripts, templates, or protocols created
- After archiving PLANs (update active counts)

**How to Update** (Manual):
1. Open `FILE-INDEX.md`
2. Add new files to appropriate section
3. Update summary statistics (file counts)
4. Update "Last Updated" date
5. Keep sections organized

**Time**: 2-5 minutes per update

**Frequency**: Weekly or when significant changes occur

---

## 📊 Index Structure

FILE-INDEX.md is organized by file type:

1. **Summary Statistics**: Counts by type
2. **Active Plans**: PLANs in root directory
3. **Active SUBPLANs**: SUBPLANs in root
4. **Active EXECUTION_TASKs**: EXECUTION_TASKs in root
5. **Scripts**: Organized by domain (archiving/, generation/, validation/)
6. **Templates**: PLAN, SUBPLAN, EXECUTION_TASK, etc.
7. **Protocols**: START_POINT, END_POINT, RESUME, etc.
8. **Guides**: Focus rules, context management, etc.
9. **Documentation**: README, QUICK-START, etc.
10. **Archived Work**: Reference to documentation/archive/

---

## 🚀 Quick Start

**Finding a file? Start here**:

1. Open `FILE-INDEX.md`
2. Cmd+F / Ctrl+F for keyword
3. Navigate to location

**Time**: <30 seconds to find any file

---

## 🔮 Future Enhancements

**Planned** (see `PLAN_FILE-MOVING-ADVANCED-OPTIMIZATION.md`):
- Automated search tool (`LLM/scripts/index/search_files.py`)
- Auto-update mechanism (no manual updates needed)
- Search by metadata/tags
- Search by content (full-text search)

**Current**: Manual index, manual updates (good enough for quick wins)

---

## 📖 Related Documentation

- `LLM-METHODOLOGY.md` - Main methodology document
- `LLM/guides/FOCUS-RULES.md` - Context management
- `PLAN_FILE-MOVING-OPTIMIZATION.md` - File moving optimization (this achievement)
- `PLAN_FILE-MOVING-ADVANCED-OPTIMIZATION.md` - Advanced search tool

---

**Index Version**: 1.0  
**Maintained By**: Manual updates  
**Next Version**: Automated with search tool (see advanced optimization plan)


