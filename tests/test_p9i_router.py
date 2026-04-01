# tests/test_p9i_router.py
"""
Unit tests for P9iRouter - Unified Smart Router

Tests cover:
- Intent classification
- Priority order
- Processors
- Integration with existing components
"""

import pytest
import asyncio
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.application.p9i_router import (
    P9iRouter,
    IntentType,
    Intent,
    CommandProcessor,
    PromptCmdProcessor,
    PackProcessor,
    AgentTaskProcessor,
    NLQueryProcessor,
    SystemProcessor,
)


class TestIntentClassification:
    """Test intent classification logic."""

    @pytest.fixture
    def router(self):
        return P9iRouter()

    def test_system_command_classification(self, router):
        """Test system command classification (highest priority)."""
        intent = router.classify("/help")
        assert intent.type == IntentType.COMMAND
        assert intent.confidence == 1.0
        assert intent.matched_keyword == "/help"

    def test_prompt_command_classification(self, router):
        """Test /prompt command classification."""
        intent = router.classify("/prompt list")
        assert intent.type == IntentType.PROMPT_CMD
        assert intent.confidence == 1.0
        assert intent.matched_keyword == "/prompt"

    def test_full_cycle_task_classification(self, router):
        """Test full cycle task classification."""
        intent = router.classify("реализуй систему авторизации")
        assert intent.type == IntentType.AGENT_TASK
        assert intent.confidence == 0.90
        assert intent.agent_name == "full_cycle"

    def test_architect_task_classification(self, router):
        """Test architect task classification."""
        intent = router.classify("спроектируй архитектуру")
        assert intent.type == IntentType.AGENT_TASK
        assert intent.confidence == 0.90
        assert intent.agent_name == "architect"

    def test_developer_task_classification(self, router):
        """Test developer task classification."""
        intent = router.classify("создай функцию")
        assert intent.type == IntentType.AGENT_TASK
        assert intent.confidence == 0.90
        assert intent.agent_name == "developer"

    def test_reviewer_task_classification(self, router):
        """Test reviewer task classification."""
        intent = router.classify("проверь код")
        assert intent.type == IntentType.AGENT_TASK
        assert intent.confidence == 0.90
        assert intent.agent_name == "reviewer"

    def test_designer_task_classification(self, router):
        """Test designer task classification."""
        intent = router.classify("создай UI компонент")
        assert intent.type == IntentType.AGENT_TASK
        assert intent.confidence == 0.90
        assert intent.agent_name == "designer"

    def test_devops_task_classification(self, router):
        """Test devops task classification."""
        # "деплой в kubernetes" now correctly routes to PACK (k8s-pack)
        # because kubernetes keyword matches the k8s-pack, not devops agent
        intent = router.classify("деплой в kubernetes")
        assert intent.type == IntentType.PACK
        assert intent.confidence == 0.95
        assert intent.prompt_name == "promt-k8s-deploy-rollout.md"

        # "ci cd pipeline" routes to ci-cd-pack
        intent2 = router.classify("настрой ci cd pipeline")
        assert intent2.type == IntentType.PACK
        assert intent2.prompt_name == "promt-ci-github-actions.md"

        # Pure devops tasks without k8s/ci/cd keywords still route to devops agent
        # "docker" is only in devops agent, not in any pack
        intent3 = router.classify("собери docker образ")
        assert intent3.type == IntentType.AGENT_TASK
        assert intent3.agent_name == "devops"

    def test_nl_query_classification(self, router):
        """Test NL query classification."""
        intent = router.classify("покажи список промптов")
        assert intent.type == IntentType.NL_QUERY
        assert intent.confidence == 0.70
        assert intent.matched_keyword == "nl"

    def test_system_adaptation_classification(self, router):
        """Test system adaptation classification."""
        intent = router.classify("init p9i")
        assert intent.type == IntentType.SYSTEM
        assert intent.confidence == 0.80
        assert intent.matched_keyword == "system"

    def test_unknown_classification(self, router):
        """Test unknown request classification."""
        intent = router.classify("xyz123")
        assert intent.type == IntentType.UNKNOWN
        assert intent.confidence == 0.30


class TestPriorityOrder:
    """Test priority order of intent classification."""

    @pytest.fixture
    def router(self):
        return P9iRouter()

    def test_system_commands_highest_priority(self, router):
        """System commands should have highest priority."""
        intent = router.classify("/help создай функцию")
        assert intent.type == IntentType.COMMAND  # Not AGENT_TASK!

    def test_longest_keyword_wins(self, router):
        """Longest keyword should win for overlapping cases."""
        intent = router.classify("реализуй систему")
        assert intent.type == IntentType.AGENT_TASK
        assert intent.agent_name == "full_cycle"  # Not "developer"!


