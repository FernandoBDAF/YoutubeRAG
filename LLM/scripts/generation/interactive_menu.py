#!/usr/bin/env python3
"""
Interactive Menu Module - Two-Stage Interactive Experience

═══════════════════════════════════════════════════════════════════════
PURPOSE
═══════════════════════════════════════════════════════════════════════

Provides two-stage interactive menu system for prompt generation workflow:
  Stage 1 (Pre-execution): Choose workflow before prompt generation
  Stage 2 (Post-generation): Handle generated prompt output

Extracted from generate_prompt.py (Achievement 2.1) to improve maintainability
and reduce main file complexity (~600 lines extracted).

═══════════════════════════════════════════════════════════════════════
ARCHITECTURE
═══════════════════════════════════════════════════════════════════════

Two-Stage Design:
  1. Pre-execution menu (prompt_interactive_menu):
     - Choose workflow (next/specific/view achievements)
     - Modifies sys.argv for main() re-parsing
     - Shows workflow context (SUBPLANs, EXECUTIONs detected)

  2. Post-generation menu (output_interactive_menu):
     - Handle prompt output (copy/view/save/execute)
     - Dynamic menu based on content (commands detected)
     - Feedback generation integration
     - Smart defaults (Enter = copy)

Key Features:
  • Context-aware menus (adapt to workflow state)
  • Command extraction (copy individual commands)
  • Feedback generation helper
  • Error handling with fallbacks
  • Recursive menu on invalid input

═══════════════════════════════════════════════════════════════════════
USAGE
═══════════════════════════════════════════════════════════════════════

from interactive_menu import InteractiveMenu

menu = InteractiveMenu()

# Pre-execution menu (Stage 1)
menu.show_pre_execution_menu()  # Modifies sys.argv, returns to main()

# Post-generation menu (Stage 2)
menu.show_post_generation_menu(
    prompt="Generated prompt text...",
    workflow_state="create_execution",
    command="python generate_execution_prompt.py ...",
    plan_path=Path("work-space/plans/FEATURE/PLAN_FEATURE.md"),
    achievement_num="1.1"
)

# Feedback generation helper
menu.generate_feedback_interactive(
    plan_path=Path("work-space/plans/FEATURE/PLAN_FEATURE.md"),
    achievement_num="1.1"
)

═══════════════════════════════════════════════════════════════════════
"""

import re
import sys
import subprocess
from pathlib import Path
from typing import Optional


