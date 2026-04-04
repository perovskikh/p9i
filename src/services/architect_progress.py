# src/services/architect_progress.py
"""
Architect Progress Tracker - Progress tracking for architect agent tasks.

Part of ADR-018: Architect Agent Refactoring.
Tracks task state, tool activities, and phase transitions.
"""

import logging
from typing import Dict, Optional, List, Any
from datetime import datetime

from src.domain.entities.architect import (
    AgentStatus,
    Phase,
    ToolActivity,
    AgentProgress,
    ArchitectTaskState,
    ResearchResult,
    SynthesisResult,
)

logger = logging.getLogger(__name__)


class ArchitectProgressTracker:
    """
    Tracks progress of architect agent tasks.

    Provides:
    - Task state management
    - Tool activity recording
    - Phase transition tracking
    - Checkpoint integration for file creation

    Usage:
        tracker = ArchitectProgressTracker()
        task = tracker.create_task("design auth system")
        tracker.start_task(task)
        tracker.add_activity(task.agent_id, ToolActivity("grep", "Found 5 auth files"))
        tracker.set_phase(task.agent_id, Phase.SYNTHESIS)
        tracker.complete_task(task.agent_id, "Architecture designed successfully")
    """

    def __init__(self):
        self._tasks: Dict[str, ArchitectTaskState] = {}

    def create_task(self, request: str, agent_id: Optional[str] = None) -> ArchitectTaskState:
        """
        Create a new architect task.

        Args:
            request: The architect request/task description
            agent_id: Optional agent ID (generated if not provided)

        Returns:
            ArchitectTaskState for the new task
        """
        import uuid
        task_id = agent_id or str(uuid.uuid4())[:8]

        task = ArchitectTaskState(
            agent_id=task_id,
            request=request,
        )
        self._tasks[task_id] = task
        logger.info(f"Created architect task: {task_id}")
        return task

    def get_task(self, agent_id: str) -> Optional[ArchitectTaskState]:
        """Get task by agent ID."""
        return self._tasks.get(agent_id)

    def start_task(self, agent_id: str) -> bool:
        """
        Mark task as started.

        Args:
            agent_id: Task agent ID

        Returns:
            True if task was found and started
        """
        task = self._tasks.get(agent_id)
        if not task:
            logger.warning(f"Task not found: {agent_id}")
            return False

        task.start()
        logger.info(f"Started architect task: {agent_id}")
        return True

    def add_activity(
        self,
        agent_id: str,
        tool_name: str,
        description: str,
        is_search: bool = False,
        is_read: bool = False,
        is_write: bool = False,
        success: bool = True,
        error: Optional[str] = None,
    ) -> bool:
        """
        Record a tool activity for a task.

        Args:
            agent_id: Task agent ID
            tool_name: Name of tool executed
            description: Human-readable description
            is_search: Was this a search tool (grep, glob)
            is_read: Was this a read tool
            is_write: Was this a write tool
            success: Did tool execute successfully
            error: Error message if failed

        Returns:
            True if activity was recorded
        """
        task = self._tasks.get(agent_id)
        if not task:
            return False

        activity = ToolActivity(
            tool_name=tool_name,
            activity_description=description,
            is_search=is_search,
            is_read=is_read,
            is_write=is_write,
            success=success,
            error=error,
        )
        task.add_activity(activity)
        logger.debug(f"Activity recorded for {agent_id}: {tool_name}")
        return True

    def set_phase(self, agent_id: str, phase: Phase) -> bool:
        """
        Transition task to a new phase.

        Args:
            agent_id: Task agent ID
            phase: New phase to transition to

        Returns:
            True if phase was set
        """
        task = self._tasks.get(agent_id)
        if not task:
            return False

        old_phase = task.current_phase
        task.set_phase(phase)
        logger.info(f"Task {agent_id} phase: {old_phase.value} -> {phase.value}")
        return True

    def add_adr_file(self, agent_id: str, file_path: str) -> bool:
        """
        Record an ADR file created by the task.

        Args:
            agent_id: Task agent ID
            file_path: Path to ADR file created

        Returns:
            True if file was recorded
        """
        task = self._tasks.get(agent_id)
        if not task:
            return False

        task.adr_files_created.append(file_path)
        logger.info(f"ADR created by {agent_id}: {file_path}")
        return True

    def set_checkpoint(self, agent_id: str, checkpoint_id: str) -> bool:
        """Set checkpoint ID for task."""
        task = self._tasks.get(agent_id)
        if not task:
            return False

        task.checkpoint_id = checkpoint_id
        return True

    def complete_task(self, agent_id: str, summary: str = "") -> bool:
        """
        Mark task as completed.

        Args:
            agent_id: Task agent ID
            summary: Final summary of work done

        Returns:
            True if task was completed
        """
        task = self._tasks.get(agent_id)
        if not task:
            return False

        task.complete(summary)
        logger.info(f"Completed architect task: {agent_id}, summary: {summary[:100]}")
        return True

    def fail_task(self, agent_id: str, error: str) -> bool:
        """
        Mark task as failed.

        Args:
            agent_id: Task agent ID
            error: Error message

        Returns:
            True if task was marked as failed
        """
        task = self._tasks.get(agent_id)
        if not task:
            return False

        task.fail(error)
        logger.error(f"Failed architect task: {agent_id}, error: {error}")
        return True

    def get_progress(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get progress summary for a task.

        Args:
            agent_id: Task agent ID

        Returns:
            Dict with progress info or None if task not found
        """
        task = self._tasks.get(agent_id)
        if not task:
            return None

        return task.to_dict()

    def list_active_tasks(self) -> List[Dict[str, Any]]:
        """
        List all active (non-completed) tasks.

        Returns:
            List of task info dicts
        """
        active = [
            t for t in self._tasks.values()
            if t.status not in (AgentStatus.COMPLETED, AgentStatus.FAILED)
        ]

        return [
            {
                "agent_id": t.agent_id,
                "status": t.status.value,
                "phase": t.current_phase.value,
                "progress": t.progress.tool_use_count,
            }
            for t in active
        ]

    def cleanup_completed(self, max_age_hours: int = 24) -> int:
        """
        Remove completed tasks older than max_age_hours.

        Args:
            max_age_hours: Maximum age in hours

        Returns:
            Number of tasks removed
        """
        now = datetime.now()
        to_remove = []

        for task_id, task in self._tasks.items():
            if task.status in (AgentStatus.COMPLETED, AgentStatus.FAILED):
                if task.completed_at:
                    age_hours = (now - task.completed_at).total_seconds() / 3600
                    if age_hours > max_age_hours:
                        to_remove.append(task_id)

        for task_id in to_remove:
            del self._tasks[task_id]

        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} completed tasks")

        return len(to_remove)


# Global instance for reuse
_tracker: Optional[ArchitectProgressTracker] = None


def get_architect_tracker() -> ArchitectProgressTracker:
    """Get or create global architect tracker instance."""
    global _tracker
    if _tracker is None:
        _tracker = ArchitectProgressTracker()
    return _tracker
