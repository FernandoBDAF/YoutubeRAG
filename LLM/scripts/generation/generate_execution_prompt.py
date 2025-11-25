#!/usr/bin/env python3
"""
EXECUTION Prompt Generator - Generate prompts for EXECUTION lifecycle

Supports 3 modes:
1. Create EXECUTION: Generate prompt to create EXECUTION_TASK from SUBPLAN
2. Continue EXECUTION: Generate prompt to continue EXECUTION work
3. Next EXECUTION: Generate prompt to start next EXECUTION in sequence

Usage:
    # Mode 1: Create EXECUTION from SUBPLAN
    python LLM/scripts/generation/generate_execution_prompt.py create @SUBPLAN_FEATURE_11.md --execution 01

    # Mode 2: Continue EXECUTION
    python LLM/scripts/generation/generate_execution_prompt.py continue @EXECUTION_TASK_FEATURE_11_01.md

    # Mode 3: Next EXECUTION
    python LLM/scripts/generation/generate_execution_prompt.py next @SUBPLAN_FEATURE_11.md

    # Parallel executions
    python LLM/scripts/generation/generate_execution_prompt.py create @SUBPLAN_FEATURE_11.md --execution 01 --parallel

    # Copy to clipboard
    python LLM/scripts/generation/generate_execution_prompt.py create @SUBPLAN_FEATURE_11.md --execution 01 --clipboard
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


def extract_subplan_objective(subplan_content: str) -> Optional[str]:
    """
    Extract SUBPLAN objective (1-2 sentences only).

    Args:
        subplan_content: Full SUBPLAN file content

    Returns:
        Objective (1-2 sentences), or None if not found
    """
    # Find Objective section
    objective_match = re.search(
        r"##\s*🎯\s*Objective\s*\n(.*?)(?=\n##\s|\Z)",
        subplan_content,
        re.DOTALL | re.IGNORECASE,
    )

    if not objective_match:
        return None

    objective_text = objective_match.group(1).strip()

    # Extract first 1-2 sentences
    sentences = re.split(r"[.!?]+\s+", objective_text)
    if len(sentences) >= 2:
        return ". ".join(sentences[:2]) + "."
    elif len(sentences) == 1:
        return sentences[0] + "."
    else:
        return objective_text[:200]  # Fallback: first 200 chars


def extract_subplan_approach(subplan_content: str) -> Optional[str]:
    """
    Extract SUBPLAN approach summary (3-5 sentences only).

    Args:
        subplan_content: Full SUBPLAN file content

    Returns:
        Approach summary (3-5 sentences), or None if not found
    """
    # TODO: Replace with structured metadata (see EXECUTION_ANALYSIS_SUBPLAN-EXTRACTION-BUG-8.md)
    # This emoji-agnostic regex is a temporary fix to prevent Bug #9, #10, #11...

    # Find Approach section - emoji-agnostic (matches ANY emoji + "Approach")
    # Unicode ranges: \U0001F300-\U0001F9FF (most common emojis)
    approach_match = re.search(
        r"##\s*[\U0001F300-\U0001F9FF]\s*Approach\s*\n(.*?)(?=\n##\s|\Z)",
        subplan_content,
        re.DOTALL | re.IGNORECASE,
    )

    # Try "Implementation Strategy" if Approach not found
    if not approach_match:
        approach_match = re.search(
            r"##\s*[\U0001F300-\U0001F9FF]\s*Implementation Strategy\s*\n(.*?)(?=\n##\s|\Z)",
            subplan_content,
            re.DOTALL | re.IGNORECASE,
        )

    # Try "Design" section if neither found
    if not approach_match:
        approach_match = re.search(
            r"##\s*[\U0001F300-\U0001F9FF]\s*Design[:\s]+(.*?)(?=\n##\s|\Z)",
            subplan_content,
            re.DOTALL | re.IGNORECASE,
        )

    if not approach_match:
        return None

    approach_text = approach_match.group(1).strip()

    # Check if content is structured with subsections (### headers)
    subsection_matches = re.findall(r"###\s+(.+?)(?:\n|$)", approach_match.group(1))

    if subsection_matches and len(subsection_matches) >= 2:
        # Content is structured - extract phase titles
        clean_titles = []
        for title in subsection_matches[:5]:
            # Remove time estimates in parentheses
            clean_title = re.sub(r"\s*\([^)]*\)\s*$", "", title)
            clean_titles.append(clean_title)
        return "Implementation phases: " + " → ".join(clean_titles)

    # Content is prose - extract first 3-5 sentences
    sentences = re.split(r"[.!?]+\s+", approach_text)
    if len(sentences) >= 5:
        return ". ".join(sentences[:5]) + "."
    elif len(sentences) >= 3:
        return ". ".join(sentences[:3]) + "."
    else:
        return approach_text[:300]  # Fallback: first 300 chars


def extract_parallelization_context(subplan_content: str) -> Optional[Dict[str, any]]:
    """
    Extract parallelization context from SUBPLAN.

    Args:
        subplan_content: Full SUBPLAN file content

    Returns:
        Dict with parallel group info, or None if not parallel
    """
    # Check Planned Executions section
    planned_match = re.search(
        r"##\s*🔀\s*Planned Executions.*?\n(.*?)(?=##|\Z)",
        subplan_content,
        re.DOTALL | re.IGNORECASE,
    )

    if not planned_match:
        return None

    planned_text = planned_match.group(1)

    # Check if parallel
    is_parallel = "Parallel" in planned_text or "parallel" in planned_text.lower()

    if not is_parallel:
        return None

    # Extract parallel group
    execution_matches = re.findall(
        r"EXECUTION_TASK_([A-Z_-]+)_(\d+)_(\d+)",
        planned_text,
    )

    return {
        "is_parallel": True,
        "executions": execution_matches,
    }


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


def find_previous_executions(subplan_path: Path) -> List[Path]:
    """
    Find previous EXECUTION_TASK files for this SUBPLAN.

    Supports both flat and nested workspace structures:
    - Flat: work-space/execution/EXECUTION_TASK_*.md
    - Nested: plan_folder/execution/EXECUTION_TASK_*.md

    Args:
        subplan_path: Path to SUBPLAN file

    Returns:
        List of EXECUTION_TASK file paths, sorted by execution number
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

    # Sort by execution number
    execution_files.sort(
        key=lambda p: (
            int(re.search(r"_(\d+)\.md$", p.name).group(1))
            if re.search(r"_(\d+)\.md$", p.name)
            else 0
        )
    )

    return execution_files


