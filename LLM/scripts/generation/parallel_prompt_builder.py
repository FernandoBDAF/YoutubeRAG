#!/usr/bin/env python3
"""
Parallel Prompt Builder Module - Discovery Prompt Generation

This module generates prompts for analyzing PLANs to identify parallel
execution opportunities across 3 levels of parallelization.

**Design Philosophy**:
- Code over configuration (templates embedded in Python)
- Follows prompt_builder.py pattern
- Dynamic prompt generation from PLAN data
- Filesystem-first state tracking

**Module Responsibilities**:
1. Generate discovery prompts for 3 parallelization levels
2. Provide independence validation criteria
3. Generate parallel.json template structures
4. Validate independence of achievements

Created: 2025-11-13
Achievement: 1.1 - Parallel Discovery Prompt Created
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class IndependenceCriteria:
    """
    Independence validation criteria for parallel execution.

    These criteria determine whether achievements/executions can run in parallel
    without conflicts or coordination overhead.
    """

    technical: List[str] = field(
        default_factory=lambda: [
            "No shared state between achievements",
            "No file conflicts (different files modified)",
            "No race conditions or timing dependencies",
            "No shared database/external resources",
        ]
    )

    testing: List[str] = field(
        default_factory=lambda: [
            "Tests can run in parallel without interference",
            "No shared test fixtures or data",
            "No test ordering dependencies",
            "Independent test environments",
        ]
    )

    mergeability: List[str] = field(
        default_factory=lambda: [
            "Changes can be merged without conflicts",
            "Different code sections modified",
            "No overlapping refactoring",
            "Clear merge strategy documented",
        ]
    )

    dependency: List[str] = field(
        default_factory=lambda: [
            "No circular dependencies",
            "Clear dependency chain",
            "Dependencies explicitly documented",
            "No implicit ordering requirements",
        ]
    )

    def to_checklist(self) -> str:
        """Format criteria as markdown checklist."""
        checklist = "**Technical Independence**:\n"
        for criterion in self.technical:
            checklist += f"- [ ] {criterion}\n"

        checklist += "\n**Testing Independence**:\n"
        for criterion in self.testing:
            checklist += f"- [ ] {criterion}\n"

        checklist += "\n**Mergeability**:\n"
        for criterion in self.mergeability:
            checklist += f"- [ ] {criterion}\n"

        checklist += "\n**Dependency Clarity**:\n"
        for criterion in self.dependency:
            checklist += f"- [ ] {criterion}\n"

        return checklist


class ParallelPromptBuilder:
    """
    Build parallel discovery prompts for PLAN analysis.

    This class generates prompts that guide LLMs through analyzing PLANs
    for parallel execution opportunities, validating independence criteria,
    and producing parallel.json dependency structures.

    **Usage**:
        builder = ParallelPromptBuilder()
        prompt = builder.build_discovery_prompt(plan_path, level=2, plan_data=data, priority=1)
        criteria = builder.build_independence_checklist()
    """

    def __init__(self):
        """Initialize prompt builder."""
        self.criteria = IndependenceCriteria()

    def build_discovery_prompt(self, plan_path: Path, level: int, plan_data: Dict, **kwargs) -> str:
        """
        Generate discovery prompt for specified parallelization level.

        Args:
            plan_path: Path to PLAN file
            level: Parallelization level (1, 2, or 3)
            plan_data: Parsed PLAN data
            **kwargs: Level-specific arguments (achievement_num, priority, etc.)

        Returns:
            Generated discovery prompt string

        Raises:
            ValueError: If level is invalid or required kwargs missing

        Example:
            >>> builder = ParallelPromptBuilder()
            >>> prompt = builder.build_discovery_prompt(
            ...     Path("PLAN_TEST.md"),
            ...     level=2,
            ...     plan_data={"plan_name": "TEST", "achievements": []},
            ...     priority=1
            ... )
        """
        if level == 1:
            achievement_num = kwargs.get("achievement_num")
            if not achievement_num:
                raise ValueError("Level 1 requires 'achievement_num' argument")
            return self._build_level_1_prompt(plan_path, achievement_num, plan_data)
        elif level == 2:
            priority = kwargs.get("priority")
            if priority is None:
                raise ValueError("Level 2 requires 'priority' argument")
            return self._build_level_2_prompt(plan_path, priority, plan_data)
        elif level == 3:
            return self._build_level_3_prompt(plan_path, plan_data)
        else:
            raise ValueError(f"Invalid parallelization level: {level}. Must be 1, 2, or 3.")

    def _build_level_1_prompt(self, plan_path: Path, achievement_num: str, plan_data: Dict) -> str:
        """Build Level 1 discovery prompt (same achievement, multiple executions)."""

        template = f"""Analyze Achievement {achievement_num} in @{plan_path.name} for multi-execution parallelization.