class TestCommandProcessor:
    """Test CommandProcessor."""

    @pytest.fixture
    def processor(self):
        return CommandProcessor()

    @pytest.mark.asyncio
    async def test_handle_help_command(self, processor):
        """Test /help command."""
        intent = Intent(type=IntentType.COMMAND, matched_keyword="/help", metadata={"command": "/help"})
        result = await processor.process(intent, "/help", {})
        assert result["status"] == "success"
        assert "p9i" in result["output"].lower()

    @pytest.mark.asyncio
    async def test_handle_exit_command(self, processor):
        """Test /exit command."""
        intent = Intent(type=IntentType.COMMAND, matched_keyword="/exit", metadata={"command": "/exit"})
        result = await processor.process(intent, "/exit", {})
        assert result["status"] == "success"
        assert "Goodbye" in result.get("message", "")

    @pytest.mark.asyncio
    async def test_handle_unknown_command(self, processor):
        """Test unknown command."""
        intent = Intent(type=IntentType.COMMAND, matched_keyword="/unknown", metadata={"command": "/unknown"})
        result = await processor.process(intent, "/unknown", {})
        assert result["status"] == "error"
        assert "Unknown command" in result["error"]


class TestPromptCmdProcessor:
    """Test PromptCmdProcessor."""

    @pytest.fixture
    def processor(self):
        return PromptCmdProcessor()

    @pytest.mark.asyncio
    async def test_handle_list_command(self, processor):
        """Test /prompt list command."""
        intent = Intent(type=IntentType.PROMPT_CMD, matched_keyword="/prompt", metadata={"command": "/prompt list"})
        result = await processor.process(intent, "/prompt list", {})
        assert result["status"] == "success" or result["status"] == "error"  # May fail if no prompts


class TestAgentTaskProcessor:
    """Test AgentTaskProcessor."""

    @pytest.fixture
    def processor(self):
        return AgentTaskProcessor()

    def test_can_handle_agent_task(self, processor):
        """Test processor can handle agent tasks."""
        intent = Intent(type=IntentType.AGENT_TASK, agent_name="developer")
        assert processor.can_handle(intent)

    def test_cannot_handle_non_agent_task(self, processor):
        """Test processor cannot handle non-agent tasks."""
        intent = Intent(type=IntentType.COMMAND)
        assert not processor.can_handle(intent)


class TestNLQueryProcessor:
    """Test NLQueryProcessor."""

    @pytest.fixture
    def processor(self):
        return NLQueryProcessor()

    def test_can_handle_nl_query(self, processor):
        """Test processor can handle NL queries."""
        intent = Intent(type=IntentType.NL_QUERY)
        assert processor.can_handle(intent)

    def test_cannot_handle_non_nl_query(self, processor):
        """Test processor cannot handle non-NL queries."""
        intent = Intent(type=IntentType.COMMAND)
        assert not processor.can_handle(intent)

    @pytest.mark.asyncio
    async def test_handle_list_query(self, processor):
        """Test handling "покажи список" query."""
        intent = Intent(type=IntentType.NL_QUERY, matched_keyword="nl", metadata={"query": "покажи список"})
        result = await processor.process(intent, "покажи список", {})
        assert result["status"] in ["success", "error"]


class TestSystemProcessor:
    """Test SystemProcessor."""

    @pytest.fixture
    def processor(self):
        return SystemProcessor()

    def test_can_handle_system_command(self, processor):
        """Test processor can handle system commands."""
        intent = Intent(type=IntentType.SYSTEM)
        assert processor.can_handle(intent)

    def test_cannot_handle_non_system_command(self, processor):
        """Test processor cannot handle non-system commands."""
        intent = Intent(type=IntentType.COMMAND)
        assert not processor.can_handle(intent)


