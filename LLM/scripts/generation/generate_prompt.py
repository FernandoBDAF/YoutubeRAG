#!/usr/bin/env python3
"""
LLM Prompt Generator - Automated high-quality prompt generation

Generates ideal prompts for LLM development methodology with:
- Context boundaries (read only what's needed)
- Required steps (SUBPLAN, EXECUTION_TASK, etc.)
- Validation enforcement (scripts that will run)
- Size limits (200-line EXECUTION_TASK)
- DO NOTs (anti-patterns)
- External verification

Usage:
    python LLM/scripts/generate_prompt.py @PLAN_FEATURE.md --next
    python LLM/scripts/generate_prompt.py @PLAN_FEATURE.md --achievement 1.1
    python LLM/scripts/generate_prompt.py @PLAN_FEATURE.md --next --clipboard
"""

import argparse
import re
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional


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
    """Extract structured data from PLAN file."""
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

    Args:
        plan_content: Full PLAN file content as string

    Returns:
        Section content as string, or None if section not found
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
    Find next achievement from PLAN's 'Current Status & Handoff' section or full file.

    Prioritizes the "Current Status & Handoff" section (authoritative source),
    then falls back to full file search with reordered patterns.
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
    feature_name: str, achievements: List[Achievement], 
    archive_location: str, plan_content: str
) -> Optional[Achievement]:
    """
    Find first achievement without archived SUBPLAN (skip completed).
    
    FIXED: Skips achievements marked complete in PLAN.
    
    Args:
        feature_name: Feature name
        achievements: List of achievements
        archive_location: Archive directory path
        plan_content: PLAN file content (for completion checking)
        
    Returns:
        First incomplete achievement without archived SUBPLAN, or None
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
    Find first achievement without SUBPLAN in root (skip completed).
    
    FIXED: Skips achievements marked complete in PLAN.
    
    Args:
        feature_name: Feature name
        achievements: List of achievements
        plan_content: PLAN file content (for completion checking)
        
    Returns:
        First incomplete achievement without SUBPLAN, or None
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
    
    Priority 1: Check handoff section (most authoritative)
    Priority 2: Check full plan content if handoff doesn't have info
    
    Args:
        ach_num: Achievement number (e.g., "1.1")
        plan_content: Full PLAN file content
        
    Returns:
        True if achievement is marked complete, False otherwise
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
    Extract PLAN status from content.
    
    Args:
        plan_content: Full PLAN file content
        
    Returns:
        Status string (e.g., "planning", "in progress", "complete") or "unknown"
    """
    # Check handoff section first
    handoff_section = extract_handoff_section(plan_content)
    if handoff_section:
        status_match = re.search(r"\*\*Status\*\*[:\s]+(\w+(?:\s+\w+)?)", handoff_section, re.IGNORECASE)
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
    
    FIXED: More specific patterns to avoid false positives.
    
    Args:
        plan_content: Full PLAN file content as string
        achievements: List of achievements from PLAN

    Returns:
        True if all achievements are complete, False otherwise
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
    
    COMPREHENSIVE FIX: Addresses all bugs with full validation.
    
    Args:
        plan_path: Path to PLAN file
        feature_name: Feature name (e.g., "API-REVIEW-AND-TESTING")
        achievements: List of achievements from PLAN
        archive_location: Archive directory path
        
    Returns:
        Achievement object or None if PLAN is complete or no achievement found
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
                UserWarning
            )
        else:
            # Achievement doesn't exist (Bug #1, #3)
            import warnings
            warnings.warn(
                f"Achievement {next_num} mentioned in handoff but not found in PLAN. "
                f"Available achievements: {[a.number for a in achievements]}. "
                f"Falling back to archive/root methods.",
                UserWarning
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
    """Detect which validation scripts exist (check new domain structure)."""
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
    """Estimate lines in achievement section."""
    count = 0
    for i in range(start_idx, len(lines)):
        if i > start_idx and lines[i].startswith("**Achievement"):
            break
        if lines[i].startswith("## "):
            break
        count += 1
    return min(count, 100)  # Cap estimate at 100


def find_archive_location(lines: List[str]) -> str:
    """Find archive location from PLAN."""
    for line in lines:
        if "Archive Location" in line and "./" in line:
            match = re.search(r"\./([a-z0-9-]+)/", line)
            if match:
                return f"./{match.group(1)}/"
    return "./feature-archive/"


def calculate_handoff_size(lines: List[str]) -> int:
    """Calculate lines in Current Status & Handoff section."""
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

    Args:
        include_context: Whether to include project context (default: True)

    Returns:
        Formatted project context section, or empty string if disabled or file not found
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
    """Fill template with actual values."""

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


def generate_prompt(
    plan_path: Path, achievement_num: Optional[str] = None, include_context: bool = True
) -> str:
    """Generate prompt for PLAN.

    Args:
        plan_path: Path to PLAN file
        achievement_num: Optional specific achievement number
        include_context: Whether to include project context (default: True)

    Returns:
        Generated prompt string
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


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate high-quality LLM prompts for methodology execution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python LLM/scripts/generate_prompt.py @PLAN_FEATURE.md --next
  python LLM/scripts/generate_prompt.py @PLAN_FEATURE.md --achievement 1.1
  python LLM/scripts/generate_prompt.py @PLAN_FEATURE.md --next --clipboard

Exit Codes:
  0 = Success
  1 = Error (file not found, parsing failed, etc.)
        """,
    )

    parser.add_argument("plan_file", help="PLAN file (e.g., @PLAN_FEATURE.md or PLAN_FEATURE.md)")

    parser.add_argument(
        "--next", action="store_true", help="Generate prompt for next achievement (auto-detect)"
    )

    parser.add_argument("--achievement", help="Specific achievement number (e.g., 1.1)")

    parser.add_argument("--clipboard", action="store_true", help="Copy prompt to clipboard")

    parser.add_argument(
        "--no-project-context",
        action="store_true",
        help="Disable project context injection (for testing)",
    )

    args = parser.parse_args()

    try:
        # Clean file path
        plan_path = Path(args.plan_file.replace("@", ""))

        if not plan_path.exists():
            print(f"❌ Error: File not found: {plan_path}")
            sys.exit(1)

        # Generate prompt
        if args.next or args.achievement:
            include_context = not args.no_project_context
            prompt = generate_prompt(plan_path, args.achievement, include_context)
        else:
            print("❌ Error: Use --next or --achievement N.N")
            parser.print_help()
            sys.exit(1)

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
