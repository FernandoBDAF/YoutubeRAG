#!/usr/bin/env python3
"""
Validate PLAN document compliance with structured LLM development methodology.

Checks PLANs for template compliance, required sections, naming conventions,
and format adherence. Generates compliance report with scores and recommendations.

Usage:
    python scripts/validate_plan_compliance.py PLAN_FEATURE.md
    python scripts/validate_plan_compliance.py --all
    python scripts/validate_plan_compliance.py --json > report.json
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"


REQUIRED_SECTIONS = [
    "Context for LLM Execution",
    "Goal",
    "Problem Statement",
    "Success Criteria",
    "Scope Definition",
    "Desirable Achievements",
    "Subplan Tracking",
    "Current Status & Handoff",
]

V14_SECTIONS = [
    "GrammaPlan Consideration",
    "Summary Statistics",
    "Key Learnings",
    "Pre-Completion Review",
]

OPTIONAL_SECTIONS = [
    "Achievement Addition Log",
    "Related Plans",
]


def find_plan_files(root_dir: Path) -> List[Path]:
    """Find all PLAN files in project."""
    plans = []

    # Root directory PLANs
    for plan in root_dir.glob("PLAN_*.md"):
        plans.append(plan)

    # GrammaPlans
    for grammaplan in root_dir.glob("GRAMMAPLAN_*.md"):
        plans.append(grammaplan)

    return sorted(plans)


def extract_sections(file_path: Path) -> List[str]:
    """Extract all markdown ## sections from file."""
    sections = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("## "):
                    section_name = line[3:].strip()
                    # Remove emojis and extra markers
                    section_name = re.sub(r"[📋🎯📝🔄✅🔗⏱️📚🎓📦]", "", section_name).strip()
                    sections.append(section_name)
    except Exception as e:
        print(f"{Colors.YELLOW}Warning: Could not read {file_path}: {e}{Colors.END}")

    return sections


def check_naming_compliance(file_path: Path) -> Tuple[bool, str]:
    """Check if file follows naming convention."""
    name = file_path.name

    # Valid patterns
    if re.match(r"PLAN_[A-Z0-9-]+\.md$", name):
        return (True, "Valid PLAN name")
    if re.match(r"GRAMMAPLAN_[A-Z0-9-]+\.md$", name):
        return (True, "Valid GRAMMAPLAN name")

    return (False, f"Invalid name format: {name}")


def calculate_compliance_score(file_path: Path, sections: List[str]) -> Dict:
    """Calculate compliance score based on various criteria."""
    score = 0
    max_score = 100
    issues = []
    successes = []

    # Template Compliance (40 points)
    required_present = 0
    for required in REQUIRED_SECTIONS:
        if any(required.lower() in s.lower() for s in sections):
            required_present += 1
            successes.append(f"✓ Has '{required}' section")
        else:
            issues.append(f"✗ Missing '{required}' section (-5pts)")

    template_score = int((required_present / len(REQUIRED_SECTIONS)) * 40)
    score += template_score

    # V1.4 Features (20 points bonus, not penalized)
    v14_present = 0
    for v14_section in V14_SECTIONS:
        if any(v14_section.lower() in s.lower() for s in sections):
            v14_present += 1
            successes.append(f"✓ Has v1.4 feature: '{v14_section}'")

    v14_bonus = min(20, int((v14_present / len(V14_SECTIONS)) * 20))
    score += v14_bonus

    # Naming Compliance (20 points)
    naming_ok, naming_msg = check_naming_compliance(file_path)
    if naming_ok:
        score += 20
        successes.append(f"✓ {naming_msg}")
    else:
        issues.append(f"✗ {naming_msg} (-20pts)")

    # Related Plans Section (10 points)
    if any("related plans" in s.lower() for s in sections):
        score += 10
        successes.append("✓ Has 'Related Plans' section")
    else:
        issues.append("✗ Missing 'Related Plans' section (-10pts)")

    # Subplan Tracking (10 points)
    if any("subplan tracking" in s.lower() for s in sections):
        score += 10
        successes.append("✓ Has 'Subplan Tracking' section")
    else:
        issues.append("✗ Missing 'Subplan Tracking' section (-10pts)")

    return {
        "score": min(score, 100),  # Cap at 100
        "max_score": max_score,
        "issues": issues,
        "successes": successes,
        "template_score": template_score,
        "v14_bonus": v14_bonus,
        "sections_found": sections,
    }


