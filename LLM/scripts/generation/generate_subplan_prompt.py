#!/usr/bin/env python3
"""
SUBPLAN Prompt Generator - Generate prompts for SUBPLAN lifecycle

Supports 3 modes:
1. Create SUBPLAN: Generate prompt to create SUBPLAN for a PLAN achievement
2. Continue SUBPLAN: Generate prompt to continue SUBPLAN work
3. Synthesize SUBPLAN: Generate prompt to synthesize results from all EXECUTIONs

Usage:
    # Mode 1: Create SUBPLAN
    python LLM/scripts/generation/generate_subplan_prompt.py create @PLAN_FEATURE.md --achievement 1.1

    # Mode 2: Continue SUBPLAN
    python LLM/scripts/generation/generate_subplan_prompt.py continue @SUBPLAN_FEATURE_11.md

    # Mode 3: Synthesize SUBPLAN
    python LLM/scripts/generation/generate_subplan_prompt.py synthesize @SUBPLAN_FEATURE_11.md

    # Auto-detect next step
    python LLM/scripts/generation/generate_subplan_prompt.py --next @SUBPLAN_FEATURE_11.md

    # Copy to clipboard
    python LLM/scripts/generation/generate_subplan_prompt.py create @PLAN_FEATURE.md --achievement 1.1 --clipboard
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Optional, List, Dict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Import shared path resolution (Bug #9 fix)
try:
    from LLM.scripts.generation.path_resolution import resolve_plan_path, copy_to_clipboard_safe
except ImportError as e:
    # Fallback for development/testing
    print(f"Warning: Could not import path_resolution: {e}", file=sys.stderr)
    def resolve_plan_path(path_str: str, file_type: str = "PLAN") -> Path:
        """Fallback: strip @ and check existence."""
        path = Path(path_str.lstrip("@"))
        if not path.exists():
            print(f"Error: File not found: {path}", file=sys.stderr)
            sys.exit(1)
        return path
    
    def copy_to_clipboard_safe(text: str, enabled: bool = True) -> bool:
        """Fallback: no clipboard support."""
        return False

# Import structure detection for dual structure support
try:
    from LLM.scripts.workflow.structure_detection import detect_structure
except ImportError:
    # Fallback if structure_detection not available (backward compatibility)
    def detect_structure(plan_path: Path) -> str:
        """Fallback: always return flat structure."""
        return "flat"


def extract_achievement_section(plan_content: str, achievement_num: str) -> Optional[str]:
    """
    Extract achievement section from PLAN content.

    Args:
        plan_content: Full PLAN file content
        achievement_num: Achievement number (e.g., "1.1")

    Returns:
        Achievement section content, or None if not found
    """
    lines = plan_content.split("\n")
    section_start = None

    # Find achievement section start
    pattern = rf"\*\*Achievement\s+{re.escape(achievement_num)}\*\*"
    for i, line in enumerate(lines):
        if re.search(pattern, line, re.IGNORECASE):
            section_start = i
            break

    if section_start is None:
        return None

    # Find section end (next achievement or major section)
    section_end = len(lines)
    for i in range(section_start + 1, len(lines)):
        line = lines[i]
        # Stop at next achievement
        if re.match(r"\*\*Achievement\s+\d+\.\d+\*\*", line):
            section_end = i
            break
        # Stop at major section (##)
        if re.match(r"^##\s+", line) and i > section_start + 5:
            section_end = i
            break

    return "\n".join(lines[section_start:section_end])


def extract_current_status(plan_content: str) -> Optional[str]:
    """Extract 'Current Status & Handoff' section from PLAN."""
    lines = plan_content.split("\n")
    section_start = None

    # Find section start
    for i, line in enumerate(lines):
        if re.search(r"##\s*.*Current Status.*Handoff", line, re.IGNORECASE):
            section_start = i
            break

    if section_start is None:
        return None

    # Find section end (next major section or end of file)
    section_end = len(lines)
    for i in range(section_start + 1, len(lines)):
        if re.match(r"^##\s+", line):
            section_end = i
            break

    # Limit to ~14 lines as per context budget
    section_lines = lines[section_start : min(section_start + 14, section_end)]
    return "\n".join(section_lines)


def get_subplan_status(subplan_content: str) -> Dict[str, any]:
    """
    Analyze SUBPLAN status and determine current phase.

    Returns:
        Dict with: phase, has_executions, active_count, completed_count
    """
    status = {
        "phase": "Design",  # Design, Execution Planning, Execution, Synthesis
        "has_executions": False,
        "active_count": 0,
        "completed_count": 0,
    }

    # Check for Execution Strategy section
    if re.search(r"##\s*🔄\s*Execution Strategy", subplan_content, re.IGNORECASE):
        status["phase"] = "Execution Planning"

    # Check Active EXECUTION_TASKs section
    active_match = re.search(
        r"##\s*🔄\s*Active EXECUTION_TASKs",
        subplan_content,
        re.IGNORECASE,
    )
    if active_match:
        status["has_executions"] = True
        status["phase"] = "Execution"

        # Count active executions
        active_section = subplan_content[active_match.start() :]
        # Count table rows or list items
        active_count = len(
            re.findall(
                r"EXECUTION_TASK.*Planning|EXECUTION_TASK.*Executing", active_section, re.IGNORECASE
            )
        )
        status["active_count"] = active_count

    # Check for Execution Results Synthesis section
    if re.search(r"##\s*📊\s*Execution Results Synthesis", subplan_content, re.IGNORECASE):
        status["phase"] = "Synthesis"

    # Check for completed executions (in synthesis section or references)
    completed_count = len(
        re.findall(r"EXECUTION_TASK.*Complete|✅.*EXECUTION", subplan_content, re.IGNORECASE)
    )
    status["completed_count"] = completed_count

    return status


def find_plan_from_subplan(subplan_path: Path) -> Optional[Path]:
    """
    Find PLAN file from SUBPLAN path (for structure detection).

    Supports both flat and nested structures:
    - Flat: SUBPLAN in work-space/subplans/, PLAN in work-space/plans/
    - Nested: SUBPLAN in plan_folder/subplans/, PLAN in plan_folder/

    Args:
        subplan_path: Path to SUBPLAN file

    Returns:
        Path to PLAN file, or None if not found
    """
    # Check if nested structure (subplan is in a subplans/ subdirectory)
    if subplan_path.parent.name == "subplans":
        plan_folder = subplan_path.parent.parent
        # Look for PLAN file in parent folder
        for plan_file in plan_folder.glob("PLAN_*.md"):
            return plan_file

    # Flat structure: extract feature name from SUBPLAN filename
    match = re.match(r"SUBPLAN_([A-Z0-9_-]+)_\d+\.md", subplan_path.name)
    if match:
        feature_name = match.group(1)
        plan_path = Path(f"work-space/plans/PLAN_{feature_name}.md")
        if plan_path.exists():
            return plan_path

    return None


def find_execution_files(subplan_path: Path) -> List[Path]:
    """
    Find all EXECUTION_TASK files referenced in SUBPLAN.

    Supports both flat and nested workspace structures:
    - Flat: work-space/execution/EXECUTION_TASK_*.md
    - Nested: plan_folder/execution/EXECUTION_TASK_*.md

    Args:
        subplan_path: Path to SUBPLAN file

    Returns:
        List of EXECUTION_TASK file paths
    """
    with open(subplan_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find EXECUTION_TASK references
    execution_pattern = r"EXECUTION_TASK_([A-Z_-]+)_(\d+)_(\d+)"
    matches = re.findall(execution_pattern, content)

    # Detect structure by finding PLAN
    plan_path = find_plan_from_subplan(subplan_path)
    structure = "flat"  # Default for backward compatibility
    plan_folder = None
    if plan_path and plan_path.exists():
        structure = detect_structure(plan_path)
        plan_folder = plan_path.parent

    execution_files = []
    for match in matches:
        feature, subplan_num, exec_num = match
        pattern = f"EXECUTION_TASK_{feature}_{subplan_num}_{exec_num}.md"

        # Check nested structure first (if detected)
        if structure == "nested" and plan_folder:
            nested_execution = plan_folder / "execution" / pattern
            if nested_execution.exists():
                execution_files.append(nested_execution)
                continue

        # Check flat structure
        flat_execution = Path("work-space/execution") / pattern
        if flat_execution.exists():
            execution_files.append(flat_execution)
            continue

        # Check archive locations (both structures)
        for archive_base in [
            Path("documentation/archive"),
            Path("feature-archive"),
        ]:
            if archive_base.exists():
                for archive_dir in archive_base.iterdir():
                    if archive_dir.is_dir():
                        # Check nested archive structure
                        nested_archive_execution = archive_dir / "execution" / pattern
                        if nested_archive_execution.exists():
                            execution_files.append(nested_archive_execution)
                            break
                        # Check flat archive structure (legacy)
                        flat_archive_execution = archive_dir / pattern
                        if flat_archive_execution.exists():
                            execution_files.append(flat_archive_execution)
                            break

    return execution_files


def extract_execution_summary(execution_path: Path) -> Optional[str]:
    """Extract summary from EXECUTION_TASK file."""
    try:
        with open(execution_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract Learning Summary section
        learning_match = re.search(
            r"##\s*📊\s*Learning Summary(.*?)(?=##|\Z)",
            content,
            re.DOTALL | re.IGNORECASE,
        )
        if learning_match:
            return learning_match.group(1).strip()[:500]  # Limit length

        # Fallback: Extract completion status
        completion_match = re.search(
            r"##\s*✅\s*Completion Status(.*?)(?=##|\Z)",
            content,
            re.DOTALL | re.IGNORECASE,
        )
        if completion_match:
            return completion_match.group(1).strip()[:500]

        return None
    except Exception:
        return None


def generate_create_prompt(plan_path: Path, achievement_num: str) -> str:
    """Generate prompt for creating SUBPLAN."""
    with open(plan_path, "r", encoding="utf-8") as f:
        plan_content = f.read()

    achievement_section = extract_achievement_section(plan_content, achievement_num)
    current_status = extract_current_status(plan_content)

    if not achievement_section:
        return f"Error: Achievement {achievement_num} not found in PLAN"

    prompt = f"""Execute Achievement {achievement_num} in @{plan_path.name} following strict methodology.

