#!/usr/bin/env python3
"""
Analyze Entity Type Distribution in Extraction Data

Analyzes entity type frequency, OTHER category usage, confidence by type,
and identifies missing or underused entity types to improve classification.

Usage:
    python scripts/analyze_entity_types.py \
        --db-name mongo_hack \
        --coll-name video_chunks \
        --output-dir reports \
        --min-frequency 10

Output:
    - Markdown report: reports/entity_type_distribution_YYYYMMDD_HHMMSS.md
    - JSON statistics: reports/entity_type_distribution_stats_YYYYMMDD_HHMMSS.json
"""

import sys
import os
import json
import argparse
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime, timezone
from pathlib import Path
from collections import Counter, defaultdict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dependencies.database.mongodb import MongoDBClient
from core.config.paths import COLL_CHUNKS

# Expected entity types from EntityType enum
EXPECTED_ENTITY_TYPES = {
    "PERSON",
    "ORGANIZATION",
    "TECHNOLOGY",
    "CONCEPT",
    "LOCATION",
    "EVENT",
    "OTHER",
}


class EntityTypeDistributionAnalyzer:
    """
    Analyze entity type distribution in extraction data.

    Identifies:
    - Entity type frequencies
    - OTHER category usage ratio
    - Confidence scores by entity type
    - Missing or underused entity types
    - Quality indicators and recommendations
    """

    def __init__(
        self,
        db_name: str,
        coll_name: str = COLL_CHUNKS,
    ):
        """
        Initialize analyzer.

        Args:
            db_name: Name of database to analyze
            coll_name: Collection name in database
        """
        self.db_name = db_name
        self.coll_name = coll_name
        self.expected_types = EXPECTED_ENTITY_TYPES

    def load_extraction_data(self) -> List[Dict[str, Any]]:
        """
        Load extraction data from MongoDB.

        Returns:
            List of chunks with completed extraction data
        """
        client = MongoDBClient.get_instance()

        collection = client[self.db_name][self.coll_name]

        # Query for chunks with completed extraction
        # Note: Extraction stage writes chunks as "completed" immediately after processing,
        # so this query will return all chunks that have been processed so far
        query = {
            "graphrag_extraction.status": "completed",
            "graphrag_extraction.data": {"$exists": True},
        }

        # Load data
        data = list(
            collection.find(
                query, {"chunk_id": 1, "video_id": 1, "graphrag_extraction.data": 1}
            )
        )

        return data

    def analyze_type_distribution(self, data: List[Dict[str, Any]]) -> Counter:
        """
        Analyze entity type frequency distribution.

        Args:
            data: List of chunks with extraction data

        Returns:
            Counter of entity type frequencies (normalized to uppercase)
        """
        distribution = Counter()

        for chunk in data:
            extraction = chunk.get("graphrag_extraction", {}).get("data", {})
            entities = extraction.get("entities", [])

            for entity in entities:
                entity_type = entity.get("type", "OTHER")
                # Normalize to uppercase for consistency
                entity_type = str(entity_type).upper().strip()
                if not entity_type:
                    entity_type = "OTHER"
                distribution[entity_type] += 1

        return distribution

    def calculate_other_ratio(self, distribution: Counter) -> float:
        """
        Calculate OTHER category usage ratio.

        Args:
            distribution: Counter of entity type frequencies

        Returns:
            Ratio of OTHER entities (0.0 to 1.0)
        """
        if not distribution:
            return 0.0

        total = sum(distribution.values())
        other_count = distribution.get("OTHER", 0)

        return other_count / total if total > 0 else 0.0

    def analyze_confidence_by_type(
        self, data: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, float]]:
        """
        Analyze confidence scores by entity type.

        Args:
            data: List of chunks with extraction data

        Returns:
            Dictionary mapping entity type to confidence statistics:
            {
                "type": {
                    "avg": float,
                    "min": float,
                    "max": float,
                    "count": int,
                }
            }
        """
        confidence_by_type = defaultdict(list)

        for chunk in data:
            extraction = chunk.get("graphrag_extraction", {}).get("data", {})
            entities = extraction.get("entities", [])

            for entity in entities:
                entity_type = entity.get("type", "OTHER")
                entity_type = str(entity_type).upper().strip()
                if not entity_type:
                    entity_type = "OTHER"

                # Only include entities with confidence scores
                if "confidence" in entity:
                    confidence = float(entity.get("confidence", 0.0))
                    confidence_by_type[entity_type].append(confidence)

        # Calculate statistics for each type
        stats = {}
        for entity_type, confidences in confidence_by_type.items():
            if confidences:
                stats[entity_type] = {
                    "avg": round(sum(confidences) / len(confidences), 4),
                    "min": round(min(confidences), 4),
                    "max": round(max(confidences), 4),
                    "count": len(confidences),
                }

        return stats

    def identify_missing_types(
        self, distribution: Counter, min_frequency: int = 10
    ) -> List[str]:
        """
        Identify entity types that are rarely used or missing.

        Args:
            distribution: Counter of entity type frequencies
            min_frequency: Minimum frequency threshold for considering a type "used"

        Returns:
            List of entity types that are missing or below threshold
        """
        missing = []

        for expected_type in self.expected_types:
            # Skip OTHER as it's a catch-all category
            if expected_type == "OTHER":
                continue

            frequency = distribution.get(expected_type, 0)
            if frequency < min_frequency:
                missing.append(expected_type)

        # Also check for unexpected types (not in expected_types)
        for entity_type in distribution:
            if entity_type not in self.expected_types:
                # Unexpected type found - might be a variant or error
                missing.append(f"{entity_type} (unexpected)")

        # Sort by frequency (ascending) - most missing first
        missing.sort(key=lambda t: distribution.get(t.split(" (")[0], 0))

        return missing

    def generate_report(
        self,
        distribution: Counter,
        other_ratio: float,
        confidence_by_type: Dict[str, Dict[str, float]],
        missing_types: List[str],
    ) -> str:
        """
        Generate markdown report of analysis results.

        Args:
            distribution: Counter of entity type frequencies
            other_ratio: OTHER category usage ratio
            confidence_by_type: Dictionary of confidence statistics by type
            missing_types: List of missing or underused entity types

        Returns:
            Markdown report string
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        total_entities = sum(distribution.values())
        type_diversity = len(distribution)

        report = f"""# Entity Type Distribution Analysis Report

