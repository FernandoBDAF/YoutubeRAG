#!/usr/bin/env python3
"""
Generate prompt to resume a paused PLAN following IMPLEMENTATION_RESUME.md protocol.

Usage:
    python LLM/scripts/generation/generate_resume_prompt.py @PLAN_FEATURE.md
    python LLM/scripts/generation/generate_resume_prompt.py @PLAN_FEATURE.md --clipboard
"""

import argparse
import re
import sys
from pathlib import Path


def extract_plan_info(plan_path: Path) -> dict:
    """Extract plan information."""
    with open(plan_path, "r", encoding="utf-8") as f:
        content = f.read()

    feature_name = plan_path.stem.replace("PLAN_", "")

    # Find next achievement
    next_achievement = None
    next_title = None

    # Try "What's Next" section
    match = re.search(
        r"(?:Next|What\'s Next)[:\s]+Achievement\s+(\d+\.\d+)", content, re.IGNORECASE
    )
    if match:
        next_achievement = match.group(1)
        # Try to find achievement title
        ach_match = re.search(rf"\*\*Achievement {next_achievement}\*\*:(.+)", content)
        if ach_match:
            next_title = ach_match.group(1).strip()

    # Get archive location
    archive_location = "./feature-archive/"
    match = re.search(r"Archive Location[:\s]+\*\*[:\s]*`?([^`\n]+)`?", content, re.IGNORECASE)
    if match:
        archive_location = match.group(1).strip().strip("\"'")

    return {
        "feature_name": feature_name,
        "next_achievement": next_achievement or "X.Y",
        "next_title": next_title or "[Title]",
        "plan_path": plan_path.name,
        "archive_location": archive_location,
    }


RESUME_PROMPT_TEMPLATE = """Resume @{plan_path} following @LLM/protocols/IMPLEMENTATION_RESUME.md protocol

═══════════════════════════════════════════════════════════════════════

✅ Pre-Resume Checklist:

Step 1: Context Gathering (10-15 min)
- [ ] Read @ACTIVE_PLANS.md (verify this is the PLAN to resume)
- [ ] Read @{plan_path} completely
- [ ] Read "Current Status & Handoff" section
- [ ] Review "Subplan Tracking" section
- [ ] Review "Achievement Addition Log" (if exists)
- [ ] Identify next achievement to tackle

Step 2: Naming Convention (5 min)
- [ ] Review @LLM/protocols/IMPLEMENTATION_START_POINT.md naming rules
- [ ] Check existing SUBPLAN/EXECUTION_TASK numbering
- [ ] Determine next SUBPLAN/EXECUTION_TASK numbers

Step 2.5: Dependencies (5 min)
- [ ] Read "Related Plans" section
- [ ] Verify dependencies are Ready (not Blocked)
- [ ] Review @LLM/guides/MULTIPLE-PLANS-PROTOCOL.md if needed

Step 2.6: Format Compliance (2 min)
- [ ] Verify "Related Plans" uses 6-type format
- [ ] Update format if outdated

Step 3: Technical Pre-Flight (5 min)
- [ ] Git status clean
- [ ] Tests passing
- [ ] Virtual environment active
- [ ] Configuration correct

Step 4: Context Understanding (variable)
- [ ] Read last EXECUTION_TASK (from archive: {archive_location}execution/)
- [ ] Check for blockers
- [ ] Review learnings

Step 5: ACTIVE_PLANS.md Update (REQUIRED)
- [ ] Pause any other "🚀 In Progress" PLAN
- [ ] Mark this PLAN as "🚀 In Progress"
- [ ] Update "Last Updated" timestamp
- [ ] Verify only ONE PLAN "In Progress"

✅ Next Achievement: {next_achievement} ({next_title})

═══════════════════════════════════════════════════════════════════════

VALIDATION ENFORCEMENT:

Before resuming, these scripts will run:
✓ validate_execution_start.py (checks prerequisites)
✓ check_plan_size.py (validates PLAN still within limits)
✓ validate_mid_plan.py (checks statistics accuracy)

If issues found: BLOCKS with error + fix prompt

DO NOT:
❌ Resume without checking prerequisites
❌ Skip validation steps
❌ Resume if PLAN exceeds size limits
❌ Resume without updating ACTIVE_PLANS.md

═══════════════════════════════════════════════════════════════════════

Now resuming PLAN...

1. Complete Pre-Resume Checklist above
2. Generate prompt for next achievement:
   python LLM/scripts/generation/generate_prompt.py @{plan_path} --next --clipboard
3. Begin work on Achievement {next_achievement}
"""


def generate_resume_prompt(plan_path: Path) -> str:
    """Generate resume prompt for PLAN."""
    info = extract_plan_info(plan_path)

    return RESUME_PROMPT_TEMPLATE.format(
        plan_path=info["plan_path"],
        feature_name=info["feature_name"],
        next_achievement=info["next_achievement"],
        next_title=info["next_title"],
        archive_location=info["archive_location"],
    )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate prompt to resume a paused PLAN",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python LLM/scripts/generation/generate_resume_prompt.py @PLAN_FEATURE.md
  python LLM/scripts/generation/generate_resume_prompt.py @PLAN_FEATURE.md --clipboard

Exit Codes:
  0 = Success
  1 = Error (file not found, parsing failed, etc.)
        """,
    )

    parser.add_argument("plan_file", help="PLAN file (e.g., @PLAN_FEATURE.md or PLAN_FEATURE.md)")

    parser.add_argument("--clipboard", action="store_true", help="Copy prompt to clipboard")

    args = parser.parse_args()

    try:
        # Clean file path
        plan_path = Path(args.plan_file.replace("@", ""))

        # If not found, check work-space/plans/ (workspace structure support)
        if not plan_path.exists():
            # Only check workspace if path is relative (not absolute)
            if not plan_path.is_absolute():
                workspace_path = Path("work-space/plans") / plan_path.name
                if workspace_path.exists():
                    plan_path = workspace_path
                else:
                    # File not found - show all checked locations
                    print(f"❌ Error: File not found: {args.plan_file.replace('@', '')}")
                    print(f"   Checked: {plan_path}")
                    print(f"   Checked: {workspace_path}")
                    sys.exit(1)
            else:
                # Absolute path not found
                print(f"❌ Error: File not found: {plan_path}")
                sys.exit(1)

        # Generate prompt
        prompt = generate_resume_prompt(plan_path)

        # Output
        print(prompt)

        # Clipboard support
        if args.clipboard:
            try:
                import pyperclip

                pyperclip.copy(prompt)
                print("\n✅ Prompt copied to clipboard!")
            except ImportError:
                print("\n⚠️  Install pyperclip for clipboard support: pip install pyperclip")

        sys.exit(0)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
