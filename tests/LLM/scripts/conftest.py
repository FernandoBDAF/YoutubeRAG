"""Pytest configuration and shared fixtures for LLM script tests."""

import pytest
import sys
import tempfile
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tests.LLM.scripts.fixtures.sample_plans import (
    get_sample_plan_content,
    get_minimal_plan_content,
    get_plan_with_achievements,
    get_plan_with_handoff,
)
from tests.LLM.scripts.fixtures.mock_archives import create_mock_archive


@pytest.fixture
def sample_plan_content():
    """Fixture providing sample PLAN content."""
    return get_sample_plan_content()


@pytest.fixture
def minimal_plan_content():
    """Fixture providing minimal valid PLAN content."""
    return get_minimal_plan_content()


@pytest.fixture
def plan_with_achievements():
    """Fixture providing PLAN content with multiple achievements."""
    return get_plan_with_achievements()


@pytest.fixture
def plan_with_handoff():
    """Fixture providing PLAN content with handoff section."""
    return get_plan_with_handoff()


@pytest.fixture
def sample_plan_path(tmp_path):
    """Fixture providing temporary PLAN file path with sample content."""
    plan_file = tmp_path / "PLAN_TEST.md"
    plan_file.write_text(get_sample_plan_content())
    return plan_file


@pytest.fixture
def temp_plan_file(tmp_path):
    """Fixture providing temporary PLAN file path (empty, can be customized)."""
    plan_file = tmp_path / "PLAN_TEMP.md"
    return plan_file


@pytest.fixture
def mock_archive_structure(tmp_path):
    """Fixture providing mock archive directory structure."""
    archive_dir = tmp_path / "mock-archive"
    create_mock_archive(archive_dir)
    return archive_dir


@pytest.fixture
def temp_archive_dir(tmp_path):
    """Fixture providing temporary archive directory."""
    archive_dir = tmp_path / "temp-archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    (archive_dir / "subplans").mkdir(exist_ok=True)
    (archive_dir / "execution").mkdir(exist_ok=True)
    return archive_dir


