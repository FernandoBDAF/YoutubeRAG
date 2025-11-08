"""Mock archive structure fixtures for testing LLM scripts."""

from pathlib import Path


def create_mock_archive(archive_dir: Path):
    """Create mock archive directory structure.
    
    Args:
        archive_dir: Path to create archive structure at
    """
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    subplans_dir = archive_dir / "subplans"
    execution_dir = archive_dir / "execution"
    planning_dir = archive_dir / "planning"
    summary_dir = archive_dir / "summary"
    
    subplans_dir.mkdir(exist_ok=True)
    execution_dir.mkdir(exist_ok=True)
    planning_dir.mkdir(exist_ok=True)
    summary_dir.mkdir(exist_ok=True)
    
    # Create sample files
    (subplans_dir / "SUBPLAN_FEATURE_01.md").write_text("# SUBPLAN: Test\n\n**Status**: Complete\n")
    (subplans_dir / "SUBPLAN_FEATURE_02.md").write_text("# SUBPLAN: Test 2\n\n**Status**: Complete\n")
    
    (execution_dir / "EXECUTION_TASK_FEATURE_01_01.md").write_text("# EXECUTION_TASK: Test\n\n**Status**: Complete\n")
    (execution_dir / "EXECUTION_TASK_FEATURE_02_01.md").write_text("# EXECUTION_TASK: Test 2\n\n**Status**: Complete\n")


def get_archive_structure(archive_dir: Path) -> dict:
    """Get archive directory structure as dictionary.
    
    Args:
        archive_dir: Path to archive directory
        
    Returns:
        Dictionary with structure information
    """
    structure = {
        "subplans": [],
        "execution": [],
        "planning": [],
        "summary": [],
    }
    
    for subdir in ["subplans", "execution", "planning", "summary"]:
        subdir_path = archive_dir / subdir
        if subdir_path.exists():
            structure[subdir] = [f.name for f in subdir_path.iterdir() if f.is_file()]
    
    return structure


