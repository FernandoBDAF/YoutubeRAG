#!/usr/bin/env python3
"""
Generate prompt to pause a PLAN following IMPLEMENTATION_RESUME.md protocol.

Usage:
    python LLM/scripts/generation/generate_pause_prompt.py @PLAN_FEATURE.md
    python LLM/scripts/generation/generate_pause_prompt.py @PLAN_FEATURE.md --clipboard
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

    # Find current achievement (prioritize "Next Achievement" over "Paused At")
    current_achievement = None

    # Priority 1: Check "Next Achievement" (what to work on next)
    next_match = re.search(r"\*\*Next Achievement\*\*[:\s]+(\d+\.\d+)", content, re.IGNORECASE)
    if next_match:
        current_achievement = next_match.group(1)

    # Priority 2: Check "What's Next" section
    if not current_achievement:
        next_match = re.search(
            r"(?:What\'s Next|Next)[:\s]+Achievement\s+(\d+\.\d+)", content, re.IGNORECASE
        )
        if next_match:
            current_achievement = next_match.group(1)

    # Priority 3: Check if already paused (has "Paused At" section)
    if not current_achievement:
        paused_match = re.search(r"Paused At[:\s]+Achievement\s+(\d+\.\d+)", content, re.IGNORECASE)
        if paused_match:
            current_achievement = paused_match.group(1)

    # Fallback: Find last completed achievement
    if not current_achievement:
        matches = re.findall(r"✅ Achievement (\d+\.\d+) complete", content)
        if matches:
            current_achievement = matches[-1]

    return {
        "feature_name": feature_name,
        "next_achievement": current_achievement or "X.Y",
        "plan_path": plan_path.name,
    }


PAUSE_PROMPT_TEMPLATE = """Pause @{plan_path} at Achievement {achievement} following @LLM/protocols/IMPLEMENTATION_RESUME.md

═══════════════════════════════════════════════════════════════════════

PRE-PAUSE CHECKLIST:

Step 1: Update PLAN "Current Status & Handoff" Section
- [ ] Document: What's done (list completed achievements)
- [ ] Document: What's next (next achievement to tackle)
- [ ] Document: Any blockers or notes
- [ ] Update "Last Updated" timestamp
- [ ] Update progress percentage

Step 2: Verify Current State
- [ ] All completed work is committed
- [ ] No uncommitted changes in working directory
- [ ] All SUBPLANs/EXECUTION_TASKs archived (if complete)

Step 3: Update ACTIVE_PLANS.md (REQUIRED)
- [ ] Mark PLAN status as "⏸️ Paused"
- [ ] Update "Last Updated" timestamp
- [ ] Add note: "Paused at Achievement {achievement}"
- [ ] Verify only ONE PLAN "In Progress" (should be 0)

Step 4: Commit Pause State
- [ ] Commit all changes: git commit -m "Pausing {feature_name} at Achievement {achievement}"
- [ ] Verify: git status clean

═══════════════════════════════════════════════════════════════════════

VALIDATION ENFORCEMENT:

Before pausing, these scripts will run:
✓ check_plan_size.py (validates PLAN still within limits)
✓ validate_mid_plan.py (checks statistics accuracy)

If issues found: BLOCKS with error + fix prompt

DO NOT:
❌ Pause without updating "Current Status & Handoff"
❌ Pause without updating ACTIVE_PLANS.md
❌ Leave uncommitted changes
❌ Skip validation steps

═══════════════════════════════════════════════════════════════════════

Now pausing PLAN...

1. Update PLAN "Current Status & Handoff" section
2. Update ACTIVE_PLANS.md
3. Commit pause state
4. Ready to switch context
"""


def generate_pause_prompt(plan_path: Path) -> str:
    """Generate pause prompt for PLAN."""
    info = extract_plan_info(plan_path)

    return PAUSE_PROMPT_TEMPLATE.format(
        plan_path=info["plan_path"],
        feature_name=info["feature_name"],
        achievement=info["next_achievement"] or "X.Y",
    )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate prompt to pause a PLAN",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python LLM/scripts/generation/generate_pause_prompt.py @PLAN_FEATURE.md
  python LLM/scripts/generation/generate_pause_prompt.py @PLAN_FEATURE.md --clipboard

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
        prompt = generate_pause_prompt(plan_path)

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
