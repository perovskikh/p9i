# src/application/dto/__init__.py
"""Application DTOs - Data Transfer Objects."""

from src.application.dto.prompt_dto import (
    RunPromptRequest,
    RunPromptChainRequest,
    ListPromptsRequest,
    CreatePromptRequest,
    PromptResponse,
    PromptListResponse,
    RunPromptResponse,
    RunPromptChainResponse,
)

from src.application.dto.auth_dto import (
    GenerateTokenRequest,
    ValidateTokenRequest,
    RevokeTokenRequest,
    TokenResponse,
    TokenValidationResponse,
    TokenRevokeResponse,
)

from src.application.dto.agent_dto import (
    ExecuteAgentRequest,
    RouteRequestRequest,
    AgentInfoResponse,
    AgentListResponse,
    ExecuteAgentResponse,
    RouteResponse,
)

__all__ = [
    # Prompt DTOs
    "RunPromptRequest",
    "RunPromptChainRequest",
    "ListPromptsRequest",
    "CreatePromptRequest",
    "PromptResponse",
    "PromptListResponse",
    "RunPromptResponse",
    "RunPromptChainResponse",
    # Auth DTOs
    "GenerateTokenRequest",
    "ValidateTokenRequest",
    "RevokeTokenRequest",
    "TokenResponse",
    "TokenValidationResponse",
    "TokenRevokeResponse",
    # Agent DTOs
    "ExecuteAgentRequest",
    "RouteRequestRequest",
    "AgentInfoResponse",
    "AgentListResponse",
    "ExecuteAgentResponse",
    "RouteResponse",
]
