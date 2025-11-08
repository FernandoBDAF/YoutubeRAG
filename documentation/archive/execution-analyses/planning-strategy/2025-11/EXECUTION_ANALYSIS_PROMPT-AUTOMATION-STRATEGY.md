# EXECUTION_ANALYSIS: Prompt Automation Strategy

**Purpose**: Design automated prompt generation system  
**Date**: 2025-11-07  
**User Insight**: "Creating those prompts during implementation is not practical - how to automate?"  
**Goal**: Make high-quality prompts automatic and effortless

---

## 🎯 Problem Statement

**Current Reality**: Ideal prompts require:
- Reading PLAN to extract achievement details
- Calculating line counts for context boundaries
- Knowing which validation scripts exist
- Formatting with all required sections
- Customizing for tree level (PLAN vs SUBPLAN vs EXECUTION)

**User Insight**: This is **not practical** to do manually during implementation

**Solution Needed**: Automated prompt generation that produces ideal prompts in <5 seconds

---

## 📋 Automation Approaches (3 Options)

### Option 1: Command-Line Script (Most Practical) ⭐

**Concept**: Single command generates complete prompt

**Usage**:
```bash
# Generate prompt for next achievement
python LLM/scripts/generate_prompt.py @PLAN_METHODOLOGY-V2-ENHANCEMENTS.md --next

# Generate prompt for specific achievement
python LLM/scripts/generate_prompt.py @PLAN_METHODOLOGY-V2-ENHANCEMENTS.md --achievement 0.1

# Generate prompt to continue EXECUTION_TASK
python LLM/scripts/generate_prompt.py @EXECUTION_TASK_METHODOLOGY-V2-ENHANCEMENTS_01_01.md --continue

# Output to clipboard (for easy paste)
python LLM/scripts/generate_prompt.py @PLAN_X.md --next --clipboard
```

**Output**: Complete prompt (like ideal example) ready to paste into Cursor

**Advantages**:
- ✅ Fast: 1-2 seconds to generate
- ✅ Accurate: Reads actual PLAN, no manual errors
- ✅ Consistent: Same quality every time
- ✅ Context-aware: Calculates line counts automatically
- ✅ Easy integration: Single command

**Implementation Complexity**: Medium (2-3 hours to build)

---

### Option 2: Interactive Menu System (Most User-Friendly)

**Concept**: Interactive menu guides you through prompt generation

**Usage**:
```bash
python LLM/scripts/prompt_helper.py

> Welcome to LLM Prompt Generator
> 
> What would you like to do?
> 1. Start new PLAN
> 2. Resume paused PLAN
> 3. Execute next achievement in active PLAN
> 4. Continue active SUBPLAN
> 5. Continue active EXECUTION_TASK
> 
> Choice: 3
>
> Select PLAN:
> 1. PLAN_METHODOLOGY-V2-ENHANCEMENTS.md (10 achievements, 0% complete)
> 2. PLAN_ENTITY-RESOLUTION-REFACTOR.md (17/31 complete, paused)
> 
> Choice: 1
>
> Next achievement is: 0.1 (Archive Failed GrammaPlan, 2-3h)
> Context: 75 lines (Achievement section + handoff)
>
> Generate prompt? [Y/n]: Y
>
> ✅ Prompt generated! Copied to clipboard.
> 
> Paste into Cursor to execute Achievement 0.1.
```

**Advantages**:
- ✅ User-friendly: No need to remember commands
- ✅ Safe: Shows what will happen before generating
- ✅ Discoverable: Menu shows all options
- ✅ Contextual: Suggests next logical step

**Implementation Complexity**: High (4-5 hours to build full menu system)

---

### Option 3: Cursor Integration (Most Seamless)

**Concept**: Cursor command palette integration

**Usage**:
```
In Cursor:
1. Cmd+Shift+P → "LLM: Execute Next Achievement"
2. Cursor reads current file (PLAN)
3. Generates and inserts prompt automatically
4. You review and send to AI
```

**Advantages**:
- ✅ Seamless: No leaving Cursor
- ✅ Context-aware: Knows current file
- ✅ Zero-friction: 2 keystrokes