═══════════════════════════════════════════════════════════════════════

CONTEXT BOUNDARIES (Read ONLY These):

✅ @{plan_path.name} - Achievement {achievement_num} section only ({len(achievement_section.split(chr(10)))} lines)

✅ @{plan_path.name} - "Current Status & Handoff" section ({len(current_status.split(chr(10))) if current_status else 0} lines)

❌ DO NOT READ: Full PLAN, other achievements, archived work

CONTEXT BUDGET: {len(achievement_section.split(chr(10))) + (len(current_status.split(chr(10))) if current_status else 0)} lines maximum

═══════════════════════════════════════════════════════════════════════

ACHIEVEMENT {achievement_num}:

{achievement_section}

═══════════════════════════════════════════════════════════════════════

REQUIRED STEPS (No Shortcuts):

Step 1: Create SUBPLAN (MANDATORY)
- File: SUBPLAN_[FEATURE]_{achievement_num.replace('.', '')}.md
- Size: 200-600 lines
- Must include: Objective, Deliverables, Approach, Execution Strategy, Tests, Expected Results
- Reference: LLM/templates/SUBPLAN-TEMPLATE.md
- Guide: LLM/guides/SUBPLAN-WORKFLOW-GUIDE.md (Phase 1: Design)

Step 2: Plan Execution(s) (MANDATORY)
- Decide: Single or Multiple EXECUTIONs?
- Decide: Parallel or Sequential?
- Document in SUBPLAN "Execution Strategy" section
- Reference: LLM/guides/SUBPLAN-WORKFLOW-GUIDE.md (Phase 2: Execution Planning)