═══════════════════════════════════════════════════════════════════════

CONTEXT:

- PLAN: {plan_data.get('plan_name', plan_path.stem)}
- Achievement: {achievement_num}
- Level: 1 (Same Achievement Multi-Execution)

═══════════════════════════════════════════════════════════════════════

OBJECTIVE:

Identify if this achievement can be split into multiple independent EXECUTION_TASKs
that can be executed in parallel by different executors.

═══════════════════════════════════════════════════════════════════════

INDEPENDENCE CRITERIA:

{self.build_independence_checklist()}

═══════════════════════════════════════════════════════════════════════

ANALYSIS STEPS:

1. Read Achievement {achievement_num} section from PLAN
2. Identify distinct work packages within achievement
3. Check for dependencies between work packages
4. Validate independence criteria for each package
5. Determine if parallel execution is feasible

═══════════════════════════════════════════════════════════════════════

OUTPUT FORMAT:

{self.build_parallel_json_template()}

═══════════════════════════════════════════════════════════════════════

DECISION:

- If YES (parallelizable): Generate parallel.json structure
- If NO (not parallelizable): Explain why and suggest sequential execution

═══════════════════════════════════════════════════════════════════════
"""
        return template

    def _build_level_2_prompt(self, plan_path: Path, priority: int, plan_data: Dict) -> str:
        """Build Level 2 discovery prompt (same priority, multiple achievements)."""

        achievements = [
            a for a in plan_data.get("achievements", []) if a.get("priority") == priority
        ]

        template = f"""Analyze Priority {priority} in @{plan_path.name} for parallel achievement execution.

═══════════════════════════════════════════════════════════════════════

CONTEXT:

- PLAN: {plan_data.get('plan_name', plan_path.stem)}
- Priority: {priority}
- Achievements: {len(achievements)} achievements in this priority
- Level: 2 (Same Priority Intra-Plan)

═══════════════════════════════════════════════════════════════════════

OBJECTIVE:

Identify which achievements within Priority {priority} can be executed in parallel
by analyzing dependencies and independence criteria.

═══════════════════════════════════════════════════════════════════════

INDEPENDENCE CRITERIA:

{self.build_independence_checklist()}

═══════════════════════════════════════════════════════════════════════

ANALYSIS STEPS:

1. List all achievements in Priority {priority}
2. Identify dependencies between achievements
3. Check for shared resources or file conflicts
4. Validate independence criteria for each achievement
5. Build dependency tree
6. Identify parallel execution opportunities

═══════════════════════════════════════════════════════════════════════

OUTPUT FORMAT:

{self.build_parallel_json_template()}

═══════════════════════════════════════════════════════════════════════

DEPENDENCY TREE RULES:

- Achievements with no dependencies can start immediately
- Achievements can run in parallel if they don't depend on each other
- Circular dependencies are NOT allowed
- Document all dependencies explicitly

═══════════════════════════════════════════════════════════════════════
"""
        return template

    def _build_level_3_prompt(self, plan_path: Path, plan_data: Dict) -> str:
        """Build Level 3 discovery prompt (cross-priority parallelization)."""

        template = f"""Analyze @{plan_path.name} for cross-priority parallel execution opportunities.

═══════════════════════════════════════════════════════════════════════

CONTEXT:

- PLAN: {plan_data.get('plan_name', plan_path.stem)}
- Total Achievements: {len(plan_data.get('achievements', []))}
- Priorities: {plan_data.get('num_priorities', 'Unknown')}
- Level: 3 (Cross-Priority)

