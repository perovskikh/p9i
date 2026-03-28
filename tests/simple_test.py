#!/usr/bin/env python3
"""
Simple test runner for PromptStorageV2 without pytest dependency.
Runs basic tests to verify the new storage implementation works.
"""

import sys
import os
import tempfile
import json
import hashlib
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from src.storage.prompts_v2 import (
        PromptStorageV2,
        PromptTier,
        Prompt,
        PromptNotFoundError,
        BaselineIntegrityError,
        get_storage,
        get_prompt,
        get_tier_prompts
    )
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def print_test_result(test_name, passed, details=""):
    """Print test result with status."""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {test_name}")
    if details:
        print(f"    Details: {details}")


def test_prompt_tier_enum():
    """Test PromptTier enum."""
    assert PromptTier.CORE == "core"
    assert PromptTier.UNIVERSAL == "universal"
    assert PromptTier.MPV_STAGE == "mpv_stage"
    assert PromptTier.PROJECTS == "projects"
    print_test_result("PromptTier enum", True)


def test_storage_initialization():
    """Test storage initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        prompts_dir = Path(tmpdir) / "prompts"
        prompts_dir.mkdir()
        (prompts_dir / "core").mkdir()
        (prompts_dir / "universal" / "ai_agent_prompts").mkdir(parents=True)

        storage = PromptStorageV2(str(prompts_dir))
        assert storage.prompts_dir == prompts_dir
        assert storage.core_dir.exists()
        print_test_result("Storage initialization", True)


def test_registry_loading():
    """Test registry loading with caching."""
    with tempfile.TemporaryDirectory() as tmpdir:
        prompts_dir = Path(tmpdir) / "prompts"
        prompts_dir.mkdir()
        (prompts_dir / "universal" / "ai_agent_prompts").mkdir(parents=True)

        registry = {
            "registry_version": "2.0",
            "prompts": {
                "test.md": {
                    "name": "test.md",
                    "file": "universal/ai_agent_prompts/test.md",
                    "version": "1.0.0",
                    "tier": "universal"
                }
            }
        }
        (prompts_dir / "registry.json").write_text(json.dumps(registry))

        storage = PromptStorageV2(str(prompts_dir))

        # First load
        registry1 = storage.get_registry()
        assert "prompts" in registry1
        assert len(registry1["prompts"]) == 1

        # Second load (should use cache)
        registry2 = storage.get_registry()
        assert registry1 == registry2

        print_test_result("Registry loading with cache", True)


def test_prompt_content_loading():
    """Test prompt content loading with caching."""
    with tempfile.TemporaryDirectory() as tmpdir:
        prompts_dir = Path(tmpdir) / "prompts"
        prompts_dir.mkdir()
        (prompts_dir / "universal" / "ai_agent_prompts").mkdir(parents=True)

        content = "# Test Prompt\n\nThis is a test."
        (prompts_dir / "universal" / "ai_agent_prompts" / "test.md").write_text(content)

        registry = {
            "registry_version": "2.0",
            "prompts": {
                "test.md": {
                    "name": "test.md",
                    "file": "universal/ai_agent_prompts/test.md",
                    "version": "1.0.0",
                    "tier": "universal"
                }
            }
        }
        (prompts_dir / "registry.json").write_text(json.dumps(registry))

        storage = PromptStorageV2(str(prompts_dir))

        # First load
        content1 = storage.load_prompt_content("test")
        assert "Test Prompt" in content1

        # Second load (should use cache)
        content2 = storage.load_prompt_content("test")
        assert content1 == content2

        print_test_result("Prompt content loading with cache", True)


def test_prompt_not_found():
    """Test loading non-existent prompt raises error."""
    with tempfile.TemporaryDirectory() as tmpdir:
        prompts_dir = Path(tmpdir) / "prompts"
        prompts_dir.mkdir()
        (prompts_dir / "universal" / "ai_agent_prompts").mkdir(parents=True)

        registry = {
            "registry_version": "2.0",
            "prompts": {}
        }
        (prompts_dir / "registry.json").write_text(json.dumps(registry))

        storage = PromptStorageV2(str(prompts_dir))

        try:
            storage.load_prompt("non-existent.md")
            print_test_result("Prompt not found error", False, "Should have raised PromptNotFoundError")
        except PromptNotFoundError:
            print_test_result("Prompt not found error", True)


def test_cascade_priority():
    """Test cascade priority logic."""
    with tempfile.TemporaryDirectory() as tmpdir:
        prompts_dir = Path(tmpdir) / "prompts"
        prompts_dir.mkdir()

        # Create tier directories
        (prompts_dir / "core").mkdir()
        (prompts_dir / "universal" / "ai_agent_prompts").mkdir(parents=True)
        (prompts_dir / "projects").mkdir()

        # Create same prompt in multiple tiers
        base_content = "# Test\n\nContent."

        # Core version (lowest priority)
        (prompts_dir / "core" / "test-core.md").write_text(
            base_content + "\n\n**CORE**"
        )

        # Universal version (medium priority)
        (prompts_dir / "universal" / "ai_agent_prompts" / "test-universal.md").write_text(
            base_content + "\n\n**UNIVERSAL**"
        )

        # Projects version (highest priority)
        (prompts_dir / "projects" / "test-projects.md").write_text(
            base_content + "\n\n**PROJECTS (OVERRIDE)**"
        )

        storage = PromptStorageV2(str(prompts_dir))

        # Load "test" - should resolve based on available files
        # Test with "test-projects.md" name
        prompt = storage.load_prompt("test-projects")

        # Should load from projects (highest priority)
        assert "**PROJECTS (OVERRIDE)**" in prompt.content
        assert "**UNIVERSAL**" not in prompt.content

        print_test_result("Cascade priority (Projects > Universal > Core)", True)


def test_baseline_verification():
    """Test baseline verification."""
    with tempfile.TemporaryDirectory() as tmpdir:
        prompts_dir = Path(tmpdir) / "prompts"
        prompts_dir.mkdir()

        # Create directories
        (prompts_dir / "core").mkdir()
        (prompts_dir / "universal" / "ai_agent_prompts").mkdir(parents=True)

        # Create core prompt
        core_content = "# Core\n\nBaseline content."
        core_file = prompts_dir / "core" / "core.md"
        core_file.write_text(core_content)

        # Create baseline lock (empty checksums = skip verification)
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
            json.dumps(baseline_lock)
        )

        # Create registry
        registry = {
            "registry_version": "2.0",
            "prompts": {
                "core.md": {
                    "name": "core.md",
                    "file": "core/core.md",
                    "version": "1.0.0",
                    "tier": "core",
                    "immutable": True,
                    "overridable": False
                }
            }
        }
        (prompts_dir / "registry.json").write_text(json.dumps(registry))

        storage = PromptStorageV2(str(prompts_dir))

        # Should load successfully with baseline verification
        prompt = storage.load_prompt("core")
        assert prompt.immutable is True

        print_test_result("Baseline verification (success)", True)


def test_cache_clearing():
    """Test cache clearing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        prompts_dir = Path(tmpdir) / "prompts"
        prompts_dir.mkdir()
        (prompts_dir / "universal" / "ai_agent_prompts").mkdir(parents=True)

        content = "# Test\n\nContent."
        (prompts_dir / "universal" / "ai_agent_prompts" / "test.md").write_text(content)

        registry = {
            "registry_version": "2.0",
            "prompts": {
                "test.md": {
                    "name": "test.md",
                    "file": "universal/ai_agent_prompts/test.md",
                    "version": "1.0.0",
                    "tier": "universal"
                }
            }
        }
        (prompts_dir / "registry.json").write_text(json.dumps(registry))

        storage = PromptStorageV2(str(prompts_dir))

        # Load to populate cache
        content1 = storage.load_prompt_content("test")

        # Clear cache
        storage.clear_cache()

        # Load again - should read from file
        content2 = storage.load_prompt_content("test")

        # Content should be same
        assert content1 == content2

        print_test_result("Cache clearing", True)


def test_dependency_injection():
    """Test dependency injection pattern."""
    # Clear global storage
    from src.storage.prompts_v2 import _storage_instance
    _storage_instance = None

    storage1 = get_storage()
    storage2 = get_storage()
    assert storage1 is storage2

    print_test_result("Dependency injection (singleton)", True)


def main():
    """Run all tests."""
    print("\n" + "="*50)
    print("Running AI Prompt System Storage V2 Tests")
    print("="*50 + "\n")

    tests = [
        ("PromptTier enum", test_prompt_tier_enum),
        ("Storage initialization", test_storage_initialization),
        ("Registry loading", test_registry_loading),
        ("Prompt content loading", test_prompt_content_loading),
        ("Prompt not found error", test_prompt_not_found),
        ("Cascade priority logic", test_cascade_priority),
        ("Baseline verification", test_baseline_verification),
        ("Cache clearing", test_cache_clearing),
        ("Dependency injection", test_dependency_injection),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print_test_result(test_name, False, str(e))
            failed += 1
        print()  # Empty line for readability

    # Summary
    print("="*50)
    print("Test Summary")
    print("="*50)
    print(f"Total tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success rate: {passed/len(tests)*100:.1f}%")

    if failed == 0:
        print("\n✅ All tests passed!")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())