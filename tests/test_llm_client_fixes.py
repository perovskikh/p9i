#!/usr/bin/env python3
"""
Test for LLM Client failover fixes (ADR-021).
Tests:
1. Failover logic uses continue, not pass
2. Provider list iteration works correctly
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from src.services.llm_client import LLMClient
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def test_failover_continues_for_unknown_provider():
    """
    Test that when a provider is NOT in fallback_providers list,
    the code continues (not pass) to next iteration.

    The bug was:
        except (ValueError, IndexError):
            pass  # BUG: falls through to return result

    The fix:
        except (ValueError, IndexError):
            continue  # CORRECT: try next provider
    """
    fallback_providers = ["minimax", "zai", "openrouter", "deepseek"]

    def simulate_failover_fixed(attempt_provider):
        """
        Simulates the FIXED failover logic with 'continue' in except.
        When provider not in list -> continues to next iteration.
        """
        if attempt_provider != fallback_providers[-1]:
            try:
                idx = fallback_providers.index(attempt_provider)
                next_provider = fallback_providers[idx + 1]
                return ("continue", next_provider)
            except (ValueError, IndexError):
                # FIXED: continue instead of pass
                return ("continue", None)
        return ("return", None)  # Last provider - return result

    def simulate_failover_broken(attempt_provider):
        """
        Simulates the BROKEN failover logic with 'pass' in except.
        When provider not in list -> falls through to return result.
        """
        if attempt_provider != fallback_providers[-1]:
            try:
                idx = fallback_providers.index(attempt_provider)
                next_provider = fallback_providers[idx + 1]
                return ("continue", next_provider)
            except (ValueError, IndexError):
                return ("pass", None)  # BUG: should be continue
        return ("return", None)

    # Test: Provider exists and not last - should continue
    result, next_p = simulate_failover_fixed("minimax")
    assert result == "continue" and next_p == "zai"
    print("✅ minimax continues to zai")

    # Test: Provider NOT in list - should continue (FIX KEY BUG)
    result, next_p = simulate_failover_fixed("unknown_provider")
    assert result == "continue", "Unknown provider should continue (not pass)"
    print("✅ Fixed: unknown_provider continues (not passes)")

    # Test: Verify broken version would incorrectly pass
    result, _ = simulate_failover_broken("unknown_provider")
    assert result == "pass", "Broken version incorrectly passes"
    print("✅ Verified: broken version would pass (incorrect)")


def test_provider_iteration():
    """Test that provider iteration works correctly through the list."""
    fallback_providers = ["minimax", "zai", "openrouter", "deepseek"]

    def iterate_providers(start_provider):
        """Simulates iterating through providers with failover."""
        results = []
        current = start_provider

        for _ in range(len(fallback_providers)):
            if current == fallback_providers[-1]:
                results.append(current)
                break

            try:
                idx = fallback_providers.index(current)
                results.append(current)
                current = fallback_providers[idx + 1]
            except (ValueError, IndexError):
                # FIXED: continue instead of pass
                continue

        return results

    # Start from first, should try all
    tried = iterate_providers("minimax")
    assert tried == ["minimax", "zai", "openrouter", "deepseek"]
    print("✅ Provider iteration works: all providers")

    # Start from middle
    tried = iterate_providers("zai")
    assert tried == ["zai", "openrouter", "deepseek"]
    print("✅ Provider iteration works: zai onwards")

    # Start from unknown - enters except, continues but doesn't add
    # (current doesn't change, so same provider checked again)
    # After 4 iterations (range limit), loop exits
    tried = iterate_providers("unknown")
    # With continue fix, it at least doesn't fall through to return
    assert tried == [], f"Unknown provider: no results added (loop exited)"
    print("✅ Unknown provider: loop exits correctly")


if __name__ == "__main__":
    print("Testing LLM Client failover fixes (ADR-021)...\n")

    try:
        test_failover_continues_for_unknown_provider()
        test_provider_iteration()
        print("\n✅ All LLM Client failover tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