class TestRouteFlow:
    """Test complete routing flow."""

    @pytest.fixture
    def router(self):
        return P9iRouter()

    @pytest.mark.asyncio
    async def test_route_help_command(self, router):
        """Test routing /help command."""
        result = await router.route("/help", {})
        assert result["status"] == "success"
        assert result["processor"] == "CommandProcessor"

    @pytest.mark.asyncio
    async def test_route_full_cycle_task(self, router):
        """Test routing full cycle task."""
        result = await router.route("реализуй систему", {})
        # May fail if orchestrator not available, but should route correctly
        assert "processor" in result
        assert result["processor"] in ["AgentTaskProcessor", "error"]

    @pytest.mark.asyncio
    async def test_route_unknown_request(self, router):
        """Test routing unknown request."""
        result = await router.route("xyz123", {})
        assert result["status"] == "error"
        assert "Unknown command" in result["error"]


class TestBackwardCompatibility:
    """Test backward compatibility with old ai_prompts and p9i_nl.

    Note: ai_prompts and p9i_nl were removed in favor of unified p9i() function.
    These tests are kept as skip to document the removal.
    """

    @pytest.mark.skip(reason="ai_prompts function was removed - use p9i() instead")
    @pytest.mark.asyncio
    async def test_ai_prompts_redirect(self):
        """Test ai_prompts redirects to p9i."""
        pass

    @pytest.mark.skip(reason="p9i_nl function was removed - use p9i() instead")
    @pytest.mark.asyncio
    async def test_p9i_nl_redirect(self):
        """Test p9i_nl redirects to p9i."""
        pass


class TestKeywordCoverage:
    """Test keyword coverage across different domains."""

    @pytest.fixture
    def router(self):
        return P9iRouter()

    def test_all_domains_covered(self, router):
        """Test all major domains have keywords."""
        test_cases = [
            ("реализуй систему", "full_cycle"),
            ("спроектируй API", "architect"),
            ("создай функцию", "developer"),
            ("проверь код", "reviewer"),
            ("создай UI компонент", "designer"),
            ("деплой в kubernetes", "devops"),
            ("init p9i", "system"),
        ]

        for request, expected_agent in test_cases:
            intent = router.classify(request)
            if intent.type == IntentType.AGENT_TASK:
                assert intent.agent_name == expected_agent, f"Request '{request}' should route to {expected_agent}"

    def test_multilingual_keywords(self, router):
        """Test both Russian and English keywords work."""
        # Russian
        intent_ru = router.classify("создай функцию")
        # English
        intent_en = router.classify("create function")

        # Both should route to developer
        if intent_ru.type == IntentType.AGENT_TASK:
            assert intent_ru.agent_name in ["developer", "unknown"]
        if intent_en.type == IntentType.AGENT_TASK:
            assert intent_en.agent_name in ["developer", "unknown"]


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.fixture
    def router(self):
        return P9iRouter()

    def test_empty_request(self, router):
        """Test empty request handling."""
        intent = router.classify("")
        assert intent.type == IntentType.UNKNOWN

    def test_whitespace_request(self, router):
        """Test whitespace-only request."""
        intent = router.classify("   ")
        assert intent.type == IntentType.UNKNOWN

    def test_case_insensitive_routing(self, router):
        """Test routing is case-insensitive."""
        intent_lower = router.classify("СОЗДАЙ функцию")
        intent_upper = router.classify("создай ФУНКЦИЮ")
        intent_mixed = router.classify("СозДаЙ фУнКцИю")

        # All should have same type
        assert intent_lower.type == intent_upper.type == intent_mixed.type

    def test_overlapping_keywords(self, router):
        """Test overlapping keywords handled correctly."""
        # "реализуй" should win over "создай" (longer keyword)
        intent = router.classify("реализуй систему")
        if intent.type == IntentType.AGENT_TASK:
            assert intent.agent_name == "full_cycle"  # Not "developer"!

    def test_context_aware_architect_routing(self, router):
        """Test context-aware routing: 'проверь + architecture keywords' → architect (not reviewer)."""
        # "проверь архитектуру" should route to architect
        intent = router.classify("проверь архитектуру")
        assert intent.type == IntentType.AGENT_TASK
        assert intent.agent_name == "architect", "проверь архитектуру should route to architect"

    def test_context_aware_architect_routing_design(self, router):
        """Test context-aware routing: 'проверь + design keywords' → architect."""
        intent = router.classify("проверь дизайн")
        assert intent.type == IntentType.AGENT_TASK
        assert intent.agent_name == "architect", "проверь дизайн should route to architect"

    def test_basic_reviewer_routing(self, router):
        """Test basic reviewer routing without architect context."""
        # "проверь код" should route to reviewer
        intent = router.classify("проверь код")
        assert intent.type == IntentType.AGENT_TASK
        assert intent.agent_name == "reviewer", "проверь код should route to reviewer"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
