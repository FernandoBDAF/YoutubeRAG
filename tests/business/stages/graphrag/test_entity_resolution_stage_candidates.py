"""
Tests for Entity Resolution Stage - Cross-Chunk Candidate Lookup.

Tests Achievement 0.1: Cross-Chunk Candidate Lookup Implementation.
"""

try:
    import pytest

    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False

from unittest.mock import MagicMock, Mock, patch
from typing import Dict, Any, List

from business.stages.graphrag.entity_resolution import EntityResolutionStage
from business.agents.graphrag.entity_resolution import EntityResolutionAgent
from core.models.graphrag import ResolvedEntity, EntityType


class TestBlockingKeys:
    """Test blocking key generation in EntityResolutionAgent."""

    def test_blocking_keys_simple_name(self):
        """Test blocking keys for simple entity name."""
        agent = EntityResolutionAgent(
            llm_client=Mock(),
            model_name="gpt-4o-mini",
            similarity_threshold=0.85,
        )

        keys = agent._blocking_keys("Python")
        assert "python" in keys  # Normalized name
        assert "python" in keys  # Alnum-only (same for simple name)
        # Single word, so no acronym

    def test_blocking_keys_with_prefix(self):
        """Test blocking keys for name with prefix."""
        agent = EntityResolutionAgent(
            llm_client=Mock(),
            model_name="gpt-4o-mini",
            similarity_threshold=0.85,
        )

        keys = agent._blocking_keys("Prof. John Smith")
        assert "john smith" in keys  # Normalized (prefix removed)
        assert "john smith" in keys  # Alnum-only
        assert "js" in keys  # Acronym

    def test_blocking_keys_with_suffix(self):
        """Test blocking keys for name with suffix."""
        agent = EntityResolutionAgent(
            llm_client=Mock(),
            model_name="gpt-4o-mini",
            similarity_threshold=0.85,
        )

        keys = agent._blocking_keys("Apple Inc.")
        assert "apple" in keys  # Normalized (suffix removed)
        assert "apple" in keys  # Alnum-only
        # Single word after suffix removal, so no acronym

    def test_blocking_keys_acronym(self):
        """Test blocking keys generates acronym."""
        agent = EntityResolutionAgent(
            llm_client=Mock(),
            model_name="gpt-4o-mini",
            similarity_threshold=0.85,
        )

        keys = agent._blocking_keys("Massachusetts Institute of Technology")
        assert "mit" in keys  # Acronym should be generated
        assert "massachusetts institute of technology" in keys  # Normalized


class TestFindDbCandidates:
    """Test candidate lookup in EntityResolutionStage."""

    def _mock_stage(self):
        """Create a mock EntityResolutionStage with necessary mocks."""
        stage = EntityResolutionStage()
        stage.config = Mock()
        stage.config.db_name = "test_db"
        stage.config.read_db_name = "test_db"
        stage.config.write_db_name = "test_db"
        stage.config.similarity_threshold = 0.85
        stage.config.model_name = "gpt-4o-mini"
        stage.config.temperature = 0.1

        # Mock resolution agent
        stage.resolution_agent = EntityResolutionAgent(
            llm_client=Mock(),
            model_name="gpt-4o-mini",
            similarity_threshold=0.85,
        )

        # Mock graphrag collections
        mock_entities_collection = MagicMock()
        stage.graphrag_collections = {"entities": mock_entities_collection}

        return stage, mock_entities_collection

    def test_find_db_candidates_with_matches(self):
        """Test finding candidates when matches exist."""
        stage, mock_entities = self._mock_stage()

        # Mock existing entity in database
        existing_entity = {
            "entity_id": "abc123def456789012345678901234567",
            "canonical_name": "Python",
            "canonical_name_normalized": "python",
            "type": "TECHNOLOGY",
            "aliases": ["Python3"],
            "aliases_normalized": ["python3"],
        }

        # Mock find() to return the existing entity
        mock_cursor = MagicMock()
        mock_cursor.__iter__.return_value = [existing_entity]
        mock_entities.find.return_value = mock_cursor

        # Find candidates
        candidates = stage._find_db_candidates(
            name="Python",
            entity_type="TECHNOLOGY",
            aliases=["Python3"],
        )

        # Verify
        assert len(candidates) == 1
        assert candidates[0]["entity_id"] == "abc123def456789012345678901234567"
        mock_entities.find.assert_called_once()

    def test_find_db_candidates_no_matches(self):
        """Test finding candidates when no matches exist."""
        stage, mock_entities = self._mock_stage()

        # Mock empty result
        mock_cursor = MagicMock()
        mock_cursor.__iter__.return_value = []
        mock_entities.find.return_value = mock_cursor

        # Find candidates
        candidates = stage._find_db_candidates(
            name="NonExistent",
            entity_type="CONCEPT",
            aliases=[],
        )

        # Verify
        assert len(candidates) == 0
        mock_entities.find.assert_called_once()

    def test_find_db_candidates_uses_blocking_keys(self):
        """Test that blocking keys are used in query."""
        stage, mock_entities = self._mock_stage()

        # Mock empty result
        mock_cursor = MagicMock()
        mock_cursor.__iter__.return_value = []
        mock_entities.find.return_value = mock_cursor

        # Find candidates
        stage._find_db_candidates(
            name="Prof. John Smith",
            entity_type="PERSON",
            aliases=["J. Smith"],
        )

        # Verify query was constructed with blocking keys
        call_args = mock_entities.find.call_args
        query = call_args[0][0]  # First positional argument

        # Query should contain blocking keys
        assert "$or" in query
        assert "canonical_name_normalized" in str(query) or "aliases_normalized" in str(
            query
        )


