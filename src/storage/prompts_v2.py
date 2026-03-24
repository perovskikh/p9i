# src/storage/prompts_v2.py
"""
Prompt storage and management v2.0.0

Implements tiered prompt architecture with:
- Lazy loading with FastAPI Depends() pattern
- Baseline lock verification with SHA256 checksums
- Cascade priority logic (Projects → MPV Stages → Universal → Core)
- lru_cache for performance optimization
"""

from pathlib import Path
from typing import Optional, Dict, List, Any
from enum import Enum
from functools import lru_cache
import json
import logging
import hashlib
from pydantic import BaseModel, Field
from datetime import datetime

logger = logging.getLogger(__name__)


class PromptTier(str, Enum):
    """Prompt tier enumeration for cascade priority."""
    CORE = "core"                # Tier 0: Baseline prompts, immutable
    UNIVERSAL = "universal"        # Tier 1: Universal prompts, overridable
    MPV_STAGE = "mpv_stage"       # Tier 2: MPV pipeline stages, high priority
    PROJECTS = "projects"          # Tier 3: Project-specific prompts, highest priority


class Prompt(BaseModel):
    """Prompt model with Pydantic v2 validation."""
    name: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)
    version: str = Field(default="1.0.0", pattern=r"^\d+\.\d+\.\d+$")
    tier: PromptTier = Field(default=PromptTier.UNIVERSAL)
    immutable: bool = Field(default=False)
    overridable: bool = Field(default=True)
    checksum: Optional[str] = Field(default=None)
    tags: List[str] = Field(default_factory=list)
    variables: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[str] = Field(default=None)


class PromptNotFoundError(Exception):
    """Raised when a prompt is not found."""
    pass


class BaselineIntegrityError(Exception):
    """Raised when baseline prompt integrity is compromised."""
    pass


class BaselineLockManager:
    """Manages baseline lock verification with SHA256 checksums."""

    def __init__(self, prompts_dir: str = "./prompts"):
        self.prompts_dir = Path(prompts_dir)
        self._lock = None
        self.core_dir = self.prompts_dir / "core"
        self.lock_file = self.core_dir / ".promt-baseline-lock"

    def load_lock(self) -> Dict:
        """Load baseline lock file."""
        if not self.lock_file.exists():
            logger.warning(f"Baseline lock file not found: {self.lock_file}")
            return {}

        try:
            with open(self.lock_file, 'r') as f:
                self._lock = json.load(f)
            logger.info(f"Baseline lock loaded: {self._lock.get('version', 'unknown')}")
            return self._lock
        except Exception as e:
            logger.error(f"Error loading baseline lock: {e}")
            return {}

    def verify_core_prompt(self, prompt_name: str, content: str) -> bool:
        """Verify core prompt integrity against baseline lock."""
        lock = self.load_lock()
        if not lock:
            return True  # No lock file, skip verification

        checksums = lock.get("checksums", {})
        expected_checksum = checksums.get(f"{prompt_name}.md")

        if not expected_checksum:
            logger.warning(f"No checksum in baseline lock for: {prompt_name}")
            return False

        # Compute SHA256 of current content
        current_checksum = hashlib.sha256(content.encode()).hexdigest()

        # Strip "sha256:" prefix from expected checksum if present
        expected_clean = expected_checksum.replace("sha256:", "")

        # Compare checksums (handle both short and long formats)
        if current_checksum == expected_clean:
            return True

        # Handle legacy short checksum format
        if current_checksum.startswith(expected_clean):
            return True

        # Checksum mismatch
        logger.error(
            f"Baseline integrity check FAILED for {prompt_name}:\n"
            f"  Expected: {expected_checksum}\n"
            f"  Current:  {current_checksum}"
        )
        return False

    def get_verification_rules(self) -> Dict:
        """Get baseline verification rules."""
        lock = self.load_lock()
        return lock.get("verification_rules", {})


