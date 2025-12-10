"""
Tests for extraction quality comparison tools.

Tests the ExtractionQualityComparator class and related functionality.
"""

import pytest
from unittest.mock import MagicMock, Mock, patch
from typing import Dict, Any, List
import sys
import os

# Add project root to path
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

# Import after path setup
from app.scripts.analysis.quality.compare_extraction_quality import ExtractionQualityComparator


class TestExtractionQualityComparator:
    """Test suite for ExtractionQualityComparator."""

    def test_init(self):
        """Test comparator initialization."""
        comparator = ExtractionQualityComparator(
            old_db="validation_db",
            new_db="mongo_hack",
            old_coll="video_chunks",
            new_coll="video_chunks",
        )

        assert comparator.old_db == "validation_db"
        assert comparator.new_db == "mongo_hack"
        assert comparator.old_coll == "video_chunks"
        assert comparator.new_coll == "video_chunks"

    def test_load_extraction_data_empty_databases(self):
        """Test loading from empty databases."""
        comparator = ExtractionQualityComparator(
            old_db="test_db_old",
            new_db="test_db_new",
            old_coll="chunks",
            new_coll="chunks",
        )

        # Mock MongoDB collections
        with patch(
            "app.scripts.analysis.quality.compare_extraction_quality.get_mongo_client"
        ) as mock_client:
            mock_db_old = MagicMock()
            mock_db_new = MagicMock()
            mock_client.return_value = {
                "test_db_old": mock_db_old,
                "test_db_new": mock_db_new,
            }

            mock_coll_old = MagicMock()
            mock_coll_new = MagicMock()
            mock_db_old.__getitem__.return_value = mock_coll_old
            mock_db_new.__getitem__.return_value = mock_coll_new

            mock_coll_old.find.return_value = []  # Empty
            mock_coll_new.find.return_value = []  # Empty

            old_data, new_data = comparator.load_extraction_data()

            assert len(old_data) == 0
            assert len(new_data) == 0

    def test_load_extraction_data_with_mock_chunks(self):
        """Test loading extraction data with mock chunks."""
        comparator = ExtractionQualityComparator(
            old_db="test_db_old",
            new_db="test_db_new",
            old_coll="chunks",
            new_coll="chunks",
        )

        # Mock chunks with extraction data
        mock_old_chunks = [
            {
                "chunk_id": "chunk_1",
                "video_id": "video_1",
                "graphrag_extraction": {
                    "status": "completed",
                    "data": {
                        "entities": [
                            {"name": "Python", "type": "TECHNOLOGY", "confidence": 0.9}
                        ],
                        "relationships": [
                            {
                                "source_entity": {"name": "Python"},
                                "target_entity": {"name": "Django"},
                                "relation": "uses",
                                "confidence": 0.8,
                            }
                        ],
                    },
                },
            }
        ]

        mock_new_chunks = [
            {
                "chunk_id": "chunk_1",
                "video_id": "video_1",
                "graphrag_extraction": {
                    "status": "completed",
                    "data": {
                        "entities": [
                            {"name": "Python", "type": "TECHNOLOGY", "confidence": 0.95}
                        ],
                        "relationships": [
                            {
                                "source_entity": {"name": "Python"},
                                "target_entity": {"name": "Django"},
                                "relation": "uses",  # Canonical predicate
                                "confidence": 0.9,
                            }
                        ],
                    },
                },
            }
        ]

        with patch(
            "app.scripts.analysis.quality.compare_extraction_quality.get_mongo_client"
        ) as mock_client:
            mock_db_old = MagicMock()
            mock_db_new = MagicMock()
            mock_client.return_value.__getitem__.side_effect = lambda key: {
                "test_db_old": mock_db_old,
                "test_db_new": mock_db_new,
            }[key]

            mock_coll_old = MagicMock()
            mock_coll_new = MagicMock()
            mock_db_old.__getitem__.return_value = mock_coll_old
            mock_db_new.__getitem__.return_value = mock_coll_new

            mock_coll_old.find.return_value = mock_old_chunks
            mock_coll_new.find.return_value = mock_new_chunks

            old_data, new_data = comparator.load_extraction_data()

            assert len(old_data) == 1
            assert len(new_data) == 1
            assert old_data[0]["chunk_id"] == "chunk_1"
            assert new_data[0]["chunk_id"] == "chunk_1"

    def test_calculate_predicate_quality_canonical_ratio(self):
        """Test predicate quality calculation - canonical ratio."""
        comparator = ExtractionQualityComparator(
            old_db="test_old", new_db="test_new", old_coll="chunks", new_coll="chunks"
        )

        # Mock data: old has non-canonical, new has canonical
        old_data = [
            {
                "graphrag_extraction": {
                    "data": {
                        "relationships": [
                            {"relation": "uses"},
                            {"relation": "works_with"},  # Non-canonical
                        ]
                    }
                }
            }
        ]

        new_data = [
            {
                "graphrag_extraction": {
                    "data": {
                        "relationships": [
                            {"relation": "uses"},  # Canonical
                            {
                                "relation": "uses"
                            },  # Canonical (mapped from "works_with")
                        ]
                    }
                }
            }
        ]

        # Mock canonical predicates
        with patch.object(
            comparator,
            "_load_canonical_predicates",
            return_value={"uses", "depends_on"},
        ):
            metrics = comparator.calculate_predicate_quality(old_data, new_data)

            assert "canonical_ratio_old" in metrics
            assert "canonical_ratio_new" in metrics
            assert metrics["canonical_ratio_old"] < metrics["canonical_ratio_new"]

    def test_calculate_entity_quality_type_distribution(self):
        """Test entity quality calculation - type distribution."""
        comparator = ExtractionQualityComparator(
            old_db="test_old", new_db="test_new", old_coll="chunks", new_coll="chunks"
        )

        old_data = [
            {
                "graphrag_extraction": {
                    "data": {
                        "entities": [
                            {"type": "OTHER", "confidence": 0.7},
                            {"type": "TECHNOLOGY", "confidence": 0.8},
                        ]
                    }
                }
            }
        ]

        new_data = [
            {
                "graphrag_extraction": {
                    "data": {
                        "entities": [
                            {"type": "TECHNOLOGY", "confidence": 0.9},
                            {"type": "TECHNOLOGY", "confidence": 0.95},
                        ]
                    }
                }
            }
        ]

        metrics = comparator.calculate_entity_quality(old_data, new_data)

        assert "other_ratio_old" in metrics
        assert "other_ratio_new" in metrics
        assert metrics["other_ratio_old"] > metrics["other_ratio_new"]
        assert "avg_confidence_old" in metrics
        assert "avg_confidence_new" in metrics

    def test_calculate_relationship_quality_constraint_validation(self):
        """Test relationship quality - constraint validation."""
        comparator = ExtractionQualityComparator(
            old_db="test_old", new_db="test_new", old_coll="chunks", new_coll="chunks"
        )

        # Mock type constraints
        with patch.object(
            comparator,
            "_load_type_constraints",
            return_value={"uses": [("TECHNOLOGY", "TECHNOLOGY")]},
        ):
            old_data = [
                {
                    "graphrag_extraction": {
                        "data": {
                            "relationships": [
                                {
                                    "relation": "uses",
                                    "source_entity": {"type": "PERSON"},
                                    "target_entity": {"type": "TECHNOLOGY"},
                                }
                            ]
                        }
                    }
                }
            ]

            new_data = [
                {
                    "graphrag_extraction": {
                        "data": {
                            "relationships": [
                                {
                                    "relation": "uses",
                                    "source_entity": {"type": "TECHNOLOGY"},
                                    "target_entity": {"type": "TECHNOLOGY"},
                                }
                            ]
                        }
                    }
                }
            ]

            metrics = comparator.calculate_relationship_quality(old_data, new_data)

            assert "constraint_violation_rate_old" in metrics
            assert "constraint_violation_rate_new" in metrics
            assert (
                metrics["constraint_violation_rate_old"]
                > metrics["constraint_violation_rate_new"]
            )

    def test_calculate_coverage_metrics(self):
        """Test coverage metrics calculation."""
        comparator = ExtractionQualityComparator(
            old_db="test_old", new_db="test_new", old_coll="chunks", new_coll="chunks"
        )

        old_data = [
            {
                "graphrag_extraction": {
                    "data": {
                        "entities": [{"type": "TECHNOLOGY"}],
                        "relationships": [{"relation": "uses"}],
                    }
                }
            }
        ]

        new_data = [
            {
                "graphrag_extraction": {
                    "data": {
                        "entities": [
                            {"type": "TECHNOLOGY"},
                            {"type": "CONCEPT"},
                            {"type": "PERSON"},
                        ],
                        "relationships": [
                            {"relation": "uses"},
                            {"relation": "teaches"},
                            {"relation": "depends_on"},
                        ],
                    }
                }
            }
        ]

        with patch.object(
            comparator,
            "_load_canonical_predicates",
            return_value={"uses", "teaches", "depends_on"},
        ):
            metrics = comparator.calculate_coverage_metrics(old_data, new_data)

            assert "predicate_coverage_old" in metrics
            assert "predicate_coverage_new" in metrics
            assert metrics["predicate_coverage_new"] > metrics["predicate_coverage_old"]
            assert "entity_type_coverage_old" in metrics
            assert "entity_type_coverage_new" in metrics

    def test_generate_report_creates_markdown(self):
        """Test report generation creates valid markdown."""
        comparator = ExtractionQualityComparator(
            old_db="test_old", new_db="test_new", old_coll="chunks", new_coll="chunks"
        )

        # Mock metrics
        metrics = {
            "canonical_ratio_old": 0.70,
            "canonical_ratio_new": 0.85,
            "other_ratio_old": 0.15,
            "other_ratio_new": 0.05,
        }

        report = comparator.generate_report(metrics)

        assert isinstance(report, str)
        assert "# Extraction Quality Comparison" in report
        assert "## Summary" in report
        assert "## Recommendations" in report
        assert "0.70" in report or "70%" in report
        assert "0.85" in report or "85%" in report

    def test_export_metrics_creates_valid_json(self):
        """Test metrics export creates valid JSON."""
        comparator = ExtractionQualityComparator(
            old_db="test_old", new_db="test_new", old_coll="chunks", new_coll="chunks"
        )

        metrics = {
            "canonical_ratio_old": 0.70,
            "canonical_ratio_new": 0.85,
        }

        import json

        json_str = comparator.export_metrics(metrics)

        # Should be valid JSON
        parsed = json.loads(json_str)
        assert parsed["canonical_ratio_old"] == 0.70
        assert parsed["canonical_ratio_new"] == 0.85

    def test_handles_missing_fields_gracefully(self):
        """Test handling of missing fields in old data."""
        comparator = ExtractionQualityComparator(
            old_db="test_old", new_db="test_new", old_coll="chunks", new_coll="chunks"
        )

        # Old data missing some fields
        old_data = [
            {
                "graphrag_extraction": {
                    "data": {
                        "entities": [{"name": "Python"}],  # Missing type, confidence
                        "relationships": [],  # Missing relationships
                    }
                }
            }
        ]

        new_data = [
            {
                "graphrag_extraction": {
                    "data": {
                        "entities": [
                            {"name": "Python", "type": "TECHNOLOGY", "confidence": 0.9}
                        ],
                        "relationships": [{"relation": "uses", "confidence": 0.8}],
                    }
                }
            }
        ]

        # Should not raise exceptions
        entity_metrics = comparator.calculate_entity_quality(old_data, new_data)
        relationship_metrics = comparator.calculate_relationship_quality(
            old_data, new_data
        )

        assert isinstance(entity_metrics, dict)
        assert isinstance(relationship_metrics, dict)
