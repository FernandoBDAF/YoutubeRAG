#!/usr/bin/env python3
"""
Generate FIX-Specific Prompts for Achievement Fixes

This script detects FIX_XX.md feedback files and generates specialized prompts
to guide executors in addressing reviewer feedback.

**Purpose**: Close the feedback loop by automating fix guidance
**Part of**: Feedback System (Achievement 2.5 conventions, 2.9 detection)
**Created**: 2025-11-13
**Achievement**: 2.9 - Implement FIX Feedback Detection & Prompt Generation

**Workflow**:
1. Detect FIX_XX.md file (via get_achievement_status() == "needs_fix")
2. Parse FIX file (extract issues, code references, metadata)
3. Generate structured fix prompt with action plan
4. Provide FIX_RESOLUTION template for re-review

**Usage**:
    python generate_fix_prompt.py @PLAN_FEATURE.md 2.1
    python generate_fix_prompt.py path/to/PLAN.md 0.3 --clipboard
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path for imports
project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from LLM.scripts.generation.utils import get_achievement_status, copy_to_clipboard_safe


def extract_fix_issues(fix_file_path: Path) -> Dict[str, any]:
    """
    Extract issues and code references from FIX_XX.md file.

    Parses FIX feedback file to extract:
    - Metadata (reviewer, date, status)
    - Critical issues (with titles and descriptions)
    - Minor issues (bullet list)
    - Code references (@Python (779-1075), @TypeScript (45-120), etc.)
    - What worked well (positive feedback)

    **Parser Strategy**:
    - Uses regex for markdown section extraction
    - Handles variations in formatting (some FIX files might omit sections)
    - Returns empty lists for missing sections (graceful handling)

    Args:
        fix_file_path: Path to FIX_XX.md file

    Returns:
        Dictionary with extracted data:
        {
            "critical_issues": List[Dict],  # [{title, body}, ...]
            "minor_issues": List[Dict],     # [{text}, ...]
            "code_references": List[str],   # ["@Python (779-1075)", ...]
            "what_worked_well": List[str],  # ["Item 1", "Item 2", ...]
            "reviewer": str,
            "review_date": str,
            "status": str
        }

    Example:
        >>> issues = extract_fix_issues(Path("FIX_21.md"))
        >>> len(issues["critical_issues"])
        3
        >>> issues["critical_issues"][0]["title"]
        "PRIMARY OBJECTIVE NOT ACHIEVED"

    Achievement: 2.9 - FIX Prompt Generation
    """
    with open(fix_file_path, "r", encoding="utf-8") as f:
        content = f.read()

    result = {
        "critical_issues": [],
        "minor_issues": [],
        "code_references": [],
        "what_worked_well": [],
        "reviewer": "Unknown",
        "review_date": "Unknown",
        "status": "NEEDS FIXES",
    }

    # Extract metadata from header
    reviewer_match = re.search(r"\*\*Reviewer\*\*:\s*(.+)", content)
    if reviewer_match:
        result["reviewer"] = reviewer_match.group(1).strip()

    date_match = re.search(r"\*\*Review Date\*\*:\s*(.+)", content)
    if date_match:
        result["review_date"] = date_match.group(1).strip()

    status_match = re.search(r"\*\*Status\*\*:\s*(.+)", content)
    if status_match:
        result["status"] = status_match.group(1).strip()

    # Extract Critical Issues section
    # Format: ### Critical Issues ... #### 1. **Title** ... body text ... #### 2. ...
    critical_section = re.search(
        r"### Critical Issues.*?\n+(.*?)(?=^### [^#]|^## [^#]|\Z)",
        content,
        re.DOTALL | re.IGNORECASE | re.MULTILINE,
    )
    if critical_section:
        critical_text = critical_section.group(1)
        # Parse individual issues (starts with ####)
        # Pattern: #### 1. **Title** (optional emoji) ... body
        # Capture everything until next #### or end
        issues = re.findall(
            r"####\s+\d+\.\s+\*\*(.+?)\*\*(?:\s+[⚠️🚨💡🔴]*)?[^\n]*\n+(.*?)(?=^####|\Z)",
            critical_text,
            re.DOTALL | re.MULTILINE,
        )
        for title, body in issues:
            result["critical_issues"].append({"title": title.strip(), "body": body.strip()})

    # Extract Minor Issues section
    # Format: ### Minor Issues ... - Item 1 ... - Item 2
    minor_section = re.search(
        r"### Minor Issues.*?\n(.*?)(?=###[^#]|\n---|\Z)", content, re.DOTALL | re.IGNORECASE
    )
    if minor_section:
        minor_text = minor_section.group(1)
        # Parse bullet points
        issues = re.findall(r"^-\s+(.+)$", minor_text, re.MULTILINE)
        result["minor_issues"] = [{"text": issue.strip()} for issue in issues]

    # Extract code references (@Python, @TypeScript, @JavaScript patterns)
    # Format: @FileType (start-end)
    code_refs = re.findall(r"@(\w+)\s*\((\d+-\d+)\)", content)
    for file_type, line_range in code_refs:
        result["code_references"].append(f"@{file_type} ({line_range})")

    # Remove duplicates from code references
    result["code_references"] = list(set(result["code_references"]))
    result["code_references"].sort()  # Sort for consistent output

    # Extract "What Worked Well" section
    # Format: ## What Worked Well ... - Item 1 ... - Item 2
    worked_well_section = re.search(
        r"## What Worked Well.*?\n(.*?)(?=##[^#]|\n---|\Z)", content, re.DOTALL | re.IGNORECASE
    )
    if worked_well_section:
        worked_well_text = worked_well_section.group(1)
        items = re.findall(r"^-\s+(.+)$", worked_well_text, re.MULTILINE)
        result["what_worked_well"] = [item.strip() for item in items]

    return result


# FIX Prompt Template
FIX_PROMPT_TEMPLATE = """Address fixes for Achievement {achievement} in @{plan_name}

