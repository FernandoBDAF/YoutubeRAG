"""
Tests for GraphRAG Ontology-Based Extraction.

Tests normalization, canonicalization, type constraints, and symmetric predicates.
Run with: python tests/test_ontology_extraction.py
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from business.agents.graphrag.extraction import GraphExtractionAgent
from core.models.graphrag import (
    KnowledgeModel,
    EntityModel,
    RelationshipModel,
    EntityType,
)
from core.libraries.ontology.loader import load_ontology, clear_cache
from openai import OpenAI


def test_normalization_prevents_bad_stems():
    """Test that normalization avoids bad stems."""
    # Try to use real OpenAI client if API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        llm_client = OpenAI(api_key=api_key)
        print("  Using real OpenAI client for LLM normalization")
    else:
        # Create proper mock for nested structure
        mock_llm_client = MagicMock(spec=OpenAI)
        # Mock the nested chat.completions.create structure
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "teach"  # Default response for ambiguous tokens
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]

        mock_chat = MagicMock()
        mock_completions = MagicMock()

        # Create a function that returns different responses based on token
        def mock_create(**kwargs):
            user_content = kwargs.get("messages", [{}])[-1].get("content", "")
            # Extract token from prompt (format: "Predicate: {token}")
            token = None
            if "Predicate:" in user_content:
                token = user_content.split("Predicate:")[-1].strip().split()[0].strip()

            # Map known tokens to expected results
            token_map = {
                "teaches": "teach",
                "includes": "include",
                "uses": "use",
                "boxes": "box",
                "reaches": "reach",
                "phases": "phases",
                "classes": "classes",
                "bases": "bases",
                "cases": "cases",
                # Additional tokens for canonicalization tests
                "utiliz": "utilize",
                "does": "do",
                "results": "result",
                "results_in": "result_in",  # Keep underscore-separated predicates as-is
            }

            if token and token in token_map:
                result = token_map[token]
            elif token:
                # For unknown tokens, try to normalize by removing "s" or "es"
                # But preserve underscores (multi-word predicates)
                if "_" in token:
                    # For multi-word predicates, normalize each part
                    parts = token.split("_")
                    normalized_parts = []
                    for part in parts:
                        if part.endswith("es") and len(part) > 4:
                            if (
                                part.endswith("ches")
                                or part.endswith("ses")
                                or part.endswith("shes")
                            ):
                                normalized_parts.append(part[:-1])  # Remove "s"
                            else:
                                normalized_parts.append(part[:-2])  # Remove "es"
                        elif part.endswith("s") and len(part) > 2:
                            normalized_parts.append(part[:-1])  # Remove "s"
                        else:
                            normalized_parts.append(part)  # Keep as-is
                    result = "_".join(normalized_parts)
                elif token.endswith("es") and len(token) > 4:
                    # Try removing "s" first (for verbs like "teaches")
                    if (
                        token.endswith("ches")
                        or token.endswith("ses")
                        or token.endswith("shes")
                    ):
                        result = token[:-1]  # Remove "s"
                    else:
                        result = token[:-2]  # Remove "es"
                elif token.endswith("s") and len(token) > 2:
                    result = token[:-1]  # Remove "s"
                else:
                    result = token  # Keep as-is
            else:
                result = "unknown"  # Fallback

            # Always set content to a string (never MagicMock)
            mock_message.content = str(result)
            return mock_response

        mock_completions.create = mock_create
        mock_chat.completions = mock_completions
        mock_llm_client.chat = mock_chat
        llm_client = mock_llm_client
        print("  Using mock OpenAI client for testing")

    agent = GraphExtractionAgent(llm_client=llm_client, model_name="gpt-4o-mini")

    test_cases = [
        ("uses", "use"),  # Should stem to "use", not "us"
        ("has", "has"),  # Should keep "has", not stem to "ha"
        ("applies_to", "apply_to"),  # Should stem to "apply_to", not "appli_to"
        ("classes", "classes"),  # Should keep plural form
        ("teaches", "teach"),  # Normal stem (requires LLM)
        ("includes", "include"),  # Normal stem (requires LLM)
    ]

    for input_pred, expected in test_cases:
        result = agent._normalize_predicate_string(input_pred)
        assert (
            result == expected
        ), f"Expected '{expected}' for '{input_pred}', got '{result}'"
    print("✓ Normalization prevents bad stems")


def test_normalization_handles_short_words():
    """Test that short words are not over-stemmed."""
    mock_llm_client = MagicMock(spec=OpenAI)
    agent = GraphExtractionAgent(llm_client=mock_llm_client, model_name="gpt-4o-mini")

    short_words = ["is", "as", "has", "us"]
    for word in short_words:
        result = agent._normalize_predicate_string(word)
        assert len(result) >= 2, f"Short word '{word}' was over-stemmed to '{result}'"
    print("✓ Normalization handles short words")


def test_canonicalization_with_mapping():
    """Test that predicates in predicate_map are mapped correctly."""
    mock_llm_client = MagicMock(spec=OpenAI)
    agent = GraphExtractionAgent(llm_client=mock_llm_client, model_name="gpt-4o-mini")

    ontology = agent.ontology
    if "utiliz" in ontology.get("predicate_map", {}):
        canonical = agent._canonicalize_predicate("utiliz", confidence=0.5)
        assert canonical == ontology["predicate_map"]["utiliz"]
        print("✓ Canonicalization with mapping works")
    else:
        print("⚠ Skipped: predicate_map.yml doesn't have 'utiliz' mapping")


def test_canonicalization_drops_explicit():
    """Test that __DROP__ predicates return None."""
    mock_llm_client = MagicMock(spec=OpenAI)
    agent = GraphExtractionAgent(llm_client=mock_llm_client, model_name="gpt-4o-mini")

    ontology = agent.ontology
    drop_predicates = [
        k for k, v in ontology.get("predicate_map", {}).items() if v == "__DROP__"
    ]
    if drop_predicates:
        result = agent._canonicalize_predicate(drop_predicates[0], confidence=0.5)
        assert (
            result is None
        ), f"Expected None for __DROP__ predicate '{drop_predicates[0]}'"
        print("✓ Canonicalization drops explicit __DROP__ predicates")
    else:
        print("⚠ Skipped: No __DROP__ predicates found in predicate_map")


def test_canonicalization_keeps_canonical():
    """Test that already-canonical predicates are kept."""
    # Use the same mock setup as other tests
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        llm_client = OpenAI(api_key=api_key)
    else:
        # Create proper mock for nested structure
        mock_llm_client = MagicMock(spec=OpenAI)
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content = ""  # Default
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]

        mock_chat = MagicMock()
        mock_completions = MagicMock()

        def mock_create(**kwargs):
            user_content = kwargs.get("messages", [{}])[-1].get("content", "")
            token = None
            if "Predicate:" in user_content:
                token = user_content.split("Predicate:")[-1].strip().split()[0].strip()

            # For canonical predicates, return them as-is (they're already normalized)
            if token:
                # Multi-word predicates: normalize each part
                if "_" in token:
                    parts = token.split("_")
                    normalized_parts = []
                    for part in parts:
                        if part.endswith("es") and len(part) > 4:
                            if (
                                part.endswith("ches")
                                or part.endswith("ses")
                                or part.endswith("shes")
                            ):
                                normalized_parts.append(part[:-1])
                            else:
                                normalized_parts.append(part[:-2])
                        elif part.endswith("s") and len(part) > 2:
                            normalized_parts.append(part[:-1])
                        else:
                            normalized_parts.append(part)
                    result = "_".join(normalized_parts)
                else:
                    result = token  # Keep as-is for canonical predicates
            else:
                result = ""

            mock_message.content = str(result)
            return mock_response

        mock_completions.create = mock_create
        mock_chat.completions = mock_completions
        mock_llm_client.chat = mock_chat
        llm_client = mock_llm_client

    agent = GraphExtractionAgent(llm_client=llm_client, model_name="gpt-4o-mini")

    ontology = agent.ontology
    canonical_preds = list(ontology.get("canonical_predicates", set()))[:5]
    if canonical_preds:
        for pred in canonical_preds:
            result = agent._canonicalize_predicate(pred, confidence=0.5)
            assert (
                result == pred
            ), f"Canonical predicate '{pred}' was changed to '{result}'"
        print("✓ Canonicalization keeps canonical predicates")
    else:
        print("⚠ Skipped: No canonical predicates loaded")


def test_soft_keep_unknown_predicates():
    """Test that unknown predicates can be soft-kept with env flag."""
    # Set env flag
    os.environ["GRAPHRAG_KEEP_UNKNOWN_PREDICATES"] = "true"

    try:
        clear_cache()  # Reload agent with new env var
        # Create proper mock for nested structure
        mock_llm_client = MagicMock(spec=OpenAI)
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content = ""  # Default
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]

        mock_chat = MagicMock()
        mock_completions = MagicMock()

        def mock_create(**kwargs):
            user_content = kwargs.get("messages", [{}])[-1].get("content", "")
            token = None
            if "Predicate:" in user_content:
                token = user_content.split("Predicate:")[-1].strip().split()[0].strip()

            # For unknown predicates, return as-is (they're already normalized)
            if token:
                result = token  # Keep as-is
            else:
                result = ""

            mock_message.content = str(result) if result else ""
            return mock_response

        mock_completions.create = mock_create
        mock_chat.completions = mock_completions
        mock_llm_client.chat = mock_chat

        agent = GraphExtractionAgent(
            llm_client=mock_llm_client, model_name="gpt-4o-mini"
        )

        # Test with high confidence and sufficient length
        # Note: The result will be normalized, so we check it's not None and has sufficient length
        result = agent._canonicalize_predicate("unknown_predicate_xyz", confidence=0.9)
        assert (
            result is not None and len(result) >= 4
        ), f"Should soft-keep high-confidence unknown predicate, got: {result}"

        # Test with low confidence - should drop
        result = agent._canonicalize_predicate("unknown_short", confidence=0.5)
        assert result is None, "Should drop low-confidence unknown predicate"

        # Test with short length - should drop
        result = agent._canonicalize_predicate("abc", confidence=0.9)
        assert result is None, "Should drop short unknown predicate"

        print("✓ Soft-keep unknown predicates works")
    finally:
        # Clean up
        del os.environ["GRAPHRAG_KEEP_UNKNOWN_PREDICATES"]
        clear_cache()


def test_type_constraint_allowed():
    """Test that allowed type pairs pass validation."""
    mock_llm_client = MagicMock(spec=OpenAI)
    agent = GraphExtractionAgent(llm_client=mock_llm_client, model_name="gpt-4o-mini")

    ontology = agent.ontology
    constraints = ontology.get("predicate_type_constraints", {})

    if constraints:
        # Get first predicate with constraints
        predicate = list(constraints.keys())[0]
        allowed_pair = constraints[predicate][0]

        # Map to EntityType enum (or use string if not in enum)
        # Note: EntityType enum only has 7 types, but constraints may reference more
        # So we create a mock type object if needed
        src_type_str, tgt_type_str = allowed_pair

        # Try to find in enum
        src_type = None
        tgt_type = None
        for et in EntityType:
            if et.value == src_type_str:
                src_type = et
            if et.value == tgt_type_str:
                tgt_type = et

        # If not found in enum, create a simple object with .value attribute
        if src_type is None:

            class MockType:
                def __init__(self, value):
                    self.value = value

            src_type = MockType(src_type_str)

        if tgt_type is None:

            class MockType:
                def __init__(self, value):
                    self.value = value

            tgt_type = MockType(tgt_type_str)

        result = agent._validate_type_pair(predicate, src_type, tgt_type)
        assert (
            result is True
        ), f"Allowed type pair {allowed_pair} for '{predicate}' was rejected"
        print("✓ Type constraint allows valid pairs")
    else:
        print("⚠ Skipped: No type constraints loaded")


def test_type_constraint_violation():
    """Test that disallowed type pairs are rejected."""
    mock_llm_client = MagicMock(spec=OpenAI)
    agent = GraphExtractionAgent(llm_client=mock_llm_client, model_name="gpt-4o-mini")

    ontology = agent.ontology
    constraints = ontology.get("predicate_type_constraints", {})

    if constraints:
        # Get first predicate with constraints
        predicate = list(constraints.keys())[0]
        allowed_pair = constraints[predicate][0]

        # Create a violating pair (swap or use different types)
        violating_src = EntityType.PERSON
        violating_tgt = EntityType.LOCATION

        # Only test if this is actually a violation
        if [violating_src.value, violating_tgt.value] not in constraints[predicate]:
            result = agent._validate_type_pair(predicate, violating_src, violating_tgt)
            assert result is False, f"Violating type pair was incorrectly allowed"
            print("✓ Type constraint rejects invalid pairs")
        else:
            print("⚠ Skipped: Violating pair is actually allowed")
    else:
        print("⚠ Skipped: No type constraints loaded")


def test_symmetric_normalization():
    """Test that symmetric predicates have sorted endpoints."""
    import logging

    logging.basicConfig(level=logging.DEBUG)

    mock_llm_client = MagicMock(spec=OpenAI)
    agent = GraphExtractionAgent(llm_client=mock_llm_client, model_name="gpt-4o-mini")

    ontology = agent.ontology
    symmetric_preds = list(ontology.get("symmetric_predicates", set()))[:3]

    if not symmetric_preds:
        print("⚠ Skipped: No symmetric predicates loaded")
        return

    print(f"\n[DEBUG] Testing with symmetric predicate: {repr(symmetric_preds[0])}")
    print(
        f"[DEBUG] Symmetric predicates set: {sorted(list(ontology.get('symmetric_predicates', set())))}"
    )

    # Create test relationship with symmetric predicate
    entity_a = EntityModel(
        name="EntityA",
        type=EntityType.CONCEPT,
        description="Test entity A description",
        confidence=0.8,
    )
    entity_b = EntityModel(
        name="EntityB",
        type=EntityType.CONCEPT,
        description="Test entity B description",
        confidence=0.8,
    )

    rel = RelationshipModel(
        source_entity=entity_b,  # B -> A (should be swapped to A -> B)
        target_entity=entity_a,
        relation=symmetric_preds[0],
        description="Test relationship description",
        confidence=0.8,
    )

    print(f"[DEBUG] Created relationship:")
    print(f"  Source: {rel.source_entity.name}")
    print(f"  Target: {rel.target_entity.name}")
    print(f"  Relation: {repr(rel.relation)}")
    print(f"  Relation type: {type(rel.relation)}")
    print(
        f"  Relation in symmetric set: {rel.relation in ontology.get('symmetric_predicates', set())}"
    )

    # Normalize should swap to A -> B
    normalized = agent._normalize_symmetric_relation(rel)

    print(f"[DEBUG] Normalized relationship:")
    print(f"  Source: {normalized.source_entity.name}")
    print(f"  Target: {normalized.target_entity.name}")
    print(f"  Relation: {repr(normalized.relation)}")
    print(f"  Is same object: {rel is normalized}")

    # Note: EntityModel validator uses .title() which converts "EntityA" -> "Entitya"
    # So after validation, entity names are title-cased
    # The swap should result in: Entitya -> Entityb (alphabetical order)
    expected_source = entity_a.name  # Already title-cased by validator: "Entitya"
    expected_target = entity_b.name  # Already title-cased by validator: "Entityb"

    assert (
        normalized.source_entity.name == expected_source
    ), f"Should swap to alphabetical order. Got: {normalized.source_entity.name} -> {normalized.target_entity.name}, expected: {expected_source} -> {expected_target}"
    assert (
        normalized.target_entity.name == expected_target
    ), f"Should swap to alphabetical order. Got: {normalized.source_entity.name} -> {normalized.target_entity.name}, expected: {expected_source} -> {expected_target}"
    assert (
        normalized.relation == symmetric_preds[0]
    ), f"Predicate should remain unchanged. Got: {repr(normalized.relation)}, expected: {repr(symmetric_preds[0])}"
    print("✓ Symmetric normalization works")


def test_non_symmetric_unchanged():
    """Test that non-symmetric predicates are unchanged."""
    mock_llm_client = MagicMock(spec=OpenAI)
    agent = GraphExtractionAgent(llm_client=mock_llm_client, model_name="gpt-4o-mini")

    entity_a = EntityModel(
        name="EntityA",
        type=EntityType.CONCEPT,
        description="Test entity A description",
        confidence=0.8,
    )
    entity_b = EntityModel(
        name="EntityB",
        type=EntityType.CONCEPT,
        description="Test entity B description",
        confidence=0.8,
    )

    rel = RelationshipModel(
        source_entity=entity_a,
        target_entity=entity_b,
        relation="uses",  # Non-symmetric predicate
        description="Test relationship description",
        confidence=0.8,
    )

    normalized = agent._normalize_symmetric_relation(rel)

    # Note: EntityModel validator uses .title() which converts "EntityA" -> "Entitya"
    # So we check against the validated entity names
    expected_source = entity_a.name  # "Entitya" after validation
    expected_target = entity_b.name  # "Entityb" after validation

    assert (
        normalized.source_entity.name == expected_source
    ), f"Non-symmetric should remain unchanged. Got: {normalized.source_entity.name}, expected: {expected_source}"
    assert (
        normalized.target_entity.name == expected_target
    ), f"Non-symmetric should remain unchanged. Got: {normalized.target_entity.name}, expected: {expected_target}"
    assert normalized.relation == "uses", "Predicate should remain unchanged"
    assert (
        rel is normalized
    ), "Non-symmetric relationships should return the same object (unchanged)"
    print("✓ Non-symmetric predicates unchanged")


def test_loader_smoke_test():
    """Smoke test: verify loader returns expected structure."""
    clear_cache()
    ontology = load_ontology()

    assert isinstance(ontology, dict), "Ontology should be a dictionary"
    assert "canonical_predicates" in ontology, "Should have canonical_predicates"
    assert "symmetric_predicates" in ontology, "Should have symmetric_predicates"
    assert "predicate_map" in ontology, "Should have predicate_map"
    assert (
        "predicate_type_constraints" in ontology
    ), "Should have predicate_type_constraints"
    assert "type_map" in ontology, "Should have type_map"

    assert isinstance(
        ontology["canonical_predicates"], set
    ), "canonical_predicates should be a set"
    assert isinstance(ontology["predicate_map"], dict), "predicate_map should be a dict"

    print(f"✓ Loader smoke test passed")
    print(f"  - {len(ontology['canonical_predicates'])} canonical predicates")
    print(f"  - {len(ontology['symmetric_predicates'])} symmetric predicates")
    print(f"  - {len(ontology['predicate_map'])} predicate mappings")
    print(f"  - {len(ontology['predicate_type_constraints'])} type constraints")
    print(f"  - {len(ontology['type_map'])} type mappings")


def run_all_tests():
    """Run all ontology extraction tests."""
    print("Testing GraphRAG Ontology Extraction")
    print("=" * 60)
    print()

    test_normalization_prevents_bad_stems()
    test_normalization_handles_short_words()
    test_canonicalization_with_mapping()
    test_canonicalization_drops_explicit()
    test_canonicalization_keeps_canonical()
    test_soft_keep_unknown_predicates()
    test_type_constraint_allowed()
    test_type_constraint_violation()
    test_symmetric_normalization()
    test_non_symmetric_unchanged()
    test_loader_smoke_test()

    print()
    print("=" * 60)
    print("🎉 All ontology extraction tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        run_all_tests()
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
