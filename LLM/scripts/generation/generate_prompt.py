#!/usr/bin/env python3
"""
LLM Prompt Generator - Automated high-quality prompt generation

Generates ideal prompts for LLM development methodology with:
- Context boundaries (read only what's needed)
- Required steps (SUBPLAN, EXECUTION_TASK, etc.)
- Validation enforcement (scripts that will run)
- Size limits (200-line EXECUTION_TASK)
- DO NOTs (anti-patterns)
- External verification

Usage:
    python LLM/scripts/generate_prompt.py @PLAN_FEATURE.md --next
    python LLM/scripts/generate_prompt.py @PLAN_FEATURE.md --achievement 1.1
    python LLM/scripts/generate_prompt.py @PLAN_FEATURE.md --next --clipboard
"""

import argparse
import re
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Achievement:
    """Achievement data structure."""
    number: str  # "0.1", "1.1"
    title: str
    goal: str
    effort: str  # "2-3 hours"
    priority: str
    section_lines: int  # Lines in achievement section


def parse_plan_file(plan_path: Path) -> dict:
    """Extract structured data from PLAN file."""
    with open(plan_path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
    
    # Extract feature name
    feature_name = plan_path.stem.replace('PLAN_', '')
    
    # Parse achievements
    achievements = []
    for i, line in enumerate(lines):
        if match := re.match(r'\*\*Achievement (\d+\.\d+)\*\*:(.+)', line):
            ach_num = match.group(1)
            ach_title = match.group(2).strip()
            
            # Estimate section size (until next achievement or section)
            section_lines = estimate_section_size(lines, i)
            
            achievements.append(Achievement(
                number=ach_num,
                title=ach_title,
                goal="",  # Would need more parsing
                effort="",  # Would need more parsing
                priority="",  # Would need more parsing
                section_lines=section_lines
            ))
    
    # Find archive location
    archive_location = find_archive_location(lines)
    
    # Calculate handoff section size
    handoff_lines = calculate_handoff_size(lines)
    
    return {
        'feature_name': feature_name,
        'achievements': achievements,
        'archive_location': archive_location,
        'total_plan_lines': len(lines),
        'handoff_lines': handoff_lines
    }


def find_next_achievement_from_plan(plan_content: str) -> Optional[str]:
    """Find next achievement from PLAN's 'What's Next' section."""
    # Look for patterns like:
    # - "Next: Achievement X.Y"
    # - "⏳ Next: Achievement X.Y"
    # - "What's Next: Achievement X.Y"
    # - "Next: Achievement X.Y (Description)"
    patterns = [
        r'(?:Next|What\'s Next)[:\s]+Achievement\s+(\d+\.\d+)',
        r'⏳\s*Next[:\s]+Achievement\s+(\d+\.\d+)',
        r'Next[:\s]+Achievement\s+(\d+\.\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, plan_content, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1)
    
    return None


def find_next_achievement_from_archive(feature_name: str, achievements: List[Achievement], archive_location: str) -> Optional[Achievement]:
    """Find first achievement without archived SUBPLAN."""
    # Convert archive location string to Path
    archive_path = Path(archive_location)
    
    # Check if archive location exists
    if not archive_path.exists():
        return None
    
    # Check subplans directory
    archive_subplans = archive_path / "subplans"
    if not archive_subplans.exists():
        return None
    
    # Find first achievement without archived SUBPLAN
    for ach in achievements:
        subplan_num = ach.number.replace('.', '')
        subplan_file = archive_subplans / f"SUBPLAN_{feature_name}_{subplan_num}.md"
        if not subplan_file.exists():
            return ach
    
    return None


def find_next_achievement_from_root(feature_name: str, achievements: List[Achievement]) -> Optional[Achievement]:
    """Find first achievement without SUBPLAN file in root directory."""
    for ach in achievements:
        subplan_num = ach.number.replace('.', '')
        subplan_file = Path(f"SUBPLAN_{feature_name}_{subplan_num}.md")
        if not subplan_file.exists():
            return ach
    return None


def find_next_achievement_hybrid(plan_path: Path, feature_name: str, achievements: List[Achievement], archive_location: str) -> Optional[Achievement]:
    """Find next achievement using multiple methods (hybrid approach)."""
    
    # Method 1: Parse PLAN "What's Next" (most reliable)
    try:
        with open(plan_path, 'r', encoding='utf-8') as f:
            plan_content = f.read()
        
        next_num = find_next_achievement_from_plan(plan_content)
        if next_num:
            next_ach = next((a for a in achievements if a.number == next_num), None)
            if next_ach:
                return next_ach
    except Exception:
        # If parsing fails, continue to fallback methods
        pass
    
    # Method 2: Check archive directory (handles immediate archiving)
    next_ach = find_next_achievement_from_archive(feature_name, achievements, archive_location)
    if next_ach:
        return next_ach
    
    # Method 3: Check root directory (backward compatible for non-archived plans)
    return find_next_achievement_from_root(feature_name, achievements)


def detect_validation_scripts() -> List[str]:
    """Detect which validation scripts exist (check new domain structure)."""
    validation_dir = Path('LLM/scripts/validation')
    
    validation_scripts = [
        'validate_achievement_completion.py',
        'validate_execution_start.py',
        'validate_mid_plan.py',
        'check_plan_size.py',
        'check_execution_task_size.py',
        'validate_registration.py',
        'validate_references.py',
        'validate_plan_compliance.py'
    ]
    
    existing = []
    for script in validation_scripts:
        # Check new domain structure first (validation/)
        if (validation_dir / script).exists():
            existing.append(script)
        # Fallback to old structure (LLM/scripts/) for backward compatibility
        elif (Path('LLM/scripts') / script).exists():
            existing.append(script)
    
    return existing


def estimate_section_size(lines: List[str], start_idx: int) -> int:
    """Estimate lines in achievement section."""
    count = 0
    for i in range(start_idx, len(lines)):
        if i > start_idx and lines[i].startswith('**Achievement'):
            break
        if lines[i].startswith('## '):
            break
        count += 1
    return min(count, 100)  # Cap estimate at 100


def find_archive_location(lines: List[str]) -> str:
    """Find archive location from PLAN."""
    for line in lines:
        if 'Archive Location' in line and './' in line:
            match = re.search(r'\./([a-z0-9-]+)/', line)
            if match:
                return f"./{match.group(1)}/"
    return "./feature-archive/"


def calculate_handoff_size(lines: List[str]) -> int:
    """Calculate lines in Current Status & Handoff section."""
    in_section = False
    count = 0
    for line in lines:
        if 'Current Status & Handoff' in line:
            in_section = True
        elif in_section and line.startswith('##'):
            break
        elif in_section:
            count += 1
    return count if count > 0 else 30  # Default estimate


# PROMPT TEMPLATES

ACHIEVEMENT_EXECUTION_TEMPLATE = """Execute Achievement {achievement_num} in @PLAN_{feature}.md following strict methodology.

═══════════════════════════════════════════════════════════════════════

CONTEXT BOUNDARIES (Read ONLY These):
✅ @PLAN_{feature}.md - Achievement {achievement_num} section only ({achievement_lines} lines)
✅ @PLAN_{feature}.md - "Current Status & Handoff" section ({handoff_lines} lines)

❌ DO NOT READ: Full PLAN ({plan_total_lines} lines), other achievements, archived work

CONTEXT BUDGET: {context_budget} lines maximum

═══════════════════════════════════════════════════════════════════════

ACHIEVEMENT {achievement_num}: {achievement_title}

Goal: {achievement_goal}
Estimated: {estimated_hours}

═══════════════════════════════════════════════════════════════════════

REQUIRED STEPS (No Shortcuts):

Step 1: Create SUBPLAN (MANDATORY)
- File: SUBPLAN_{feature}_{subplan_num}.md
- Size: 200-400 lines
- Must include: Objective, Deliverables, Approach, Tests, Expected Results

Step 2: Create EXECUTION_TASK (MANDATORY)
- File: EXECUTION_TASK_{feature}_{subplan_num}_01.md
- Size: 100-200 lines maximum
- Start with: Objective, Approach, Iteration Log (Iteration 1)

Step 3: Execute Work
[Implement the achievement deliverables]

Step 4: Verify Deliverables (MANDATORY)
Run verification:
  ls -1 [each deliverable path]

If any missing: FIX before continuing

Step 5: Complete EXECUTION_TASK
- Update: Iteration Log with "Complete"
- Add: Learning Summary
- Verify: <200 lines (run: wc -l EXECUTION_TASK_*.md)

Step 6: Archive Immediately
- Move: SUBPLAN → {archive_location}subplans/
- Move: EXECUTION_TASK → {archive_location}execution/
- Update: PLAN Subplan Tracking

Step 7: Update PLAN Statistics
- Calculate from EXECUTION_TASK (not imagination)

═══════════════════════════════════════════════════════════════════════

VALIDATION ENFORCEMENT:

{validation_scripts}

═══════════════════════════════════════════════════════════════════════

DO NOT:
❌ Skip SUBPLAN ("it's simple" - NO, all work needs SUBPLANs)
❌ Skip EXECUTION_TASK ("just document in PLAN" - NO)
❌ Mark complete without verifying files exist (run: ls -1)
❌ Read full PLAN (read Achievement {achievement_num} only)
❌ Claim hours without EXECUTION_TASK to verify from

REMEMBER:
✓ SUBPLAN + EXECUTION_TASK for EVERY achievement
✓ Verify deliverables exist (ls -1)
✓ Archive immediately on completion
✓ Statistics from EXECUTION_TASK data
✓ Stay within context budget ({context_budget} lines)

═══════════════════════════════════════════════════════════════════════

EXTERNAL VERIFICATION:

After completing, I will verify:
1. SUBPLAN file exists and complete?
2. EXECUTION_TASK file exists with learnings?
3. All deliverables exist? (filesystem check)
4. Statistics accurate?
5. EXECUTION_TASK <200 lines?

Do not proceed until verification passes.

═══════════════════════════════════════════════════════════════════════

Now beginning Achievement {achievement_num} execution:

Creating SUBPLAN_{feature}_{subplan_num}.md...
"""


def fill_template(template: str, context: dict, validation_scripts: List[str]) -> str:
    """Fill template with actual values."""
    
    # Format validation scripts section
    if validation_scripts:
        scripts_text = "After Step 4, these scripts will run:\n"
        for script in validation_scripts:
            scripts_text += f"✓ {script}\n"
        scripts_text += "\nIf issues found: BLOCKS with error + fix prompt"
    else:
        scripts_text = "(Validation scripts being built in this PLAN)"
    
    return template.format(
        feature=context['feature_name'],
        achievement_num=context['achievement_num'],
        achievement_title=context['achievement_title'],
        achievement_goal=context.get('achievement_goal', 'See PLAN for details'),
        estimated_hours=context.get('estimated_hours', 'See PLAN'),
        achievement_lines=context['achievement_lines'],
        handoff_lines=context['handoff_lines'],
        plan_total_lines=context['plan_total_lines'],
        context_budget=context['context_budget'],
        subplan_num=context['subplan_num'],
        archive_location=context['archive_location'],
        validation_scripts=scripts_text
    )


def generate_prompt(plan_path: Path, achievement_num: Optional[str] = None) -> str:
    """Generate prompt for PLAN."""
    
    # Parse PLAN
    plan_data = parse_plan_file(plan_path)
    
    # Find next achievement
    if achievement_num:
        next_ach = next((a for a in plan_data['achievements'] if a.number == achievement_num), None)
    else:
        next_ach = find_next_achievement_hybrid(
            plan_path,
            plan_data['feature_name'],
            plan_data['achievements'],
            plan_data['archive_location']
        )
    
    if not next_ach:
        return "❌ No achievements found or all complete!"
    
    # Detect validation scripts
    validation_scripts = detect_validation_scripts()
    
    # Build context
    context = {
        'feature_name': plan_data['feature_name'],
        'achievement_num': next_ach.number,
        'achievement_title': next_ach.title,
        'achievement_lines': next_ach.section_lines,
        'handoff_lines': plan_data['handoff_lines'],
        'plan_total_lines': plan_data['total_plan_lines'],
        'context_budget': next_ach.section_lines + plan_data['handoff_lines'],
        'subplan_num': next_ach.number.replace('.', ''),
        'archive_location': plan_data['archive_location']
    }
    
    # Fill template
    prompt = fill_template(ACHIEVEMENT_EXECUTION_TEMPLATE, context, validation_scripts)
    
    return prompt


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate high-quality LLM prompts for methodology execution',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python LLM/scripts/generate_prompt.py @PLAN_FEATURE.md --next
  python LLM/scripts/generate_prompt.py @PLAN_FEATURE.md --achievement 1.1
  python LLM/scripts/generate_prompt.py @PLAN_FEATURE.md --next --clipboard

Exit Codes:
  0 = Success
  1 = Error (file not found, parsing failed, etc.)
        """
    )
    
    parser.add_argument(
        'plan_file',
        help='PLAN file (e.g., @PLAN_FEATURE.md or PLAN_FEATURE.md)'
    )
    
    parser.add_argument(
        '--next',
        action='store_true',
        help='Generate prompt for next achievement (auto-detect)'
    )
    
    parser.add_argument(
        '--achievement',
        help='Specific achievement number (e.g., 1.1)'
    )
    
    parser.add_argument(
        '--clipboard',
        action='store_true',
        help='Copy prompt to clipboard'
    )
    
    args = parser.parse_args()
    
    try:
        # Clean file path
        plan_path = Path(args.plan_file.replace('@', ''))
        
        if not plan_path.exists():
            print(f"❌ Error: File not found: {plan_path}")
            sys.exit(1)
        
        # Generate prompt
        if args.next or args.achievement:
            prompt = generate_prompt(plan_path, args.achievement)
        else:
            print("❌ Error: Use --next or --achievement N.N")
            parser.print_help()
            sys.exit(1)
        
        # Output
        print(prompt)
        
        # Clipboard support
        if args.clipboard:
            try:
                import pyperclip
                pyperclip.copy(prompt)
                print("\n✅ Prompt copied to clipboard!")
            except ImportError:
                print("\n⚠️  Install pyperclip for clipboard support: pip install pyperclip")
        
        sys.exit(0)
    
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

