# LLM Methodology Scripts

**Purpose**: Scripts for the LLM Development Methodology  
**Status**: Active  
**Created**: 2025-11-07

---

## 📁 Directory Structure

Scripts are organized by domain for better discoverability and maintainability:

```
LLM/scripts/
├── validation/     # Validation and compliance checking scripts
├── generation/     # Prompt and content generation scripts
├── archiving/      # Archiving and file management scripts
└── README.md       # This file
```

---

## 🔍 Scripts by Domain

### Validation Scripts (`validation/`)

**Purpose**: Validate methodology compliance and enforce rules

**Scripts**:

1. **check_plan_size.py**

   - Validates PLAN size limits (600 lines / 32 hours)
   - Usage: `python LLM/scripts/validation/check_plan_size.py @PLAN_FEATURE.md`
   - Exit code 1 if limits exceeded

2. **check_execution_task_size.py**

   - Validates EXECUTION_TASK size limits (200 lines)
   - Usage: `python LLM/scripts/validation/check_execution_task_size.py @EXECUTION_TASK_FILE.md`
   - Exit code 1 if limit exceeded

3. **validate_achievement_completion.py**

   - Validates achievement completion before marking complete
   - Usage: `python LLM/scripts/validation/validate_achievement_completion.py @PLAN_FILE.md --achievement 1.1`
   - Checks: SUBPLAN exists, EXECUTION_TASK exists, deliverables exist

4. **validate_execution_start.py**

   - Validates prerequisites before starting EXECUTION_TASK
   - Usage: `python LLM/scripts/validation/validate_execution_start.py @EXECUTION_TASK_FILE.md`
   - Checks: SUBPLAN exists, parent PLAN exists, archive location exists

5. **validate_mid_plan.py**

   - Validates PLAN compliance at mid-point
   - Usage: `python LLM/scripts/validation/validate_mid_plan.py @PLAN_FILE.md`
   - Checks: Statistics accuracy, SUBPLAN registration, archive compliance

6. **validate_registration.py**

   - Validates component registration in PLAN/SUBPLAN
   - Usage: `python LLM/scripts/validation/validate_registration.py @PLAN_FILE.md`
   - Checks: All components registered, no orphaned files

7. **validate_plan_compliance.py** (if exists)

   - Validates PLAN compliance with methodology
   - Usage: `python LLM/scripts/validation/validate_plan_compliance.py @PLAN_FILE.md`

8. **validate_references.py** (if exists)
   - Validates references in documentation
   - Usage: `python LLM/scripts/validation/validate_references.py`

---

### Generation Scripts (`generation/`)

**Purpose**: Generate prompts and content automatically

**Scripts**:

1. **generate_prompt.py**

   - Generates methodology-compliant prompts for LLM execution
   - Usage: `python LLM/scripts/generation/generate_prompt.py --next --clipboard @PLAN_FEATURE.md`
   - Options: `--next`, `--achievement X.Y`, `--clipboard`
   - Auto-detects context boundaries and validation scripts

2. **generate_pause_prompt.py**

   - Generates prompt to pause a PLAN
   - Usage: `python LLM/scripts/generation/generate_pause_prompt.py @PLAN_FEATURE.md --clipboard`
   - Includes checklist for pausing properly

3. **generate_resume_prompt.py**

   - Generates prompt to resume a paused PLAN
   - Usage: `python LLM/scripts/generation/generate_resume_prompt.py @PLAN_FEATURE.md --clipboard`
   - Includes pre-resume checklist from IMPLEMENTATION_RESUME.md

4. **generate_verify_prompt.py**
   - Generates prompt to verify PLAN status and fix inconsistencies
   - Usage: `python LLM/scripts/generation/generate_verify_prompt.py @PLAN_FEATURE.md --clipboard`
   - Runs validate_mid_plan.py and provides fix instructions

---

### Archiving Scripts (`archiving/`)

**Purpose**: Archive completed work immediately

**Scripts**:

1. **archive_completed.py**
   - Archives completed SUBPLANs and EXECUTION_TASKs immediately
   - Usage: `python LLM/scripts/archiving/archive_completed.py @SUBPLAN_FILE.md`
   - Auto-detects archive location from PLAN
   - Creates archive structure if needed

---

## 🚀 Quick Reference

### Most Common Commands

**Generate prompt for next achievement**:

```bash
python LLM/scripts/generation/generate_prompt.py @PLAN_FEATURE.md --next --clipboard
```

**Pause PLAN**:

```bash
python LLM/scripts/generation/generate_pause_prompt.py @PLAN_FEATURE.md --clipboard
```

**Resume PLAN**:

```bash
python LLM/scripts/generation/generate_resume_prompt.py @PLAN_FEATURE.md --clipboard
```

**Verify PLAN status**:

```bash
python LLM/scripts/generation/generate_verify_prompt.py @PLAN_FEATURE.md --clipboard
```

**Validate achievement before marking complete**:

```bash
python LLM/scripts/validation/validate_achievement_completion.py @PLAN_FEATURE.md --achievement 1.1
```

**Archive completed component**:

```bash
python LLM/scripts/archiving/archive_completed.py @SUBPLAN_FEATURE_XX.md
```

**Check PLAN size**:

```bash
python LLM/scripts/validation/check_plan_size.py @PLAN_FEATURE.md
```

---

## 📝 Adding New Scripts

**Guidelines**:

1. **Choose Domain**: Determine which domain the script belongs to

   - Validation: Compliance checking, rule enforcement
   - Generation: Creating prompts, content, templates
   - Archiving: File management, archiving workflows

2. **Place Script**: Move script to appropriate domain directory

   ```bash
   mv new_script.py LLM/scripts/[domain]/
   ```

3. **Update README**: Add script to this README with:

   - Purpose
   - Usage example
   - Key options

4. **Update References**: If script is referenced in documentation, update paths

---

## 🔗 Related Documentation

- **Methodology Overview**: `LLM-METHODOLOGY.md`
- **Protocols**: `LLM/protocols/`
- **Templates**: `LLM/templates/`
- **Guides**: `LLM/guides/`

---

**Last Updated**: 2025-11-07
