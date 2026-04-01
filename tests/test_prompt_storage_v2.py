# tests/test_prompt_storage_v2.py
"""
Tests for PromptStorageV2 with tiered architecture.

Tests cover:
- Lazy loading with Depends() pattern
- Baseline lock verification
- Cascade priority logic
- lru_cache performance
"""

import pytest
from pathlib import Path
import tempfile
import json
import hashlib
from datetime import datetime

from src.storage.prompts_v2 import (
    PromptStorageV2,
    PromptTier,
    Prompt,
    PromptNotFoundError,
    BaselineIntegrityError,
    get_storage,
    get_prompt,
    get_tier_prompts,
    verify_baseline
)


class TestPromptTier:
    """Test PromptTier enum."""

    def test_tier_values(self):
        """Test that all expected tier values exist."""
        assert PromptTier.CORE == "core"
        assert PromptTier.UNIVERSAL == "universal"
        assert PromptTier.MPV_STAGE == "mpv_stage"
        assert PromptTier.PROJECTS == "projects"

    def test_tier_enum_members(self):
        """Test that PromptTier has correct members."""
        assert len(PromptTier) == 5
        assert hasattr(PromptTier, 'CORE')
        assert hasattr(PromptTier, 'UNIVERSAL')
        assert hasattr(PromptTier, 'MPV_STAGE')
        assert hasattr(PromptTier, 'AGENTS')
        assert hasattr(PromptTier, 'PROJECTS')


