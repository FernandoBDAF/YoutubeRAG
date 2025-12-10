#!/usr/bin/env python3
"""
Compare GraphRAG Experiments

Achievement 2.3: Enhanced Experiment Comparison

Enhanced comparison tool for analyzing different GraphRAG configurations with comprehensive metrics.

Usage:
    python scripts/compare_graphrag_experiments.py mongo_hack graphrag_exp1 graphrag_exp2 [--format json|csv|markdown]
    
Output:
    Comprehensive comparison including quality, cost, performance, and coverage metrics
"""

import sys
import os
import json
import csv
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dependencies.database.mongodb import get_mongo_client
from core.config.paths import COLL_CHUNKS


def get_experiment_stats(db_name: str) -> Dict[str, Any]:
    """
    Get comprehensive stats for a GraphRAG experiment.
    
    Achievement 2.3: Enhanced Experiment Comparison
    
    Args:
        db_name: Name of the experiment database
        
    Returns:
        Dictionary with comprehensive experiment statistics including:
        - Quality metrics (modularity, graph density, average degree, clustering)
        - Cost metrics (total tokens, estimated cost)
        - Performance metrics (runtime, throughput)
        - Coverage metrics (chunks processed, entities/chunk, relationships/chunk)
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
    
    # Coverage metrics
    processed_chunks = chunks.count_documents({"graphrag_communities.status": "completed"})
    failed_chunks = chunks.count_documents({"graphrag_communities.status": "failed"})
    entities_per_chunk = total_entities / processed_chunks if processed_chunks > 0 else 0
    relationships_per_chunk = total_relationships / processed_chunks if processed_chunks > 0 else 0
    
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
    min_community_size = min(community_sizes) if community_sizes else 0
    multi_entity_pct = (multi_entity_communities / total_communities * 100) if total_communities > 0 else 0
    
    # Quality metrics - Graph density
    potential_edges = total_entities * (total_entities - 1) / 2 if total_entities > 1 else 0
    graph_density = (total_relationships / potential_edges * 100) if potential_edges > 0 else 0
    
    # Quality metrics - Average degree
    entity_degrees = {}
    outgoing_pipeline = [{"$group": {"_id": "$subject_id", "count": {"$sum": 1}}}]
    incoming_pipeline = [{"$group": {"_id": "$object_id", "count": {"$sum": 1}}}]
    
    for result in relationships.aggregate(outgoing_pipeline):
        entity_id = result["_id"]
        entity_degrees[entity_id] = entity_degrees.get(entity_id, 0) + result["count"]
    
    for result in relationships.aggregate(incoming_pipeline):
        entity_id = result["_id"]
        entity_degrees[entity_id] = entity_degrees.get(entity_id, 0) + result["count"]
    
    avg_degree = sum(entity_degrees.values()) / len(entity_degrees) if entity_degrees else 0
    max_degree = max(entity_degrees.values()) if entity_degrees else 0
    
    # Quality metrics - Modularity (from graphrag_metrics if available)
    metrics_collection = db.graphrag_metrics
    latest_metrics = metrics_collection.find_one(sort=[("timestamp", -1)])
    modularity = latest_metrics.get("quality_metrics", {}).get("modularity", 0) if latest_metrics else 0
    
    # Get experiment metadata from experiment_tracking
    tracking_coll = db.experiment_tracking
    experiment_meta = tracking_coll.find_one(sort=[("started_at", -1)])
    
    algorithm = "unknown"
    resolution = "unknown"
    started_at = None
    completed_at = None
    runtime_seconds = None
    
    if experiment_meta:
        config = experiment_meta.get("configuration", {})
        cd_config = config.get("community_detection", {})
        algorithm = cd_config.get("algorithm", "unknown")
        resolution = cd_config.get("resolution", "unknown")
        started_at = experiment_meta.get("started_at")
        completed_at = experiment_meta.get("completed_at")
        if started_at and completed_at:
            runtime_seconds = (completed_at - started_at).total_seconds()
    
    # Cost metrics (estimate from tokens if available)
    total_tokens = 0
    estimated_cost_usd = 0.0
    
    # Performance metrics
    throughput_entities_per_sec = total_entities / runtime_seconds if runtime_seconds and runtime_seconds > 0 else 0
    throughput_relationships_per_sec = total_relationships / runtime_seconds if runtime_seconds and runtime_seconds > 0 else 0
    
    return {
        "db_name": db_name,
        "experiment_id": experiment_meta.get("experiment_id", "unknown") if experiment_meta else "unknown",
        "started_at": started_at.isoformat() if started_at else None,
        "completed_at": completed_at.isoformat() if completed_at else None,
        "runtime_seconds": runtime_seconds,
        "runtime_formatted": f"{runtime_seconds / 3600:.2f}h" if runtime_seconds else "unknown",
        # Coverage
        "chunks": total_chunks,
        "processed_chunks": processed_chunks,
        "failed_chunks": failed_chunks,
        "entities": total_entities,
        "relationships": total_relationships,
        "communities": total_communities,
        "entities_per_chunk": round(entities_per_chunk, 2),
        "relationships_per_chunk": round(relationships_per_chunk, 2),
        # Quality
        "avg_community_size": round(avg_community_size, 2),
        "min_community_size": min_community_size,
        "max_community_size": max_community_size,
        "multi_entity_pct": round(multi_entity_pct, 2),
        "graph_density_pct": round(graph_density, 4),
        "avg_degree": round(avg_degree, 2),
        "max_degree": max_degree,
        "modularity": round(modularity, 4),
        # Performance
        "throughput_entities_per_sec": round(throughput_entities_per_sec, 2),
        "throughput_relationships_per_sec": round(throughput_relationships_per_sec, 2),
        # Cost
        "total_tokens": total_tokens,
        "estimated_cost_usd": round(estimated_cost_usd, 2),
        # Config
        "algorithm": algorithm,
        "resolution": resolution
    }


def print_comparison_table(experiments: List[Dict[str, Any]], format: str = "markdown"):
    """
    Print comparison table in specified format.
    
    Achievement 2.3: Enhanced Experiment Comparison
    
    Args:
        experiments: List of experiment stats dictionaries
        format: Output format ("markdown", "json", "csv")
    """
    if format == "json":
        print(json.dumps(experiments, indent=2, default=str))
        return
    
    if format == "csv":
        if not experiments:
            return
        writer = csv.DictWriter(sys.stdout, fieldnames=experiments[0].keys())
        writer.writeheader()
        writer.writerows(experiments)
        return
    
    # Markdown format
    print("\n# GraphRAG Experiment Comparison")
    print(f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n**Experiments**: {len(experiments)}")
    
    # Coverage Table
    print("\n## Coverage Metrics\n")
    print("| Metric | " + " | ".join([exp["db_name"] for exp in experiments]) + " |")
    print("|--------|" + "|".join(["--------" for _ in experiments]) + "|")
    
    coverage_metrics = [
        ("Chunks", "chunks"),
        ("Processed Chunks", "processed_chunks"),
        ("Failed Chunks", "failed_chunks"),
        ("Entities", "entities"),
        ("Relationships", "relationships"),
        ("Communities", "communities"),
        ("Entities/Chunk", "entities_per_chunk"),
        ("Relationships/Chunk", "relationships_per_chunk"),
    ]
    
    for label, key in coverage_metrics:
        values = [str(exp.get(key, "N/A")) for exp in experiments]
        print(f"| {label} | " + " | ".join(values) + " |")
    
    # Quality Table
    print("\n## Quality Metrics\n")
    print("| Metric | " + " | ".join([exp["db_name"] for exp in experiments]) + " |")
    print("|--------|" + "|".join(["--------" for _ in experiments]) + "|")
    
    quality_metrics = [
        ("Avg Community Size", "avg_community_size"),
        ("Min Community Size", "min_community_size"),
        ("Max Community Size", "max_community_size"),
        ("Multi-Entity %", "multi_entity_pct"),
        ("Graph Density %", "graph_density_pct"),
        ("Avg Degree", "avg_degree"),
        ("Max Degree", "max_degree"),
        ("Modularity", "modularity"),
    ]
    
    for label, key in quality_metrics:
        values = [str(exp.get(key, "N/A")) for exp in experiments]
        print(f"| {label} | " + " | ".join(values) + " |")
    
    # Performance Table
    print("\n## Performance Metrics\n")
    print("| Metric | " + " | ".join([exp["db_name"] for exp in experiments]) + " |")
    print("|--------|" + "|".join(["--------" for _ in experiments]) + "|")
    
    perf_metrics = [
        ("Runtime", "runtime_formatted"),
        ("Throughput (entities/sec)", "throughput_entities_per_sec"),
        ("Throughput (relationships/sec)", "throughput_relationships_per_sec"),
    ]
    
    for label, key in perf_metrics:
        values = [str(exp.get(key, "N/A")) for exp in experiments]
        print(f"| {label} | " + " | ".join(values) + " |")
    
    # Cost Table
    print("\n## Cost Metrics\n")
    print("| Metric | " + " | ".join([exp["db_name"] for exp in experiments]) + " |")
    print("|--------|" + "|".join(["--------" for _ in experiments]) + "|")
    
    cost_metrics = [
        ("Total Tokens", "total_tokens"),
        ("Estimated Cost (USD)", "estimated_cost_usd"),
    ]
    
    for label, key in cost_metrics:
        values = [str(exp.get(key, "N/A")) for exp in experiments]
        print(f"| {label} | " + " | ".join(values) + " |")
    
    # Configuration
    print("\n## Configuration\n")
    print("| Parameter | " + " | ".join([exp["db_name"] for exp in experiments]) + " |")
    print("|--------|" + "|".join(["--------" for _ in experiments]) + "|")
    
    config_metrics = [
        ("Algorithm", "algorithm"),
        ("Resolution", "resolution"),
    ]
    
    for label, key in config_metrics:
        values = [str(exp.get(key, "N/A")) for exp in experiments]
        print(f"| {label} | " + " | ".join(values) + " |")
    
    # Analysis
    print("\n## Analysis\n")
    
    # Find best by different criteria
    if experiments:
        most_communities = max(experiments, key=lambda x: x.get("communities", 0))
        largest_avg = max(experiments, key=lambda x: x.get("avg_community_size", 0))
        highest_multi = max(experiments, key=lambda x: x.get("multi_entity_pct", 0))
        highest_modularity = max(experiments, key=lambda x: x.get("modularity", 0))
        fastest = min(experiments, key=lambda x: x.get("runtime_seconds", float('inf')) if x.get("runtime_seconds") else float('inf'))
        
        print(f"- **Most communities**: {most_communities['db_name']} ({most_communities.get('communities', 0)} communities)")
        print(f"- **Largest avg size**: {largest_avg['db_name']} ({largest_avg.get('avg_community_size', 0)} entities/community)")
        print(f"- **Highest multi-entity %**: {highest_multi['db_name']} ({highest_multi.get('multi_entity_pct', 0)}%)")
        print(f"- **Highest modularity**: {highest_modularity['db_name']} ({highest_modularity.get('modularity', 0)})")
        if fastest.get("runtime_seconds"):
            print(f"- **Fastest**: {fastest['db_name']} ({fastest.get('runtime_formatted', 'unknown')})")
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

