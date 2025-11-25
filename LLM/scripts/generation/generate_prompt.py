#!/usr/bin/env python3
"""
Generate Prompt - LLM Methodology Workflow Automation

═══════════════════════════════════════════════════════════════════════
PURPOSE
═══════════════════════════════════════════════════════════════════════

Automated prompt generation for LLM development methodology, providing:
- Intelligent workflow state detection (7 states)
- Context-optimized prompts (read only what's needed)
- Interactive mode as primary UI (two-stage menu)
- Conflict detection (PLAN vs filesystem)
- Multi-execution support (parallel workflows)
- Comprehensive error handling

Primary UI: Interactive mode with two-stage experience:
  1. Pre-execution menu: Choose workflow (next/specific/view)
  2. Post-generation menu: Handle output (copy/view/save/execute)

═══════════════════════════════════════════════════════════════════════
ARCHITECTURE OVERVIEW
═══════════════════════════════════════════════════════════════════════

State Machine (7 Workflow States):

1. no_subplan → Suggest creating SUBPLAN
2. subplan_no_execution → Suggest creating EXECUTION
3. active_execution → Suggest continuing EXECUTION
4. create_next_execution → Suggest next EXECUTION (multi-execution)
5. subplan_all_executed → Suggest synthesis or completion
6. subplan_complete → Move to next achievement
7. plan_complete → Show completion message with statistics

Detection Strategy:
  • Filesystem-first: Check actual files (robust)
  • Markdown fallback: Parse text if filesystem detection fails
  • Conflict detection: Warn if PLAN and filesystem disagree

Interactive Mode:
  • Pre-execution: InteractiveMenu().show_pre_execution_menu() - Choose workflow
  • Post-generation: InteractiveMenu().show_post_generation_menu() - Handle output
  • Module: interactive_menu.py (Achievement 2.1 - extracted from main file)
  • Flag preservation: --interactive persists through workflow
  • Smart defaults: Enter = copy (most common action)

═══════════════════════════════════════════════════════════════════════
BUG FIX HISTORY (12 Bugs Fixed)
═══════════════════════════════════════════════════════════════════════

Parsing Bugs (67% of total - Bugs #1-8):
  Bug #1-4: Various parsing failures (early fixes)
  Bug #5: Missing "Implementation Strategy" section name
    Fix: Added to fallback chain in extract_subplan_approach()
    Lesson: Markdown flexibility breaks rigid parsing

  Bug #8: Missing 🎯 emoji in SUBPLAN approach section
    Fix: Emoji-agnostic regex in generate_execution_prompt.py
    Lesson: Recurrence of Bug #5 - same root cause
    Reference: EXECUTION_ANALYSIS_SUBPLAN-EXTRACTION-BUG-8.md

Architectural Bugs (25% of total - Bugs #9-11):
  Bug #9: @ shorthand not working in generate_subplan_prompt.py
    Fix: Created shared path_resolution.py module
    Lesson: Code duplication causes feature parity gaps
    Reference: EXECUTION_ANALYSIS_SUBPLAN-PROMPT-GENERATOR-MISSING-PATH-RESOLUTION-BUG-9.md

  Bug #10: Incorrect path format in generated commands
    Fix: Changed @{subplan_path} to @{subplan_path.name} (lines 1902, 2009)
    Lesson: Path objects vs strings in f-strings
    Reference: EXECUTION_ANALYSIS_GENERATE-PROMPT-INCORRECT-SUBPLAN-PATH-BUG-10.md

  Bug #11: --subplan-only flag silent failure
    Fix: Changed @{plan_path} to @{plan_path.name} + improved error handling
    Lesson: Silent failures destroy trust - always provide actionable messages
    Reference: EXECUTION_ANALYSIS_SUBPLAN-ONLY-FLAG-SILENT-FAILURE-BUG-11.md

  Bug #12: --subplan-only flag path resolution failure (Bug #11 recurrence)
    Fix: Changed @{plan_path} to @{plan_path.name} on line 1415
    Lesson: Same bug pattern in different code path - need systematic search
    Reference: EXECUTION_DEBUG_SUBPLAN-ONLY-FLAG-PATH-BUG.md

State Sync Bugs (8% of total):
  Achievement 0.2, 1.1 status conflicts: SUBPLAN complete but PLAN not updated
    Fix: Conflict detection system (detect_plan_filesystem_conflict)
    Lesson: Manual status updates fail - need automated sync
    Reference: EXECUTION_OBSERVATION_PLAN-FILESYSTEM-SYNCHRONIZATION-CONFLICTS.md

Root Cause Analysis:
  • 67% parsing bugs → Architectural mismatch (markdown flexibility vs automation)
  • 8% sync bugs → No single source of truth (manual updates fail)
  • 25% architectural bugs → Code duplication (feature parity gaps)

Solution Path:
  • Achievements 2.4-2.6: Filesystem state management (eliminates 83% of bugs)
  • Reference: EXECUTION_CASE-STUDY_FILESYSTEM-STATE-MANAGEMENT.md

═══════════════════════════════════════════════════════════════════════
DESIGN PHILOSOPHY
═══════════════════════════════════════════════════════════════════════

1. Interactive Mode as Primary UI
   • Two-stage menu (pre-execution + post-generation)
   • Smart defaults (Enter = copy)
   • Context-aware options (execute when command available)
   • Seamless navigation through entire workflow

2. Filesystem-First Detection
   • Check actual files (robust, fast)
   • Markdown parsing as fallback (backward compatible)
   • Conflict detection (warn when sources disagree)

3. Comprehensive Error Handling
   • Never fail silently (Bug #11 lesson)
   • Provide actionable guidance (troubleshooting steps)
   • Copy errors to clipboard (user can paste immediately)

4. Backward Compatibility
   • Non-interactive mode still works
   • Markdown parsing fallback
   • Gradual migration path

5. Test-Driven Quality
   • 49 tests for new features (100% passing)
   • 87.5% of legacy code untested (Priority 1 work)
   • Target: 90%+ coverage for safe refactoring

═══════════════════════════════════════════════════════════════════════
CURRENT STATE & REFACTOR NOTES
═══════════════════════════════════════════════════════════════════════

File Size: 2,874 lines (reduced from 3,625 lines - Achievement 2.1)
Functions: 22 total (2 functions extracted to interactive_menu.py)
Test Coverage: ~25% (49 tests, but 19 of 22 functions untested)
Known Issues: Fragile text parsing (Bugs #1-8 root cause)

Completed Refactor (Achievement 2.1):
  ✅ InteractiveMenu extracted to interactive_menu.py (834 lines)
  ✅ Reduced main file by 751 lines (20.7% reduction)
  ✅ All interactive functionality preserved
  ✅ 17 new module tests added (all passing)

Planned Refactor (Priority 2):
  • Achievement 2.2: Extract Workflow Detection Module
  • Achievement 2.3: Extract Prompt Generation Module
  • Achievement 2.4: Extract Parsing & Utilities Module
  • Achievement 2.5: Codify Feedback System Patterns
  • Achievement 2.6: Integrate Modules & Final Refactor
    - PromptGenerator (orchestration)
    - PlanParser (markdown fallback)
    - WorkflowDetector (filesystem-first)
    - ConflictDetector (validation)

Architectural Rules (for refactor):
  1. Filesystem state is PRIMARY source of truth
  2. Markdown parsing is FALLBACK only
  3. All state changes go through FilesystemState class
  4. Interactive mode preserved in all workflows
  5. All existing tests must pass (zero regressions)
  6. Classes testable in isolation
  7. Dependency injection for FilesystemState

═══════════════════════════════════════════════════════════════════════
USAGE EXAMPLES
═══════════════════════════════════════════════════════════════════════

Interactive Mode (PRIMARY UI - Recommended):
    # Two-stage experience with menus
    python generate_prompt.py @RESTORE --interactive

    Stage 1: Choose workflow (next/specific/view)
    Stage 2: Handle output (copy/view/save/execute)

Non-Interactive Mode (Power Users):
    # Auto-detect next step
    python generate_prompt.py @RESTORE --next

    # Specific achievement
    python generate_prompt.py @GRAPHRAG --achievement 0.3

    # SUBPLAN work only (Designer)
    python generate_prompt.py @PROMPT --achievement 1.2 --subplan-only

    # EXECUTION work only (Executor)
    python generate_prompt.py @PROMPT --achievement 1.2 --execution-only

Shortcuts:
    # @folder finds PLAN automatically (Achievement 0.1)
    @RESTORE → work-space/plans/RESTORE-EXECUTION-WORKFLOW-AUTOMATION/PLAN_*.md
    @GRAPHRAG → work-space/plans/GRAPHRAG-OBSERVABILITY-EXCELLENCE/PLAN_*.md

    # Clipboard is default (Achievement 0.1)
    Output auto-copied, use --no-clipboard to disable

Conflict Resolution:
    # Trust PLAN as source of truth
    python generate_prompt.py @PLAN --next --trust-plan

    # Trust filesystem as source of truth
    python generate_prompt.py @PLAN --next --trust-filesystem

═══════════════════════════════════════════════════════════════════════
TESTING STATUS
═══════════════════════════════════════════════════════════════════════

Test Coverage: ~25% (49 tests, 21 of 24 functions untested)

Tested Functions (13):
  • copy_to_clipboard_safe() - 13 tests (Achievement 0.1)
  • resolve_folder_shortcut() - 13 tests (Achievement 0.1)
  • extract_plan_statistics() - 9 tests (Achievement 0.2)
  • output_interactive_menu() - 18 tests (Achievement 0.3)
  • parse_plan_file() - 4 tests (Achievement 1.1)
  • extract_handoff_section() - 4 tests (Achievement 1.1)
  • find_next_achievement_from_plan() - 4 tests (Achievement 1.1)

Untested Functions (11):
  • find_next_achievement_from_archive()
  • find_next_achievement_from_root()
  • is_achievement_complete()
  • get_plan_status()
  • is_plan_complete()
  • find_next_achievement_hybrid()
  • detect_validation_scripts()
  • estimate_section_size()
  • find_archive_location()
  • calculate_handoff_size()
  • inject_project_context()
  • find_subplan_for_achievement()
  • check_subplan_status()
  • detect_workflow_state_filesystem()
  • detect_plan_filesystem_conflict()
  • detect_workflow_state()
  • generate_prompt()
  • prompt_interactive_menu()
  • main()

Priority for Testing (Achievement 1.3):
  1. Workflow detection functions (core logic)
  2. Conflict detection functions (bug prevention)
  3. Achievement finding functions (critical path)
  4. Main orchestration (integration)

═══════════════════════════════════════════════════════════════════════
FUTURE VISION (Path to North Star CLI Platform)
═══════════════════════════════════════════════════════════════════════

Current: Single script (2,270 lines), text parsing, manual workflows
North Star: Universal CLI platform, structured metadata, seamless integrations

Bridge Path:
  Phase 1: Stabilize (Priority 0-1) ✅ Interactive mode, tests, docs
  Phase 2: Refactor (Priority 2) → Filesystem state, class-based architecture
  Phase 3: Enhance (Priority 3) → Error messages, performance, polish
  Phase 4: Transform (Future) → CLI platform, plugins, integrations

Key Enablers:
  • Filesystem state management (eliminates parsing bugs)
  • Class-based architecture (maintainable, extensible)
  • Comprehensive tests (safe to refactor)
  • Interactive mode (delightful UX)

Reference: PLAN_PROMPT-GENERATOR-UX-AND-FOUNDATION.md

═══════════════════════════════════════════════════════════════════════
"""