def generate_report(results: List[Dict], output_json: bool = False) -> str:
    """Generate compliance report."""

    if output_json:
        return json.dumps(results, indent=2)

    # Human-readable report
    lines = []
    lines.append(f"\n{Colors.BOLD}═══════════════════════════════════════════════════{Colors.END}")
    lines.append(f"{Colors.BOLD}   PLAN COMPLIANCE VALIDATION REPORT{Colors.END}")
    lines.append(f"{Colors.BOLD}═══════════════════════════════════════════════════{Colors.END}\n")

    total_score = sum(r["data"]["score"] for r in results)
    avg_score = total_score / len(results) if results else 0

    lines.append(f"📊 {Colors.BOLD}Summary:{Colors.END}")
    lines.append(f"   PLANs Reviewed: {len(results)}")

    # Build compliance line with color
    compliance_color = (
        Colors.GREEN if avg_score >= 90 else Colors.YELLOW if avg_score >= 75 else Colors.RED
    )
    compliance_text = (
        "Excellent" if avg_score >= 90 else "Good" if avg_score >= 75 else "Needs Improvement"
    )
    lines.append(
        f"   Average Compliance: {avg_score:.0f}/100 {compliance_color}({compliance_text}){Colors.END}"
    )
    lines.append("")

    # Per-PLAN results
    for result in results:
        plan_name = result["file"]
        data = result["data"]
        score = data["score"]

        color = Colors.GREEN if score >= 90 else Colors.YELLOW if score >= 75 else Colors.RED
        lines.append(
            f"{color}{'✓' if score >= 75 else '✗'}{Colors.END} {Colors.BOLD}{plan_name}{Colors.END}: {score}/100"
        )

        if data["issues"]:
            for issue in data["issues"][:3]:  # Show top 3 issues
                lines.append(f"    {issue}")

        lines.append("")

    lines.append(f"{Colors.BOLD}═══════════════════════════════════════════════════{Colors.END}\n")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Validate PLAN compliance with methodology",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/validate_plan_compliance.py PLAN_FEATURE.md
  python scripts/validate_plan_compliance.py --all
  python scripts/validate_plan_compliance.py --json
  
Exit Codes:
  0 = All PLANs compliant (>75%)
  1 = Some PLANs non-compliant
  2 = Script error
        """,
    )

    parser.add_argument("plan_file", nargs="?", help="Specific PLAN file to validate")

    parser.add_argument("--all", action="store_true", help="Validate all PLANs in project")

    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    try:
        script_dir = Path(__file__).parent
        root_dir = script_dir.parent

        # Determine which PLANs to check
        plans_to_check = []

        if args.all:
            plans_to_check = find_plan_files(root_dir)
        elif args.plan_file:
            plan_path = root_dir / args.plan_file
            if not plan_path.exists():
                print(f"{Colors.RED}Error: File not found: {args.plan_file}{Colors.END}")
                sys.exit(2)
            plans_to_check = [plan_path]
        else:
            print("Error: Specify a PLAN file or use --all")
            parser.print_help()
            sys.exit(2)

        # Check each PLAN
        results = []
        for plan_file in plans_to_check:
            sections = extract_sections(plan_file)
            compliance_data = calculate_compliance_score(plan_file, sections)

            results.append({"file": plan_file.name, "data": compliance_data})

        # Generate report
        report = generate_report(results, args.json)
        print(report)

        # Exit code based on compliance
        if all(r["data"]["score"] >= 75 for r in results):
            sys.exit(0)
        else:
            sys.exit(1)

    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.END}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
