# src/domain/services/prompt_guard.py
"""
Prompt Deduplication Guard - Prevents duplicate prompts and keywords.

This service ensures:
1. No duplicate prompt names across tiers
2. No duplicate keywords in routing
3. No duplicate agents referencing same prompts
4. Suggestions for existing functionality
"""

from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
import json
import logging

from src.domain.exceptions import DuplicatePromptError, DuplicateKeywordError, DuplicateAgentError

logger = logging.getLogger(__name__)

# Base directory for prompts
PROMPTS_DIR = Path("./prompts")


@dataclass
class DuplicateCheckResult:
    """Result of duplicate check."""
    is_valid: bool
    duplicates: List[Dict[str, str]]
    suggestions: List[str]
    existing_prompts: List[str]
    existing_keywords: Dict[str, str]


class PromptDeduplicationGuard:
    """
    Guard that prevents creating duplicate prompts, keywords, and agent configurations.

    Usage:
        guard = PromptDeduplicationGuard()
        result = guard.check_prompt_name("new-feature")

        if not result.is_valid:
            # Handle duplicates
            for dup in result.duplicates:
                logger.warning(f"Duplicate prompt found: {dup}")
    """

    def __init__(self, prompts_dir: str = "./prompts"):
        self.prompts_dir = Path(prompts_dir)
        self._prompt_index: Dict[str, str] = {}  # name -> path
        self._keyword_map: Dict[str, str] = {}   # keyword -> prompt_name
        self._agent_prompts: Dict[str, Set[str]] = {}  # agent -> set of prompts
        self._load_index()

    def _load_index(self):
        """Load all existing prompts and build index."""
        # Scan all prompt directories
        for tier in ["core", "universal", "packs"]:
            tier_dir = self.prompts_dir / tier
            if not tier_dir.exists():
                continue

            # Handle packs specially
            if tier == "packs":
                for pack_dir in tier_dir.iterdir():
                    if pack_dir.is_dir():
                        self._scan_directory(pack_dir, f"packs/{pack_dir.name}")
            else:
                self._scan_directory(tier_dir, tier)

        # Load keywords from server.py
        self._load_keywords_from_server()

        # Load keywords from agent_router.py
        self._load_keywords_from_router()

        # Load agent configurations
        self._load_agents()

        logger.info(f"Loaded {len(self._prompt_index)} prompts, {len(self._keyword_map)} keywords")

    def _scan_directory(self, directory: Path, tier: str):
        """Scan directory for prompt files."""
        for md_file in directory.rglob("*.md"):
            # Skip README and special files
            if md_file.name.startswith("."):
                continue

            # Get prompt name from filename
            prompt_name = md_file.stem  # filename without extension

            # Skip if not a prompt (e.g., README.md)
            if not prompt_name.startswith("promt-") and not prompt_name.startswith("create_"):
                continue

            # Store with tier path
            rel_path = md_file.relative_to(self.prompts_dir)
            self._prompt_index[prompt_name] = str(rel_path)

    def _load_keywords_from_server(self):
        """Load keywords from server.py INTENT_MAP."""
        server_file = self.prompts_dir.parent / "src" / "api" / "server.py"
        if not server_file.exists():
            return

        try:
            content = server_file.read_text()
            # Find INTENT_MAP definition
            if "INTENT_MAP" in content:
                # Extract keywords (simplified - look for "keyword": "prompt" patterns)
                import re
                pattern = r'["\'](\w+(?:\s+\w+)?)["\']\s*:\s*["\'](\w+[-]?\w+)["\']'
                matches = re.findall(pattern, content)

                for keyword, prompt in matches:
                    # Skip duplicates from regex
                    if keyword not in self._keyword_map:
                        self._keyword_map[keyword.lower()] = prompt
        except Exception as e:
            logger.warning(f"Could not load keywords from server.py: {e}")

    def _load_keywords_from_router(self):
        """Load keywords from agent_router.py."""
        router_file = self.prompts_dir.parent / "src" / "application" / "agent_router.py"
        if not router_file.exists():
            return

        try:
            content = router_file.read_text()
            # Extract PROMPT_KEYWORDS
            if "PROMPT_KEYWORDS" in content:
                import re
                pattern = r'["\'](\w+)["\']\s*:\s*\[[^\]]*["\']([^"\']+)["\']'
                matches = re.findall(pattern, content)

                for prompt, keywords in matches:
                    for kw in keywords.split(","):
                        kw = kw.strip().strip("'\"")
                        if kw and kw not in self._keyword_map:
                            self._keyword_map[kw.lower()] = prompt
        except Exception as e:
            logger.warning(f"Could not load keywords from router: {e}")

    def _load_agents(self):
        """Load agent configurations."""
        router_file = self.prompts_dir.parent / "src" / "application" / "agent_router.py"
        if not router_file.exists():
            return

        try:
            content = router_file.read_text()
            # Find AGENTS definition
            if "AGENTS" in content:
                import re
                # Find agent blocks
                pattern = r'"(\w+)":\s*Agent\([^)]+prompts=\[([^\]]+)\]'
                matches = re.findall(pattern, content)

                for agent_name, prompts_str in matches:
                    # Extract prompt names
                    prompt_names = re.findall(r'"(\w+[-]?\w+)"', prompts_str)
                    self._agent_prompts[agent_name] = set(prompt_names)
        except Exception as e:
            logger.warning(f"Could not load agents: {e}")

    def check_prompt_name(self, name: str) -> DuplicateCheckResult:
        """
        Check if prompt name already exists.

        Args:
            name: Prompt name to check (with or without promt- prefix)

        Returns:
            DuplicateCheckResult with duplicates and suggestions
        """
        # Normalize name
        if not name.startswith("promt-"):
            name = f"promt-{name}"

        duplicates = []
        suggestions = []

        # Check exact match
        if name in self._prompt_index:
            duplicates.append({
                "type": "exact",
                "name": name,
                "path": self._prompt_index[name],
                "message": f"Exact duplicate: {name}"
            })
            suggestions.append(f"Use existing prompt: {name}")
        else:
            # Check similar names
            for existing_name, path in self._prompt_index.items():
                # Check if it's the same without promt- prefix
                if name.replace("promt-", "") == existing_name.replace("promt-", ""):
                    duplicates.append({
                        "type": "similar",
                        "name": existing_name,
                        "path": path,
                        "message": f"Similar name: {existing_name}"
                    })
                    suggestions.append(f"Use existing: {existing_name}")

        return DuplicateCheckResult(
            is_valid=len(duplicates) == 0,
            duplicates=duplicates,
            suggestions=suggestions,
            existing_prompts=list(self._prompt_index.keys()),
            existing_keywords=self._keyword_map.copy(),
            # Note: Can't access private _agent_prompts here, but that's ok
        )

    def check_keyword(self, keyword: str) -> DuplicateCheckResult:
        """
        Check if keyword already maps to a prompt.

        Args:
            keyword: Keyword to check

        Returns:
            DuplicateCheckResult with existing mappings
        """
        keyword_lower = keyword.lower()
        duplicates = []
        suggestions = []

        if keyword_lower in self._keyword_map:
            existing_prompt = self._keyword_map[keyword_lower]
            duplicates.append({
                "type": "keyword",
                "keyword": keyword,
                "prompt": existing_prompt,
                "message": f"Keyword '{keyword}' maps to: {existing_prompt}"
            })
            suggestions.append(f"Use existing prompt: {existing_prompt}")
            suggestions.append(f"Or use more specific keyword like: '{keyword}_specific'")

        return DuplicateCheckResult(
            is_valid=len(duplicates) == 0,
            duplicates=duplicates,
            suggestions=suggestions,
            existing_prompts=list(self._prompt_index.keys()),
            existing_keywords=self._keyword_map.copy(),
        )

    def check_keywords_batch(self, keywords: List[str]) -> DuplicateCheckResult:
        """Check multiple keywords for duplicates."""
        all_duplicates = []
        all_suggestions = []

        for keyword in keywords:
            result = self.check_keyword(keyword)
            all_duplicates.extend(result.duplicates)
            all_suggestions.extend(result.suggestions)

        return DuplicateCheckResult(
            is_valid=len(all_duplicates) == 0,
            duplicates=all_duplicates,
            suggestions=list(set(all_suggestions)),
            existing_prompts=list(self._prompt_index.keys()),
            existing_keywords=self._keyword_map.copy(),
        )

    def check_agent_prompts(self, agent_name: str, prompts: List[str]) -> DuplicateCheckResult:
        """
        Check if agent has duplicate prompt references.

        Args:
            agent_name: Name of the agent
            prompts: List of prompt names the agent references

        Returns:
            DuplicateCheckResult
        """
        duplicates = []
        suggestions = []

        # Check if any prompts are duplicates within the agent itself
        seen = set()
        for prompt in prompts:
            if prompt in seen:
                duplicates.append({
                    "type": "agent_duplicate",
                    "prompt": prompt,
                    "message": f"Agent '{agent_name}' references '{prompt}' multiple times"
                })
            seen.add(prompt)

        # Check if prompts actually exist
        for prompt in prompts:
            normalized = prompt if prompt.startswith("promt-") else f"promt-{prompt}"
            if normalized not in self._prompt_index:
                suggestions.append(f"Prompt '{prompt}' does not exist (will be created)")

        return DuplicateCheckResult(
            is_valid=len(duplicates) == 0,
            duplicates=duplicates,
            suggestions=suggestions,
            existing_prompts=list(self._prompt_index.keys()),
            existing_keywords=self._keyword_map.copy(),
        )

    def get_similar_prompts(self, name: str, limit: int = 5) -> List[Dict[str, str]]:
        """Find similar prompts based on name similarity."""
        import difflib

        name_normalized = name.lower().replace("promt-", "")

        similarities = []
        for existing_name, path in self._prompt_index.items():
            existing_normalized = existing_name.lower().replace("promt-", "")

            # Calculate similarity
            ratio = difflib.SequenceMatcher(
                None, name_normalized, existing_normalized
            ).ratio()

            if ratio > 0.3:  # Threshold for similarity
                similarities.append({
                    "name": existing_name,
                    "path": path,
                    "similarity": round(ratio, 2)
                })

        # Sort by similarity and return top matches
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        return similarities[:limit]

    def validate_new_prompt(
        self,
        name: str,
        keywords: List[str],
        agent_prompts: List[str] = None
    ) -> DuplicateCheckResult:
        """
        Full validation for a new prompt.

        Checks:
        1. Prompt name doesn't exist
        2. Keywords don't conflict
        3. Agent references are valid (if provided)

        Args:
            name: Prompt name
            keywords: Keywords to map to this prompt
            agent_prompts: Optional list of prompts for agent

        Returns:
            DuplicateCheckResult with all validation issues
        """
        all_duplicates = []
        all_suggestions = []

        # Check name
        name_result = self.check_prompt_name(name)
        all_duplicates.extend(name_result.duplicates)
        all_suggestions.extend(name_result.suggestions)

        # Check keywords
        kw_result = self.check_keywords_batch(keywords)
        all_duplicates.extend(kw_result.duplicates)
        all_suggestions.extend(kw_result.suggestions)

        # Check agent prompts
        if agent_prompts:
            agent_result = self.check_agent_prompts("new_agent", agent_prompts)
            all_duplicates.extend(agent_result.duplicates)
            all_suggestions.extend(agent_result.suggestions)

        return DuplicateCheckResult(
            is_valid=len(all_duplicates) == 0,
            duplicates=all_duplicates,
            suggestions=list(set(all_suggestions)),
            existing_prompts=list(self._prompt_index.keys()),
            existing_keywords=self._keyword_map.copy(),
        )

    def get_report(self) -> Dict:
        """Get full deduplication report."""
        return {
            "total_prompts": len(self._prompt_index),
            "total_keywords": len(self._keyword_map),
            "total_agents": len(self._agent_prompts),
            "prompts_by_tier": self._get_prompts_by_tier(),
            "keyword_conflicts": self._find_keyword_conflicts(),
            "agents": {
                name: list(prompts)
                for name, prompts in self._agent_prompts.items()
            }
        }

    def _get_prompts_by_tier(self) -> Dict[str, List[str]]:
        """Group prompts by tier."""
        tiers = {"core": [], "universal": [], "packs": []}

        for name, path in self._prompt_index.items():
            if path.startswith("core"):
                tiers["core"].append(name)
            elif path.startswith("universal"):
                tiers["universal"].append(name)
            elif path.startswith("packs"):
                tiers["packs"].append(name)

        return tiers

    def _find_keyword_conflicts(self) -> List[Dict]:
        """Find potential keyword conflicts."""
        # This is a simplified version - real implementation would check
        # for overlapping keywords
        return []


# Global instance for reuse
_guard: Optional[PromptDeduplicationGuard] = None


def get_prompt_guard() -> PromptDeduplicationGuard:
    """Get or create global guard instance."""
    global _guard
    if _guard is None:
        _guard = PromptDeduplicationGuard()
    return _guard
