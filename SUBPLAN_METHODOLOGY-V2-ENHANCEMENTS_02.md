# SUBPLAN: Automated Prompt Generation Tool

**Mother Plan**: PLAN_METHODOLOGY-V2-ENHANCEMENTS.md  
**Achievement Addressed**: Achievement 0.2 (Automated Prompt Generation Tool)  
**Status**: In Progress  
**Created**: 2025-11-07  
**Estimated Effort**: 3-4 hours

---

## 🎯 Objective

Build `LLM/scripts/generate_prompt.py` - an automated script that generates ideal prompts for any achievement in <5 seconds. The script will parse PLAN files, extract achievements, calculate context boundaries, detect existing validation scripts, and fill prompt templates with accurate values. This eliminates manual prompt creation (impractical per user) and ensures consistent high-quality prompts for all future work.

---

## 📋 What Needs to Be Created

### Files to Create

1. **LLM/scripts/generate_prompt.py** (300-400 lines):
   - Main script with CLI interface
   - PLAN parsing functions
   - Context calculation functions
   - Template system
   - Output formatting

### Functions to Implement

**Core Functions**:

```python
parse_plan_file(plan_path: Path) -> PlanContext
    # Extract: feature name, achievements, current state, archive location

find_next_achievement(feature_name: str, achievements: List) -> Achievement
    # Detect: First achievement without SUBPLAN file

calculate_context_lines(plan_content: str, achievement: Achievement) -> int
    # Calculate: Lines in achievement section + handoff section

detect_validation_scripts() -> List[str]
    # Detect: Which validation scripts exist in LLM/scripts/

fill_template(template: str, context: dict) -> str
    # Fill: Template placeholders with actual values
```

**Supporting Functions**:

```python
extract_achievements(content: str) -> List[Achievement]
    # Parse: "**Achievement X.Y**: Title" patterns

calculate_section_lines(content: str, section_name: str) -> int
    # Count: Lines in specific section

format_deliverables(deliverables: List[str]) -> str
    # Format: As ls -1 verification commands

format_subplan_number(achievement_num: str) -> str
    # Format: "1.1" → "11" for SUBPLAN_XX
```

### Templates to Embed

**Template 1**: ACHIEVEMENT_EXECUTION_TEMPLATE

- Based on ideal prompt structure
- Placeholders: {feature}, {achievement_num}, {context_budget}, etc.
- All sections: Context Boundaries, Steps, Validation, DO NOTs

**Template 2**: CONTINUE_EXECUTION_TEMPLATE

- For continuing active EXECUTION_TASK
- Context: Read THIS EXECUTION only

**Template 3**: NEXT_ACHIEVEMENT_TEMPLATE

- For starting next in active PLAN
- Context: Current status + next achievement

### Tests Required

- Test 1: Generate prompt for Achievement 1.1, verify structure
- Test 2: Generate prompt for Achievement 0.1, verify context calc
- Test 3: CLI flags work (--help, --next, --achievement, --clipboard)

---

## 📝 Approach

**Strategy**: Build incrementally, test each phase

**Method**:

### Phase 1: Core Parsing (1h)

**Goal**: Extract structured data from PLAN files

**Implementation**:

1. Read PLAN file content
2. Extract feature name from filename
3. Parse achievements using regex: `\*\*Achievement (\d+\.\d+)\*\*:(.+)`
4. Extract achievement details (goal, effort, priority)
5. Find next achievement (check for SUBPLAN files)
6. Calculate context lines (achievement section + handoff section)

**Test**: Parse current PLAN, verify extracts 10 achievements correctly

### Phase 2: Template System (1.5h)

**Goal**: Embed prompt templates and fill with values

**Implementation**:

1. Define ACHIEVEMENT_EXECUTION_TEMPLATE (based on ideal prompt)
2. Create fill_template() function
3. Handle all placeholders: {feature}, {achievement_num}, {context_budget}, {deliverables}, etc.
4. Detect validation scripts (which exist in LLM/scripts/)
5. Format verification commands (ls -1 per deliverable)

**Test**: Fill template with test data, verify output structure

### Phase 3: CLI & Output (0.5h)

**Goal**: Command-line interface with argparse

**Implementation**:

1. argparse setup: file argument, --next flag, --achievement flag, --clipboard flag
2. Main workflow: Parse file → Detect action → Generate prompt → Output
3. Clipboard support: Use pyperclip if available, fallback to stdout
4. Help text with examples

**Test**: Run with --help, verify usage clear

### Phase 4: Integration Testing (0.5-1h)

**Goal**: Validate script produces ideal prompts

**Implementation**:

1. Test: `generate_prompt.py @PLAN_METHODOLOGY-V2-ENHANCEMENTS.md --next`
2. Verify: Output has all required sections
3. Test: `generate_prompt.py @PLAN_METHODOLOGY-V2-ENHANCEMENTS.md --achievement 1.1`
4. Verify: Context boundaries accurate
5. Compare: Generated vs ideal prompt structure (should match!)

**Success Criteria**: Generated prompt indistinguishable from ideal manual prompt

---

## ✅ Expected Results

### Functional Changes

1. **Script Exists**: LLM/scripts/generate_prompt.py working
2. **One Command**: Generates complete prompt in 5 seconds
3. **Quality**: Output matches ideal prompt structure
4. **Tested**: Verified with current PLAN

### Observable Outcomes

1. **Ease of Use**: `python script.py @PLAN --next --clipboard` → perfect prompt in clipboard
2. **Time Savings**: 8 minutes manual → 5 seconds automated (96% reduction)
3. **Consistency**: Every prompt has all safeguards
4. **Validation**: Generator itself can be validated (run it, check output)

### Deliverables

- LLM/scripts/generate_prompt.py (300-400 lines)
- SUBPLAN with approach documented
- EXECUTION_TASK with learnings (<200 lines)
- Tested and working for remaining achievements

---

## 📊 Success Criteria

**This Subplan is Complete When**:

- [ ] generate_prompt.py exists and runs
- [ ] Script parses PLAN files correctly
- [ ] Script generates prompts matching ideal structure
- [ ] All CLI flags work (--next, --achievement, --clipboard)
- [ ] Tested with current PLAN (generates for Achievement 1.1)
- [ ] EXECUTION_TASK complete with learnings
- [ ] Files archived immediately
- [ ] PLAN updated with statistics

---

**Ready to Execute**: Create EXECUTION_TASK and begin building  
**Reference**: EXECUTION_ANALYSIS_PROMPT-AUTOMATION-STRATEGY.md (implementation details)  
**Mother PLAN**: PLAN_METHODOLOGY-V2-ENHANCEMENTS.md
