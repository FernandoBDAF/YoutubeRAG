"""
State watcher for filesystem monitoring.

Achievement 2.3: Real-Time State Updates

Monitors filesystem for changes to execution and feedback files,
provides callbacks for state updates with debouncing.

Uses simple polling approach (no external dependencies like watchdog).
"""

import time
import threading
from pathlib import Path
from typing import Callable, Dict, Optional, Set
from datetime import datetime

from core.libraries.logging import get_logger

logger = get_logger(__name__)


class StateWatcher:
    """
    Watch filesystem for state changes.
    
    Monitors execution/feedbacks/ and execution/ directories for:
    - New APPROVED/FIX files in feedbacks/
    - New EXECUTION_TASK files in execution/
    - Modified files (via mtime tracking)
    
    Uses polling (2-second interval) with debouncing (500ms) to avoid
    excessive callbacks.
    
    Example:
        >>> def on_change():
        >>>     print("State changed!")
        >>> watcher = StateWatcher(plan_path, on_change)
        >>> watcher.start()
        >>> # ... do work ...
        >>> watcher.stop()
    """
    
    def __init__(
        self,
        plan_path: Path,
        callback: Callable[[], None],
        poll_interval: float = 2.0,
        debounce_delay: float = 0.5
    ):
        """
        Initialize state watcher.
        
        Args:
            plan_path: Path to plan directory
            callback: Function to call when changes detected
            poll_interval: Seconds between filesystem polls (default: 2.0)
            debounce_delay: Seconds to wait after last change before callback (default: 0.5)
        """
        self.plan_path = plan_path
        self.callback = callback
        self.poll_interval = poll_interval
        self.debounce_delay = debounce_delay
        
        # Directories to watch
        self.execution_dir = plan_path / "execution"
        self.feedbacks_dir = plan_path / "execution" / "feedbacks"
        
        # State tracking
        self.file_mtimes: Dict[Path, float] = {}
        self.is_running = False
        self.polling_thread: Optional[threading.Thread] = None
        self.debounce_timer: Optional[threading.Timer] = None
        self.lock = threading.Lock()
        
        # Track last change time for debouncing
        self.last_change_time: Optional[float] = None
        
        logger.info(
            "State watcher initialized",
            extra={
                "plan_path": str(plan_path),
                "poll_interval": poll_interval,
                "debounce_delay": debounce_delay
            }
        )
    
    def start(self):
        """Start watching for changes."""
        if self.is_running:
            logger.warning("State watcher already running")
            return
        
        logger.info("Starting state watcher")
        self.is_running = True
        
        # Initialize file mtimes
        self._scan_files()
        
        # Start polling thread
        self.polling_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.polling_thread.start()
    
    def stop(self):
        """Stop watching for changes."""
        if not self.is_running:
            return
        
        logger.info("Stopping state watcher")
        self.is_running = False
        
        # Cancel any pending debounce timer
        if self.debounce_timer:
            self.debounce_timer.cancel()
            self.debounce_timer = None
        
        # Wait for polling thread to finish
        if self.polling_thread:
            self.polling_thread.join(timeout=5.0)
            self.polling_thread = None
    
    def _poll_loop(self):
        """Main polling loop (runs in background thread)."""
        while self.is_running:
            try:
                self._check_for_changes()
            except Exception as e:
                logger.error(
                    "Error in polling loop",
                    exc_info=True,
                    extra={"error": str(e)}
                )
            
            # Sleep for poll interval
            time.sleep(self.poll_interval)
    
    def _check_for_changes(self):
        """Check for filesystem changes."""
        changed = False
        
        # Get current file states
        current_files = self._scan_files()
        
        with self.lock:
            # Check for new files
            new_files = current_files.keys() - self.file_mtimes.keys()
            if new_files:
                logger.debug(f"New files detected: {len(new_files)}")
                changed = True
            
            # Check for modified files
            for file_path, current_mtime in current_files.items():
                if file_path in self.file_mtimes:
                    old_mtime = self.file_mtimes[file_path]
                    if current_mtime > old_mtime:
                        logger.debug(f"Modified file: {file_path.name}")
                        changed = True
            
            # Check for deleted files
            deleted_files = self.file_mtimes.keys() - current_files.keys()
            if deleted_files:
                logger.debug(f"Deleted files detected: {len(deleted_files)}")
                changed = True
            
            # Update tracked files
            self.file_mtimes = current_files
        
        if changed:
            self._trigger_debounced_callback()
    
    def _scan_files(self) -> Dict[Path, float]:
        """
        Scan watched directories for relevant files.
        
        Returns:
            Dict mapping file paths to modification times
        """
        files = {}
        
        # Scan feedbacks directory for APPROVED/FIX files
        if self.feedbacks_dir.exists():
            for file_path in self.feedbacks_dir.iterdir():
                if file_path.is_file() and (
                    file_path.name.startswith("APPROVED_") or
                    file_path.name.startswith("FIX_")
                ):
                    try:
                        files[file_path] = file_path.stat().st_mtime
                    except OSError:
                        pass  # File may have been deleted
        
        # Scan execution directory for EXECUTION_TASK files
        if self.execution_dir.exists():
            for file_path in self.execution_dir.iterdir():
                if file_path.is_file() and file_path.name.startswith("EXECUTION_TASK_"):
                    try:
                        files[file_path] = file_path.stat().st_mtime
                    except OSError:
                        pass  # File may have been deleted
        
        return files
    
    def _trigger_debounced_callback(self):
        """Trigger callback with debouncing."""
        with self.lock:
            # Cancel any existing timer
            if self.debounce_timer:
                self.debounce_timer.cancel()
            
            # Update last change time
            self.last_change_time = time.time()
            
            # Schedule new callback after debounce delay
            self.debounce_timer = threading.Timer(
                self.debounce_delay,
                self._execute_callback
            )
            self.debounce_timer.daemon = True
            self.debounce_timer.start()
    
    def _execute_callback(self):
        """Execute the callback (after debounce period)."""
        try:
            logger.info("Executing state change callback")
            self.callback()
        except Exception as e:
            logger.error(
                "Error in state change callback",
                exc_info=True,
                extra={"error": str(e)}
            )
    
    def get_watched_files(self) -> Set[Path]:
        """
        Get set of currently watched files.
        
        Returns:
            Set of file paths being monitored
        """
        with self.lock:
            return set(self.file_mtimes.keys())
    
    def force_callback(self):
        """
        Force immediate callback (bypasses debouncing).
        
        Useful for manual refresh triggers.
        """
        logger.info("Forcing immediate callback")
        try:
            self.callback()
        except Exception as e:
            logger.error(
                "Error in forced callback",
                exc_info=True,
                extra={"error": str(e)}
            )