**Disadvantages**:
- ❌ Complex: Requires Cursor extension development
- ❌ Time-consuming: 10-15 hours for full extension
- ❌ Maintenance: Need to update with Cursor API changes

**Implementation Complexity**: Very High (defer to future)

---

## 🎯 Recommended Approach: Option 1 (CLI Script)

### Why Command-Line Is Best

1. **Fast to Implement**: 2-3 hours vs 4-5 for menu vs 10-15 for extension
2. **Immediately Useful**: Works today, not next month
3. **Simple**: One command, one output
4. **Portable**: Works anywhere Python works
5. **Maintainable**: Easy to update as methodology changes

---

## 📋 Design: generate_prompt.py

### Core Features

**Input**:
- PLAN file path (or auto-detect from current directory)
- Action: `--next`, `--achievement N.N`, `--continue`, `--resume`
- Optional: `--clipboard` (copy to clipboard)

**Output**:
- Complete prompt (like ideal example)
- Ready to paste into Cursor
- Customized for situation

**Intelligence**:
- Reads PLAN file (parses achievements)
- Calculates context boundaries (line counts)
- Detects which scripts exist (mentions real validation)
- Knows current state (which SUBPLANs exist, what's next)
- Determines tree level (PLAN vs SUBPLAN vs EXECUTION)

---

### Implementation Approach

```python
#!/usr/bin/env python3
"""
LLM Prompt Generator - Automated high-quality prompt generation

Usage:
    python LLM/scripts/generate_prompt.py @PLAN_FEATURE.md --next
    python LLM/scripts/generate_prompt.py @PLAN_FEATURE.md --achievement 1.1
    python LLM/scripts/generate_prompt.py @EXECUTION_TASK_X_01_01.md --continue
    python LLM/scripts/generate_prompt.py @PLAN_FEATURE.md --next --clipboard
"""

import argparse
import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Achievement:
    number: str  # "0.1", "1.1", etc.
    title: str
    goal: str
    effort: str  # "2-3 hours"
    priority: str
    deliverables: List[str]
    line_start: int  # Line where achievement starts in PLAN
    line_end: int    # Line where achievement ends

@dataclass
class PlanContext:
    feature_name: str  # "METHODOLOGY-V2-ENHANCEMENTS"
    current_status: str
    next_achievement: Achievement
    archive_location: str
    subplans_completed: int
    total_achievements: int

def parse_plan_file(plan_path: Path) -> PlanContext:
    """Extract structured data from PLAN file."""
    with open(plan_path) as f:
        content = f.read()
        lines = content.split('\n')
    
    # Extract feature name from filename
    feature_name = plan_path.stem.replace('PLAN_', '')
    
    # Parse achievements (scan for "**Achievement X.Y**:")
    achievements = []
    for i, line in enumerate(lines):
        if match := re.match(r'\*\*Achievement (\d+\.\d+)\*\*:(.+)', line):
            ach_num = match.group(1)
            ach_title = match.group(2).strip()
            # Extract details from following lines...
            achievements.append(Achievement(...))
    
    # Determine next achievement (first without SUBPLAN)
    next_ach = find_next_achievement(feature_name, achievements)
    
    # Calculate context boundaries
    ach_section_lines = calculate_section_lines(content, next_ach)
    handoff_lines = calculate_section_lines(content, "Current Status")
    
    return PlanContext(
        feature_name=feature_name,
        next_achievement=next_ach,
        context_lines=ach_section_lines + handoff_lines,
        # ... etc
    )

def find_next_achievement(feature_name: str, achievements: List[Achievement]) -> Achievement:
    """Find next achievement without SUBPLAN."""
    for ach in achievements:
        subplan_file = f"SUBPLAN_{feature_name}_{ach.number.replace('.', '')}.md"
        if not Path(subplan_file).exists():
            return ach
    return None

def generate_prompt(context: PlanContext, template: str) -> str:
    """Fill template with actual values."""
    
    # Detect which validation scripts exist
    validation_scripts = detect_validation_scripts()
    
    prompt = template.format(
        feature=context.feature_name,
        achievement_num=context.next_achievement.number,
        achievement_title=context.next_achievement.title,
        achievement_goal=context.next_achievement.goal,
        estimated_hours=context.next_achievement.effort,
        context_budget=context.context_lines,
        plan_total_lines=context.total_plan_lines,
        subplan_number=format_subplan_number(context.next_achievement.number),
        deliverables=format_deliverables(context.next_achievement.deliverables),
        validation_scripts=format_scripts(validation_scripts),
        archive_location=context.archive_location
    )
    
    return prompt

def main():
    parser = argparse.ArgumentParser(description='Generate high-quality LLM prompts')
    parser.add_argument('file', help='PLAN or EXECUTION_TASK file')
    parser.add_argument('--next', action='store_true', help='Generate for next achievement')
    parser.add_argument('--achievement', help='Specific achievement (e.g., 1.1)')
    parser.add_argument('--continue', action='store_true', help='Continue current work')
    parser.add_argument('--clipboard', action='store_true', help='Copy to clipboard')
    
    args = parser.parse_args()
    
    # Parse input file
    file_path = Path(args.file.replace('@', ''))
    
    if file_path.name.startswith('PLAN_'):
        context = parse_plan_file(file_path)
        template = ACHIEVEMENT_EXECUTION_TEMPLATE
    elif file_path.name.startswith('EXECUTION_TASK_'):
        context = parse_execution_task_file(file_path)
        template = CONTINUE_EXECUTION_TEMPLATE
    
    # Generate prompt
    prompt = generate_prompt(context, template)
    
    # Output
    print(prompt)
    
    if args.clipboard:
        import pyperclip
        pyperclip.copy(prompt)
        print("\n✅ Prompt copied to clipboard!")

if __name__ == '__main__':
    main()
```

**Key Intelligence**:
- Parses PLAN structure (achievements, estimates, deliverables)
- Calculates actual line counts (context boundaries)
- Detects existing SUBPLANs (knows what's next)
- Finds validation scripts (lists real checks)
- Formats everything into ideal prompt structure

---

## 🎯 Workflow Integration

### Ideal User Workflow

**Current** (Manual - Not Practical):
1. Read PLAN
2. Identify next achievement
3. Calculate context lines
4. Write detailed prompt with all sections
5. Double-check everything
6. Paste into Cursor
**Time**: 5-10 minutes, error-prone

**With Automation** (Proposed):
```bash
# One command
python LLM/scripts/generate_prompt.py @PLAN_X.md --next --clipboard

# Paste into Cursor (Cmd+V)
# Send to AI
```
**Time**: 5 seconds, perfect quality

---

### Integration Points

**In PROMPTS.md**: Add section:
```markdown
## 🤖 Automated Prompt Generation

**Instead of manually creating prompts, use the generator**:

```bash
# Generate prompt for next achievement
python LLM/scripts/generate_prompt.py @PLAN_FEATURE.md --next --clipboard

# Paste into Cursor and send to AI
```

The generator creates ideal prompts with:
✓ Exact context boundaries (calculated from file)
✓ All required steps
✓ Validation enforcement
✓ Size limits
✓ DO NOTs
✓ External verification
```

**In START_POINT**: Add to workflow:
```markdown
## Step 3: Generate Prompt (Automated)

Instead of constructing prompt manually:

```bash
python LLM/scripts/generate_prompt.py @PLAN_FEATURE.md --next --clipboard
```

This generates ideal prompt with all safeguards.
```

---

## 📊 Prompt Templates (Used by Generator)

### Template 1: Execute Achievement

```python
ACHIEVEMENT_EXECUTION_TEMPLATE = """
Execute Achievement {achievement_num} in @PLAN_{feature}.md following strict methodology.

═══════════════════════════════════════════════════════════════

CONTEXT BOUNDARIES (Read ONLY These):
✅ @PLAN_{feature}.md - Achievement {achievement_num} section only ({achievement_lines} lines)
✅ @PLAN_{feature}.md - "Current Status & Handoff" section ({handoff_lines} lines)
❌ DO NOT READ: Full PLAN ({plan_total_lines} lines), other achievements

CONTEXT BUDGET: {context_budget} lines maximum

═══════════════════════════════════════════════════════════════

ACHIEVEMENT {achievement_num}: {achievement_title}

Goal: {achievement_goal}
Estimated: {estimated_hours}
Priority: {priority}

═══════════════════════════════════════════════════════════════

REQUIRED STEPS (No Shortcuts):

Step 1: Create SUBPLAN (MANDATORY)
- File: SUBPLAN_{feature}_{subplan_num}.md
- Size: 200-400 lines
- Must include: Objective, Deliverables, Approach, Tests, Expected Results

Step 2: Create EXECUTION_TASK (MANDATORY)
- File: EXECUTION_TASK_{feature}_{subplan_num}_01.md
- Size: 100-200 lines maximum
- Start with: Objective, Approach, Iteration Log (Iteration 1)

Step 3: Execute Work
{deliverables_list}

Step 4: Verify Deliverables (MANDATORY)
{verification_commands}

Step 5: Complete EXECUTION_TASK
- Update: Iteration Log with "Complete"
- Add: Learning Summary
- Verify: <200 lines (run: wc -l EXECUTION_TASK_*.md)

Step 6: Archive Immediately
- Move: SUBPLAN → {archive_location}/subplans/
- Move: EXECUTION_TASK → {archive_location}/execution/
- Update: PLAN Subplan Tracking

Step 7: Update PLAN Statistics
- Calculate from EXECUTION_TASK (not imagination)

═══════════════════════════════════════════════════════════════

VALIDATION ENFORCEMENT:

{validation_scripts_list}

═══════════════════════════════════════════════════════════════

DO NOT:
❌ Skip SUBPLAN ("it's simple" - NO, all work needs SUBPLANs)
❌ Skip EXECUTION_TASK ("just document in PLAN" - NO)
❌ Mark complete without verifying files exist (run: ls -1)
❌ Read full PLAN (read Achievement {achievement_num} only)
❌ Claim hours without EXECUTION_TASK to verify from

REMEMBER:
✓ SUBPLAN + EXECUTION_TASK for EVERY achievement
✓ Verify deliverables exist (ls -1)
✓ Archive immediately on completion
✓ Statistics from EXECUTION_TASK data
✓ Stay within context budget ({context_budget} lines)

═══════════════════════════════════════════════════════════════

EXTERNAL VERIFICATION:

After completing, I will verify:
1. SUBPLAN file exists and complete?
2. EXECUTION_TASK file exists with learnings?
3. All deliverables exist? (filesystem check)
4. Statistics accurate?
5. EXECUTION_TASK <200 lines?

Do not proceed until verification passes.

═══════════════════════════════════════════════════════════════

Now beginning Achievement {achievement_num} execution:

Creating SUBPLAN_{feature}_{subplan_num}.md...
"""
```

---

### Template 2: Continue EXECUTION_TASK

```python
CONTINUE_EXECUTION_TEMPLATE = """
Continue @EXECUTION_TASK_{feature}_{subplan}_{execution}.md (Iteration {next_iteration})

═══════════════════════════════════════════════════════════════

CONTEXT BOUNDARIES:
✅ THIS EXECUTION_TASK only ({execution_lines} lines)
✅ Parent SUBPLAN objective section only (50 lines)
❌ DO NOT READ: Full SUBPLAN, PLAN, other EXECUTION_TASKs

CONTEXT BUDGET: {context_budget} lines maximum

═══════════════════════════════════════════════════════════════

CURRENT STATUS:
- Iteration: {current_iteration}
- Status: {status}
- Last action: {last_action}
- Blockers: {blockers}

═══════════════════════════════════════════════════════════════

NEXT ITERATION WORKFLOW:

1. Read: THIS EXECUTION_TASK iteration log
2. Understand: What was tried, what failed, learnings
3. Plan: Next approach (different from previous)
4. Execute: Implementation
5. Document: Add Iteration {next_iteration} to log (40-50 lines max)
6. Verify: EXECUTION_TASK still <200 lines (wc -l)
7. If >200 lines after {max_iterations} iterations: Create new EXECUTION_TASK

═══════════════════════════════════════════════════════════════

SIZE ENFORCEMENT:
✓ Current: {execution_lines} lines
✓ Limit: 200 lines
✓ After iteration: Will check size
✓ If >200: Must create EXECUTION_TASK_{feature}_{subplan}_{next_execution}.md

═══════════════════════════════════════════════════════════════

Continuing iteration {next_iteration}...
"""
```

---

### Template 3: Start Next Achievement

```python
NEXT_ACHIEVEMENT_TEMPLATE = """
Start next achievement in @PLAN_{feature}.md

═══════════════════════════════════════════════════════════════

CONTEXT BOUNDARIES:
✅ @PLAN_{feature}.md - Current Status section (20 lines)
✅ @PLAN_{feature}.md - Next achievement section (50 lines)
✅ @PLAN_{feature}.md - Archive location (5 lines)
❌ DO NOT READ: Full PLAN, completed achievements, other sections

CONTEXT BUDGET: 75 lines maximum

═══════════════════════════════════════════════════════════════

PREVIOUS ACHIEVEMENT:
✅ Achievement {prev_achievement}: Complete
✅ SUBPLAN archived: {archive_location}/subplans/
✅ EXECUTION_TASK archived: {archive_location}/execution/

NEXT ACHIEVEMENT: {next_achievement}
[Rest of template similar to Template 1...]
```

---

## 🎯 Intelligence Features

### Feature 1: Context Calculation

**Auto-Calculate Line Counts**:
```python
def calculate_context_lines(plan_path: Path, achievement_num: str) -> int:
    with open(plan_path) as f:
        content = f.read()
        lines = content.split('\n')
    
    # Find achievement section
    start = find_section_start(lines, f"Achievement {achievement_num}")
    end = find_section_end(lines, start)
    achievement_lines = end - start
    
    # Find handoff section
    handoff_start = find_section_start(lines, "Current Status")
    handoff_end = find_section_end(lines, handoff_start)
    handoff_lines = handoff_end - handoff_start
    
    return achievement_lines + handoff_lines
```

**Advantage**: Accurate context budgets automatically

---

### Feature 2: Validation Script Detection

**Auto-Detect Which Scripts Exist**:
```python
def detect_validation_scripts() -> List[str]:
    scripts_dir = Path('LLM/scripts')
    
    validation_scripts = [
        'validate_achievement_completion.py',
        'validate_execution_start.py',
        'validate_mid_plan.py',
        'check_plan_size.py',
        'check_execution_task_size.py',
        'validate_references.py',
        'validate_plan_compliance.py'
    ]
    
    existing = []
    for script in validation_scripts:
        if (scripts_dir / script).exists():
            existing.append(script)
    
    return existing
```

**Advantage**: Prompt only mentions scripts that actually exist

---

### Feature 3: State Detection

**Auto-Detect Current State**:
```python
def detect_current_state(feature_name: str) -> dict:
    # Check which SUBPLANs exist
    subplans = list(Path('.').glob(f'SUBPLAN_{feature_name}_*.md'))
    
    # Check archive
    archive_path = Path(f'{feature_name.lower()}-archive')
    archived_subplans = []
    if archive_path.exists():
        archived_subplans = list(archive_path.glob('subplans/SUBPLAN_*.md'))
    
    return {
        'active_subplans': len(subplans),
        'archived_subplans': len(archived_subplans),
        'next_subplan_num': len(subplans) + len(archived_subplans) + 1,
        'has_archive': archive_path.exists()
    }
```

**Advantage**: Knows what's done, what's next, correct numbering

---

### Feature 4: Deliverable Formatting

**Auto-Format Deliverables as Verification Commands**:
```python
def format_deliverables(deliverables: List[str]) -> str:
    commands = []
    for deliverable in deliverables:
        commands.append(f"ls -1 {deliverable}")
    
    return "Run verification:\n" + "\n".join(f"  {cmd}" for cmd in commands)
```

**Advantage**: Ready-to-run verification commands in prompt

---

## 🎯 Enhanced Features (v2.0)

### Feature 5: Effort Tracking

**Auto-Track Time Spent**:
```python
def calculate_time_spent(feature_name: str) -> float:
    """Sum time from all archived EXECUTION_TASKs."""
    archive_path = Path(f'{feature_name.lower()}-archive/execution')
    
    total_hours = 0.0
    for execution_task in archive_path.glob('EXECUTION_TASK_*.md'):
        # Parse "Total Time: Xh" from file
        time = extract_time_from_execution(execution_task)
        total_hours += time
    
    return total_hours
```

**Advantage**: Prompt can show "Already spent: Xh, Remaining: Yh"

---

### Feature 6: Progress Indicator

**Show Progress in Prompt**:
```python
Progress: {completed_achievements}/{total_achievements} ({percentage}%)
Time: {time_spent}h / {estimated_total}h
Next: Achievement {next_achievement}
```

**Advantage**: Context about where you are in PLAN

---

### Feature 7: Suggested Actions

**AI-Suggested Next Steps**:
```python
def suggest_next_action(context: PlanContext) -> str:
    if context.time_spent > 20 and not context.mid_plan_review_done:
        return "⚠️ SUGGESTION: Run mid-plan review (>20h worked)"
    
    if context.plan_size > 400:
        return "⚠️ SUGGESTION: Plan approaching 600-line limit (consider GrammaPlan)"
    
    if context.completed_achievements > 0 and not context.has_learnings:
        return "⚠️ SUGGESTION: Extract learnings from completed EXECUTION_TASKs"
    
    return f"✅ Ready to start Achievement {context.next_achievement}"
```

**Advantage**: Proactive guidance prevents issues

---

## 📋 Implementation Phases

### Phase 1: Minimal Viable Script (2-3h)

**Features**:
- Parse PLAN file (extract achievements)
- Detect next achievement (no SUBPLAN exists)
- Generate basic prompt (fill template)
- Output to stdout

**Deliverable**: `LLM/scripts/generate_prompt.py` (basic version, 200-300 lines)

---

### Phase 2: Intelligence Features (2-3h)

**Add**:
- Context line calculation
- Validation script detection
- State detection (archived vs active)
- Deliverable formatting
- Clipboard support

**Enhancement**: Prompts now have accurate, auto-calculated values

---

### Phase 3: Multi-Template Support (1-2h)

**Add**:
- Continue EXECUTION_TASK template
- Start next achievement template
- Resume SUBPLAN template
- Create new PLAN template

**Enhancement**: Handles all scenarios, not just "next achievement"

---

### Phase 4: Advanced Features (2-3h)

**Add**:
- Progress tracking
- Time calculation
- Suggested actions
- Interactive menu (optional)

**Enhancement**: Proactive guidance, full workflow support

---

## 🎯 Recommended Implementation

### **Build in 2 Stages**

**Stage 1: Core Generator** (2-3h) - **Do This First**
- Basic prompt generation
- Template filling
- Context calculation
- Clipboard support
- **Deliverable**: Works for 80% of cases

**Stage 2: Enhancements** (3-4h) - **Do After Testing**
- Multi-template support
- State detection
- Progress tracking
- Suggested actions
- **Deliverable**: Handles all scenarios

**Total**: 5-7 hours for complete solution

---

## 🎯 Integration with PLAN_METHODOLOGY-V2-ENHANCEMENTS

**This Should Be Achievement 5.4!**

**Add to PLAN**:
```markdown
**Achievement 5.4**: Automated Prompt Generation

- **Goal**: Create script that generates ideal prompts automatically
- **What**:
  - Create LLM/scripts/generate_prompt.py
  - Parse PLAN files, extract achievements
  - Calculate context boundaries
  - Fill templates with actual values
  - Clipboard support
  - Multiple templates (execute, continue, resume)
- **Success**: One command generates perfect prompt
- **Effort**: 3-4 hours
- **Deliverables**:
  - LLM/scripts/generate_prompt.py (300-400 lines)
  - Prompt templates (embedded in script)
  - Integration with PROMPTS.md
  - Examples and documentation
```

**Priority**: HIGH (enables all other work to be easier)

**Placement**: After organization work (Priority 5), before testing

---

## 📊 Expected Impact

### Before Automation:
- Prompt creation: 5-10 minutes per achievement
- Quality: Variable (depends on manual effort)
- Consistency: Low (forget elements)
- Context boundaries: Guessed (often wrong)
- Error rate: 30% (missing elements)

### After Automation:
- Prompt creation: 5 seconds per achievement
- Quality: Perfect (always includes all elements)
- Consistency: 100% (template-based)
- Context boundaries: Accurate (calculated)
- Error rate: <5% (only if script bugs)

**Time Savings**: ~8 minutes per achievement × 200 achievements = **1,600 minutes saved (26 hours!)**

---

## 🎯 Critical Success Factors

### Success Factor 1: Accurate Parsing

**Critical**: Script must correctly parse PLAN structure

**Implementation**:
- Use regex for achievement markers
- Handle variations (whitespace, formatting)
- Fallback: Manual input if parsing fails

---

### Success Factor 2: Template Quality

**Critical**: Templates must include all learnings

**Implementation**:
- Use ideal prompt as reference
- Include all 7 required steps
- All DO NOTs
- All validation mentions
- External verification

---

### Success Factor 3: Easy to Use

**Critical**: Must be simpler than manual

**Implementation**:
- Single command: `generate_prompt.py @PLAN --next`
- Auto-detects context
- Clipboard support (--clipboard flag)
- Clear output

---

## 🎯 Recommendation

### **Implement as Achievement 5.4 in Current PLAN**

**Why**:
- ✅ Fits naturally in organization achievements (Priority 5)
- ✅ High value (saves 26 hours across 200 achievements)
- ✅ Realistic effort (3-4 hours)
- ✅ Immediately useful (use for remaining achievements)
- ✅ Validates automation approach

**Execution**:
1. Add Achievement 5.4 to PLAN_METHODOLOGY-V2-ENHANCEMENTS.md
2. Execute after Achievement 5.3 (validation visibility)
3. Create SUBPLAN for prompt generator
4. Build script properly with EXECUTION_TASK
5. Test with Achievement 6.1 (use generated prompt)
6. If works: All future prompts are automated!

**Self-Validating**: The script that generates prompts can generate its own execution prompt (meta!)

---

## 📋 Alternative: Quick Prototype Now

### **If Wanted Immediately** (30 min):

Create simple version:
```bash
#!/bin/bash
# quick_prompt.sh - Temporary until full script built

PLAN=$1
ACHIEVEMENT=$2

cat << EOF
Execute Achievement $ACHIEVEMENT in @$PLAN

REQUIRED STEPS:
1. Create SUBPLAN
2. Create EXECUTION_TASK
3. Do work
4. Verify: ls -1 [deliverables]
5. Complete EXECUTION_TASK
6. Archive immediately
7. Update PLAN stats

DO NOT skip steps. DO NOT claim without verification.

External verification will be requested.

Creating SUBPLAN...
EOF
```

**Usage**: `./quick_prompt.sh PLAN_FEATURE.md 0.1`

**Advantage**: Works immediately, good enough for current PLAN

**Disadvantage**: Not intelligent (no parsing, no calculation)

---

## 🎯 Final Recommendation

### **Two-Path Approach**

**Path A: Quick Solution** (30 min):
- Create simple bash script (quick_prompt.sh)
- Use for immediate work (Achievement 0.1-6.1)
- Good enough for current PLAN

**Path B: Full Solution** (3-4h):
- Add as Achievement 5.4 to current PLAN
- Build proper Python script with intelligence
- Use for all future work

**Best**: Start with Path A (immediate relief), then Path B (permanent solution)

---

## 🎓 Meta-Insight

**The Question Itself Is Valuable**:

You identified that manual prompt creation is impractical. This insight should drive automation priority.

**Lesson**: Tools should make methodology EASIER, not harder. If something is tedious, automate it.

**Application**: Prompt generation automation is HIGH PRIORITY (should be Tier 1, not Tier 2)

---

## 📊 Summary

**Answer to "How to automate?"**:

**Immediate** (use now):
- Copy ideal prompt from EXECUTION_ANALYSIS_IDEAL-PROMPT-EXAMPLE.md
- Use for Achievement 0.1
- Takes 10 seconds to copy/paste

**Short-term** (30 min):
- Create quick_prompt.sh (bash script)
- Simple template filling
- Good enough for current PLAN

**Long-term** (3-4h):
- Create LLM/scripts/generate_prompt.py (Python)
- Full parsing, calculation, intelligence
- Add as Achievement 5.4 to current PLAN
- Permanent solution for all future work

**Recommended**: Use ideal prompt now, create full script as Achievement 5.4

---

**Status**: Prompt Automation Strategy Complete  
**Immediate Action**: Use ideal prompt from IDEAL-PROMPT-EXAMPLE.md  
**Future Action**: Build generate_prompt.py as Achievement 5.4

