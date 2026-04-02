# src/services/checkpoint_executor.py
"""
Checkpoint-based executor for reliable code generation.

Solves the problem: "p9i generated code but didn't write files"
- Phase 1: Generate + Validate (in-memory)
- Phase 2: Write files (durably)
- Checkpoint recovery on failure
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


# Patterns for parsing bash commands from LLM output
BASH_BLOCK_PATTERN = re.compile(
    r"```(?:bash|sh|shell)\s*\n(.*?)```",
    re.DOTALL | re.IGNORECASE
)
BASH_INLINE_PATTERN = re.compile(
    r"^\s*(?:\$\s*|>)\s+(.+)$",
    re.MULTILINE
)

# Checkpoint storage directory
CHECKPOINT_DIR = Path(__file__).parent.parent.parent / "memory" / "checkpoints"


@dataclass
class ExecutionState:
    """State captured at each checkpoint."""
    phase: str  # "generating", "validating", "parsing", "executing_bash", "writing", "complete"
    request: str
    generated_content: str = ""
    planned_files: dict[str, str] = field(default_factory=dict)
    planned_bash_commands: list[str] = field(default_factory=list)
    bash_results: list[dict] = field(default_factory=list)
    written_files: set[str] = field(default_factory=set)
    validation_errors: list[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)


class CheckpointManager:
    """Manages execution checkpoints for recovery."""

    def __init__(self, storage_dir: Path = CHECKPOINT_DIR):
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _get_checkpoint_path(self, execution_id: str) -> Path:
        """Get path for checkpoint file."""
        return self.storage_dir / f"{execution_id}.json"

    def save(self, execution_id: str, state: ExecutionState) -> None:
        """Save checkpoint state."""
        try:
            data = {
                "execution_id": execution_id,
                "phase": state.phase,
                "request": state.request,
                "generated_content": state.generated_content,
                "planned_files": state.planned_files,
                "written_files": list(state.written_files),
                "validation_errors": state.validation_errors,
                "timestamp": state.timestamp,
            }
            path = self._get_checkpoint_path(execution_id)
            path.write_text(json.dumps(data, indent=2))
            logger.debug(f"Checkpoint saved: {execution_id} [{state.phase}]")
        except Exception as e:
            logger.error(f"Failed to save checkpoint {execution_id}: {e}")

    def load(self, execution_id: str) -> Optional[ExecutionState]:
        """Load checkpoint state."""
        try:
            path = self._get_checkpoint_path(execution_id)
            if not path.exists():
                return None
            data = json.loads(path.read_text())
            return ExecutionState(
                phase=data["phase"],
                request=data["request"],
                generated_content=data.get("generated_content", ""),
                planned_files=data.get("planned_files", {}),
                written_files=set(data.get("written_files", [])),
                validation_errors=data.get("validation_errors", []),
                timestamp=data.get("timestamp", 0),
            )
        except Exception as e:
            logger.error(f"Failed to load checkpoint {execution_id}: {e}")
            return None

    def complete(self, execution_id: str) -> None:
        """Remove checkpoint after successful completion."""
        try:
            path = self._get_checkpoint_path(execution_id)
            if path.exists():
                path.unlink()
                logger.debug(f"Checkpoint completed and removed: {execution_id}")
        except Exception as e:
            logger.error(f"Failed to remove checkpoint {execution_id}: {e}")

    def list_pending(self) -> list[str]:
        """List all pending (incomplete) checkpoints."""
        try:
            return [p.stem for p in self.storage_dir.glob("*.json")]
        except Exception:
            return []


class CheckpointExecutor:
    """
    Executor with checkpoint-based pipeline.

    Problem: LLM generates code → validation blocks → files never written
    Solution: Checkpoint at each phase, recover on failure
    """

    def __init__(self):
        self.checkpoint_manager = CheckpointManager()
        self._metrics = {
            "generated_not_written": 0,
            "validation_failures": 0,
            "write_failures": 0,
            "checkpoint_recoveries": 0,
        }

    def _generate_execution_id(self, request: str) -> str:
        """Generate unique ID for this execution."""
        return hashlib.sha256(f"{request}:{time.time()}".encode()).hexdigest()[:16]

    async def execute_with_checkpoint(
        self,
        prompt: str,
        request: str,
        context: dict,
        write_to_disk: bool = True,
    ) -> dict:
        """
        Execute with checkpoint-based pipeline.

        Phase 1: Generate + Validate (in-memory)
        Phase 2: Write files (durably)
        """
        execution_id = self._generate_execution_id(request)
        state = ExecutionState(phase="generating", request=request)

        # Load executor lazily
        from src.services.executor import PromptExecutor
        executor = PromptExecutor()

        try:
            # Phase 1: Generate
            logger.info(f"[CHECKPOINT] {execution_id}: Generating...")
            state.phase = "generating"
            self.checkpoint_manager.save(execution_id, state)

            result = await executor.execute(prompt, {**context, "task": request})
            generated_content = result.get("content", "")

            if not generated_content:
                return {
                    "status": "error",
                    "error": "No content generated",
                    "execution_id": execution_id,
                }

            state.generated_content = generated_content

            # Phase 2: Validate
            logger.info(f"[CHECKPOINT] {execution_id}: Validating...")
            state.phase = "validating"
            self.checkpoint_manager.save(execution_id, state)

            validation_result = self._validate_output(generated_content)
            if not validation_result["valid"]:
                state.validation_errors = validation_result["errors"]
                state.phase = "validation_failed"
                self.checkpoint_manager.save(execution_id, state)

                self._metrics["validation_failures"] += 1
                logger.error(f"Validation failed: {validation_result['errors']}")

                return {
                    "status": "validation_error",
                    "errors": validation_result["errors"],
                    "execution_id": execution_id,
                    "generated_content": generated_content,
                }

            # Phase 3: Parse files from output
            logger.info(f"[CHECKPOINT] {execution_id}: Parsing files...")
            state.phase = "parsing"
            self.checkpoint_manager.save(execution_id, state)

            planned_files = self._parse_files_from_output(generated_content)
            state.planned_files = planned_files

            # Also parse bash commands from output
            bash_commands = self._parse_bash_commands_from_output(generated_content)
            state.planned_bash_commands = bash_commands

            if write_to_disk and planned_files:
                # Phase 4: Write files FIRST
                logger.info(f"[CHECKPOINT] {execution_id}: Writing {len(planned_files)} files...")
                state.phase = "writing"
                self.checkpoint_manager.save(execution_id, state)

                write_result = await self._write_files(planned_files)
                state.written_files = write_result["written"]

                if write_result["failed"]:
                    self._metrics["write_failures"] += 1
                    logger.error(f"Write failures: {write_result['failed']}")

            # Phase 3.5: Execute bash commands AFTER files are written
            failed_commands = []  # Initialize to avoid reference errors
            if bash_commands:
                logger.info(f"[CHECKPOINT] {execution_id}: Executing {len(bash_commands)} bash commands...")
                state.phase = "executing_bash"
                self.checkpoint_manager.save(execution_id, state)

                bash_results = await self._execute_bash_commands(bash_commands)
                state.bash_results = bash_results

                # Check if any commands failed
                failed_commands = [r for r in bash_results if not r["success"]]
                if failed_commands:
                    logger.warning(f"Bash command failures: {len(failed_commands)}")
                    # Include failure info in state for response
                    state.validation_errors.extend([f"Bash failed: {r['command']}" for r in failed_commands])

            if write_to_disk and planned_files:
                state.phase = "complete"
                self.checkpoint_manager.save(execution_id, state)
                self.checkpoint_manager.complete(execution_id)

                # Check for any bash failures - if bash failed, the overall status should reflect error
                if bash_commands and failed_commands:
                    return {
                        "status": "error",
                        "error": f"Bash commands failed: {len(failed_commands)}",
                        "content": generated_content,
                        "files": write_result,
                        "bash_results": state.bash_results,
                        "execution_id": execution_id,
                    }

                return {
                    "status": "success",
                    "content": generated_content,
                    "files": write_result,
                    "bash_results": state.bash_results,
                    "execution_id": execution_id,
                }
            else:
                # No files to write - just return content (but still execute bash)
                state.phase = "complete"
                self.checkpoint_manager.save(execution_id, state)
                self.checkpoint_manager.complete(execution_id)

                # Check for any bash failures
                if failed_commands:
                    return {
                        "status": "error",
                        "error": f"Bash commands failed: {len(failed_commands)}",
                        "content": generated_content,
                        "files": {"written": [], "failed": []},
                        "bash_results": state.bash_results,
                        "execution_id": execution_id,
                    }

                return {
                    "status": "success",
                    "content": generated_content,
                    "files": {"written": [], "failed": []},
                    "bash_results": state.bash_results,
                    "execution_id": execution_id,
                }

        except Exception as e:
            logger.error(f"Execution error: {e}")
            state.phase = "error"
            state.validation_errors.append(str(e))
            self.checkpoint_manager.save(execution_id, state)
            return {
                "status": "error",
                "error": str(e),
                "execution_id": execution_id,
            }

    def _validate_output(self, content: str) -> dict:
        """
        Validate generated output.

        Returns:
            {"valid": bool, "errors": list[str]}
        """
        errors = []

        # Check minimum length
        if len(content) < 50:
            errors.append("Content too short (< 50 chars)")

        # Check for placeholder patterns
        placeholders = ["[TODO]", "[FIXME]", "TEMPLATE", "PLACEHOLDER"]
        for placeholder in placeholders:
            if placeholder in content:
                errors.append(f"Contains placeholder: {placeholder}")

        # Check for code-like content (if it looks like code)
        # Only validate code density if output has many code-like lines
        # For text/markdown outputs (architect reports), this check is too strict
        lines = content.split("\n")
        code_lines = sum(1 for line in lines if "{" in line or "def " in line or "class " in line or "import " in line)
        # Only fail if: lots of code lines AND very low density (looks like template)
        # For markdown/text reports, low code line density is normal
        if code_lines > 10 and code_lines / len(lines) < 0.05:
            errors.append("Low code density (possible template)")

        return {"valid": len(errors) == 0, "errors": errors}

    def _parse_bash_commands_from_output(self, content: str) -> list[str]:
        """
        Parse bash commands from LLM output.

        Expected formats:
        - ```bash
          command1
          command2
          ```
        - $ command1
        - > command1
        """
        commands = []

        # Extract from fenced code blocks
        for match in BASH_BLOCK_PATTERN.finditer(content):
            block = match.group(1).strip()
            for line in block.split("\n"):
                line = line.strip()
                if line and not line.startswith("#"):
                    commands.append(line)

        # Extract inline commands
        for match in BASH_INLINE_PATTERN.finditer(content):
            cmd = match.group(1).strip()
            if cmd and not cmd.startswith("#"):
                commands.append(cmd)

        return commands

    async def _execute_bash_commands(self, commands: list[str]) -> list[dict]:
        """
        Execute bash commands and return results.

        Returns:
            [{"command": str, "returncode": int, "stdout": str, "stderr": str, "success": bool}, ...]
        """
        results = []
        for cmd in commands:
            try:
                proc = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=300
                )
                result = {
                    "command": cmd,
                    "returncode": proc.returncode,
                    "stdout": stdout.decode() if stdout else "",
                    "stderr": stderr.decode() if stderr else "",
                    "success": proc.returncode == 0,
                }
            except asyncio.TimeoutExpired:
                result = {
                    "command": cmd,
                    "returncode": -1,
                    "stdout": "",
                    "stderr": "Command timed out after 300 seconds",
                    "success": False,
                    "error": "timeout",
                }
            except Exception as e:
                result = {
                    "command": cmd,
                    "returncode": -1,
                    "stdout": "",
                    "stderr": str(e),
                    "success": False,
                    "error": type(e).__name__,
                }
            results.append(result)
            logger.info(f"Bash executed: {cmd} -> {result['returncode']}")

        return results

    def _is_comment_line(self, line: str) -> bool:
        """Check if line is a code comment (not a file path)."""
        stripped = line.strip()
        # Skip comment-only lines: // comment, /* comment */, <!-- comment -->
        if stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("<!--"):
            return True
        return False

    def _is_valid_filename(self, filename: str) -> bool:
        """Check if filename is a valid file path (not a comment)."""
        if not filename:
            return False
        stripped = filename.strip()
        # Reject comment-style paths: // path, /* path
        if stripped.startswith("//") or stripped.startswith("/*"):
            return False
        # Must have valid file extension
        valid_exts = (".py", ".js", ".ts", ".tsx", ".jsx", ".md", ".yaml", ".yml", ".json", ".txt", ".sh", ".bash", ".go", ".rs", ".java", ".cpp", ".c", ".h", ".hpp", ".css", ".html", ".vue", ".svelte")
        if not any(stripped.endswith(ext) for ext in valid_exts):
            return False
        return True

    def _parse_files_from_output(self, content: str) -> dict[str, str]:
        """
        Parse file paths and content from LLM output.

        Expected formats:
        - ```python filename.py
          ...
          ```
        - ```python\nfilename.py\n...```
        - File: path/to/file.py
          ```python
          ...
          ```
        """
        import re

        files = {}

        # Pattern 1: Code block with filename - flexible spacing
        # Matches: ```python filename.ext ...``` or ```python\nfilename.ext\n...```
        code_block_pattern = r"```(\w+)\s*\n?(?:([^\n]+?)\s*\n)?(.*?)```"
        for match in re.finditer(code_block_pattern, content, re.DOTALL):
            lang = match.group(1)
            filename = match.group(2).strip() if match.group(2) else ""
            file_content = match.group(3).strip()
            if file_content:
                # If no filename but content looks like a path, try to extract
                if not filename:
                    first_line = file_content.split("\n")[0].strip()
                    # Skip comment lines - // or /* at start means it's not a path
                    if first_line and not self._is_comment_line(first_line):
                        if "/" in first_line or first_line.endswith((".py", ".js", ".ts", ".tsx")):
                            filename = first_line
                            file_content = "\n".join(file_content.split("\n")[1:])
                # Validate filename is not a comment
                if filename and self._is_valid_filename(filename):
                    files[filename] = file_content

        # Pattern 2: File: path/to/file (case insensitive, supports Russian)
        file_path_pattern = r"(?:File|Файл):\s*(.+?)(?:\n|$)```(\w+)?\n?(.*?)```"
        for match in re.finditer(file_path_pattern, content, re.DOTALL):
            filename = match.group(1).strip()
            file_content = match.group(3).strip()
            if filename and file_content and self._is_valid_filename(filename):
                files[filename] = file_content

        return files

    async def _write_files(self, files: dict[str, str]) -> dict:
        """
        Write files to disk with tracking.

        Returns:
            {"written": list[str], "failed": dict[str, str]}
        """
        written = []
        failed = {}

        for filename, content in files.items():
            try:
                # Determine base path (use current directory or project root)
                base_path = Path.cwd()

                # Handle path traversal - only allow relative paths
                file_path = (base_path / filename).resolve()
                if not str(file_path).startswith(str(base_path)):
                    raise ValueError(f"Path traversal blocked: {filename}")

                # Create parent directories
                file_path.parent.mkdir(parents=True, exist_ok=True)

                # Write file
                file_path.write_text(content, encoding="utf-8")
                written.append(filename)
                logger.info(f"File written: {filename}")

            except Exception as e:
                failed[filename] = str(e)
                logger.error(f"Failed to write {filename}: {e}")

        return {"written": written, "failed": failed}

    def recover_from_checkpoint(self, execution_id: str) -> Optional[dict]:
        """Attempt to recover from a failed checkpoint."""
        state = self.checkpoint_manager.load(execution_id)
        if not state:
            return None

        self._metrics["checkpoint_recoveries"] += 1

        # If we were in writing phase but didn't complete, try again
        if state.phase == "writing" and state.planned_files:
            logger.info(f"Recovering checkpoint {execution_id}: retry writing {len(state.planned_files)} files")

            # Re-attempt write
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(self._write_files(state.planned_files))
                return {
                    "status": "recovered",
                    "files": result,
                    "execution_id": execution_id,
                }
            finally:
                loop.close()

        return None

    def get_metrics(self) -> dict:
        """Get execution metrics."""
        return self._metrics.copy()


# Global instance
_checkpoint_executor: Optional[CheckpointExecutor] = None


def get_checkpoint_executor() -> CheckpointExecutor:
    """Get or create global checkpoint executor."""
    global _checkpoint_executor
    if _checkpoint_executor is None:
        _checkpoint_executor = CheckpointExecutor()
    return _checkpoint_executor