"""
Plan Discovery Module

Discovers plans from filesystem by scanning work-space/plans/ directory.

**Design Philosophy**:
- Filesystem-first: Discover plans from directory structure
- No state persistence: Always fresh from filesystem
- Graceful degradation: Handle missing files/directories
- Fast queries: Use Path.glob() for efficiency

Created: 2025-11-13
Achievement: 0.2 - Plan Discovery & State Detection
Updated: 2025-11-13
Achievement: 0.4 - Library Integration & Production Patterns
"""

from pathlib import Path
from typing import List, Optional

from core.libraries.logging import get_logger
from LLM.dashboard.exceptions import PlanLoadError

logger = get_logger(__name__)


class PlanDiscovery:
    """
    Discover plans from filesystem.

    Scans work-space/plans/ directory to find all plan directories and their
    PLAN_*.md files. Filters out hidden directories and handles missing files.

    **Usage**:
        discovery = PlanDiscovery()
        plans = discovery.get_all_plans()

        for plan_dir in plans:
            plan_file = discovery.get_plan_file(plan_dir)
            if plan_file:
                name = discovery.get_plan_name(plan_dir)
                print(f"Found: {name}")
    """

    def __init__(self, plans_root: Optional[Path] = None):
        """
        Initialize plan discovery.

        Args:
            plans_root: Root directory for plans (default: work-space/plans/)
        """
        if plans_root is None:
            # Default to work-space/plans/ relative to project root
            self.plans_root = Path("work-space/plans")
        else:
            self.plans_root = Path(plans_root)

    def get_all_plans(self) -> List[Path]:
        """
        Get all plan directories from work-space/plans/.

        Filters out:
        - Hidden directories (starting with '.')
        - Files (not directories)
        - Non-existent paths

        Returns:
            List of plan directory paths, sorted alphabetically

        Raises:
            PlanLoadError: If plans_root directory is not accessible

        **Example**:
            discovery = PlanDiscovery()
            plans = discovery.get_all_plans()
            # [Path('work-space/plans/PLAN-A'), Path('work-space/plans/PLAN-B')]
        """
        if not self.plans_root.exists():
            logger.warning(f"Plans root directory does not exist: {self.plans_root}")
            return []

        try:
            logger.debug(f"Discovering plans in: {self.plans_root}")
            plans = []
            for item in self.plans_root.iterdir():
                # Skip hidden directories
                if item.name.startswith("."):
                    continue

                # Skip non-directories
                if not item.is_dir():
                    continue

                plans.append(item)

            # Sort alphabetically for consistent ordering
            sorted_plans = sorted(plans, key=lambda p: p.name)
            logger.info(f"Discovered {len(sorted_plans)} plan(s)", extra={'plan_count': len(sorted_plans)})
            return sorted_plans
            
        except OSError as e:
            logger.error(f"Failed to read plans directory: {str(e)}", exc_info=True, extra={
                'plans_root': str(self.plans_root)
            })
            raise PlanLoadError(
                f"Failed to read plans directory: {str(e)}",
                context={
                    'plans_root': str(self.plans_root),
                    'error': str(e)
                },
                suggestions=[
                    "Verify plans directory is accessible",
                    "Check file system permissions",
                    "Ensure disk is mounted and available"
                ]
            ) from e

    def get_plan_file(self, plan_dir: Path) -> Optional[Path]:
        """
        Get PLAN_*.md file from plan directory.

        Searches for files matching pattern PLAN_*.md in the directory.
        If multiple PLAN files exist, returns the first one found.

        Args:
            plan_dir: Plan directory path

        Returns:
            Path to PLAN file, or None if not found

        Raises:
            PlanLoadError: If directory cannot be read (permissions, I/O error)

        **Example**:
            plan_dir = Path('work-space/plans/MY-PLAN')
            plan_file = discovery.get_plan_file(plan_dir)
            # Path('work-space/plans/MY-PLAN/PLAN_MY-PLAN.md')
        """
        if not plan_dir.exists() or not plan_dir.is_dir():
            return None

        try:
            plan_files = list(plan_dir.glob("PLAN_*.md"))

            if not plan_files:
                return None

            # If multiple PLAN files, return first (shouldn't happen in practice)
            return plan_files[0]
            
        except OSError as e:
            raise PlanLoadError(
                f"Failed to read plan directory: {str(e)}",
                context={
                    'plan_dir': str(plan_dir),
                    'error': str(e)
                },
                suggestions=[
                    "Verify plan directory is accessible",
                    "Check file permissions",
                    "Ensure PLAN_*.md file is not corrupted"
                ]
            ) from e

    def get_plan_name(self, plan_dir: Path) -> str:
        """
        Extract plan name from directory path.

        Args:
            plan_dir: Plan directory path

        Returns:
            Plan name (directory name)

        **Example**:
            plan_dir = Path('work-space/plans/MY-PLAN')
            name = discovery.get_plan_name(plan_dir)
            # "MY-PLAN"
        """
        return plan_dir.name

    def validate_plan_structure(self, plan_dir: Path) -> bool:
        """
        Validate that plan directory has required structure.

        Checks for:
        - PLAN_*.md file exists
        - execution/ directory exists
        - subplans/ directory exists

        Args:
            plan_dir: Plan directory path

        Returns:
            True if structure is valid, False otherwise

        **Example**:
            plan_dir = Path('work-space/plans/MY-PLAN')
            if discovery.validate_plan_structure(plan_dir):
                print("Plan structure is valid")
        """
        if not plan_dir.exists() or not plan_dir.is_dir():
            return False

        # Check for PLAN file
        if not self.get_plan_file(plan_dir):
            return False

        # Check for required directories
        execution_dir = plan_dir / "execution"
        subplans_dir = plan_dir / "subplans"

        return execution_dir.exists() and subplans_dir.exists()
