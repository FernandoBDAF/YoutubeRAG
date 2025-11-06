"""
Tests for entity type distribution analyzer.

Tests the EntityTypeDistributionAnalyzer class and related functionality.
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
from scripts.analyze_entity_types import EntityTypeDistributionAnalyzer


class TestEntityTypeDistributionAnalyzer:
    """Test suite for EntityTypeDistributionAnalyzer."""

    def test_init(self):
        """Test analyzer initialization."""
        analyzer = EntityTypeDistributionAnalyzer(
            db_name="test_db",
            coll_name="video_chunks",
        )

        assert analyzer.db_name == "test_db"
        assert analyzer.coll_name == "video_chunks"
        assert analyzer.expected_types is not None
        assert isinstance(analyzer.expected_types, set)

    def test_load_extraction_data_empty(self):
        """Test loading from empty collection."""
        analyzer = EntityTypeDistributionAnalyzer(
            db_name="test_db",
            coll_name="chunks",
        )

        # Mock MongoDB collection
        mock_collection = MagicMock()
        mock_collection.find.return_value = []

        with patch(
            "scripts.analyze_entity_types.MongoDBClient"
        ) as mock_client:
            mock_client.get_instance.return_value.__getitem__.return_value.__getitem__.return_value = (
                mock_collection
            )

            data = analyzer.load_extraction_data()

            assert data == []

    def test_load_extraction_data_success(self):
        """Test loading extraction data successfully."""
        analyzer = EntityTypeDistributionAnalyzer(
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
                        "entities": [
                            {
                                "name": "John",
                                "type": "PERSON",
                                "confidence": 0.9,
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
                        "entities": [
                            {
                                "name": "Python",
                                "type": "TECHNOLOGY",
                                "confidence": 0.85,
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
            "scripts.analyze_entity_types.MongoDBClient"
        ) as mock_client:
            mock_client.get_instance.return_value.__getitem__.return_value.__getitem__.return_value = (
                mock_collection
            )

            data = analyzer.load_extraction_data()

            assert len(data) == 2
            assert data[0]["chunk_id"] == "chunk1"
            assert data[1]["chunk_id"] == "chunk2"

    def test_analyze_type_distribution(self):
        """Test entity type frequency distribution."""
        analyzer = EntityTypeDistributionAnalyzer(
            db_name="test_db",
            coll_name="chunks",
        )

        # Mock data
        mock_data = [
            {
                "graphrag_extraction": {
                    "data": {
                        "entities": [
                            {"type": "PERSON", "name": "John"},
                            {"type": "PERSON", "name": "Alice"},
                            {"type": "TECHNOLOGY", "name": "Python"},
                            {"type": "OTHER", "name": "Unknown"},
                        ]
                    }
                }
            }
        ]

        distribution = analyzer.analyze_type_distribution(mock_data)

        assert distribution["PERSON"] == 2
        assert distribution["TECHNOLOGY"] == 1
        assert distribution["OTHER"] == 1

    def test_calculate_other_ratio(self):
        """Test OTHER category ratio calculation."""
        analyzer = EntityTypeDistributionAnalyzer(
            db_name="test_db",
            coll_name="chunks",
        )

        distribution = Counter({"PERSON": 10, "TECHNOLOGY": 5, "OTHER": 3})

        ratio = analyzer.calculate_other_ratio(distribution)

        assert ratio == pytest.approx(3 / 18, rel=0.01)  # 3 OTHER / 18 total

    def test_calculate_other_ratio_all_other(self):
        """Test OTHER ratio when all entities are OTHER."""
        analyzer = EntityTypeDistributionAnalyzer(
            db_name="test_db",
            coll_name="chunks",
        )

        distribution = Counter({"OTHER": 10})

        ratio = analyzer.calculate_other_ratio(distribution)

        assert ratio == 1.0  # 100% OTHER

    def test_calculate_other_ratio_no_other(self):
        """Test OTHER ratio when no entities are OTHER."""
        analyzer = EntityTypeDistributionAnalyzer(
            db_name="test_db",
            coll_name="chunks",
        )

        distribution = Counter({"PERSON": 10, "TECHNOLOGY": 5})

        ratio = analyzer.calculate_other_ratio(distribution)

        assert ratio == 0.0

    def test_calculate_other_ratio_empty(self):
        """Test OTHER ratio with empty distribution."""
        analyzer = EntityTypeDistributionAnalyzer(
            db_name="test_db",
            coll_name="chunks",
        )

        distribution = Counter()

        ratio = analyzer.calculate_other_ratio(distribution)

        assert ratio == 0.0

    def test_analyze_confidence_by_type(self):
        """Test confidence analysis by entity type."""
        analyzer = EntityTypeDistributionAnalyzer(
            db_name="test_db",
            coll_name="chunks",
        )

        # Mock data with confidence scores
        mock_data = [
            {
                "graphrag_extraction": {
                    "data": {
                        "entities": [
                            {"type": "PERSON", "name": "John", "confidence": 0.9},
                            {"type": "PERSON", "name": "Alice", "confidence": 0.85},
                            {"type": "TECHNOLOGY", "name": "Python", "confidence": 0.8},
                            {"type": "OTHER", "name": "Unknown", "confidence": 0.5},
                        ]
                    }
                }
            }
        ]

        confidence_by_type = analyzer.analyze_confidence_by_type(mock_data)

        assert "PERSON" in confidence_by_type
        assert "TECHNOLOGY" in confidence_by_type
        assert "OTHER" in confidence_by_type
        assert confidence_by_type["PERSON"]["avg"] == pytest.approx(0.875, rel=0.01)
        assert confidence_by_type["TECHNOLOGY"]["avg"] == pytest.approx(0.8, rel=0.01)

    def test_analyze_confidence_by_type_missing_confidence(self):
        """Test confidence analysis with missing confidence scores."""
        analyzer = EntityTypeDistributionAnalyzer(
            db_name="test_db",
            coll_name="chunks",
        )

        # Mock data with some missing confidence
        mock_data = [
            {
                "graphrag_extraction": {
                    "data": {
                        "entities": [
                            {"type": "PERSON", "name": "John", "confidence": 0.9},
                            {"type": "PERSON", "name": "Alice"},  # Missing confidence
                        ]
                    }
                }
            }
        ]

        confidence_by_type = analyzer.analyze_confidence_by_type(mock_data)

        # Should only count entities with confidence scores
        assert "PERSON" in confidence_by_type
        assert confidence_by_type["PERSON"]["count"] == 1
        assert confidence_by_type["PERSON"]["avg"] == pytest.approx(0.9, rel=0.01)

    def test_identify_missing_types(self):
        """Test identification of rarely used entity types."""
        analyzer = EntityTypeDistributionAnalyzer(
            db_name="test_db",
            coll_name="chunks",
        )

        # Expected types: PERSON, ORGANIZATION, TECHNOLOGY, CONCEPT, LOCATION, EVENT, OTHER
        analyzer.expected_types = {
            "PERSON",
            "ORGANIZATION",
            "TECHNOLOGY",
            "CONCEPT",
            "LOCATION",
            "EVENT",
            "OTHER",
        }

        distribution = Counter(
            {
                "PERSON": 100,  # Frequently used
                "TECHNOLOGY": 50,  # Frequently used
                "ORGANIZATION": 5,  # Rarely used (below threshold)
                "CONCEPT": 3,  # Rarely used
                "LOCATION": 0,  # Not used
                "EVENT": 0,  # Not used
                "OTHER": 20,  # Used
            }
        )

        # Test with minimum frequency threshold of 10
        missing = analyzer.identify_missing_types(distribution, min_frequency=10)

        assert "LOCATION" in missing  # Not used at all
        assert "EVENT" in missing  # Not used at all
        assert "ORGANIZATION" in missing  # Below threshold
        assert "CONCEPT" in missing  # Below threshold
        assert "PERSON" not in missing  # Above threshold
        assert "TECHNOLOGY" not in missing  # Above threshold
        assert "OTHER" not in missing  # Above threshold (even though it's a catch-all)

    def test_generate_report(self):
        """Test report generation."""
        analyzer = EntityTypeDistributionAnalyzer(
            db_name="test_db",
            coll_name="chunks",
        )

        distribution = Counter({"PERSON": 10, "TECHNOLOGY": 5, "OTHER": 3})
        other_ratio = 0.167  # 3/18
        confidence_by_type = {
            "PERSON": {"avg": 0.9, "count": 10, "min": 0.8, "max": 1.0},
            "TECHNOLOGY": {"avg": 0.85, "count": 5, "min": 0.7, "max": 0.9},
        }
        missing_types = ["LOCATION", "EVENT"]

        report = analyzer.generate_report(
            distribution, other_ratio, confidence_by_type, missing_types
        )

        assert isinstance(report, str)
        assert "Entity Type Distribution Analysis" in report
        assert "PERSON" in report or "10" in report
        assert "OTHER" in report.lower() or "16.7" in report
        assert "confidence" in report.lower()

    def test_export_stats(self):
        """Test JSON statistics export."""
        analyzer = EntityTypeDistributionAnalyzer(
            db_name="test_db",
            coll_name="chunks",
        )

        distribution = Counter({"PERSON": 10, "TECHNOLOGY": 5})
        other_ratio = 0.0
        confidence_by_type = {"PERSON": {"avg": 0.9, "count": 10}}
        missing_types = []

        stats = analyzer.export_stats(
            distribution, other_ratio, confidence_by_type, missing_types
        )

        assert isinstance(stats, dict)
        assert "total_entities" in stats
        assert "other_ratio" in stats
        assert "type_distribution" in stats
        assert "confidence_by_type" in stats
        assert stats["other_ratio"] == 0.0

    def test_end_to_end_analysis(self):
        """Integration test for full analysis flow."""
        analyzer = EntityTypeDistributionAnalyzer(
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
                        "entities": [
                            {"type": "PERSON", "name": "John", "confidence": 0.9},
                            {"type": "TECHNOLOGY", "name": "Python", "confidence": 0.8},
                        ]
                    },
                },
            }
        ]

        # Mock MongoDB
        mock_collection = MagicMock()
        mock_collection.find.return_value = mock_data

        with patch(
            "scripts.analyze_entity_types.MongoDBClient"
        ) as mock_client:
            mock_client.get_instance.return_value.__getitem__.return_value.__getitem__.return_value = (
                mock_collection
            )

            # Run full analysis
            data = analyzer.load_extraction_data()
            distribution = analyzer.analyze_type_distribution(data)
            other_ratio = analyzer.calculate_other_ratio(distribution)

            assert len(data) == 1
            assert distribution["PERSON"] == 1
            assert distribution["TECHNOLOGY"] == 1
            assert isinstance(other_ratio, float)

    def test_edge_cases_missing_fields(self):
        """Test handling of missing type or confidence fields."""
        analyzer = EntityTypeDistributionAnalyzer(
            db_name="test_db",
            coll_name="chunks",
        )

        # Mock data with missing fields
        mock_data = [
            {
                "graphrag_extraction": {
                    "data": {
                        "entities": [
                            {"name": "John"},  # Missing type
                            {"type": "PERSON", "name": "Alice"},  # Missing confidence
                            {"type": "TECHNOLOGY", "name": "Python", "confidence": 0.8},
                        ]
                    }
                }
            }
        ]

        distribution = analyzer.analyze_type_distribution(mock_data)
        confidence_by_type = analyzer.analyze_confidence_by_type(mock_data)

        # Should handle missing fields gracefully
        assert "PERSON" in distribution or "OTHER" in distribution  # Missing type might default to OTHER
        assert "TECHNOLOGY" in distribution
        assert isinstance(confidence_by_type, dict)

