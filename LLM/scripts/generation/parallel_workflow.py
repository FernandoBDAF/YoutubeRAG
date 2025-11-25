#!/usr/bin/env python3
"""
Parallel Workflow Module

Provides parallel workflow support for generate_prompt.py, including:
- Parallel discovery prompt generation
- parallel.json detection and validation
- Parallel execution menu
- Dependency graph visualization

Created: 2025-11-13
Achievement: 2.1 - generate_prompt.py Enhanced with Parallel Support
"""

import json
from pathlib import Path
from typing import Dict, Optional, Tuple


def generate_parallel_upgrade_prompt(plan_dir: Path) -> str:
    """
    Generate parallel discovery prompt for a PLAN.

    Uses ParallelPromptBuilder from Achievement 1.1 to generate a comprehensive
    prompt that helps users identify parallelization opportunities across the
    entire plan (Level 3: cross-priority analysis).

    Args:
        plan_dir: Path to plan directory (containing PLAN_*.md file)

    Returns:
        Formatted prompt string with independence checklist and schema template

    Example:
        >>> plan_dir = Path("work-space/plans/MY-PLAN")
        >>> prompt = generate_parallel_upgrade_prompt(plan_dir)
        >>> print(prompt)  # Shows formatted discovery prompt
    """
    from LLM.scripts.generation.parallel_prompt_builder import ParallelPromptBuilder
    from LLM.scripts.generation.plan_parser import PlanParser

    # Find PLAN file in directory
    plan_files = list(plan_dir.glob("PLAN_*.md"))
    if not plan_files:
        raise FileNotFoundError(f"No PLAN_*.md file found in {plan_dir}")
    plan_file = plan_files[0]

    # Parse PLAN to get data
    parser = PlanParser()
    plan_data = parser.parse_plan_file(plan_file)

    # Build discovery prompt (use level 3 for whole-plan analysis)
    builder = ParallelPromptBuilder()
    return builder.build_discovery_prompt(plan_path=plan_file, level=3, plan_data=plan_data)


def detect_parallel_json(plan_path: Path) -> Optional[Path]:
    """
    Detect parallel.json in plan directory (supports multiple filename patterns).

    Checks for:
    1. parallel.json (standard name)
    2. PARALLEL-EXECUTION-ANALYSIS.json (alternative name)
    3. parallel-execution.json (alternative name)
    4. parallel_analysis.json (alternative name)

    Args:
        plan_path: Path to plan directory

    Returns:
        Path to parallel.json if exists, None otherwise

    Example:
        >>> plan_path = Path("work-space/plans/MY-PLAN")
        >>> parallel_json = detect_parallel_json(plan_path)
        >>> if parallel_json:
        ...     print(f"Found: {parallel_json}")
    """
    # Try standard name first
    parallel_json = plan_path / "parallel.json"
    if parallel_json.exists():
        return parallel_json

    # Try alternative names
    alternatives = [
        "PARALLEL-EXECUTION-ANALYSIS.json",
        "parallel-execution.json",
        "parallel_analysis.json",
    ]

    for alt_name in alternatives:
        alt_path = plan_path / alt_name
        if alt_path.exists():
            return alt_path

    return None


