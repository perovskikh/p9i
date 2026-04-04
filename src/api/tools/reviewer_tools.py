"""
Reviewer MCP Tools - Provides code review as MCP tools.

These tools wrap review functionality for use by the Reviewer Agent.
They provide cached access to code analysis and security scanning.

Based on Claude Code simplify.ts and verificationAgent patterns:
- READ-ONLY operations only (except verification which can run tests)
- 3-phase parallel review: Reuse, Quality, Efficiency
- Security vulnerability scanning
- Adversarial testing with VERDICT output
"""

import hashlib
import logging
import re
import subprocess
import time
from typing import Any, Dict, List, Optional, Tuple

from src.services.reviewer_cache import get_reviewer_cache_manager, ReviewerCacheManager
from src.services.explorer_cache import hash_query

logger = logging.getLogger(__name__)


# Common vulnerability patterns for security scanning
VULNERABILITY_PATTERNS = {
    "sql_injection": [
        (r'f"SELECT.*\{', "SQL f-string interpolation"),
        (r'f"INSERT.*\{', "SQL f-string interpolation"),
        (r'f"UPDATE.*\{', "SQL f-string interpolation"),
        (r'f"DELETE.*\{', "SQL f-string interpolation"),
        (r'"\s*\+\s*.*\+\s*".*SELECT', "SQL string concatenation"),
        (r'"\s*%\s*.*".*%s.*SELECT', "SQL % formatting"),
    ],
    "command_injection": [
        (r'os\.system\(', "os.system call"),
        (r'subprocess\.(call|run|exec)\(.*shell=True', "subprocess with shell=True"),
        (r'eval\(', "eval() call"),
        (r'exec\(', "exec() call"),
    ],
    "hardcoded_secrets": [
        (r'API_KEY\s*=\s*["\']sk[-_]', "Hardcoded API key"),
        (r'PASSWORD\s*=\s*["\'][^"\']{6,}', "Hardcoded password"),
        (r'SECRET\s*=\s*["\'][^"\']{16,}', "Hardcoded secret"),
        (r'TOKEN\s*=\s*["\']eyJ', "Hardcoded JWT token"),
    ],
    "path_traversal": [
        (r'open\([^)]*\+[^)]*\)', "Potential path traversal"),
        (r'open\(.*\(user|file|path', "Unvalidated file open"),
    ],
    "auth_bypass": [
        (r'if\s+user\.is_admin:', "Missing role check"),
        (r'\.check_permissions\s*\(\s*\)', "Empty permission check"),
    ],
}

# Anti-patterns for quality review
QUALITY_PATTERNS = {
    "redundant_state": [
        (r'cached_\w+\s*=', "Redundant cached value"),
        (r'state\s*=\s*self\.state', "State duplication"),
    ],
    "copy_paste": [
        (r'for .* in .*:\s*\n\s*for .* in .*:', "Nested loops (possible N+1)"),
    ],
    "stringly_typed": [
        (r'if .* == ["\']\w+["\']:', "String comparison instead of constant"),
    ],
}


