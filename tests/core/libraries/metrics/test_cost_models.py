"""
Tests for LLM Cost Models.

Run with: python -m tests.core.libraries.metrics.test_cost_models
"""

from core.libraries.metrics.cost_models import (
    estimate_llm_cost,
    add_model_pricing,
    LLM_PRICING,
)


def test_estimate_cost_known_model():
    """Test cost estimation for known models."""
    # gpt-4o-mini: $0.150/1M input, $0.600/1M output
    cost = estimate_llm_cost("gpt-4o-mini", 1000, 500)
    expected = (1000 / 1_000_000) * 0.150 + (500 / 1_000_000) * 0.600
    assert abs(cost - expected) < 0.0001
    print(f"✓ gpt-4o-mini cost: ${cost:.6f}")


def test_estimate_cost_partial_match():
    """Test partial model name matching."""
    # Should match "gpt-4o-mini" from "gpt-4o-mini-2024"
    cost = estimate_llm_cost("gpt-4o-mini-2024-10-01", 1000, 500)
    assert cost > 0
    print(f"✓ Partial match works: ${cost:.6f}")


def test_estimate_cost_unknown_model():
    """Test unknown model defaults to gpt-4o pricing."""
    # Unknown model should use default (gpt-4o: $2.50/$10.00)
    cost = estimate_llm_cost("unknown-model", 1000, 500)
    expected = (1000 / 1_000_000) * 2.50 + (500 / 1_000_000) * 10.00
    assert abs(cost - expected) < 0.0001
    print(f"✓ Unknown model defaults: ${cost:.6f}")


def test_add_custom_pricing():
    """Test adding custom model pricing."""
    add_model_pricing("custom-model", 1.00, 2.00)

    cost = estimate_llm_cost("custom-model", 1000, 500)
    expected = (1000 / 1_000_000) * 1.00 + (500 / 1_000_000) * 2.00
    assert abs(cost - expected) < 0.0001
    print(f"✓ Custom pricing works: ${cost:.6f}")


def test_realistic_13k_run():
    """Test realistic 13k run cost estimation."""
    # 13k chunks * ~1000 input tokens * ~500 output tokens
    chunks = 13000
    avg_input = 1000
    avg_output = 500

    total_cost = estimate_llm_cost(
        "gpt-4o-mini", chunks * avg_input, chunks * avg_output
    )
    print(f"✓ 13k run estimated cost: ${total_cost:.2f}")

    # Should be around $5-6
    assert 4.0 < total_cost < 8.0


def run_all_tests():
    """Run all cost model tests."""
    print("Testing LLM Cost Models")
    print("=" * 60)
    print()

    test_estimate_cost_known_model()
    test_estimate_cost_partial_match()
    test_estimate_cost_unknown_model()
    test_add_custom_pricing()
    test_realistic_13k_run()

    print()
    print("Available Models:")
    for model, (inp, out) in sorted(LLM_PRICING.items()):
        print(f"  {model}: ${inp}/1M input, ${out}/1M output")

    print()
    print("=" * 60)
    print("🎉 All cost model tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