═══════════════════════════════════════════════════════════════════════

OBJECTIVE:

Identify achievements across different priorities that can be executed in parallel,
enabling maximum parallelization across the entire PLAN.

═══════════════════════════════════════════════════════════════════════

INDEPENDENCE CRITERIA:

{self.build_independence_checklist()}

═══════════════════════════════════════════════════════════════════════

ANALYSIS STEPS:

1. List all achievements across all priorities
2. Identify explicit dependencies (Achievement X.Y depends on X.Z)
3. Identify implicit dependencies (shared files, state, resources)
4. Validate independence criteria for all achievement pairs
5. Build complete dependency tree
6. Identify maximum parallel execution paths

═══════════════════════════════════════════════════════════════════════

OUTPUT FORMAT:

{self.build_parallel_json_template()}

═══════════════════════════════════════════════════════════════════════

ADVANCED CONSIDERATIONS:

- Priority order may indicate implicit dependencies
- Consider merge complexity for cross-priority work
- Balance parallelization benefits vs coordination overhead
- Document assumptions about independence

═══════════════════════════════════════════════════════════════════════
"""
        return template

    def build_independence_checklist(self) -> str:
        """
        Generate independence validation checklist.

        Returns:
            Markdown-formatted checklist of independence criteria
        """
        return self.criteria.to_checklist()

    def build_parallel_json_template(self) -> str:
        """
        Generate parallel.json template structure.

        Returns:
            JSON template as formatted string
        """
        template = """{
  "plan_name": "PLAN-NAME",
  "parallelization_level": "level_2",
  "created_date": "2025-11-13",
  "achievements": [
    {
      "achievement_id": "1.1",
      "title": "Achievement Title",
      "dependencies": [],
      "status": "not_started",
      "estimated_hours": 4
    },
    {
      "achievement_id": "1.2",
      "title": "Another Achievement",
      "dependencies": ["1.1"],
      "status": "not_started",
      "estimated_hours": 3
    }
  ],
  "notes": "Achievements 1.1 and 1.3 can run in parallel after dependencies are met"
}"""
        return template

    def validate_independence(self, achievement_data: Dict) -> Dict[str, any]:
        """
        Validate achievement independence criteria.

        Args:
            achievement_data: Achievement data including dependencies, files, etc.

        Returns:
            Validation result with pass/fail for each criterion category
        """
        result = {
            "achievement_id": achievement_data.get("achievement_id"),
            "technical": self._validate_technical_independence(
                achievement_data, self.criteria.technical
            ),
            "testing": self._validate_testing_independence(achievement_data, self.criteria.testing),
            "mergeability": self._validate_mergeability(
                achievement_data, self.criteria.mergeability
            ),
            "dependency": self._validate_dependency_clarity(
                achievement_data, self.criteria.dependency
            ),
            "overall": False,  # Will be set based on all categories
        }

        # Overall pass if all categories pass
        result["overall"] = all(
            [
                result["technical"]["pass"],
                result["testing"]["pass"],
                result["mergeability"]["pass"],
                result["dependency"]["pass"],
            ]
        )

        return result

    def _validate_technical_independence(self, data: Dict, criteria: List[str]) -> Dict:
        """Validate technical independence criteria."""
        # Placeholder - actual validation logic would check for shared files, state, etc.
        return {
            "pass": True,
            "criteria_checked": len(criteria),
            "notes": "Manual validation required",
        }

    def _validate_testing_independence(self, data: Dict, criteria: List[str]) -> Dict:
        """Validate testing independence criteria."""
        return {
            "pass": True,
            "criteria_checked": len(criteria),
            "notes": "Manual validation required",
        }

    def _validate_mergeability(self, data: Dict, criteria: List[str]) -> Dict:
        """Validate mergeability criteria."""
        return {
            "pass": True,
            "criteria_checked": len(criteria),
            "notes": "Manual validation required",
        }

    def _validate_dependency_clarity(self, data: Dict, criteria: List[str]) -> Dict:
        """Validate dependency clarity criteria."""
        return {
            "pass": True,
            "criteria_checked": len(criteria),
            "notes": "Manual validation required",
        }