class InteractiveMenu:
    """
    Two-stage interactive menu system for prompt generation workflow.

    Provides pre-execution and post-generation menus with context-aware
    options, command extraction, and feedback generation integration.

    Attributes:
        None (stateless class, all state passed as method arguments)

    Methods:
        show_pre_execution_menu(): Stage 1 - Choose workflow
        show_post_generation_menu(): Stage 2 - Handle output
        generate_feedback_interactive(): Helper for feedback generation
    """

    def __init__(self):
        """Initialize InteractiveMenu (stateless, no setup needed)."""
        pass

    def show_pre_execution_menu(self) -> None:
        """
        Interactive menu for workflow selection (PRE-EXECUTION).

        Achievement 0.3 feature - STAGE 1 of two-stage interactive experience.
        This is the "What would you like to do?" menu that appears BEFORE
        prompt generation, allowing users to choose their workflow.

        Two-Stage Interactive Design:
          Stage 1 (Pre): show_pre_execution_menu() - Choose workflow ← YOU ARE HERE
          Stage 2 (Post): show_post_generation_menu() - Handle output

        Menu Options:
        1. Generate next achievement (auto-detect) - DEFAULT
        2. Generate specific achievement (user chooses)
        3. View all available achievements
        4. Copy prompt to clipboard
        5. Exit

        Workflow Context Detection (Enhancement):
        - Detects latest SUBPLAN
        - Counts EXECUTION_TASK files
        - Shows helpful context before menu
        - Provides specific recommendations

        Context Display:
        - "SUBPLAN detected, no EXECUTION" → Suggest option 1
        - "EXECUTION_TASKs found: 8 files" → Tip for next step

        Flag Preservation:
        - Adds --interactive to sys.argv modifications
        - Ensures post-generation menu is triggered
        - Maintains interactive mode through workflow

        Used by: main() (when args.interactive is True, before arg parsing)
        Tested: Partially (integration tests in test_interactive_output_menu.py)

        Returns:
            None (modifies sys.argv and returns to main for re-parsing)

        Example:
            >>> # User runs: python generate_prompt.py @RESTORE --interactive
            >>> menu = InteractiveMenu()
            >>> menu.show_pre_execution_menu()
            # Shows menu, user chooses option 1
            # sys.argv becomes: ['generate_prompt.py', '@RESTORE', '--next', '--interactive']
            # Returns to main() for re-parsing
        """
        # Quick workflow detection to show context
        workflow_context = None
        if len(sys.argv) > 1:
            try:
                plan_file = sys.argv[1]
                # Quick path resolution
                if plan_file.startswith("@"):
                    shorthand = plan_file[1:]
                    if "/" not in shorthand and not shorthand.endswith(".md"):
                        # @folder format
                        plans_dir = Path("work-space/plans")
                        for folder in plans_dir.iterdir():
                            if folder.is_dir() and shorthand.upper() in folder.name.upper():
                                plan_files = list(folder.glob("PLAN_*.md"))
                                if plan_files:
                                    plan_path = plan_files[0]
                                    feature_name = folder.name

                                    # Quick workflow detection
                                    subplans_dir = folder / "subplans"
                                    execution_dir = folder / "execution"

                                    if subplans_dir.exists():
                                        subplan_files = sorted(
                                            list(subplans_dir.glob("SUBPLAN_*.md"))
                                        )
                                        if subplan_files:
                                            latest_subplan = subplan_files[-1]

                                            # Check if EXECUTION exists for this SUBPLAN
                                            if execution_dir.exists():
                                                # Extract subplan number (e.g., "02" from "SUBPLAN_FEATURE_02.md")
                                                match = re.search(
                                                    r"_(\d+)\.md$", latest_subplan.name
                                                )
                                                if match:
                                                    subplan_num = match.group(1)
                                                    # Look for any EXECUTION file starting with the pattern
                                                    exec_pattern = f"EXECUTION_TASK_{feature_name}_{subplan_num}_*"
                                                    exec_files = [
                                                        f
                                                        for f in execution_dir.iterdir()
                                                        if f.name.startswith(
                                                            f"EXECUTION_TASK_{feature_name}_{subplan_num}_"
                                                        )
                                                    ]

                                                    if not exec_files:
                                                        # SUBPLAN exists but no EXECUTION
                                                        workflow_context = {
                                                            "type": "needs_execution",
                                                            "subplan": latest_subplan.name,
                                                            "subplan_num": subplan_num,
                                                            "feature": feature_name,
                                                        }
                                                    else:
                                                        # EXECUTION exists - show helpful context
                                                        # Try to detect next achievement
                                                        next_ach = None
                                                        next_ach_title = None
                                                        try:
                                                            from LLM.scripts.generation.workflow_detector import (
                                                                WorkflowDetector,
                                                            )
                                                            from LLM.scripts.generation.plan_parser import (
                                                                PlanParser,
                                                            )

                                                            detector = WorkflowDetector()
                                                            parser = PlanParser()

                                                            plan_content = plan_path.read_text()
                                                            plan_data = parser.parse_plan_file(
                                                                plan_path
                                                            )

                                                            # Get archive location
                                                            archive_loc = (
                                                                parser.find_archive_location(
                                                                    plan_content.splitlines()
                                                                )
                                                            )

                                                            # Detect next achievement
                                                            next_result = detector.find_next_achievement_hybrid(
                                                                plan_path=plan_path,
                                                                feature_name=feature_name,
                                                                achievements=plan_data[
                                                                    "achievements"
                                                                ],
                                                                archive_location=archive_loc,
                                                            )

                                                            if next_result:
                                                                # next_result is an Achievement object with .number and .title attributes
                                                                next_ach = next_result.number
                                                                next_ach_title = next_result.title
                                                        except Exception as e:
                                                            # If detection fails, continue without next achievement info
                                                            # Silent failure - detection is optional
                                                            pass

                                                        workflow_context = {
                                                            "type": "has_execution",
                                                            "subplan": latest_subplan.name,
                                                            "subplan_num": subplan_num,
                                                            "feature": feature_name,
                                                            "exec_count": len(exec_files),
                                                            "next_achievement": next_ach,
                                                            "next_achievement_title": next_ach_title,
                                                        }
                                    break
            except Exception:
                # If detection fails, continue without context
                pass

        # Detect parallel.json (Achievement 2.1 integration)
        parallel_data = None
        parallel_json_path = None
        if len(sys.argv) > 1:
            try:
                from LLM.scripts.generation.path_resolution import resolve_plan_path
                from LLM.scripts.generation.parallel_workflow import (
                    detect_and_validate_parallel_json,
                    get_parallel_menu_state,
                )

                plan_file = sys.argv[1]
                plan_path = resolve_plan_path(plan_file, file_type="PLAN")

                parallel_json_path, parallel_data = detect_and_validate_parallel_json(
                    plan_path.parent
                )

                if parallel_data:
                    # Show parallel workflow indicator
                    plan_name = plan_path.stem.replace("PLAN_", "")

                    print("\n" + "=" * 70)
                    print("🔀 PARALLEL WORKFLOW DETECTED")
                    print("=" * 70)
                    print(f"Plan: {plan_name}")
                    print(
                        f"Parallelization Level: {parallel_data.get('parallelization_level', 'unknown')}"
                    )
                    print(f"Total Achievements: {len(parallel_data.get('achievements', []))}")

                    # Get state-aware information
                    state = get_parallel_menu_state(parallel_data, plan_path.parent)
                    progress = state.get("progress", {})
                    next_available = state.get("next_available", [])

                    print(
                        f"Progress: {progress.get('complete', 0)}/{progress.get('total', 0)} complete ({progress.get('percentage', 0)}%)"
                    )
                    print(f"Remaining: {progress.get('remaining', 0)} achievements")

                    # Show parallel opportunities
                    if next_available:
                        print(f"\n💡 PARALLELIZATION OPPORTUNITY:")
                        print(f"   {len(next_available)} achievements can run in parallel NOW")
                        ach_ids = [a.get("achievement_id", "?") for a in next_available[:5]]
                        print(f"   Achievements: {', '.join(ach_ids)}")
                        if len(next_available) > 5:
                            print(f"   ... and {len(next_available) - 5} more")
                        print(f"\n   → Use option 6 to access Parallel Execution Menu")

                    print("=" * 70)
            except Exception:
                # If parallel detection fails, continue without it
                pass

        print("\n" + "=" * 70)
        print("🎯 What would you like to do?")
        print("=" * 70)

        # Show workflow context if detected
        if workflow_context:
            if workflow_context["type"] == "needs_execution":
                print(f"\n💡 WORKFLOW CONTEXT:")
                print(f"   SUBPLAN detected: {workflow_context['subplan']}")
                print(f"   Status: No EXECUTION_TASK found")
                print(
                    f"   Suggestion: Create EXECUTION for achievement {workflow_context['subplan_num']}"
                )
                print(
                    f"\n   Recommended: Choose option 1 (auto-detect) or option 2 (specific achievement)"
                )
                print()
            elif workflow_context["type"] == "has_execution":
                print(f"\n💡 WORKFLOW CONTEXT:")
                print(f"   Latest SUBPLAN: {workflow_context['subplan']}")
                print(f"   EXECUTION_TASKs: {workflow_context['exec_count']} file(s) found")

                # Show next achievement if detected
                if workflow_context.get("next_achievement"):
                    next_ach = workflow_context["next_achievement"]
                    next_title = workflow_context.get("next_achievement_title", "")
                    print(f"   Next Achievement: {next_ach}")
                    if next_title:
                        print(f"   Title: {next_title}")
                    print(f"\n   → Option 1 will generate prompt for Achievement {next_ach}")
                else:
                    print(f"   Next Achievement: Unable to detect (all work may be complete)")
                    print(
                        f"\n   → Use option 1 to auto-detect or option 2 for specific achievement"
                    )
                print()

        print("\n1. Generate prompt for next achievement (auto-detect)")
        print("2. Generate prompt for specific achievement")
        print("3. View all available achievements")
        print("4. Copy prompt to clipboard")
        print("5. Run parallel discovery analysis")
        print("6. Access Parallel Execution Menu")
        print("7. Exit\n")

        choice = input("Enter choice (1-7, default 1): ").strip() or "1"

        if choice == "1":
            # Next achievement (default)
            if len(sys.argv) > 1:
                plan_file = sys.argv[1]
                sys.argv = [sys.argv[0], plan_file, "--next", "--interactive"]
            else:
                print("❌ Error: PLAN file required")
                sys.exit(1)
        elif choice == "2":
            # Specific achievement
            if len(sys.argv) > 1:
                plan_file = sys.argv[1]
                achievement = input("Enter achievement number (e.g., 1.1): ").strip()
                if achievement:
                    sys.argv = [
                        sys.argv[0],
                        plan_file,
                        "--achievement",
                        achievement,
                        "--interactive",
                    ]
                else:
                    print("❌ Invalid achievement number")
                    sys.exit(1)
            else:
                print("❌ Error: PLAN file required")
                sys.exit(1)
        elif choice == "3":
            # View achievements
            print("\n📋 Available achievements vary by PLAN")
            print("Use option 1 or 2 to generate prompts for specific achievements")
            sys.exit(0)
        elif choice == "4":
            # Copy to clipboard
            if len(sys.argv) > 1:
                plan_file = sys.argv[1]
                sys.argv = [sys.argv[0], plan_file, "--next", "--interactive"]
            else:
                print("❌ Error: PLAN file required")
                sys.exit(1)
        elif choice == "5":
            # Run parallel discovery analysis
            if len(sys.argv) > 1:
                plan_file = sys.argv[1]
                print("\n" + "=" * 70)
                print("🔀 Parallel Discovery Analysis")
                print("=" * 70)
                print("\nThis will analyze your PLAN for parallel execution opportunities.")
                print("It will generate a parallel.json file describing which achievements")
                print("can be executed in parallel.\n")

                # Extract plan name from file
                plan_name = plan_file.lstrip("@").replace("PLAN_", "").replace(".md", "")

                print("📋 Command to run:")
                print(f"\n  python LLM/scripts/generation/generate_prompt.py \\")
                print(f"      @PLAN_{plan_name}.md \\")
                print(f"      --parallel-upgrade\n")

                run_now = input("Run parallel discovery now? (y/N): ").strip().lower()

                if run_now == "y":
                    # Run parallel discovery
                    sys.argv = [sys.argv[0], plan_file, "--parallel-upgrade"]
                    return  # Will execute --parallel-upgrade
                else:
                    print("\n💡 TIP: Copy the command above and run it when ready.")
                    print("After generating parallel.json, you can use batch operations:")
                    print("  - Batch create SUBPLANs: generate_subplan_prompt.py --batch")
                    print("  - Batch create EXECUTIONs: generate_execution_prompt.py --batch")
                    sys.exit(0)
            else:
                print("❌ Error: PLAN file required")
                sys.exit(1)
        elif choice == "6":
            # Access Parallel Execution Menu
            if parallel_data and len(sys.argv) > 1:
                from LLM.scripts.generation.parallel_workflow import (
                    show_parallel_menu,
                    handle_parallel_menu_selection,
                )
                from LLM.scripts.generation.path_resolution import resolve_plan_path

                plan_file = sys.argv[1]
                plan_path = resolve_plan_path(plan_file, file_type="PLAN")
                plan_name = plan_path.stem.replace("PLAN_", "")

                print("\n🔀 Opening Parallel Execution Menu...")

                while True:
                    menu_choice = show_parallel_menu(parallel_data, plan_name, plan_path.parent)
                    handle_parallel_menu_selection(
                        menu_choice, parallel_data, plan_name, plan_path.parent
                    )
                    # Exit on "Back to Main Menu" (option 5 or 6 depending on state)
                    if menu_choice in ["5", "6"]:
                        break

                # Return to pre-execution menu
                print("\n↩️  Returning to main menu...")
                return self.show_pre_execution_menu()
            else:
                print("\n❌ No parallel.json found for this PLAN")
                print("💡 Use option 5 to run parallel discovery analysis first")
                print()
                return self.show_pre_execution_menu()
        elif choice == "7":
            # Exit
            sys.exit(0)
        else:
            print("❌ Invalid choice. Please try again.")
            return self.show_pre_execution_menu()

    def show_post_generation_menu(
        self,
        prompt: str,
        workflow_state: str,
        command: str = None,
        plan_path: Path = None,
        achievement_num: str = None,
    ) -> None:
        """
        Interactive menu for handling generated prompt output (POST-GENERATION).

        Achievement 0.3 feature - STAGE 2 of two-stage interactive experience.
        This is the "What to do with this prompt?" menu that appears AFTER
        prompt generation, complementing the pre-execution menu.

        Two-Stage Interactive Design:
          Stage 1 (Pre): show_pre_execution_menu() - Choose workflow
          Stage 2 (Post): show_post_generation_menu() - Handle output ← YOU ARE HERE

        Menu Options (dynamic based on content):
        - If commands detected: Offers to copy individual commands or full message
        - If no commands: Original behavior (copy full prompt)
        - Smart defaults: Enter = copy most useful content
        - Generate feedback: Create review prompt for completed achievement

        Smart Defaults:
        - Enter key = copy (most common action, 95% of users)
        - Execute option only shown if command available (context-aware)
        - Help adapts to workflow state

        Error Handling:
        - Invalid choice loops back to menu
        - Clipboard failure falls back to display
        - File save errors caught and reported

        Used by: main() (when args.interactive is True)
        Tested: Yes (18 tests in test_interactive_output_menu.py)

        Args:
            prompt: Generated prompt text
            workflow_state: Current workflow state (for context)
            command: Recommended command to execute (optional)
            plan_path: Path to PLAN file (for feedback generation)
            achievement_num: Achievement number (for feedback generation)

        Returns:
            None (exits after handling user choice)

        Example:
            >>> menu = InteractiveMenu()
            >>> menu.show_post_generation_menu(
            ...     prompt, "create_execution",
            ...     "python generate_execution_prompt.py ...",
            ...     plan_path, "1.1"
            ... )
            # Shows menu with command-specific options and feedback generation

            >>> menu.show_post_generation_menu(prompt, "next_achievement", None, plan_path, "1.1")
            # Shows standard menu with feedback option
        """
        # Import helper function from generate_prompt.py
        # Note: This creates a circular dependency, but it's acceptable for now
        # In a future refactor, copy_to_clipboard_safe should be moved to a utils module
        from LLM.scripts.generation import utils

        # Extract recommended commands from prompt
        command_pattern = r"\*\*Recommended Command\*\*:\s*\n\s*(.+?)(?:\n\n|\nOr use|$)"
        commands = re.findall(command_pattern, prompt, re.DOTALL)

        # Also check for "Or use ... directly:" pattern
        alt_command_pattern = r"Or use .+ directly:\s*\n\s*(.+?)(?:\n\n|$)"
        alt_commands = re.findall(alt_command_pattern, prompt, re.DOTALL)

        # Clean commands (remove leading spaces, take first line if multiline)
        cleaned_commands = []
        for cmd in commands + alt_commands:
            lines = [line.strip() for line in cmd.split("\n") if line.strip()]
            if lines:
                cleaned_commands.append(lines[0])

        print("\n" + "=" * 70)
        print("🎯 What would you like to do with this prompt?")
        print("=" * 70)

        # Build menu based on whether commands were detected
        if cleaned_commands:
            if len(cleaned_commands) == 1:
                print("\n1. Copy command to clipboard (default - press Enter)")
                print(f"   → {cleaned_commands[0]}")
                print("2. Copy full message")
                print("3. View full prompt")
                print("4. Save to file")
                if plan_path and achievement_num:
                    print("5. Generate feedback for this achievement")
                if command:
                    print(
                        f"{6 if plan_path and achievement_num else 5}. Execute recommended command"
                    )
                    print(f"{7 if plan_path and achievement_num else 6}. Get help")
                    print(f"{8 if plan_path and achievement_num else 7}. Exit")
                    max_choice = 8 if plan_path and achievement_num else 7
                else:
                    print(f"{6 if plan_path and achievement_num else 5}. Get help")
                    print(f"{7 if plan_path and achievement_num else 6}. Exit")
                    max_choice = 7 if plan_path and achievement_num else 6
            else:  # Multiple commands
                print("\n1. Copy first command to clipboard (default - press Enter)")
                print(f"   → {cleaned_commands[0]}")
                print("2. Copy second command to clipboard")
                print(f"   → {cleaned_commands[1]}")
                print("3. Copy full message")
                print("4. View full prompt")
                print("5. Save to file")
                if plan_path and achievement_num:
                    print("6. Generate feedback for this achievement")
                if command:
                    print(
                        f"{7 if plan_path and achievement_num else 6}. Execute recommended command"
                    )
                    print(f"{8 if plan_path and achievement_num else 7}. Get help")
                    print(f"{9 if plan_path and achievement_num else 8}. Exit")
                    max_choice = 9 if plan_path and achievement_num else 8
                else:
                    print(f"{7 if plan_path and achievement_num else 6}. Get help")
                    print(f"{8 if plan_path and achievement_num else 7}. Exit")
                    max_choice = 8 if plan_path and achievement_num else 7
        else:
            # No commands detected - original behavior
            print("\n1. Copy to clipboard (default - press Enter)")
            print("2. View full prompt")
            print("3. Save to file")
            if plan_path and achievement_num:
                print("4. Generate feedback for this achievement")
            if command:
                print(f"{5 if plan_path and achievement_num else 4}. Execute recommended command")
                print(f"{6 if plan_path and achievement_num else 5}. Get help")
                print(f"{7 if plan_path and achievement_num else 6}. Exit")
                max_choice = 7 if plan_path and achievement_num else 6
            else:
                print(f"{5 if plan_path and achievement_num else 4}. Get help")
                print(f"{6 if plan_path and achievement_num else 5}. Exit")
                max_choice = 6 if plan_path and achievement_num else 5

        choice = input(f"\nChoose [1-{max_choice}] or press Enter for default: ").strip() or "1"

        # Handle choices based on menu structure
        if cleaned_commands:
            if len(cleaned_commands) == 1:
                # Single command menu
                if choice == "1":
                    # Copy first command only
                    if utils.copy_to_clipboard_safe(cleaned_commands[0], enabled=True):
                        print("✅ Command copied to clipboard!")
                    else:
                        print("⚠️  Clipboard not available, displaying command:")
                        print(f"\n{cleaned_commands[0]}")
                elif choice == "2":
                    # Copy full message
                    if utils.copy_to_clipboard_safe(prompt, enabled=True):
                        print("✅ Full message copied to clipboard!")
                    else:
                        print("⚠️  Clipboard not available, displaying prompt:")
                        print("\n" + prompt)
                elif choice == "3":
                    # View full prompt
                    print("\n" + "=" * 70)
                    print(prompt)
                    print("=" * 70)
                    next_action = input("\nCopy command or full message? (c/f/n): ").strip().lower()
                    if next_action == "c":
                        if utils.copy_to_clipboard_safe(cleaned_commands[0], enabled=True):
                            print("✅ Command copied to clipboard!")
                    elif next_action == "f":
                        if utils.copy_to_clipboard_safe(prompt, enabled=True):
                            print("✅ Full message copied to clipboard!")
                elif choice == "4":
                    # Save to file
                    filename = input("Enter filename (e.g., prompt.txt): ").strip()
                    if filename:
                        try:
                            with open(filename, "w") as f:
                                f.write(prompt)
                            print(f"✅ Saved to {filename}")
                        except Exception as e:
                            print(f"❌ Error saving file: {e}")
                    else:
                        print("❌ No filename provided")
                elif choice == "5":
                    if plan_path and achievement_num:
                        # Generate feedback
                        self.generate_feedback_interactive(plan_path, achievement_num)
                        sys.exit(0)
                    elif command:
                        # Execute command
                        print(f"\n🚀 Executing: {command}")
                        result = subprocess.run(command, shell=True)
                        if result.returncode == 0:
                            print("✅ Command completed successfully")
                        else:
                            print(f"❌ Command failed with exit code {result.returncode}")
                    else:
                        # Get help
                        print("\n💡 Help:")
                        print(f"   Workflow State: {workflow_state}")
                        print(f"   Recommended Command: {cleaned_commands[0]}")
                        print("   • Copy the command and run it in your terminal")
                        print("   • Or copy the full message to your LLM chat")
                elif choice == "6":
                    if plan_path and achievement_num:
                        if command:
                            # Execute command
                            print(f"\n🚀 Executing: {command}")
                            result = subprocess.run(command, shell=True)
                            if result.returncode == 0:
                                print("✅ Command completed successfully")
                            else:
                                print(f"❌ Command failed with exit code {result.returncode}")
                        else:
                            # Get help
                            print("\n💡 Help:")
                            print(f"   Workflow State: {workflow_state}")
                            print(f"   Recommended Command: {cleaned_commands[0]}")
                            print("   • Copy the command and run it in your terminal")
                            print("   • Or copy the full message to your LLM chat")
                    elif command:
                        # Get help
                        print("\n💡 Help:")
                        print(f"   Workflow State: {workflow_state}")
                        print(f"   Recommended Command: {cleaned_commands[0]}")
                        print("   • Copy the command and run it in your terminal")
                        print("   • Or copy the full message to your LLM chat")
                    else:
                        # Exit
                        print("👋 Goodbye!")
                        sys.exit(0)
                elif choice == "7":
                    if plan_path and achievement_num:
                        if command:
                            # Get help
                            print("\n💡 Help:")
                            print(f"   Workflow State: {workflow_state}")
                            print(f"   Recommended Command: {cleaned_commands[0]}")
                            print("   • Copy the command and run it in your terminal")
                            print("   • Or copy the full message to your LLM chat")
                        else:
                            # Exit
                            print("👋 Goodbye!")
                            sys.exit(0)
                    elif command:
                        # Exit
                        print("👋 Goodbye!")
                        sys.exit(0)
                elif choice == "8" and plan_path and achievement_num and command:
                    # Exit
                    print("👋 Goodbye!")
                    sys.exit(0)
                else:
                    print(f"❌ Invalid choice. Please enter 1-{max_choice}")
                    return self.show_post_generation_menu(
                        prompt, workflow_state, command, plan_path, achievement_num
                    )
            else:
                # Multiple commands menu
                if choice == "1":
                    # Copy first command
                    if utils.copy_to_clipboard_safe(cleaned_commands[0], enabled=True):
                        print("✅ First command copied to clipboard!")
                    else:
                        print("⚠️  Clipboard not available, displaying command:")
                        print(f"\n{cleaned_commands[0]}")
                elif choice == "2":
                    # Copy second command
                    if utils.copy_to_clipboard_safe(cleaned_commands[1], enabled=True):
                        print("✅ Second command copied to clipboard!")
                    else:
                        print("⚠️  Clipboard not available, displaying command:")
                        print(f"\n{cleaned_commands[1]}")
                elif choice == "3":
                    # Copy full message
                    if utils.copy_to_clipboard_safe(prompt, enabled=True):
                        print("✅ Full message copied to clipboard!")
                    else:
                        print("⚠️  Clipboard not available, displaying prompt:")
                        print("\n" + prompt)
                elif choice == "4":
                    # View full prompt
                    print("\n" + "=" * 70)
                    print(prompt)
                    print("=" * 70)
                    next_action = (
                        input("\nCopy command 1, 2, or full message? (1/2/f/n): ").strip().lower()
                    )
                    if next_action == "1":
                        if utils.copy_to_clipboard_safe(cleaned_commands[0], enabled=True):
                            print("✅ First command copied to clipboard!")
                    elif next_action == "2":
                        if utils.copy_to_clipboard_safe(cleaned_commands[1], enabled=True):
                            print("✅ Second command copied to clipboard!")
                    elif next_action == "f":
                        if utils.copy_to_clipboard_safe(prompt, enabled=True):
                            print("✅ Full message copied to clipboard!")
                elif choice == "5":
                    # Save to file
                    filename = input("Enter filename (e.g., prompt.txt): ").strip()
                    if filename:
                        try:
                            with open(filename, "w") as f:
                                f.write(prompt)
                            print(f"✅ Saved to {filename}")
                        except Exception as e:
                            print(f"❌ Error saving file: {e}")
                    else:
                        print("❌ No filename provided")
                elif choice == "6":
                    if plan_path and achievement_num:
                        # Generate feedback
                        self.generate_feedback_interactive(plan_path, achievement_num)
                        sys.exit(0)
                    elif command:
                        # Execute command
                        print(f"\n🚀 Executing: {command}")
                        result = subprocess.run(command, shell=True)
                        if result.returncode == 0:
                            print("✅ Command completed successfully")
                        else:
                            print(f"❌ Command failed with exit code {result.returncode}")
                    else:
                        # Get help
                        print("\n💡 Help:")
                        print(f"   Workflow State: {workflow_state}")
                        print(f"   Commands available:")
                        for i, cmd in enumerate(cleaned_commands, 1):
                            print(f"     {i}. {cmd}")
                        print("   • Copy a command and run it in your terminal")
                        print("   • Or copy the full message to your LLM chat")
                elif choice == "7":
                    if plan_path and achievement_num:
                        if command:
                            # Execute command
                            print(f"\n🚀 Executing: {command}")
                            result = subprocess.run(command, shell=True)
                            if result.returncode == 0:
                                print("✅ Command completed successfully")
                            else:
                                print(f"❌ Command failed with exit code {result.returncode}")
                        else:
                            # Get help
                            print("\n💡 Help:")
                            print(f"   Workflow State: {workflow_state}")
                            print(f"   Commands available:")
                            for i, cmd in enumerate(cleaned_commands, 1):
                                print(f"     {i}. {cmd}")
                            print("   • Copy a command and run it in your terminal")
                            print("   • Or copy the full message to your LLM chat")
                    elif command:
                        # Get help
                        print("\n💡 Help:")
                        print(f"   Workflow State: {workflow_state}")
                        print(f"   Commands available:")
                        for i, cmd in enumerate(cleaned_commands, 1):
                            print(f"     {i}. {cmd}")
                        print("   • Copy a command and run it in your terminal")
                        print("   • Or copy the full message to your LLM chat")
                    else:
                        # Exit
                        print("👋 Goodbye!")
                        sys.exit(0)
                elif choice == "8":
                    if plan_path and achievement_num:
                        if command:
                            # Get help
                            print("\n💡 Help:")
                            print(f"   Workflow State: {workflow_state}")
                            print(f"   Commands available:")
                            for i, cmd in enumerate(cleaned_commands, 1):
                                print(f"     {i}. {cmd}")
                            print("   • Copy a command and run it in your terminal")
                            print("   • Or copy the full message to your LLM chat")
                        else:
                            # Exit
                            print("👋 Goodbye!")
                            sys.exit(0)
                    elif command:
                        # Exit
                        print("👋 Goodbye!")
                        sys.exit(0)
                elif choice == "9" and plan_path and achievement_num and command:
                    # Exit
                    print("👋 Goodbye!")
                    sys.exit(0)
                else:
                    print(f"❌ Invalid choice. Please enter 1-{max_choice}")
                    return self.show_post_generation_menu(
                        prompt, workflow_state, command, plan_path, achievement_num
                    )
        else:
            # No commands detected - original behavior
            if choice == "1":
                # Copy to clipboard
                if utils.copy_to_clipboard_safe(prompt, enabled=True):
                    print("✅ Copied to clipboard!")
                else:
                    print("⚠️  Clipboard not available, displaying prompt:")
                    print("\n" + prompt)
            elif choice == "2":
                # View full prompt
                print("\n" + "=" * 70)
                print(prompt)
                print("=" * 70)
                next_action = input("\nCopy to clipboard? (Y/n): ").strip().lower()
                if next_action != "n":
                    if utils.copy_to_clipboard_safe(prompt, enabled=True):
                        print("✅ Copied to clipboard!")
            elif choice == "3":
                # Save to file
                filename = input("Enter filename (e.g., prompt.txt): ").strip()
                if filename:
                    try:
                        with open(filename, "w") as f:
                            f.write(prompt)
                        print(f"✅ Saved to {filename}")
                    except Exception as e:
                        print(f"❌ Error saving file: {e}")
                else:
                    print("❌ No filename provided")
            elif choice == "4":
                if plan_path and achievement_num:
                    # Generate feedback
                    self.generate_feedback_interactive(plan_path, achievement_num)
                    sys.exit(0)
                elif command:
                    # Execute command
                    print(f"\n🚀 Executing: {command}")
                    result = subprocess.run(command, shell=True)
                    if result.returncode == 0:
                        print("✅ Command completed successfully")
                    else:
                        print(f"❌ Command failed with exit code {result.returncode}")
                else:
                    # Get help (no command available)
                    print("\n💡 Help:")
                    print(f"   Workflow State: {workflow_state}")
                    print("   • Copy the prompt and paste into your LLM chat")
                    print("   • Follow the instructions in the prompt")
                    print("   • Use --next flag to auto-detect next step")
            elif choice == "5":
                if plan_path and achievement_num:
                    if command:
                        # Execute command
                        print(f"\n🚀 Executing: {command}")
                        result = subprocess.run(command, shell=True)
                        if result.returncode == 0:
                            print("✅ Command completed successfully")
                        else:
                            print(f"❌ Command failed with exit code {result.returncode}")
                    else:
                        # Get help (no command available)
                        print("\n💡 Help:")
                        print(f"   Workflow State: {workflow_state}")
                        print("   • Copy the prompt and paste into your LLM chat")
                        print("   • Follow the instructions in the prompt")
                        print("   • Use --next flag to auto-detect next step")
                elif command:
                    # Get help (command available)
                    print("\n💡 Help:")
                    print(f"   Workflow State: {workflow_state}")
                    print(f"   Recommended Command: {command}")
                    print("   • Copy the prompt and paste into your LLM chat")
                    print("   • Or execute the recommended command")
                    print("   • Use --next flag to auto-detect next step")
                else:
                    # Exit
                    print("👋 Goodbye!")
                    sys.exit(0)
            elif choice == "6":
                if plan_path and achievement_num:
                    if command:
                        # Get help (command available)
                        print("\n💡 Help:")
                        print(f"   Workflow State: {workflow_state}")
                        print(f"   Recommended Command: {command}")
                        print("   • Copy the prompt and paste into your LLM chat")
                        print("   • Or execute the recommended command")
                        print("   • Use --next flag to auto-detect next step")
                    else:
                        # Exit
                        print("👋 Goodbye!")
                        sys.exit(0)
                elif command:
                    # Exit
                    print("👋 Goodbye!")
                    sys.exit(0)
            elif choice == "7" and plan_path and achievement_num and command:
                # Exit
                print("👋 Goodbye!")
                sys.exit(0)
            else:
                print(f"❌ Invalid choice. Please enter 1-{max_choice}")
                return self.show_post_generation_menu(
                    prompt, workflow_state, command, plan_path, achievement_num
                )

    def generate_feedback_interactive(self, plan_path: Path, achievement_num: str) -> None:
        """
        Generate feedback prompt for an achievement (interactive mode helper).

        Calls generate_feedback_prompt.py script and copies output to clipboard.

        Args:
            plan_path: Path to PLAN file
            achievement_num: Achievement number (e.g., "1.1")

        Example:
            >>> menu = InteractiveMenu()
            >>> menu.generate_feedback_interactive(
            ...     Path("work-space/plans/FEATURE/PLAN_FEATURE.md"),
            ...     "1.1"
            ... )
            🔍 Generating feedback prompt for Achievement 1.1...
            ✅ Feedback prompt generated and copied to clipboard!
        """
        # Extract folder name from plan_path for @ shortcut
        # Example: work-space/plans/PROMPT-GENERATOR-UX-AND-FOUNDATION/PLAN_*.md
        #          -> @PROMPT-GENERATOR-UX-AND-FOUNDATION
        plan_folder_name = plan_path.parent.name

        # Build command
        script_path = Path(__file__).parent / "generate_feedback_prompt.py"
        cmd = [
            "python",
            str(script_path),
            "review",
            f"@{plan_folder_name}",
            "--achievement",
            achievement_num,
            "--clipboard",
        ]

        print(f"\n🔍 Generating feedback prompt for Achievement {achievement_num}...")

        try:
            # Run from current working directory (should be project root)
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(result.stdout)
                print("\n✅ Feedback prompt generated and copied to clipboard!")
                print(f"\n💡 Next step: Review the work and create feedback file:")
                print(f"   execution/feedbacks/APPROVED_{achievement_num.replace('.', '')}.md")
                print(f"   OR")
                print(f"   execution/feedbacks/FIX_{achievement_num.replace('.', '')}.md")
            else:
                print(f"❌ Error generating feedback prompt:")
                print(result.stderr)
        except Exception as e:
            print(f"❌ Error: {e}")
