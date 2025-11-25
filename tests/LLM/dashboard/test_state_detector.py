"""
Tests for state_detector module.

Tests state detection logic with filesystem queries.
"""
import pytest
from pathlib import Path

from LLM.dashboard.state_detector import StateDetector
from LLM.dashboard.models import PlanStatus


class TestStateDetector:
    """Tests for StateDetector class."""
    
    def test_get_plan_state_minimal(self, tmp_path):
        """Test get_plan_state() with minimal plan (no files)."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        
        detector = StateDetector()
        state = detector.get_plan_state(plan_dir)
        
        assert state.name == "MY-PLAN"
        assert state.last_achievement is None
        assert state.next_achievements == []
        assert state.total_achievements == 0
        assert state.completed_achievements == 0
        assert state.progress_percentage == 0.0
    
    def test_get_last_complete_single_approved(self, tmp_path):
        """Test _get_last_complete() with single APPROVED file."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        feedbacks_dir = plan_dir / "execution" / "feedbacks"
        feedbacks_dir.mkdir(parents=True)
        (feedbacks_dir / "APPROVED_11.md").touch()
        
        detector = StateDetector()
        result = detector._get_last_complete(plan_dir)
        
        assert result == "1.1"
    
    def test_get_last_complete_multiple_approved(self, tmp_path):
        """Test _get_last_complete() returns highest numbered APPROVED."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        feedbacks_dir = plan_dir / "execution" / "feedbacks"
        feedbacks_dir.mkdir(parents=True)
        (feedbacks_dir / "APPROVED_11.md").touch()
        (feedbacks_dir / "APPROVED_23.md").touch()
        (feedbacks_dir / "APPROVED_12.md").touch()
        
        detector = StateDetector()
        result = detector._get_last_complete(plan_dir)
        
        # Should return last in sorted order (APPROVED_23.md)
        assert result == "2.3"
    
    def test_get_last_complete_no_approved(self, tmp_path):
        """Test _get_last_complete() with no APPROVED files."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        feedbacks_dir = plan_dir / "execution" / "feedbacks"
        feedbacks_dir.mkdir(parents=True)
        
        detector = StateDetector()
        result = detector._get_last_complete(plan_dir)
        
        assert result is None
    
    def test_get_last_complete_missing_feedbacks_dir(self, tmp_path):
        """Test _get_last_complete() with missing feedbacks directory."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        
        detector = StateDetector()
        result = detector._get_last_complete(plan_dir)
        
        assert result is None
    
    def test_get_pending_fixes_single_fix(self, tmp_path):
        """Test _get_pending_fixes() with single FIX file."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        feedbacks_dir = plan_dir / "execution" / "feedbacks"
        feedbacks_dir.mkdir(parents=True)
        (feedbacks_dir / "FIX_12.md").touch()
        
        detector = StateDetector()
        result = detector._get_pending_fixes(plan_dir)
        
        assert result == ["1.2"]
    
    def test_get_pending_fixes_multiple_fixes(self, tmp_path):
        """Test _get_pending_fixes() with multiple FIX files."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        feedbacks_dir = plan_dir / "execution" / "feedbacks"
        feedbacks_dir.mkdir(parents=True)
        (feedbacks_dir / "FIX_12.md").touch()
        (feedbacks_dir / "FIX_23.md").touch()
        (feedbacks_dir / "FIX_11.md").touch()
        
        detector = StateDetector()
        result = detector._get_pending_fixes(plan_dir)
        
        # Should be sorted
        assert result == ["1.1", "1.2", "2.3"]
    
    def test_get_pending_fixes_no_fixes(self, tmp_path):
        """Test _get_pending_fixes() with no FIX files."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        feedbacks_dir = plan_dir / "execution" / "feedbacks"
        feedbacks_dir.mkdir(parents=True)
        
        detector = StateDetector()
        result = detector._get_pending_fixes(plan_dir)
        
        assert result == []
    
    def test_calculate_progress_normal(self):
        """Test _calculate_progress() with normal values."""
        detector = StateDetector()
        
        result = detector._calculate_progress(5, 10)
        assert result == 50.0
        
        result = detector._calculate_progress(3, 10)
        assert result == 30.0
        
        result = detector._calculate_progress(10, 10)
        assert result == 100.0
    
    def test_calculate_progress_zero_total(self):
        """Test _calculate_progress() with zero total."""
        detector = StateDetector()
        result = detector._calculate_progress(0, 0)
        
        assert result == 0.0
    
    def test_get_next_available_first_achievement(self):
        """Test _get_next_available() when no achievements complete."""
        detector = StateDetector()
        all_achievements = ["0.1", "0.2", "1.1", "1.2"]
        
        result = detector._get_next_available(all_achievements, None, [])
        
        assert result == ["0.1"]
    
    def test_get_next_available_sequential(self):
        """Test _get_next_available() returns next achievements."""
        detector = StateDetector()
        all_achievements = ["0.1", "0.2", "1.1", "1.2", "1.3"]
        
        result = detector._get_next_available(all_achievements, "0.2", [])
        
        # Should return up to 3 next achievements
        assert result == ["1.1", "1.2", "1.3"]
    
    def test_get_next_available_excludes_fixes(self):
        """Test _get_next_available() excludes achievements with FIX files."""
        detector = StateDetector()
        all_achievements = ["0.1", "0.2", "1.1", "1.2"]
        pending_fixes = ["1.1"]
        
        result = detector._get_next_available(all_achievements, "0.2", pending_fixes)
        
        # Should skip 1.1 (has FIX) and return 1.2
        assert result == ["1.2"]
    
    def test_get_next_available_empty_list(self):
        """Test _get_next_available() with empty achievement list."""
        detector = StateDetector()
        
        result = detector._get_next_available([], None, [])
        
        assert result == []
    
    def test_parse_achievement_index_standard_format(self, tmp_path):
        """Test _parse_achievement_index() with standard PLAN format."""
        plan_file = tmp_path / "PLAN_TEST.md"
        plan_file.write_text("""
# PLAN: Test Plan

## 📋 Achievement Index

- Achievement 0.1: Setup
- Achievement 0.2: Foundation
- Achievement 1.1: Core Feature

## Next Section
""")
        
        detector = StateDetector()
        result = detector._parse_achievement_index(plan_file)
        
        assert result == ["0.1", "0.2", "1.1"]
    
    def test_parse_achievement_index_with_status(self, tmp_path):
        """Test _parse_achievement_index() with status markers."""
        plan_file = tmp_path / "PLAN_TEST.md"
        plan_file.write_text("""
## 📋 Achievement Index

- Achievement 0.1 ✅: Setup Complete
- Achievement 0.2: Foundation
- Achievement 1.1 ⚠️: Needs Fix

## End
""")
        
        detector = StateDetector()
        result = detector._parse_achievement_index(plan_file)
        
        assert result == ["0.1", "0.2", "1.1"]
    
    def test_parse_achievement_index_no_section(self, tmp_path):
        """Test _parse_achievement_index() with no Achievement Index."""
        plan_file = tmp_path / "PLAN_TEST.md"
        plan_file.write_text("# PLAN: Test\n\nNo achievement index here")
        
        detector = StateDetector()
        result = detector._parse_achievement_index(plan_file)
        
        assert result == []
    
    def test_parse_achievement_index_missing_file(self):
        """Test _parse_achievement_index() with missing file."""
        detector = StateDetector()
        result = detector._parse_achievement_index(Path("/nonexistent.md"))
        
        assert result == []
    
    def test_determine_status_active(self):
        """Test _determine_status() returns ACTIVE."""
        detector = StateDetector()
        result = detector._determine_status(3, 10, [])
        
        assert result == PlanStatus.ACTIVE
    
    def test_determine_status_complete(self):
        """Test _determine_status() returns COMPLETE."""
        detector = StateDetector()
        result = detector._determine_status(10, 10, [])
        
        assert result == PlanStatus.COMPLETE
    
    def test_determine_status_needs_attention(self):
        """Test _determine_status() returns NEEDS_ATTENTION."""
        detector = StateDetector()
        result = detector._determine_status(5, 10, ["1.2", "2.3"])
        
        assert result == PlanStatus.NEEDS_ATTENTION



