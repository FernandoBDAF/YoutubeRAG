#!/usr/bin/env python3
"""
Inspect Community Detection Algorithm Output

This script investigates what hierarchical_leiden returns and how
our code processes it to understand why we're getting single-entity communities.
"""

import os
import sys
from collections import defaultdict, Counter
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.utils import get_mongo_client
from config.paths import DB_NAME
from agents.community_detection_agent import CommunityDetectionAgent
from core.graphrag_models import ResolvedEntity, ResolvedRelationship
import networkx as nx
from graspologic.partition import hierarchical_leiden
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


def inspect_hierarchical_leiden_output():
    """Inspect what hierarchical_leiden actually returns."""
    client = get_mongo_client()
    db = client[DB_NAME]

    print("=" * 80)
    print("Inspecting hierarchical_leiden Output")
    print("=" * 80)
    print()

    # Get entities and relationships
    entities_docs = list(db.entities.find())
    relationships_docs = list(db.relations.find())

    print(f"1. INPUT DATA")
    print("-" * 80)
    print(f"  Entities: {len(entities_docs):,}")
    print(f"  Relationships: {len(relationships_docs):,}")
    print()

    # Convert to ResolvedEntity and ResolvedRelationship objects
    entities = []
    for doc in entities_docs:
        try:
            entity = ResolvedEntity(
                entity_id=doc["entity_id"],
                canonical_name=doc["canonical_name"],
                name=doc["name"],
                type=doc["type"],
                description=doc["description"],
                confidence=doc.get("confidence", 0.0),
                source_count=doc.get("source_count", 1),
                resolution_methods=doc.get("resolution_methods", []),
                aliases=doc.get("aliases", []),
            )
            entities.append(entity)
        except Exception as e:
            print(f"  ⚠️  Failed to parse entity: {e}")
            continue

    relationships = []
    for doc in relationships_docs:
        try:
            rel = ResolvedRelationship(
                relationship_id=doc["relationship_id"],
                subject_id=doc["subject_id"],
                object_id=doc["object_id"],
                predicate=doc["predicate"],
                description=doc["description"],
                confidence=doc.get("confidence", 0.0),
                source_count=doc.get("source_count", 1),
            )
            relationships.append(rel)
        except Exception as e:
            print(f"  ⚠️  Failed to parse relationship: {e}")
            continue

    print(f"  Parsed entities: {len(entities):,}")
    print(f"  Parsed relationships: {len(relationships):,}")
    print()

    # Create NetworkX graph
    print("2. NETWORKX GRAPH STRUCTURE")
    print("-" * 80)
    G = nx.Graph()

    # Add nodes
    for entity in entities:
        G.add_node(
            entity.entity_id,
            name=entity.name,
            type=entity.type.value,
        )

    # Add edges
    edges_added = 0
    edges_skipped = 0
    for rel in relationships:
        if G.has_node(rel.subject_id) and G.has_node(rel.object_id):
            G.add_edge(
                rel.subject_id,
                rel.object_id,
                predicate=rel.predicate,
            )
            edges_added += 1
        else:
            edges_skipped += 1

    print(f"  Nodes: {G.number_of_nodes():,}")
    print(f"  Edges: {edges_added:,} (skipped: {edges_skipped:,})")
    print(f"  Graph density: {nx.density(G):.4f}")
    print()

    # Check connected components
    print("3. CONNECTED COMPONENTS ANALYSIS")
    print("-" * 80)
    components = list(nx.connected_components(G))
    component_sizes = [len(c) for c in components]
    size_distribution = Counter(component_sizes)

    print(f"  Total connected components: {len(components):,}")
    print(f"  Component size distribution:")
    for size, count in sorted(size_distribution.items()):
        print(f"    {size} node(s): {count} components")

    isolated_nodes = sum(1 for size in component_sizes if size == 1)
    connected_nodes = sum(size for size in component_sizes if size > 1)

    print(f"\n  Isolated nodes (size=1): {isolated_nodes:,}")
    print(f"  Nodes in multi-node components: {connected_nodes:,}")
    print()

    # Run hierarchical_leiden
    print("4. hierarchical_leiden OUTPUT")
    print("-" * 80)

    try:
        communities = hierarchical_leiden(G, max_cluster_size=10)

        print(f"  ✅ hierarchical_leiden succeeded")
        print(f"  Returned {len(communities)} community objects")
        print()

        # Inspect structure of returned objects
        print("  Sample community objects (first 5):")
        for i, comm in enumerate(communities[:5]):
            print(f"    Community {i}:")
            print(f"      Type: {type(comm)}")
            print(f"      Attributes: {dir(comm)}")
            # Try to get common attributes
            attrs_to_check = [
                "cluster",
                "node",
                "nodes",
                "level",
                "cluster_id",
                "community_id",
            ]
            for attr in attrs_to_check:
                if hasattr(comm, attr):
                    value = getattr(comm, attr)
                    if attr == "nodes":
                        value = f"<set with {len(value) if hasattr(value, '__len__') else '?'} items>"
                    print(f"      {attr}: {value}")
            print()

        # Analyze what hierarchical_leiden actually returns
        print("  Analyzing community structure:")
        clusters = defaultdict(set)
        levels = defaultdict(int)
        nodes_in_communities = set()

        for comm in communities:
            # Try to extract cluster ID
            cluster_id = None
            if hasattr(comm, "cluster"):
                cluster_id = comm.cluster
            elif hasattr(comm, "cluster_id"):
                cluster_id = comm.cluster_id
            else:
                # Fallback: use object ID or index
                cluster_id = id(comm)

            # Try to extract node(s)
            nodes_in_comm = set()
            if hasattr(comm, "nodes"):
                nodes_in_comm = set(comm.nodes)
            elif hasattr(comm, "node"):
                nodes_in_comm = {comm.node}
            elif hasattr(comm, "__iter__"):
                try:
                    nodes_in_comm = set(comm)
                except:
                    pass

            # Try to extract level
            level = 1
            if hasattr(comm, "level"):
                level = comm.level

            if nodes_in_comm:
                clusters[cluster_id].update(nodes_in_comm)
                levels[cluster_id] = max(levels[cluster_id], level)
                nodes_in_communities.update(nodes_in_comm)

        print(f"    Unique clusters found: {len(clusters):,}")
        print(f"    Nodes in communities: {len(nodes_in_communities):,}")
        print(
            f"    Nodes not in communities: {G.number_of_nodes() - len(nodes_in_communities):,}"
        )
        print()

        # Cluster size distribution
        cluster_sizes = Counter(len(nodes) for nodes in clusters.values())
        print(f"    Cluster size distribution:")
        for size, count in sorted(cluster_sizes.items()):
            print(f"      {size} node(s): {count} clusters")

        # Check if hierarchical_leiden creates single-node communities
        single_node_clusters = sum(1 for nodes in clusters.values() if len(nodes) == 1)
        multi_node_clusters = sum(1 for nodes in clusters.values() if len(nodes) > 1)

        print(f"\n    Single-node clusters: {single_node_clusters:,}")
        print(f"    Multi-node clusters: {multi_node_clusters:,}")

        if single_node_clusters > 0:
            print(
                f"\n    ⚠️  PROBLEM: hierarchical_leiden is creating {single_node_clusters} single-node communities!"
            )
            print(f"       This explains why all communities have entity_count=1")

    except Exception as e:
        print(f"  ❌ hierarchical_leiden failed: {e}")
        import traceback

        traceback.print_exc()
        print()
        print("  Using fallback detection instead...")
        # Try fallback
        components = list(nx.connected_components(G))
        communities = []
        for i, component in enumerate(components):
            if len(component) >= 2:  # min_cluster_size
                if len(component) > 1:
                    community = type(
                        "Community", (), {"cluster": i, "nodes": component, "level": 1}
                    )()
                else:
                    community = type(
                        "Community",
                        (),
                        {"cluster": i, "node": list(component)[0], "level": 1},
                    )()
                communities.append(community)

        print(f"  Fallback created {len(communities)} communities")
        print()

    # Now test how our code processes these
    print("5. HOW OUR CODE PROCESSES COMMUNITIES")
    print("-" * 80)

    # Use the actual agent
    agent = CommunityDetectionAgent(max_cluster_size=10, min_cluster_size=2)

    try:
        result = agent.detect_communities(entities, relationships)

        print(f"  ✅ Agent processing succeeded")
        print(f"  Organized communities: {len(result.get('communities', {}))} levels")
        print(f"  Total communities: {result.get('total_communities', 0)}")
        print()

        # Inspect organized communities
        organized = result.get("communities", {})
        for level, level_communities in organized.items():
            print(f"  Level {level}: {len(level_communities)} communities")
            size_dist = Counter(
                comm.get("entity_count", 0) for comm in level_communities.values()
            )
            for size, count in sorted(size_dist.items()):
                print(f"    {size} entity(ies): {count} communities")

        # Check quality metrics
        quality = result.get("quality_metrics", {})
        print(f"\n  Quality metrics:")
        print(f"    Avg coherence: {quality.get('avg_coherence', 0):.3f}")
        print(f"    Avg size: {quality.get('avg_size', 0):.2f}")
        print(f"    Coverage: {quality.get('coverage', 0):.1%}")

    except Exception as e:
        print(f"  ❌ Agent processing failed: {e}")
        import traceback

        traceback.print_exc()

    print()
    print("=" * 80)
    print("DIAGNOSIS")
    print("=" * 80)
    print()


if __name__ == "__main__":
    try:
        inspect_hierarchical_leiden_output()
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
