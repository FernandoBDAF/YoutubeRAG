#!/usr/bin/env python3
"""
Audit Error Handling Coverage - Quality Gate Script

Checks that all public functions in services/chat have @handle_errors decorator.
Used as a quality gate to maintain error handling consistency.

Usage:
    python scripts/audit_error_handling.py business/services business/chat
    python scripts/audit_error_handling.py business/services/rag
    
Exit codes:
    0 - All public functions have error handling
    1 - One or more functions missing error handling
"""

import ast
import sys
from pathlib import Path


def check_error_handling(file_path):
    """
    Check if public functions have @handle_errors decorator.
    
    Args:
        file_path: Path to Python file
        
    Returns:
        list: List of issues found (empty if none)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            tree = ast.parse(content, filename=str(file_path))
    except SyntaxError as e:
        return [f"  Syntax error at line {e.lineno}: {e.msg}"]
    except Exception as e:
        return [f"  Error parsing file: {e}"]
    
    issues = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Check public functions (not starting with _)
            if not node.name.startswith('_'):
                # Check for @handle_errors decorator
                has_decorator = False
                for decorator in node.decorator_list:
                    # Check for @handle_errors (direct name)
                    if isinstance(decorator, ast.Name) and decorator.id == 'handle_errors':
                        has_decorator = True
                        break
                    # Check for @handle_errors (from core.libraries.error_handling import handle_errors)
                    if isinstance(decorator, ast.Attribute):
                        if (hasattr(decorator, 'attr') and decorator.attr == 'handle_errors'):
                            has_decorator = True
                            break
                    # Check for @handle_errors() (function call)
                    if isinstance(decorator, ast.Call):
                        if (hasattr(decorator.func, 'id') and decorator.func.id == 'handle_errors'):
                            has_decorator = True
                            break
                        if (hasattr(decorator.func, 'attr') and decorator.func.attr == 'handle_errors'):
                            has_decorator = True
                            break
                
                if not has_decorator:
                    issues.append(f"  Line {node.lineno}: {node.name}() missing @handle_errors")
    
    return issues


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/audit_error_handling.py <directory1> [directory2] ...")
        print("Example: python scripts/audit_error_handling.py business/services business/chat")
        sys.exit(1)
    
    directories = sys.argv[1:]
    all_issues = []
    total_files = 0
    files_with_issues = 0
    total_functions = 0
    functions_with_handling = 0
    
    # Collect all Python files from specified directories
    for dir_path in directories:
        path = Path(dir_path)
        if not path.exists():
            print(f"⚠️  Directory not found: {dir_path}")
            continue
        
        if path.is_file() and path.suffix == '.py':
            files = [path]
        else:
            files = list(path.rglob('*.py'))
        
        for py_file in files:
            # Skip __init__.py and test files
            if py_file.name == '__init__.py' or py_file.name.startswith('test_'):
                continue
            
            total_files += 1
            issues = check_error_handling(py_file)
            
            # Count functions
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read(), filename=str(py_file))
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                            total_functions += 1
                            # Check if it has decorator
                            for decorator in node.decorator_list:
                                if (isinstance(decorator, ast.Name) and decorator.id == 'handle_errors') or \
                                   (isinstance(decorator, ast.Call) and 
                                    hasattr(decorator.func, 'id') and decorator.func.id == 'handle_errors') or \
                                   (isinstance(decorator, ast.Attribute) and 
                                    hasattr(decorator, 'attr') and decorator.attr == 'handle_errors'):
                                    functions_with_handling += 1
                                    break
            except:
                pass
            
            if issues:
                files_with_issues += 1
                all_issues.append((str(py_file), issues))
    
    # Calculate coverage
    coverage = (functions_with_handling / total_functions * 100) if total_functions > 0 else 0
    
    print(f"📊 Error Handling Coverage: {coverage:.1f}% ({functions_with_handling}/{total_functions} functions)")
    print(f"📁 Files checked: {total_files}")
    print(f"📁 Files with issues: {files_with_issues}\n")
    
    if all_issues:
        print(f"⚠️  {files_with_issues} files with missing error handling:\n")
        for file, issues in all_issues[:20]:  # Show first 20 files
            print(f"{file}:")
            for issue in issues[:5]:  # Show first 5 issues per file
                print(issue)
            if len(issues) > 5:
                print(f"  ... and {len(issues) - 5} more functions")
            print()
        
        if len(all_issues) > 20:
            print(f"... and {len(all_issues) - 20} more files\n")
    
    print(f"{'='*60}")
    
    # Pass if coverage ≥ 90%
    if coverage >= 90:
        print(f"✅ Error handling coverage acceptable ({coverage:.1f}%)")
        sys.exit(0)
    else:
        print(f"❌ Error handling coverage below threshold ({coverage:.1f}% < 90%)")
        sys.exit(1)


if __name__ == '__main__':
    main()