def extract_execution_learnings(execution_path: Path) -> Optional[str]:
    """Extract learnings from EXECUTION_TASK file."""
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

        return None
    except Exception:
        return None


def get_last_iteration(execution_content: str) -> Optional[Dict[str, any]]:
    """Get last iteration from EXECUTION_TASK."""
    # Find all iterations
    iteration_matches = re.finditer(
        r"###\s*Iteration\s+(\d+)(.*?)(?=###|##|\Z)",
        execution_content,
        re.DOTALL | re.IGNORECASE,
    )

    iterations = []
    for match in iteration_matches:
        iterations.append(
            {
                "number": match.group(1),
                "content": match.group(2).strip(),
            }
        )

    if not iterations:
        return None

    # Return last iteration
    return iterations[-1]


def generate_create_prompt(subplan_path: Path, execution_num: str, parallel: bool = False) -> str:
    """Generate prompt for creating EXECUTION from SUBPLAN."""
    with open(subplan_path, "r", encoding="utf-8") as f:
        subplan_content = f.read()

    objective = extract_subplan_objective(subplan_content)
    approach = extract_subplan_approach(subplan_content)
    parallel_context = extract_parallelization_context(subplan_content)

    if not objective or not approach:
        return f"Error: Could not extract SUBPLAN objective or approach"

    # Build context boundaries
    context_lines = len(objective.split("\n")) + len(approach.split("\n"))

    prompt = f"""Execute EXECUTION_TASK from SUBPLAN: @{subplan_path.name}

═══════════════════════════════════════════════════════════════════════

CONTEXT BOUNDARIES (Read ONLY These):

✅ @{subplan_path.name} - Objective section (1-2 sentences only)
✅ @{subplan_path.name} - Approach section summary (3-5 sentences only)

❌ DO NOT READ: Full SUBPLAN (400-600 lines), other sections, archived work

CONTEXT BUDGET: ~{context_lines} lines maximum

═══════════════════════════════════════════════════════════════════════

SUBPLAN CONTEXT (Minimal Reading):

**SUBPLAN Objective** (read only this):
{objective}

**SUBPLAN Approach Summary** (read only this):
{approach}

**⚠️ DO NOT READ**: Full SUBPLAN (Designer already decided approach)

═══════════════════════════════════════════════════════════════════════"""

    # Add parallel execution context if applicable
    if parallel or (parallel_context and parallel_context.get("is_parallel")):
        prompt += f"""

PARALLEL EXECUTION CONTEXT:

**Parallel Group**: This EXECUTION runs in parallel with other EXECUTIONs
**Independence**: Work independently, no coordination needed during execution
**Results**: Will be compared in SUBPLAN synthesis (Phase 4)

═══════════════════════════════════════════════════════════════════════"""

    prompt += f"""

REQUIRED STEPS:

Step 1: Read SUBPLAN Context (MANDATORY)
- Read SUBPLAN objective (above)
- Read SUBPLAN approach summary (above)
- DO NOT read full SUBPLAN

Step 2: Create EXECUTION_TASK (MANDATORY)
- File: EXECUTION_TASK_[FEATURE]_{execution_num}.md
- Size: <200 lines
- Reference: LLM/templates/EXECUTION_TASK-TEMPLATE.md
- Copy SUBPLAN objective + approach to "SUBPLAN Context" section

Step 3: Execute Work
- Follow SUBPLAN approach
- Implement deliverables
- Document journey in EXECUTION_TASK

Step 4: Run Tests (MANDATORY - if code changes)
- Test folder structure mirrors project structure
- Example: LLM/scripts/generation/file.py → tests/LLM/scripts/generation/test_file.py
- Run relevant tests: pytest tests/path/to/test_file.py
- Fix any test failures before proceeding
- Update tests if function signatures or behavior changed

Step 5: Verify Deliverables (MANDATORY)
Run verification:
  ls -1 [each deliverable path]

Step 6: Complete EXECUTION_TASK
- Update: Iteration Log with "Complete"
- Add: Learning Summary
- Verify: <200 lines

═══════════════════════════════════════════════════════════════════════

VALIDATION ENFORCEMENT:

After Step 4, these scripts will run:
✓ validate_achievement_completion.py
✓ check_execution_task_size.py

If issues found: BLOCKS with error + fix prompt

═══════════════════════════════════════════════════════════════════════

DO NOT:
❌ Read full SUBPLAN (read objective + approach only)
❌ Re-design approach (Designer already decided)
❌ Skip EXECUTION_TASK ("just document in SUBPLAN" - NO)
❌ Mark complete without verifying files exist (run: ls -1)

REMEMBER:
✓ Read SUBPLAN objective + approach only (~10 lines)
✓ Follow Designer's plan (no re-design)
✓ Execute according to SUBPLAN approach
✓ Document journey in EXECUTION_TASK
✓ Archive immediately on completion

═══════════════════════════════════════════════════════════════════════

Reference: LLM/guides/SUBPLAN-WORKFLOW-GUIDE.md (Phase 3: Execution)

Now beginning EXECUTION work..."""

    return prompt