def validate_and_load_parallel_json(parallel_json_path: Path) -> Optional[Dict]:
    """
    Validate and load parallel.json.

    Uses validate_parallel_json from Achievement 1.3 to ensure file is valid
    before loading. Shows clear error messages if validation fails.

    Args:
        parallel_json_path: Path to parallel.json file

    Returns:
        Loaded JSON data if valid, None if invalid

    Example:
        >>> parallel_json = Path("work-space/plans/MY-PLAN/parallel.json")
        >>> data = validate_and_load_parallel_json(parallel_json)
        >>> if data:
        ...     print(f"Level: {data['parallelization_level']}")
    """
    from LLM.scripts.validation.validate_parallel_json import validate_parallel_json

    result = validate_parallel_json(parallel_json_path)
    if not result.valid:
        print(f"\n❌ Invalid parallel.json: {parallel_json_path}")
        for error in result.errors:
            print(f"  - {error}")
        print("\n💡 Fix: Regenerate with --parallel-upgrade or fix errors manually")
        return None

    with open(parallel_json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def detect_and_validate_parallel_json(plan_path: Path) -> Tuple[Optional[Path], Optional[Dict]]:
    """
    Detect and validate parallel.json in one call.

    Convenience function that combines detection and validation.

    Args:
        plan_path: Path to plan directory

    Returns:
        Tuple of (parallel_json_path, parallel_data)
        Both None if file doesn't exist or is invalid

    Example:
        >>> plan_path = Path("work-space/plans/MY-PLAN")
        >>> parallel_json, parallel_data = detect_and_validate_parallel_json(plan_path)
        >>> if parallel_data:
        ...     print(f"Achievements: {len(parallel_data['achievements'])}")
    """
    parallel_json = detect_parallel_json(plan_path)
    if not parallel_json:
        return None, None

    parallel_data = validate_and_load_parallel_json(parallel_json)
    return parallel_json, parallel_data


def get_parallel_menu_state(parallel_data: Dict, plan_path: Path) -> Dict:
    """
    Get comprehensive state for parallel menu display.

    Uses filesystem-first detection via get_parallel_status.py.

    Args:
        parallel_data: Loaded parallel.json data
        plan_path: Path to plan directory

    Returns:
        Dict with:
        - progress: {complete, total, percentage, remaining}
        - next_available: List of achievements ready to start
        - parallel_opportunities: Groups of parallelizable achievements
        - last_completed: Most recent completed achievement
        - recommended_action: What user should do next
        - status_map: Filesystem-based status for all achievements

    Example:
        >>> state = get_parallel_menu_state(parallel_data, plan_path)
        >>> print(f"Progress: {state['progress']['percentage']}%")
    """
    from LLM.scripts.validation.get_parallel_status import get_parallel_status

    achievements = parallel_data.get("achievements", [])

    # Get filesystem-based status
    parallel_json = plan_path / "parallel.json"
    status_map = get_parallel_status(parallel_json) if parallel_json.exists() else {}

    # Calculate progress
    complete = sum(1 for s in status_map.values() if s == "complete")
    total = len(status_map)
    remaining = total - complete
    percentage = int((complete / total * 100)) if total > 0 else 0

    # Find next available (not_started with all deps met)
    next_available = []
    for ach in achievements:
        ach_id = ach.get("achievement_id")
        if status_map.get(ach_id) == "not_started":
            # Check if all dependencies are complete
            deps = ach.get("dependencies", [])
            all_deps_met = all(status_map.get(dep) == "complete" for dep in deps)
            if all_deps_met:
                next_available.append(ach)

    # Find parallel opportunities
    parallel_opportunities = find_parallel_opportunities(next_available, achievements)

    # Find last completed
    last_completed = None
    for ach in reversed(achievements):
        ach_id = ach.get("achievement_id")
        if status_map.get(ach_id) == "complete":
            last_completed = ach
            break

    # Detect placeholder SUBPLANs
    # Check ALL achievements with "subplan_created" status, not just next_available
    placeholder_subplans = []
    for ach in achievements:
        ach_id = ach.get("achievement_id")
        # Only check achievements with SUBPLANs
        if status_map.get(ach_id) == "subplan_created":
            subplan_num = ach_id.replace(".", "")
            subplan_files = list(plan_path.glob(f"subplans/SUBPLAN_*_{subplan_num}.md"))

            if subplan_files:
                # Check if it's a placeholder
                try:
                    with open(subplan_files[0], "r", encoding="utf-8") as f:
                        content = f.read()
                        if "[TO BE FILLED" in content:  # Match both "[TO BE FILLED]" and "[TO BE FILLED:"
                            placeholder_subplans.append(ach)
                except Exception:
                    pass

    # Determine recommended action
    recommended = get_recommended_action_from_state(
        next_available, parallel_opportunities, status_map, plan_path
    )

    return {
        "progress": {
            "complete": complete,
            "total": total,
            "percentage": percentage,
            "remaining": remaining,
        },
        "next_available": next_available,
        "parallel_opportunities": parallel_opportunities,
        "last_completed": last_completed,
        "recommended_action": recommended,
        "status_map": status_map,
        "placeholder_subplans": placeholder_subplans,
    }


def find_parallel_opportunities(next_available: list, all_achievements: list) -> list:
    """
    Find groups of achievements that can run in parallel.

    Since all next_available achievements have their dependencies met,
    they can all potentially run in parallel. Returns them as a single group.

    Args:
        next_available: List of achievements ready to start
        all_achievements: All achievements in the plan

    Returns:
        List with single parallel group (or empty if < 2 achievements)

    Example:
        >>> opportunities = find_parallel_opportunities(next_avail, all_achs)
        >>> if opportunities:
        ...     opp = opportunities[0]
        ...     print(f"{opp['count']} achievements, {opp['time_savings_percent']}% savings")
    """
    if len(next_available) < 2:
        return []

    # All next_available achievements can run in parallel
    # (their dependencies are met, so no blocking)
    sequential_time = sum(a.get("estimated_hours", 0) for a in next_available)
    parallel_time = max(a.get("estimated_hours", 0) for a in next_available)
    time_savings = int((1 - parallel_time / sequential_time) * 100) if sequential_time > 0 else 0

    return [
        {
            "achievements": next_available,
            "count": len(next_available),
            "sequential_hours": sequential_time,
            "parallel_hours": parallel_time,
            "time_savings_percent": time_savings,
        }
    ]


def get_recommended_action_from_state(
    next_available: list, parallel_opportunities: list, status_map: Dict, plan_path: Path
) -> Dict:
    """
    Determine recommended next action based on current state.

    Args:
        next_available: List of achievements ready to start
        parallel_opportunities: Groups of parallelizable achievements
        status_map: Filesystem-based status map
        plan_path: Path to plan directory

    Returns:
        Dict with type, message, and optional details

    Example:
        >>> action = get_recommended_action_from_state(next_avail, opps, status, path)
        >>> print(action['message'])
    """
    if not next_available:
        return {"type": "complete", "message": "All achievements complete! 🎉"}

    # Check if SUBPLANs exist for next available
    missing_subplans = []
    for ach in next_available:
        ach_id = ach.get("achievement_id")
        subplan_num = ach_id.replace(".", "")

        # Check if SUBPLAN file exists
        subplan_files = list(plan_path.glob(f"subplans/SUBPLAN_*_{subplan_num}.md"))
        if not subplan_files:
            missing_subplans.append(ach)

    if missing_subplans:
        if parallel_opportunities:
            # Multiple achievements ready, can batch create
            opp = parallel_opportunities[0]
            return {
                "type": "batch_subplan",
                "message": f"Batch create SUBPLANs for {opp['count']} achievements (option 1)",
                "details": f"Then batch create EXECUTIONs and execute in parallel",
                "time_savings": f"{opp['time_savings_percent']}% time savings",
            }
        else:
            # Single achievement ready
            ach = next_available[0]
            return {
                "type": "create_subplan",
                "achievement_id": ach.get("achievement_id"),
                "message": f"Create SUBPLAN for {ach.get('achievement_id')}",
            }

    # SUBPLANs exist, check EXECUTIONs
    missing_executions = []
    for ach in next_available:
        ach_id = ach.get("achievement_id")
        exec_num = ach_id.replace(".", "")

        # Check if EXECUTION file exists
        exec_files = list(plan_path.glob(f"execution/EXECUTION_TASK_*_{exec_num}_01.md"))
        if not exec_files:
            missing_executions.append(ach)

    if missing_executions:
        if parallel_opportunities:
            opp = parallel_opportunities[0]
            return {
                "type": "batch_execution",
                "message": f"Batch create EXECUTIONs for {opp['count']} achievements (option 2)",
                "details": "Then execute in parallel",
            }
        else:
            ach = next_available[0]
            return {
                "type": "create_execution",
                "achievement_id": ach.get("achievement_id"),
                "message": f"Create EXECUTION for {ach.get('achievement_id')}",
            }

    # Everything ready, can execute
    if parallel_opportunities:
        opp = parallel_opportunities[0]
        return {
            "type": "execute_parallel",
            "message": f"Execute {opp['count']} achievements in parallel (option 3)",
            "time_savings": f"{opp['time_savings_percent']}% time savings",
        }
    else:
        ach = next_available[0]
        return {
            "type": "execute",
            "achievement_id": ach.get("achievement_id"),
            "message": f"Execute {ach.get('achievement_id')}",
        }


def show_parallel_menu(parallel_data: Dict, plan_name: str, plan_path: Path = None) -> str:
    """
    Show parallel execution menu with state context.

    Displays interactive menu with comprehensive state information and options
    for parallel workflow management.

    Args:
        parallel_data: Loaded parallel.json data
        plan_name: Name of the plan
        plan_path: Path to plan directory (optional, enables state display)

    Returns:
        Selected option ('1'-'6' if state available, '1'-'5' otherwise)

    Example:
        >>> data = {"parallelization_level": "level_1", "achievements": [...]}
        >>> choice = show_parallel_menu(data, "MY-PLAN", Path("work-space/plans/MY-PLAN"))
        >>> print(f"User selected: {choice}")
    """
    print("\n" + "=" * 80)
    print("🔀 Parallel Execution Menu")
    print("=" * 80)
    print(f"Plan: {plan_name}")
    print(f"Parallelization Level: {parallel_data.get('parallelization_level', 'unknown')}")
    print(f"Total Achievements: {len(parallel_data.get('achievements', []))}")
    print()

    # Get and display current state if plan_path provided
    state = None
    if plan_path:
        try:
            state = get_parallel_menu_state(parallel_data, plan_path)

            # Progress
            prog = state["progress"]
            print(f"📊 CURRENT STATE:")
            print(
                f"   Progress: {prog['complete']}/{prog['total']} complete ({prog['percentage']}%)"
            )
            print(f"   Remaining: {prog['remaining']} achievements")

            if state["last_completed"]:
                last = state["last_completed"]
                print(f"   Last completed: {last.get('achievement_id')} ({last.get('title')})")
            print()

            # Next available
            next_avail = state["next_available"]
            if next_avail:
                print(f"🎯 NEXT AVAILABLE:")
                for ach in next_avail[:3]:  # Show top 3
                    ach_id = ach.get("achievement_id")
                    title = ach.get("title")
                    status = state["status_map"].get(ach_id, "unknown")
                    print(f"   {ach_id}: {title} ({status})")
                if len(next_avail) > 3:
                    print(f"   ... and {len(next_avail) - 3} more")

                # Show dependency status
                first = next_avail[0]
                deps = first.get("dependencies", [])
                if deps:
                    all_met = all(state["status_map"].get(d) == "complete" for d in deps)
                    if all_met:
                        print(f"   Dependencies: All met ✅")
                    else:
                        print(f"   Dependencies: Some incomplete ⚠️")

                # Show SUBPLAN/EXECUTION status
                ach_id = first.get("achievement_id")
                subplan_num = ach_id.replace(".", "")
                has_subplan = len(list(plan_path.glob(f"subplans/SUBPLAN_*_{subplan_num}.md"))) > 0
                has_execution = (
                    len(list(plan_path.glob(f"execution/EXECUTION_TASK_*_{subplan_num}_01.md"))) > 0
                )

                if not has_subplan:
                    print(f"   Status: Ready to start - no SUBPLANs exist yet")
                elif not has_execution:
                    print(f"   Status: SUBPLANs exist - need EXECUTIONs")
                else:
                    print(f"   Status: Ready to execute")

                print()

            # Parallel opportunities
            opportunities = state["parallel_opportunities"]
            if opportunities:
                print(f"🔀 PARALLEL OPPORTUNITY:")
                # Show single merged group
                opp = opportunities[0]
                count = opp["count"]
                seq_time = opp["sequential_hours"]
                par_time = opp["parallel_hours"]
                savings = opp["time_savings_percent"]

                print(f"   {count} achievements can run in parallel NOW:")
                for ach in opp["achievements"][:6]:  # Show up to 6
                    ach_id = ach.get("achievement_id")
                    title = ach.get("title")
                    print(f"   - {ach_id}: {title}")
                if len(opp["achievements"]) > 6:
                    print(f"   ... and {len(opp['achievements']) - 6} more")

                print(f"   ")
                print(f"   Estimated time: {seq_time}h sequential → {par_time}h parallel")
                print(f"   Time savings: {savings}%")
                print()

            # Recommended action
            recommended = state["recommended_action"]
            if recommended:
                print(f"💡 RECOMMENDED ACTION:")
                print(f"   {recommended['message']}")
                if recommended.get("details"):
                    print(f"   {recommended['details']}")
                if recommended.get("time_savings"):
                    print(f"   {recommended['time_savings']}")
                print()
        except Exception as e:
            # If state detection fails, continue without it
            print(f"⚠️  Could not load state: {e}")
            print()

    # Options
    print("Options:")

    # Customize option 1 text based on state
    if state and state["next_available"]:
        from LLM.scripts.generation.batch_subplan import calculate_dependency_level

        next_avail = state["next_available"]
        first_ach = next_avail[0]
        ach_id = first_ach.get("achievement_id")

        # Calculate dependency level
        memo = {}
        level = calculate_dependency_level(ach_id, parallel_data.get("achievements", []), memo)

        # Show achievement IDs
        ach_ids = [a.get("achievement_id") for a in next_avail[:2]]
        ach_str = ", ".join(ach_ids)
        if len(next_avail) > 2:
            ach_str += f", +{len(next_avail)-2} more"

        print(f"  1. Batch Create SUBPLANs (level {level}: {ach_str})")
    else:
        print("  1. Batch Create SUBPLANs (for same level)")

    print("  2. Batch Create EXECUTIONs (for same level)")
    print("  3. Run Parallel Executions (multi-executor)")
    print("  4. View Dependency Graph")

    # Add option to generate prompt for next available
    option_num = 5
    if state and state["next_available"]:
        ach_id = state["next_available"][0].get("achievement_id")
        print(f"  {option_num}. Generate prompt for next available ({ach_id})")
        option_num += 1

    # Add option to fill placeholder SUBPLANs if detected
    if state and state.get("placeholder_subplans"):
        count = len(state["placeholder_subplans"])
        print(f"  {option_num}. Generate prompt to FILL {count} placeholder SUBPLANs")
        option_num += 1

    print(f"  {option_num}. Back to Main Menu")
    max_option = str(option_num)

    print()
    choice = input(f"Select option (1-{max_option}): ").strip()
    return choice


def handle_parallel_menu_selection(
    choice: str, parallel_data: Dict, plan_name: str, plan_path: Path
):
    """
    Handle parallel menu selection with state awareness.

    Routes user selection to appropriate handler. Uses filesystem-based state
    detection to provide context-aware responses.

    Args:
        choice: Selected option ('1'-'6')
        parallel_data: Loaded parallel.json data
        plan_name: Name of the plan
        plan_path: Path to plan directory

    Example:
        >>> data = {"achievements": [...]}
        >>> handle_parallel_menu_selection('4', data, "MY-PLAN", plan_path)
        # Shows dependency graph
    """
    # Get current state for context-aware handling
    try:
        state = get_parallel_menu_state(parallel_data, plan_path)
    except Exception:
        state = None

    if choice == "1":
        # Batch SUBPLAN creation (state-aware)
        if not state or not state["next_available"]:
            print("❌ No achievements available for batch creation")
            return

        from LLM.scripts.generation.batch_subplan import (
            batch_create_subplans,
            calculate_dependency_level,
            detect_missing_subplans,
            show_batch_preview,
            confirm_batch_creation,
        )

        print("\n🔀 Batch SUBPLAN Creation")
        print("=" * 80)

        # Use next_available from state
        next_avail = state["next_available"]

        # Calculate dependency level for first achievement
        first_ach = next_avail[0]
        ach_id = first_ach.get("achievement_id")
        memo = {}
        level = calculate_dependency_level(ach_id, parallel_data.get("achievements", []), memo)

        print(f"Target: Level {level} achievements")
        ach_ids = [a.get("achievement_id") for a in next_avail[:6]]
        ach_str = ", ".join(ach_ids)
        if len(next_avail) > 6:
            ach_str += f", +{len(next_avail)-6} more"
        print(f"Achievements: {ach_str}")
        print()

        # Detect missing SUBPLANs
        missing = detect_missing_subplans(plan_path, next_avail)

        if not missing:
            print(f"✅ All SUBPLANs already exist for level {level} achievements")
            return

        # Show preview
        show_batch_preview(missing, plan_name, level)

        # Confirm
        if not confirm_batch_creation(missing):
            print("❌ Batch creation cancelled")
            return

        # Create SUBPLANs (pass achievements, skip confirmation - already done above)
        result = batch_create_subplans(
            plan_path, dry_run=False, achievements=next_avail, skip_confirmation=True
        )
        print("\n" + "=" * 80)
        print(result)
        print("=" * 80)

        # Offer to generate fill prompt if SUBPLANs were created
        if result.created:
            print("\n💡 NEXT STEP: Fill placeholder content")
            print()
            response = (
                input("Would you like to generate a prompt to fill these SUBPLANs? (y/N): ")
                .strip()
                .lower()
            )

            if response in ["y", "yes"]:
                from LLM.scripts.generation.batch_subplan_fill import generate_batch_fill_prompt

                achievement_ids = [a.get("achievement_id") for a in next_avail]

                try:
                    prompt = generate_batch_fill_prompt(plan_path, achievement_ids)

                    print("\n✅ Prompt generated!")
                    print()

                    # Try to copy to clipboard
                    try:
                        import pyperclip

                        pyperclip.copy(prompt)
                        print("📋 Copied to clipboard!")
                        print()
                        print("💡 Paste the prompt into your LLM to generate SUBPLAN content.")
                    except ImportError:
                        # pyperclip not available, save to file instead
                        output_file = plan_path / f"BATCH_FILL_PROMPT_{plan_name}.txt"
                        with open(output_file, "w", encoding="utf-8") as f:
                            f.write(prompt)
                        print(f"📄 Saved to: {output_file}")
                        print()
                        print("💡 Use this file to generate SUBPLAN content with your LLM.")
                except Exception as e:
                    print(f"❌ Error generating prompt: {e}")

    elif choice == "2":
        # Batch EXECUTION creation (Achievement 2.3)
        from LLM.scripts.generation.batch_execution import (
            batch_create_executions,
            validate_subplan_prerequisites,
            detect_missing_executions,
            show_batch_preview,
            confirm_batch_creation,
        )
        from LLM.scripts.generation.batch_subplan import filter_by_dependency_level

        print("\n🔀 Batch EXECUTION Creation")
        print("=" * 80)

        # Filter level 0 achievements (no dependencies)
        achievements = parallel_data.get("achievements", [])
        level_0 = filter_by_dependency_level(achievements, level=0)

        if not level_0:
            print("❌ No achievements at level 0 (no dependencies)")
            return

        # Validate SUBPLANs exist (NEW - prerequisite check)
        valid, missing_subplans = validate_subplan_prerequisites(plan_path, level_0)

        if missing_subplans:
            print(f"⚠️  Missing {len(missing_subplans)} SUBPLANs (create these first):")
            for ach_id in missing_subplans:
                print(f"  - Achievement {ach_id}")
            print("\n💡 Tip: Use option 1 to batch create SUBPLANs first")
            return

        # Detect missing EXECUTION_TASKs
        missing = detect_missing_executions(plan_path, valid)

        if not missing:
            print("✅ All EXECUTION_TASKs already exist for level 0 achievements")
            return

        # Show preview
        show_batch_preview(missing, plan_name)

        # Confirm
        if not confirm_batch_creation(missing):
            print("❌ Batch creation cancelled")
            return

        # Create EXECUTION_TASKs
        result = batch_create_executions(plan_path, dry_run=False)
        print("\n" + "=" * 80)
        print(result)
        print("=" * 80)
    elif choice == "3":
        print("\n⏳ Parallel execution coordination (Coming in Achievement 3.1)")
        print("\nThis feature will allow you to:")
        print("  - View achievements at current level")
        print("  - Select specific achievements to execute")
        print("  - Generate execution prompts for selected achievements")
        print("  - Track parallel execution progress")
        print("\nPlanned for Achievement 3.1: Interactive Menu Polished")
    elif choice == "4":
        show_dependency_graph(parallel_data)
    elif choice == "5":
        # Generate prompt for next available (if state available)
        if state and state["next_available"]:
            next_ach = state["next_available"][0]
            ach_id = next_ach.get("achievement_id")

            print(f"\n✨ Generating prompt for Achievement {ach_id}")
            print("=" * 80)

            # Determine what type of prompt to generate
            subplan_num = ach_id.replace(".", "")
            has_subplan = len(list(plan_path.glob(f"subplans/SUBPLAN_*_{subplan_num}.md"))) > 0
            has_execution = (
                len(list(plan_path.glob(f"execution/EXECUTION_TASK_*_{subplan_num}_01.md"))) > 0
            )

            if not has_subplan:
                print(f"\n💡 Next step: Create SUBPLAN for Achievement {ach_id}")
                print(f"\nCommand to run:")
                print(f"  python LLM/scripts/generation/generate_prompt.py {ach_id} @{plan_name}")
            elif not has_execution:
                print(f"\n💡 Next step: Create EXECUTION for Achievement {ach_id}")
                print(f"\nCommand to run:")
                print(
                    f"  python LLM/scripts/generation/generate_execution_prompt.py design @{plan_name}"
                )
            else:
                print(f"\n💡 Next step: Execute Achievement {ach_id}")
                print(f"\nCommand to run:")
                print(
                    f"  python LLM/scripts/generation/generate_execution_prompt.py continue @EXECUTION_TASK_{plan_name}_{subplan_num}_01.md"
                )

            print("=" * 80)
        else:
            return  # Back to main menu
    elif choice == "6":
        # Check if this is "Fill placeholder SUBPLANs" or "Back to main menu"
        if state and state.get("placeholder_subplans"):
            # Generate prompt to fill placeholder SUBPLANs
            from LLM.scripts.generation.batch_subplan_fill import generate_batch_fill_prompt

            placeholders = state["placeholder_subplans"]
            achievement_ids = [p.get("achievement_id") for p in placeholders]

            print(f"\n✨ Generating prompt to fill {len(placeholders)} placeholder SUBPLANs")
            print("=" * 80)

            try:
                prompt = generate_batch_fill_prompt(plan_path, achievement_ids)

                print("\n✅ Prompt generated!")
                print()

                # Try to copy to clipboard
                try:
                    import pyperclip

                    pyperclip.copy(prompt)
                    print("📋 Copied to clipboard!")
                    print()
                    print("💡 Paste the prompt into your LLM to generate SUBPLAN content.")
                except ImportError:
                    # pyperclip not available, save to file instead
                    output_file = plan_path / f"BATCH_FILL_PROMPT_{plan_name}.txt"
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(prompt)
                    print(f"📄 Saved to: {output_file}")
                    print()
                    print("💡 Use this file to generate SUBPLAN content with your LLM.")

                print("=" * 80)
            except Exception as e:
                print(f"❌ Error generating prompt: {e}")
        else:
            return  # Back to main menu
    elif choice == "7":
        return  # Back to main menu (when option 6 is fill prompt)
    else:
        # Determine max option based on state
        max_option = "7"
        if state:
            if state.get("placeholder_subplans") and state.get("next_available"):
                max_option = "7"
            elif state.get("next_available"):
                max_option = "6"
            else:
                max_option = "5"
        else:
            max_option = "5"
        print(f"\n❌ Invalid option. Please select 1-{max_option}.")


def show_dependency_graph(parallel_data: Dict):
    """
    Show simple ASCII dependency graph.

    Displays achievement dependencies in a simple text format.

    Args:
        parallel_data: Loaded parallel.json data

    Example:
        >>> data = {
        ...     "achievements": [
        ...         {"achievement_id": "1.1", "dependencies": []},
        ...         {"achievement_id": "1.2", "dependencies": ["1.1"]}
        ...     ]
        ... }
        >>> show_dependency_graph(data)
        📊 Dependency Graph:
        ================================================================================
          1.1 → no dependencies
          1.2 → depends on: 1.1
        ================================================================================
    """
    print("\n📊 Dependency Graph:")
    print("=" * 80)

    achievements = parallel_data.get("achievements", [])
    for ach in achievements:
        ach_id = ach.get("achievement_id", "?")
        deps = ach.get("dependencies", [])

        if deps:
            deps_str = ", ".join(deps)
            print(f"  {ach_id} → depends on: {deps_str}")
        else:
            print(f"  {ach_id} → no dependencies")

    print("=" * 80)
