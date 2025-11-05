#!/usr/bin/env python3
"""
Compare GraphRAG Experiments

Quick comparison tool for analyzing different GraphRAG configurations.

Usage:
    python scripts/compare_graphrag_experiments.py mongo_hack graphrag_exp1 graphrag_exp2
    
Output:
    Markdown table comparing entity counts, community metrics, and performance
"""

import sys
import os
from typing import List, Dict, Any
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dependencies.database.mongodb import get_mongo_client
from core.config.paths import COLL_CHUNKS


def get_experiment_stats(db_name: str) -> Dict[str, Any]:
    """
    Get comprehensive stats for a GraphRAG experiment.
    
    Args:
        db_name: Name of the experiment database
        
    Returns:
        Dictionary with experiment statistics
    """
    client = get_mongo_client()
    db = client[db_name]
    
    # Collections
    chunks = db[COLL_CHUNKS]
    entities = db.entities
    relationships = db.relationships
    communities = db.communities
    
    # Basic counts
    total_chunks = chunks.count_documents({})
    total_entities = entities.count_documents({})
    total_relationships = relationships.count_documents({})
    total_communities = communities.count_documents({})
    
    # Community stats
    community_sizes = []
    multi_entity_communities = 0
    
    for comm in communities.find({}, {"entity_count": 1}):
        size = comm.get("entity_count", 0)
        community_sizes.append(size)
        if size > 1:
            multi_entity_communities += 1
    
    avg_community_size = sum(community_sizes) / len(community_sizes) if community_sizes else 0
    max_community_size = max(community_sizes) if community_sizes else 0
    multi_entity_pct = (multi_entity_communities / total_communities * 100) if total_communities > 0 else 0
    
    # Get algorithm and resolution from a sample chunk
    sample_chunk = chunks.find_one({"graphrag_communities.status": "completed"})
    algorithm = "unknown"
    resolution = "unknown"
    
    if sample_chunk:
        detection_data = sample_chunk.get("graphrag_communities", {})
        model_used = detection_data.get("model_used", "unknown")
        # Try to extract from logs or metadata (simplified for now)
        algorithm = "louvain"  # Default assumption
    
    # Graph density (relationships per entity pair)
    potential_edges = total_entities * (total_entities - 1) / 2 if total_entities > 1 else 0
    graph_density = (total_relationships / potential_edges * 100) if potential_edges > 0 else 0
    
    return {
        "db_name": db_name,
        "chunks": total_chunks,
        "entities": total_entities,
        "relationships": total_relationships,
        "communities": total_communities,
        "avg_community_size": round(avg_community_size, 2),
        "max_community_size": max_community_size,
        "multi_entity_pct": round(multi_entity_pct, 2),
        "graph_density_pct": round(graph_density, 4),
        "algorithm": algorithm,
        "resolution": resolution
    }


def print_comparison_table(experiments: List[Dict[str, Any]]):
    """
    Print comparison table in markdown format.
    
    Args:
        experiments: List of experiment stats dictionaries
    """
    print("\n# GraphRAG Experiment Comparison")
    print(f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n**Experiments**: {len(experiments)}")
    
    # Table header
    print("\n## Summary Table\n")
    print("| Metric | " + " | ".join([exp["db_name"] for exp in experiments]) + " |")
    print("|--------|" + "|".join(["--------" for _ in experiments]) + "|")
    
    # Metrics rows
    metrics = [
        ("Chunks", "chunks"),
        ("Entities", "entities"),
        ("Relationships", "relationships"),
        ("Communities", "communities"),
        ("Avg Community Size", "avg_community_size"),
        ("Max Community Size", "max_community_size"),
        ("Multi-Entity %", "multi_entity_pct"),
        ("Graph Density %", "graph_density_pct"),
    ]
    
    for label, key in metrics:
        values = [str(exp[key]) for exp in experiments]
        print(f"| {label} | " + " | ".join(values) + " |")
    
    # Detailed stats
    print("\n## Detailed Statistics\n")
    for exp in experiments:
        print(f"### {exp['db_name']}\n")
        print(f"- **Total Chunks**: {exp['chunks']:,}")
        print(f"- **Total Entities**: {exp['entities']:,}")
        print(f"- **Total Relationships**: {exp['relationships']:,}")
        print(f"- **Total Communities**: {exp['communities']:,}")
        print(f"- **Average Community Size**: {exp['avg_community_size']}")
        print(f"- **Largest Community**: {exp['max_community_size']} entities")
        print(f"- **Multi-Entity Communities**: {exp['multi_entity_pct']}%")
        print(f"- **Graph Density**: {exp['graph_density_pct']}%")
        print()
    
    # Recommendations
    print("\n## Analysis\n")
    
    # Find best by different criteria
    most_communities = max(experiments, key=lambda x: x["communities"])
    largest_avg = max(experiments, key=lambda x: x["avg_community_size"])
    highest_multi = max(experiments, key=lambda x: x["multi_entity_pct"])
    
    print(f"- **Most communities**: {most_communities['db_name']} ({most_communities['communities']} communities)")
    print(f"- **Largest avg size**: {largest_avg['db_name']} ({largest_avg['avg_community_size']} entities/community)")
    print(f"- **Highest multi-entity %**: {highest_multi['db_name']} ({highest_multi['multi_entity_pct']}%)")
    print()


def main():
    """Main comparison function."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/compare_graphrag_experiments.py DB1 DB2 [DB3 ...]")
        print("\nExample:")
        print("  python scripts/compare_graphrag_experiments.py \\")
        print("    mongo_hack \\")
        print("    graphrag_exp_louvain_res08 \\")
        print("    graphrag_exp_louvain_res15")
        sys.exit(1)
    
    db_names = sys.argv[1:]
    
    print(f"Comparing {len(db_names)} GraphRAG experiments...")
    print(f"Databases: {', '.join(db_names)}")
    
    # Collect stats from all experiments
    experiments = []
    for db_name in db_names:
        try:
            print(f"  Analyzing {db_name}...")
            stats = get_experiment_stats(db_name)
            experiments.append(stats)
        except Exception as e:
            print(f"  ⚠️  Error analyzing {db_name}: {e}")
            continue
    
    if not experiments:
        print("❌ No valid experiments found")
        sys.exit(1)
    
    # Print comparison
    print_comparison_table(experiments)
    
    print("\n✅ Comparison complete!")


if __name__ == "__main__":
    main()