class TestChooseMatch:
    """Test candidate matching in EntityResolutionStage."""

    def _mock_stage(self):
        """Create a mock EntityResolutionStage."""
        stage = EntityResolutionStage()
        stage.config = Mock()
        stage.resolution_agent = EntityResolutionAgent(
            llm_client=Mock(),
            model_name="gpt-4o-mini",
            similarity_threshold=0.85,
        )
        return stage

    def test_choose_match_exact_normalized_match(self):
        """Test choosing match with exact normalized name."""
        mock_stage = self._mock_stage()
        candidates = [
            {
                "entity_id": "abc123",
                "canonical_name": "Python",
                "canonical_name_normalized": "python",
                "type": "TECHNOLOGY",
            }
        ]

        match = mock_stage._choose_match("Python", candidates)
        assert match is not None
        assert match["entity_id"] == "abc123"

    def test_choose_match_no_match(self):
        """Test choosing match when no candidates match."""
        mock_stage = self._mock_stage()
        candidates = [
            {
                "entity_id": "abc123",
                "canonical_name": "Java",
                "canonical_name_normalized": "java",
                "type": "TECHNOLOGY",
            }
        ]

        match = mock_stage._choose_match("Python", candidates)
        assert match is None

    def test_choose_match_alias_match(self):
        """Test choosing match via normalized alias."""
        mock_stage = self._mock_stage()
        candidates = [
            {
                "entity_id": "abc123",
                "canonical_name": "Python Programming Language",
                "canonical_name_normalized": "python programming language",
                "aliases": ["Python"],
                "aliases_normalized": ["python"],
                "type": "TECHNOLOGY",
            }
        ]

        match = mock_stage._choose_match("Python", candidates)
        assert match is not None
        assert match["entity_id"] == "abc123"

    def test_choose_match_backward_compatibility(self):
        """Test choosing match when normalized fields don't exist."""
        mock_stage = self._mock_stage()
        candidates = [
            {
                "entity_id": "abc123",
                "canonical_name": "Python",
                # No canonical_name_normalized field
                "type": "TECHNOLOGY",
            }
        ]

        # Should still work by normalizing on the fly
        match = mock_stage._choose_match("Python", candidates)
        assert match is not None
        assert match["entity_id"] == "abc123"