class PromptStorageV2:
    """
    Manages prompt storage and retrieval with tiered architecture.

    Features:
    - Lazy loading with Depends() pattern (via cached methods)
    - Baseline lock verification for core prompts
    - Cascade priority logic for prompt resolution
    - Tier-based prompt organization
    - lru_cache for performance optimization
    """

    def __init__(self, prompts_dir: str = "./prompts"):
        self.prompts_dir = Path(prompts_dir)
        self._registry = None
        self._baseline_lock = BaselineLockManager(prompts_dir)

        # Tier directories
        self.core_dir = self.prompts_dir / "core"
        self.universal_dir = self.prompts_dir / "universal" / "ai_agent_prompts"
        self.mpv_stages_dir = self.prompts_dir / "universal" / "mpv_stages"
        self.projects_dir = self.prompts_dir / "projects"

        # Create directories if they don't exist
        self.core_dir.mkdir(parents=True, exist_ok=True)
        self.universal_dir.mkdir(parents=True, exist_ok=True)
        self.mpv_stages_dir.mkdir(parents=True, exist_ok=True)
        self.projects_dir.mkdir(parents=True, exist_ok=True)

    @lru_cache(maxsize=128)
    def get_registry(self) -> Dict:
        """Load prompt registry with caching."""
        if self._registry is None:
            registry_file = self.prompts_dir / "registry.json"
            if registry_file.exists():
                with open(registry_file, 'r') as f:
                    self._registry = json.load(f)
                logger.info(f"Registry loaded: {len(self._registry.get('prompts', {}))} prompts")
            else:
                self._registry = {"registry_version": "2.0", "prompts": {}}
                logger.warning("Registry file not found, using empty registry")
        return self._registry

    def get_prompt_file_path(self, name: str, tier: PromptTier) -> Path:
        """Get file path for a prompt based on tier."""
        # Remove .md extension if present
        name = name.replace(".md", "")

        # Check different directories based on tier
        if tier == PromptTier.CORE:
            return self.core_dir / f"{name}.md"
        elif tier == PromptTier.MPV_STAGE:
            return self.mpv_stages_dir / f"{name}.md"
        elif tier == PromptTier.PROJECTS:
            # Projects directory can have subdirectories by project_id
            return self.projects_dir / f"{name}.md"
        else:  # UNIVERSAL (default)
            # Check universal/ai_agent_prompts first
            path = self.universal_dir / f"{name}.md"
            if path.exists():
                return path
            # Check deprecated subdirectory
            deprecated_path = self.universal_dir / "deprecated" / f"{name}.md"
            if deprecated_path.exists():
                return deprecated_path
            return path

    def resolve_prompt_tier(self, name: str) -> PromptTier:
        """
        Resolve prompt tier using cascade priority logic.

        Priority order: Projects → MPV Stages → Universal → Core

        Args:
            name: Prompt name (without .md extension)

        Returns:
            PromptTier: The tier where the prompt was found
        """
        name = name.replace(".md", "")

        # Priority 1: Projects (highest)
        project_path = self.projects_dir / f"{name}.md"
        if project_path.exists():
            logger.debug(f"Prompt '{name}' found in projects tier")
            return PromptTier.PROJECTS

        # Priority 2: MPV Stages
        mpv_path = self.mpv_stages_dir / f"{name}.md"
        if mpv_path.exists():
            logger.debug(f"Prompt '{name}' found in mpv_stage tier")
            return PromptTier.MPV_STAGE

        # Priority 3: Universal (default)
        universal_path = self.universal_dir / f"{name}.md"
        if universal_path.exists():
            logger.debug(f"Prompt '{name}' found in universal tier")
            return PromptTier.UNIVERSAL

        # Priority 4: Core (lowest, immutable)
        core_path = self.core_dir / f"{name}.md"
        if core_path.exists():
            logger.debug(f"Prompt '{name}' found in core tier")
            return PromptTier.CORE

        # Not found in any tier
        logger.warning(f"Prompt '{name}' not found in any tier")
        return PromptTier.UNIVERSAL

    @lru_cache(maxsize=256)
    def load_prompt_content(self, name: str, tier: Optional[PromptTier] = None) -> str:
        """
        Load prompt content from file with caching.

        Args:
            name: Prompt name
            tier: Optional tier (if not provided, will be resolved)

        Returns:
            str: Prompt content

        Raises:
            PromptNotFoundError: If prompt not found
        """
        if tier is None:
            tier = self.resolve_prompt_tier(name)

        prompt_file = self.get_prompt_file_path(name, tier)

        if not prompt_file.exists():
            raise PromptNotFoundError(f"Prompt not found: {name} (tier: {tier})")

        with open(prompt_file, 'r') as f:
            content = f.read()

        logger.debug(f"Loaded prompt '{name}' from {tier.value} tier ({len(content)} chars)")
        return content

    def load_prompt(self, name: str, verify_baseline: bool = True) -> Prompt:
        """
        Load a prompt by name with full metadata.

        Args:
            name: Prompt name
            verify_baseline: Whether to verify baseline lock for core prompts

        Returns:
            Prompt: Loaded prompt with metadata

        Raises:
            PromptNotFoundError: If prompt not found
            BaselineIntegrityError: If baseline verification fails
        """
        # Resolve tier
        tier = self.resolve_prompt_tier(name)

        # Load content
        content = self.load_prompt_content(name, tier)

        # Verify baseline for core prompts
        if tier == PromptTier.CORE and verify_baseline:
            if not self._baseline_lock.verify_core_prompt(name, content):
                raise BaselineIntegrityError(
                    f"Baseline integrity check failed for core prompt: {name}"
                )

        # Try to load metadata from registry
        registry = self.get_registry()
        prompt_meta = registry.get("prompts", {}).get(f"{name}.md", {})

        return Prompt(
            name=name,
            content=content,
            version=prompt_meta.get("version", "1.0.0"),
            tier=tier,
            immutable=prompt_meta.get("immutable", False),
            overridable=prompt_meta.get("overridable", True),
            checksum=prompt_meta.get("checksum"),
            tags=prompt_meta.get("tags", []),
            variables=prompt_meta.get("variables", {}),
            created_at=prompt_meta.get("created_at")
        )

    def list_prompts(self, tier: Optional[PromptTier] = None) -> List[Dict]:
        """
        List available prompts with optional tier filter.

        Args:
            tier: Optional tier filter

        Returns:
            List of prompt dictionaries
        """
        registry = self.get_registry()
        all_prompts = []

        for prompt_name, meta in registry.get("prompts", {}).items():
            prompt_tier_str = meta.get("tier", "universal")
            try:
                prompt_tier = PromptTier(prompt_tier_str)
            except ValueError:
                prompt_tier = PromptTier.UNIVERSAL

            # Filter by tier if specified
            if tier is not None and prompt_tier != tier:
                continue

            all_prompts.append({
                "name": prompt_name.replace(".md", ""),
                "file": meta.get("file", prompt_name),
                "tier": prompt_tier.value,
                "version": meta.get("version", "1.0.0"),
                "immutable": meta.get("immutable", False),
                "overridable": meta.get("overridable", True),
                "tags": meta.get("tags", []),
                "created_at": meta.get("created_at")
            })

        logger.info(f"Listed {len(all_prompts)} prompts" + (f" in {tier.value} tier" if tier else ""))
        return all_prompts

    def list_tier_prompts(self, tier: PromptTier) -> List[Dict]:
        """
        List prompts in a specific tier.

        This is a specialized method for loading prompts from a specific tier
        with cascade override priority consideration.

        Args:
            tier: Prompt tier to list

        Returns:
            List of prompt dictionaries in that tier
        """
        return self.list_prompts(tier=tier)

    def search_prompts(self, query: str, tier: Optional[PromptTier] = None) -> List[Dict]:
        """
        Search prompts by query string with optional tier filter.

        Args:
            query: Search query
            tier: Optional tier filter

        Returns:
            List of matching prompts
        """
        prompts = self.list_prompts(tier=tier)
        query_lower = query.lower()

        return [
            p for p in prompts
            if query_lower in p.get("name", "").lower()
            or query_lower in " ".join(p.get("tags", [])).lower()
            or query_lower in p.get("tier", "").lower()
        ]

    def get_prompt_by_name(self, name: str) -> Prompt:
        """
        FastAPI Depends() compatible function for getting a prompt.

        This function is designed to work with FastAPI's Depends()
        pattern for dependency injection while maintaining caching.

        Args:
            name: Prompt name

        Returns:
            Prompt: Loaded prompt

        Raises:
            PromptNotFoundError: If prompt not found
        """
        return self.load_prompt(name)

    def get_tier_prompts(self, tier: PromptTier) -> List[Prompt]:
        """
        FastAPI Depends() compatible function for getting all prompts in a tier.

        Args:
            tier: Prompt tier

        Returns:
            List of Prompts in that tier
        """
        prompt_dicts = self.list_tier_prompts(tier)
        prompts = []

        for p_dict in prompt_dicts:
            try:
                prompts.append(self.load_prompt(p_dict["name"]))
            except PromptNotFoundError:
                logger.warning(f"Prompt '{p_dict['name']}' listed but not found")
                continue

        return prompts

    def get_all_prompts(self) -> List[Prompt]:
        """
        Get all prompts across all tiers with cascade priority.

        This method respects the cascade priority:
        Projects → MPV Stages → Universal → Core

        Returns:
            List of all available prompts
        """
        all_prompts = []

        # Load prompts in priority order
        for tier in [PromptTier.PROJECTS, PromptTier.MPV_STAGE,
                    PromptTier.UNIVERSAL, PromptTier.CORE]:
            tier_prompts = self.get_tier_prompts(tier)
            all_prompts.extend(tier_prompts)

        logger.info(f"Loaded {len(all_prompts)} total prompts across all tiers")
        return all_prompts

    def verify_baseline_integrity(self) -> Dict:
        """
        Verify integrity of all core prompts against baseline lock.

        Returns:
            dict: Verification results
        """
        results = {
            "verified": True,
            "verified_prompts": [],
            "failed_prompts": [],
            "missing_prompts": [],
            "timestamp": datetime.now().isoformat()
        }

        # Get list of core prompts from baseline lock
        lock = self._baseline_lock.load_lock()
        checksums = lock.get("checksums", {})

        for prompt_name, expected_checksum in checksums.items():
            try:
                content = self.load_prompt_content(prompt_name, PromptTier.CORE)
                current_checksum = hashlib.sha256(content.encode()).hexdigest()

                if current_checksum == expected_checksum or \
                   current_checksum.startswith(expected_checksum):
                    results["verified_prompts"].append(prompt_name)
                else:
                    results["failed_prompts"].append({
                        "name": prompt_name,
                        "expected": expected_checksum,
                        "current": current_checksum
                    })
                    results["verified"] = False

            except PromptNotFoundError:
                results["missing_prompts"].append(prompt_name)
                results["verified"] = False

        logger.info(
            f"Baseline verification: {len(results['verified_prompts'])} verified, "
            f"{len(results['failed_prompts'])} failed, "
            f"{len(results['missing_prompts'])} missing"
        )

        return results

    def clear_cache(self):
        """Clear all lru_cache entries."""
        self.load_prompt_content.cache_clear()
        self.get_registry.cache_clear()
        logger.info("Prompt storage cache cleared")