def generate_continue_prompt(execution_path: Path) -> str:
    """Generate prompt for continuing EXECUTION work."""
    with open(execution_path, "r", encoding="utf-8") as f:
        execution_content = f.read()

    last_iteration = get_last_iteration(execution_content)

    prompt = f"""Continue EXECUTION work: @{execution_path.name}

═══════════════════════════════════════════════════════════════════════

CONTEXT BOUNDARIES (Read ONLY These):

✅ This EXECUTION_TASK file (complete file)
✅ Code files being modified (if code work)

❌ DO NOT READ: Parent SUBPLAN, parent PLAN, other EXECUTIONs

CONTEXT BUDGET: ~200 lines (EXECUTION_TASK size limit)

═══════════════════════════════════════════════════════════════════════"""

    if last_iteration:
        prompt += f"""

LAST ITERATION ({last_iteration['number']}):

{last_iteration['content'][:300]}...

═══════════════════════════════════════════════════════════════════════"""

    prompt += f"""

REQUIRED STEPS:

Step 1: Review Last Iteration
- Read last iteration in EXECUTION_TASK
- Understand current status
- Identify next step

Step 2: Continue Work
- Continue implementation
- Follow iteration approach
- Document progress

Step 3: Run Tests (MANDATORY - if code changes)
- Test folder structure mirrors project structure
- Example: LLM/scripts/generation/file.py → tests/LLM/scripts/generation/test_file.py
- Run relevant tests: pytest tests/path/to/test_file.py
- Fix any test failures before proceeding
- Update tests if function signatures or behavior changed

Step 4: Update Iteration Log
- Add new iteration entry
- Document what was done
- Note learnings

Step 5: Verify Progress
- Check if deliverables progressing
- Update completion status

Step 6: Complete or Continue
- If complete: Add Learning Summary, mark complete
- If not: Continue to next iteration

═══════════════════════════════════════════════════════════════════════

DO NOT:
❌ Read parent SUBPLAN (stay focused on EXECUTION)
❌ Read parent PLAN
❌ Read other EXECUTIONs

REMEMBER:
✓ Stay focused on this EXECUTION_TASK
✓ Continue from last iteration
✓ Document progress thoroughly
✓ Keep EXECUTION_TASK <200 lines

═══════════════════════════════════════════════════════════════════════

Now continuing EXECUTION work..."""

    return prompt


