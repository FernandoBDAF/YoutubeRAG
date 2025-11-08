"""Helper functions for testing LLM scripts."""

import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple


def run_script(script_path: Path, args: list = None, cwd: Optional[Path] = None) -> Tuple[int, str, str]:
    """Run a script and capture output.
    
    Args:
        script_path: Path to script to run
        args: List of arguments to pass to script
        cwd: Working directory for script execution
        
    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    if args is None:
        args = []
    
    cmd = [sys.executable, str(script_path)] + args
    
    result = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
    )
    
    return result.returncode, result.stdout, result.stderr


def assert_script_success(return_code: int, stdout: str = "", stderr: str = ""):
    """Assert that script execution was successful.
    
    Args:
        return_code: Script return code
        stdout: Script stdout
        stderr: Script stderr
        
    Raises:
        AssertionError: If script did not succeed
    """
    assert return_code == 0, f"Script failed with return code {return_code}. stderr: {stderr}"


def assert_script_failure(return_code: int, expected_code: int = 1):
    """Assert that script execution failed with expected code.
    
    Args:
        return_code: Script return code
        expected_code: Expected failure code
        
    Raises:
        AssertionError: If script did not fail as expected
    """
    assert return_code == expected_code, f"Script did not fail with expected code {expected_code}. Got {return_code}"


def get_script_output(return_code: int, stdout: str, stderr: str) -> str:
    """Get combined script output.
    
    Args:
        return_code: Script return code
        stdout: Script stdout
        stderr: Script stderr
        
    Returns:
        Combined output string
    """
    output = f"Return code: {return_code}\n"
    if stdout:
        output += f"STDOUT:\n{stdout}\n"
    if stderr:
        output += f"STDERR:\n{stderr}\n"
    return output


def create_temp_plan_file(tmp_path: Path, content: str, name: str = "PLAN_TEST.md") -> Path:
    """Create temporary PLAN file.
    
    Args:
        tmp_path: Temporary directory path
        content: PLAN file content
        name: PLAN file name
        
    Returns:
        Path to created PLAN file
    """
    plan_file = tmp_path / name
    plan_file.write_text(content)
    return plan_file


def create_temp_archive(tmp_path: Path, archive_name: str = "test-archive") -> Path:
    """Create temporary archive structure.
    
    Args:
        tmp_path: Temporary directory path
        archive_name: Archive directory name
        
    Returns:
        Path to created archive directory
    """
    archive_dir = tmp_path / archive_name
    archive_dir.mkdir(parents=True, exist_ok=True)
    (archive_dir / "subplans").mkdir(exist_ok=True)
    (archive_dir / "execution").mkdir(exist_ok=True)
    (archive_dir / "planning").mkdir(exist_ok=True)
    (archive_dir / "summary").mkdir(exist_ok=True)
    return archive_dir