class ReviewerTools:
    """
    Reviewer tools for MCP integration.

    These tools provide code review capabilities:
    - reviewer_diff: Get git diff for review
    - reviewer_search: Search vulnerability/anti-patterns
    - reviewer_security: Security vulnerability scan
    - reviewer_quality: Quality metrics
    - reviewer_metrics: Code complexity analysis
    - reviewer_verify: Run verification with VERDICT
    """

    def __init__(self, project_path: str = "."):
        self.project_path = project_path
        self._cache: Optional[ReviewerCacheManager] = None

    async def _ensure_cache(self) -> None:
        """Ensure Redis cache is initialized."""
        if self._cache is None:
            self._cache = get_reviewer_cache_manager()
            if self._cache.redis is None:
                # Cache not initialized with Redis yet, will be set during server startup
                pass

    async def reviewer_diff(
        self,
        scope: str = "unstaged",
        file_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get git diff for review.

        Args:
            scope: "unstaged", "staged", "HEAD", or "branch"
            file_path: Optional specific file to diff

        Returns:
            Dict with:
            - diff: Git diff output
            - files: List of changed files
            - lines: Total lines changed
            - scope: The scope used
            - cached: Whether result was from cache
        """
        await self._ensure_cache()

        # Build cache key
        cache_key = f"{self.project_path}:diff:{scope}:{file_path or ''}"
        query_hash = hash_query(cache_key)

        # Check Redis cache (diff changes frequently, short TTL)
        if self._cache and self._cache.redis:
            cached = await self._cache.get_diff_result(self.project_path, query_hash)
            if cached is not None:
                cached["cached"] = True
                return cached

        try:
            if scope == "unstaged":
                cmd = ["git", "diff"]
            elif scope == "staged":
                cmd = ["git", "diff", "--cached"]
            elif scope == "HEAD":
                cmd = ["git", "diff", "HEAD~1"]
            elif file_path:
                cmd = ["git", "diff", "HEAD~1", "--", file_path]
            else:
                cmd = ["git", "diff", "HEAD~1"]

            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=30,
            )

            diff_text = result.stdout
            files = set()
            lines_added = 0
            lines_deleted = 0

            for line in diff_text.split("\n"):
                if line.startswith("+++"):
                    match = re.search(r"\+\+\+ b/(.+)", line)
                    if match:
                        files.add(match.group(1))
                elif line.startswith("@@"):
                    match = re.search(r"\+(\d+),?(\d*)", line)
                    if match:
                        added = int(match.group(1) or 0)
                        deleted = int(match.group(2) or 0)
                        lines_added += added
                        lines_deleted += deleted

            result_data = {
                "diff": diff_text,
                "files": list(files),
                "files_count": len(files),
                "lines_added": lines_added,
                "lines_deleted": lines_deleted,
                "scope": scope,
                "success": True,
            }

            # Cache result in Redis
            if self._cache and self._cache.redis:
                await self._cache.set_diff_result(self.project_path, query_hash, result_data)

            result_data["cached"] = False
            return result_data

        except subprocess.TimeoutExpired:
            return {"error": "Git command timeout", "success": False}
        except Exception as e:
            return {"error": str(e), "success": False}

    async def reviewer_search(
        self,
        query: str,
        file_pattern: str = "*.py",
    ) -> Dict[str, Any]:
        """
        Search code for vulnerability patterns or anti-patterns.

        Args:
            query: Pattern type ("sql_injection", "hardcoded_secrets", etc.)
                  or custom search term
            file_pattern: File pattern to search (default: *.py)

        Returns:
            Dict with:
            - results: List of {file, line, pattern, context}
            - count: Number of findings
            - cached: Whether result was from cache
        """
        await self._ensure_cache()

        # Build cache key
        cache_key = f"{self.project_path}:search:{query}:{file_pattern}"
        query_hash = hash_query(cache_key)

        # Check Redis cache
        if self._cache and self._cache.redis:
            cached = await self._cache.get_search_result(self.project_path, query_hash)
            if cached is not None:
                return {
                    "results": cached,
                    "cached": True,
                    "count": len(cached),
                    "query": query,
                }

        import glob

        results = []

        # Determine what to search for
        if query in VULNERABILITY_PATTERNS:
            patterns = VULNERABILITY_PATTERNS[query]
        elif query in QUALITY_PATTERNS:
            patterns = QUALITY_PATTERNS[query]
        else:
            # Custom search - treat as regex
            patterns = [(query, f"Custom: {query}")]

        # Search files
        search_files = glob.glob(
            f"{self.project_path}/**/{file_pattern}",
            recursive=True,
        )

        exclude_dirs = {"node_modules", ".git", "__pycache__", "venv", ".venv", "dist", "build"}
        search_files = [
            f for f in search_files
            if not any(excl in f for excl in exclude_dirs)
        ]

        for file_path in search_files:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()

                for line_num, line in enumerate(lines, 1):
                    for pattern, description in patterns:
                        if re.search(pattern, line):
                            rel_path = file_path.replace(self.project_path + "/", "")
                            results.append({
                                "file": rel_path,
                                "line": line_num,
                                "pattern": description,
                                "code": line.strip(),
                                "context": f"{lines[max(0, line_num-2):line_num+1]}",
                            })
            except Exception:
                continue

        result_data = {
            "results": results[:100],  # Limit results
            "count": len(results),
            "query": query,
            "files_searched": len(search_files),
        }

        # Cache result in Redis
        if self._cache and self._cache.redis:
            await self._cache.set_search_result(self.project_path, query_hash, results)

        result_data["cached"] = False

        return result_data

    async def reviewer_security(
        self,
        file_path: str,
    ) -> Dict[str, Any]:
        """
        Security vulnerability scan for a specific file.

        Args:
            file_path: Path to file to scan

        Returns:
            Dict with:
            - issues: List of {severity, category, line, description, confidence}
            - score: Overall security score (0-100)
            - recommendations: List of fixes
            - cached: Whether result was from cache
        """
        await self._ensure_cache()

        # Check Redis cache
        if self._cache and self._cache.redis:
            cached = await self._cache.get_security_result(self.project_path, file_path)
            if cached is not None:
                cached["cached"] = True
                return cached

        issues = []

        try:
            with open(f"{self.project_path}/{file_path}", "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")

            # Check each vulnerability category
            for category, patterns in VULNERABILITY_PATTERNS.items():
                for pattern, description in patterns:
                    for line_num, line in enumerate(lines, 1):
                        if re.search(pattern, line):
                            # Calculate confidence based on pattern
                            if category == "hardcoded_secrets":
                                confidence = 95
                            elif category == "sql_injection" and "f\"" in line:
                                confidence = 98
                            else:
                                confidence = 85

                            issues.append({
                                "severity": "CRITICAL" if confidence >= 95 else "HIGH",
                                "category": category,
                                "line": line_num,
                                "description": description,
                                "code": line.strip(),
                                "confidence": confidence,
                                "recommendation": f"Use parameterized query / remove hardcoded value",
                            })

        except Exception as e:
            return {"error": str(e), "issues": [], "score": 100}

        # Calculate score
        if not issues:
            score = 100
        else:
            critical = sum(1 for i in issues if i["severity"] == "CRITICAL")
            high = sum(1 for i in issues if i["severity"] == "HIGH")
            score = max(0, 100 - (critical * 20) - (high * 10))

        result_data = {
            "file": file_path,
            "issues": issues,
            "issue_count": len(issues),
            "score": score,
            "recommendations": [i["recommendation"] for i in issues],
        }

        # Cache result in Redis
        if self._cache and self._cache.redis:
            await self._cache.set_security_result(self.project_path, file_path, result_data)

        result_data["cached"] = False

        return result_data

    async def reviewer_quality(
        self,
        file_path: str,
    ) -> Dict[str, Any]:
        """
        Quality metrics for a file.

        Args:
            file_path: Path to file to analyze

        Returns:
            Dict with:
            - issues: List of quality issues
            - metrics: Quality metrics (complexity, duplication, etc.)
            - cached: Whether result was from cache
        """
        await self._ensure_cache()

        # Check Redis cache
        if self._cache and self._cache.redis:
            cached = await self._cache.get_quality_result(self.project_path, file_path)
            if cached is not None:
                cached["cached"] = True
                return cached

        issues = []

        try:
            with open(f"{self.project_path}/{file_path}", "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")

            # Check quality patterns
            for category, patterns in QUALITY_PATTERNS.items():
                for pattern, description in patterns:
                    for line_num, line in enumerate(lines, 1):
                        if re.search(pattern, line):
                            issues.append({
                                "category": category,
                                "line": line_num,
                                "description": description,
                                "code": line.strip(),
                                "severity": "INFO",
                            })

            # Calculate basic metrics
            loc = len([l for l in lines if l.strip() and not l.strip().startswith("#")])
            comment_lines = len([l for l in lines if l.strip().startswith("#")])
            blank_lines = len([l for l in lines if not l.strip()])

            # Count functions
            functions = len(re.findall(r'def \w+\(', content))
            classes = len(re.findall(r'class \w+', content))

            # Calculate complexity (rough)
            complexity = len(re.findall(r'\b(if|elif|for|while|and|or)\b', content))

            metrics = {
                "loc": loc,
                "comment_lines": comment_lines,
                "blank_lines": blank_lines,
                "functions": functions,
                "classes": classes,
                "cyclomatic_complexity": complexity,
            }

        except Exception as e:
            return {"error": str(e), "issues": [], "metrics": {}}

        result_data = {
            "file": file_path,
            "issues": issues,
            "issue_count": len(issues),
            "metrics": metrics,
        }

        # Cache result in Redis
        if self._cache and self._cache.redis:
            await self._cache.set_quality_result(self.project_path, file_path, result_data)

        result_data["cached"] = False

        return result_data

    async def reviewer_metrics(
        self,
        file_path: str,
    ) -> Dict[str, Any]:
        """
        Code complexity metrics.

        Args:
            file_path: Path to file

        Returns:
            Dict with:
            - complexity: Cyclomatic complexity score
            - coupling: Fan-in/fan-out estimate
            - cohesion: Module cohesion estimate
            - cached: Whether result was from cache
        """
        await self._ensure_cache()

        # Check Redis cache
        if self._cache and self._cache.redis:
            cached = await self._cache.get_metrics_result(self.project_path, file_path)
            if cached is not None:
                cached["cached"] = True
                return cached

        try:
            with open(f"{self.project_path}/{file_path}", "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")

            # Cyclomatic complexity
            keywords = ["if", "elif", "for", "while", "except", "and", "or"]
            complexity = 1  # Base complexity
            for line in lines:
                for kw in keywords:
                    if re.search(rf'\b{kw}\b', line):
                        complexity += 1

            # Count imports as fan-out
            imports = len(re.findall(r'^import |^from ', content, re.MULTILINE))

            # Count function definitions as internal complexity
            functions = len(re.findall(r'def \w+\(', content))

            result_data = {
                "file": file_path,
                "cyclomatic_complexity": complexity,
                "fan_out": imports,
                "functions": functions,
                "lines": len(lines),
                "grade": self._complexity_grade(complexity),
            }

            # Cache result in Redis
            if self._cache and self._cache.redis:
                await self._cache.set_metrics_result(self.project_path, file_path, result_data)

            result_data["cached"] = False

            return result_data

        except Exception as e:
            return {"error": str(e), "success": False}

    async def reviewer_verify(
        self,
        test_command: str,
        expected: str,
        adversarial: bool = False,
    ) -> Dict[str, Any]:
        """
        Run verification test with adversarial probing.

        Args:
            test_command: Command to run
            expected: Expected output
            adversarial: Whether this is an adversarial probe

        Returns:
            Dict with:
            - command: Command run
            - actual: Actual output
            - expected: Expected output
            - passed: Whether test passed
            - verdict: PASS/FAIL/PARTIAL
        """
        try:
            result = subprocess.run(
                test_command,
                shell=True,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=30,
            )

            actual = result.stdout.strip()
            passed = expected in actual or expected.lower() in actual.lower()

            verdict = "PASS" if passed else "FAIL"

            return {
                "command": test_command,
                "expected": expected,
                "actual": actual,
                "exit_code": result.returncode,
                "passed": passed,
                "verdict": verdict,
                "adversarial": adversarial,
                "stderr": result.stderr[:500] if result.stderr else "",
            }

        except subprocess.TimeoutExpired:
            return {
                "command": test_command,
                "expected": expected,
                "actual": "TIMEOUT",
                "passed": False,
                "verdict": "FAIL",
                "adversarial": adversarial,
                "error": "Command timeout",
            }
        except Exception as e:
            return {
                "command": test_command,
                "expected": expected,
                "actual": f"ERROR: {str(e)}",
                "passed": False,
                "verdict": "FAIL",
                "adversarial": adversarial,
                "error": str(e),
            }

    async def reviewer_reuse_analysis(
        self,
        symbol_name: str,
    ) -> Dict[str, Any]:
        """
        Analyze symbol for potential reuse from existing code.
        Uses explorer_search to find similar symbols.

        Args:
            symbol_name: Name of symbol to analyze for reuse

        Returns:
            Dict with:
            - symbol: The symbol analyzed
            - suggestions: List of similar symbols found
            - cached: Whether result was from cache
        """
        await self._ensure_cache()

        # Build cache key
        cache_key = f"{self.project_path}:reuse:{symbol_name}"
        query_hash = hash_query(cache_key)

        # Check Redis cache (reuse analysis uses search TTL)
        if self._cache and self._cache.redis:
            cached = await self._cache.get_search_result(self.project_path, query_hash)
            if cached is not None:
                return {
                    "symbol": symbol_name,
                    "suggestions": cached,
                    "cached": True,
                }

        # Use explorer_search to find similar symbols
        try:
            from src.api.tools.explorer_tools import get_explorer_tools

            explorer = get_explorer_tools(self.project_path)

            # Search for the symbol in the codebase
            search_result = await explorer.explorer_search(
                query=symbol_name,
                file_pattern="*.py"
            )

            suggestions = []
            for result in search_result.get("results", []):
                # Filter out the symbol itself
                if result.get("name") != symbol_name:
                    suggestions.append({
                        "file": result.get("file"),
                        "line": result.get("line"),
                        "name": result.get("name"),
                        "type": result.get("type"),
                        "context": result.get("context"),
                    })

            result_data = {
                "symbol": symbol_name,
                "suggestions": suggestions[:10],  # Limit to 10 suggestions
                "count": len(suggestions),
            }

            # Cache result in Redis
            if self._cache and self._cache.redis:
                await self._cache.set_search_result(self.project_path, query_hash, suggestions)

            result_data["cached"] = False
            return result_data

        except Exception as e:
            logger.error(f"Reuse analysis error: {e}")
            return {
                "symbol": symbol_name,
                "suggestions": [],
                "error": str(e),
                "cached": False,
            }

    def _complexity_grade(self, complexity: int) -> str:
        """Convert complexity to letter grade."""
        if complexity <= 10:
            return "A (Low risk)"
        elif complexity <= 20:
            return "B (Moderate)"
        elif complexity <= 50:
            return "C (High risk)"
        else:
            return "D (Very high risk)"


# Global instance per project
_reviewer_tools: Dict[str, ReviewerTools] = {}


def get_reviewer_tools(project_path: str = ".") -> ReviewerTools:
    """Get or create ReviewerTools for project."""
    if project_path not in _reviewer_tools:
        _reviewer_tools[project_path] = ReviewerTools(project_path)
    return _reviewer_tools[project_path]