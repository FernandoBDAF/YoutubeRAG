#!/usr/bin/env python3
"""
LLM Methodology Dashboard CLI - Main Entry Point

This is the main entry point for the LLM Methodology Dashboard CLI.
The dashboard provides an intuitive interface for managing PLAN execution,
replacing verbose command-line arguments with an interactive UI.

**Usage**:
    python LLM/main.py              # Launch interactive dashboard
    python LLM/main.py --dashboard  # Explicitly launch dashboard
    python LLM/main.py --help       # Show help message
    python LLM/main.py --version    # Show version

**Features**:
    - Plan discovery and state visualization (Achievement 0.2, 0.3)
    - One-key shortcuts for common operations (coming in Achievement 1.3)
    - Real-time state updates (coming in Achievement 2.3)
    - Parallel execution detection (coming in Achievement 2.1)
    - Interactive workflow execution (coming in Achievement 2.2)

Created: 2025-11-13
Updated: 2025-11-13 (Achievement 0.3 - Main Dashboard)
"""
import argparse
import sys
from pathlib import Path

# Add workspace root to Python path for imports
# This allows running as both `python LLM/main.py` and `python -m LLM.main`
WORKSPACE_ROOT = Path(__file__).parent.parent.resolve()
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

try:
    from rich.console import Console
except ImportError:
    print("ERROR: Rich library not found")
    print("Install: pip install rich>=13.0.0")
    sys.exit(1)

try:
    from LLM.dashboard.main_dashboard import MainDashboard
except ImportError:
    print("ERROR: Dashboard modules not found")
    print("Ensure LLM/dashboard/ package is available")
    sys.exit(1)


def main():
    """Main entry point for LLM Dashboard CLI."""
    console = Console()

    parser = argparse.ArgumentParser(
        description="LLM Methodology Dashboard CLI",
        epilog="For more information, see: LLM/dashboard/README.md (coming soon)",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="LLM Dashboard CLI v0.3.0 (Main Dashboard)",
    )

    parser.add_argument(
        "--dashboard",
        action="store_true",
        default=False,
        help="Launch dashboard (default when no args)",
    )

    args = parser.parse_args()

    # Launch dashboard if no args provided or --dashboard flag set
    if len(sys.argv) == 1 or args.dashboard:
        dashboard = MainDashboard()
        dashboard.show()
        return

    # If we get here, user provided other flags but we don't have them yet
    # Just show a message for now
    console.print("[yellow]Other command-line options coming in future achievements[/yellow]")
    console.print("[dim]For now, use 'python LLM/main.py' to launch dashboard[/dim]")


if __name__ == "__main__":
    main()
