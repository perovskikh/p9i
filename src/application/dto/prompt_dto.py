# src/application/dto/prompt_dto.py
"""
Prompt DTOs - Data Transfer Objects for prompts.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# Request DTOs
class RunPromptRequest(BaseModel):
    """Request to run a prompt."""
    prompt_name: str = Field(..., min_length=1, max_length=100)
    input_data: Dict[str, Any] = Field(default_factory=dict)
    context: Optional[Dict[str, Any]] = None


class RunPromptChainRequest(BaseModel):
    """Request to run a chain of prompts."""
    stages: List[str] = Field(..., min_items=1)
    initial_data: Dict[str, Any] = Field(default_factory=dict)


class ListPromptsRequest(BaseModel):
    """Request to list prompts."""
    tier: Optional[str] = None
    search: Optional[str] = None
    limit: int = Field(default=50, le=100)


class CreatePromptRequest(BaseModel):
    """Request to create a prompt."""
    name: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)
    tier: str = Field(default="universal")
    tags: List[str] = Field(default_factory=list)
    variables: Dict[str, Any] = Field(default_factory=dict)


# Response DTOs
class PromptResponse(BaseModel):
    """Response containing a prompt."""
    name: str
    content: str
    tier: str
    version: str
    tags: List[str] = []
    variables: Dict[str, Any] = {}


class PromptListResponse(BaseModel):
    """Response containing a list of prompts."""
    prompts: List[Dict[str, Any]]
    total: int
    tier: Optional[str] = None


class RunPromptResponse(BaseModel):
    """Response from running a prompt."""
    status: str
    prompt_name: str
    output: str
    usage: Optional[Dict[str, Any]] = None
    errors: List[str] = []


class RunPromptChainResponse(BaseModel):
    """Response from running a prompt chain."""
    status: str
    stages: List[Dict[str, Any]]
    final_output: str
    errors: List[str] = []
