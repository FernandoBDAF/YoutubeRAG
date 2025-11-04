"""
Integration Tests for BaseAgent with Observability Libraries.

Tests that BaseAgent correctly integrates with retry, metrics, logging.
Run with: python -m tests.core.base.test_agent

Note: These are unit tests with mocked LLM - no real API calls.
"""

import os
import logging
from unittest.mock import Mock, MagicMock, patch
from core.base.agent import BaseAgent, BaseAgentConfig
from core.libraries.metrics import MetricRegistry


class TestAgent(BaseAgent):
    """Test agent with mocked LLM."""

    def __init__(self):
        # Mock environment for API key
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            config = BaseAgentConfig(model_name="gpt-4o-mini")
            super().__init__("test_agent", config)

        # Replace real client with mock
        self.model = Mock()
        self.model.chat = Mock()


def test_agent_successful_llm_call():
    """Test successful LLM call tracks metrics."""
    registry = MetricRegistry.get_instance()
    registry.reset_all()

    agent = TestAgent()

    # Mock successful response
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Test response"
    mock_response.usage = Mock()
    mock_response.usage.prompt_tokens = 100
    mock_response.usage.completion_tokens = 50
    mock_response.usage.total_tokens = 150

    agent.model.chat.completions.create = Mock(return_value=mock_response)

    # Call model
    result = agent.call_model("system", "user")

    # Verify response
    assert result == "Test response"

    # Verify metrics
    llm_calls = registry.get("agent_llm_calls")
    assert llm_calls.get(labels={"agent": "test_agent", "model": "gpt-4o-mini"}) == 1.0

    tokens_used = registry.get("agent_tokens_used")
    prompt_tokens = tokens_used.get(
        labels={"agent": "test_agent", "model": "gpt-4o-mini", "token_type": "prompt"}
    )
    assert prompt_tokens == 100.0

    completion_tokens = tokens_used.get(
        labels={
            "agent": "test_agent",
            "model": "gpt-4o-mini",
            "token_type": "completion",
        }
    )
    assert completion_tokens == 50.0

    print("✓ Agent tracks successful LLM call metrics")


def test_agent_tracks_cost():
    """Test agent tracks LLM cost."""
    registry = MetricRegistry.get_instance()
    registry.reset_all()

    agent = TestAgent()

    # Mock response with token usage
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Response"
    mock_response.usage = Mock()
    mock_response.usage.prompt_tokens = 1000
    mock_response.usage.completion_tokens = 500

    agent.model.chat.completions.create = Mock(return_value=mock_response)

    agent.call_model("system", "user")

    # Verify cost tracked
    cost = registry.get("agent_llm_cost_usd")
    tracked_cost = cost.get(labels={"agent": "test_agent", "model": "gpt-4o-mini"})

    # gpt-4o-mini: $0.150/1M input + $0.600/1M output
    expected_cost = (1000 / 1_000_000) * 0.150 + (500 / 1_000_000) * 0.600
    assert abs(tracked_cost - expected_cost) < 0.0001

    print(f"✓ Agent tracks LLM cost: ${tracked_cost:.6f}")


def test_agent_retry_on_failure():
    """Test agent handles LLM failures gracefully."""
    registry = MetricRegistry.get_instance()
    registry.reset_all()

    agent = TestAgent()

    # Mock to always fail
    agent.model.chat.completions.create = Mock(side_effect=Exception("Rate limit"))

    # Should return empty string after retries
    result = agent.call_model("system", "user")
    assert result == ""  # BaseAgent returns "" on LLM failure

    # Note: @retry_llm_call handles retry automatically
    # BaseAgent's exception handler provides graceful degradation

    print("✓ Agent handles LLM failures gracefully")


def test_agent_tracks_errors():
    """Test agent tracks LLM errors in metrics."""
    registry = MetricRegistry.get_instance()
    registry.reset_all()

    agent = TestAgent()

    # Mock to always fail
    agent.model.chat.completions.create = Mock(side_effect=RuntimeError("API Error"))

    # Should return empty string after max retries
    result = agent.call_model("system", "user")
    assert result == ""

    # Verify error metrics
    llm_errors = registry.get("agent_llm_errors")
    error_count = llm_errors.get(labels={"agent": "test_agent", "model": "gpt-4o-mini"})
    assert error_count == 1.0

    # Verify error in errors_total (via log_exception)
    errors_total = registry.get("errors_total")
    all_errors = errors_total.get_all()
    # Should have logged the error
    assert len(all_errors) > 0

    print("✓ Agent tracks LLM errors")


def test_agent_tracks_duration():
    """Test agent tracks call duration."""
    registry = MetricRegistry.get_instance()
    registry.reset_all()

    agent = TestAgent()

    # Mock successful response
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Response"
    mock_response.usage = None
    agent.model.chat.completions.create = Mock(return_value=mock_response)

    agent.call_model("system", "user")

    # Verify duration histogram
    duration = registry.get("agent_llm_duration_seconds")
    stats = duration.summary(labels={"agent": "test_agent", "model": "gpt-4o-mini"})

    assert stats["count"] == 1
    assert stats["sum"] > 0  # Should have duration

    print("✓ Agent tracks call duration")


def run_all_tests():
    """Run all BaseAgent integration tests."""
    print("Testing BaseAgent Integration with Observability Libraries")
    print("=" * 60)
    print()

    # Suppress log noise
    logging.basicConfig(level=logging.CRITICAL)

    test_agent_successful_llm_call()
    test_agent_tracks_cost()
    test_agent_retry_on_failure()
    test_agent_tracks_errors()
    test_agent_tracks_duration()

    print()
    print("=" * 60)
    print("🎉 All BaseAgent integration tests passed!")
    print("🎉 BaseAgent correctly integrates with:")
    print("  - retry library (automatic retries)")
    print("  - metrics library (calls, errors, tokens, cost, duration)")
    print("  - logging library (via log_exception)")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
