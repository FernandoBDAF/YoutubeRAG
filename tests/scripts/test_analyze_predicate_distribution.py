"""
Tests for predicate distribution analyzer.

Tests the PredicateDistributionAnalyzer class and related functionality.
"""

import pytest
from unittest.mock import MagicMock, Mock, patch
from typing import Dict, Any, List
from collections import Counter
import sys
import os

# Add project root to path
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

# Import after path setup
from scripts.analyze_predicate_distribution import PredicateDistributionAnalyzer


class TestPredicateDistributionAnalyzer:
    """Test suite for PredicateDistributionAnalyzer."""

    def test_init(self):
        """Test analyzer initialization."""
        analyzer = PredicateDistributionAnalyzer(
            db_name="test_db",
            coll_name="video_chunks",
        )

        assert analyzer.db_name == "test_db"
        assert analyzer.coll_name == "video_chunks"
        assert analyzer.canonical_predicates is not None
        assert isinstance(analyzer.canonical_predicates, set)

    def test_load_extraction_data_empty(self):
        """Test loading from empty collection."""
        analyzer = PredicateDistributionAnalyzer(
            db_name="test_db",
            coll_name="chunks",
        )

        # Mock MongoDB collection
        mock_collection = MagicMock()
        mock_collection.find.return_value = []

        with patch(
            "scripts.analyze_predicate_distribution.MongoDBClient"
        ) as mock_client:
            mock_client.get_instance.return_value.__getitem__.return_value.__getitem__.return_value = (
                mock_collection
            )

            data = analyzer.load_extraction_data()

            assert data == []

    def test_load_extraction_data_success(self):
        """Test loading extraction data successfully."""
        analyzer = PredicateDistributionAnalyzer(
            db_name="test_db",
            coll_name="chunks",
        )

        # Mock data
        mock_chunks = [
            {
                "chunk_id": "chunk1",
                "graphrag_extraction": {
                    "status": "completed",
                    "data": {
                        "relationships": [
                            {
                                "relation": "teaches",
                                "source_entity": {"name": "John", "type": "PERSON"},
                                "target_entity": {"name": "Python", "type": "TOPIC"},
                            }
                        ]
                    },
                },
            },
            {
                "chunk_id": "chunk2",
                "graphrag_extraction": {
                    "status": "completed",
                    "data": {
                        "relationships": [
                            {
                                "relation": "uses",
                                "source_entity": {"name": "Alice", "type": "PERSON"},
                                "target_entity": {"name": "TensorFlow", "type": "TOOL"},
                            }
                        ]
                    },
                },
            },
        ]

        # Mock MongoDB collection
        mock_collection = MagicMock()
        mock_collection.find.return_value = mock_chunks

        with patch(
            "scripts.analyze_predicate_distribution.MongoDBClient"
        ) as mock_client:
            mock_client.get_instance.return_value.__getitem__.return_value.__getitem__.return_value = (
                mock_collection
            )

            data = analyzer.load_extraction_data()

            assert len(data) == 2
            assert data[0]["chunk_id"] == "chunk1"
            assert data[1]["chunk_id"] == "chunk2"

    def test_analyze_frequencies(self):
        """Test predicate frequency analysis."""
        analyzer = PredicateDistributionAnalyzer(
            db_name="test_db",
            coll_name="chunks",
        )

        # Mock data
        mock_data = [
            {
                "graphrag_extraction": {
                    "data": {
                        "relationships": [
                            {"relation": "teaches"},
                            {"relation": "teaches"},
                            {"relation": "uses"},
                            {"relation": "unknown_pred"},
                        ]
                    }
                }
            }
        ]

        frequencies = analyzer.analyze_frequencies(mock_data)

        assert frequencies["teaches"] == 2
        assert frequencies["uses"] == 1
        assert frequencies["unknown_pred"] == 1

    def test_calculate_canonical_ratio(self):
        """Test canonical ratio calculation."""
        analyzer = PredicateDistributionAnalyzer(
            db_name="test_db",
            coll_name="chunks",
        )

        # Mock canonical predicates (teaches, uses are canonical)
        analyzer.canonical_predicates = {"teaches", "uses", "works_at"}

        frequencies = Counter({"teaches": 10, "uses": 5, "unknown_pred": 3})

        ratio = analyzer.calculate_canonical_ratio(frequencies)

        assert ratio == pytest.approx(15 / 18, rel=0.01)  # 15 canonical / 18 total

    def test_calculate_canonical_ratio_all_canonical(self):
        """Test canonical ratio when all predicates are canonical."""
        analyzer = PredicateDistributionAnalyzer(
            db_name="test_db",
            coll_name="chunks",
        )

        analyzer.canonical_predicates = {"teaches", "uses"}

        frequencies = Counter({"teaches": 10, "uses": 5})

        ratio = analyzer.calculate_canonical_ratio(frequencies)

        assert ratio == 1.0  # 100% canonical

    def test_calculate_canonical_ratio_empty(self):
        """Test canonical ratio with empty frequencies."""
        analyzer = PredicateDistributionAnalyzer(
            db_name="test_db",
            coll_name="chunks",
        )

        frequencies = Counter()

        ratio = analyzer.calculate_canonical_ratio(frequencies)

        assert ratio == 0.0

    def test_identify_non_canonical_predicates(self):
        """Test identification of non-canonical predicates."""
        analyzer = PredicateDistributionAnalyzer(
            db_name="test_db",
            coll_name="chunks",
        )

        analyzer.canonical_predicates = {"teaches", "uses"}

        frequencies = Counter(
            {
                "teaches": 10,  # canonical
                "uses": 5,  # canonical
                "unknown_pred": 8,  # non-canonical, high frequency
                "rare_pred": 1,  # non-canonical, low frequency
            }
        )

        # Test with minimum frequency threshold of 5
        non_canonical = analyzer.identify_non_canonical_predicates(
            frequencies, min_frequency=5
        )

        assert "unknown_pred" in non_canonical
        assert "rare_pred" not in non_canonical  # Below threshold
        assert "teaches" not in non_canonical  # Canonical
        assert "uses" not in non_canonical  # Canonical

    def test_suggest_canonical_predicates(self):
        """Test suggestion of new canonical predicates."""
        analyzer = PredicateDistributionAnalyzer(
            db_name="test_db",
            coll_name="chunks",
        )

        analyzer.canonical_predicates = {"teaches", "uses"}

        frequencies = Counter(
            {
                "teaches": 10,  # canonical
                "unknown_pred": 15,  # high frequency, non-canonical
                "rare_pred": 2,  # low frequency, non-canonical
            }
        )

        # Test with minimum frequency threshold of 10
        suggestions = analyzer.suggest_canonical_predicates(
            frequencies, min_frequency=10
        )

        assert "unknown_pred" in suggestions
        assert "rare_pred" not in suggestions  # Below threshold
        assert "teaches" not in suggestions  # Already canonical

    def test_suggest_mappings(self):
        """Test suggestion of mappings for non-canonical predicates."""
        analyzer = PredicateDistributionAnalyzer(
            db_name="test_db",
            coll_name="chunks",
        )

        analyzer.canonical_predicates = {"teaches", "uses", "teach"}
        analyzer.predicate_map = {"teach": "teaches"}

        non_canonical = ["teach", "teach_to"]

        # Mock similarity function or use actual jellyfish
        suggestions = analyzer.suggest_mappings(non_canonical, min_similarity=0.7)

        # Should suggest mappings based on similarity
        assert isinstance(suggestions, dict)
        # "teach" should map to "teaches" (high similarity)
        # "teach_to" might map to "teaches" or be suggested as new canonical

    def test_generate_report(self):
        """Test report generation."""
        analyzer = PredicateDistributionAnalyzer(
            db_name="test_db",
            coll_name="chunks",
        )

        frequencies = Counter({"teaches": 10, "uses": 5, "unknown_pred": 3})
        canonical_ratio = 0.833  # 15/18
        non_canonical = ["unknown_pred"]
        suggestions = {
            "unknown_pred": {"frequency": 3, "suggested_canonical": "unknown_pred"}
        }

        report = analyzer.generate_report(
            frequencies, canonical_ratio, non_canonical, suggestions
        )

        assert isinstance(report, str)
        assert "Predicate Distribution Analysis" in report
        assert "teaches" in report or "10" in report
        assert "canonical" in report.lower() or "83.3" in report

    def test_export_stats(self):
        """Test JSON statistics export."""
        analyzer = PredicateDistributionAnalyzer(
            db_name="test_db",
            coll_name="chunks",
        )

        frequencies = Counter({"teaches": 10, "uses": 5})
        canonical_ratio = 1.0
        non_canonical = []
        suggestions = {}

        stats = analyzer.export_stats(
            frequencies, canonical_ratio, non_canonical, suggestions
        )

        assert isinstance(stats, dict)
        assert "total_predicates" in stats
        assert "canonical_ratio" in stats
        assert "frequencies" in stats
        assert stats["canonical_ratio"] == 1.0

    def test_end_to_end_analysis(self):
        """Integration test for full analysis flow."""
        analyzer = PredicateDistributionAnalyzer(
            db_name="test_db",
            coll_name="chunks",
        )

        # Mock data
        mock_data = [
            {
                "chunk_id": "chunk1",
                "graphrag_extraction": {
                    "status": "completed",
                    "data": {
                        "relationships": [
                            {"relation": "teaches"},
                            {"relation": "teaches"},
                            {"relation": "unknown_pred"},
                        ]
                    },
                },
            }
        ]

        # Mock MongoDB
        mock_collection = MagicMock()
        mock_collection.find.return_value = mock_data

        with patch(
            "scripts.analyze_predicate_distribution.MongoDBClient"
        ) as mock_client:
            mock_client.get_instance.return_value.__getitem__.return_value.__getitem__.return_value = (
                mock_collection
            )

            # Run full analysis
            data = analyzer.load_extraction_data()
            frequencies = analyzer.analyze_frequencies(data)
            ratio = analyzer.calculate_canonical_ratio(frequencies)

            assert len(data) == 1
            assert frequencies["teaches"] == 2
            assert frequencies["unknown_pred"] == 1
            assert isinstance(ratio, float)
