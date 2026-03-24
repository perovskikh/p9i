# src/domain/exceptions.py
"""
Domain exceptions - Core business exceptions.
"""

from typing import Optional


class DomainException(Exception):
    """Base domain exception."""
    pass


class PromptNotFoundError(DomainException):
    """Raised when a prompt is not found."""
    def __init__(self, name: str, tier: Optional[str] = None):
        self.name = name
        self.tier = tier
        message = f"Prompt not found: {name}"
        if tier:
            message += f" (tier: {tier})"
        super().__init__(message)


class BaselineIntegrityError(DomainException):
    """Raised when baseline prompt integrity is compromised."""
    def __init__(self, prompt_name: str):
        self.prompt_name = prompt_name
        super().__init__(f"Baseline integrity check failed for core prompt: {prompt_name}")


class ProjectNotFoundError(DomainException):
    """Raised when a project is not found."""
    def __init__(self, project_id: str):
        self.project_id = project_id
        super().__init__(f"Project not found: {project_id}")


class AgentNotFoundError(DomainException):
    """Raised when an agent is not found."""
    def __init__(self, agent_key: str):
        self.agent_key = agent_key
        super().__init__(f"Agent not found: {agent_key}")


class StorageError(DomainException):
    """Raised when storage operation fails."""
    pass


class ValidationError(DomainException):
    """Raised when entity validation fails."""
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__(f"Validation failed: {', '.join(errors)}")


class DuplicatePromptError(DomainException):
    """Raised when attempting to create a duplicate prompt."""
    def __init__(self, name: str, existing_path: str, suggestion: str = None):
        self.name = name
        self.existing_path = existing_path
        self.suggestion = suggestion
        message = f"Prompt '{name}' already exists at: {existing_path}"
        if suggestion:
            message += f"\nSuggestion: {suggestion}"
        super().__init__(message)


class DuplicateKeywordError(DomainException):
    """Raised when a keyword maps to multiple prompts."""
    def __init__(self, keyword: str, prompts: list[str]):
        self.keyword = keyword
        self.prompts = prompts
        super().__init__(
            f"Keyword '{keyword}' is already used by: {', '.join(prompts)}. "
            f"Use a more specific keyword or update existing mapping."
        )


class DuplicateAgentError(DomainException):
    """Raised when creating an agent with duplicate prompts."""
    def __init__(self, agent_name: str, duplicates: list[str]):
        self.agent_name = agent_name
        self.duplicates = duplicates
        super().__init__(
            f"Agent '{agent_name}' references duplicate prompts: {', '.join(duplicates)}"
        )