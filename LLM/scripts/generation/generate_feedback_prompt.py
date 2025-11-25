#!/usr/bin/env python3
"""
Generate feedback prompt for reviewing completed Achievement work.

This script generates prompts for reviewers to assess SUBPLAN + EXECUTION work
and create feedback documents (APPROVED_XX.md or FIX_XX.md).

Usage:
    python generate_feedback_prompt.py review @PLAN_NAME.md --achievement X.Y
    python generate_feedback_prompt.py review @SUBPLAN_NAME.md

The feedback file determines Achievement completion status:
- APPROVED_XX.md → Achievement complete ✅
- FIX_XX.md → Achievement needs fixes ⚠️

Created: 2025-11-11
Part of: Plan folder structure upgrade
"""

import argparse
import sys
from pathlib import Path
import re


def resolve_plan_path(plan_identifier: str) -> Path:
    """
    Resolve @shorthand or full path to actual PLAN file.

    Args:
        plan_identifier: @PLAN_NAME, @PLAN_NAME.md, or full path

    Returns:
        Path to PLAN file
    """
    if plan_identifier.startswith("@"):
        # Remove @ and .md if present
        folder_name = plan_identifier[1:].replace(".md", "").replace("PLAN_", "")

        # Search in work-space/plans/
        plans_dir = Path("work-space/plans")
        if not plans_dir.exists():
            print(f"❌ Error: Plans directory not found: {plans_dir}", file=sys.stderr)
            sys.exit(1)

        # Find matching folder (case-insensitive partial match)
        matches = []
        for folder in plans_dir.iterdir():
            if folder.is_dir() and folder_name.upper() in folder.name.upper():
                matches.append(folder)

        if len(matches) == 0:
            print(f"❌ Error: No plan folder found matching: {folder_name}", file=sys.stderr)
            print(f"\nAvailable plans:", file=sys.stderr)
            for folder in sorted(plans_dir.iterdir()):
                if folder.is_dir():
                    print(f"  - {folder.name}", file=sys.stderr)
            sys.exit(1)

        if len(matches) > 1:
            print(f"❌ Error: Multiple plan folders match: {folder_name}", file=sys.stderr)
            for folder in matches:
                print(f"  - {folder.name}", file=sys.stderr)
            sys.exit(1)

        # Find PLAN file in folder
        plan_folder = matches[0]
        plan_files = list(plan_folder.glob("PLAN_*.md"))

        if len(plan_files) == 0:
            print(f"❌ Error: No PLAN file found in: {plan_folder}", file=sys.stderr)
            sys.exit(1)

        return plan_files[0]
    else:
        # Direct path
        path = Path(plan_identifier)
        if not path.exists():
            print(f"❌ Error: File not found: {path}", file=sys.stderr)
            sys.exit(1)
        return path


def find_subplan_for_achievement(plan_path: Path, achievement_num: str) -> Path:
    """Find SUBPLAN file for given achievement."""
    plan_folder = plan_path.parent
    subplans_dir = plan_folder / "subplans"

    if not subplans_dir.exists():
        return None

    # Convert 1.1 → 11
    subplan_num = achievement_num.replace(".", "")
    feature_name = plan_folder.name

    # Look for SUBPLAN file
    subplan_pattern = f"SUBPLAN_{feature_name}_{subplan_num}.md"
    subplan_path = subplans_dir / subplan_pattern

    if subplan_path.exists():
        return subplan_path

    return None


def find_execution_tasks(plan_path: Path, achievement_num: str) -> list:
    """Find all EXECUTION_TASK files for given achievement."""
    plan_folder = plan_path.parent
    execution_dir = plan_folder / "execution"

    if not execution_dir.exists():
        return []

    # Convert 1.1 → 11
    exec_num = achievement_num.replace(".", "")
    feature_name = plan_folder.name

    # Find all EXECUTION_TASK files for this achievement
    pattern = f"EXECUTION_TASK_{feature_name}_{exec_num}_*.md"
    execution_files = sorted(execution_dir.glob(pattern))

    return execution_files