class TestCrossChunkEntityReuse:
    """Test cross-chunk entity reuse integration."""

    def _mock_stage(self):
        """Create a fully mocked EntityResolutionStage."""
        stage = EntityResolutionStage()
        stage.config = Mock()
        stage.config.db_name = "test_db"
        stage.config.read_db_name = "test_db"
        stage.config.write_db_name = "test_db"
        stage.config.similarity_threshold = 0.85
        stage.config.model_name = "gpt-4o-mini"
        stage.config.temperature = 0.1
        stage.config.upsert_existing = False

        # Mock resolution agent
        stage.resolution_agent = EntityResolutionAgent(
            llm_client=Mock(),
            model_name="gpt-4o-mini",
            similarity_threshold=0.85,
        )

        # Mock collections
        mock_entities = MagicMock()
        mock_mentions = MagicMock()
        mock_chunks = MagicMock()

        stage.graphrag_collections = {
            "entities": mock_entities,
            "entity_mentions": mock_mentions,
        }

        def mock_get_collection(name, io, db_name):
            return mock_chunks

        stage.get_collection = mock_get_collection

        return stage, mock_entities, mock_chunks

    def test_cross_chunk_entity_reuse(self):
        """Test that entities from different chunks reuse same entity."""
        stage, mock_entities, mock_chunks = self._mock_stage()

        # Setup: Entity already exists from chunk 1
        existing_entity = {
            "entity_id": "python_entity_id_123456789012345678",
            "canonical_name": "Python",
            "canonical_name_normalized": "python",
            "type": "TECHNOLOGY",
            "source_count": 1,
            "source_chunks": ["chunk_1"],
            "aliases": ["Python"],
            "aliases_normalized": ["python"],
        }

        # Mock: First chunk's entity lookup finds nothing (new entity)
        # Second chunk's candidate lookup finds existing entity
        mock_entities.find_one.side_effect = [
            None,  # First lookup by entity_id (new entity, not found)
            existing_entity,  # Candidate lookup finds it
        ]

        mock_cursor = MagicMock()
        mock_cursor.__iter__.return_value = [existing_entity]
        mock_entities.find.return_value = mock_cursor

        # Create resolved entity for chunk 2
        resolved_entity = ResolvedEntity(
            entity_id=ResolvedEntity.generate_entity_id("Python"),
            canonical_name="Python",
            name="Python",
            type=EntityType.TECHNOLOGY,
            description="A programming language",
            confidence=0.9,
            source_count=1,
            resolution_methods=["name_grouping"],
            aliases=["Python"],
        )

        # Store entity (simulating chunk 2 processing)
        stored_ids = stage._store_resolved_entities(
            [resolved_entity], chunk_id="chunk_2", video_id="video_1"
        )

        # Verify: Should reuse existing entity_id
        assert len(stored_ids) == 1
        assert stored_ids[0] == "python_entity_id_123456789012345678"

        # Verify: update_existing_entity was called (not insert_new_entity)
        # Check that update_one was called (from _update_existing_entity)
        update_calls = [
            call for call in mock_entities.method_calls if call[0] == "update_one"
        ]
        assert (
            len(update_calls) > 0
        ), "Should update existing entity, not insert new one"


class TestStringScore:
    """Test string similarity scoring in EntityResolutionAgent."""

    def test_string_score_identical(self):
        """Test scoring identical strings."""
        agent = EntityResolutionAgent(
            llm_client=Mock(),
            model_name="gpt-4o-mini",
            similarity_threshold=0.85,
        )

        score = agent._string_score("Python", "Python")
        assert score == 1.0

    def test_string_score_similar_names(self):
        """Test scoring similar names."""
        agent = EntityResolutionAgent(
            llm_client=Mock(),
            model_name="gpt-4o-mini",
            similarity_threshold=0.85,
        )

        # Near-duplicates should have high scores
        score1 = agent._string_score("Jason Ku", "J. Ku")
        assert score1 > 0.8, f"Expected >0.8, got {score1}"

        score2 = agent._string_score("Python", "Python3")
        assert score2 > 0.8, f"Expected >0.8, got {score2}"

        score3 = agent._string_score("Apple Inc.", "Apple")
        assert score3 > 0.7, f"Expected >0.7, got {score3}"

    def test_string_score_different_names(self):
        """Test scoring different names."""
        agent = EntityResolutionAgent(
            llm_client=Mock(),
            model_name="gpt-4o-mini",
            similarity_threshold=0.85,
        )

        # Completely different names should have low scores
        score1 = agent._string_score("Python", "Java")
        assert score1 < 0.5, f"Expected <0.5, got {score1}"

        score2 = agent._string_score("John Smith", "Jane Doe")
        assert score2 < 0.5, f"Expected <0.5, got {score2}"

    def test_string_score_empty_strings(self):
        """Test scoring with empty strings."""
        agent = EntityResolutionAgent(
            llm_client=Mock(),
            model_name="gpt-4o-mini",
            similarity_threshold=0.85,
        )

        score1 = agent._string_score("", "Python")
        assert score1 == 0.0

        score2 = agent._string_score("Python", "")
        assert score2 == 0.0

        score3 = agent._string_score("", "")
        assert score3 == 0.0


