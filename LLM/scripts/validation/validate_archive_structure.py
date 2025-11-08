#!/usr/bin/env python3
"""
Validate archive structure compliance for PLAN documents.

Checks:
- Archive directory exists
- Subdirectories exist (subplans/, execution/)
- Archive location matches PLAN specification
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Optional, Tuple


def extract_archive_location(plan_path: Path) -> Optional[str]:
    """Extract archive location from PLAN file."""
    try:
        with open(plan_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Look for "Archive Location" section
        patterns = [
            r"\*\*Archive Location\*\*:\s*`([^`]+)`",
            r"Archive Location[:\s]+`([^`]+)`",
            r"Archive Location[:\s]+([^\n]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                # Normalize path
                if location.startswith("./"):
                    location = location[2:]
                if location.endswith("/"):
                    location = location[:-1]
                return location
        
    except Exception as e:
        print(f"❌ Error reading PLAN file: {e}", file=sys.stderr)
        return None


def validate_archive_structure(plan_path: Path) -> Tuple[bool, str]:
    """Validate archive structure compliance."""
    plan_path = Path(plan_path)
    
    if not plan_path.exists():
        return False, f"❌ PLAN file not found: {plan_path}"
    
    # Extract archive location from PLAN
    archive_location = extract_archive_location(plan_path)
    
    if not archive_location:
        return False, "❌ Archive location not found in PLAN. Add 'Archive Location' section to PLAN."
    
    # Convert to Path
    archive_path = Path(archive_location)
    
    # Check archive directory exists
    if not archive_path.exists():
        return False, (
            f"❌ Archive directory does not exist: {archive_location}\n"
            f"**Fix**: Create archive structure:\n"
            f"  mkdir -p {archive_location}/{{subplans,execution}}"
        )
    
    # Check subdirectories exist
    subplans_dir = archive_path / "subplans"
    execution_dir = archive_path / "execution"
    
    issues = []
    if not subplans_dir.exists():
        issues.append(f"Missing subplans/ directory: {subplans_dir}")
    if not execution_dir.exists():
        issues.append(f"Missing execution/ directory: {execution_dir}")
    
    if issues:
        error_msg = f"❌ Archive structure incomplete:\n"
        error_msg += f"  Archive Location: {archive_location}\n\n"
        error_msg += "**Missing Directories**:\n"
        for issue in issues:
            error_msg += f"  - {issue}\n"
        error_msg += f"\n**Fix**: Create missing directories:\n"
        error_msg += f"  mkdir -p {archive_location}/{{subplans,execution}}\n"
        return False, error_msg
    
    return True, f"✅ Archive structure validated: {archive_location}\n  - Directory exists\n  - subplans/ exists\n  - execution/ exists"


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate archive structure compliance for PLAN documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument("plan_file", help="PLAN file to validate (e.g., PLAN_FEATURE.md)")
    
    args = parser.parse_args()
    
    plan_path = Path(args.plan_file.replace("@", ""))
    
    is_valid, message = validate_archive_structure(plan_path)
    
    print(message)
    
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()