**Generated**: {timestamp}  
**Database**: {self.db_name}  
**Collection**: {self.coll_name}

---

## Summary

- **Total Entities**: {total_entities:,} entities
- **Type Diversity**: {type_diversity} unique entity types
- **OTHER Category Ratio**: {other_ratio:.2%}
- **Missing/Underused Types**: {len(missing_types)} types

---

## Entity Type Distribution

### Type Frequency Table

| Entity Type | Count | % of Total | Avg Confidence | Status |
|-------------|-------|------------|----------------|--------|
"""

        # Sort by frequency (descending)
        sorted_types = sorted(distribution.items(), key=lambda x: x[1], reverse=True)

        for entity_type, count in sorted_types:
            percentage = (count / total_entities * 100) if total_entities > 0 else 0
            confidence_info = confidence_by_type.get(entity_type, {})
            avg_conf = (
                f"{confidence_info.get('avg', 0.0):.3f}" if confidence_info else "N/A"
            )
            count_conf = confidence_info.get("count", 0)

            # Status indicator
            if entity_type == "OTHER":
                status = "⚠️ Catch-all"
            elif entity_type in missing_types:
                status = "❌ Underused"
            elif entity_type not in self.expected_types:
                status = "⚠️ Unexpected"
            else:
                status = "✅ Active"

            report += f"| `{entity_type}` | {count:,} | {percentage:.2f}% | {avg_conf} ({count_conf}) | {status} |\n"

        report += "\n---\n\n## Confidence Analysis by Type\n\n"

        if confidence_by_type:
            report += "| Entity Type | Avg Confidence | Min | Max | Count |\n"
            report += "|-------------|----------------|-----|-----|-------|\n"

            # Sort by average confidence (descending)
            sorted_confidence = sorted(
                confidence_by_type.items(),
                key=lambda x: x[1].get("avg", 0.0),
                reverse=True,
            )

            for entity_type, stats in sorted_confidence:
                report += f"| `{entity_type}` | {stats['avg']:.3f} | {stats['min']:.3f} | {stats['max']:.3f} | {stats['count']:,} |\n"
        else:
            report += "⚠️ No confidence data available.\n"

        report += "\n---\n\n## Missing/Underused Entity Types\n\n"

        if missing_types:
            report += f"Found {len(missing_types)} entity types that are missing or underused:\n\n"
            report += "| Entity Type | Frequency | Recommendation |\n"
            report += "|-------------|-----------|----------------|\n"

            for entity_type in missing_types:
                # Extract base type if it has "(unexpected)" suffix
                base_type = entity_type.split(" (")[0]
                frequency = distribution.get(base_type, 0)

                if "(unexpected)" in entity_type:
                    recommendation = "Review: This type is not in expected list"
                elif frequency == 0:
                    recommendation = (
                        "Consider: Type not used - may need prompt adjustments"
                    )
                else:
                    recommendation = f"Consider: Type used {frequency} times - may need better classification"

                report += f"| `{entity_type}` | {frequency:,} | {recommendation} |\n"
        else:
            report += "✅ All expected entity types are being used!\n"

        report += "\n---\n\n## Recommendations\n\n"

        # Generate recommendations
        if other_ratio > 0.15:
            report += (
                f"⚠️ **OTHER category is {other_ratio:.2%}** - Consider reducing by:\n\n"
            )
            report += "1. Reviewing OTHER entities to identify patterns\n"
            report += "2. Adding new entity types if patterns emerge\n"
            report += "3. Improving entity type classification prompts\n\n"

        if missing_types:
            report += f"📝 **Found {len(missing_types)} missing/underused types** - Consider:\n\n"
            report += (
                "1. Reviewing if these types are relevant to your content domain\n"
            )
            report += (
                "2. Adjusting extraction prompts to encourage use of specific types\n"
            )
            report += "3. Adding examples of these types in the extraction prompt\n\n"

        # Confidence recommendations
        if confidence_by_type:
            low_confidence_types = [
                t
                for t, stats in confidence_by_type.items()
                if stats.get("avg", 1.0) < 0.7
            ]
            if low_confidence_types:
                report += f"⚠️ **Low confidence types** ({len(low_confidence_types)} types with avg < 0.7):\n\n"
                for entity_type in low_confidence_types[:5]:
                    avg_conf = confidence_by_type[entity_type].get("avg", 0.0)
                    report += f"- `{entity_type}`: avg confidence {avg_conf:.3f}\n"
                report += "\nConsider improving extraction quality for these types.\n\n"

        # Type diversity recommendation
        if type_diversity < len(self.expected_types) - 1:  # -1 for OTHER
            report += f"📊 **Type diversity**: Using {type_diversity}/{len(self.expected_types)-1} expected types\n"
            report += "Consider expanding entity type usage to improve knowledge graph coverage.\n\n"

        report += "---\n\n"
        report += "**Report Generated by**: Entity Type Distribution Analyzer\n"
        report += "**Version**: 1.0\n"

        return report

    def export_stats(
        self,
        distribution: Counter,
        other_ratio: float,
        confidence_by_type: Dict[str, Dict[str, float]],
        missing_types: List[str],
    ) -> Dict[str, Any]:
        """
        Export analysis statistics as JSON.

        Args:
            distribution: Counter of entity type frequencies
            other_ratio: OTHER category usage ratio
            confidence_by_type: Dictionary of confidence statistics by type
            missing_types: List of missing or underused entity types

        Returns:
            Dictionary of statistics
        """
        # Convert Counter to dict for JSON serialization
        distribution_dict = dict(distribution)

        stats = {
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
            "database": self.db_name,
            "collection": self.coll_name,
            "total_entities": sum(distribution.values()),
            "type_diversity": len(distribution),
            "expected_types_count": len(self.expected_types),
            "other_ratio": round(other_ratio, 4),
            "type_distribution": distribution_dict,
            "confidence_by_type": confidence_by_type,
            "missing_types": missing_types,
        }

        return stats


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze entity type distribution in extraction data"
    )
    parser.add_argument(
        "--db-name",
        type=str,
        required=True,
        help="Database name to analyze",
    )
    parser.add_argument(
        "--coll-name",
        type=str,
        default=COLL_CHUNKS,
        help=f"Collection name (default: {COLL_CHUNKS})",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="reports",
        help="Output directory for reports (default: reports)",
    )
    parser.add_argument(
        "--min-frequency",
        type=int,
        default=10,
        help="Minimum frequency for considering a type 'used' (default: 10)",
    )

    args = parser.parse_args()

    # Verify MongoDB URI
    mongodb_uri = os.getenv("MONGODB_URI")
    if not mongodb_uri:
        print("❌ ERROR: MONGODB_URI not found in environment variables")
        print("   Please set MONGODB_URI in .env file or environment")
        return 1

    print("=" * 80)
    print("Entity Type Distribution Analyzer")
    print("=" * 80)
    print(f"Database: {args.db_name}")
    print(f"Collection: {args.coll_name}")
    print(f"Output Directory: {args.output_dir}")
    print(f"Min Frequency: {args.min_frequency}")
    print()

    # Create analyzer
    analyzer = EntityTypeDistributionAnalyzer(
        db_name=args.db_name,
        coll_name=args.coll_name,
    )

    print(f"Expected entity types: {len(analyzer.expected_types)} types")
    print()

    # Load data
    print("Loading extraction data...")
    data = analyzer.load_extraction_data()
    print(f"  Loaded {len(data):,} chunks with completed extraction")
    print()

    if len(data) == 0:
        print("❌ No extraction data found!")
        return 1

    # Analyze type distribution
    print("Analyzing entity type distribution...")
    distribution = analyzer.analyze_type_distribution(data)
    print(f"  Found {len(distribution)} unique entity types")
    print(f"  Total entities: {sum(distribution.values()):,}")
    print()

    # Calculate OTHER ratio
    other_ratio = analyzer.calculate_other_ratio(distribution)
    print(f"OTHER Category Ratio: {other_ratio:.2%}")
    print()

    # Analyze confidence by type
    print("Analyzing confidence by entity type...")
    confidence_by_type = analyzer.analyze_confidence_by_type(data)
    print(f"  Analyzed confidence for {len(confidence_by_type)} entity types")
    print()

    # Identify missing types
    print(
        f"Identifying missing/underused types (min frequency: {args.min_frequency})..."
    )
    missing_types = analyzer.identify_missing_types(
        distribution, min_frequency=args.min_frequency
    )
    print(f"  Found {len(missing_types)} missing/underused types")
    print()

    # Generate report
    print("Generating report...")
    report = analyzer.generate_report(
        distribution, other_ratio, confidence_by_type, missing_types
    )

    # Export stats
    stats = analyzer.export_stats(
        distribution, other_ratio, confidence_by_type, missing_types
    )

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate filenames with timestamp
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    report_file = output_dir / f"entity_type_distribution_{timestamp}.md"
    stats_file = output_dir / f"entity_type_distribution_stats_{timestamp}.json"

    # Write files
    report_file.write_text(report, encoding="utf-8")
    stats_file.write_text(
        json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"✅ Report written: {report_file}")
    print(f"✅ Statistics written: {stats_file}")
    print()

    print("Analysis complete!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