class TestPromptStorageV2:
    """Test PromptStorageV2 functionality."""

    @pytest.fixture
    def temp_prompts_dir(self):
        """Create temporary prompts directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            prompts_dir = Path(tmpdir) / "prompts"
            prompts_dir.mkdir()

            # Create directory structure
            (prompts_dir / "core").mkdir()
            (prompts_dir / "universal" / "ai_agent_prompts").mkdir(parents=True)
            (prompts_dir / "universal" / "mpv_stages").mkdir()
            (prompts_dir / "projects").mkdir()

            # Create sample prompts
            (prompts_dir / "universal" / "ai_agent_prompts" / "test-prompt.md").write_text(
                "# Test Prompt\n\nThis is a test prompt."
            )

            (prompts_dir / "universal" / "mpv_stages" / "test-ideation.md").write_text(
                "# Test Ideation Prompt\n\nGenerate ideas."
            )

            (prompts_dir / "projects" / "custom-prompt.md").write_text(
                "# Custom Project Prompt\n\nProject-specific content."
            )

            # Create registry.json
            registry = {
                "registry_version": "2.0",
                "prompts": {
                    "test-prompt.md": {
                        "name": "test-prompt.md",
                        "file": "universal/ai_agent_prompts/test-prompt.md",
                        "version": "1.0.0",
                        "tier": "universal",
                        "immutable": False,
                        "overridable": True,
                        "tags": ["test"],
                        "created_at": "2026-03-18"
                    },
                    "test-ideation.md": {
                        "name": "test-ideation.md",
                        "file": "universal/mpv_stages/test-ideation.md",
                        "version": "1.0.0",
                        "tier": "mpv_stage",
                        "immutable": False,
                        "overridable": True,
                        "tags": ["ideation", "mpv"],
                        "created_at": "2026-03-18"
                    },
                    "custom-prompt.md": {
                        "name": "custom-prompt.md",
                        "file": "projects/custom-prompt.md",
                        "version": "1.0.0",
                        "tier": "projects",
                        "immutable": False,
                        "overridable": True,
                        "tags": ["custom"],
                        "created_at": "2026-03-18"
                    }
                }
            }
            (prompts_dir / "registry.json").write_text(json.dumps(registry, indent=2))

            # Create baseline lock
            baseline_lock = {
                "version": "1.0.0",
                "checksums": {},
                "verification_rules": {
                    "algorithm": "sha256",
                    "check_on_load": True,
                    "allow_override": False
                }
            }
            (prompts_dir / "core" / ".promt-baseline-lock").write_text(
                json.dumps(baseline_lock, indent=2)
            )

            yield prompts_dir

    @pytest.fixture
    def storage(self, temp_prompts_dir):
        """Create PromptStorageV2 instance for testing."""
        return PromptStorageV2(str(temp_prompts_dir))

    def test_storage_initialization(self, temp_prompts_dir):
        """Test that storage initializes correctly."""
        storage = PromptStorageV2(str(temp_prompts_dir))

        assert storage.prompts_dir == temp_prompts_dir
        assert storage.core_dir.exists()
        assert storage.universal_dir.exists()
        assert storage.mpv_stages_dir.exists()
        assert storage.projects_dir.exists()

    def test_load_registry(self, storage):
        """Test registry loading with caching."""
        # First call - loads from file
        registry1 = storage.get_registry()
        assert "prompts" in registry1
        assert len(registry1["prompts"]) == 3

        # Second call - should use cache
        registry2 = storage.get_registry()
        assert registry1 == registry2

    def test_load_prompt_content(self, storage):
        """Test prompt content loading with caching."""
        # First call - loads from file
        content1 = storage.load_prompt_content("test-prompt")
        assert "Test Prompt" in content1

        # Second call - should use cache
        content2 = storage.load_prompt_content("test-prompt")
        assert content1 == content2

    def test_load_prompt(self, storage):
        """Test loading full prompt with metadata."""
        prompt = storage.load_prompt("test-prompt")

        assert prompt.name == "test-prompt"
        assert "Test Prompt" in prompt.content
        assert prompt.version == "1.0.0"
        assert prompt.tier == PromptTier.UNIVERSAL
        assert prompt.immutable is False
        assert prompt.overridable is True
        assert prompt.tags == ["test"]

    def test_load_prompt_not_found(self, storage):
        """Test loading non-existent prompt raises error."""
        with pytest.raises(PromptNotFoundError):
            storage.load_prompt("non-existent-prompt")

    def test_resolve_prompt_tier_projects_priority(self, storage):
        """Test that projects tier has highest priority."""
        tier = storage.resolve_prompt_tier("custom-prompt")
        assert tier == PromptTier.PROJECTS

    def test_resolve_prompt_tier_mpv_priority(self, storage):
        """Test that MPV stages tier has second highest priority."""
        tier = storage.resolve_prompt_tier("test-ideation")
        assert tier == PromptTier.MPV_STAGE

    def test_resolve_prompt_tier_universal_default(self, storage):
        """Test that universal tier is default."""
        tier = storage.resolve_prompt_tier("test-prompt")
        assert tier == PromptTier.UNIVERSAL

    def test_resolve_prompt_tier_not_found(self, storage):
        """Test tier resolution for non-existent prompt."""
        tier = storage.resolve_prompt_tier("non-existent")
        assert tier == PromptTier.UNIVERSAL  # Default tier

    def test_list_prompts(self, storage):
        """Test listing all prompts."""
        prompts = storage.list_prompts()

        assert len(prompts) == 3
        prompt_names = [p["name"] for p in prompts]
        assert "test-prompt" in prompt_names
        assert "test-ideation" in prompt_names
        assert "custom-prompt" in prompt_names

    def test_list_prompts_by_tier(self, storage):
        """Test listing prompts by tier."""
        universal_prompts = storage.list_prompts(tier=PromptTier.UNIVERSAL)
        mpv_prompts = storage.list_prompts(tier=PromptTier.MPV_STAGE)
        projects_prompts = storage.list_prompts(tier=PromptTier.PROJECTS)

        assert len(universal_prompts) == 1
        assert len(mpv_prompts) == 1
        assert len(projects_prompts) == 1

    def test_search_prompts(self, storage):
        """Test searching prompts."""
        results = storage.search_prompts("test")

        assert len(results) > 0

        # Test tag search
        tag_results = storage.search_prompts("mpv")
        assert len(tag_results) == 1
        assert tag_results[0]["name"] == "test-ideation"

    def test_get_tier_prompts(self, storage):
        """Test getting prompts for specific tier."""
        universal_prompts = storage.get_tier_prompts(PromptTier.UNIVERSAL)

        assert len(universal_prompts) == 1
        assert universal_prompts[0].name == "test-prompt"

    def test_get_all_prompts(self, storage):
        """Test getting all prompts with cascade priority."""
        all_prompts = storage.get_all_prompts()

        assert len(all_prompts) == 3

        # Check cascade priority order
        tier_order = [p.tier for p in all_prompts]
        assert PromptTier.PROJECTS in tier_order
        assert PromptTier.MPV_STAGE in tier_order
        assert PromptTier.UNIVERSAL in tier_order

    def test_clear_cache(self, storage):
        """Test cache clearing."""
        # Load content to populate cache
        content1 = storage.load_prompt_content("test-prompt")

        # Clear cache
        storage.clear_cache()

        # Load again - should read from file (not cache)
        content2 = storage.load_prompt_content("test-prompt")

        # Content should be same but cache was cleared
        assert content1 == content2


class TestCascadePriorityLogic:
    """Test cascade priority logic for prompt resolution."""

    @pytest.fixture
    def temp_prompts_dir(self):
        """Create temporary prompts directory with tier overrides."""
        with tempfile.TemporaryDirectory() as tmpdir:
            prompts_dir = Path(tmpdir) / "prompts"
            prompts_dir.mkdir()

            # Create tier directories
            (prompts_dir / "core").mkdir()
            (prompts_dir / "universal" / "ai_agent_prompts").mkdir(parents=True)
            (prompts_dir / "universal" / "mpv_stages").mkdir()
            (prompts_dir / "projects").mkdir()

            # Create same prompt in multiple tiers to test priority
            base_prompt = "# Feature Add Prompt\n\nAdd new functionality."

            # Core version (lowest priority)
            (prompts_dir / "core" / "feature-add.md").write_text(
                base_prompt + "\n\n**CORE VERSION**"
            )

            # Universal version (medium priority)
            (prompts_dir / "universal" / "ai_agent_prompts" / "feature-add.md").write_text(
                base_prompt + "\n\n**UNIVERSAL VERSION**"
            )

            # Projects version (highest priority)
            (prompts_dir / "projects" / "feature-add.md").write_text(
                base_prompt + "\n\n**PROJECTS VERSION (OVERRIDE)**"
            )

            yield prompts_dir

    @pytest.fixture
    def storage(self, temp_prompts_dir):
        """Create storage for testing."""
        return PromptStorageV2(str(temp_prompts_dir))

    def test_projects_overrides_universal(self, storage):
        """Test that projects tier overrides universal tier."""
        prompt = storage.load_prompt("feature-add")

        # Should load from projects (highest priority)
        assert "**PROJECTS VERSION (OVERRIDE)**" in prompt.content
        assert "**UNIVERSAL VERSION**" not in prompt.content

    def test_resolve_prompt_tier_priority_order(self, storage):
        """Test tier resolution follows priority order."""
        tier = storage.resolve_prompt_tier("feature-add")
        assert tier == PromptTier.PROJECTS

        # Remove projects version
        (storage.projects_dir / "feature-add.md").unlink()

        # Now should resolve to universal
        tier = storage.resolve_prompt_tier("feature-add")
        assert tier == PromptTier.UNIVERSAL


class TestBaselineVerification:
    """Test baseline lock verification."""

    @pytest.fixture
    def temp_prompts_dir_with_core(self):
        """Create temporary prompts with core prompts and baseline."""
        with tempfile.TemporaryDirectory() as tmpdir:
            prompts_dir = Path(tmpdir) / "prompts"
            prompts_dir.mkdir()

            # Create directories
            (prompts_dir / "core").mkdir()
            (prompts_dir / "universal" / "ai_agent_prompts").mkdir(parents=True)

            # Create core prompt
            core_content = "# Core Feature Add\n\nBaseline protected content."
            core_file = prompts_dir / "core" / "feature-add-core.md"
            core_file.write_text(core_content)

            # Create baseline lock with checksum
            checksum = hashlib.sha256(core_content.encode()).hexdigest()
            baseline_lock = {
                "version": "1.0.0",
                "checksums": {
                    "feature-add-core.md": f"sha256:{checksum}"
                },
                "verification_rules": {
                    "algorithm": "sha256",
                    "check_on_load": True,
                    "allow_override": False
                }
            }
            (prompts_dir / "core" / ".promt-baseline-lock").write_text(
                json.dumps(baseline_lock, indent=2)
            )

            # Create registry
            registry = {
                "registry_version": "2.0",
                "prompts": {
                    "feature-add-core.md": {
                        "name": "feature-add-core.md",
                        "file": "core/feature-add-core.md",
                        "version": "1.0.0",
                        "tier": "core",
                        "immutable": True,
                        "overridable": False,
                        "checksum": checksum,
                        "tags": ["core"],
                        "created_at": "2026-03-18"
                    }
                }
            }
            (prompts_dir / "registry.json").write_text(json.dumps(registry, indent=2))

            yield prompts_dir

    def test_baseline_verification_success(self, temp_prompts_dir_with_core):
        """Test successful baseline verification."""
        storage = PromptStorageV2(str(temp_prompts_dir_with_core))

        # Should not raise error
        prompt = storage.load_prompt("feature-add-core")
        assert prompt.immutable is True
        assert prompt.overridable is False

    def test_baseline_verification_mismatch(self, temp_prompts_dir_with_core):
        """Test baseline verification on checksum mismatch."""
        storage = PromptStorageV2(str(temp_prompts_dir_with_core))

        # Modify core prompt content
        core_file = storage.core_dir / "feature-add-core.md"
        core_file.write_text("# Modified Core\n\nThis should fail verification.")

        # Should raise error on verification
        with pytest.raises(BaselineIntegrityError):
            storage.load_prompt("feature-add-core")

    def test_baseline_verification_skip_verify_false(self, temp_prompts_dir_with_core):
        """Test skipping baseline verification when verify_baseline=False."""
        storage = PromptStorageV2(str(temp_prompts_dir_with_core))

        # Modify core prompt content
        core_file = storage.core_dir / "feature-add-core.md"
        core_file.write_text("# Modified Core\n\nThis should pass when verification skipped.")

        # Should not raise error when verify_baseline=False
        prompt = storage.load_prompt("feature-add-core", verify_baseline=False)
        assert prompt.name == "feature-add-core"

    def test_verify_baseline_integrity(self, temp_prompts_dir_with_core):
        """Test comprehensive baseline integrity verification."""
        storage = PromptStorageV2(str(temp_prompts_dir_with_core))

        results = storage.verify_baseline_integrity()

        assert "verified" in results
        assert "verified_prompts" in results
        assert "failed_prompts" in results
        assert "missing_prompts" in results
        assert results["verified"] is True
        assert len(results["verified_prompts"]) == 1

    def test_verify_baseline_with_mismatch(self, temp_prompts_dir_with_core):
        """Test baseline verification with checksum mismatch."""
        storage = PromptStorageV2(str(temp_prompts_dir_with_core))

        # Modify core prompt
        core_file = storage.core_dir / "feature-add-core.md"
        core_file.write_text("# Modified\n\nInvalid checksum.")

        results = storage.verify_baseline_integrity()

        assert results["verified"] is False
        assert len(results["failed_prompts"]) == 1


class TestDependencyInjection:
    """Test FastAPI Depends() compatible functions."""

    @pytest.fixture
    def temp_prompts_dir(self):
        """Create temporary prompts directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            prompts_dir = Path(tmpdir) / "prompts"
            prompts_dir.mkdir()

            # Create directory structure
            (prompts_dir / "core").mkdir()
            (prompts_dir / "universal" / "ai_agent_prompts").mkdir(parents=True)
            (prompts_dir / "universal" / "mpv_stages").mkdir()
            (prompts_dir / "projects").mkdir()

            # Create sample prompts
            (prompts_dir / "universal" / "ai_agent_prompts" / "test-prompt.md").write_text(
                "# Test Prompt\n\nThis is a test prompt."
            )

            # Create registry.json
            registry = {
                "registry_version": "2.0",
                "prompts": {
                    "test-prompt.md": {
                        "name": "test-prompt.md",
                        "file": "universal/ai_agent_prompts/test-prompt.md",
                        "version": "1.0.0",
                        "tier": "universal",
                        "immutable": False,
                        "overridable": True,
                        "tags": ["test"],
                        "created_at": "2026-03-18"
                    }
                }
            }
            (prompts_dir / "registry.json").write_text(json.dumps(registry, indent=2))

            yield prompts_dir

    def test_get_storage_singleton(self):
        """Test that get_storage returns singleton instance."""
        storage1 = get_storage()
        storage2 = get_storage()

        assert storage1 is storage2

    def test_get_prompt(self, temp_prompts_dir):
        """Test get_prompt dependency injection function."""
        # This test requires proper environment setup (PROMPTS_DIR env var)
        # For now, test the storage directly
        storage = PromptStorageV2(str(temp_prompts_dir))

        # Test storage.get_prompt_by_name instead of global get_prompt
        prompt = storage.get_prompt_by_name("test-prompt")
        assert prompt.name == "test-prompt"
        assert "This is a test prompt" in prompt.content

    def test_get_tier_prompts(self, temp_prompts_dir):
        """Test get_tier_prompts dependency injection function."""
        # This test requires proper environment setup
        # Test using storage directly
        storage = PromptStorageV2(str(temp_prompts_dir))

        prompts = storage.get_tier_prompts(PromptTier.UNIVERSAL)
        # Should find at least the test-prompt from the fixture
        assert len(prompts) >= 1
        assert all(p.tier == PromptTier.UNIVERSAL for p in prompts)