def generate_feedback_prompt(plan_path: Path, achievement_num: str) -> str:
    """Generate feedback review prompt."""

    plan_folder = plan_path.parent
    feature_name = plan_folder.name

    # Find SUBPLAN
    subplan_path = find_subplan_for_achievement(plan_path, achievement_num)
    if not subplan_path:
        return f"❌ Error: No SUBPLAN found for Achievement {achievement_num}"

    # Find EXECUTION_TASKs
    execution_files = find_execution_tasks(plan_path, achievement_num)
    if not execution_files:
        return f"❌ Error: No EXECUTION_TASK files found for Achievement {achievement_num}"

    # Convert 1.1 → 11 for feedback filename
    feedback_num = achievement_num.replace(".", "")

    prompt = f"""Review Achievement {achievement_num} in @{plan_path.name}

═══════════════════════════════════════════════════════════════════════

# Achievement {achievement_num} Review

**PLAN**: {plan_path.name}
**SUBPLAN**: {subplan_path.name}
**EXECUTION_TASKs**: {len(execution_files)} file(s)

═══════════════════════════════════════════════════════════════════════

## 📋 Review Scope

Read and assess:

1. **SUBPLAN**: @{subplan_path.name}
   - Objective clarity
   - Approach soundness
   - Deliverables definition
   - Execution strategy

2. **EXECUTION_TASK(s)**:"""

    for i, exec_file in enumerate(execution_files, 1):
        prompt += f"\n   - @{exec_file.name}"

    prompt += f"""

Review each EXECUTION_TASK:
   - Iteration log completeness
   - Learning summary quality
   - Deliverables verification
   - Status accuracy

3. **Deliverables** (verify they exist):
   - Check all files mentioned in EXECUTION_TASK(s)
   - Verify quality and completeness
   - Confirm tests passing (if code changes)

═══════════════════════════════════════════════════════════════════════

## 🎯 Review Criteria

### ✅ APPROVED Criteria (all must be met):

1. **Objective Achieved**
   - SUBPLAN objective fully met
   - All deliverables created and verified
   - Quality meets or exceeds expectations

2. **Documentation Complete**
   - EXECUTION_TASK(s) have complete iteration logs
   - Learning summary captures key insights
   - Status accurately reflects completion

3. **Tests Passing** (if code changes)
   - All relevant tests run and passing
   - New tests added for new functionality
   - No regressions introduced

4. **Quality Standards**
   - Code follows project conventions
   - Documentation is clear and helpful
   - No obvious bugs or issues

### ⚠️ FIX Criteria (any of these):

1. **Incomplete Work**
   - Deliverables missing or incomplete
   - Objective not fully achieved
   - Tests not run or failing

2. **Quality Issues**
   - Code quality below standards
   - Documentation unclear or missing
   - Bugs or regressions introduced

3. **Process Issues**
   - EXECUTION_TASK status inaccurate
   - Learning summary missing or shallow
   - Verification steps skipped

═══════════════════════════════════════════════════════════════════════

## 📝 Create Feedback Document

Based on your review, create ONE of these files:

### Option A: APPROVED ✅

File: `execution/feedbacks/APPROVED_{feedback_num}.md`

Structure:
```markdown
# APPROVED: Achievement {achievement_num}

**Reviewer**: [Your name/role]
**Review Date**: [Date]
**Status**: ✅ APPROVED

## Summary

[2-3 sentences on what was achieved and why it's approved]

## Strengths

- [What was done particularly well]
- [Positive aspects worth noting]
- [Best practices followed]

## Deliverables Verified

- ✅ [Deliverable 1] - [Brief verification note]
- ✅ [Deliverable 2] - [Brief verification note]
- ✅ [Deliverable 3] - [Brief verification note]

## Tests Status

- [Test results summary]
- [Coverage information if applicable]

## Recommendations for Future Work

- [Optional: Suggestions for next achievements]
- [Optional: Patterns to continue]
```

### Option B: NEEDS FIXES ⚠️

File: `execution/feedbacks/FIX_{feedback_num}.md`

Structure:
```markdown
# FIX REQUIRED: Achievement {achievement_num}

**Reviewer**: [Your name/role]
**Review Date**: [Date]
**Status**: ⚠️ NEEDS FIXES

## Summary

[2-3 sentences on what needs to be fixed and why]

## Issues Found

### Critical Issues (must fix)
1. [Issue description]
   - Impact: [Why this matters]
   - Fix: [What needs to be done]

2. [Issue description]
   - Impact: [Why this matters]
   - Fix: [What needs to be done]

### Minor Issues (should fix)
- [Issue description and suggested fix]
- [Issue description and suggested fix]

## What Worked Well

- [Positive aspects to acknowledge]

## Next Steps

1. [Specific action to take]
2. [Specific action to take]
3. [Re-review after fixes]
```

═══════════════════════════════════════════════════════════════════════

## 🔍 Verification Checklist

Before finalizing your feedback:

- [ ] Read SUBPLAN objective and approach
- [ ] Review all EXECUTION_TASK iteration logs
- [ ] Verify all deliverables exist and are complete
- [ ] Check test results (if applicable)
- [ ] Assess documentation quality
- [ ] Confirm status accuracy
- [ ] Create APPROVED_{feedback_num}.md or FIX_{feedback_num}.md
- [ ] Place file in: execution/feedbacks/

═══════════════════════════════════════════════════════════════════════

## 💡 Important Notes

1. **Feedback determines completion**: 
   - APPROVED_{feedback_num}.md → Achievement marked complete ✅
   - FIX_{feedback_num}.md → Achievement needs rework ⚠️

2. **Be specific**: 
   - Vague feedback doesn't help
   - Cite specific examples
   - Provide actionable recommendations

3. **Balance**: 
   - Acknowledge what worked well
   - Be constructive about issues
   - Focus on improvement, not criticism

4. **Consistency**: 
   - Apply same standards to all achievements
   - Use the templates provided
   - Keep feedback concise but complete

═══════════════════════════════════════════════════════════════════════

Now beginning review of Achievement {achievement_num}...
"""

    return prompt


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate feedback review prompts for completed achievements"
    )

    parser.add_argument(
        "action", choices=["review"], help="Action to perform (currently only 'review')"
    )

    parser.add_argument("plan_file", help="PLAN file (@PLAN_NAME, @PLAN_NAME.md, or full path)")

    parser.add_argument("--achievement", required=True, help="Achievement number (e.g., 1.1, 0.2)")

    parser.add_argument("--clipboard", action="store_true", help="Copy prompt to clipboard")

    args = parser.parse_args()

    try:
        # Resolve PLAN path
        plan_path = resolve_plan_path(args.plan_file)

        # Generate prompt
        prompt = generate_feedback_prompt(plan_path, args.achievement)

        # Output
        print(prompt)

        # Copy to clipboard if requested
        if args.clipboard:
            try:
                import pyperclip

                pyperclip.copy(prompt)
                print("\n✅ Prompt copied to clipboard!")
            except Exception as e:
                print(f"\n⚠️  Could not copy to clipboard: {e}", file=sys.stderr)

        sys.exit(0)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
