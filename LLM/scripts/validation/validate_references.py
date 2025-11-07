#!/usr/bin/env python3
"""
Validate markdown references in documentation.

Scans all markdown files for references to other files and checks if they exist.
Useful for catching broken links after refactoring or moving files.

Usage:
    python scripts/validate_references.py
    python scripts/validate_references.py --ignore-archives
    python scripts/validate_references.py --verbose
    python scripts/validate_references.py --json > report.json
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


# ANSI color codes for terminal output
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"


def find_markdown_files(root_dir: Path, ignore_archives: bool = False) -> List[Path]:
    """Find all markdown files in the project."""
    markdown_files = []

    for md_file in root_dir.rglob("*.md"):
        # Skip archives if requested
        if ignore_archives and "/archive/" in str(md_file):
            continue

        # Skip hidden directories
        if any(part.startswith(".") for part in md_file.parts):
            continue

        markdown_files.append(md_file)

    return sorted(markdown_files)


def extract_references(file_path: Path, root_dir: Path) -> List[Tuple[str, int, str]]:
    """
    Extract markdown link references from a file.

    Returns: List of (reference_path, line_number, link_text) tuples
    """
    references = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                # Match markdown links: [text](path) or [text](path#section)
                matches = re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", line)

                for match in matches:
                    link_text = match.group(1)
                    ref_path = match.group(2)

                    # Skip external URLs
                    if ref_path.startswith(("http://", "https://", "mailto:", "#")):
                        continue

                    # Remove section anchors for file validation
                    ref_file = ref_path.split("#")[0]

                    # Skip empty refs
                    if not ref_file:
                        continue

                    references.append((ref_file, line_num, link_text))

    except Exception as e:
        print(f"{Colors.YELLOW}Warning: Could not read {file_path}: {e}{Colors.END}")

    return references


def validate_reference(ref_path: str, source_file: Path, root_dir: Path) -> Tuple[bool, Path]:
    """
    Validate that a reference path exists.

    Returns: (is_valid, resolved_path)
    """
    # Handle absolute paths from root
    if ref_path.startswith("/"):
        target = root_dir / ref_path[1:]
    else:
        # Relative to source file's directory
        target = (source_file.parent / ref_path).resolve()

    return (target.exists(), target)


def scan_project(root_dir: Path, ignore_archives: bool = False, verbose: bool = False) -> Dict:
    """
    Scan entire project for broken references.

    Returns: Dictionary with findings
    """
    findings = {
        "total_files": 0,
        "total_references": 0,
        "broken_references": [],
        "files_with_issues": set(),
        "valid_references": 0,
    }

    markdown_files = find_markdown_files(root_dir, ignore_archives)
    findings["total_files"] = len(markdown_files)

    if verbose:
        print(f"{Colors.BLUE}Scanning {findings['total_files']} markdown files...{Colors.END}\n")

    for md_file in markdown_files:
        references = extract_references(md_file, root_dir)

        for ref_path, line_num, link_text in references:
            findings["total_references"] += 1

            is_valid, resolved_path = validate_reference(ref_path, md_file, root_dir)

            if is_valid:
                findings["valid_references"] += 1
                if verbose:
                    print(f"  ✓ {ref_path}")
            else:
                findings["broken_references"].append(
                    {
                        "file": str(md_file.relative_to(root_dir)),
                        "line": line_num,
                        "reference": ref_path,
                        "link_text": link_text,
                        "resolved_path": str(resolved_path),
                    }
                )
                findings["files_with_issues"].add(str(md_file.relative_to(root_dir)))

    return findings


def generate_report(findings: Dict, output_json: bool = False) -> str:
    """Generate human-readable or JSON report."""

    if output_json:
        # Convert set to list for JSON serialization
        findings["files_with_issues"] = list(findings["files_with_issues"])
        return json.dumps(findings, indent=2)

    # Human-readable report
    lines = []
    lines.append(f"\n{Colors.BOLD}═══════════════════════════════════════════════════{Colors.END}")
    lines.append(f"{Colors.BOLD}   MARKDOWN REFERENCE VALIDATION REPORT{Colors.END}")
    lines.append(f"{Colors.BOLD}═══════════════════════════════════════════════════{Colors.END}\n")

    lines.append(f"📊 {Colors.BOLD}Statistics:{Colors.END}")
    lines.append(f"   Files Scanned: {findings['total_files']}")
    lines.append(f"   Total References: {findings['total_references']}")
    lines.append(f"   Valid References: {findings['valid_references']} {Colors.GREEN}✓{Colors.END}")
    lines.append(
        f"   Broken References: {len(findings['broken_references'])} {Colors.RED if findings['broken_references'] else Colors.GREEN}{'✗' if findings['broken_references'] else '✓'}{Colors.END}"
    )
    lines.append(f"   Files with Issues: {len(findings['files_with_issues'])}\n")

    if findings["broken_references"]:
        lines.append(f"{Colors.RED}{Colors.BOLD}⚠️  BROKEN REFERENCES FOUND:{Colors.END}\n")

        for issue in findings["broken_references"]:
            lines.append(
                f"{Colors.RED}✗{Colors.END} {Colors.BOLD}{issue['file']}{Colors.END}:{issue['line']}"
            )
            lines.append(f"  Link Text: \"{issue['link_text']}\"")
            lines.append(f"  Reference: {issue['reference']}")
            lines.append(f"  Resolved To: {issue['resolved_path']}")
            lines.append(f"  {Colors.YELLOW}Action: Fix reference or remove link{Colors.END}\n")

        lines.append(
            f"\n{Colors.RED}{Colors.BOLD}STATUS: FAILED{Colors.END} - Please fix broken references above"
        )
    else:
        lines.append(
            f"{Colors.GREEN}{Colors.BOLD}✅ SUCCESS{Colors.END} - All references are valid!\n"
        )

    lines.append(
        f"\n{Colors.BOLD}═══════════════════════════════════════════════════{Colors.END}\n"
    )

    return "\n".join(lines)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate markdown references in project documentation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/validate_references.py
  python scripts/validate_references.py --ignore-archives
  python scripts/validate_references.py --verbose
  python scripts/validate_references.py --json > report.json
  
Exit Codes:
  0 = All references valid
  1 = Broken references found
  2 = Script error
        """,
    )

    parser.add_argument(
        "--ignore-archives",
        action="store_true",
        help="Skip files in documentation/archive/ directories",
    )

    parser.add_argument(
        "--verbose", action="store_true", help="Show all references checked (not just broken ones)"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON instead of human-readable format",
    )

    args = parser.parse_args()

    try:
        # Get project root (4 levels up from scripts/)
        script_dir = Path(__file__).parent
        root_dir = script_dir.parent

        # Scan project
        findings = scan_project(root_dir, args.ignore_archives, args.verbose)

        # Generate report
        report = generate_report(findings, args.json)
        print(report)

        # Exit with appropriate code
        if findings["broken_references"]:
            sys.exit(1)
        else:
            sys.exit(0)

    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.END}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
