# src/domain/entities/architect.py
"""
Architect Agent Entities - Task State and Progress Tracking.

Part of ADR-018: Architect Agent Refactoring.
Implements Claude Code-inspired task state machine.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime


class AgentStatus(Enum):
    """Agent task lifecycle status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"


class Phase(Enum):
    """Architect agent phases."""
    RESEARCH = "research"      # Parallel exploration
    SYNTHESIS = "synthesis"   # Blueprint generation
    OUTPUT = "output"         # File creation


@dataclass
class ToolActivity:
    """
    Track individual tool executions within an agent task.

    Records what tools were used, when, and for what purpose.
    """
    tool_name: str
    activity_description: str
    timestamp: datetime = field(default_factory=datetime.now)
    duration_ms: int = 0
    success: bool = True
    error: Optional[str] = None
    # Classification flags
    is_search: bool = False    # glob, grep, search
    is_read: bool = False      # read, cat, head
    is_write: bool = False     # write, edit, create


@dataclass
class AgentProgress:
    """
    Aggregated progress data for an agent task.

    Tracks tool usage, tokens, and recent activities.
    """
    tool_use_count: int = 0
    token_count: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    last_activity: Optional[datetime] = None
    recent_activities: List[ToolActivity] = field(default_factory=list)
    summary: str = ""

    def add_activity(self, activity: ToolActivity):
        """Add activity and maintain recent list (max 10)."""
        self.recent_activities.append(activity)
        if len(self.recent_activities) > 10:
            self.recent_activities.pop(0)
        self.last_activity = datetime.now()
        self.tool_use_count += 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization."""
        return {
            "tool_use_count": self.tool_use_count,
            "token_count": self.token_count,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "recent_activities": [
                {
                    "tool": a.tool_name,
                    "description": a.activity_description,
                    "timestamp": a.timestamp.isoformat(),
                }
                for a in self.recent_activities[-5:]
            ],
            "summary": self.summary,
        }


@dataclass
class ArchitectTaskState:
    """
    Architect agent task state with progress tracking.

    Tracks the full lifecycle of an architect task including:
    - Status and phase
    - Progress metrics
    - Files created
    - Errors encountered
    """
    agent_id: str
    request: str
    status: AgentStatus = AgentStatus.PENDING
    progress: AgentProgress = field(default_factory=AgentProgress)
    current_phase: Phase = Phase.RESEARCH
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    adr_files_created: List[str] = field(default_factory=list)
    checkpoint_id: Optional[str] = None
    error: Optional[str] = None

    def start(self):
        """Mark task as started."""
        self.status = AgentStatus.RUNNING
        self.started_at = datetime.now()

    def complete(self, summary: str = ""):
        """Mark task as completed."""
        self.status = AgentStatus.COMPLETED
        self.completed_at = datetime.now()
        self.progress.summary = summary

    def fail(self, error: str):
        """Mark task as failed."""
        self.status = AgentStatus.FAILED
        self.completed_at = datetime.now()
        self.error = error

    def set_phase(self, phase: Phase):
        """Transition to new phase."""
        self.current_phase = phase

    def add_activity(self, activity: ToolActivity):
        """Add tool activity to progress."""
        self.progress.add_activity(activity)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization."""
        return {
            "agent_id": self.agent_id,
            "request": self.request,
            "status": self.status.value,
            "phase": self.current_phase.value,
            "progress": self.progress.to_dict(),
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "adr_files_created": self.adr_files_created,
            "checkpoint_id": self.checkpoint_id,
            "error": self.error,
        }


@dataclass
class ResearchResult:
    """Result from a single explorer agent in parallel research."""
    explorer_type: str  # "tech_stack", "code_patterns", "best_practices"
    findings: Dict[str, Any]
    raw_output: str
    success: bool = True
    error: Optional[str] = None


@dataclass
class SynthesisResult:
    """Result from synthesis phase."""
    patterns_found: List[Dict[str, str]]
    architecture_decision: Dict[str, Any]
    components: List[Dict[str, Any]]
    implementation_map: List[Dict[str, Any]]
    data_flow: List[Dict[str, Any]]
    build_sequence: List[Dict[str, Any]]
    critical_details: Dict[str, str]
    confidence: float = 0.0  # 0.0 - 1.0
