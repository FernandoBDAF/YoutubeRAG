#!/usr/bin/env python3
"""
Analyze GraphRAG Graph Structure

This script analyzes the graph structure to understand connectivity patterns,
identify issues, and suggest improvements.
"""

import os
import sys
from collections import defaultdict, Counter
from dotenv import load_dotenv
import networkx as nx

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dependencies.database.mongodb import get_mongo_client
from core.config.paths import DB_NAME

load_dotenv()


def analyze_graph_structure():
    """Analyze the GraphRAG knowledge graph structure."""
    client = get_mongo_client()
    db = client[DB_NAME]

    print("=" * 80)
    print("GraphRAG Graph Structure Analysis")
    print("=" * 80)
    print()

    # Build NetworkX graph
    print("1. BUILDING GRAPH")
    print("-" * 80)

    G = nx.Graph()
    entity_data = {}
    relationship_data = []

    # Add entities as nodes
    for entity in db.entities.find():
        entity_id = entity.get("entity_id")
        entity_data[entity_id] = {
            "name": entity.get("name", "Unknown"),
            "type": entity.get("type", "OTHER"),
            "description": entity.get("description", "")[:100],
            "source_count": entity.get("source_count", 0),
            "confidence": entity.get("confidence", 0.0),
        }
        G.add_node(entity_id, **entity_data[entity_id])

    # Add relationships as edges
    for rel in db.relations.find():
        subject_id = rel.get("subject_id")
        object_id = rel.get("object_id")
        predicate = rel.get("predicate", "related_to")

        if G.has_node(subject_id) and G.has_node(object_id):
            G.add_edge(
                subject_id,
                object_id,
                predicate=predicate,
                confidence=rel.get("confidence", 0.0),
                description=rel.get("description", "")[:100],
            )
            relationship_data.append(
                {
                    "subject": subject_id,
                    "object": object_id,
                    "predicate": predicate,
                }
            )

    print(f"  Nodes (entities): {G.number_of_nodes():,}")
    print(f"  Edges (relationships): {G.number_of_edges():,}")
    print(f"  Graph density: {nx.density(G):.6f}")
    print()

    # 2. Connectivity Analysis
    print("2. CONNECTIVITY ANALYSIS")
    print("-" * 80)

    # Node degrees
    degrees = dict(G.degree())
    degree_distribution = Counter(degrees.values())
    isolated_nodes = [n for n, d in degrees.items() if d == 0]
    single_edge_nodes = [n for n, d in degrees.items() if d == 1]
    highly_connected_nodes = [n for n, d in degrees.items() if d >= 5]

    print(f"  Isolated nodes (degree=0): {len(isolated_nodes):,}")
    print(f"  Leaf nodes (degree=1): {len(single_edge_nodes):,}")
    print(f"  Highly connected (degree≥5): {len(highly_connected_nodes):,}")
    print()
    print(f"  Degree distribution:")
    for degree, count in sorted(degree_distribution.items())[:10]:
        print(f"    degree={degree}: {count} nodes")
    if len(degree_distribution) > 10:
        print(f"    ... (showing top 10)")
    print()

    # Connected components
    components = list(nx.connected_components(G))
    component_sizes = [len(c) for c in components]
    size_distribution = Counter(component_sizes)

    print(f"  Connected components: {len(components):,}")
    print(f"  Largest component size: {max(component_sizes) if component_sizes else 0}")
    print(f"  Component size distribution:")
    for size, count in sorted(size_distribution.items(), reverse=True)[:10]:
        print(f"    {size} node(s): {count} components")
    if len(size_distribution) > 10:
        print(f"    ... (showing top 10)")
    print()

    # 3. Relationship Type Analysis
    print("3. RELATIONSHIP TYPE ANALYSIS")
    print("-" * 80)

    predicate_counts = Counter(r["predicate"] for r in relationship_data)
    print(f"  Unique relationship types: {len(predicate_counts):,}")
    print(f"  Most common relationship types:")
    for predicate, count in predicate_counts.most_common(15):
        print(f"    '{predicate}': {count}")
    if len(predicate_counts) > 15:
        print(f"    ... (showing top 15)")
    print()

    # 4. Entity Type Analysis
    print("4. ENTITY TYPE ANALYSIS")
    print("-" * 80)

    entity_types = Counter(e.get("type", "UNKNOWN") for e in entity_data.values())
    print(f"  Entity type distribution:")
    for etype, count in sorted(entity_types.items(), key=lambda x: -x[1]):
        print(f"    {etype}: {count} entities")
    print()

    # Analyze connectivity by entity type
    print("  Connectivity by entity type:")
    type_connectivity = defaultdict(list)
    for entity_id, data in entity_data.items():
        degree = degrees.get(entity_id, 0)
        type_connectivity[data["type"]].append(degree)

    for etype in sorted(entity_types.keys()):
        conn_list = type_connectivity[etype]
        if conn_list:
            avg_degree = sum(conn_list) / len(conn_list)
            isolated_count = sum(1 for d in conn_list if d == 0)
            print(f"    {etype}:")
            print(f"      Avg degree: {avg_degree:.2f}")
            print(
                f"      Isolated: {isolated_count}/{len(conn_list)} ({isolated_count/len(conn_list)*100:.1f}%)"
            )
    print()

    # 5. Hub Analysis (Highly Connected Nodes)
    print("5. HUB ANALYSIS (Most Connected Entities)")
    print("-" * 80)

    if highly_connected_nodes:
        top_nodes = sorted(degrees.items(), key=lambda x: -x[1])[:10]
        print(f"  Top 10 most connected entities:")
        for i, (entity_id, degree) in enumerate(top_nodes, 1):
            entity_info = entity_data[entity_id]
            print(
                f"    {i}. {entity_info['name']} ({entity_info['type']}): {degree} connections"
            )
    else:
        print("  No highly connected entities (degree ≥ 5)")
    print()

    # 6. Path Analysis
    print("6. PATH ANALYSIS")
    print("-" * 80)

    # Calculate average shortest path for largest component
    largest_component = max(components, key=len) if components else set()
    if len(largest_component) > 1:
        subgraph = G.subgraph(largest_component)
        if nx.is_connected(subgraph):
            avg_path_length = nx.average_shortest_path_length(subgraph)
            diameter = nx.diameter(subgraph)
            print(f"  Largest component (size={len(largest_component)}):")
            print(f"    Average path length: {avg_path_length:.2f}")
            print(f"    Diameter: {diameter}")
        else:
            print(
                f"  Largest component (size={len(largest_component)}) is not connected"
            )
    else:
        print("  No large connected components")
    print()

    # 7. Clustering Analysis
    print("7. CLUSTERING ANALYSIS")
    print("-" * 80)

    if G.number_of_edges() > 0:
        # Global clustering coefficient
        clustering_coeff = nx.average_clustering(G)
        print(f"  Average clustering coefficient: {clustering_coeff:.4f}")
        print(f"    (Higher = more triangles, more cohesive communities)")

        # Local clustering for top nodes
        local_clustering = nx.clustering(G)
        top_clustered = sorted(local_clustering.items(), key=lambda x: -x[1])[:5]
        if top_clustered:
            print(f"  Top 5 most clustered nodes:")
            for entity_id, coeff in top_clustered:
                entity_info = entity_data[entity_id]
                print(f"    {entity_info['name']}: {coeff:.3f}")
    else:
        print("  No edges - cannot calculate clustering")
    print()

    # 8. Identify Issues
    print("=" * 80)
    print("ISSUES IDENTIFIED")
    print("=" * 80)
    print()

    issues = []

    # Issue 1: Sparse graph
    density = nx.density(G)
    if density < 0.01:
        issues.append(
            f"⚠️  LOW GRAPH DENSITY: {density:.6f}\n"
            f"   - Graph is very sparse (density < 0.01)\n"
            f"   - Ideal density for community detection: 0.05 - 0.3\n"
            f"   - Impact: Difficult to form meaningful communities"
        )

    # Issue 2: Many isolated nodes
    if len(isolated_nodes) > G.number_of_nodes() * 0.2:
        issues.append(
            f"⚠️  MANY ISOLATED NODES: {len(isolated_nodes)} ({len(isolated_nodes)/G.number_of_nodes()*100:.1f}%)\n"
            f"   - {len(isolated_nodes)} entities have no relationships\n"
            f"   - These will always form single-node communities\n"
            f"   - Impact: Creates {len(isolated_nodes)} meaningless communities"
        )

    # Issue 3: Fragmented graph
    if len(components) > G.number_of_nodes() * 0.5:
        issues.append(
            f"⚠️  FRAGMENTED GRAPH: {len(components)} components\n"
            f"   - Graph is highly fragmented\n"
            f"   - Average component size: {sum(component_sizes)/len(component_sizes):.1f}\n"
            f"   - Impact: Cannot find large, cohesive communities"
        )

    # Issue 4: Low connectivity for entities
    if len(single_edge_nodes) > G.number_of_nodes() * 0.3:
        issues.append(
            f"⚠️  MANY LEAF NODES: {len(single_edge_nodes)} ({len(single_edge_nodes)/G.number_of_nodes()*100:.1f}%)\n"
            f"   - Many entities only connected to one other entity\n"
            f"   - These create linear chains, not communities\n"
            f"   - Impact: Weak community structure"
        )

    # Issue 5: Limited relationship diversity
    if len(predicate_counts) < 10:
        issues.append(
            f"⚠️  LIMITED RELATIONSHIP TYPES: {len(predicate_counts)} types\n"
            f"   - Few relationship types limits graph structure\n"
            f"   - May indicate extraction issues\n"
            f"   - Impact: Less semantic richness in graph"
        )

    if issues:
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")
            print()
    else:
        print("✅ No major structural issues detected!")
        print()

    # 9. Recommendations
    print("=" * 80)
    print("RECOMMENDATIONS FOR IMPROVEMENT")
    print("=" * 80)
    print()

    recommendations = []

    if density < 0.01:
        recommendations.append(
            "📈 INCREASE GRAPH DENSITY:\n"
            "   1. Extract more relationships per chunk (aim for 5-10 per chunk)\n"
            "   2. Extract implicit relationships (co-occurrence, similarity)\n"
            "   3. Extract hierarchical relationships (parent-child, part-of)\n"
            "   4. Link entities based on semantic similarity\n"
            "   Target: Density > 0.05"
        )

    if len(isolated_nodes) > G.number_of_nodes() * 0.2:
        recommendations.append(
            "🔗 CONNECT ISOLATED ENTITIES:\n"
            "   1. Use entity similarity (embeddings) to link similar entities\n"
            "   2. Extract co-occurrence relationships (entities in same chunk)\n"
            "   3. Extract temporal relationships (entities mentioned sequentially)\n"
            "   4. Create 'related_to' edges for semantically similar entities\n"
            "   Target: < 10% isolated entities"
        )

    if len(components) > G.number_of_nodes() * 0.5:
        recommendations.append(
            "🌐 REDUCE FRAGMENTATION:\n"
            "   1. Extract bridging relationships between topics\n"
            "   2. Link entities from different chunks/videos\n"
            "   3. Extract cross-references and mentions\n"
            "   4. Create meta-relationships (e.g., 'discusses_topic_with')\n"
            "   Target: Fewer, larger components"
        )

    if len(single_edge_nodes) > G.number_of_nodes() * 0.3:
        recommendations.append(
            "🔄 INCREASE NODE DEGREE:\n"
            "   1. Extract multiple relationship types per entity pair\n"
            "   2. Create bidirectional relationships\n"
            "   3. Extract multi-hop relationships (entity A → concept → entity B)\n"
            "   4. Link entities through shared concepts/topics\n"
            "   Target: Average degree > 2.0"
        )

    recommendations.append(
        "🎯 EXTRACTION IMPROVEMENTS:\n"
        "   1. Review extraction prompts - ensure comprehensive relationship extraction\n"
        "   2. Extract more relationship types (currently limited diversity)\n"
        "   3. Post-process to add implicit relationships (co-occurrence, similarity)\n"
        "   4. Use entity embeddings to find similar entities and link them\n"
        "   5. Extract relationships across chunk boundaries (global graph view)"
    )

    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
        print()

    print("=" * 80)
    print()


if __name__ == "__main__":
    try:
        analyze_graph_structure()
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