═══════════════════════════════════════════════════════════════════════

⚠️  REVIEWER FEEDBACK: NEEDS FIXES

Reviewer: {reviewer}
Review Date: {review_date}
Status: {status}
Feedback File: execution/feedbacks/FIX_{achievement_clean}.md

═══════════════════════════════════════════════════════════════════════

CRITICAL ISSUES TO FIX:

{critical_issues}

═══════════════════════════════════════════════════════════════════════

{minor_issues_section}

═══════════════════════════════════════════════════════════════════════

CODE REFERENCES FROM FEEDBACK:

{code_references}

═══════════════════════════════════════════════════════════════════════

WHAT WORKED WELL (Acknowledged):

{what_worked_well}

═══════════════════════════════════════════════════════════════════════

FIX ACTION PLAN:

Step 1: Review Feedback File
- Read complete feedback: execution/feedbacks/FIX_{achievement_clean}.md
- Understand all critical and minor issues
- Note code references for investigation

Step 2: Address Critical Issues (REQUIRED)
{critical_action_items}

Step 3: Address Minor Issues (RECOMMENDED)
{minor_action_items}

Step 4: Update EXECUTION_TASK
- Document fixes applied
- Update status to reflect resolution
- Add learning summary about issues

Step 5: Request Re-Review
Create: execution/feedbacks/FIX_{achievement_clean}_RESOLUTION.md

Structure:
```markdown
# FIX RESOLUTION: Achievement {achievement}

**Executor**: [Your name/role]
**Resolution Date**: [Date]
**Status**: ✅ FIXES APPLIED

## Summary

[2-3 sentences on fixes applied]

## Critical Issues Resolved

1. [Issue 1 title]
   - Fix Applied: [Description]
   - Verification: [How verified]

2. [Issue 2 title]
   - Fix Applied: [Description]
   - Verification: [How verified]

## Minor Issues Addressed

- [Issue and fix]
- [Issue and fix]

## Verification

- [ ] All critical issues resolved
- [ ] All minor issues addressed or explained
- [ ] Tests passing
- [ ] Deliverables complete
- [ ] Ready for re-review

## Request

Ready for re-review. Please create APPROVED_{achievement_clean}.md if satisfied.
```