def generate_next_prompt(subplan_path: Path) -> str:
    """Generate prompt for starting next EXECUTION in sequence."""
    with open(subplan_path, "r", encoding="utf-8") as f:
        subplan_content = f.read()

    objective = extract_subplan_objective(subplan_content)
    approach = extract_subplan_approach(subplan_content)
    previous_executions = find_previous_executions(subplan_path)

    if not objective or not approach:
        return f"Error: Could not extract SUBPLAN objective or approach"

    # Extract learnings from previous executions
    previous_learnings = []
    for exec_file in previous_executions:
        learnings = extract_execution_learnings(exec_file)
        if learnings:
            previous_learnings.append(f"**{exec_file.name}**:\n{learnings}\n")

    # Determine next execution number
    if previous_executions:
        last_exec = previous_executions[-1]
        last_num = int(re.search(r"_(\d+)\.md$", last_exec.name).group(1))
        next_num = f"{last_num + 1:02d}"
    else:
        next_num = "01"

    prompt = f"""Start Next EXECUTION from SUBPLAN: @{subplan_path.name}

═══════════════════════════════════════════════════════════════════════

CONTEXT BOUNDARIES (Read ONLY These):

✅ @{subplan_path.name} - Objective section (1-2 sentences only)
✅ @{subplan_path.name} - Approach section summary (3-5 sentences only)
✅ Previous EXECUTION learnings (below)

❌ DO NOT READ: Full SUBPLAN, full previous EXECUTIONs, parent PLAN

CONTEXT BUDGET: ~{len(objective.split('\n')) + len(approach.split('\n')) + 20} lines maximum

═══════════════════════════════════════════════════════════════════════

SUBPLAN CONTEXT (Minimal Reading):

**SUBPLAN Objective**:
{objective}

**SUBPLAN Approach Summary**:
{approach}

═══════════════════════════════════════════════════════════════════════"""

    if previous_learnings:
        prompt += f"""

PREVIOUS EXECUTION LEARNINGS:

{chr(10).join(previous_learnings)}

**Apply These Learnings**: Use insights from previous EXECUTION(s) to improve this EXECUTION

═══════════════════════════════════════════════════════════════════════"""

    prompt += f"""

REQUIRED STEPS:

Step 1: Review Previous Learnings
- Read learnings from previous EXECUTION(s) above
- Understand what worked/didn't work
- Identify improvements to apply

Step 2: Create Next EXECUTION_TASK
- File: EXECUTION_TASK_[FEATURE]_{next_num}.md
- Size: <200 lines
- Reference: LLM/templates/EXECUTION_TASK-TEMPLATE.md
- Copy SUBPLAN objective + approach to "SUBPLAN Context" section
- Note previous EXECUTION learnings

Step 3: Execute Work
- Apply learnings from previous EXECUTION(s)
- Follow SUBPLAN approach (improved based on learnings)
- Document journey in EXECUTION_TASK

Step 4: Run Tests (MANDATORY - if code changes)
- Test folder structure mirrors project structure
- Example: LLM/scripts/generation/file.py → tests/LLM/scripts/generation/test_file.py
- Run relevant tests: pytest tests/path/to/test_file.py
- Fix any test failures before proceeding
- Update tests if function signatures or behavior changed

Step 5: Verify Deliverables
- Run verification: ls -1 [each deliverable path]

Step 6: Complete EXECUTION_TASK
- Update: Iteration Log with "Complete"
- Add: Learning Summary (note improvements from previous)
- Verify: <200 lines

Step 7: Archive Immediately
- Move: EXECUTION_TASK → documentation/archive/[FEATURE]/execution/
- Update: SUBPLAN "Active EXECUTION_TASKs" section

═══════════════════════════════════════════════════════════════════════

DO NOT:
❌ Read full SUBPLAN (read objective + approach only)
❌ Read full previous EXECUTIONs (read learnings only)
❌ Ignore previous learnings (apply improvements)

REMEMBER:
✓ Apply learnings from previous EXECUTION(s)
✓ Improve based on what worked/didn't work
✓ Follow SUBPLAN approach (enhanced with learnings)
✓ Document improvements in EXECUTION_TASK

═══════════════════════════════════════════════════════════════════════

Reference: LLM/guides/SUBPLAN-WORKFLOW-GUIDE.md (Phase 3: Execution, Sequential Pattern)

Now starting next EXECUTION..."""

    return prompt


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
    # Check if --batch flag is present (handle before argparse to avoid positional arg issues)
    if '--batch' in sys.argv:
        # Simple argument parsing for batch mode
        dry_run = '--dry-run' in sys.argv
        
        # Find the file argument (anything starting with @ or containing PLAN_)
        file_arg = None
        for arg in sys.argv[1:]:
            if arg.startswith('@') or 'PLAN_' in arg or arg.startswith('work-space'):
                file_arg = arg
                break
        
        if not file_arg:
            print("Error: File path required for --batch mode", file=sys.stderr)
            print("Usage: generate_execution_prompt.py --batch [--dry-run] @PLAN_FILE.md", file=sys.stderr)
            sys.exit(1)
        
        # Handle batch creation
        from LLM.scripts.generation.batch_execution import batch_create_executions
        
        # Resolve plan path
        if file_arg.startswith("@"):
            file_type = "PLAN" if "PLAN_" in file_arg else "FILE"
        else:
            file_type = "FILE"
        
        plan_path = resolve_plan_path(file_arg, file_type=file_type)
        
        # Run batch creation
        result = batch_create_executions(
            plan_path=plan_path,
            dry_run=dry_run
        )
        
        # Print result
        print("\n" + "="*80)
        print(result)
        print("="*80)
        
        return 0
    
    # Normal mode: use argparse
    parser = argparse.ArgumentParser(
        description="Generate prompts for EXECUTION lifecycle",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create EXECUTION from SUBPLAN
  python generate_execution_prompt.py create @SUBPLAN_FEATURE_11.md --execution 01
  
  # Continue EXECUTION
  python generate_execution_prompt.py continue @EXECUTION_TASK_FEATURE_11_01.md
  
  # Next EXECUTION
  python generate_execution_prompt.py next @SUBPLAN_FEATURE_11.md
  
  # Parallel execution
  python generate_execution_prompt.py create @SUBPLAN_FEATURE_11.md --execution 01 --parallel
  
  # Batch creation
  python generate_execution_prompt.py --batch @PLAN_FEATURE.md
  python generate_execution_prompt.py --batch --dry-run @PLAN_FEATURE.md
        """,
    )

    parser.add_argument(
        "mode",
        choices=["create", "continue", "next"],
        help="Mode: create, continue, or next",
    )
    parser.add_argument(
        "file",
        type=str,
        help="SUBPLAN file (for create/next) or EXECUTION_TASK file (for continue)",
    )
    parser.add_argument(
        "--execution",
        type=str,
        help="Execution number (e.g., '01') - required for create mode",
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Mark as parallel execution (for create mode)",
    )
    parser.add_argument(
        "--clipboard",
        action="store_true",
        help="Copy prompt to clipboard",
    )

    args = parser.parse_args()

    # Resolve path with @ shorthand support (Bug #9 fix)
    file_path = resolve_plan_path(args.file, file_type="SUBPLAN")

    # Generate prompt based on mode
    if args.mode == "create":
        if not args.execution:
            print("Error: --execution required for create mode", file=sys.stderr)
            sys.exit(1)
        prompt = generate_create_prompt(file_path, args.execution, args.parallel)
    elif args.mode == "continue":
        prompt = generate_continue_prompt(file_path)
    elif args.mode == "next":
        prompt = generate_next_prompt(file_path)
    else:
        print(f"Error: Unknown mode: {args.mode}", file=sys.stderr)
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
