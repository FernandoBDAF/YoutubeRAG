"""
Batch Rollback Module

Provides git-based rollback functionality for batch operations, enabling safe
recovery from errors during batch SUBPLAN or EXECUTION creation.

Usage:
    from LLM.scripts.generation.batch_rollback import (
        create_rollback_point,
        rollback_to_point,
        cleanup_partial_batch
    )
    
    # Create rollback point before batch operation
    commit_sha = create_rollback_point(plan_path)
    
    try:
        # Perform batch operation
        ...
    except Exception:
        # Rollback on error
        if commit_sha:
            rollback_to_point(commit_sha, plan_path)
        else:
            cleanup_partial_batch(created_files)
"""

import subprocess
from pathlib import Path
from typing import List, Optional


def create_rollback_point(
    plan_path: Path
) -> Optional[str]:
    """
    Create git commit before batch operation.
    
    This function captures the current git state so that batch operations can be
    rolled back if they fail. It does NOT create a new commit, but rather returns
    the current HEAD commit SHA for reference.
    
    Args:
        plan_path: Path to PLAN directory or file
    
    Returns:
        Commit SHA for rollback, or None if git unavailable
    
    Example:
        >>> commit_sha = create_rollback_point(plan_path)
        >>> if commit_sha:
        ...     print(f"Rollback point: {commit_sha[:8]}")
        ... else:
        ...     print("Git not available, manual cleanup required")
    """
    # Get workspace root (3 levels up from plan directory)
    if plan_path.is_file():
        workspace_root = plan_path.parent.parent.parent
    else:
        workspace_root = plan_path.parent.parent
    
    try:
        # Check if git is available and get current HEAD
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=workspace_root,
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
        commit_sha = result.stdout.strip()
        
        # Verify we got a valid SHA (40 hex characters)
        if len(commit_sha) == 40 and all(c in '0123456789abcdef' for c in commit_sha):
            return commit_sha
        else:
            return None
            
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return None


def rollback_to_point(
    commit_sha: str,
    plan_path: Path
) -> bool:
    """
    Rollback to previous commit.
    
    WARNING: This performs a hard reset, which will discard all uncommitted changes
    in the working directory. Use with caution.
    
    Args:
        commit_sha: Commit SHA to rollback to
        plan_path: Path to PLAN directory or file
    
    Returns:
        True if rollback successful, False otherwise
    
    Example:
        >>> success = rollback_to_point(commit_sha, plan_path)
        >>> if success:
        ...     print("Rollback successful")
        ... else:
        ...     print("Rollback failed, manual cleanup required")
    """
    # Get workspace root
    if plan_path.is_file():
        workspace_root = plan_path.parent.parent.parent
    else:
        workspace_root = plan_path.parent.parent
    
    try:
        # Verify commit exists
        verify_result = subprocess.run(
            ["git", "cat-file", "-e", commit_sha],
            cwd=workspace_root,
            capture_output=True,
            timeout=5
        )
        
        if verify_result.returncode != 0:
            print(f"⚠️  Commit {commit_sha[:8]} not found in git history")
            return False
        
        # Perform hard reset
        subprocess.run(
            ["git", "reset", "--hard", commit_sha],
            cwd=workspace_root,
            check=True,
            timeout=10
        )
        
        print(f"✅ Rolled back to commit {commit_sha[:8]}")
        return True
        
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"❌ Rollback failed: {e}")
        return False


def cleanup_partial_batch(
    created_files: List[Path]
) -> None:
    """
    Clean up partially created SUBPLANs on error.
    
    This is a fallback cleanup method when git rollback is not available.
    It manually deletes files that were created during a failed batch operation.
    
    Args:
        created_files: List of files created before error
    
    Example:
        >>> created_files = [Path("subplans/SUBPLAN_X_11.md"), Path("subplans/SUBPLAN_X_12.md")]
        >>> cleanup_partial_batch(created_files)
        Cleaned up 2 files
    """
    if not created_files:
        print("ℹ️  No files to clean up")
        return
    
    cleaned_count = 0
    failed_count = 0
    
    for file_path in created_files:
        try:
            if file_path.exists():
                file_path.unlink()
                cleaned_count += 1
                print(f"  🗑️  Deleted: {file_path.name}")
        except Exception as e:
            failed_count += 1
            print(f"  ⚠️  Failed to delete {file_path.name}: {e}")
    
    print(f"\n✅ Cleaned up {cleaned_count} files")
    if failed_count > 0:
        print(f"⚠️  Failed to clean up {failed_count} files (manual cleanup required)")


def get_git_status(plan_path: Path) -> Optional[str]:
    """
    Get current git status for the workspace.
    
    Args:
        plan_path: Path to PLAN directory or file
    
    Returns:
        Git status output, or None if git unavailable
    
    Example:
        >>> status = get_git_status(plan_path)
        >>> if status:
        ...     print(f"Git status:\\n{status}")
    """
    # Get workspace root
    if plan_path.is_file():
        workspace_root = plan_path.parent.parent.parent
    else:
        workspace_root = plan_path.parent.parent
    
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=workspace_root,
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return None


def is_git_available(plan_path: Path) -> bool:
    """
    Check if git is available in the workspace.
    
    Args:
        plan_path: Path to PLAN directory or file
    
    Returns:
        True if git is available, False otherwise
    
    Example:
        >>> if is_git_available(plan_path):
        ...     print("Git rollback available")
        ... else:
        ...     print("Manual cleanup will be required")
    """
    # Get workspace root
    if plan_path.is_file():
        workspace_root = plan_path.parent.parent.parent
    else:
        workspace_root = plan_path.parent.parent
    
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=workspace_root,
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