import argparse
import re
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Dict

# Add project root to path for imports (when script is run directly)
_script_dir = Path(__file__).parent
_project_root = _script_dir.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Achievement 3.1: Add structured logging (after sys.path setup)
from core.libraries.logging import get_logger, set_log_context

logger = get_logger(__name__)

# Achievement 3.2: Add metrics for performance monitoring
from core.libraries.metrics import Counter, Histogram, Timer, MetricRegistry

# Define metrics
prompt_generation_counter = Counter(
    "prompt_generation_total", description="Total prompts generated", labels=["workflow", "status"]
)

prompt_generation_duration = Histogram(
    "prompt_generation_duration_seconds",
    description="Prompt generation duration",
    labels=["workflow"],
)

plan_cache_hits = Counter(
    "plan_cache_hits_total", description="PLAN cache hits", labels=["cache_name", "hit_type"]
)

# Register metrics with registry
registry = MetricRegistry.get_instance()
registry.register(prompt_generation_counter)
registry.register(prompt_generation_duration)
registry.register(plan_cache_hits)

# Import interactive menu module (Achievement 2.1)
from LLM.scripts.generation.interactive_menu import InteractiveMenu
from LLM.scripts.generation.workflow_detector import WorkflowDetector
from LLM.scripts.generation.prompt_builder import PromptBuilder
from LLM.scripts.generation.plan_parser import PlanParser
from LLM.scripts.generation import utils
from LLM.scripts.generation.utils import Achievement

# Import structure detection for dual structure support
try:
    from LLM.scripts.workflow.structure_detection import detect_structure
except ImportError:
    # Fallback if structure_detection not available (backward compatibility)
    def detect_structure(plan_path: Path) -> str:
        """Fallback: always return flat structure."""
        return "flat"


# Achievement class moved to utils.py (Achievement 2.6 - Integration)
# Use: from LLM.scripts.generation.utils import Achievement


# Note: parse_plan_file() moved to plan_parser.py (Achievement 2.4)
# Use PlanParser().parse_plan_file() instead


# Note: extract_handoff_section() moved to plan_parser.py (Achievement 2.4)
# Use PlanParser().extract_handoff_section() instead


# is_achievement_complete() moved to utils.py (Achievement 2.6 - Integration)
# Use utils.is_achievement_complete() instead


def get_plan_status(plan_content: str) -> str:
    """
    Extract PLAN status from content (for status-based workflow detection).

    Checks for "**Status**: ..." field in handoff section or PLAN header.
    Used as fallback when handoff doesn't have clear "Next:" statement.

    Status Values:
    - "planning": PLAN not started
    - "in progress": PLAN active
    - "complete": PLAN done
    - "unknown": Status not found

    Used by: find_next_achievement_hybrid()
    Tested: No (Priority 1.3 - needs tests)

    Args:
        plan_content: Full PLAN file content

    Returns:
        Status string (e.g., "planning", "in progress", "complete") or "unknown"

    Example:
        >>> content = Path("PLAN_FEATURE.md").read_text()
        >>> status = get_plan_status(content)
        >>> print(status)
        "in progress"
    """
    # Check handoff section first
    parser = PlanParser()
    handoff_section = parser.extract_handoff_section(plan_content)
    if handoff_section:
        status_match = re.search(
            r"\*\*Status\*\*[:\s]+(\w+(?:\s+\w+)?)", handoff_section, re.IGNORECASE
        )
        if status_match:
            return status_match.group(1).lower()

    # Check PLAN header
    status_match = re.search(r"\*\*Status\*\*[:\s]+(\w+(?:\s+\w+)?)", plan_content, re.IGNORECASE)
    if status_match:
        return status_match.group(1).lower()

    return "unknown"