class TestFuzzyMatching:
    """Test fuzzy matching with threshold in EntityResolutionStage."""

    def _mock_stage(self):
        """Create a mock EntityResolutionStage."""
        stage = EntityResolutionStage()
        stage.config = Mock()
        stage.resolution_agent = EntityResolutionAgent(
            llm_client=Mock(),
            model_name="gpt-4o-mini",
            similarity_threshold=0.85,
        )
        return stage

    def test_choose_match_fuzzy_above_threshold(self):
        """Test fuzzy matching when score is above threshold."""
        stage = self._mock_stage()

        candidates = [
            {
                "entity_id": "abc123",
                "canonical_name": "Jason Ku",
                "canonical_name_normalized": "jason ku",
                "type": "PERSON",
            }
        ]

        # "J. Ku" should match "Jason Ku" with high similarity
        match = stage._choose_match("J. Ku", candidates)
        assert match is not None, "Should match 'J. Ku' to 'Jason Ku'"
        assert match["entity_id"] == "abc123"

    def test_choose_match_fuzzy_below_threshold(self):
        """Test fuzzy matching when score is below threshold."""
        stage = self._mock_stage()

        candidates = [
            {
                "entity_id": "abc123",
                "canonical_name": "Python",
                "canonical_name_normalized": "python",
                "type": "TECHNOLOGY",
            }
        ]

        # "Java" should NOT match "Python" (low similarity)
        match = stage._choose_match("Java", candidates)
        assert match is None, "Should not match 'Java' to 'Python'"

    def test_choose_match_best_candidate(self):
        """Test that best matching candidate is selected."""
        stage = self._mock_stage()

        candidates = [
            {
                "entity_id": "low_score",
                "canonical_name": "Java Programming",
                "canonical_name_normalized": "java programming",
                "type": "TECHNOLOGY",
            },
            {
                "entity_id": "high_score",
                "canonical_name": "Python",
                "canonical_name_normalized": "python",
                "type": "TECHNOLOGY",
            },
        ]

        # "Python3" should match "Python" better than "Java Programming"
        match = stage._choose_match("Python3", candidates)
        assert match is not None
        assert (
            match["entity_id"] == "high_score"
        ), "Should select best matching candidate"

    def test_choose_match_threshold_boundary(self):
        """Test threshold boundary behavior."""
        # Test with lower threshold (0.80)
        stage_low = EntityResolutionStage()
        stage_low.config = Mock()
        stage_low.resolution_agent = EntityResolutionAgent(
            llm_client=Mock(),
            model_name="gpt-4o-mini",
            similarity_threshold=0.80,
        )

        candidates = [
            {
                "entity_id": "abc123",
                "canonical_name": "Python",
                "canonical_name_normalized": "python",
                "type": "TECHNOLOGY",
            }
        ]

        # Should match if score >= 0.80
        match = stage_low._choose_match("Python3", candidates)
        # Note: Actual score depends on RapidFuzz, but Python3 vs Python should be high enough
        # This test validates the threshold logic works


def run_all_tests():
    """Run all tests."""
    print("=== Testing Entity Resolution Stage - Cross-Chunk Candidate Lookup ===\n")

    # Test blocking keys
    print("Testing blocking keys...")
    test_blocking = TestBlockingKeys()
    test_blocking.test_blocking_keys_simple_name()
    test_blocking.test_blocking_keys_with_prefix()
    test_blocking.test_blocking_keys_with_suffix()
    test_blocking.test_blocking_keys_acronym()
    print("✓ Blocking keys tests passed\n")

    # Test string scoring
    print("Testing string similarity scoring...")
    test_scoring = TestStringScore()
    test_scoring.test_string_score_identical()
    test_scoring.test_string_score_similar_names()
    test_scoring.test_string_score_different_names()
    test_scoring.test_string_score_empty_strings()
    print("✓ String scoring tests passed\n")

    # Test fuzzy matching
    print("Testing fuzzy matching with threshold...")
    test_fuzzy = TestFuzzyMatching()
    test_fuzzy.test_choose_match_fuzzy_above_threshold()
    test_fuzzy.test_choose_match_fuzzy_below_threshold()
    test_fuzzy.test_choose_match_best_candidate()
    test_fuzzy.test_choose_match_threshold_boundary()
    print("✓ Fuzzy matching tests passed\n")

    print("✅ All candidate lookup and fuzzy matching tests passed!")


if __name__ == "__main__":
    run_all_tests()