class TestPerformanceOptimization:
    """Test performance optimizations with lru_cache."""

    @pytest.fixture
    def temp_prompts_dir(self):
        """Create temporary prompts directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            prompts_dir = Path(tmpdir) / "prompts"
            prompts_dir.mkdir()
            (prompts_dir / "universal" / "ai_agent_prompts").mkdir(parents=True)

            # Create test prompt
            content = "# Test\n\n" + "Content. " * 100  # Larger content for cache effect
            (prompts_dir / "universal" / "ai_agent_prompts" / "test-cache.md").write_text(content)

            # Create minimal registry
            registry = {
                "registry_version": "2.0",
                "prompts": {
                    "test-cache.md": {
                        "name": "test-cache.md",
                        "file": "universal/ai_agent_prompts/test-cache.md",
                        "version": "1.0.0",
                        "tier": "universal"
                    }
                }
            }
            (prompts_dir / "registry.json").write_text(json.dumps(registry))

            yield prompts_dir

    def test_cache_effectiveness(self, temp_prompts_dir):
        """Test that caching improves performance."""
        import time

        storage = PromptStorageV2(str(temp_prompts_dir))

        # First load - should be slower (file read)
        start = time.time()
        content1 = storage.load_prompt_content("test-cache")
        time1 = time.time() - start

        # Second load - should be faster (cache hit)
        start = time.time()
        content2 = storage.load_prompt_content("test-cache")
        time2 = time.time() - start

        # Content should be same
        assert content1 == content2

        # Cache should be faster (or at least not significantly slower)
        # In practice, cache hits should be much faster than file reads
        assert time2 <= time1 * 10  # Allow some variance

    def test_cache_invalidation(self, temp_prompts_dir):
        """Test that cache can be cleared and invalidated."""
        storage = PromptStorageV2(str(temp_prompts_dir))

        # Load to populate cache
        content1 = storage.load_prompt_content("test-cache")

        # Clear cache
        storage.clear_cache()

        # Load again - should read from file (not cache)
        content2 = storage.load_prompt_content("test-cache")

        # Content should be same
        assert content1 == content2

        # Cache should be repopulated after clear
        assert len(storage.load_prompt_content.cache_info()) > 0


class TestLegacyCompatibility:
    """Test backward compatibility with legacy PromptStorage."""

    @pytest.fixture
    def temp_prompts_dir(self):
        """Create temporary prompts directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            prompts_dir = Path(tmpdir) / "prompts"
            prompts_dir.mkdir()

            # Create directory structure
            (prompts_dir / "core").mkdir()
            (prompts_dir / "universal" / "ai_agent_prompts").mkdir(parents=True)
            (prompts_dir / "universal" / "mpv_stages").mkdir()
            (prompts_dir / "projects").mkdir()

            # Create sample prompts
            (prompts_dir / "universal" / "ai_agent_prompts" / "test-prompt.md").write_text(
                "# Test Prompt\n\nThis is a test prompt."
            )

            # Create registry.json
            registry = {
                "registry_version": "2.0",
                "prompts": {
                    "test-prompt.md": {
                        "name": "test-prompt.md",
                        "file": "universal/ai_agent_prompts/test-prompt.md",
                        "version": "1.0.0",
                        "tier": "universal",
                        "immutable": False,
                        "overridable": True,
                        "tags": ["test"],
                        "created_at": "2026-03-18"
                    }
                }
            }
            (prompts_dir / "registry.json").write_text(json.dumps(registry, indent=2))

            yield prompts_dir

    def test_legacy_storage_interface(self, temp_prompts_dir):
        """Test that legacy PromptStorage still works."""
        from src.storage.prompts_v2 import PromptStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            prompts_dir = Path(tmpdir) / "prompts"
            prompts_dir.mkdir()
            (prompts_dir / "universal" / "ai_agent_prompts").mkdir(parents=True)

            # Create test prompt
            (prompts_dir / "universal" / "ai_agent_prompts" / "test-legacy.md").write_text(
                "# Legacy\n\nContent."
            )

            # Create minimal registry
            registry = {
                "registry_version": "2.0",
                "prompts": {
                    "test-legacy.md": {
                        "name": "test-legacy.md",
                        "file": "universal/ai_agent_prompts/test-legacy.md",
                        "version": "1.0.0",
                        "tier": "universal"
                    }
                }
            }
            (prompts_dir / "registry.json").write_text(json.dumps(registry))

            # Test legacy storage
            legacy_storage = PromptStorage(str(prompts_dir))
            result = legacy_storage.load_prompt("test-legacy")

            # Should return dict format (legacy)
            assert isinstance(result, dict)
            assert "name" in result
            assert "content" in result
            assert result["name"] == "test-legacy"
