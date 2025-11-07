#!/usr/bin/env python3
"""
Validate Python Imports - Quality Gate Script

Validates that all Python files in specified directories can be imported successfully.
Used as a quality gate to catch syntax errors and import issues early.

Usage:
    python scripts/validate_imports.py business app core
    python scripts/validate_imports.py business/services
    
Exit codes:
    0 - All imports successful
    1 - One or more imports failed
"""

import sys
import subprocess
from pathlib import Path


def validate_imports(files):
    """
    Test that all Python files can be imported.
    
    Args:
        files: List of file paths to validate
        
    Returns:
        bool: True if all imports successful, False otherwise
    """
    failed = []
    
    for f in files:
        # Skip __init__.py and test files
        if f.name == '__init__.py' or f.name.startswith('test_'):
            continue
            
        # Convert file path to module path
        module_path = str(f.relative_to('.')).replace('/', '.').replace('.py', '')
        
        try:
            result = subprocess.run(
                [sys.executable, '-c', f'import {module_path}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                print(f'✓ {module_path}')
            else:
                print(f'✗ {module_path} - IMPORT FAILED')
                if result.stderr:
                    print(f'  Error: {result.stderr[:200]}')
                failed.append(module_path)
                
        except subprocess.TimeoutExpired:
            print(f'✗ {module_path} - TIMEOUT')
            failed.append(module_path)
        except Exception as e:
            print(f'✗ {module_path} - ERROR: {e}')
            failed.append(module_path)
    
    return len(failed) == 0, failed


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/validate_imports.py <directory1> [directory2] ...")
        print("Example: python scripts/validate_imports.py business app core")
        sys.exit(1)
    
    directories = sys.argv[1:]
    all_files = []
    
    # Collect all Python files from specified directories
    for dir_path in directories:
        path = Path(dir_path)
        if not path.exists():
            print(f"⚠️  Directory not found: {dir_path}")
            continue
            
        if path.is_file() and path.suffix == '.py':
            all_files.append(path)
        else:
            py_files = list(path.rglob('*.py'))
            all_files.extend(py_files)
    
    if not all_files:
        print("❌ No Python files found")
        sys.exit(1)
    
    print(f"Validating {len(all_files)} Python files...\n")
    
    # Validate imports
    success, failed = validate_imports(all_files)
    
    print(f"\n{'='*60}")
    if success:
        print(f"✅ All {len(all_files)} files import successfully")
        sys.exit(0)
    else:
        print(f"❌ {len(failed)} files failed to import:")
        for module in failed:
            print(f"  - {module}")
        sys.exit(1)


if __name__ == '__main__':
    main()