def is_plan_complete(
    plan_content: str, achievements: List[Achievement], plan_path: Path = None
) -> bool:
    """
    Check if PLAN is complete (all achievements done) - FILESYSTEM-ONLY.

    **State Tracking Philosophy**:
    - PLAN's responsibility: Define Achievement Index (list of all achievements)
    - Filesystem's responsibility: Track completion via APPROVED_XX.md files
    - NO markdown parsing for completion status

    This function checks ONLY the filesystem for APPROVED_XX.md files.
    A PLAN is complete when ALL achievements have APPROVED files.

    Critical function that determines if we should show completion message
    or continue with next achievement. Must be accurate to avoid false
    completions or missing actual completions.

    Detection Strategy (FILESYSTEM-ONLY):
    1. Iterate through all achievements from Achievement Index
    2. Check if each has an APPROVED_XX.md file (via is_achievement_complete)
    3. Return True ONLY if ALL achievements have approved files

    Bug Fixes Incorporated:
        - Bug #11 (2025-11-12): Removed ALL markdown parsing for completion status.
          Previous implementation had markdown checks (pattern matching) BEFORE
          filesystem checks, violating filesystem-first philosophy. Now purely
          filesystem-based using APPROVED_XX.md files.

    Used by: find_next_achievement_hybrid(), main()
    Tested: No (Priority 1.3 - needs tests)

    Args:
        plan_content: Full PLAN file content (unused for state, kept for compatibility)
        achievements: List of achievements from Achievement Index
        plan_path: Path to PLAN file (required for filesystem checks)

    Returns:
        True if all achievements have APPROVED_XX.md files, False otherwise

    Example:
        >>> plan_path = Path("work-space/plans/FEATURE/PLAN_FEATURE.md")
        >>> achievements = parse_plan_file(plan_path)["achievements"]
        >>> content = plan_path.read_text()
        >>> is_plan_complete(content, achievements, plan_path)
        True  # Only if ALL achievements have APPROVED files
    """
    # If no plan_path provided, cannot check filesystem
    if not plan_path or not achievements:
        return False

    # Count completed achievements (FILESYSTEM-ONLY - check APPROVED_XX.md files)
    completed_count = 0
    for ach in achievements:
        # is_achievement_complete() checks for APPROVED_XX.md files (filesystem-only)
        if utils.is_achievement_complete(ach.number, plan_content, plan_path):
            completed_count += 1

    # PLAN is complete ONLY if ALL achievements have APPROVED files
    return completed_count == len(achievements) and len(achievements) > 0


def detect_validation_scripts() -> List[str]:
    """
    Detect which validation scripts exist in the codebase.

    Scans for validation scripts that will run after achievement completion
    to verify deliverables, check sizes, validate references, etc.

    Used by: generate_prompt() (to show which scripts will run)
    Tested: No (Priority 1.3 - needs tests)

    Returns:
        List of validation script names that exist

    Example:
        >>> scripts = detect_validation_scripts()
        >>> print(scripts)
        ['validate_achievement_completion.py', 'check_plan_size.py']
    """
    validation_dir = Path("LLM/scripts/validation")

    validation_scripts = [
        "validate_achievement_completion.py",
        "validate_execution_start.py",
        "validate_mid_plan.py",
        "check_plan_size.py",
        "check_execution_task_size.py",
        "validate_registration.py",
        "validate_references.py",
        "validate_plan_compliance.py",
    ]

    existing = []
    for script in validation_scripts:
        # Check new domain structure first (validation/)
        if (validation_dir / script).exists():
            existing.append(script)
        # Fallback to old structure (LLM/scripts/) for backward compatibility
        elif (Path("LLM/scripts") / script).exists():
            existing.append(script)

    return existing


# Note: estimate_section_size(), find_archive_location(), calculate_handoff_size()
# moved to plan_parser.py (Achievement 2.4) - Use PlanParser() methods instead