═══════════════════════════════════════════════════════════════════════

DO NOT:
❌ Ignore reviewer feedback
❌ Skip critical issues
❌ Assume issues are minor without addressing
❌ Request approval without creating FIX_RESOLUTION

REMEMBER:
✓ Address ALL critical issues (required)
✓ Address or explain ALL minor issues
✓ Update EXECUTION_TASK with learnings
✓ Create FIX_RESOLUTION before requesting re-review
✓ Verify all fixes work as expected

═══════════════════════════════════════════════════════════════════════

Now addressing feedback for Achievement {achievement}...

"""


def generate_fix_prompt(plan_path: Path, achievement_num: str) -> str:
    """
    Generate prompt to address fixes in FIX_XX.md feedback file.

    Main entry point for FIX prompt generation. Loads FIX file, extracts
    issues, and formats them into a comprehensive fix prompt with:
    - Reviewer metadata and feedback file reference
    - Critical issues (numbered, with details)
    - Minor issues (if present)
    - Code references (extracted from @patterns)
    - What worked well (positive acknowledgment)
    - Step-by-step fix action plan
    - FIX_RESOLUTION template for re-review

    Args:
        plan_path: Path to PLAN file
        achievement_num: Achievement number (e.g., "2.1")

    Returns:
        Formatted fix prompt string

    Raises:
        FileNotFoundError: If FIX_XX.md file doesn't exist

    Example:
        >>> prompt = generate_fix_prompt(Path("PLAN.md"), "2.1")
        >>> "CRITICAL ISSUES TO FIX" in prompt
        True

    Achievement: 2.9 - FIX Prompt Generation
    """
    plan_folder = plan_path.parent
    plan_name = plan_path.stem.replace("PLAN_", "")
    ach_num_clean = achievement_num.replace(".", "")
    fix_file = plan_folder / "execution" / "feedbacks" / f"FIX_{ach_num_clean}.md"

    if not fix_file.exists():
        return f"❌ Error: FIX file not found: {fix_file}\n\nExpected file: execution/feedbacks/FIX_{ach_num_clean}.md"

    # Extract issues from FIX file
    issues = extract_fix_issues(fix_file)

    # Format critical issues
    if issues["critical_issues"]:
        critical_text = ""
        for i, issue in enumerate(issues["critical_issues"], 1):
            critical_text += f"{i}. **{issue['title']}**\n\n"
            critical_text += f"{issue['body']}\n\n"
            critical_text += "---\n\n"
        critical_text = critical_text.rstrip("\n\n---\n\n")  # Remove trailing separator
    else:
        critical_text = "(No critical issues specified - check FIX file)"

    # Format minor issues section
    if issues["minor_issues"]:
        minor_text = "MINOR ISSUES (Nice to Fix):\n\n"
        for issue in issues["minor_issues"]:
            minor_text += f"- {issue['text']}\n"
        minor_text += "\n"
    else:
        minor_text = "(No minor issues specified)\n\n"

    # Format code references
    if issues["code_references"]:
        code_refs_text = ""
        for ref in issues["code_references"]:
            code_refs_text += f"- {ref}\n"
        code_refs_text += "\nThese code sections need review/modification based on feedback."
    else:
        code_refs_text = "(No specific code references provided)"

    # Format what worked well
    if issues["what_worked_well"]:
        worked_well_text = ""
        for item in issues["what_worked_well"]:
            worked_well_text += f"- {item}\n"
    else:
        worked_well_text = "(See FIX file for positive feedback)"

    # Generate action items for critical issues
    critical_action_items = ""
    for i, issue in enumerate(issues["critical_issues"], 1):
        critical_action_items += f"- Fix Critical Issue #{i}: {issue['title']}\n"
    if not critical_action_items:
        critical_action_items = "- Review FIX file for specific requirements\n"

    # Generate action items for minor issues
    minor_action_items = ""
    for i, issue in enumerate(issues["minor_issues"], 1):
        # Truncate long issue text for action item
        issue_preview = issue["text"][:60] + "..." if len(issue["text"]) > 60 else issue["text"]
        minor_action_items += f"- Address Minor Issue #{i}: {issue_preview}\n"
    if not minor_action_items:
        minor_action_items = "- Review FIX file for minor improvements\n"

    # Fill template
    prompt = FIX_PROMPT_TEMPLATE.format(
        achievement=achievement_num,
        plan_name=plan_name,
        reviewer=issues["reviewer"],
        review_date=issues["review_date"],
        status=issues["status"],
        achievement_clean=ach_num_clean,
        critical_issues=critical_text,
        minor_issues_section=minor_text,
        code_references=code_refs_text,
        what_worked_well=worked_well_text,
        critical_action_items=critical_action_items,
        minor_action_items=minor_action_items,
    )

    return prompt


def main():
    """
    CLI entry point for generate_fix_prompt.py.

    Supports:
    - @folder shortcuts (e.g., @PROMPT-GENERATOR)
    - Direct PLAN paths
    - Clipboard integration (--clipboard flag)
    """
    parser = argparse.ArgumentParser(
        description="Generate FIX-specific prompt for achievement fixes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_fix_prompt.py @PLAN_FEATURE.md 2.1
  python generate_fix_prompt.py work-space/plans/FEATURE/PLAN_FEATURE.md 0.3 --clipboard
  python generate_fix_prompt.py @GRAPHRAG-OBSERVABILITY 2.1

Workflow:
  1. Detects FIX_XX.md file in execution/feedbacks/
  2. Extracts issues and code references
  3. Generates structured fix prompt
  4. Copies to clipboard (if --clipboard)
        """,
    )
    parser.add_argument("plan_file", help="PLAN file path or @folder shortcut")
    parser.add_argument("achievement", help="Achievement number (e.g., '2.1')")
    parser.add_argument(
        "--clipboard",
        action="store_true",
        help="Copy prompt to clipboard (default: True)",
        default=True,
    )
    parser.add_argument("--no-clipboard", action="store_true", help="Disable clipboard copy")

    args = parser.parse_args()

    # Resolve PLAN path (handle @shortcuts)
    plan_path_str = args.plan_file
    if plan_path_str.startswith("@"):
        # Remove @ and .md extension if present
        folder_name = plan_path_str[1:].replace(".md", "")
        from LLM.scripts.generation.utils import resolve_folder_shortcut

        plan_path = resolve_folder_shortcut(folder_name)
    else:
        plan_path = Path(plan_path_str)

    if not plan_path.exists():
        print(f"❌ Error: PLAN file not found: {plan_path}")
        sys.exit(1)

    # Check achievement status
    status = get_achievement_status(args.achievement, plan_path)

    if status != "needs_fix":
        print(f"⚠️  Achievement {args.achievement} status: {status}")
        print(f"\nExpected 'needs_fix' but got '{status}'")

        if status == "approved":
            print(
                f"✅ Achievement is already approved (APPROVED_{args.achievement.replace('.', '')}.md exists)"
            )
        elif status == "incomplete":
            print(f"ℹ️  No FIX file found (achievement incomplete)")
            print(f"\nExpected: execution/feedbacks/FIX_{args.achievement.replace('.', '')}.md")

        sys.exit(1)

    # Generate FIX prompt
    try:
        prompt = generate_fix_prompt(plan_path, args.achievement)
    except Exception as e:
        print(f"❌ Error generating FIX prompt: {e}")
        sys.exit(1)

    # Output prompt
    print(prompt)

    # Copy to clipboard
    clipboard_enabled = args.clipboard and not args.no_clipboard
    if clipboard_enabled:
        success = copy_to_clipboard_safe(prompt)
        if success:
            print("\n✅ Prompt copied to clipboard!")
        else:
            print("\n⚠️  Clipboard not available, displaying prompt above")


if __name__ == "__main__":
    main()
