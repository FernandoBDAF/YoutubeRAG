#!/usr/bin/env python3
"""
Test community detection on the cleaned graph.
"""

import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv
import networkx as nx

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
db_name = os.getenv("DB_NAME", "mongo_hack")

client = MongoClient(mongo_uri)
db = client[db_name]

print("=" * 80)
print("TESTING COMMUNITY DETECTION ON CLEANED GRAPH")
print("=" * 80)

# Get entities and relationships
entities = list(db.entities.find())
relationships = list(db.relations.find())

print(f"\nGraph data:")
print(f"  Entities: {len(entities)}")
print(f"  Relationships: {len(relationships)}")

# Build NetworkX graph
print(f"\nBuilding NetworkX graph...")
G = nx.Graph()

for entity in entities:
    G.add_node(entity["entity_id"], **entity)

for rel in relationships:
    G.add_edge(rel["subject_id"], rel["object_id"], **rel)

print(f"  Nodes: {G.number_of_nodes()}")
print(f"  Edges: {G.number_of_edges()}")
print(f"  Density: {nx.density(G):.6f}")

# Try hierarchical Leiden
print(f"\n" + "-" * 80)
print("Running hierarchical_leiden algorithm...")
print("-" * 80)

try:
    from graspologic.partition import hierarchical_leiden

    communities = hierarchical_leiden(G, max_cluster_size=50)

    print(f"\n✓ Detected {len(communities)} communities")

    # Count communities by size
    community_sizes = {}
    for community in communities:
        if hasattr(community, "nodes"):
            size = len(list(community.nodes))
        else:
            size = 1

        community_sizes[size] = community_sizes.get(size, 0) + 1

    print(f"\nCommunity size distribution:")
    for size in sorted(community_sizes.keys(), reverse=True):
        count = community_sizes[size]
        print(f"  {size} entities: {count} communities")

    # Count multi-entity communities (≥2)
    multi_entity = sum(count for size, count in community_sizes.items() if size >= 2)
    single_entity = sum(count for size, count in community_sizes.items() if size == 1)

    print(f"\nSummary:")
    print(f"  Multi-entity communities (≥2): {multi_entity}")
    print(f"  Single-entity communities: {single_entity}")

    if multi_entity > 0:
        print(f"\n✅ SUCCESS: Detected {multi_entity} meaningful communities!")
    else:
        print(f"\n⚠️ WARNING: All communities are single-entity")
        print(f"   This might indicate the graph is still too sparse or fragmented")

except ImportError:
    print("\n❌ graspologic not installed")
    print("   Install with: pip install graspologic")
    print("\nFalling back to simple community detection...")

    # Fallback: Use NetworkX connected components
    components = list(nx.connected_components(G))
    print(f"\n✓ Found {len(components)} connected components")

    for i, component in enumerate(components[:10]):
        print(f"  Component {i+1}: {len(component)} nodes")

    # Try Louvain (built into NetworkX)
    try:
        import networkx.algorithms.community as nx_comm

        communities = list(nx_comm.greedy_modularity_communities(G))

        print(f"\n✓ Detected {len(communities)} communities (Louvain)")

        # Show community sizes
        community_sizes = [len(c) for c in communities]
        for i, size in enumerate(sorted(community_sizes, reverse=True)[:10]):
            print(f"  Community {i+1}: {size} entities")

        multi_entity = sum(1 for c in communities if len(c) >= 2)
        print(f"\n✅ Multi-entity communities: {multi_entity}")

    except Exception as e:
        print(f"\n❌ Louvain failed: {e}")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