# Legacy compatibility: maintain old storage interface
class PromptStorage:
    """Legacy prompt storage for backward compatibility."""

    def __init__(self, prompts_dir: str = "./prompts"):
        self.prompts_dir = Path(prompts_dir)
        # Use new v2 storage internally
        self._v2_storage = PromptStorageV2(prompts_dir)

    def load_prompt(self, name: str) -> dict:
        """Load a prompt by name (legacy format)."""
        prompt = self._v2_storage.load_prompt(name)
        return {
            "name": prompt.name,
            "content": prompt.content,
            "version": prompt.version,
            "tier": prompt.tier.value,
            "tags": prompt.tags,
            "immutable": prompt.immutable,
            "overridable": prompt.overridable
        }

    def get_registry(self) -> dict:
        """Load prompt registry (legacy format)."""
        return self._v2_storage.get_registry()

    def list_prompts(self) -> list[dict]:
        """List all available prompts (legacy format)."""
        return self._v2_storage.list_prompts()

    def search_prompts(self, query: str) -> list[dict]:
        """Search prompts by query string (legacy format)."""
        return self._v2_storage.search_prompts(query)


# Legacy storage instance for backward compatibility
storage = PromptStorage()


# Global storage instance with lazy initialization
_storage_instance: Optional[PromptStorageV2] = None


def get_storage() -> PromptStorageV2:
    """Get or create global PromptStorageV2 instance."""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = PromptStorageV2()
    return _storage_instance


def get_prompt(name: str) -> Prompt:
    """FastAPI Depends() compatible function for getting a prompt."""
    return get_storage().load_prompt(name)


def get_tier_prompts(tier: PromptTier) -> List[Prompt]:
    """FastAPI Depends() compatible function for getting prompts by tier."""
    return get_storage().get_tier_prompts(tier)


def verify_baseline():
    """
    Verify baseline integrity of all core prompts.

    Usage in FastAPI:
        @app.get("/baseline/verify")
        async def verify_baseline_result(
            result: Dict = Depends(verify_baseline)
        ):
            return result

    Returns:
        dict: Verification results
    """
    storage = get_storage()
    return storage.verify_baseline_integrity()