Step 3: Review and Finalize
- Verify SUBPLAN is complete (200-600 lines)
- Ensure all sections present
- Ready for executor to create EXECUTION_TASK

═══════════════════════════════════════════════════════════════════════

DO NOT:
❌ Create EXECUTION_TASK (that's the executor's job)
❌ Implement the work (wait for EXECUTION phase)
❌ Mark achievement complete (only after execution)
❌ Skip SUBPLAN ("it's simple" - NO, all work needs SUBPLANs)
❌ Read full PLAN (read Achievement {achievement_num} only)

REMEMBER:
✓ SUBPLAN is design phase only
✓ Executor will create EXECUTION_TASK separately
✓ Follow SUBPLAN-TEMPLATE.md structure
✓ Follow SUBPLAN-WORKFLOW-GUIDE.md (Design & Planning phases)

═══════════════════════════════════════════════════════════════════════

Now beginning Achievement {achievement_num} SUBPLAN design:

Creating SUBPLAN..."""

    return prompt


def generate_continue_prompt(subplan_path: Path) -> str:
    """Generate prompt for continuing SUBPLAN work."""
    with open(subplan_path, "r", encoding="utf-8") as f:
        subplan_content = f.read()

    status = get_subplan_status(subplan_content)

    # Determine next step based on phase
    if status["phase"] == "Design":
        next_step = "Complete SUBPLAN design, then plan execution(s)"
    elif status["phase"] == "Execution Planning":
        next_step = "Create EXECUTION_TASK(s) according to plan"
    elif status["phase"] == "Execution":
        if status["active_count"] > 0:
            next_step = (
                f"Monitor {status['active_count']} active EXECUTION(s), or create new if needed"
            )
        else:
            next_step = "All EXECUTIONs complete - ready for synthesis"
    else:  # Synthesis
        next_step = "Complete synthesis, mark SUBPLAN complete"

    prompt = f"""Continue SUBPLAN work: @{subplan_path.name}

