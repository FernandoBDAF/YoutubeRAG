#!/usr/bin/env python3
"""
Analyze Predicate Distribution in Extraction Data

Analyzes predicate frequency, canonical vs non-canonical ratios, and suggests
new canonical predicates and mappings to improve ontology coverage.

Usage:
    python scripts/analyze_predicate_distribution.py \
        --db-name mongo_hack \
        --coll-name video_chunks \
        --output-dir reports \
        --min-frequency 5

Output:
    - Markdown report: reports/predicate_distribution_YYYYMMDD_HHMMSS.md
    - JSON statistics: reports/predicate_distribution_stats_YYYYMMDD_HHMMSS.json
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
from core.libraries.ontology.loader import load_ontology

try:
    import jellyfish
except ImportError:
    jellyfish = None
    print(
        "Warning: jellyfish not installed. Similarity-based mapping suggestions will be disabled."
    )


class PredicateDistributionAnalyzer:
    """
    Analyze predicate distribution in extraction data.

    Identifies:
    - Predicate frequencies
    - Canonical vs non-canonical ratios
    - High-frequency non-canonical predicates (gaps)
    - Suggested new canonical predicates
    - Suggested mappings for non-canonical predicates
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

        # Load ontology for canonical predicates and mappings
        ontology_data = load_ontology()
        self.canonical_predicates: Set[str] = ontology_data.get(
            "canonical_predicates", set()
        )
        self.predicate_map: Dict[str, str] = ontology_data.get("predicate_map", {})
        self.type_constraints: Dict[str, List[List[str]]] = ontology_data.get(
            "predicate_type_constraints", {}
        )

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

    def analyze_frequencies(self, data: List[Dict[str, Any]]) -> Counter:
        """
        Analyze predicate frequencies.

        Args:
            data: List of chunks with extraction data

        Returns:
            Counter of predicate frequencies (normalized to lowercase)
        """
        frequencies = Counter()

        for chunk in data:
            extraction = chunk.get("graphrag_extraction", {}).get("data", {})
            relationships = extraction.get("relationships", [])

            for rel in relationships:
                pred = rel.get("relation", "").lower().strip()
                if pred:
                    frequencies[pred] += 1

        return frequencies

    def calculate_canonical_ratio(self, frequencies: Counter) -> float:
        """
        Calculate canonical predicate ratio.

        Args:
            frequencies: Counter of predicate frequencies

        Returns:
            Ratio of canonical predicates (0.0 to 1.0)
        """
        if not frequencies:
            return 0.0

        total = sum(frequencies.values())
        canonical_count = sum(
            count
            for pred, count in frequencies.items()
            if pred in self.canonical_predicates
        )

        return canonical_count / total if total > 0 else 0.0

    def identify_non_canonical_predicates(
        self, frequencies: Counter, min_frequency: int = 5
    ) -> List[str]:
        """
        Identify high-frequency non-canonical predicates.

        Args:
            frequencies: Counter of predicate frequencies
            min_frequency: Minimum frequency threshold for inclusion

        Returns:
            List of non-canonical predicates meeting frequency threshold
        """
        non_canonical = []

        for pred, count in frequencies.items():
            if pred not in self.canonical_predicates and count >= min_frequency:
                non_canonical.append(pred)

        # Sort by frequency (descending)
        non_canonical.sort(key=lambda p: frequencies[p], reverse=True)

        return non_canonical

    def suggest_canonical_predicates(
        self, frequencies: Counter, min_frequency: int = 10
    ) -> List[str]:
        """
        Suggest new canonical predicates based on frequency.

        Args:
            frequencies: Counter of predicate frequencies
            min_frequency: Minimum frequency threshold for suggestion

        Returns:
            List of suggested canonical predicates (sorted by frequency)
        """
        suggestions = []

        for pred, count in frequencies.items():
            if pred not in self.canonical_predicates and count >= min_frequency:
                suggestions.append(pred)

        # Sort by frequency (descending)
        suggestions.sort(key=lambda p: frequencies[p], reverse=True)

        return suggestions

    def suggest_mappings(
        self, non_canonical: List[str], min_similarity: float = 0.7
    ) -> Dict[str, Dict[str, Any]]:
        """
        Suggest mappings for non-canonical predicates to canonical ones.

        Uses Jaro-Winkler similarity to find best matches.

        Args:
            non_canonical: List of non-canonical predicates
            min_similarity: Minimum similarity threshold for suggestions

        Returns:
            Dictionary mapping non-canonical predicate to suggestion dict:
            {
                "suggested_canonical": str,
                "similarity": float,
                "frequency": int,
            }
        """
        if not jellyfish:
            # Return empty suggestions if jellyfish not available
            return {}

        suggestions = {}

        for pred in non_canonical:
            best_match = None
            best_similarity = 0.0

            # Check against all canonical predicates
            for canonical in self.canonical_predicates:
                similarity = jellyfish.jaro_winkler_similarity(pred, canonical)
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = canonical

            # Also check if there's already a mapping
            if pred in self.predicate_map:
                mapped = self.predicate_map[pred]
                if mapped in self.canonical_predicates:
                    # Use existing mapping if it's better
                    existing_similarity = jellyfish.jaro_winkler_similarity(
                        pred, mapped
                    )
                    if existing_similarity > best_similarity:
                        best_match = mapped
                        best_similarity = existing_similarity

            if best_match and best_similarity >= min_similarity:
                suggestions[pred] = {
                    "suggested_canonical": best_match,
                    "similarity": round(best_similarity, 3),
                    "frequency": 0,  # Will be set by caller if needed
                }
            else:
                # No good match found - suggest as new canonical
                suggestions[pred] = {
                    "suggested_canonical": pred,  # Suggest itself as new canonical
                    "similarity": 0.0,
                    "frequency": 0,  # Will be set by caller if needed
                }

        return suggestions

    def generate_report(
        self,
        frequencies: Counter,
        canonical_ratio: float,
        non_canonical: List[str],
        suggestions: Dict[str, Dict[str, Any]],
    ) -> str:
        """
        Generate markdown report of analysis results.

        Args:
            frequencies: Counter of predicate frequencies
            canonical_ratio: Canonical predicate ratio
            non_canonical: List of high-frequency non-canonical predicates
            suggestions: Dictionary of mapping suggestions

        Returns:
            Markdown report string
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        report = f"""# Predicate Distribution Analysis Report

