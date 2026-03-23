# src/application/dto/agent_dto.py
"""
Agent DTOs - Data Transfer Objects for agents.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


# Request DTOs
class ExecuteAgentRequest(BaseModel):
    """Request to execute an agent."""
    agent_key: str = Field(..., min_length=1, max_length=30)
    request: str = Field(..., min_length=1)
    context: Optional[Dict[str, Any]] = None


class RouteRequestRequest(BaseModel):
    """Request to route to appropriate agents."""
    request: str = Field(..., min_length=1)
    context: Optional[Dict[str, Any]] = None


# Response DTOs
class AgentInfoResponse(BaseModel):
    """Response containing agent information."""
    key: str
    name: str
    description: str
    prompts: List[str]
    memory_key: str


class AgentListResponse(BaseModel):
    """Response containing a list of agents."""
    agents: List[AgentInfoResponse]


class ExecuteAgentResponse(BaseModel):
    """Response from executing an agent."""
    agent: str
    status: str
    output: str
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class RouteResponse(BaseModel):
    """Response from routing a request."""
    status: str
    request: str
    agents_used: List[str]
    results: List[Dict[str, Any]]
    output: str
    errors: List[str] = []