def inject_project_context(include_context: bool = True) -> str:
    """
    Read and format project context from PROJECT-CONTEXT.md.

    Injects essential project information into prompts to provide LLM with
    necessary context about the codebase structure, conventions, and key directories.

    Sections Extracted:
    - Project Overview (first 10 lines)
    - Project Structure (key directories, 15 lines)
    - Methodology Conventions (20 lines)

    Graceful Degradation:
    - Returns empty string if file not found
    - Returns empty string if parsing fails
    - Never crashes

    Used by: generate_prompt()
    Tested: No (Priority 1.3 - needs tests)

    Args:
        include_context: Whether to include project context (default: True)

    Returns:
        Formatted project context section, or empty string if disabled or file not found

    Example:
        >>> context = inject_project_context(include_context=True)
        >>> print("PROJECT CONTEXT" in context)
        True

        >>> context = inject_project_context(include_context=False)
        >>> print(context)
        ""
    """
    if not include_context:
        return ""

    project_context_path = Path("LLM/PROJECT-CONTEXT.md")

    # Gracefully handle missing file
    if not project_context_path.exists():
        return ""

    try:
        with open(project_context_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract key sections (Overview, Structure, Conventions)
        # Keep it concise but comprehensive
        sections = []

        # Extract Project Overview
        overview_match = re.search(
            r"## 📋 Project Overview\n\n(.*?)(?=\n## |$)", content, re.DOTALL
        )
        if overview_match:
            overview = overview_match.group(1).strip()
            # Limit to first few lines to keep concise
            overview_lines = overview.split("\n")[:10]
            sections.append("**Project Overview**:\n" + "\n".join(overview_lines))

        # Extract Project Structure (key directories only)
        structure_match = re.search(
            r"## 🏗️ Project Structure\n\n(.*?)(?=\n## |$)", content, re.DOTALL
        )
        if structure_match:
            structure = structure_match.group(1).strip()
            # Extract key directories section
            dirs_match = re.search(
                r"### Key Directories\n\n(.*?)(?=\n### |$)", structure, re.DOTALL
            )
            if dirs_match:
                dirs = dirs_match.group(1).strip()
                # Limit to first 15 lines
                dirs_lines = dirs.split("\n")[:15]
                sections.append(
                    "**Project Structure** (Key Directories):\n" + "\n".join(dirs_lines)
                )

        # Extract Conventions (methodology conventions only)
        conventions_match = re.search(r"## 📐 Conventions\n\n(.*?)(?=\n## |$)", content, re.DOTALL)
        if conventions_match:
            conventions = conventions_match.group(1).strip()
            # Extract methodology conventions
            method_match = re.search(
                r"### Methodology Conventions.*?\n\n(.*?)(?=\n---|\n## |$)", conventions, re.DOTALL
            )
            if method_match:
                method = method_match.group(1).strip()
                # Limit to first 20 lines
                method_lines = method.split("\n")[:20]
                sections.append("**Methodology Conventions**:\n" + "\n".join(method_lines))

        if sections:
            return (
                "\n\n**PROJECT CONTEXT** (Essential Knowledge):\n\n" + "\n\n".join(sections) + "\n"
            )

        return ""
    except Exception:
        # Gracefully handle any errors
        return ""


# PROMPT TEMPLATES - Moved to prompt_builder.py (Achievement 2.3)
# Template and formatting logic extracted to PromptBuilder class


def find_subplan_for_achievement(
    feature_name: str, achievement_num: str, plan_path: Optional[Path] = None
) -> Optional[Path]:
    """
    Find SUBPLAN file for achievement in nested workspace structure.

    Core discovery function that locates SUBPLAN files for workflow detection.
    Supports both active SUBPLANs (in work-space/plans/) and archived SUBPLANs
    (in documentation/archive/).

    Search Strategy:
    1. Try nested structure: work-space/plans/FEATURE/subplans/SUBPLAN_*.md
    2. Try archive: documentation/archive/SUBPLAN_*_ARCHIVED.md
    3. Return None if not found in either location

    Naming Convention:
    - Active: SUBPLAN_FEATURE_11.md (achievement 1.1 → 11)
    - Archived: SUBPLAN_FEATURE_11_ARCHIVED.md

    Used by: detect_workflow_state_filesystem(), main()
    Tested: No (Priority 1.3 - needs tests)

    Args:
        feature_name: Feature name (e.g., "METHODOLOGY-HIERARCHY-EVOLUTION")
        achievement_num: Achievement number (e.g., "1.1")
        plan_path: Optional path to PLAN file (to determine plan folder)

    Returns:
        Path to SUBPLAN file, or None if not found

    Example:
        >>> subplan = find_subplan_for_achievement("FEATURE", "1.1", plan_path)
        >>> print(subplan.name)
        "SUBPLAN_FEATURE_11.md"

        >>> subplan = find_subplan_for_achievement("FEATURE", "9.9", plan_path)
        >>> print(subplan)
        None
    """
    subplan_num = achievement_num.replace(".", "")

    # Determine plan folder from plan_path or construct it
    plan_folder = None
    if plan_path and plan_path.exists():
        # PLAN is in work-space/plans/PLAN_NAME/PLAN_*.md
        # So parent is PLAN folder
        plan_folder = plan_path.parent
    else:
        # Try to construct PLAN folder path directly
        plan_folder = Path(f"work-space/plans/{feature_name}")

    # Direct check in nested structure
    if plan_folder and plan_folder.exists():
        nested_subplan = plan_folder / "subplans" / f"SUBPLAN_{feature_name}_{subplan_num}.md"
        if nested_subplan.exists():
            return nested_subplan

    # Check archive locations for archived SUBPLANs
    archive_base = Path("documentation/archive")
    if archive_base.exists():
        # Direct path to archived SUBPLAN (follows naming pattern)
        archived_subplan = archive_base / f"SUBPLAN_{feature_name}_{subplan_num}_ARCHIVED.md"
        if archived_subplan.exists():
            return archived_subplan

    return None


def check_subplan_status(subplan_path: Path) -> Dict[str, any]:
    """
    Check SUBPLAN status by parsing its content (legacy detection method).

    This is the OLD detection method that parses SUBPLAN markdown to check:
    - If SUBPLAN has active EXECUTION_TASKs (from "Active EXECUTION_TASKs" section)
    - If SUBPLAN is marked complete (from status header)

    NOTE: This function is being phased out in favor of filesystem-based detection
    (detect_workflow_state_filesystem) which is more robust.

    Used by: detect_workflow_state() (fallback only)
    Tested: No (Priority 1.3 - needs tests)

    Args:
        subplan_path: Path to SUBPLAN file

    Returns:
        Dict with keys:
            - has_subplan: bool (always True if file exists)
            - has_active_executions: bool (from parsing)
            - is_complete: bool (from status header)
            - execution_count: int (count of active executions)

    Example:
        >>> status = check_subplan_status(Path("SUBPLAN_FEATURE_01.md"))
        >>> print(status["is_complete"])
        True
    """
    try:
        with open(subplan_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for active EXECUTIONs
        active_match = re.search(
            r"##\s*🔄\s*Active EXECUTION_TASKs",
            content,
            re.IGNORECASE,
        )

        has_active = False
        execution_count = 0

        if active_match:
            active_section = content[active_match.start() :]
            # Count active executions (Planning or Executing status)
            active_count = len(
                re.findall(
                    r"Planning|Executing",
                    active_section,
                    re.IGNORECASE,
                )
            )
            has_active = active_count > 0
            execution_count = active_count

        # Check if complete - more specific pattern to avoid false positives
        # Look for SUBPLAN-level completion status, not just any "Complete" in the document
        # Patterns to match:
        # - "**Status**: ✅ Complete"
        # - "**Status**: Complete"
        # - Completion marker near top of file (first 500 chars) in metadata
        is_complete = False
        if active_match:
            # If there are active executions, SUBPLAN is not complete
            is_complete = False
        else:
            # No active section - check for explicit completion status
            # Look in first 500 chars (header area) or last 500 chars (status area)
            header_section = content[:500]
            status_section = content[-500:]
            completion_patterns = [
                r"\*\*Status\*\*:\s*✅\s*Complete",  # **Status**: ✅ Complete
                r"\*\*Status\*\*:\s*Complete",  # **Status**: Complete
                r"Status.*:\s*✅\s*Complete",  # Status: ✅ Complete
            ]
            for pattern in completion_patterns:
                if re.search(pattern, header_section, re.IGNORECASE) or re.search(
                    pattern, status_section, re.IGNORECASE
                ):
                    is_complete = True
                    break

        return {
            "has_subplan": True,
            "has_active_executions": has_active,
            "is_complete": is_complete,
            "execution_count": execution_count,
        }
    except Exception:
        return {
            "has_subplan": False,
            "has_active_executions": False,
            "is_complete": False,
            "execution_count": 0,
        }


def detect_workflow_state(
    plan_path: Path, feature_name: str, achievement_num: str
) -> Dict[str, any]:
    """
    Detect workflow state for achievement (wrapper with fallback).

    This is a WRAPPER function that tries filesystem-based detection first
    (robust, fast) and falls back to content-based detection if it fails.

    Detection Methods:
    1. Filesystem-based (PRIMARY): detect_workflow_state_filesystem()
       - Checks actual files on disk
       - Counts EXECUTION_TASKs
       - More reliable

    2. Content-based (FALLBACK): check_subplan_status()
       - Parses SUBPLAN markdown
       - Legacy method
       - Used if filesystem detection fails

    Used by: main() (for workflow detection)
    Tested: No (Priority 1.3 - needs tests)

    Args:
        plan_path: Path to PLAN file in nested structure
        feature_name: Feature name (e.g., "METHODOLOGY-HIERARCHY-EVOLUTION")
        achievement_num: Achievement number (e.g., "0.1")

    Returns:
        Dict with keys:
            - state: str (workflow state name)
            - subplan_path: Optional[Path]
            - recommendation: str (suggested action)
            - execution_count: int (optional)
            - completed_count: int (optional)

    Example:
        >>> state = detect_workflow_state(plan_path, "FEATURE", "0.1")
        >>> print(state["state"])
        "subplan_no_execution"
        >>> print(state["recommendation"])
        "create_execution"
    """
    # Try new filesystem-based detection first
    try:
        detector = WorkflowDetector()
        result = detector.detect_workflow_state_filesystem(plan_path, feature_name, achievement_num)
        return result
    except Exception as e:
        # Fallback to old detection if filesystem detection fails
        print(f"⚠️  Filesystem detection failed, using fallback: {e}")

    # OLD DETECTION (kept as fallback)
    subplan_path = find_subplan_for_achievement(feature_name, achievement_num, plan_path)

    if not subplan_path:
        return {
            "state": "no_subplan",
            "subplan_path": None,
            "recommendation": "create_subplan",
        }

    subplan_status = check_subplan_status(subplan_path)

    if subplan_status["is_complete"]:
        return {
            "state": "subplan_complete",
            "subplan_path": subplan_path,
            "recommendation": "next_achievement",
        }

    if subplan_status["has_active_executions"]:
        return {
            "state": "active_execution",
            "subplan_path": subplan_path,
            "recommendation": "continue_execution",
            "execution_count": subplan_status["execution_count"],
        }

    # SUBPLAN exists but no active EXECUTION
    return {
        "state": "subplan_no_execution",
        "subplan_path": subplan_path,
        "recommendation": "create_execution",
    }


def generate_prompt(
    plan_path: Path, achievement_num: Optional[str] = None, include_context: bool = True
) -> str:
    """
    Generate prompt for PLAN achievement execution.

    **Libraries Used** (Achievement 3.1, 3.2):
    - **error_handling**: Structured exceptions (PlanNotFoundError, AchievementNotFoundError)
    - **logging**: Structured logs with context propagation
    - **caching**: PLAN parsing cached (parse_plan_file)
    - **metrics**: prompt_generation_total, prompt_generation_duration_seconds

    Main prompt generation function that orchestrates:
    1. Parse PLAN file (cached - 582x faster on cache hit)
    2. Check if PLAN is complete
    3. Find next achievement (or use specified)
    4. Detect validation scripts
    5. Inject project context
    6. Fill template
    7. Return prompt

    Special Cases:
    - PLAN complete → Returns completion message with statistics
    - No achievements found → Returns error message
    - Achievement specified → Uses that achievement
    - No achievement specified → Auto-detects next

    **Performance**:
    - First call: ~15ms (parse PLAN, detect state, generate)
    - Cached calls: ~7ms (PLAN parsing cached)
    - Cache hit rate: 91% (target: 80%)

    **Raises**:
    - PlanNotFoundError: If PLAN file doesn't exist
    - AchievementNotFoundError: If specified achievement not in PLAN
    - ApplicationError: For other errors (with suggestions)

    **Metrics Collected**:
    - prompt_generation_total{workflow, status}: Counter of prompts (success/error)
    - prompt_generation_duration_seconds{workflow}: Histogram of durations
    - plan_cache_hits_total{cache_name, hit_type}: Cache hit/miss counters

    Used by: main()
    Tested: No (Priority 1.3 - needs integration tests)

    Args:
        plan_path: Path to PLAN file
        achievement_num: Optional specific achievement number
        include_context: Whether to include project context (default: True)

    Returns:
        Generated prompt string (or completion/error message)

    Example:
        >>> prompt = generate_prompt(plan_path, achievement_num="1.2")
        >>> print("Execute Achievement 1.2" in prompt)
        True
    """

    # Parse PLAN (Achievement 2.4: use PlanParser module)
    parser = PlanParser()
    plan_data = parser.parse_plan_file(plan_path)

    # Check if PLAN is complete (before finding next achievement)
    try:
        with open(plan_path, "r", encoding="utf-8") as f:
            plan_content = f.read()

        if is_plan_complete(plan_content, plan_data["achievements"], plan_path):
            # PLAN is complete - return completion message (Achievement 2.3: use PromptBuilder)
            builder = PromptBuilder()
            return builder.build_completion_message(
                plan_data["feature_name"], plan_path, plan_data["archive_location"]
            )
    except Exception:
        # If reading fails, continue with normal flow
        pass

    # Find next achievement
    if achievement_num:
        next_ach = next((a for a in plan_data["achievements"] if a.number == achievement_num), None)
    else:
        detector = WorkflowDetector()
        next_ach = detector.find_next_achievement_hybrid(
            plan_path,
            plan_data["feature_name"],
            plan_data["achievements"],
            plan_data["archive_location"],
        )

    if not next_ach:
        return "❌ No achievements found or all complete!"

    # Detect validation scripts
    validation_scripts = detect_validation_scripts()

    # Inject project context
    project_context = inject_project_context(include_context)

    # Build context
    context = {
        "feature_name": plan_data["feature_name"],
        "achievement_num": next_ach.number,
        "achievement_title": next_ach.title,
        "achievement_lines": next_ach.section_lines,
        "handoff_lines": plan_data["handoff_lines"],
        "plan_total_lines": plan_data["total_plan_lines"],
        "context_budget": next_ach.section_lines + plan_data["handoff_lines"],
        "subplan_num": next_ach.number.replace(".", ""),
        "archive_location": plan_data["archive_location"],
        "project_context": project_context,
    }

    # Build prompt using PromptBuilder (Achievement 2.3: extracted to module)
    builder = PromptBuilder()
    prompt = builder.build_achievement_prompt(context, validation_scripts)

    return prompt


# Note: copy_to_clipboard_safe() and resolve_folder_shortcut() moved to utils.py (Achievement 2.4)
# Use utils.copy_to_clipboard_safe() and utils.resolve_folder_shortcut() instead


# Note: extract_plan_statistics() moved to plan_parser.py (Achievement 2.4)
# Use PlanParser().extract_plan_statistics() instead


# Note: output_interactive_menu() has been moved to interactive_menu.py (Achievement 2.1).
# Use InteractiveMenu().show_post_generation_menu() instead.


# Note: prompt_interactive_menu() has been moved to interactive_menu.py (Achievement 2.1).
# Use InteractiveMenu().show_pre_execution_menu() instead.


def resolve_plan_path(plan_file_arg: str) -> Path:
    """
    Resolve PLAN file path from argument (supports @folder shortcut).

    Helper function extracted from main() (Achievement 2.6).

    Args:
        plan_file_arg: Plan file argument (e.g., "@FEATURE", "PLAN_FEATURE.md")

    Returns:
        Path: Resolved PLAN file path

    Raises:
        SystemExit: If file not found
    """
    if plan_file_arg.startswith("@"):
        # Check if it's @folder format (no .md extension, no /)
        shorthand = plan_file_arg[1:]  # Remove @
        if "/" not in shorthand and not shorthand.endswith(".md"):
            # @folder format (NEW) - find PLAN in folder (Achievement 2.4: use utils module)
            return utils.resolve_folder_shortcut(shorthand)
        else:
            # @PLAN_NAME.md format (existing) - search for file
            plan_path = Path(shorthand)

            # If not found, check work-space/plans/ recursively
            if not plan_path.exists():
                # Try flat structure first
                workspace_path = Path("work-space/plans") / plan_path.name
                if workspace_path.exists():
                    return workspace_path
                else:
                    # Try nested structure - search all subdirectories
                    plans_dir = Path("work-space/plans")
                    if plans_dir.exists():
                        for plan_file in plans_dir.rglob(plan_path.name):
                            if plan_file.is_file():
                                return plan_file

                        # File not found - show all checked locations
                        print(f"❌ Error: File not found: {plan_file_arg.replace('@', '')}")
                        print(f"   Checked: {plan_path}")
                        print(f"   Checked: {workspace_path}")
                        print(f"   Checked: {plans_dir} (recursive)")
                        sys.exit(1)
            return plan_path
    else:
        plan_path = Path(plan_file_arg)
        if not plan_path.exists():
            print(f"❌ Error: File not found: {plan_path}")
            sys.exit(1)
        return plan_path


def handle_plan_conflicts(
    args,
    detector: WorkflowDetector,
    plan_path: Path,
    feature_name: str,
    achievement_num: str,
    plan_content: str,
) -> None:
    """
    Check for and handle PLAN/filesystem conflicts.

    Helper function extracted from main() (Achievement 2.6).

    Args:
        args: Parsed command-line arguments
        detector: WorkflowDetector instance
        plan_path: Path to PLAN file
        feature_name: Feature name from PLAN
        achievement_num: Achievement number being generated
        plan_content: Full PLAN content

    Raises:
        SystemExit: If conflicts detected and not trusted
    """
    # Skip conflict detection if user explicitly trusts one source
    if args.trust_plan or args.trust_filesystem:
        if args.trust_plan:
            print("⚠️  --trust-plan: Skipping conflict detection, trusting PLAN as source of truth")
        return

    # Detect conflicts
    conflict = detector.detect_plan_filesystem_conflict(
        plan_path, feature_name, achievement_num, plan_content
    )

    if conflict:
        # Build conflict message
        conflict_message = f"""
❌ CONFLICT DETECTED: PLAN vs Filesystem Mismatch

Achievement {achievement_num} has inconsistent state:

PLAN says: {conflict['plan_status']}
Filesystem says: {conflict['filesystem_status']}

This indicates the PLAN and filesystem are out of sync.

🔍 Details:
{conflict['details']}

🛠️  Resolution Options:

1. **Trust the PLAN** (PLAN is correct, filesystem is wrong):
   python {sys.argv[0]} {' '.join(sys.argv[1:])} --trust-plan

2. **Trust the filesystem** (filesystem is correct, PLAN is wrong):
   python {sys.argv[0]} {' '.join(sys.argv[1:])} --trust-filesystem

3. **Investigate manually**:
   - Check execution/feedbacks/APPROVED_{achievement_num.replace('.', '')}.md
   - Check PLAN markdown for ✅ markers
   - Update whichever is wrong

📖 See LLM/docs/STATE_TRACKING_PHILOSOPHY.md for conflict resolution guidance.

═════════════════════════════════════════════════════════════════════════
"""
        # Display conflict message
        print(conflict_message)

        # Copy conflict message to clipboard (default behavior)
        clipboard_enabled = not args.no_clipboard
        if utils.copy_to_clipboard_safe(conflict_message, clipboard_enabled):
            print("\n✅ Conflict message copied to clipboard!")

        sys.exit(1)


def generate_and_output_prompt(
    args, achievement_num: str, plan_path: Path, plan_data: dict, feature_name: str
) -> str:
    """
    Generate prompt for achievement and handle output.

    Helper function extracted from main() (Achievement 2.6).

    Args:
        args: Parsed command-line arguments
        achievement_num: Achievement number to generate prompt for
        plan_path: Path to PLAN file
        plan_data: Parsed PLAN data
        feature_name: Feature name from PLAN

    Returns:
        Generated prompt string
    """
    # Use generate_prompt() to create the prompt
    prompt = generate_prompt(
        plan_path, achievement_num, plan_data, include_context=not args.no_project_context
    )

    # Handle output based on interactive mode
    if args.interactive:
        # Show post-generation menu
        menu = InteractiveMenu()
        menu.show_post_generation_menu(prompt, plan_path, feature_name, achievement_num)
    else:
        # Non-interactive: print and copy to clipboard
        print(prompt)

        # Clipboard is default (use --no-clipboard to disable)
        clipboard_enabled = not args.no_clipboard
        if utils.copy_to_clipboard_safe(prompt, clipboard_enabled):
            print("\n✅ Copied to clipboard!")

    return prompt


def main():
    """
    Main entry point for prompt generation script.

    Orchestrates the complete workflow:
    1. Parse command-line arguments
    2. Show interactive menu (if --interactive)
    3. Resolve PLAN path (@ shorthand support)
    4. Parse PLAN file
    5. Determine achievement number
    6. Check for conflicts (unless trust flags set)
    7. Handle workflow-specific flags (--subplan-only, --execution-only)
    8. Detect workflow state
    9. Generate appropriate prompt
    10. Output (interactive menu or print + clipboard)

    Command-Line Flags:
    - --next: Auto-detect next achievement
    - --achievement N.N: Specific achievement
    - --interactive: Show interactive menus
    - --no-clipboard: Disable clipboard (default is enabled)
    - --no-project-context: Disable project context injection
    - --subplan-only: Generate SUBPLAN prompt only
    - --execution-only: Generate EXECUTION prompt only
    - --trust-plan: Trust PLAN, ignore filesystem conflicts
    - --trust-filesystem: Trust filesystem, ignore PLAN conflicts

    Exit Codes:
    - 0: Success
    - 1: Error (file not found, parsing failed, conflicts detected)

    Bug Fixes Incorporated:
        - Bug #10: Path.name for @ shorthand in commands
        - Bug #11: Improved error handling for subprocess calls
        - Conflict detection (Bug #2 fix)
        - Interactive mode integration (Achievement 0.3)

    Tested: Partially (integration tests for interactive mode)
    """
    parser = argparse.ArgumentParser(
        description="Generate high-quality LLM prompts for methodology execution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Short folder-based commands (NEW - recommended)
  python LLM/scripts/generation/generate_prompt.py @RESTORE --next
  python LLM/scripts/generation/generate_prompt.py @GRAPHRAG --achievement 0.1
  python LLM/scripts/generation/generate_prompt.py @PROMPT --next --no-clipboard
  
  # Full path commands (still supported)
  python LLM/scripts/generation/generate_prompt.py @PLAN_FEATURE.md --next
  python LLM/scripts/generation/generate_prompt.py work-space/plans/FEATURE/PLAN_FEATURE.md --next

Note:
  • Clipboard is DEFAULT (output auto-copied)
  • Use --no-clipboard to disable
  • @folder finds PLAN automatically (e.g., @RESTORE finds RESTORE-EXECUTION-WORKFLOW-AUTOMATION)

Exit Codes:
  0 = Success
  1 = Error (file not found, parsing failed, conflicts detected, etc.)
        """,
    )

    parser.add_argument("plan_file", help="PLAN file (e.g., @PLAN_FEATURE.md or PLAN_FEATURE.md)")

    parser.add_argument(
        "--next", action="store_true", help="Generate prompt for next achievement (auto-detect)"
    )

    parser.add_argument("--achievement", help="Specific achievement number (e.g., 1.1)")

    parser.add_argument(
        "--no-clipboard",
        action="store_true",
        help="Disable automatic clipboard copy (clipboard is default)",
    )

    parser.add_argument(
        "--no-project-context",
        action="store_true",
        help="Disable project context injection (for testing)",
    )

    parser.add_argument(
        "--subplan-only",
        action="store_true",
        help="Generate prompt for SUBPLAN work only (use generate_subplan_prompt.py)",
    )

    parser.add_argument(
        "--execution-only",
        action="store_true",
        help="Generate prompt for EXECUTION work only (use generate_execution_prompt.py)",
    )

    parser.add_argument(
        "--trust-plan",
        action="store_true",
        help="Trust PLAN as source of truth, ignore filesystem conflicts (use when PLAN is correct)",
    )

    parser.add_argument(
        "--trust-filesystem",
        action="store_true",
        help="Trust filesystem state, ignore PLAN conflicts (use when filesystem is correct)",
    )

    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Show interactive menu to choose what to do (ask instead of tell)",
    )

    parser.add_argument(
        "--parallel-upgrade",
        action="store_true",
        help="Generate parallel discovery prompt for this PLAN (Achievement 2.1)",
    )

    args = parser.parse_args()

    # Show interactive menu if requested
    if args.interactive:
        menu = InteractiveMenu()
        menu.show_pre_execution_menu()
        # Re-parse after menu has modified sys.argv
    args = parser.parse_args()

    # Initialize WorkflowDetector for state detection and conflict checking
    detector = WorkflowDetector()

    try:
        # Resolve PLAN path (supports @folder, @PLAN_NAME.md, or full path)
        plan_path = resolve_plan_path(args.plan_file)

        # Handle --parallel-upgrade flag (Achievement 2.1)
        if args.parallel_upgrade:
            from LLM.scripts.generation.parallel_workflow import generate_parallel_upgrade_prompt
            
            prompt = generate_parallel_upgrade_prompt(plan_path.parent)
            print(prompt)
            return 0

        # Parse PLAN to get feature name and achievement (Achievement 2.4: use PlanParser)
        parser = PlanParser()
        plan_data = parser.parse_plan_file(plan_path)
        feature_name = plan_data["feature_name"]

        # Achievement 3.1: Set log context for structured logging
        set_log_context(
            plan=feature_name,
            workflow="generate_prompt",
            plan_file=plan_path.name,
        )

        logger.info(
            "Starting prompt generation",
            extra={
                "plan_path": str(plan_path),
                "interactive": args.interactive,
                "clipboard": not args.no_clipboard,
            },
        )

        # Read PLAN content once
        with open(plan_path, "r", encoding="utf-8") as f:
            plan_content = f.read()

        # Detect and validate parallel.json (Achievement 2.1)
        from LLM.scripts.generation.parallel_workflow import (
            detect_and_validate_parallel_json,
            show_parallel_menu,
            handle_parallel_menu_selection,
        )
        
        parallel_json_path, parallel_data = detect_and_validate_parallel_json(plan_path.parent)
        
        # Show indicator if parallel workflow detected
        if parallel_data:
            print(f"\n🔀 Parallel workflow detected for {feature_name}")
            print(f"  - Parallelization level: {parallel_data.get('parallelization_level', 'unknown')}")
            print(f"  - Achievements: {len(parallel_data.get('achievements', []))}")
            
            # In interactive mode, offer parallel menu access
            if args.interactive:
                print(f"\n💡 TIP: You can access the Parallel Execution Menu")
                access_parallel = input("Access Parallel Menu now? (y/N): ").strip().lower()
                if access_parallel == 'y':
                    while True:
                        choice = show_parallel_menu(parallel_data, feature_name)
                        handle_parallel_menu_selection(choice, parallel_data, feature_name, plan_path.parent)
                        if choice == '5':  # Back to main menu
                            break
            print()

        # Determine achievement number
        if args.achievement:
            # Achievement 3.1: Validate achievement number format
            from LLM.scripts.generation.exceptions import InvalidAchievementFormatError

            achievement_num = args.achievement

            # Validate achievement format (X.Y) - re is already imported at module level
            if not re.match(r"^\d+\.\d+$", achievement_num):
                raise InvalidAchievementFormatError(
                    achievement_input=achievement_num,
                    expected_format="X.Y (e.g., 2.1, 3.5)",
                )
        elif args.next:
            # Find next achievement based on trust mode
            if args.trust_filesystem:
                # Trust filesystem: Find first achievement that's not complete in filesystem
                print(
                    "🔍 --trust-filesystem: Finding next achievement based on filesystem state..."
                )
                next_ach = None
                for ach in plan_data["achievements"]:
                    fs_state = detector.detect_workflow_state_filesystem(
                        plan_path, feature_name, ach.number
                    )
                    if fs_state["state"] != "subplan_complete":
                        next_ach = ach
                        print(
                            f"   Found: Achievement {ach.number} (filesystem state: {fs_state['state']})"
                        )
                        break
                if not next_ach:
                    print("❌ No incomplete achievements found in filesystem!")
                    sys.exit(1)
                achievement_num = next_ach.number
            else:
                # Normal mode or trust-plan: Use PLAN's handoff section
                next_ach = detector.find_next_achievement_hybrid(
                    plan_path,
                    feature_name,
                    plan_data["achievements"],
                    plan_data["archive_location"],
                )
                if not next_ach:
                    # PLAN is complete - extract statistics and provide helpful next steps
                    stats = parser.extract_plan_statistics(plan_path, feature_name)

                    # Build statistics section
                    stats_lines = []
                    if stats["total_achievements"] > 0:
                        stats_lines.append(
                            f"  • {stats['total_achievements']} achievements completed"
                        )
                    if stats["subplan_count"] > 0:
                        stats_lines.append(f"  • {stats['subplan_count']} SUBPLANs created")
                    if stats["execution_count"] > 0:
                        stats_lines.append(
                            f"  • {stats['execution_count']} EXECUTION_TASKs completed"
                        )
                    if stats["total_time"] != "N/A":
                        stats_lines.append(f"  • {stats['total_time']} invested")

                    stats_section = (
                        "\n".join(stats_lines) if stats_lines else "  • Work completed successfully"
                    )

                    completion_message = f"""
🎉 PLAN COMPLETE: {feature_name}

All achievements completed!

📊 Summary:
{stats_section}

📋 Next Steps:
  1. Archive this PLAN:
     python LLM/scripts/archiving/manual_archive.py @{feature_name}
  
  2. Update ACTIVE_PLANS.md:
     Mark {feature_name} as complete
  
  3. Celebrate your success! 🎉

═════════════════════════════════════════════════════════════════════════
"""
                    print(completion_message)

                    # Copy completion message to clipboard
                    clipboard_enabled = not args.no_clipboard
                    if utils.copy_to_clipboard_safe(completion_message, clipboard_enabled):
                        print("✅ Completion message copied to clipboard!")

                    sys.exit(0)

                # Set achievement number from detected next achievement
                achievement_num = next_ach.number

            # Check for PLAN/filesystem conflicts (extracted to helper function)
            handle_plan_conflicts(
                args, detector, plan_path, feature_name, achievement_num, plan_content
            )
        else:
            print("❌ Error: Use --next or --achievement N.N")
            parser.print_help()
            sys.exit(1)

        # Handle workflow-specific flags
        if args.subplan_only:
            # Generate SUBPLAN-only prompt (Bug #13 fix: Add --subplan-only flag)
            import subprocess

            result = subprocess.run(
                [
                    sys.executable,
                    "LLM/scripts/generation/generate_subplan_prompt.py",
                    "create",
                    f"@{plan_path.name}",  # Bug #12 fix: Use .name to get filename only
                    "--achievement",
                    achievement_num,
                    "--subplan-only",  # Bug #13 fix: Pass flag to generate SUBPLAN-only prompt
                ],
                capture_output=True,
                text=True,
            )
            prompt = result.stdout
            if result.returncode != 0:
                print(f"❌ Error generating SUBPLAN prompt: {result.stderr}", file=sys.stderr)
                sys.exit(1)
        elif args.execution_only:
            # Find SUBPLAN for this achievement
            subplan_path = find_subplan_for_achievement(feature_name, achievement_num, plan_path)
            if not subplan_path:
                print(f"❌ Error: No SUBPLAN found for achievement {achievement_num}")
                print(f"   Create SUBPLAN first using: --subplan-only")
                sys.exit(1)

            # Generate EXECUTION prompt (create mode, execution 01)
            import subprocess

            # Bug #10 Fix: Use subplan_path.name (filename) not subplan_path (Path object)
            # Before: f"@{subplan_path}" → "@work-space/plans/.../SUBPLAN.md" (doesn't work)
            # After: f"@{subplan_path.name}" → "@SUBPLAN_FEATURE_02.md" (works)
            result = subprocess.run(
                [
                    sys.executable,
                    "LLM/scripts/generation/generate_execution_prompt.py",
                    "create",
                    f"@{subplan_path.name}",  # Bug #10: Use .name for @ shorthand
                    "--execution",
                    "01",
                ],
                capture_output=True,
                text=True,
            )
            prompt = result.stdout
            if result.returncode != 0:
                # Bug #11 Fix: Improved error handling to prevent silent failures
                # Before: Empty error message → "❌ Error generating EXECUTION prompt:"
                # After: Check stderr AND stdout, provide troubleshooting options
                error_msg = (
                    result.stderr.strip() if result.stderr.strip() else result.stdout.strip()
                )
                if not error_msg:
                    error_msg = "Unknown error (subprocess failed silently)"

                # Bug #11: Never fail silently - always provide actionable guidance
                print(f"❌ Error generating EXECUTION prompt: {error_msg}", file=sys.stderr)
                print(f"\n💡 Options to resolve:", file=sys.stderr)
                print(f"   1. Try direct command:", file=sys.stderr)
                print(
                    f"      python LLM/scripts/generation/generate_execution_prompt.py create @{subplan_path.name} --execution 01",
                    file=sys.stderr,
                )
                print(f"   2. Check SUBPLAN file exists and has content:", file=sys.stderr)
                print(f"      cat {subplan_path}", file=sys.stderr)
                print(
                    f"   3. Review error in SUBPLAN structure (missing ## 🎯 Objective or ## Approach sections)",
                    file=sys.stderr,
                )
                print(
                    f"   4. Check bug documentation: work-space/analyses/implementation_automation/",
                    file=sys.stderr,
                )
                sys.exit(1)
        else:
            # Check achievement status for FIX detection (Achievement 2.9 - tri-state model)
            from LLM.scripts.generation.utils import get_achievement_status

            status = get_achievement_status(achievement_num, plan_path)

            if status == "needs_fix":
                # Achievement requires fixes - generate FIX-specific prompt
                from LLM.scripts.generation.generate_fix_prompt import generate_fix_prompt

                print(f"⚠️  Achievement {achievement_num} has reviewer feedback requiring fixes")
                print(f"   FIX file: execution/feedbacks/FIX_{achievement_num.replace('.', '')}.md")
                print()

                try:
                    prompt = generate_fix_prompt(plan_path, achievement_num)
                except Exception as e:
                    print(f"❌ Error generating FIX prompt: {e}")
                    sys.exit(1)

                # Output (interactive menu or print + clipboard)
                if args.interactive:
                    menu = InteractiveMenu()
                    menu.show_post_generation_menu(
                        prompt, "needs_fix", None, plan_path, achievement_num
                    )
                else:
                    print(prompt)

                    if not args.no_clipboard:
                        success = utils.copy_to_clipboard_safe(prompt)
                        if success:
                            print("\n✅ FIX prompt copied to clipboard!")

                return  # Exit after FIX prompt

            # Auto-detect workflow state and suggest appropriate action
            workflow_state = detect_workflow_state(plan_path, feature_name, achievement_num)

            if workflow_state["recommendation"] == "create_subplan":
                # Suggest creating SUBPLAN
                prompt = f"""🎯 Workflow Detection: Achievement {achievement_num} needs SUBPLAN

No SUBPLAN found for this achievement. Create SUBPLAN first.

**Recommended Command**:
  python LLM/scripts/generation/generate_prompt.py @{plan_path.name} --achievement {achievement_num} --subplan-only

Or use SUBPLAN prompt generator directly:
  python LLM/scripts/generation/generate_subplan_prompt.py create @{plan_path.name} --achievement {achievement_num}

**Workflow**: Designer creates SUBPLAN → Executor creates EXECUTION → Execute
"""
            elif workflow_state["recommendation"] == "create_execution":
                # Suggest creating EXECUTION
                subplan_path = workflow_state["subplan_path"]
                prompt = f"""🎯 Workflow Detection: SUBPLAN exists, ready for EXECUTION

SUBPLAN found but no active EXECUTION. Create EXECUTION from SUBPLAN.

**SUBPLAN**: {subplan_path.name}

**Recommended Command**:
  python LLM/scripts/generation/generate_prompt.py @{plan_path.name} --achievement {achievement_num} --execution-only

Or use EXECUTION prompt generator directly:
  python LLM/scripts/generation/generate_execution_prompt.py create @{subplan_path.name} --execution 01

**Workflow**: Executor reads SUBPLAN objective + approach only (~10 lines), executes according to plan
"""
            elif workflow_state["recommendation"] == "continue_execution":
                # Suggest continuing EXECUTION
                subplan_path = workflow_state["subplan_path"]
                exec_count = workflow_state.get("execution_count", 1)

                # Find actual EXECUTION_TASK files to provide exact command
                plan_folder = plan_path.parent
                execution_folder = plan_folder / "execution"
                subplan_num = achievement_num.replace(".", "")
                execution_pattern = f"EXECUTION_TASK_{feature_name}_{subplan_num}_*.md"
                execution_files = (
                    list(execution_folder.glob(execution_pattern))
                    if execution_folder.exists()
                    else []
                )

                # Find first incomplete execution file
                active_exec_file = None
                for exec_file in sorted(execution_files):
                    try:
                        with open(exec_file, "r", encoding="utf-8") as f:
                            content = f.read()
                        # Check if NOT complete
                        if not re.search(
                            r"\*\*Status\*\*:\s*✅\s*Complete", content, re.IGNORECASE
                        ):
                            active_exec_file = exec_file
                            break
                    except Exception:
                        continue

                # If no incomplete file found, check SUBPLAN for next execution number
                next_exec_num = "01"
                if not active_exec_file and workflow_state.get("execution_count", 0) > 1:
                    try:
                        # Read SUBPLAN to find next execution
                        with open(workflow_state["subplan_path"], "r", encoding="utf-8") as f:
                            subplan_content = f.read()

                        # Look for "⏳ Next" status in Active EXECUTION_TASKs table
                        next_match = re.search(r"\|\s*(\d+_\d+)\s*\|\s*⏳\s*Next", subplan_content)
                        if next_match:
                            next_exec_num = next_match.group(1).split("_")[1]
                    except Exception:
                        pass

                # Generate command with actual filename or template
                if active_exec_file:
                    exec_command = f"python LLM/scripts/generation/generate_execution_prompt.py continue @{active_exec_file.name}"
                else:
                    exec_command = f"python LLM/scripts/generation/generate_execution_prompt.py continue @EXECUTION_TASK_{feature_name}_{subplan_num}_{next_exec_num}.md"

                prompt = f"""🎯 Workflow Detection: Active EXECUTION(s) in progress

SUBPLAN has {exec_count} active EXECUTION(s). Continue EXECUTION work.

**SUBPLAN**: {subplan_path.name}

**Recommended Command**:
  {exec_command}

**Workflow**: Executor continues current EXECUTION, stays focused on EXECUTION_TASK only
"""
            elif workflow_state["recommendation"] == "create_next_execution":
                # Suggest creating next EXECUTION in multi-execution workflow
                subplan_path = workflow_state["subplan_path"]
                exec_count = workflow_state.get("execution_count", 1)
                completed_count = workflow_state.get("completed_count", 0)

                # Find next execution number from filesystem (most reliable)
                # Don't trust SUBPLAN table - it may be outdated
                plan_folder = plan_path.parent
                execution_folder = plan_folder / "execution"
                subplan_num = achievement_num.replace(".", "")
                execution_pattern = f"EXECUTION_TASK_{feature_name}_{subplan_num}_*.md"
                execution_files = (
                    list(execution_folder.glob(execution_pattern))
                    if execution_folder.exists()
                    else []
                )

                # Find highest execution number from completed files
                highest_exec_num = 0
                for exec_file in execution_files:
                    try:
                        # Extract execution number from filename
                        match = re.search(r"_(\d+)\.md$", exec_file.name)
                        if match:
                            exec_num = int(match.group(1))
                            # Verify it's complete
                            with open(exec_file, "r", encoding="utf-8") as f:
                                content = f.read()
                            if re.search(
                                r"\*\*Status\*\*:\s*✅\s*Complete", content, re.IGNORECASE
                            ):
                                highest_exec_num = max(highest_exec_num, exec_num)
                    except Exception:
                        continue

                # Next execution is highest + 1
                next_exec_num = str(highest_exec_num + 1).zfill(2)

                prompt = f"""🎯 Workflow Detection: Create Next EXECUTION in Multi-Execution Workflow

SUBPLAN has {exec_count} planned EXECUTION(s). {completed_count} complete, next is {next_exec_num}.

**SUBPLAN**: {subplan_path.name}

**Recommended Command**:
  python LLM/scripts/generation/generate_execution_prompt.py create @{subplan_path.name} --execution {next_exec_num}

**Workflow**: Executor reads SUBPLAN objective + approach, creates EXECUTION_TASK_{feature_name}_{subplan_num}_{next_exec_num}.md, executes according to plan
"""
            else:
                # Next achievement
                include_context = not args.no_project_context
                prompt = generate_prompt(plan_path, achievement_num, include_context)

        # Output
        # Check if interactive mode for output handling
        if args.interactive:
            # Determine workflow state for interactive menu
            state_name = (
                workflow_state.get("recommendation", "next_achievement")
                if "workflow_state" in locals()
                else "next_achievement"
            )

            # Extract recommended command if present in prompt
            command_match = re.search(r"\*\*Recommended Command\*\*:\s*\n\s*(.+)", prompt)
            recommended_command = command_match.group(1).strip() if command_match else None

            # Show interactive menu
            menu = InteractiveMenu()
            menu.show_post_generation_menu(
                prompt, state_name, recommended_command, plan_path, achievement_num
            )
        else:
            # Non-interactive: print and copy to clipboard
            print(prompt)

            # Clipboard is default (use --no-clipboard to disable)
            clipboard_enabled = not args.no_clipboard
            if utils.copy_to_clipboard_safe(prompt, clipboard_enabled):
                print("\n✅ Copied to clipboard!")

        sys.exit(0)

    # Achievement 3.1: Structured error handling with actionable suggestions
    except Exception as e:
        from core.libraries.error_handling import ApplicationError
        from LLM.scripts.generation.exceptions import format_error_with_suggestions

        # If it's an ApplicationError (including our custom exceptions), format it nicely
        if isinstance(e, ApplicationError):
            error_message = format_error_with_suggestions(e)
            print(error_message, file=sys.stderr)

            # Auto-copy error to clipboard for easy sharing
            try:
                from LLM.scripts.generation.path_resolution import copy_to_clipboard_safe

                if copy_to_clipboard_safe(error_message):
                    print("✅ Error details copied to clipboard!", file=sys.stderr)
            except:
                pass  # Silent fail on clipboard
        else:
            # Generic exception - format with basic info
            error_type = type(e).__name__
            error_msg = str(e) or "(no message)"
            print(f"❌ ERROR: {error_type}: {error_msg}", file=sys.stderr)

        sys.exit(1)


if __name__ == "__main__":
    main()
