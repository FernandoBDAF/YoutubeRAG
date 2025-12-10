#!/usr/bin/env python3
"""
Validate Metrics Registration - Quality Gate Script

Validates that all expected metrics are registered and accessible.
Used as a quality gate to ensure observability coverage.

Usage:
    python scripts/validate_metrics.py
    
Exit codes:
    0 - All expected metrics found
    1 - One or more metrics missing
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

try:
    # Import all services/chat modules to register metrics
    import business.services.rag.core  # noqa
    import business.services.rag.generation  # noqa
    import business.services.rag.retrieval  # noqa
    import business.services.rag.indexes  # noqa
    import business.services.rag.filters  # noqa
    import business.services.rag.feedback  # noqa
    import business.services.rag.profiles  # noqa
    import business.services.rag.persona_utils  # noqa
    import business.services.graphrag.retrieval  # noqa
    import business.services.graphrag.generation  # noqa
    import business.services.graphrag.query  # noqa
    import business.services.graphrag.indexes  # noqa
    import business.services.graphrag.run_metadata  # noqa
    import business.services.ingestion.transcripts  # noqa
    import business.services.ingestion.metadata  # noqa
    import business.chat.memory  # noqa
    import business.chat.retrieval  # noqa
    import business.chat.answering  # noqa
    import business.chat.query_rewriter  # noqa
    import business.services.chat.citations  # noqa
    import business.services.chat.export  # noqa
    import business.services.chat.filters  # noqa

    from core.libraries.metrics import MetricRegistry, export_prometheus_text
except ImportError as e:
    print(f"❌ Failed to import modules: {e}")
    sys.exit(1)


def validate_metrics():
    """
    Validate that all expected metrics are registered.
    
    Returns:
        tuple: (success: bool, found: list, missing: list)
    """
    registry = MetricRegistry.get_instance()
    expected_prefixes = [
        # RAG services
        'rag_service_',
        'rag_embedding_',
        'rag_generation_',
        'rag_retrieval_',
        'rag_index_',
        'rag_filter_',
        'rag_feedback_',
        'rag_profile_',
        'rag_persona_',
        # GraphRAG services
        'graphrag_retrieval_',
        'graphrag_generation_',
        'graphrag_query_',
        'graphrag_index_',
        'graphrag_run_metadata_',
        # Ingestion services
        'ingestion_service_',
        'ingestion_metadata_',
        # Chat modules
        'chat_memory_',
        'chat_retrieval_',
        'chat_answering_',
        'chat_query_rewriter_',
        # Chat services
        'chat_citations_',
        'chat_export_',
        'chat_filters_',
        # Base classes (via agents/stages)
        'agent_llm_',
        'stage_',
    ]
    
    try:
        metrics_text = export_prometheus_text()
    except Exception as e:
        print(f"❌ Failed to export metrics: {e}")
        return False, [], expected_prefixes
    
    found = []
    missing = []
    
    for prefix in expected_prefixes:
        if prefix in metrics_text:
            found.append(prefix)
        else:
            missing.append(prefix)
    
    return len(missing) == 0, found, missing


def main():
    """Main entry point."""
    print("Validating metrics registration...\n")
    
    try:
        success, found, missing = validate_metrics()
        
        print(f"✅ Found {len(found)}/{len(found) + len(missing)} metric groups")
        
        if found:
            print("\n📊 Registered metric groups:")
            for prefix in sorted(found):
                print(f"  ✓ {prefix}*")
        
        if missing:
            print(f"\n⚠️  Missing {len(missing)} metric groups:")
            for prefix in sorted(missing):
                print(f"  ✗ {prefix}*")
        
        print(f"\n{'='*60}")
        if success:
            print("✅ All expected metrics registered")
            sys.exit(0)
        else:
            print(f"❌ {len(missing)} metric groups missing")
            print("\nNote: Some metrics may be registered but not yet exported.")
            print("Check that services are properly importing and registering metrics.")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Metrics validation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

