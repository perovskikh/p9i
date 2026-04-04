# src/services/executor.py
"""
Prompt executor service

Handles execution of prompts through LLM.
"""

from typing import Optional
import logging

from .llm_client import get_llm_client, LLMClient
from src.domain.services.prompt_guard import sanitize_dict

logger = logging.getLogger(__name__)


class PromptExecutor:
    """Executes prompts through LLM."""

    def __init__(self, model: str = None, temperature: float = 0.7):
        # Use environment variable or auto-detect via LLM client
        import os
        self.model = model or os.getenv("LLM_MODEL", "auto")
        self.temperature = temperature
        self._client: Optional[LLMClient] = None

    @property
    def client(self) -> LLMClient:
        """Lazy initialization of LLM client."""
        if self._client is None:
            self._client = get_llm_client()
        return self._client

    async def execute(self, prompt_content: str, input_data: dict, stream: bool = False) -> dict:
        """
        Execute a prompt with input data through LLM.

        Args:
            prompt_content: The prompt template (markdown content)
            input_data: Input data to pass to the prompt
            stream: Enable streaming output

        Returns:
            dict: Execution result with generated content
            If stream=True, returns dict with 'stream' containing async generator
        """
        logger.info(f"[EXECUTOR] Starting execution: model={self.model}, stream={stream}, input_keys={list(input_data.keys())}")

        # Sanitize input_data to prevent prompt injection
        input_data = sanitize_dict(input_data)

        # Substitute variables in prompt template before parsing
        prompt_content = self._substitute_vars(prompt_content, input_data)

        # Parse prompt - extract system instruction and user query
        logger.info("[EXECUTOR] Parsing prompt...")
        system_prompt, user_prompt = self._parse_prompt(prompt_content)
        logger.info(f"[EXECUTOR] Parsed: system_len={len(system_prompt)}, user_len={len(user_prompt)}")

        # FIX: Use input_data['task'] as user prompt when no explicit user section
        task = input_data.get('task', '')
        if task and user_prompt == "Process the following input:":
            user_prompt = task
            logger.info(f"[EXECUTOR] Using task as user prompt: {task[:100]}...")

        context = {k: v for k, v in input_data.items() if k != 'task'}
        logger.info(f"[EXECUTOR] Context keys: {list(context.keys())}")

        # Streaming mode
        if stream:
            logger.info("[EXECUTOR] Using streaming mode")
            # Get the result from client.generate
            client_result = await self.client.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                context=context,
                stream=True,
            )
            # Extract the stream and usage from the result dict
            logger.info(f"[EXECUTOR] Stream result received: status={client_result.get('status')}")
            return {
                "status": "streaming",
                "stream": client_result.get("stream"),
                "usage": client_result.get("usage", {}),
                "model": client_result.get("model", self.model),
            }

        # Regular mode
        logger.info("[EXECUTOR] Using regular (non-streaming) mode")
        try:
            logger.info("[EXECUTOR] Calling client.generate()...")
            result = await self.client.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                context=context,
            )
            logger.info(f"[EXECUTOR] client.generate() returned: status={result.get('status')}, model={result.get('model')}")
        except Exception as e:
            logger.error(f"Client generate error: {type(e).__name__}: {e}")
            return {
                "status": "error",
                "model": self.model,
                "content": "",
                "error": f"{type(e).__name__}: {e}",
                "usage": {},
            }

        return {
            "status": result.get("status", "error"),
            "model": result.get("model", self.model),
            "content": result.get("content", ""),
            "error": result.get("error"),
            "usage": result.get("usage", {}),
        }

    def _parse_prompt(self, prompt_content: str) -> tuple[str, str]:
        """
        Parse markdown prompt into system and user parts.

        Expected format:
        ---
        system: System instruction here
        ---
        user: User prompt here
        ---

        Or falls back to entire content as system prompt.
        """
        lines = prompt_content.split("\n")
        system_parts = []
        user_parts = []
        current_section = None

        for line in lines:
            stripped = line.strip()

            # Check for section markers
            if stripped.startswith("---"):
                current_section = None
                continue

            # Parse section headers
            if stripped.startswith("system:"):
                current_section = "system"
                system_parts.append(stripped[8:].strip())
                continue
            elif stripped.startswith("user:"):
                current_section = "user"
                user_parts.append(stripped[6:].strip())
                continue
            elif stripped.startswith("#") and not system_parts and not user_parts:
                # First heading - treat as system prompt
                current_section = "system"
                continue

            # Add line to current section
            if current_section == "system":
                system_parts.append(line)
            elif current_section == "user":
                user_parts.append(line)
            elif current_section is None:
                # Before any section - treat as system
                system_parts.append(line)

        # Build final prompts
        system = "\n".join(system_parts).strip() if system_parts else prompt_content
        user = "\n".join(user_parts).strip() if user_parts else "Process the following input:"

        return system, user

    def _substitute_vars(self, prompt_content: str, input_data: dict) -> str:
        """
        Substitute variables in prompt template with values from input_data.

        Supported variables:
        - ${PROJECT_ROOT} - project_path from context
        - ${PROJECT_PATH} - same as PROJECT_ROOT
        - ${LANGUAGE} - language from stack (e.g., Python, JavaScript)
        - ${FRAMEWORK} - framework from stack (e.g., FastAPI, React)
        - ${APP_DIR} - inferred app directory (src/ for Python, app/ for JS, ./ for others)

        Args:
            prompt_content: The prompt template
            input_data: Context with project info

        Returns:
            str: Prompt with substituted variables
        """
        if not input_data:
            return prompt_content

        # Extract project info from context (passed via exec_context from orchestrator)
        project_path = input_data.get("project_path", ".")
        stack = input_data.get("stack", {})
        language = stack.get("language", "unknown")
        framework = stack.get("framework", "")

        # Infer APP_DIR based on language
        if language.lower().startswith("python"):
            app_dir = "src"
        elif language.lower() in ("javascript", "typescript"):
            app_dir = "app"
        elif language.lower().startswith("go"):
            app_dir = "."
        else:
            app_dir = "."

        # Perform substitutions
        substitutions = {
            "${PROJECT_ROOT}": project_path,
            "${PROJECT_PATH}": project_path,
            "${LANGUAGE}": language,
            "${FRAMEWORK}": framework,
            "${APP_DIR}": f"{project_path}/{app_dir}" if app_dir != "." else project_path,
        }

        result = prompt_content

        # First, substitute variables from input_data (handles {task}, {context}, {memory})
        for key, value in input_data.items():
            if value and isinstance(value, str):
                # Handle both ${VARIABLE} and {VARIABLE} formats
                result = result.replace(f"${{{key}}}", str(value))
                result = result.replace(f"{{{key}}}", str(value))

        # Then handle project-specific variables
        for var, value in substitutions.items():
            if value and value != "unknown" and value != ".":
                result = result.replace(var, str(value))
                # Also handle {VARIABLE} without $
                no_dollar = var.replace("${", "{").replace("}", "}")
                result = result.replace(no_dollar, str(value))

        return result

    async def execute_chain(self, prompts: list[dict], input_data: dict) -> list[dict]:
        """
        Execute a chain of prompts sequentially.

        Args:
            prompts: List of prompts to execute
            input_data: Initial input data

        Returns:
            list: Results from each prompt
        """
        results = []
        current_data = input_data.copy()

        for i, prompt_data in enumerate(prompts):
            content = prompt_data.get("content", "")
            prompt_name = prompt_data.get("name", f"step_{i}")

            logger.info(f"Chain step {i + 1}/{len(prompts)}: {prompt_name}")

            result = await self.execute(content, current_data)
            results.append({
                "step": i + 1,
                "name": prompt_name,
                "result": result,
            })

            # Pass output as context for next step
            if result.get("status") == "success" and result.get("content"):
                current_data["previous_output"] = result["content"]
                current_data[f"step_{i}_result"] = result["content"]

        return results