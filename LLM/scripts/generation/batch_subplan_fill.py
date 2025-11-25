"""
Batch SUBPLAN Fill Prompt Generator

Generates streamlined prompts for filling multiple placeholder SUBPLANs created
by batch operations. Designed for efficiency - one LLM call fills all placeholders.

Usage:
    from LLM.scripts.generation.batch_subplan_fill import generate_batch_fill_prompt

    # Generate prompt for filling placeholders
    prompt = generate_batch_fill_prompt(plan_path, achievement_ids)
    print(prompt)

Created: 2025-11-14
Context: Post batch-creation workflow enhancement
"""

from pathlib import Path
from typing import List, Dict, Optional
import re

from LLM.scripts.generation.plan_parser import PlanParser


def detect_placeholder_subplans(plan_path: Path) -> List[Dict]:
    """
    Detect SUBPLANs that are placeholders (contain [TO BE FILLED] markers).

    Args:
        plan_path: Path to PLAN directory

    Returns:
        List of dicts with achievement_id and subplan_path for placeholders

    Example:
        >>> placeholders = detect_placeholder_subplans(Path("work-space/plans/MY-PLAN"))
        >>> print(f"Found {len(placeholders)} placeholder SUBPLANs")
    """
    if plan_path.is_file():
        plan_dir = plan_path.parent
    else:
        plan_dir = plan_path

    subplans_dir = plan_dir / "subplans"
    if not subplans_dir.exists():
        return []

    placeholders = []

    # Find all SUBPLAN files
    subplan_files = list(subplans_dir.glob("SUBPLAN_*.md"))

    for subplan_file in subplan_files:
        # Read file and check for placeholder marker
        try:
            with open(subplan_file, "r", encoding="utf-8") as f:
                content = f.read()

            if "[TO BE FILLED" in content:  # Match both "[TO BE FILLED]" and "[TO BE FILLED:"
                # Extract achievement ID from filename
                # Format: SUBPLAN_{PLAN_NAME}_{ACHIEVEMENT_ID}.md
                # Example: SUBPLAN_MY-PLAN_51.md -> 5.1
                filename = subplan_file.stem
                match = re.search(r"_(\d+)$", filename)

                if match:
                    ach_id_formatted = match.group(1)
                    # Convert "51" to "5.1"
                    if len(ach_id_formatted) >= 2:
                        ach_id = f"{ach_id_formatted[0]}.{ach_id_formatted[1:]}"
                    else:
                        ach_id = ach_id_formatted

                    placeholders.append({"achievement_id": ach_id, "subplan_path": subplan_file})
        except Exception:
            # Skip files that can't be read
            continue

    return placeholders


def extract_plan_content_for_achievement(plan_data: Dict, achievement_id: str) -> str:
    """
    Extract relevant PLAN content for a specific achievement.

    Args:
        plan_data: Parsed PLAN data from PlanParser
        achievement_id: Achievement ID (e.g., "5.1")

    Returns:
        Extracted PLAN content as string

    Example:
        >>> content = extract_plan_content_for_achievement(plan_data, "5.1")
        >>> print(content)
    """
    # Find achievement in PLAN data
    achievements = plan_data.get("achievements", [])

    for ach in achievements:
        # Handle both Achievement objects and dictionaries
        if hasattr(ach, "number"):
            # Achievement object (dataclass)
            ach_id = ach.number
            title = ach.title
            description = ach.goal
            details = ""  # Achievement objects don't have details field
            estimated_hours = ach.effort
        else:
            # Dictionary
            ach_id = ach.get("id") or ach.get("achievement_id")
            title = ach.get("title", "")
            description = ach.get("description", "")
            details = ach.get("details", "")
            estimated_hours = ach.get("estimated_hours", "")

        if ach_id == achievement_id:
            # Format content
            content = f"**Title**: {title}\n\n"

            if description:
                content += f"**Description**:\n{description}\n\n"

            if details:
                content += f"**Details**:\n{details}\n\n"

            if estimated_hours:
                content += f"**Estimated Hours**: {estimated_hours}\n"

            return content.strip()

    # Achievement not found
    return f"[Achievement {achievement_id} not found in PLAN]"


