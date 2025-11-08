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
  • Pre-execution: prompt_interactive_menu() - Choose workflow
  • Post-generation: output_interactive_menu() - Handle output
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

File Size: 2,270 lines (growing, needs modularization)
Functions: 24 total
Test Coverage: ~25% (49 tests, but 21 of 24 functions untested)
Known Issues: Fragile text parsing (Bugs #1-8 root cause)

Planned Refactor (Priority 2):
  • Achievement 2.4: Filesystem state management (eliminate parsing bugs)
  • Achievement 2.5: Migration & validation
  • Achievement 2.6: Class-based architecture (5 classes)
    - PromptGenerator (orchestration)
    - PlanParser (markdown fallback)
    - WorkflowDetector (filesystem-first)
    - ConflictDetector (validation)
    - InteractiveMenu (two-stage UI)

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

# Import structure detection for dual structure support
try:
    from LLM.scripts.workflow.structure_detection import detect_structure
except ImportError:
    # Fallback if structure_detection not available (backward compatibility)
    def detect_structure(plan_path: Path) -> str:
        """Fallback: always return flat structure."""
        return "flat"


@dataclass
class Achievement:
    """Achievement data structure."""

    number: str  # "0.1", "1.1"
    title: str
    goal: str
    effort: str  # "2-3 hours"
    priority: str
    section_lines: int  # Lines in achievement section


def parse_plan_file(plan_path: Path) -> dict:
    """
    Extract structured data from PLAN file for prompt generation.
    
    Parses PLAN markdown to extract:
    - Feature name (from filename)
    - All achievements (number, title, section size)
    - Archive location
    - Handoff section size
    
    Used by: generate_prompt(), main()
    Tested: Yes (4 tests in test_core_parsing.py)
    
    Args:
        plan_path: Path to PLAN markdown file
    
    Returns:
        dict with keys:
            - feature_name: str (e.g., "RESTORE-EXECUTION-WORKFLOW-AUTOMATION")
            - achievements: List[Achievement] (all achievements in PLAN)
            - archive_location: str (e.g., "./feature-archive/")
            - total_plan_lines: int (total lines in PLAN)
            - handoff_lines: int (lines in "Current Status & Handoff" section)
    
    Example:
        >>> plan_data = parse_plan_file(Path("PLAN_FEATURE.md"))
        >>> print(plan_data["feature_name"])
        "FEATURE"
        >>> print(len(plan_data["achievements"]))
        7
    """
    with open(plan_path, "r", encoding="utf-8") as f:
        content = f.read()
        lines = content.split("\n")
    
    # Extract feature name
    feature_name = plan_path.stem.replace("PLAN_", "")
    
    # Parse achievements
    achievements = []
    for i, line in enumerate(lines):
        if match := re.match(r"\*\*Achievement (\d+\.\d+)\*\*:(.+)", line):
            ach_num = match.group(1)
            ach_title = match.group(2).strip()
            
            # Estimate section size (until next achievement or section)
            section_lines = estimate_section_size(lines, i)
            
            achievements.append(
                Achievement(
                number=ach_num,
                title=ach_title,
                goal="",  # Would need more parsing
                effort="",  # Would need more parsing
                priority="",  # Would need more parsing
                    section_lines=section_lines,
                )
            )
    
    # Find archive location
    archive_location = find_archive_location(lines)
    
    # Calculate handoff section size
    handoff_lines = calculate_handoff_size(lines)
    
    return {
        "feature_name": feature_name,
        "achievements": achievements,
        "archive_location": archive_location,
        "total_plan_lines": len(lines),
        "handoff_lines": handoff_lines,
    }


def extract_handoff_section(plan_content: str) -> Optional[str]:
    """
    Extract 'Current Status & Handoff' section content from PLAN.
    
    This section is the AUTHORITATIVE source for workflow state - it tells us
    what's complete, what's next, and what's in progress. Used by all
    achievement finding and conflict detection functions.
    
    Handles variations:
    - "## 📝 Current Status & Handoff"
    - "## Current Status & Handoff"
    - "## Current Status and Handoff"
    
    Bug Fixes Incorporated:
        - Handles emoji variations in section header
        - Stops at next ## header (not greedy)
        - Returns None if section is empty or only contains separators
    
    Used by: find_next_achievement_from_plan(), is_achievement_complete(),
             get_plan_status(), is_plan_complete(), detect_plan_filesystem_conflict()
    Tested: Yes (4 tests in test_core_parsing.py)

    Args:
        plan_content: Full PLAN file content as string

    Returns:
        Section content as string, or None if section not found or empty
    
    Example:
        >>> content = Path("PLAN_FEATURE.md").read_text()
        >>> handoff = extract_handoff_section(content)
        >>> print("Next:" in handoff)
        True
    """
    lines = plan_content.split("\n")
    section_start = None

    # Find section start - look for "Current Status & Handoff" header
    for i, line in enumerate(lines):
        # Match variations: "## 📝 Current Status & Handoff", "## Current Status & Handoff", etc.
        if re.search(r"##\s*.*Current Status.*Handoff", line, re.IGNORECASE):
            section_start = i
            break

    if section_start is None:
        return None

    # Extract content until next ## section header
    section_lines = []
    for i in range(section_start + 1, len(lines)):
        line = lines[i]
        # Stop at next ## header (any level)
        if line.strip().startswith("##"):
            break
        section_lines.append(line)

    # Return section content, or None if empty
    content = "\n".join(section_lines).strip()
    # Consider section empty if it only contains whitespace, dashes, or horizontal rules
    if not content or content.strip() in ("", "---", "***", "___"):
        return None
    return content


def find_next_achievement_from_plan(plan_content: str) -> Optional[str]:
    """
    Find next achievement from PLAN's 'Current Status & Handoff' section.
    
    This is the PRIMARY method for finding next achievement - it reads the
    PLAN's explicit "Next:" statement in the handoff section, which is the
    most authoritative source of workflow state.
    
    Search Strategy:
    1. Check handoff section first (authoritative)
    2. Try multiple patterns (⏳ Next:, Next:, etc.)
    3. Fall back to full file if handoff doesn't have clear "Next"
    
    Pattern Priority (specific → generic):
    - "⏳ Next: Achievement X.Y" (most specific)
    - "Next: Achievement X.Y"
    - "⏳ Achievement X.Y"
    - "**Next**: ... Achievement X.Y" (most greedy, last)
    
    Bug Fixes Incorporated:
        - Bug #6: Reordered patterns to avoid greedy matches
        - Prioritizes handoff section over full file
        - Handles emoji variations
    
    Used by: find_next_achievement_hybrid(), main()
    Tested: Yes (4 tests in test_core_parsing.py)
    
    Args:
        plan_content: Full PLAN file content as string
    
    Returns:
        Achievement number (e.g., "1.1") or None if not found
    
    Example:
        >>> content = Path("PLAN_FEATURE.md").read_text()
        >>> next_ach = find_next_achievement_from_plan(content)
        >>> print(next_ach)
        "1.2"
    """
    # Reordered patterns: specific formats first, generic/greedy last
    # Pattern 4 first (most specific): ⏳ Next: Achievement
    # Pattern 1 last (most greedy): **Next**: ... Achievement (matches across sections)
    patterns = [
        r"⏳\s*Next[:\s]+Achievement\s+(\d+\.\d+)",  # Pattern 4: ⏳ Next: Achievement (most specific)
        r"(?:Next|What\'s Next)[:\s]+Achievement\s+(\d+\.\d+)",  # Pattern 2: Next: Achievement
        r"Next[:\s]+Achievement\s+(\d+\.\d+)",  # Pattern 5: Next: Achievement (generic)
        r"⏳\s*Achievement\s+(\d+\.\d+)",  # Pattern 3: ⏳ Achievement (least specific)
        r"(?:Next|What\'s Next)\*\*[:\s]+.*?Achievement\s+(\d+\.\d+)",  # Pattern 1: **Next**: ... Achievement (most greedy, last)
    ]

    # Primary: Try handoff section first (authoritative source)
    handoff_section = extract_handoff_section(plan_content)
    if handoff_section:
        # Search patterns in handoff section only
        for pattern in patterns:
            match = re.search(pattern, handoff_section, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1)

    # Fallback: Search full file (reordered patterns)
    for pattern in patterns:
        match = re.search(pattern, plan_content, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1)

    return None


def find_next_achievement_from_archive(
    feature_name: str, achievements: List[Achievement], archive_location: str, plan_content: str
) -> Optional[Achievement]:
    """
    Find first achievement without archived SUBPLAN (fallback detection method).
    
    This is a FALLBACK method used when handoff section doesn't have clear
    "Next:" statement. Checks archive directory for SUBPLANs.
    
    Detection Logic:
    1. Check if archive directory exists
    2. For each achievement (in order):
       - Skip if marked complete in PLAN
       - Check if SUBPLAN exists in archive
       - Return first achievement without archived SUBPLAN
    
    Bug Fixes Incorporated:
        - Bug #2: Skips completed achievements (fixes duplicate detection)
        - Validates achievement is not complete before returning
    
    Used by: find_next_achievement_hybrid()
    Tested: No (Priority 1.3 - needs tests)

    Args:
        feature_name: Feature name
        achievements: List of achievements
        archive_location: Archive directory path
        plan_content: PLAN file content (for completion checking)

    Returns:
        First incomplete achievement without archived SUBPLAN, or None
    
    Example:
        >>> next_ach = find_next_achievement_from_archive("FEATURE", achievements, "./archive/", content)
        >>> print(next_ach.number if next_ach else None)
        "1.2"
    """
    # Convert archive location string to Path
    archive_path = Path(archive_location)

    # Check if archive location exists
    if not archive_path.exists():
        return None

    # Check subplans directory
    archive_subplans = archive_path / "subplans"
    if not archive_subplans.exists():
        return None

    # Find first achievement without archived SUBPLAN
    for ach in achievements:
        # SKIP if marked complete (fixes Bug #2, #3)
        if is_achievement_complete(ach.number, plan_content):
            continue

        # Check if SUBPLAN exists in archive
        subplan_num = ach.number.replace(".", "")
        subplan_file = archive_subplans / f"SUBPLAN_{feature_name}_{subplan_num}.md"
        if not subplan_file.exists():
            return ach

    return None


def find_next_achievement_from_root(
    feature_name: str, achievements: List[Achievement], plan_content: str
) -> Optional[Achievement]:
    """
    Find first achievement without SUBPLAN in root directory (fallback method).
    
    This is a FALLBACK method for flat workspace structure (legacy).
    Most PLANs now use nested structure, so this is rarely used.
    
    Detection Logic:
    1. For each achievement (in order):
       - Skip if marked complete in PLAN
       - Check if SUBPLAN exists in root (flat structure)
       - Return first achievement without SUBPLAN
    
    Bug Fixes Incorporated:
        - Bug #2: Skips completed achievements (fixes duplicate detection)
    
    Used by: find_next_achievement_hybrid()
    Tested: No (Priority 1.3 - needs tests)

    Args:
        feature_name: Feature name
        achievements: List of achievements
        plan_content: PLAN file content (for completion checking)

    Returns:
        First incomplete achievement without SUBPLAN, or None
    
    Example:
        >>> next_ach = find_next_achievement_from_root("FEATURE", achievements, content)
        >>> print(next_ach.number if next_ach else None)
        "1.2"
    """
    for ach in achievements:
        # SKIP if marked complete (fixes Bug #2, #3)
        if is_achievement_complete(ach.number, plan_content):
            continue

        # Check if SUBPLAN exists in root
        subplan_num = ach.number.replace(".", "")
        subplan_file = Path(f"SUBPLAN_{feature_name}_{subplan_num}.md")
        if not subplan_file.exists():
            return ach
    return None


def is_achievement_complete(ach_num: str, plan_content: str) -> bool:
    """
    Check if a single achievement is marked complete in PLAN.
    
    Critical function for workflow state detection - determines if we should
    skip an achievement or work on it. Used by conflict detection, achievement
    finding, and PLAN completion checking.
    
    Search Strategy:
    1. Check handoff section first (most authoritative source)
    2. Try multiple completion patterns (✅, "Complete:", etc.)
    3. Fall back to full PLAN if handoff doesn't have info
    
    Completion Patterns Recognized:
    - "✅ Achievement 1.1 complete"
    - "✅ Achievement 1.1"
    - "- ✅ Achievement 1.1"
    - "Achievement 1.1 ... ✅"
    - "Achievement 1.1 Complete:"
    
    Bug Fixes Incorporated:
        - Bug #2: Skips completed achievements (fixes duplicate detection)
        - Bug #3: Checks handoff section first (authoritative)
        - Handles emoji variations and format differences
    
    Used by: find_next_achievement_from_archive(), find_next_achievement_from_root(),
             find_next_achievement_hybrid(), is_plan_complete()
    Tested: No (Priority 1.3 - needs tests)

    Args:
        ach_num: Achievement number (e.g., "1.1")
        plan_content: Full PLAN file content

    Returns:
        True if achievement is marked complete, False otherwise
    
    Example:
        >>> content = Path("PLAN_FEATURE.md").read_text()
        >>> is_achievement_complete("0.1", content)
        True
        >>> is_achievement_complete("0.3", content)
        False
    """
    # Extract handoff section (most authoritative)
    handoff_section = extract_handoff_section(plan_content)

    # Priority 1: Check handoff section
    if handoff_section:
        patterns = [
            rf"✅\s+Achievement\s+{re.escape(ach_num)}\s+complete",
            rf"✅\s+Achievement\s+{re.escape(ach_num)}",
            rf"- ✅ Achievement {re.escape(ach_num)}",
            rf"Achievement\s+{re.escape(ach_num)}.*✅",
            # Match "Achievement X.Y Complete:" format (no emoji)
            rf"Achievement\s+{re.escape(ach_num)}\s+Complete:?",
        ]
        for pattern in patterns:
            if re.search(pattern, handoff_section, re.IGNORECASE):
                return True

    # Priority 2: Check full plan content (fallback)
    patterns = [
        rf"✅\s+Achievement\s+{re.escape(ach_num)}\s+complete",
        rf"✅\s+Achievement\s+{re.escape(ach_num)}",
    ]
    for pattern in patterns:
        if re.search(pattern, plan_content, re.IGNORECASE):
            return True

    return False


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
    handoff_section = extract_handoff_section(plan_content)
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


def is_plan_complete(plan_content: str, achievements: List[Achievement]) -> bool:
    """
    Check if PLAN is complete (all achievements done).
    
    Critical function that determines if we should show completion message
    or continue with next achievement. Must be accurate to avoid false
    completions or missing actual completions.
    
    Completion Detection Strategy:
    1. Check handoff section for explicit completion indicators
    2. Try multiple completion patterns (specific → generic)
    3. Count completed achievements vs total
    4. Validate completion (not in code blocks)
    
    Completion Patterns Recognized:
    - "All achievements complete"
    - "All Priority N complete"
    - "PLAN complete"
    - "Status: Complete"
    - "7/7 achievements complete"
    
    Bug Fixes Incorporated:
        - Bug #2: More specific patterns to avoid false positives
        - Bug #4: Doesn't match "plan_completion.py" or similar
        - Validates match is not in code block
        - Uses is_achievement_complete() for consistency
    
    Used by: find_next_achievement_hybrid(), main()
    Tested: No (Priority 1.3 - needs tests)

    Args:
        plan_content: Full PLAN file content as string
        achievements: List of achievements from PLAN

    Returns:
        True if all achievements are complete, False otherwise
    
    Example:
        >>> content = Path("PLAN_FEATURE.md").read_text()
        >>> achievements = parse_plan_file(Path("PLAN_FEATURE.md"))["achievements"]
        >>> is_plan_complete(content, achievements)
        True
    """
    # Extract handoff section (most authoritative source)
    handoff_section = extract_handoff_section(plan_content)
    if not handoff_section:
        # No handoff section means PLAN is likely not started or incomplete
        return False

    # Check for explicit completion indicators (MORE SPECIFIC)
    completion_patterns = [
        r"\bAll\s+achievements?\s+complete\b",  # "All achievements complete" (not "all achievements are complete")
        r"\bAll\s+Priority\s+\d+\s+complete\b",  # "All Priority 1 complete"
        r"\bPLAN\s+complete\b",  # "PLAN complete" (not "plan_completion.py")
        r"\bStatus[:\s]+Complete\b",  # "Status: Complete" (not "Status**: Achievement 2.1 Complete")
        r"✅\s+PLAN\s+Complete",  # "✅ PLAN Complete"
        r"PLAN\s+✅\s+Complete",  # "PLAN ✅ Complete"
    ]

    for pattern in completion_patterns:
        match = re.search(pattern, handoff_section, re.IGNORECASE)
        if match:
            # Additional validation: ensure it's not in a code block or script reference
            match_start = match.start()
            # Check if match is in code block (```)
            before_match = handoff_section[:match_start]
            code_block_count = before_match.count("```")
            if code_block_count % 2 == 0:  # Not in code block
                return True

    # Check completion percentage (MORE SPECIFIC - only explicit completion)
    percentage_patterns = [
        r"(\d+)/(\d+)\s+achievements?\s+complete",  # "7/7 achievements complete"
        r"(\d+)/(\d+)\s+complete",  # "7/7 complete"
        # REMOVED: r"(\d+)/(\d+)\s+achievements?" - too broad, matches statistics
    ]

    for pattern in percentage_patterns:
        match = re.search(pattern, handoff_section, re.IGNORECASE)
        if match:
            completed = int(match.group(1))
            total = int(match.group(2))
            if completed == total and total > 0:
                return True

    # Count completed achievements in handoff (FIXED - use is_achievement_complete for consistency)
    if achievements:
        completed_count = 0
        for ach in achievements:
            # Use is_achievement_complete() for consistency
            if is_achievement_complete(ach.number, plan_content):
                completed_count += 1

        # If all achievements are marked complete, PLAN is complete
        if completed_count == len(achievements) and len(achievements) > 0:
            return True

    return False


def find_next_achievement_hybrid(
    plan_path: Path, feature_name: str, achievements: List[Achievement], archive_location: str
) -> Optional[Achievement]:
    """
    Find next achievement using multiple methods (hybrid approach).
    
    This is the MAIN achievement finding function - combines multiple detection
    methods with comprehensive validation to find the correct next achievement.
    
    Detection Methods (Priority Order):
    1. Parse PLAN handoff section (MOST AUTHORITATIVE)
       - Reads explicit "Next: Achievement X.Y" statement
       - Validates achievement exists and is not complete
       - Warns if handoff is stale
    
    2. Check PLAN status (FALLBACK for plans without clear "Next")
       - If status is "planning", return first achievement
       - Handles plans just starting
    
    3. Check archive directory (FALLBACK for archived SUBPLANs)
       - Finds first achievement without archived SUBPLAN
       - Skips completed achievements
    
    4. Check root directory (FALLBACK for flat structure)
       - Finds first achievement without SUBPLAN in root
       - Skips completed achievements
    
    Validation:
    - Checks if PLAN is complete FIRST (returns None if done)
    - Skips achievements marked complete
    - Warns if handoff mentions non-existent achievement
    - Warns if handoff mentions complete achievement
    
    Bug Fixes Incorporated:
        - Bug #1: Validates achievement exists before returning
        - Bug #2: Skips completed achievements (fixes duplicate detection)
        - Bug #3: Checks handoff section first (authoritative)
        - Bug #6: Comprehensive validation with warnings
    
    Used by: main() (when --next flag is used)
    Tested: No (Priority 1.3 - needs tests)

    Args:
        plan_path: Path to PLAN file
        feature_name: Feature name (e.g., "API-REVIEW-AND-TESTING")
        achievements: List of achievements from PLAN
        archive_location: Archive directory path

    Returns:
        Achievement object or None if PLAN is complete or no achievement found
    
    Example:
        >>> next_ach = find_next_achievement_hybrid(plan_path, "FEATURE", achievements, "./archive/")
        >>> print(next_ach.number)
        "1.2"
        >>> print(next_ach.title)
        "Comprehensive Inline Documentation"
    """
    # Read PLAN content once
    try:
        with open(plan_path, "r", encoding="utf-8") as f:
            plan_content = f.read()
    except Exception:
        return None

    # STEP 1: Check if PLAN is complete FIRST (fixes Bug #2, #4)
    if is_plan_complete(plan_content, achievements):
        return None  # Indicates PLAN is complete

    # STEP 2: Method 1 - Parse PLAN "What's Next" (MOST AUTHORITATIVE - fixes Bug #6)
    next_num = find_next_achievement_from_plan(plan_content)
    if next_num:
        # Validate achievement exists (fixes Bug #1, #3)
        next_ach = next((a for a in achievements if a.number == next_num), None)
        if next_ach:
            # Additional check: ensure achievement is not complete
            if not is_achievement_complete(next_ach.number, plan_content):
                return next_ach
            # If complete, continue to fallback (shouldn't happen if handoff is correct)
            import warnings

            warnings.warn(
                f"Achievement {next_num} mentioned in handoff but is marked complete. "
                f"Falling back to next incomplete achievement.",
                UserWarning,
            )
        else:
            # Achievement doesn't exist (Bug #1, #3)
            import warnings

            warnings.warn(
                f"Achievement {next_num} mentioned in handoff but not found in PLAN. "
                f"Available achievements: {[a.number for a in achievements]}. "
                f"Falling back to archive/root methods.",
                UserWarning,
            )

    # STEP 3: Check PLAN status (FALLBACK for plans without clear "Next" in handoff)
    status = get_plan_status(plan_content)
    if status == "planning":
        # Return first achievement if PLAN not started AND first achievement not complete
        if achievements and not is_achievement_complete(achievements[0].number, plan_content):
            return achievements[0]
        # If first achievement complete, continue to fallback (stale status scenario)

    # STEP 4: Method 2 - Check archive directory (with completion check)
    next_ach = find_next_achievement_from_archive(
        feature_name, achievements, archive_location, plan_content
    )
    if next_ach:
        return next_ach

    # STEP 5: Method 3 - Check root directory (with completion check)
    return find_next_achievement_from_root(feature_name, achievements, plan_content)


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


def estimate_section_size(lines: List[str], start_idx: int) -> int:
    """
    Estimate lines in achievement section for context budget calculation.
    
    Counts lines from achievement header until next achievement or section.
    Capped at 100 lines to prevent over-estimation.
    
    Used by: parse_plan_file()
    Tested: No (Priority 1.3 - needs tests)
    
    Args:
        lines: All lines from PLAN file
        start_idx: Index of achievement header line
    
    Returns:
        Estimated line count (max 100)
    """
    count = 0
    for i in range(start_idx, len(lines)):
        if i > start_idx and lines[i].startswith("**Achievement"):
            break
        if lines[i].startswith("## "):
            break
        count += 1
    return min(count, 100)  # Cap estimate at 100


def find_archive_location(lines: List[str]) -> str:
    """
    Find archive location from PLAN file.
    
    Searches for "Archive Location" line and extracts path.
    Returns default if not found.
    
    Used by: parse_plan_file()
    Tested: No (Priority 1.3 - needs tests)
    
    Args:
        lines: All lines from PLAN file
    
    Returns:
        Archive location path (e.g., "./feature-archive/")
    """
    for line in lines:
        if "Archive Location" in line and "./" in line:
            match = re.search(r"\./([a-z0-9-]+)/", line)
            if match:
                return f"./{match.group(1)}/"
    return "./feature-archive/"


def calculate_handoff_size(lines: List[str]) -> int:
    """
    Calculate lines in Current Status & Handoff section for context budget.
    
    Used to determine how much context to allocate for handoff section
    when generating prompts.
    
    Used by: parse_plan_file()
    Tested: No (Priority 1.3 - needs tests)
    
    Args:
        lines: All lines from PLAN file
    
    Returns:
        Line count (default 30 if section not found)
    """
    in_section = False
    count = 0
    for line in lines:
        if "Current Status & Handoff" in line:
            in_section = True
        elif in_section and line.startswith("##"):
            break
        elif in_section:
            count += 1
    return count if count > 0 else 30  # Default estimate


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


# PROMPT TEMPLATES

ACHIEVEMENT_EXECUTION_TEMPLATE = """Execute Achievement {achievement_num} in @PLAN_{feature}.md following strict methodology.

═══════════════════════════════════════════════════════════════════════

CONTEXT BOUNDARIES (Read ONLY These):
✅ @PLAN_{feature}.md - Achievement {achievement_num} section only ({achievement_lines} lines)
✅ @PLAN_{feature}.md - "Current Status & Handoff" section ({handoff_lines} lines)

❌ DO NOT READ: Full PLAN ({plan_total_lines} lines), other achievements, archived work

CONTEXT BUDGET: {context_budget} lines maximum

{project_context}═══════════════════════════════════════════════════════════════════════

ACHIEVEMENT {achievement_num}: {achievement_title}

Goal: {achievement_goal}
Estimated: {estimated_hours}

═══════════════════════════════════════════════════════════════════════

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
[Implement the achievement deliverables]

Step 4: Verify Deliverables (MANDATORY)
Run verification:
  ls -1 [each deliverable path]

If any missing: FIX before continuing

Step 5: Complete EXECUTION_TASK
- Update: Iteration Log with "Complete"
- Add: Learning Summary
- Verify: <200 lines (run: wc -l EXECUTION_TASK_*.md)

Step 6: Archive Immediately
- Move: SUBPLAN → {archive_location}subplans/
- Move: EXECUTION_TASK → {archive_location}execution/
- Update: PLAN Subplan Tracking

Step 7: Update PLAN Statistics
- Calculate from EXECUTION_TASK (not imagination)

═══════════════════════════════════════════════════════════════════════

VALIDATION ENFORCEMENT:

{validation_scripts}

═══════════════════════════════════════════════════════════════════════

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

═══════════════════════════════════════════════════════════════════════

EXTERNAL VERIFICATION:

After completing, I will verify:
1. SUBPLAN file exists and complete?
2. EXECUTION_TASK file exists with learnings?
3. All deliverables exist? (filesystem check)
4. Statistics accurate?
5. EXECUTION_TASK <200 lines?

Do not proceed until verification passes.

═══════════════════════════════════════════════════════════════════════

Now beginning Achievement {achievement_num} execution:

Creating SUBPLAN_{feature}_{subplan_num}.md...
"""


def fill_template(template: str, context: dict, validation_scripts: List[str]) -> str:
    """
    Fill prompt template with actual values from context.
    
    Takes the ACHIEVEMENT_EXECUTION_TEMPLATE and replaces placeholders with
    real values (feature name, achievement number, context budget, etc.).
    
    Used by: generate_prompt()
    Tested: No (Priority 1.3 - needs tests)
    
    Args:
        template: Template string with {placeholders}
        context: Dict with values to fill
        validation_scripts: List of validation script names
    
    Returns:
        Filled template string
    """
    
    # Format validation scripts section
    if validation_scripts:
        scripts_text = "After Step 4, these scripts will run:\n"
        for script in validation_scripts:
            scripts_text += f"✓ {script}\n"
        scripts_text += "\nIf issues found: BLOCKS with error + fix prompt"
    else:
        scripts_text = "(Validation scripts being built in this PLAN)"
    
    return template.format(
        feature=context["feature_name"],
        achievement_num=context["achievement_num"],
        achievement_title=context["achievement_title"],
        achievement_goal=context.get("achievement_goal", "See PLAN for details"),
        estimated_hours=context.get("estimated_hours", "See PLAN"),
        achievement_lines=context["achievement_lines"],
        handoff_lines=context["handoff_lines"],
        plan_total_lines=context["plan_total_lines"],
        context_budget=context["context_budget"],
        subplan_num=context["subplan_num"],
        archive_location=context["archive_location"],
        validation_scripts=scripts_text,
        project_context=context.get("project_context", ""),
    )


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


def detect_workflow_state_filesystem(
    plan_path: Path, feature_name: str, achievement_num: str
) -> Dict[str, any]:
    """
    Detect workflow state using filesystem structure (not content parsing).
    
    This is the ROBUST detection method - checks actual files on disk rather
    than parsing markdown text. Introduced in Achievement 1.6 to eliminate
    parsing fragility and improve reliability.
    
    Detection Logic:
    1. Check if SUBPLAN file exists
    2. Check if SUBPLAN is marked complete (header check)
    3. Count EXECUTION_TASK files in filesystem
    4. Count completed EXECUTION_TASKs (status check)
    5. Compare completed vs total to determine state
    
    States Returned:
    - no_subplan: SUBPLAN doesn't exist → create_subplan
    - subplan_complete: SUBPLAN marked complete → next_achievement
    - subplan_no_execution: SUBPLAN exists, no EXECUTION files → create_execution
    - active_execution: Some EXECUTIONs incomplete → continue_execution or create_next_execution
    - subplan_all_executed: All EXECUTIONs complete → synthesize_or_complete
    
    Bug Fixes Incorporated:
        - Bug #6: Counts from filesystem, not SUBPLAN table (more reliable)
        - Bug #7: Finds highest execution number from filesystem
        - Handles multi-execution workflows correctly
        - Handles _V2 and other filename variations
    
    Used by: detect_workflow_state(), main()
    Tested: No (Priority 1.3 - needs tests)

    Args:
        plan_path: Path to PLAN file in nested structure
        feature_name: Feature name (e.g., "METHODOLOGY-HIERARCHY-EVOLUTION")
        achievement_num: Achievement number (e.g., "0.1")

    Returns:
        Dict with keys:
            - state: str (workflow state name)
            - subplan_path: Optional[Path] (path to SUBPLAN)
            - recommendation: str (suggested next action)
            - execution_count: int (total EXECUTION_TASKs planned/found)
            - completed_count: int (completed EXECUTION_TASKs)
    
    Example:
        >>> state = detect_workflow_state_filesystem(plan_path, "FEATURE", "0.1")
        >>> print(state["state"])
        "subplan_no_execution"
        >>> print(state["recommendation"])
        "create_execution"
    """
    # Find SUBPLAN file
    subplan_path = find_subplan_for_achievement(feature_name, achievement_num, plan_path)

    if not subplan_path:
        return {
            "state": "no_subplan",
            "subplan_path": None,
            "recommendation": "create_subplan",
            "execution_count": 0,
            "completed_count": 0,
        }

    # Check if SUBPLAN is marked complete in header
    try:
        with open(subplan_path, "r", encoding="utf-8") as f:
            header = f.read(500)  # Read first 500 chars for status

        # Check for explicit completion in header
        if re.search(r"\*\*Status\*\*:\s*✅\s*Complete", header, re.IGNORECASE):
            return {
                "state": "subplan_complete",
                "subplan_path": subplan_path,
                "recommendation": "next_achievement",
                "execution_count": 0,
                "completed_count": 0,
            }
    except Exception:
        pass

    # Find EXECUTION_TASK files in filesystem
    plan_folder = plan_path.parent
    execution_folder = plan_folder / "execution"

    if not execution_folder.exists():
        # No execution folder = no executions created yet
        return {
            "state": "subplan_no_execution",
            "subplan_path": subplan_path,
            "recommendation": "create_execution",
            "execution_count": 0,
            "completed_count": 0,
        }

    # Find all EXECUTION_TASK files for this achievement
    subplan_num = achievement_num.replace(".", "")
    execution_pattern = f"EXECUTION_TASK_{feature_name}_{subplan_num}_*.md"

    execution_files = list(execution_folder.glob(execution_pattern))

    if not execution_files:
        # SUBPLAN exists but no EXECUTION_TASKs created
        return {
            "state": "subplan_no_execution",
            "subplan_path": subplan_path,
            "recommendation": "create_execution",
            "execution_count": 0,
            "completed_count": 0,
        }

    # Check completion status of each EXECUTION_TASK
    completed_count = 0
    for exec_file in execution_files:
        try:
            with open(exec_file, "r", encoding="utf-8") as f:
                content = f.read()
            # Check for completion marker anywhere in file (not just header)
            # This handles cases where status is updated in iteration logs
            if re.search(r"\*\*Status\*\*:\s*✅\s*Complete", content, re.IGNORECASE):
                completed_count += 1
        except Exception:
            continue

    filesystem_count = len(execution_files)

    # Check SUBPLAN for planned execution count (for multi-execution workflows)
    planned_count = None
    try:
        with open(subplan_path, "r", encoding="utf-8") as f:
            subplan_content = f.read()

        # Look for "## 🔄 Active EXECUTION_TASKs" section
        active_section_match = re.search(
            r"##\s*🔄\s*Active EXECUTION_TASKs.*?(?=\n##\s|\Z)",
            subplan_content,
            re.DOTALL | re.IGNORECASE,
        )

        if active_section_match:
            # Count EXECUTION_TASK entries in the section
            # Look for table rows starting with execution numbers (first column only)
            active_section = active_section_match.group(0)
            # Split into lines and count rows that start with | followed by execution number
            lines = active_section.split("\n")
            execution_rows = []
            for line in lines:
                # Match lines like "| 01_01     | ..." (first column)
                match = re.match(r"^\|\s*(\d+_\d+)\s*\|", line)
                if match:
                    execution_rows.append(match.group(1))
            if execution_rows:
                planned_count = len(execution_rows)
    except Exception:
        pass

    # Use planned count if available, otherwise use filesystem count
    total_count = planned_count if planned_count is not None else filesystem_count

    # Determine state based on completion
    if completed_count < total_count:
        # Some executions still in progress or not yet created
        # Check if there's an incomplete file (in progress) or if next file needs to be created
        has_incomplete_file = filesystem_count > completed_count

        return {
            "state": "active_execution",
            "subplan_path": subplan_path,
            "recommendation": (
                "continue_execution" if has_incomplete_file else "create_next_execution"
            ),
            "execution_count": total_count,
            "completed_count": completed_count,
        }
    elif completed_count == total_count and total_count > 0:
        # All executions complete
        return {
            "state": "subplan_all_executed",
            "subplan_path": subplan_path,
            "recommendation": "synthesize_or_complete",
            "execution_count": total_count,
            "completed_count": completed_count,
        }
    else:
        # Fallback
        return {
            "state": "subplan_no_execution",
            "subplan_path": subplan_path,
            "recommendation": "create_execution",
            "execution_count": 0,
            "completed_count": 0,
        }


def detect_plan_filesystem_conflict(
    plan_path: Path, feature_name: str, achievement_num: str, plan_content: str
) -> Optional[Dict[str, any]]:
    """
    Detect conflicts between PLAN "Current Status & Handoff" and filesystem state.
    
    Critical quality check that catches when PLAN's handoff section becomes stale
    (not updated after achievement completion). This is a RECURRING issue that
    has happened multiple times (Achievement 0.2, 1.1, GRAPHRAG 0.2).
    
    Conflict Types Detected:
    1. plan_outdated_complete: Filesystem shows complete, PLAN says next/in-progress
    2. plan_outdated_synthesis: All EXECUTIONs complete, PLAN not updated
    3. plan_premature_complete: PLAN says complete, but work still active
    
    Detection Strategy:
    - Compare filesystem state (from detect_workflow_state_filesystem)
    - Compare PLAN state (from is_achievement_complete)
    - Identify discrepancies
    - Provide resolution guidance
    
    Bug Fixes Incorporated:
        - Bug #2: Detects PLAN/filesystem drift (Achievement 1.1 conflict)
        - Provides actionable resolution steps
        - Shows both states for comparison
        - Identifies likely cause
    
    Used by: main() (when --trust-plan and --trust-filesystem not set)
    Tested: No (Priority 1.3 - needs tests)
    
    Args:
        plan_path: Path to PLAN file
        feature_name: Feature name
        achievement_num: Achievement number from PLAN's handoff section
        plan_content: Full PLAN content

    Returns:
        Dict with conflict details if found, None if no conflict
        Conflict dict contains:
            - has_conflict: bool (always True if returned)
            - achievement_num: str
            - conflicts: List[Dict] (conflict details)
            - filesystem_state: Dict (from detect_workflow_state_filesystem)
    
    Example:
        >>> conflict = detect_plan_filesystem_conflict(plan_path, "FEATURE", "0.2", content)
        >>> if conflict:
        ...     print(f"Conflict: {conflict['conflicts'][0]['message']}")
        "Achievement 0.2 is marked COMPLETE in filesystem but PLAN says it's next"
    """
    # Get filesystem state for the achievement mentioned in PLAN
    fs_state = detect_workflow_state_filesystem(plan_path, feature_name, achievement_num)

    # Check if achievement is marked complete in PLAN
    is_complete_in_plan = is_achievement_complete(achievement_num, plan_content)

    # Detect conflicts
    conflicts = []

    # Conflict 1: PLAN says "next" but filesystem says "complete"
    if fs_state["state"] == "subplan_complete" and not is_complete_in_plan:
        conflicts.append(
            {
                "type": "plan_outdated_complete",
                "message": f"Achievement {achievement_num} is marked COMPLETE in filesystem but PLAN says it's next",
                "filesystem": "✅ Complete (SUBPLAN marked complete)",
                "plan": "⏳ Next/In Progress",
                "likely_cause": "PLAN was not updated after achievement completion",
            }
        )

    # Conflict 2: PLAN says "next" but filesystem says "all executed" (needs synthesis)
    if fs_state["state"] == "subplan_all_executed" and not is_complete_in_plan:
        exec_count = fs_state.get("execution_count", 0)
        completed = fs_state.get("completed_count", 0)
        conflicts.append(
            {
                "type": "plan_outdated_synthesis",
                "message": f"Achievement {achievement_num} has all executions complete ({completed}/{exec_count}) but PLAN not updated",
                "filesystem": f"✅ All Executions Complete ({completed}/{exec_count})",
                "plan": "⏳ Next/In Progress",
                "likely_cause": "SUBPLAN needs to be marked complete, then PLAN updated",
            }
        )

    # Conflict 3: PLAN says "complete" but filesystem says "active"
    if is_complete_in_plan and fs_state["state"] in ["active_execution", "subplan_no_execution"]:
        conflicts.append(
            {
                "type": "plan_premature_complete",
                "message": f"Achievement {achievement_num} is marked COMPLETE in PLAN but work is still active",
                "filesystem": f"🚀 {fs_state['state']}",
                "plan": "✅ Complete",
                "likely_cause": "Achievement was marked complete prematurely",
            }
        )

    if conflicts:
        return {
            "has_conflict": True,
            "achievement_num": achievement_num,
            "conflicts": conflicts,
            "filesystem_state": fs_state,
        }

    return None


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
        result = detect_workflow_state_filesystem(plan_path, feature_name, achievement_num)
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
    
    Main prompt generation function that orchestrates:
    1. Parse PLAN file
    2. Check if PLAN is complete
    3. Find next achievement
    4. Detect validation scripts
    5. Inject project context
    6. Fill template
    7. Return prompt
    
    Special Cases:
    - PLAN complete → Returns completion message with statistics
    - No achievements found → Returns error message
    - Achievement specified → Uses that achievement
    - No achievement specified → Auto-detects next
    
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
    
    # Parse PLAN
    plan_data = parse_plan_file(plan_path)
    
    # Check if PLAN is complete (before finding next achievement)
    try:
        with open(plan_path, "r", encoding="utf-8") as f:
            plan_content = f.read()

        if is_plan_complete(plan_content, plan_data["achievements"]):
            # PLAN is complete - return completion message
            completion_message = f"""✅ PLAN COMPLETE: {plan_data['feature_name']}

All achievements in this PLAN are complete. The PLAN is ready for the END_POINT protocol.

**Next Steps**:
1. Review the PLAN's "Current Status & Handoff" section to verify completion
2. Follow the IMPLEMENTATION_END_POINT.md protocol to:
   - Archive the PLAN
   - Update ACTIVE_PLANS.md
   - Create completion summary
   - Commit final state

**PLAN File**: {plan_path.name}
**Archive Location**: {plan_data['archive_location']}

**To verify completion**:
  python LLM/scripts/validation/validate_plan_completion.py @{plan_path.name}

**To proceed with END_POINT**:
  See LLM/protocols/IMPLEMENTATION_END_POINT.md for complete workflow.
"""
            return completion_message
    except Exception:
        # If reading fails, continue with normal flow
        pass

    # Find next achievement
    if achievement_num:
        next_ach = next((a for a in plan_data["achievements"] if a.number == achievement_num), None)
    else:
        next_ach = find_next_achievement_hybrid(
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
    
    # Fill template
    prompt = fill_template(ACHIEVEMENT_EXECUTION_TEMPLATE, context, validation_scripts)
    
    return prompt


def copy_to_clipboard_safe(text: str, enabled: bool = True) -> bool:
    """
    Safely copy text to clipboard with error handling.
    
    Achievement 0.1 feature - Makes clipboard the DEFAULT behavior (no flag needed).
    This function is called for ALL output (prompts, errors, conflicts, completion
    messages) to enable seamless copy-paste workflow.
    
    Error Handling:
    - Catches pyperclip exceptions (clipboard unavailable)
    - Falls back gracefully (returns False, caller handles)
    - Never crashes the script
    
    Design Philosophy:
    - Clipboard should "just work" for 95% of users
    - 5% who can't use clipboard get clear message
    - Enabled by default, can be disabled with --no-clipboard
    
    Used by: main(), output_interactive_menu()
    Tested: Yes (13 tests in test_clipboard_and_shortcuts.py)

    Args:
        text: Text to copy to clipboard
        enabled: Whether clipboard is enabled (default True)

    Returns:
        bool: True if copied successfully, False otherwise
    
    Example:
        >>> success = copy_to_clipboard_safe("Hello World")
        >>> if success:
        ...     print("✅ Copied!")
        ✅ Copied!
        
        >>> copy_to_clipboard_safe("Text", enabled=False)
        False
    """
    if not enabled:
        return False

    try:
        import pyperclip

        pyperclip.copy(text)
        return True
    except Exception as e:
        print(f"\n⚠️  Could not copy to clipboard: {e}")
        print("(Output still shown below)")
        return False


def resolve_folder_shortcut(folder_name: str) -> Path:
    """
    Resolve @folder_name to PLAN file in that folder.
    
    Achievement 0.1 feature that enables SHORT commands like:
      python generate_prompt.py @RESTORE --next
    Instead of:
      python generate_prompt.py work-space/plans/RESTORE-EXECUTION-WORKFLOW-AUTOMATION/PLAN_*.md --next
    
    This is the PRIMARY way users interact with the script (80% shorter commands).
    
    Search Strategy:
    1. Search work-space/plans/ for folders matching name (case-insensitive partial match)
    2. Find PLAN_*.md file in matching folder
    3. Error if no match, multiple matches, or no PLAN file
    
    Matching Logic:
    - Case-insensitive: "RESTORE" matches "restore" or "Restore"
    - Partial match: "RESTORE" matches "RESTORE-EXECUTION-WORKFLOW-AUTOMATION"
    - Unique match required: Error if multiple folders match
    
    Error Handling:
    - Shows all available folders if no match
    - Shows all matching folders if ambiguous
    - Clear error messages with actionable guidance
    
    Used by: main() (when args.plan_file starts with @ and has no .md extension)
    Tested: Yes (13 tests in test_clipboard_and_shortcuts.py)

    Args:
        folder_name: Folder name without @ (e.g., "RESTORE", "GRAPHRAG")

    Returns:
        Path to PLAN file in matching folder

    Raises:
        SystemExit: If folder not found, multiple matches, or no PLAN file

    Examples:
        >>> resolve_folder_shortcut("RESTORE")
        Path("work-space/plans/RESTORE-EXECUTION-WORKFLOW-AUTOMATION/PLAN_RESTORE-EXECUTION-WORKFLOW-AUTOMATION.md")
        
        >>> resolve_folder_shortcut("GRAPHRAG")
        Path("work-space/plans/GRAPHRAG-OBSERVABILITY-EXCELLENCE/PLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE.md")
    """
    plans_dir = Path("work-space/plans")

    if not plans_dir.exists():
        print(f"❌ Plans directory not found: {plans_dir}")
        sys.exit(1)

    # Find folders containing the name (case-insensitive partial match)
    matching_folders = []
    for folder in plans_dir.iterdir():
        if folder.is_dir() and folder_name.upper() in folder.name.upper():
            matching_folders.append(folder)

    if not matching_folders:
        print(f"❌ No folder found matching '@{folder_name}'")
        print(f"\n   Searched in: {plans_dir}")
        print(f"   Available folders:")
        for folder in sorted(plans_dir.iterdir()):
            if folder.is_dir():
                print(f"     - {folder.name}")
        sys.exit(1)

    if len(matching_folders) > 1:
        print(f"⚠️  Multiple folders match '@{folder_name}':")
        for f in matching_folders:
            print(f"   - {f.name}")
        print("\n   Use more specific name or full path")
        sys.exit(1)

    # Find PLAN file in folder
    folder = matching_folders[0]
    plan_files = list(folder.glob("PLAN_*.md"))

    if not plan_files:
        print(f"❌ No PLAN file found in {folder.name}")
        print(f"   Expected: PLAN_*.md")
        sys.exit(1)

    if len(plan_files) > 1:
        print(f"⚠️  Multiple PLAN files in {folder.name}:")
        for f in plan_files:
            print(f"   - {f.name}")
        sys.exit(1)

    return plan_files[0]


def extract_plan_statistics(plan_path: Path, feature_name: str) -> dict:
    """
    Extract statistics from completed PLAN for summary message.
    
    Achievement 0.2 feature that provides MEANINGFUL CLOSURE when PLAN completes.
    Instead of just "all complete", shows actual work accomplished with metrics.
    
    Statistics Extracted:
    1. Total achievements (from PLAN markdown)
    2. SUBPLANs created (from subplans/ folder)
    3. EXECUTION_TASKs completed (from execution/ folder)
    4. Total time invested (sum from EXECUTION_TASK files)
    
    Data Sources:
    - Achievements: Parse PLAN markdown (count "**Achievement X.Y**:" patterns)
    - SUBPLANs: Count files in subplans/ folder
    - EXECUTIONs: Count files in execution/ folder
    - Time: Parse EXECUTION_TASK files for "**Time**: X hours" or "**Actual**: X hours"
    
    Graceful Degradation:
    - Returns zeros if extraction fails
    - Returns "N/A" for time if no time data found
    - Never crashes (catches all exceptions)
    
    Used by: main() (when PLAN is complete)
    Tested: Yes (9 tests in test_completion_message.py)

    Args:
        plan_path: Path to PLAN file
        feature_name: Feature name (e.g., "RESTORE-EXECUTION-WORKFLOW-AUTOMATION")

    Returns:
        dict with statistics:
        - total_achievements: int (count of achievements in PLAN)
        - subplan_count: int (SUBPLANs in subplans/ folder)
        - execution_count: int (EXECUTION_TASKs in execution/ folder)
        - total_time: str (sum of time from EXECUTION_TASKs, e.g., "12.5 hours")

    Examples:
        >>> stats = extract_plan_statistics(plan_path, "RESTORE-EXECUTION-WORKFLOW-AUTOMATION")
        >>> print(stats)
        {'total_achievements': 7, 'subplan_count': 7, 'execution_count': 7, 'total_time': '25.5 hours'}
        
        >>> print(f"{stats['execution_count']} EXECUTION_TASKs completed")
        "7 EXECUTION_TASKs completed"
    """
    stats = {"total_achievements": 0, "subplan_count": 0, "execution_count": 0, "total_time": "N/A"}

    try:
        # 1. Count achievements from PLAN
        with open(plan_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Count "**Achievement X.Y**:" patterns
            achievement_pattern = r"\*\*Achievement\s+\d+\.\d+\*\*:"
            stats["total_achievements"] = len(re.findall(achievement_pattern, content))

        # 2. Count SUBPLANs from filesystem
        plan_folder = Path("work-space/plans") / feature_name
        subplans_dir = plan_folder / "subplans"
        if subplans_dir.exists():
            subplan_files = list(subplans_dir.glob("SUBPLAN_*.md"))
            stats["subplan_count"] = len(subplan_files)

        # 3. Count EXECUTION_TASKs from filesystem
        execution_dir = plan_folder / "execution"
        if execution_dir.exists():
            execution_files = list(execution_dir.glob("EXECUTION_TASK_*.md"))
            stats["execution_count"] = len(execution_files)

            # 4. Sum total time from EXECUTION_TASKs
            total_hours = 0.0
            for exec_file in execution_files:
                try:
                    with open(exec_file, "r", encoding="utf-8") as f:
                        exec_content = f.read()
                        # Look for "**Time**: X hours" or "**Actual**: X hours" or "**Time**: X.X hours"
                        time_match = re.search(
                            r"\*\*(?:Time|Actual)\*\*:\s*([\d.]+)\s*hours?",
                            exec_content,
                            re.IGNORECASE,
                        )
                        if time_match:
                            total_hours += float(time_match.group(1))
                except Exception:
                    # Skip files that can't be read or parsed
                    continue

            if total_hours > 0:
                stats["total_time"] = f"{total_hours:.1f} hours"

    except Exception as e:
        # Graceful degradation - return zeros if extraction fails
        print(f"⚠️  Could not extract all statistics: {e}")

    return stats


def output_interactive_menu(prompt: str, workflow_state: str, command: str = None) -> None:
    """
    Interactive menu for handling generated prompt output (POST-GENERATION).
    
    Achievement 0.3 feature - STAGE 2 of two-stage interactive experience.
    This is the "What to do with this prompt?" menu that appears AFTER
    prompt generation, complementing the pre-execution menu.
    
    Two-Stage Interactive Design:
      Stage 1 (Pre): prompt_interactive_menu() - Choose workflow
      Stage 2 (Post): output_interactive_menu() - Handle output ← YOU ARE HERE
    
    Menu Options (dynamic based on content):
    - If commands detected: Offers to copy individual commands or full message
    - If no commands: Original behavior (copy full prompt)
    - Smart defaults: Enter = copy most useful content
    
    Smart Defaults:
    - Enter key = copy (most common action, 95% of users)
    - Execute option only shown if command available (context-aware)
    - Help adapts to workflow state
    
    Error Handling:
    - Invalid choice loops back to menu
    - Clipboard failure falls back to display
    - File save errors caught and reported
    
    Used by: main() (when args.interactive is True)
    Tested: Yes (18 tests in test_interactive_output_menu.py)

    Args:
        prompt: Generated prompt text
        workflow_state: Current workflow state (for context)
        command: Recommended command to execute (optional)

    Returns:
        None (exits after handling user choice)
    
    Example:
        >>> output_interactive_menu(prompt, "create_execution", "python generate_execution_prompt.py ...")
        # Shows menu with command-specific options
        
        >>> output_interactive_menu(prompt, "next_achievement", None)
        # Shows standard menu
    """
    # Extract recommended commands from prompt
    command_pattern = r'\*\*Recommended Command\*\*:\s*\n\s*(.+?)(?:\n\n|\nOr use|$)'
    commands = re.findall(command_pattern, prompt, re.DOTALL)
    
    # Also check for "Or use ... directly:" pattern
    alt_command_pattern = r'Or use .+ directly:\s*\n\s*(.+?)(?:\n\n|$)'
    alt_commands = re.findall(alt_command_pattern, prompt, re.DOTALL)
    
    # Clean commands (remove leading spaces, take first line if multiline)
    cleaned_commands = []
    for cmd in commands + alt_commands:
        lines = [line.strip() for line in cmd.split('\n') if line.strip()]
        if lines:
            cleaned_commands.append(lines[0])
    
    print("\n" + "=" * 70)
    print("🎯 What would you like to do with this prompt?")
    print("=" * 70)
    
    # Build menu based on whether commands were detected
    if cleaned_commands:
        if len(cleaned_commands) == 1:
            print("\n1. Copy command to clipboard (default - press Enter)")
            print(f"   → {cleaned_commands[0][:65]}...")
            print("2. Copy full message")
            print("3. View full prompt")
            print("4. Save to file")
            if command:
                print("5. Execute recommended command")
                print("6. Get help")
                print("7. Exit")
                max_choice = 7
            else:
                print("5. Get help")
                print("6. Exit")
                max_choice = 6
        else:  # Multiple commands
            print("\n1. Copy first command to clipboard (default - press Enter)")
            print(f"   → {cleaned_commands[0][:65]}...")
            print("2. Copy second command to clipboard")
            print(f"   → {cleaned_commands[1][:65]}...")
            print("3. Copy full message")
            print("4. View full prompt")
            print("5. Save to file")
            if command:
                print("6. Execute recommended command")
                print("7. Get help")
                print("8. Exit")
                max_choice = 8
            else:
                print("6. Get help")
                print("7. Exit")
                max_choice = 7
    else:
        # No commands detected - original behavior
        print("\n1. Copy to clipboard (default - press Enter)")
        print("2. View full prompt")
        print("3. Save to file")
        if command:
            print("4. Execute recommended command")
            print("5. Get help")
            print("6. Exit")
            max_choice = 6
        else:
            print("4. Get help")
            print("5. Exit")
            max_choice = 5

    choice = input(f"\nChoose [1-{max_choice}] or press Enter for default: ").strip() or "1"

    # Handle choices based on menu structure
    if cleaned_commands:
        if len(cleaned_commands) == 1:
            # Single command menu
            if choice == "1":
                # Copy first command only
                if copy_to_clipboard_safe(cleaned_commands[0], enabled=True):
                    print("✅ Command copied to clipboard!")
                else:
                    print("⚠️  Clipboard not available, displaying command:")
                    print(f"\n{cleaned_commands[0]}")
            elif choice == "2":
                # Copy full message
                if copy_to_clipboard_safe(prompt, enabled=True):
                    print("✅ Full message copied to clipboard!")
                else:
                    print("⚠️  Clipboard not available, displaying prompt:")
                    print("\n" + prompt)
            elif choice == "3":
                # View full prompt
                print("\n" + "=" * 70)
                print(prompt)
                print("=" * 70)
                next_action = input("\nCopy command or full message? (c/f/n): ").strip().lower()
                if next_action == "c":
                    if copy_to_clipboard_safe(cleaned_commands[0], enabled=True):
                        print("✅ Command copied to clipboard!")
                elif next_action == "f":
                    if copy_to_clipboard_safe(prompt, enabled=True):
                        print("✅ Full message copied to clipboard!")
            elif choice == "4":
                # Save to file
                filename = input("Enter filename (e.g., prompt.txt): ").strip()
                if filename:
                    try:
                        with open(filename, "w") as f:
                            f.write(prompt)
                        print(f"✅ Saved to {filename}")
                    except Exception as e:
                        print(f"❌ Error saving file: {e}")
                else:
                    print("❌ No filename provided")
            elif choice == "5":
                if command:
                    # Execute command
                    print(f"\n🚀 Executing: {command}")
                    import subprocess
                    result = subprocess.run(command, shell=True)
                    if result.returncode == 0:
                        print("✅ Command completed successfully")
                    else:
                        print(f"❌ Command failed with exit code {result.returncode}")
                else:
                    # Get help
                    print("\n💡 Help:")
                    print(f"   Workflow State: {workflow_state}")
                    print(f"   Recommended Command: {cleaned_commands[0]}")
                    print("   • Copy the command and run it in your terminal")
                    print("   • Or copy the full message to your LLM chat")
            elif choice == "6":
                if command:
                    # Get help
                    print("\n💡 Help:")
                    print(f"   Workflow State: {workflow_state}")
                    print(f"   Recommended Command: {cleaned_commands[0]}")
                    print("   • Copy the command and run it in your terminal")
                    print("   • Or copy the full message to your LLM chat")
                else:
                    # Exit
                    print("👋 Goodbye!")
                    sys.exit(0)
            elif choice == "7" and command:
                # Exit
                print("👋 Goodbye!")
                sys.exit(0)
            else:
                print(f"❌ Invalid choice. Please enter 1-{max_choice}")
                return output_interactive_menu(prompt, workflow_state, command)
        else:
            # Multiple commands menu
            if choice == "1":
                # Copy first command
                if copy_to_clipboard_safe(cleaned_commands[0], enabled=True):
                    print("✅ First command copied to clipboard!")
                else:
                    print("⚠️  Clipboard not available, displaying command:")
                    print(f"\n{cleaned_commands[0]}")
            elif choice == "2":
                # Copy second command
                if copy_to_clipboard_safe(cleaned_commands[1], enabled=True):
                    print("✅ Second command copied to clipboard!")
                else:
                    print("⚠️  Clipboard not available, displaying command:")
                    print(f"\n{cleaned_commands[1]}")
            elif choice == "3":
                # Copy full message
                if copy_to_clipboard_safe(prompt, enabled=True):
                    print("✅ Full message copied to clipboard!")
                else:
                    print("⚠️  Clipboard not available, displaying prompt:")
                    print("\n" + prompt)
            elif choice == "4":
                # View full prompt
                print("\n" + "=" * 70)
                print(prompt)
                print("=" * 70)
                next_action = input("\nCopy command 1, 2, or full message? (1/2/f/n): ").strip().lower()
                if next_action == "1":
                    if copy_to_clipboard_safe(cleaned_commands[0], enabled=True):
                        print("✅ First command copied to clipboard!")
                elif next_action == "2":
                    if copy_to_clipboard_safe(cleaned_commands[1], enabled=True):
                        print("✅ Second command copied to clipboard!")
                elif next_action == "f":
                    if copy_to_clipboard_safe(prompt, enabled=True):
                        print("✅ Full message copied to clipboard!")
            elif choice == "5":
                # Save to file
                filename = input("Enter filename (e.g., prompt.txt): ").strip()
                if filename:
                    try:
                        with open(filename, "w") as f:
                            f.write(prompt)
                        print(f"✅ Saved to {filename}")
                    except Exception as e:
                        print(f"❌ Error saving file: {e}")
                else:
                    print("❌ No filename provided")
            elif choice == "6":
                if command:
                    # Execute command
                    print(f"\n🚀 Executing: {command}")
                    import subprocess
                    result = subprocess.run(command, shell=True)
                    if result.returncode == 0:
                        print("✅ Command completed successfully")
                    else:
                        print(f"❌ Command failed with exit code {result.returncode}")
                else:
                    # Get help
                    print("\n💡 Help:")
                    print(f"   Workflow State: {workflow_state}")
                    print(f"   Commands available:")
                    for i, cmd in enumerate(cleaned_commands, 1):
                        print(f"     {i}. {cmd}")
                    print("   • Copy a command and run it in your terminal")
                    print("   • Or copy the full message to your LLM chat")
            elif choice == "7":
                if command:
                    # Get help
                    print("\n💡 Help:")
                    print(f"   Workflow State: {workflow_state}")
                    print(f"   Commands available:")
                    for i, cmd in enumerate(cleaned_commands, 1):
                        print(f"     {i}. {cmd}")
                    print("   • Copy a command and run it in your terminal")
                    print("   • Or copy the full message to your LLM chat")
                else:
                    # Exit
                    print("👋 Goodbye!")
                    sys.exit(0)
            elif choice == "8" and command:
                # Exit
                print("👋 Goodbye!")
                sys.exit(0)
            else:
                print(f"❌ Invalid choice. Please enter 1-{max_choice}")
                return output_interactive_menu(prompt, workflow_state, command)
    else:
        # No commands detected - original behavior
        if choice == "1":
            # Copy to clipboard
            if copy_to_clipboard_safe(prompt, enabled=True):
                print("✅ Copied to clipboard!")
            else:
                print("⚠️  Clipboard not available, displaying prompt:")
                print("\n" + prompt)
        elif choice == "2":
            # View full prompt
            print("\n" + "=" * 70)
            print(prompt)
            print("=" * 70)
            next_action = input("\nCopy to clipboard? (Y/n): ").strip().lower()
            if next_action != "n":
                if copy_to_clipboard_safe(prompt, enabled=True):
                    print("✅ Copied to clipboard!")
        elif choice == "3":
            # Save to file
            filename = input("Enter filename (e.g., prompt.txt): ").strip()
            if filename:
                try:
                    with open(filename, "w") as f:
                        f.write(prompt)
                    print(f"✅ Saved to {filename}")
                except Exception as e:
                    print(f"❌ Error saving file: {e}")
            else:
                print("❌ No filename provided")
        elif choice == "4":
            if command:
                # Execute command
                print(f"\n🚀 Executing: {command}")
                import subprocess
                result = subprocess.run(command, shell=True)
                if result.returncode == 0:
                    print("✅ Command completed successfully")
                else:
                    print(f"❌ Command failed with exit code {result.returncode}")
            else:
                # Get help (no command available)
                print("\n💡 Help:")
                print(f"   Workflow State: {workflow_state}")
                print("   • Copy the prompt and paste into your LLM chat")
                print("   • Follow the instructions in the prompt")
                print("   • Use --next flag to auto-detect next step")
        elif choice == "5":
            if command:
                # Get help (command available)
                print("\n💡 Help:")
                print(f"   Workflow State: {workflow_state}")
                print(f"   Recommended Command: {command}")
                print("   • Copy the prompt and paste into your LLM chat")
                print("   • Or execute the recommended command")
                print("   • Use --next flag to auto-detect next step")
            else:
                # Exit
                print("👋 Goodbye!")
                sys.exit(0)
        elif choice == "6" and command:
            # Exit
            print("👋 Goodbye!")
            sys.exit(0)
        else:
            print(f"❌ Invalid choice. Please enter 1-{max_choice}")
            return output_interactive_menu(prompt, workflow_state, command)


def prompt_interactive_menu():
    """
    Interactive menu for workflow selection (PRE-EXECUTION).
    
    Achievement 0.3 feature - STAGE 1 of two-stage interactive experience.
    This is the "What would you like to do?" menu that appears BEFORE
    prompt generation, allowing users to choose their workflow.
    
    Two-Stage Interactive Design:
      Stage 1 (Pre): prompt_interactive_menu() - Choose workflow ← YOU ARE HERE
      Stage 2 (Post): output_interactive_menu() - Handle output
    
    Menu Options:
    1. Generate next achievement (auto-detect) - DEFAULT
    2. Generate specific achievement (user chooses)
    3. View all available achievements
    4. Copy prompt to clipboard
    5. Exit
    
    Workflow Context Detection (Enhancement):
    - Detects latest SUBPLAN
    - Counts EXECUTION_TASK files
    - Shows helpful context before menu
    - Provides specific recommendations
    
    Context Display:
    - "SUBPLAN detected, no EXECUTION" → Suggest option 1
    - "EXECUTION_TASKs found: 8 files" → Tip for next step
    
    Flag Preservation:
    - Adds --interactive to sys.argv modifications
    - Ensures post-generation menu is triggered
    - Maintains interactive mode through workflow
    
    Used by: main() (when args.interactive is True, before arg parsing)
    Tested: Partially (integration tests in test_interactive_output_menu.py)
    
    Returns:
        None (modifies sys.argv and returns to main for re-parsing)
    
    Example:
        >>> # User runs: python generate_prompt.py @RESTORE --interactive
        >>> prompt_interactive_menu()
        # Shows menu, user chooses option 1
        # sys.argv becomes: ['generate_prompt.py', '@RESTORE', '--next', '--interactive']
        # Returns to main() for re-parsing
    """
    # Quick workflow detection to show context
    workflow_context = None
    if len(sys.argv) > 1:
        try:
            plan_file = sys.argv[1]
            # Quick path resolution
            if plan_file.startswith("@"):
                shorthand = plan_file[1:]
                if "/" not in shorthand and not shorthand.endswith(".md"):
                    # @folder format
                    from pathlib import Path
                    plans_dir = Path("work-space/plans")
                    for folder in plans_dir.iterdir():
                        if folder.is_dir() and shorthand.upper() in folder.name.upper():
                            plan_files = list(folder.glob("PLAN_*.md"))
                            if plan_files:
                                plan_path = plan_files[0]
                                feature_name = folder.name
                                
                                # Quick workflow detection
                                subplans_dir = folder / "subplans"
                                execution_dir = folder / "execution"
                                
                                if subplans_dir.exists():
                                    subplan_files = sorted(list(subplans_dir.glob("SUBPLAN_*.md")))
                                    if subplan_files:
                                        latest_subplan = subplan_files[-1]
                                        
                                        # Check if EXECUTION exists for this SUBPLAN
                                        if execution_dir.exists():
                                            # Extract subplan number (e.g., "02" from "SUBPLAN_FEATURE_02.md")
                                            import re
                                            match = re.search(r'_(\d+)\.md$', latest_subplan.name)
                                            if match:
                                                subplan_num = match.group(1)
                                                # Look for any EXECUTION file starting with the pattern
                                                exec_pattern = f"EXECUTION_TASK_{feature_name}_{subplan_num}_*"
                                                exec_files = [f for f in execution_dir.iterdir() 
                                                             if f.name.startswith(f"EXECUTION_TASK_{feature_name}_{subplan_num}_")]
                                                
                                                if not exec_files:
                                                    # SUBPLAN exists but no EXECUTION
                                                    workflow_context = {
                                                        "type": "needs_execution",
                                                        "subplan": latest_subplan.name,
                                                        "subplan_num": subplan_num,
                                                        "feature": feature_name
                                                    }
                                                else:
                                                    # EXECUTION exists - show helpful context
                                                    workflow_context = {
                                                        "type": "has_execution",
                                                        "subplan": latest_subplan.name,
                                                        "subplan_num": subplan_num,
                                                        "feature": feature_name,
                                                        "exec_count": len(exec_files)
                                                    }
                                break
        except Exception:
            # If detection fails, continue without context
            pass
    
    print("\n" + "=" * 70)
    print("🎯 What would you like to do?")
    print("=" * 70)
    
    # Show workflow context if detected
    if workflow_context:
        if workflow_context["type"] == "needs_execution":
            print(f"\n💡 WORKFLOW CONTEXT:")
            print(f"   SUBPLAN detected: {workflow_context['subplan']}")
            print(f"   Status: No EXECUTION_TASK found")
            print(f"   Suggestion: Create EXECUTION for achievement {workflow_context['subplan_num']}")
            print(f"\n   Recommended: Choose option 1 (auto-detect) or option 2 (specific achievement)")
            print()
        elif workflow_context["type"] == "has_execution":
            print(f"\n💡 WORKFLOW CONTEXT:")
            print(f"   Latest SUBPLAN: {workflow_context['subplan']}")
            print(f"   EXECUTION_TASKs found: {workflow_context['exec_count']} file(s)")
            print(f"   Status: Work in progress or complete")
            print(f"\n   Tip: Use option 1 to auto-detect next step, or option 2 for specific achievement")
            print()
    
    print("\n1. Generate prompt for next achievement (auto-detect)")
    print("2. Generate prompt for specific achievement")
    print("3. View all available achievements")
    print("4. Copy prompt to clipboard")
    print("5. Exit\n")

    choice = input("Enter choice (1-5, default 1): ").strip() or "1"

    if choice == "1":
        # Next achievement (default)
        if len(sys.argv) > 1:
            plan_file = sys.argv[1]
            sys.argv = [sys.argv[0], plan_file, "--next", "--interactive"]
        else:
            print("❌ Error: PLAN file required")
            sys.exit(1)
    elif choice == "2":
        # Specific achievement
        if len(sys.argv) > 1:
            plan_file = sys.argv[1]
            achievement = input("Enter achievement number (e.g., 1.1): ").strip()
            if achievement:
                sys.argv = [sys.argv[0], plan_file, "--achievement", achievement, "--interactive"]
            else:
                print("❌ Invalid achievement number")
                sys.exit(1)
        else:
            print("❌ Error: PLAN file required")
            sys.exit(1)
    elif choice == "3":
        # View achievements
        print("\n📋 Available achievements vary by PLAN")
        print("Use option 1 or 2 to generate prompts for specific achievements")
        sys.exit(0)
    elif choice == "4":
        # Copy to clipboard
        if len(sys.argv) > 1:
            plan_file = sys.argv[1]
            sys.argv = [sys.argv[0], plan_file, "--next", "--interactive"]
        else:
            print("❌ Error: PLAN file required")
            sys.exit(1)
    elif choice == "5":
        # Exit
        sys.exit(0)
    else:
        print("❌ Invalid choice. Please try again.")
        return prompt_interactive_menu()


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

    args = parser.parse_args()

    # Show interactive menu if requested
    if args.interactive:
        prompt_interactive_menu()
        # Re-parse after menu has modified sys.argv
    args = parser.parse_args()
    
    try:
        # Resolve PLAN path (supports @folder, @PLAN_NAME.md, or full path)
        if args.plan_file.startswith("@"):
            # Check if it's @folder format (no .md extension, no /)
            shorthand = args.plan_file[1:]  # Remove @
            if "/" not in shorthand and not shorthand.endswith(".md"):
                # @folder format (NEW) - find PLAN in folder
                plan_path = resolve_folder_shortcut(shorthand)
            else:
                # @PLAN_NAME.md format (existing) - search for file
                plan_path = Path(shorthand)

                # If not found, check work-space/plans/ recursively
                if not plan_path.exists():
                    # Try flat structure first
                    workspace_path = Path("work-space/plans") / plan_path.name
                    if workspace_path.exists():
                        plan_path = workspace_path
                    else:
                        # Try nested structure - search all subdirectories
                        plans_dir = Path("work-space/plans")
                        if plans_dir.exists():
                            found = False
                            for plan_file in plans_dir.rglob(plan_path.name):
                                if plan_file.is_file():
                                    plan_path = plan_file
                                    found = True
                                    break

                            if not found:
                                # File not found - show all checked locations
                                print(
                                    f"❌ Error: File not found: {args.plan_file.replace('@', '')}"
                                )
                                print(f"   Checked: {plan_path}")
                                print(f"   Checked: {workspace_path}")
                                print(f"   Checked: work-space/plans/**/")
                                sys.exit(1)
                        else:
                            # File not found - show all checked locations
                            print(f"❌ Error: File not found: {args.plan_file.replace('@', '')}")
                            print(f"   Checked: {plan_path}")
                            print(f"   Checked: {workspace_path}")
                            sys.exit(1)
        else:
            # Not @ shorthand - treat as regular path
            plan_path = Path(args.plan_file)
            if not plan_path.exists():
                # Absolute path not found
                print(f"❌ Error: File not found: {plan_path}")
                sys.exit(1)
        
        # Parse PLAN to get feature name and achievement
        plan_data = parse_plan_file(plan_path)
        feature_name = plan_data["feature_name"]

        # Read PLAN content once
        with open(plan_path, "r", encoding="utf-8") as f:
            plan_content = f.read()

        # Determine achievement number
        if args.achievement:
            achievement_num = args.achievement
        elif args.next:
            # Find next achievement based on trust mode
            if args.trust_filesystem:
                # Trust filesystem: Find first achievement that's not complete in filesystem
                print(
                    "🔍 --trust-filesystem: Finding next achievement based on filesystem state..."
                )
                next_ach = None
                for ach in plan_data["achievements"]:
                    fs_state = detect_workflow_state_filesystem(plan_path, feature_name, ach.number)
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
                next_ach = find_next_achievement_hybrid(
                    plan_path,
                    feature_name,
                    plan_data["achievements"],
                    plan_data["archive_location"],
                )
                if not next_ach:
                    # PLAN is complete - extract statistics and provide helpful next steps
                    stats = extract_plan_statistics(plan_path, feature_name)

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
                    if copy_to_clipboard_safe(completion_message, clipboard_enabled):
                        print("✅ Completion message copied to clipboard!")

                    sys.exit(0)
                achievement_num = next_ach.number

            # Check for PLAN/filesystem conflicts (unless user explicitly trusts one source)
            if not args.trust_plan and not args.trust_filesystem:
                conflict = detect_plan_filesystem_conflict(
                    plan_path, feature_name, achievement_num, plan_content
                )
            else:
                conflict = None
                if args.trust_plan:
                    print(
                        "⚠️  --trust-plan: Skipping conflict detection, trusting PLAN as source of truth"
                    )

            if conflict:
                # Build conflict message
                conflict_message = f"""
╔════════════════════════════════════════════════════════════════════════╗
║                                                                        ║
║  ⚠️  PLAN/FILESYSTEM CONFLICT DETECTED                                 ║
║                                                                        ║
╚════════════════════════════════════════════════════════════════════════╝

🔍 CONFLICT SUMMARY
═════════════════════════════════════════════════════════════════════════

The PLAN's "Current Status & Handoff" section does not match the filesystem state.

Achievement: {conflict['achievement_num']}
Conflicts Found: {len(conflict['conflicts'])}

"""
                # Add conflict details
                for i, c in enumerate(conflict["conflicts"], 1):
                    conflict_message += f"""Conflict {i}: {c['type']}
─────────────────────────────────────────────────────────────────────────
{c['message']}

Filesystem State: {c['filesystem']}
PLAN State: {c['plan']}

Likely Cause: {c['likely_cause']}
"""

                fs_state = conflict["filesystem_state"]
                conflict_message += f"""
═════════════════════════════════════════════════════════════════════════

📊 DETAILED STATE INFORMATION
═════════════════════════════════════════════════════════════════════════

Filesystem Detection:
  • State: {fs_state['state']}
  • Recommendation: {fs_state['recommendation']}
  • SUBPLAN: {fs_state.get('subplan_path', 'Not found')}
  • Executions: {fs_state.get('execution_count', 0)} total, {fs_state.get('completed_count', 0)} complete

PLAN Says:
  • Next Achievement: {achievement_num}
  • Check "Current Status & Handoff" section in PLAN

═════════════════════════════════════════════════════════════════════════

🔧 HOW TO RESOLVE
═════════════════════════════════════════════════════════════════════════

Step 1: Verify Filesystem State
  • Check SUBPLAN file status header
  • Check EXECUTION_TASK file(s) status headers
  • Confirm which state is correct

Step 2: Update the Incorrect Source

  Option A: Filesystem is correct, PLAN is outdated
    1. Update SUBPLAN status if needed (mark ✅ Complete)
    2. Update PLAN "Current Status & Handoff" section:
       - Mark achievement ✅ Complete in progress list
       - Update "Next:" to point to next achievement
    3. Run this command again

  Option B: PLAN is correct, filesystem is wrong
    1. Check why files are in unexpected state
    2. Complete or fix the work as needed
    3. Ensure SUBPLAN and EXECUTION_TASK statuses are accurate

Step 3: Verify Resolution
  Run this command again to confirm conflict is resolved:
    python generate_prompt @{feature_name} --next

═════════════════════════════════════════════════════════════════════════

💡 PREVENTION TIP
═════════════════════════════════════════════════════════════════════════

Always update the PLAN's "Current Status & Handoff" section when:
  • Completing an achievement
  • Moving to the next achievement
  • Changing workflow state

The PLAN is the "source of truth" - keep it synchronized with work!

═════════════════════════════════════════════════════════════════════════

❌ Cannot proceed until conflict is resolved.

═════════════════════════════════════════════════════════════════════════
"""
                # Display conflict message
                print(conflict_message)

                # Copy conflict message to clipboard (default behavior)
                clipboard_enabled = not args.no_clipboard
                if copy_to_clipboard_safe(conflict_message, clipboard_enabled):
                    print("\n✅ Conflict message copied to clipboard!")

                sys.exit(1)
        else:
            print("❌ Error: Use --next or --achievement N.N")
            parser.print_help()
            sys.exit(1)
        
        # Handle workflow-specific flags
        if args.subplan_only:
            # Generate SUBPLAN prompt
            import subprocess

            result = subprocess.run(
                [
                    sys.executable,
                    "LLM/scripts/generation/generate_subplan_prompt.py",
                    "create",
                    f"@{plan_path}",
                    "--achievement",
                    achievement_num,
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
            output_interactive_menu(prompt, state_name, recommended_command)
        else:
            # Non-interactive: print and copy to clipboard
            print(prompt)

            # Clipboard is default (use --no-clipboard to disable)
            clipboard_enabled = not args.no_clipboard
            if copy_to_clipboard_safe(prompt, clipboard_enabled):
                print("\n✅ Copied to clipboard!")

        sys.exit(0)
    
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
