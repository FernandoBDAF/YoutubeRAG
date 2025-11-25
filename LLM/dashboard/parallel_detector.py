"""
Parallel execution detection for dashboard.

Detects parallel execution opportunities from parallel.json files and provides
UI-focused parallel group information for the dashboard.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional

from core.libraries.logging import get_logger

# Import batch tools for parallel detection
from LLM.scripts.generation.batch_subplan import filter_by_dependency_level

logger = get_logger(__name__)


@dataclass
class ParallelGroup:
    """
    Represents a group of achievements that can be executed in parallel.
    
    Attributes:
        level: Dependency level (0 = no dependencies, 1 = depends on 0, etc.)
        achievements: List of achievement objects in this group
        achievement_ids: List of achievement IDs (e.g., ["3.1", "3.2", "3.3"])
        parallel_time: Estimated time if executed in parallel (hours)
        sequential_time: Estimated time if executed sequentially (hours)
        time_savings: Time saved by parallel execution (hours)
        savings_percentage: Percentage of time saved (0-100)
    """
    level: int
    achievements: List[Dict[str, Any]]
    achievement_ids: List[str]
    parallel_time: float
    sequential_time: float
    time_savings: float
    savings_percentage: float


class ParallelDetector:
    """
    Detects and analyzes parallel execution opportunities for dashboard display.
    
    Integrates with PARALLEL-EXECUTION-AUTOMATION tools to provide UI-focused
    parallel group information.
    """
    
    def __init__(self, plan_path: Path):
        """
        Initialize parallel detector.
        
        Args:
            plan_path: Path to plan directory
        """
        self.plan_path = plan_path
        self.parallel_json_path = plan_path / "parallel.json"
    
    def has_parallel_opportunities(self) -> bool:
        """
        Check if plan has parallel.json file.
        
        Returns:
            True if parallel.json exists, False otherwise
        """
        return self.parallel_json_path.exists()
    
    def detect_parallel_opportunities(self) -> List[ParallelGroup]:
        """
        Detect parallel execution opportunities from parallel.json.
        
        Returns:
            List of ParallelGroup objects, one per dependency level.
            Empty list if no parallel.json or no opportunities.
        
        Raises:
            FileNotFoundError: If parallel.json doesn't exist
            json.JSONDecodeError: If parallel.json is invalid
        """
        if not self.has_parallel_opportunities():
            logger.debug("No parallel.json found", extra={
                'plan_path': str(self.plan_path)
            })
            return []
        
        logger.info("Detecting parallel opportunities", extra={
            'plan_path': str(self.plan_path)
        })
        
        try:
            # Load parallel.json
            parallel_data = json.loads(self.parallel_json_path.read_text())
            achievements = parallel_data.get("achievements", [])
            
            if not achievements:
                logger.warning("No achievements in parallel.json", extra={
                    'plan_path': str(self.plan_path)
                })
                return []
            
            # Normalize achievement format (id -> achievement_id for batch tools)
            normalized_achievements = self._normalize_achievements(achievements)
            
            # Filter to incomplete achievements
            incomplete_achievements = self._filter_incomplete(normalized_achievements)
            
            if not incomplete_achievements:
                logger.info("All achievements complete - no parallel opportunities", extra={
                    'plan_path': str(self.plan_path)
                })
                return []
            
            # Group by dependency level
            parallel_groups = []
            level = 0
            
            while True:
                # Use batch_subplan's filter_by_dependency_level
                level_achievements = filter_by_dependency_level(
                    incomplete_achievements, 
                    level=level
                )
                
                if not level_achievements:
                    break
                
                # Build parallel group with time calculations
                group = self._build_parallel_group(level, level_achievements)
                parallel_groups.append(group)
                
                level += 1
            
            logger.info("Parallel opportunities detected", extra={
                'plan_path': str(self.plan_path),
                'groups': len(parallel_groups),
                'total_achievements': sum(len(g.achievements) for g in parallel_groups)
            })
            
            return parallel_groups
        
        except json.JSONDecodeError as e:
            logger.error("Failed to parse parallel.json", exc_info=True, extra={
                'plan_path': str(self.plan_path)
            })
            raise
        except Exception as e:
            logger.error("Error detecting parallel opportunities", exc_info=True, extra={
                'plan_path': str(self.plan_path)
            })
            raise
    
    def _normalize_achievements(self, achievements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize achievement format for batch tools.
        
        Converts 'id' field to 'achievement_id' if needed, since batch tools
        expect 'achievement_id' but parallel.json uses 'id'.
        
        Args:
            achievements: List of achievement objects from parallel.json
        
        Returns:
            Normalized list with 'achievement_id' field
        """
        normalized = []
        for ach in achievements:
            ach_copy = ach.copy()
            # If 'id' exists but 'achievement_id' doesn't, copy id to achievement_id
            if 'id' in ach_copy and 'achievement_id' not in ach_copy:
                ach_copy['achievement_id'] = ach_copy['id']
            normalized.append(ach_copy)
        return normalized
    
    def _filter_incomplete(self, achievements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter achievements to only those without APPROVED files.
        
        Args:
            achievements: List of achievement objects from parallel.json
        
        Returns:
            List of achievements without APPROVED files
        """
        feedbacks_dir = self.plan_path / "execution" / "feedbacks"
        
        if not feedbacks_dir.exists():
            # No feedbacks directory means all achievements are incomplete
            return achievements
        
        incomplete = []
        
        for achievement in achievements:
            # Try both 'achievement_id' and 'id' fields
            achievement_id = achievement.get("achievement_id") or achievement.get("id", "")
            # Convert "1.1" to "11" for APPROVED file check
            approved_num = achievement_id.replace(".", "")
            approved_file = feedbacks_dir / f"APPROVED_{approved_num}.md"
            
            if not approved_file.exists():
                incomplete.append(achievement)
            else:
                logger.debug("Achievement already complete", extra={
                    'achievement_id': achievement_id,
                    'approved_file': str(approved_file)
                })
        
        logger.debug("Filtered to incomplete achievements", extra={
            'total': len(achievements),
            'incomplete': len(incomplete),
            'complete': len(achievements) - len(incomplete)
        })
        
        return incomplete
    
    def _build_parallel_group(
        self, 
        level: int, 
        achievements: List[Dict[str, Any]]
    ) -> ParallelGroup:
        """
        Build a ParallelGroup with time calculations.
        
        Args:
            level: Dependency level
            achievements: List of achievement objects
        
        Returns:
            ParallelGroup with time savings calculations
        """
        # Extract achievement IDs (try both field names)
        achievement_ids = [ach.get("achievement_id") or ach.get("id", "") for ach in achievements]
        
        # Calculate time estimates
        # Assumption: Each achievement takes 3-4 hours (use 3.5 average)
        time_per_achievement = 3.5  # hours
        
        # Sequential time: Sum of all achievements
        sequential_time = len(achievements) * time_per_achievement
        
        # Parallel time: Max of any single achievement (all run at once)
        parallel_time = time_per_achievement
        
        # Time savings
        time_savings = sequential_time - parallel_time
        
        # Savings percentage
        if sequential_time > 0:
            savings_percentage = (time_savings / sequential_time) * 100
        else:
            savings_percentage = 0.0
        
        logger.debug("Built parallel group", extra={
            'level': level,
            'achievements': len(achievements),
            'parallel_time': parallel_time,
            'sequential_time': sequential_time,
            'savings': time_savings
        })
        
        return ParallelGroup(
            level=level,
            achievements=achievements,
            achievement_ids=achievement_ids,
            parallel_time=parallel_time,
            sequential_time=sequential_time,
            time_savings=time_savings,
            savings_percentage=savings_percentage
        )
    
    def get_first_incomplete_group(self) -> Optional[ParallelGroup]:
        """
        Get the first (lowest level) incomplete parallel group.
        
        This is the group that should be executed next.
        
        Returns:
            First ParallelGroup or None if no opportunities
        """
        groups = self.detect_parallel_opportunities()
        return groups[0] if groups else None

