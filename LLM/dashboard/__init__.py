"""
LLM Dashboard Package

This package provides the dashboard framework for the LLM Methodology CLI.

**Core Components**:
- `base_dashboard.py`: Abstract base class for all dashboards
- `ui_components.py`: Reusable UI components (panels, tables, prompts)
- `utils.py`: Helper utilities

**Usage**:
    from LLM.dashboard import BaseDashboard
    from LLM.dashboard.ui_components import create_panel, create_table
    from LLM.dashboard.utils import format_timestamp

Created: 2025-11-13
Achievement: 0.1 - Rich Dashboard Framework Setup
"""

from LLM.dashboard.base_dashboard import BaseDashboard

__all__ = ["BaseDashboard"]
