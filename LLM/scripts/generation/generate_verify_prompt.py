#!/usr/bin/env python3
"""
Generate prompt to verify PLAN status and fix inconsistencies.

This script runs validate_mid_plan.py and generates a fix prompt if issues are found.

Usage:
    python LLM/scripts/generation/generate_verify_prompt.py @PLAN_FEATURE.md
    python LLM/scripts/generation/generate_verify_prompt.py @PLAN_FEATURE.md --clipboard
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_validation(plan_path: Path) -> tuple[bool, str]:
    """Run validate_mid_plan.py and return result."""
    try:
        result = subprocess.run(
            ["python", "LLM/scripts/validation/validate_mid_plan.py", str(plan_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0, result.stdout
    except Exception as e:
        return False, f"Error running validation: {e}"


VERIFY_PROMPT_TEMPLATE = """Verify and fix inconsistencies in @{plan_path}

═══════════════════════════════════════════════════════════════════════

VERIFICATION RESULTS:

{validation_output}

═══════════════════════════════════════════════════════════════════════

FIX PROMPT:

{fix_instructions}

═══════════════════════════════════════════════════════════════════════

VALIDATION ENFORCEMENT:

After fixing, run validation again:
  python LLM/scripts/validation/validate_mid_plan.py @{plan_path}

If validation passes, PLAN is ready to continue.

DO NOT:
❌ Continue without fixing issues
❌ Skip validation steps
❌ Ignore statistics mismatches

═══════════════════════════════════════════════════════════════════════

Now fixing PLAN inconsistencies...
"""


def generate_verify_prompt(plan_path: Path) -> str:
    """Generate verify/fix prompt for PLAN."""
    is_valid, validation_output = run_validation(plan_path)

    if is_valid:
        fix_instructions = (
            "✅ PLAN is compliant! No fixes needed.\n\nYou can continue with the next achievement."
        )
    else:
        # Extract fix instructions from validation output
        if "Fix Prompt:" in validation_output:
            fix_instructions = validation_output.split("Fix Prompt:")[-1].strip()
        else:
            fix_instructions = "Review validation output above and fix all reported issues."

    return VERIFY_PROMPT_TEMPLATE.format(
        plan_path=plan_path.name,
        validation_output=validation_output,
        fix_instructions=fix_instructions,
    )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate prompt to verify PLAN status and fix inconsistencies",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python LLM/scripts/generation/generate_verify_prompt.py @PLAN_FEATURE.md
  python LLM/scripts/generation/generate_verify_prompt.py @PLAN_FEATURE.md --clipboard

This script:
  1. Runs validate_mid_plan.py
  2. Generates fix prompt if issues found
  3. Provides clear instructions to resolve inconsistencies

Exit Codes:
  0 = Success (prompt generated)
  1 = Error (file not found, validation failed, etc.)
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
        prompt = generate_verify_prompt(plan_path)

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