**Generated**: {timestamp}  
**Database**: {self.db_name}  
**Collection**: {self.coll_name}

---

## Summary

- **Total Predicates**: {len(frequencies)} unique predicates
- **Total Occurrences**: {sum(frequencies.values()):,} total predicate occurrences
- **Canonical Ratio**: {canonical_ratio:.2%}
- **Non-Canonical Predicates**: {len(non_canonical)} high-frequency non-canonical predicates

---

## Predicate Frequency Distribution

### Top 20 Most Frequent Predicates

| Predicate | Frequency | Canonical | % of Total |
|-----------|-----------|-----------|------------|
"""

        # Top 20 predicates
        top_predicates = frequencies.most_common(20)
        total_occurrences = sum(frequencies.values())

        for pred, count in top_predicates:
            is_canonical = "✅" if pred in self.canonical_predicates else "❌"
            percentage = (
                (count / total_occurrences * 100) if total_occurrences > 0 else 0
            )
            report += f"| `{pred}` | {count:,} | {is_canonical} | {percentage:.2f}% |\n"

        report += "\n---\n\n## Non-Canonical Predicates (Ontology Gaps)\n\n"
        report += (
            f"Found {len(non_canonical)} high-frequency non-canonical predicates:\n\n"
        )

        if non_canonical:
            report += "| Predicate | Frequency | Suggestion |\n"
            report += "|-----------|-----------|------------|\n"

            for pred in non_canonical[:20]:  # Top 20 non-canonical
                count = frequencies[pred]
                suggestion_info = suggestions.get(pred, {})
                suggested_canonical = suggestion_info.get("suggested_canonical", pred)
                similarity = suggestion_info.get("similarity", 0.0)

                if similarity > 0.7:
                    suggestion = (
                        f"Map to `{suggested_canonical}` (similarity: {similarity:.2f})"
                    )
                else:
                    suggestion = f"Add as new canonical: `{suggested_canonical}`"

                report += f"| `{pred}` | {count:,} | {suggestion} |\n"
        else:
            report += "✅ No high-frequency non-canonical predicates found!\n"

        report += "\n---\n\n## Recommendations\n\n"

        # Generate recommendations
        if canonical_ratio < 0.8:
            report += f"⚠️ **Canonical ratio is {canonical_ratio:.2%}** - Consider adding more canonical predicates.\n\n"

        if non_canonical:
            report += f"📝 **Found {len(non_canonical)} high-frequency non-canonical predicates** - Consider:\n\n"
            report += "1. Adding suggested predicates to canonical list\n"
            report += "2. Adding suggested mappings to predicate_map.yml\n"
            report += "3. Reviewing predicates with similarity >0.7 for mapping opportunities\n\n"

        # Top suggestions
        if suggestions:
            report += "### Top 5 Suggested Actions\n\n"
            sorted_suggestions = sorted(
                suggestions.items(),
                key=lambda x: frequencies.get(x[0], 0),
                reverse=True,
            )[:5]

            for i, (pred, info) in enumerate(sorted_suggestions, 1):
                count = frequencies.get(pred, 0)
                suggested = info.get("suggested_canonical", pred)
                similarity = info.get("similarity", 0.0)

                if similarity > 0.7:
                    report += f"{i}. Map `{pred}` (frequency: {count:,}) → `{suggested}` (similarity: {similarity:.2f})\n"
                else:
                    report += f"{i}. Add `{pred}` (frequency: {count:,}) as new canonical predicate\n"

        report += "\n---\n\n"
        report += "**Report Generated by**: Predicate Distribution Analyzer\n"
        report += "**Version**: 1.0\n"

        return report

    def export_stats(
        self,
        frequencies: Counter,
        canonical_ratio: float,
        non_canonical: List[str],
        suggestions: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Export analysis statistics as JSON.

        Args:
            frequencies: Counter of predicate frequencies
            canonical_ratio: Canonical predicate ratio
            non_canonical: List of high-frequency non-canonical predicates
            suggestions: Dictionary of mapping suggestions

        Returns:
            Dictionary of statistics
        """
        # Convert Counter to dict for JSON serialization
        frequencies_dict = dict(frequencies)

        # Add frequency to suggestions
        suggestions_with_freq = {}
        for pred, info in suggestions.items():
            suggestions_with_freq[pred] = {
                **info,
                "frequency": frequencies.get(pred, 0),
            }

        stats = {
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
            "database": self.db_name,
            "collection": self.coll_name,
            "total_unique_predicates": len(frequencies),
            "total_predicate_occurrences": sum(frequencies.values()),
            "canonical_ratio": round(canonical_ratio, 4),
            "canonical_predicates_count": len(self.canonical_predicates),
            "non_canonical_count": len(non_canonical),
            "frequencies": frequencies_dict,
            "non_canonical_predicates": non_canonical,
            "suggestions": suggestions_with_freq,
        }

        return stats


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze predicate distribution in extraction data"
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
        default=5,
        help="Minimum frequency for non-canonical predicate identification (default: 5)",
    )
    parser.add_argument(
        "--min-similarity",
        type=float,
        default=0.7,
        help="Minimum similarity for mapping suggestions (default: 0.7)",
    )

    args = parser.parse_args()

    # Verify MongoDB URI
    mongodb_uri = os.getenv("MONGODB_URI")
    if not mongodb_uri:
        print("❌ ERROR: MONGODB_URI not found in environment variables")
        print("   Please set MONGODB_URI in .env file or environment")
        return 1

    print("=" * 80)
    print("Predicate Distribution Analyzer")
    print("=" * 80)
    print(f"Database: {args.db_name}")
    print(f"Collection: {args.coll_name}")
    print(f"Output Directory: {args.output_dir}")
    print(f"Min Frequency: {args.min_frequency}")
    print(f"Min Similarity: {args.min_similarity}")
    print()

    # Create analyzer
    analyzer = PredicateDistributionAnalyzer(
        db_name=args.db_name,
        coll_name=args.coll_name,
    )

    print(f"Loaded {len(analyzer.canonical_predicates)} canonical predicates")
    print()

    # Load data
    print("Loading extraction data...")
    data = analyzer.load_extraction_data()
    print(f"  Loaded {len(data):,} chunks with completed extraction")
    print()

    if len(data) == 0:
        print("❌ No extraction data found!")
        return 1

    # Analyze frequencies
    print("Analyzing predicate frequencies...")
    frequencies = analyzer.analyze_frequencies(data)
    print(f"  Found {len(frequencies)} unique predicates")
    print()

    # Calculate canonical ratio
    canonical_ratio = analyzer.calculate_canonical_ratio(frequencies)
    print(f"Canonical Ratio: {canonical_ratio:.2%}")
    print()

    # Identify non-canonical predicates
    print(
        f"Identifying non-canonical predicates (min frequency: {args.min_frequency})..."
    )
    non_canonical = analyzer.identify_non_canonical_predicates(
        frequencies, min_frequency=args.min_frequency
    )
    print(f"  Found {len(non_canonical)} high-frequency non-canonical predicates")
    print()

    # Generate suggestions
    print("Generating suggestions...")
    suggestions = analyzer.suggest_mappings(
        non_canonical, min_similarity=args.min_similarity
    )
    print(f"  Generated {len(suggestions)} suggestions")
    print()

    # Generate report
    print("Generating report...")
    report = analyzer.generate_report(
        frequencies, canonical_ratio, non_canonical, suggestions
    )

    # Export stats
    stats = analyzer.export_stats(
        frequencies, canonical_ratio, non_canonical, suggestions
    )

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate filenames with timestamp
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    report_file = output_dir / f"predicate_distribution_{timestamp}.md"
    stats_file = output_dir / f"predicate_distribution_stats_{timestamp}.json"

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