def format_batch_fill_prompt(
    plan_name: str,
    plan_path: Path,
    achievements: List[Dict],
    plan_data: Dict,
) -> str:
    """
    Format the batch fill prompt with all necessary context.

    Args:
        plan_name: Name of the plan
        plan_path: Path to plan directory
        achievements: List of achievement dicts with id and subplan_path
        plan_data: Parsed PLAN data

    Returns:
        Formatted prompt string

    Example:
        >>> prompt = format_batch_fill_prompt("MY-PLAN", path, achievements, plan_data)
        >>> print(len(prompt))  # Should be ~200-300 lines
    """
    # Header
    prompt = "=" * 80 + "\n"
    prompt += "BATCH SUBPLAN FILL PROMPT\n"
    prompt += "=" * 80 + "\n\n"

    # Context section
    prompt += "## CONTEXT\n\n"
    prompt += f"Plan: {plan_name}\n"

    achievement_ids = [a["achievement_id"] for a in achievements]
    prompt += f"Achievements: {', '.join(achievement_ids)}\n"
    prompt += f"Total SUBPLANs to fill: {len(achievements)}\n\n"

    prompt += "Files to update:\n"
    for ach in achievements:
        prompt += f"  - {ach['subplan_path']}\n"
    prompt += "\n"

    # Task section
    prompt += "## TASK\n\n"
    prompt += "Fill the placeholder SUBPLANs with content extracted from the PLAN.\n\n"
    prompt += "Each SUBPLAN must include:\n"
    prompt += "1. 🎯 Objective - Clear, specific goal from PLAN\n"
    prompt += "2. 📦 Deliverables - Concrete, measurable outputs (3-5 items)\n"
    prompt += "3. 🔧 Approach - Phases and steps to achieve objective\n"
    prompt += "4. 🔄 Execution Strategy - Single or multiple executions\n"
    prompt += "5. 🧪 Testing Strategy - Verification approach\n"
    prompt += "6. 📊 Expected Results - Success criteria\n\n"

    # PLAN content section
    prompt += "## PLAN CONTENT\n\n"

    for ach in achievements:
        ach_id = ach["achievement_id"]
        prompt += f"### Achievement {ach_id}\n\n"

        # Extract content from PLAN
        content = extract_plan_content_for_achievement(plan_data, ach_id)
        prompt += content + "\n\n"
        prompt += "---\n\n"

    # Template structure section
    prompt += "## TEMPLATE STRUCTURE\n\n"
    prompt += "For each SUBPLAN, use this structure:\n\n"
    prompt += "```markdown\n"
    prompt += "# SUBPLAN: Achievement {ID}\n\n"
    prompt += f"**PLAN**: {plan_name}\n"
    prompt += "**Achievement**: {ID}\n"
    prompt += "**Status**: 📋 Design Phase\n\n"
    prompt += "## 🎯 Objective\n\n"
    prompt += "[1-2 sentences: What will be achieved?]\n\n"
    prompt += "## 📦 Deliverables\n\n"
    prompt += "1. [Specific deliverable 1]\n"
    prompt += "2. [Specific deliverable 2]\n"
    prompt += "3. [Specific deliverable 3]\n\n"
    prompt += "## 🔧 Approach\n\n"
    prompt += "### Phase 1: [Phase Name]\n"
    prompt += "- [Action 1]\n"
    prompt += "- [Action 2]\n\n"
    prompt += "### Phase 2: [Phase Name]\n"
    prompt += "- [Action 1]\n"
    prompt += "- [Action 2]\n\n"
    prompt += "[Add more phases as needed]\n\n"
    prompt += "## 🔄 Execution Strategy\n\n"
    prompt += "**Execution Count**: [Single or Multiple]\n"
    prompt += "**Reasoning**: [Why this approach?]\n\n"
    prompt += "## 🧪 Testing Strategy\n\n"
    prompt += "[How to verify deliverables are complete and correct]\n\n"
    prompt += "## 📊 Expected Results\n\n"
    prompt += "- ✅ [Success criterion 1]\n"
    prompt += "- ✅ [Success criterion 2]\n"
    prompt += "- ✅ [Success criterion 3]\n"
    prompt += "```\n\n"

    # Output format section
    prompt += "## OUTPUT FORMAT\n\n"
    prompt += "Provide each filled SUBPLAN in this format:\n\n"
    prompt += "```\n"
    prompt += f"=== {achievements[0]['subplan_path'].name} ===\n\n"
    prompt += "[Complete SUBPLAN content]\n\n"
    prompt += "=== END ===\n\n"
    prompt += "```\n\n"
    prompt += "Continue this format for all achievements.\n\n"

    # Quality checklist
    prompt += "## QUALITY CHECKLIST\n\n"
    prompt += "For each SUBPLAN, ensure:\n"
    prompt += "- [ ] Objective is clear and specific\n"
    prompt += "- [ ] Deliverables are measurable\n"
    prompt += "- [ ] Approach has concrete phases\n"
    prompt += "- [ ] Execution strategy is justified\n"
    prompt += "- [ ] Testing strategy is practical\n"
    prompt += "- [ ] Expected results are verifiable\n\n"

    # References section
    prompt += "## REFERENCES\n\n"

    if plan_path.is_file():
        plan_file = plan_path
    else:
        plan_files = list(plan_path.glob("PLAN_*.md"))
        plan_file = plan_files[0] if plan_files else None

    if plan_file:
        prompt += f"- PLAN: {plan_file}\n"

    prompt += "- Template: LLM/templates/SUBPLAN-TEMPLATE.md\n"
    prompt += "- Guide: LLM/guides/SUBPLAN-WORKFLOW-GUIDE.md\n\n"

    # Footer
    prompt += "=" * 80 + "\n"

    return prompt