═══════════════════════════════════════════════════════════════════════

SUBPLAN STATUS:

- Phase: {status['phase']}
- Active EXECUTIONs: {status['active_count']}
- Completed EXECUTIONs: {status['completed_count']}

NEXT STEP: {next_step}

═══════════════════════════════════════════════════════════════════════

CONTEXT BOUNDARIES:

✅ READ ONLY:
- This SUBPLAN file (complete file)
- Active EXECUTION_TASKs (if any)
- Parent PLAN current achievement section (50-100 lines)
- Parent PLAN "Current Status & Handoff" section (30-50 lines)

❌ DO NOT READ:
- Parent PLAN full content
- Other achievements
- Completed EXECUTION_TASKs (unless needed for synthesis)

CONTEXT BUDGET: ~400-600 lines

═══════════════════════════════════════════════════════════════════════

WORKFLOW:

Reference: LLM/guides/SUBPLAN-WORKFLOW-GUIDE.md

Current Phase: {status['phase']}

If Design Phase:
- Complete SUBPLAN design
- Plan execution(s) (single or multiple?)
- Document in "Execution Strategy" section

If Execution Planning Phase:
- Create EXECUTION_TASK file(s)
- Document in "Planned Executions" section
- Update "Active EXECUTION_TASKs" section

If Execution Phase:
- Monitor active EXECUTIONs
- Update "Active EXECUTION_TASKs" status
- If all complete: Move to Synthesis

If Synthesis Phase:
- Review all EXECUTION results
- Synthesize learnings
- Update "Execution Results Synthesis" section
- Mark SUBPLAN complete

═══════════════════════════════════════════════════════════════════════

Now continuing SUBPLAN work..."""

    return prompt


def generate_synthesize_prompt(subplan_path: Path) -> str:
    """Generate prompt for synthesizing SUBPLAN results."""
    with open(subplan_path, "r", encoding="utf-8") as f:
        subplan_content = f.read()

    execution_files = find_execution_files(subplan_path)

    if not execution_files:
        return f"Error: No EXECUTION_TASK files found for SUBPLAN {subplan_path.name}"

    execution_summaries = []
    for exec_file in execution_files:
        summary = extract_execution_summary(exec_file)
        if summary:
            execution_summaries.append(f"**{exec_file.name}**:\n{summary}\n")

    prompt = f"""Synthesize SUBPLAN results: @{subplan_path.name}

═══════════════════════════════════════════════════════════════════════

SUBPLAN SYNTHESIS TASK:

Review all EXECUTION results and synthesize learnings.

EXECUTION SUMMARIES:

{chr(10).join(execution_summaries) if execution_summaries else "No summaries available"}

═══════════════════════════════════════════════════════════════════════

CONTEXT BOUNDARIES:

✅ READ ONLY:
- This SUBPLAN file (complete file)
- All completed EXECUTION_TASK files
- Parent PLAN current achievement section

❌ DO NOT READ:
- Parent PLAN full content
- Other achievements
- Active/incomplete EXECUTION_TASKs

CONTEXT BUDGET: ~600 lines (SUBPLAN + EXECUTION summaries)

═══════════════════════════════════════════════════════════════════════

SYNTHESIS STEPS:

1. Review All EXECUTION Results
   - Read all EXECUTION_TASK Learning Summary sections
   - Understand what each achieved
   - Note learnings from each

2. Synthesize Collective Learnings
   - What worked across all EXECUTIONs?
   - What didn't work?
   - What patterns emerged?
   - What should be adopted?

3. Compare Results (if multiple EXECUTIONs)
   - Compare side-by-side
   - Which approach performed best?
   - Why did one succeed over others?

