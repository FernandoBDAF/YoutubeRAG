#!/usr/bin/env python3
"""
Prompt Builder Module - Template Management and Formatting

This module provides prompt template management and formatting for the
prompt generation system, separating template content and formatting logic
from workflow orchestration.

**Design Philosophy**:
- Templates define structure and content
- fill functions handle dynamic value injection
- Builders construct messages for different scenarios
- Main script focuses on workflow orchestration

**Module Responsibilities**:
1. Store prompt templates (ACHIEVEMENT_EXECUTION_TEMPLATE)
2. Fill templates with context values
3. Build completion messages
4. Format validation scripts section
5. Prepare project context sections

**Note**: This module handles templates for generate_prompt.py specifically.
Other prompt types (SUBPLAN, EXECUTION, Feedback) have dedicated scripts:
- generate_subplan_prompt.py
- generate_execution_prompt.py
- generate_feedback_prompt.py

Created: 2025-11-12
Achievement: 2.3 - Extract Prompt Generation Module (Adapted from SUBPLAN)
"""
from __future__ import annotations  # Enable deferred type hint evaluation

from pathlib import Path
from typing import List, Dict, Optional


class PromptBuilder:
    """
    Build and format prompts for achievement execution.

    This class encapsulates prompt template management, separating the
    template content and formatting logic from the main workflow orchestration
    in generate_prompt.py.

    **Responsibilities**:
    - Store achievement execution template
    - Fill template with runtime context
    - Build completion messages
    - Format validation scripts

    **Usage**:
        builder = PromptBuilder()
        prompt = builder.build_achievement_prompt(context, validation_scripts)
        completion_msg = builder.build_completion_message(feature_name, plan_path, archive_location)
    """

    # Achievement Execution Template
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

    def __init__(self):
        """Initialize PromptBuilder (stateless, templates are class attributes)."""
        pass

    def build_achievement_prompt(
        self, context: Dict[str, any], validation_scripts: List[str]
    ) -> str:
        """
        Build achievement execution prompt from template and context.

        Takes the ACHIEVEMENT_EXECUTION_TEMPLATE and replaces placeholders with
        real values (feature name, achievement number, context budget, etc.).

        This is the main prompt builder method that generates the full prompt
        text for executing a PLAN achievement.

        Args:
            context: Dict with values to fill in template:
                - feature_name: Name of feature/PLAN
                - achievement_num: Achievement number (e.g. "1.2")
                - achievement_title: Achievement title
                - achievement_goal: Goal description (optional)
                - estimated_hours: Effort estimate (optional)
                - achievement_lines: Lines in achievement section
                - handoff_lines: Lines in handoff section
                - plan_total_lines: Total PLAN lines
                - context_budget: Max lines to read
                - subplan_num: Subplan number (achievement without ".")
                - archive_location: Where to archive files
                - project_context: Optional project context section
            validation_scripts: List of validation script names to include

        Returns:
            str: Fully formatted achievement execution prompt

        Example:
            >>> builder = PromptBuilder()
            >>> context = {
            ...     "feature_name": "FEATURE",
            ...     "achievement_num": "1.2",
            ...     "achievement_title": "Implement Feature",
            ...     "achievement_lines": 45,
            ...     "handoff_lines": 12,
            ...     "plan_total_lines": 500,
            ...     "context_budget": 57,
            ...     "subplan_num": "12",
            ...     "archive_location": "work-space/plans/FEATURE/",
            ... }
            >>> prompt = builder.build_achievement_prompt(context, [])
            >>> "Achievement 1.2" in prompt
            True
        """
        # Format validation scripts section
        validation_section = self.format_validation_scripts(validation_scripts)

        # Fill template with context values
        return self.ACHIEVEMENT_EXECUTION_TEMPLATE.format(
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
            validation_scripts=validation_section,
            project_context=context.get("project_context", ""),
        )

    def format_validation_scripts(self, validation_scripts: List[str]) -> str:
        """
        Format validation scripts section for prompt.

        Converts list of validation script names into formatted text block
        for inclusion in the prompt template.

        Args:
            validation_scripts: List of validation script names

        Returns:
            str: Formatted validation scripts text
                 - If scripts exist: Numbered list with blocking note
                 - If no scripts: Placeholder message

        Example:
            >>> builder = PromptBuilder()
            >>> text = builder.format_validation_scripts(["validate_plan.py", "check_files.py"])
            >>> "validate_plan.py" in text
            True
            >>> "BLOCKS with error" in text
            True

            >>> text = builder.format_validation_scripts([])
            >>> "being built" in text
            True
        """
        if validation_scripts:
            scripts_text = "After Step 4, these scripts will run:\n"
            for script in validation_scripts:
                scripts_text += f"✓ {script}\n"
            scripts_text += "\nIf issues found: BLOCKS with error + fix prompt"
            return scripts_text
        else:
            return "(Validation scripts being built in this PLAN)"

    def build_completion_message(
        self, feature_name: str, plan_path: Path, archive_location: str
    ) -> str:
        """
        Build PLAN completion message.

        Generates the message displayed when all achievements in a PLAN
        are complete, guiding user through END_POINT protocol.

        Args:
            feature_name: Name of the feature/PLAN
            plan_path: Path to the PLAN file
            archive_location: Where PLAN will be archived

        Returns:
            str: Formatted completion message with next steps

        Example:
            >>> builder = PromptBuilder()
            >>> from pathlib import Path
            >>> msg = builder.build_completion_message(
            ...     "FEATURE",
            ...     Path("work-space/plans/FEATURE/PLAN_FEATURE.md"),
            ...     "work-space/plans/FEATURE/"
            ... )
            >>> "PLAN COMPLETE" in msg
            True
            >>> "END_POINT protocol" in msg
            True
        """
        return f"""✅ PLAN COMPLETE: {feature_name}

All achievements in this PLAN are complete. The PLAN is ready for the END_POINT protocol.

**Next Steps**:
1. Review the PLAN's "Current Status & Handoff" section to verify completion
2. Follow the IMPLEMENTATION_END_POINT.md protocol to:
   - Archive the PLAN
   - Update ACTIVE_PLANS.md
   - Create completion summary
   - Commit final state

**PLAN File**: {plan_path.name}
**Archive Location**: {archive_location}

**To verify completion**:
  python LLM/scripts/validation/validate_plan_completion.py @{plan_path.name}

**To proceed with END_POINT**:
  See LLM/protocols/IMPLEMENTATION_END_POINT.md for complete workflow.
"""