def generate_batch_fill_prompt(plan_path: Path, achievement_ids: Optional[List[str]] = None) -> str:
    """
    Generate prompt to fill multiple placeholder SUBPLANs.

    Main entry point for batch SUBPLAN fill prompt generation.

    Args:
        plan_path: Path to PLAN directory or PLAN file
        achievement_ids: Optional list of achievement IDs to include
                        If None, auto-detects all placeholders

    Returns:
        Formatted prompt string ready for LLM

    Example:
        >>> # Auto-detect placeholders
        >>> prompt = generate_batch_fill_prompt(Path("work-space/plans/MY-PLAN"))
        >>>
        >>> # Specific achievements
        >>> prompt = generate_batch_fill_prompt(
        ...     Path("work-space/plans/MY-PLAN"),
        ...     achievement_ids=["5.1", "5.2", "6.1"]
        ... )
    """
    # Get plan directory
    if plan_path.is_file():
        plan_dir = plan_path.parent
        plan_file = plan_path
    else:
        plan_dir = plan_path
        plan_files = list(plan_dir.glob("PLAN_*.md"))
        if not plan_files:
            raise FileNotFoundError(f"No PLAN_*.md file found in {plan_dir}")
        plan_file = plan_files[0]

    plan_name = plan_file.stem.replace("PLAN_", "")

    # Parse PLAN
    parser = PlanParser()
    plan_data = parser.parse_plan_file(plan_file)

    # Get achievements to process
    if achievement_ids is None:
        # Auto-detect placeholders
        placeholders = detect_placeholder_subplans(plan_dir)
        achievements = placeholders
    else:
        # Use provided achievement IDs
        achievements = []
        for ach_id in achievement_ids:
            ach_id_formatted = ach_id.replace(".", "")
            subplan_filename = f"SUBPLAN_{plan_name}_{ach_id_formatted}.md"
            subplan_path = plan_dir / "subplans" / subplan_filename

            achievements.append({"achievement_id": ach_id, "subplan_path": subplan_path})

    if not achievements:
        return "No placeholder SUBPLANs found."

    # Format prompt
    prompt = format_batch_fill_prompt(plan_name, plan_dir, achievements, plan_data)

    return prompt