4. Update SUBPLAN
   - Add/update "Execution Results Synthesis" section
   - Document collective learnings
   - Note best approach (if multiple)
   - Capture insights

5. Mark SUBPLAN Complete
   - Update status to "Complete"
   - Verify all deliverables exist
   - Ensure quality standards met

═══════════════════════════════════════════════════════════════════════

Reference: LLM/guides/SUBPLAN-WORKFLOW-GUIDE.md (Phase 4: Synthesis)

Now synthesizing SUBPLAN results..."""

    return prompt


def auto_detect_mode(subplan_path: Path) -> str:
    """Auto-detect which mode to use based on SUBPLAN status."""
    with open(subplan_path, "r", encoding="utf-8") as f:
        content = f.read()

    status = get_subplan_status(content)

    if status["phase"] == "Synthesis" and status["completed_count"] > 0:
        return "synthesize"
    elif status["phase"] in ["Design", "Execution Planning", "Execution"]:
        return "continue"
    else:
        return "continue"  # Default


def copy_to_clipboard(text: str) -> bool:
    """Copy text to clipboard."""
    try:
        import pyperclip

        pyperclip.copy(text)
        return True
    except ImportError:
        try:
            import subprocess

            process = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE, text=True)
            process.communicate(input=text)
            return True
        except Exception:
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Generate prompts for SUBPLAN lifecycle",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create SUBPLAN
  python generate_subplan_prompt.py create @PLAN_FEATURE.md --achievement 1.1
  
  # Continue SUBPLAN
  python generate_subplan_prompt.py continue @SUBPLAN_FEATURE_11.md
  
  # Synthesize SUBPLAN
  python generate_subplan_prompt.py synthesize @SUBPLAN_FEATURE_11.md
  
  # Auto-detect next step
  python generate_subplan_prompt.py --next @SUBPLAN_FEATURE_11.md
        """,
    )

    parser.add_argument(
        "mode",
        nargs="?",
        choices=["create", "continue", "synthesize"],
        help="Mode: create, continue, or synthesize",
    )
    parser.add_argument(
        "file",
        type=str,
        help="PLAN file (for create) or SUBPLAN file (for continue/synthesize)",
    )
    parser.add_argument(
        "--achievement",
        type=str,
        help="Achievement number (e.g., '1.1') - required for create mode",
    )
    parser.add_argument(
        "--next",
        action="store_true",
        help="Auto-detect next step (requires SUBPLAN file)",
    )
    parser.add_argument(
        "--clipboard",
        action="store_true",
        help="Copy prompt to clipboard",
    )

    args = parser.parse_args()

    # Resolve path with @ shorthand support (Bug #9 fix)
    # Determine file type based on mode
    if args.file.startswith('@') and ('PLAN_' in args.file or args.mode == 'create'):
        file_type = "PLAN"
    elif args.file.startswith('@') and 'SUBPLAN_' in args.file:
        file_type = "SUBPLAN"
    else:
        file_type = "FILE"
    
    file_path = resolve_plan_path(args.file, file_type=file_type)

    # Auto-detect mode if --next flag
    if args.next:
        if not file_path.name.startswith("SUBPLAN_"):
            print("Error: --next requires SUBPLAN file", file=sys.stderr)
            sys.exit(1)
        mode = auto_detect_mode(file_path)
    else:
        mode = args.mode

    if not mode:
        print("Error: Mode required (create, continue, synthesize) or use --next", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    # Generate prompt based on mode
    if mode == "create":
        if not args.achievement:
            print("Error: --achievement required for create mode", file=sys.stderr)
            sys.exit(1)
        prompt = generate_create_prompt(file_path, args.achievement)
    elif mode == "continue":
        prompt = generate_continue_prompt(file_path)
    elif mode == "synthesize":
        prompt = generate_synthesize_prompt(file_path)
    else:
        print(f"Error: Unknown mode: {mode}", file=sys.stderr)
        sys.exit(1)

    # Output prompt
    print(prompt)

    # Copy to clipboard if requested
    if args.clipboard:
        if copy_to_clipboard(prompt):
            print("\n✅ Prompt copied to clipboard", file=sys.stderr)
        else:
            print(
                "\n⚠️  Could not copy to clipboard (install pyperclip or use pbcopy)",
                file=sys.stderr,
            )


if __name__ == "__main__":
    main()
