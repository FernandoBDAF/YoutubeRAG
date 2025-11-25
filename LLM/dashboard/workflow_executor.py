"""
Workflow executor for interactive dashboard operations.

Achievement 2.2: Interactive Workflow Execution

Executes LLM methodology workflows interactively with:
- Real-time progress tracking
- Rich result display panels
- Error handling with recovery suggestions
- Interactive user prompts and confirmations

Workflows supported:
- Next: Execute next achievement (auto-detect state)
- SUBPLAN: Create SUBPLAN for specific achievement
- EXECUTION: Create EXECUTION_TASK for specific SUBPLAN
"""

import subprocess
import time
from pathlib import Path
from typing import List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

from core.libraries.logging import get_logger
from LLM.dashboard.models import ExecutionResult, WorkflowType, WorkflowState

logger = get_logger(__name__)


class WorkflowExecutor:
    """
    Execute LLM methodology workflows interactively.
    
    Provides interactive workflow execution with progress tracking,
    result display, and error recovery for dashboard operations.
    
    Example:
        >>> executor = WorkflowExecutor(plan_path, console)
        >>> result = executor.execute_workflow("next")
        >>> if result.success:
        >>>     console.print("[green]Success![/green]")
    """
    
    def __init__(self, plan_path: Path, console: Console):
        """
        Initialize workflow executor.
        
        Args:
            plan_path: Path to plan directory
            console: Rich Console instance for output
        """
        self.plan_path = plan_path
        self.console = console
        self.plan_name = plan_path.name
        
        logger.info(
            "Workflow executor initialized",
            extra={"plan_name": self.plan_name, "plan_path": str(plan_path)}
        )
    
    def execute_workflow(self, workflow_type: str, **kwargs) -> ExecutionResult:
        """
        Route to appropriate workflow handler.
        
        Args:
            workflow_type: Type of workflow to execute ("next", "subplan", "execution")
            **kwargs: Additional arguments for specific workflows
                - achievement_id: For SUBPLAN workflow
                - subplan_id: For EXECUTION workflow
        
        Returns:
            ExecutionResult with outcome details
        
        Raises:
            ValueError: If workflow_type is invalid
        """
        logger.info(
            "Executing workflow",
            extra={"workflow_type": workflow_type, "kwargs": kwargs}
        )
        
        try:
            if workflow_type == WorkflowType.NEXT.value:
                return self._execute_next_workflow()
            elif workflow_type == WorkflowType.SUBPLAN.value:
                achievement_id = kwargs.get("achievement_id")
                if not achievement_id:
                    return self._handle_error(
                        ValueError("achievement_id required for SUBPLAN workflow"),
                        workflow_type
                    )
                return self._execute_subplan_workflow(achievement_id)
            elif workflow_type == WorkflowType.EXECUTION.value:
                subplan_id = kwargs.get("subplan_id")
                if not subplan_id:
                    return self._handle_error(
                        ValueError("subplan_id required for EXECUTION workflow"),
                        workflow_type
                    )
                return self._execute_execution_workflow(subplan_id)
            else:
                return self._handle_error(
                    ValueError(f"Unknown workflow type: {workflow_type}"),
                    workflow_type
                )
        except Exception as e:
            return self._handle_error(e, workflow_type)
    
    def _execute_next_workflow(self) -> ExecutionResult:
        """
        Execute next achievement workflow with auto-detection.
        
        Detects current state and routes to appropriate action:
        - create_subplan: If next achievement needs SUBPLAN
        - create_execution: If SUBPLAN exists, needs EXECUTION
        - continue_execution: If EXECUTION exists, continue work
        
        Returns:
            ExecutionResult with outcome
        """
        logger.info("Executing next workflow", extra={"plan_name": self.plan_name})
        
        # Show confirmation prompt
        self.console.print()
        self.console.print("[cyan]📋 Execute Next Achievement Workflow[/cyan]")
        self.console.print(f"[dim]Plan: {self.plan_name}[/dim]")
        self.console.print()
        
        if not Confirm.ask("Continue with next workflow?", default=True):
            logger.info("User cancelled next workflow")
            return ExecutionResult(
                success=False,
                error="Workflow cancelled by user"
            )
        
        # Build command
        cmd = [
            "python",
            "LLM/scripts/generation/generate_prompt.py",
            f"@{self.plan_name}",
            "--next",
            "--interactive"
        ]
        
        return self._run_subprocess(
            cmd,
            "Execute Next",
            "Detecting next achievement state..."
        )
    
    def _execute_subplan_workflow(self, achievement_id: str) -> ExecutionResult:
        """
        Execute SUBPLAN creation workflow.
        
        Args:
            achievement_id: Achievement ID (e.g., "1.2")
        
        Returns:
            ExecutionResult with outcome
        """
        logger.info(
            "Executing SUBPLAN workflow",
            extra={"plan_name": self.plan_name, "achievement_id": achievement_id}
        )
        
        # Validate achievement ID format
        if not achievement_id or "." not in achievement_id:
            return self._handle_error(
                ValueError(f"Invalid achievement ID format: {achievement_id}"),
                "subplan"
            )
        
        # Show confirmation prompt
        self.console.print()
        self.console.print(f"[cyan]📝 Create SUBPLAN for Achievement {achievement_id}[/cyan]")
        self.console.print(f"[dim]Plan: {self.plan_name}[/dim]")
        self.console.print()
        
        if not Confirm.ask("Create SUBPLAN?", default=True):
            logger.info("User cancelled SUBPLAN creation")
            return ExecutionResult(
                success=False,
                error="Workflow cancelled by user"
            )
        
        # Build command
        cmd = [
            "python",
            "LLM/scripts/generation/generate_subplan_prompt.py",
            f"@{self.plan_name}",
            "--achievement",
            achievement_id
        ]
        
        return self._run_subprocess(
            cmd,
            f"Create SUBPLAN {achievement_id}",
            f"Creating SUBPLAN for achievement {achievement_id}..."
        )
    
    def _execute_execution_workflow(self, subplan_id: str) -> ExecutionResult:
        """
        Execute EXECUTION_TASK creation workflow.
        
        Args:
            subplan_id: SUBPLAN ID (e.g., "11" for SUBPLAN_XX_11.md)
        
        Returns:
            ExecutionResult with outcome
        """
        logger.info(
            "Executing EXECUTION workflow",
            extra={"plan_name": self.plan_name, "subplan_id": subplan_id}
        )
        
        # Check if SUBPLAN exists
        subplan_file = self.plan_path / "subplans" / f"SUBPLAN_{self.plan_name}_{subplan_id}.md"
        if not subplan_file.exists():
            return self._handle_error(
                FileNotFoundError(f"SUBPLAN not found: {subplan_file.name}"),
                "execution"
            )
        
        # Show confirmation prompt
        self.console.print()
        self.console.print(f"[cyan]🚀 Create EXECUTION_TASK for SUBPLAN {subplan_id}[/cyan]")
        self.console.print(f"[dim]Plan: {self.plan_name}[/dim]")
        self.console.print(f"[dim]SUBPLAN: {subplan_file.name}[/dim]")
        self.console.print()
        
        if not Confirm.ask("Create EXECUTION_TASK?", default=True):
            logger.info("User cancelled EXECUTION creation")
            return ExecutionResult(
                success=False,
                error="Workflow cancelled by user"
            )
        
        # Build command
        cmd = [
            "python",
            "LLM/scripts/generation/generate_execution_prompt.py",
            f"@{subplan_file}"
        ]
        
        return self._run_subprocess(
            cmd,
            f"Create EXECUTION {subplan_id}",
            f"Creating EXECUTION_TASK for SUBPLAN {subplan_id}..."
        )
    
    def _run_subprocess(
        self,
        cmd: List[str],
        task_name: str,
        progress_message: str
    ) -> ExecutionResult:
        """
        Run subprocess with progress tracking and output capture.
        
        Args:
            cmd: Command list for subprocess
            task_name: Display name for task
            progress_message: Message to show during execution
        
        Returns:
            ExecutionResult with outcome
        """
        start_time = time.time()
        
        logger.info(
            "Running subprocess",
            extra={"command": " ".join(cmd), "task_name": task_name}
        )
        
        try:
            # Show progress indicator
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(progress_message, total=None)
                
                # Run subprocess with timeout
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=180,  # 3 minute timeout
                    cwd="."
                )
                
                progress.update(task, completed=True)
            
            duration = time.time() - start_time
            
            # Parse output and create result
            if result.returncode == 0:
                execution_result = self._parse_success_output(
                    result.stdout,
                    task_name,
                    duration
                )
            else:
                execution_result = ExecutionResult(
                    success=False,
                    error=result.stderr or result.stdout or "Unknown error",
                    duration=duration
                )
            
            # Display result
            self._display_result(execution_result)
            
            logger.info(
                "Subprocess completed",
                extra={
                    "task_name": task_name,
                    "success": execution_result.success,
                    "duration": duration
                }
            )
            
            return execution_result
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            logger.error(
                "Subprocess timeout",
                extra={"task_name": task_name, "duration": duration}
            )
            return ExecutionResult(
                success=False,
                error=f"Workflow timed out after {duration:.0f} seconds",
                duration=duration
            )
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "Subprocess error",
                extra={"task_name": task_name, "error": str(e)}
            )
            return ExecutionResult(
                success=False,
                error=str(e),
                duration=duration
            )
    
    def _parse_success_output(
        self,
        output: str,
        task_name: str,
        duration: float
    ) -> ExecutionResult:
        """
        Parse successful workflow output.
        
        Args:
            output: Subprocess stdout
            task_name: Name of task
            duration: Execution duration
        
        Returns:
            ExecutionResult with parsed details
        """
        # Simple parsing - look for created files in output
        deliverables = []
        lines = output.split("\n")
        
        for line in lines:
            if "created" in line.lower() or "saved" in line.lower():
                # Extract file names (simple heuristic)
                words = line.split()
                for word in words:
                    if word.endswith(".md"):
                        deliverables.append(word)
        
        return ExecutionResult(
            success=True,
            deliverables=deliverables,
            duration=duration
        )
    
    def _display_result(self, result: ExecutionResult):
        """
        Display workflow result with Rich panels.
        
        Args:
            result: ExecutionResult to display
        """
        self.console.print()
        
        if result.success:
            # Success panel (green)
            content = f"[green]✅ Workflow completed successfully![/green]\n"
            
            if result.deliverables:
                content += f"\n[bold]Deliverables:[/bold]\n"
                for deliverable in result.deliverables:
                    content += f"  • {deliverable}\n"
            
            if result.tests_total > 0:
                content += f"\n[bold]Tests:[/bold] {result.tests_passing}/{result.tests_total} passing\n"
            
            content += f"\n[dim]Duration: {result.format_duration()}[/dim]"
            
            self.console.print(Panel(
                content,
                title="✅ Success",
                border_style="green"
            ))
        else:
            # Failure panel (red)
            content = f"[red]❌ Workflow failed[/red]\n"
            content += f"\n[bold]Error:[/bold]\n{result.error}\n"
            
            # Add recovery suggestions
            suggestions = self._generate_recovery_suggestions(result.error or "")
            if suggestions:
                content += f"\n[bold]Suggestions:[/bold]\n"
                for suggestion in suggestions:
                    content += f"  • {suggestion}\n"
            
            if result.log_file:
                content += f"\n[dim]See: {result.log_file}[/dim]"
            
            self.console.print(Panel(
                content,
                title="❌ Error",
                border_style="red"
            ))
        
        self.console.print()
    
    def _generate_recovery_suggestions(self, error: str) -> List[str]:
        """
        Generate recovery suggestions based on error.
        
        Args:
            error: Error message
        
        Returns:
            List of recovery suggestions
        """
        suggestions = []
        error_lower = error.lower()
        
        if "not found" in error_lower or "does not exist" in error_lower:
            if "subplan" in error_lower:
                suggestions.append("Create SUBPLAN first (action 2 or 3)")
                suggestions.append("Verify the achievement number is correct")
            elif "execution" in error_lower:
                suggestions.append("Verify the SUBPLAN exists")
                suggestions.append("Check the SUBPLAN ID format (e.g., '11' for SUBPLAN_XX_11.md)")
        
        if "timeout" in error_lower:
            suggestions.append("Workflow took too long - check for hanging processes")
            suggestions.append("Try running the command manually to debug")
        
        if "cancelled" in error_lower:
            suggestions.append("Workflow was cancelled - you can retry anytime")
        
        if "invalid" in error_lower:
            if "achievement" in error_lower:
                suggestions.append("Check achievement ID format (should be 'X.Y')")
                suggestions.append("Verify achievement exists in PLAN")
        
        if not suggestions:
            suggestions.append("Check the error message above for details")
            suggestions.append("Review logs for more information")
        
        return suggestions
    
    def _handle_error(self, error: Exception, workflow: str) -> ExecutionResult:
        """
        Handle workflow error with logging and recovery suggestions.
        
        Args:
            error: Exception that occurred
            workflow: Workflow type that failed
        
        Returns:
            ExecutionResult with error details
        """
        error_msg = str(error)
        
        logger.error(
            "Workflow error",
            extra={
                "workflow": workflow,
                "error": error_msg,
                "plan_name": self.plan_name
            }
        )
        
        return ExecutionResult(
            success=False,
            error=error_msg
        )

