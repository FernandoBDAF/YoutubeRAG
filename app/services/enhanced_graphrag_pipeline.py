"""
Enhanced GraphRAG Pipeline with MongoDB Query Generation.

This module provides an enhanced GraphRAG pipeline that integrates advanced
MongoDB query generation capabilities for optimal performance and flexibility.
"""

import logging
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from openai import OpenAI
from pymongo import MongoClient
from pymongo.database import Database

from app.services.graphrag_mongodb_query import (
    GraphRAGMongoDBQueryGenerator,
    GraphRAGIndexManager,
    GraphRAGQueryOptimizer,
    GraphRAGMongoDBQueryBuilder,
    GraphRAGQueryMonitor,
    GraphRAGQueryContext,
)
from app.services.graphrag_generation import GraphRAGGenerationService
from app.services.graphrag_query import GraphRAGQueryProcessor
from app.services.graphrag_retrieval import GraphRAGRetrievalEngine

logger = logging.getLogger(__name__)


@dataclass
class EnhancedGraphRAGConfig:
    """Configuration for enhanced GraphRAG pipeline."""

    # MongoDB settings
    mongodb_uri: str
    database_name: str

    # LLM settings
    openai_api_key: str
    model_name: str = "gpt-4o-mini"

    # Query generation settings
    enable_natural_language_queries: bool = True
    enable_query_optimization: bool = True
    enable_performance_monitoring: bool = True

    # GraphRAG settings
    max_entities_per_query: int = 20
    max_relationship_depth: int = 2
    min_confidence_threshold: float = 0.5
    max_context_length: int = 4000

    # Performance settings
    query_timeout_ms: int = 30000
    max_concurrent_queries: int = 5


class EnhancedGraphRAGPipeline:
    """
    Enhanced GraphRAG pipeline with advanced MongoDB query generation.

    This pipeline integrates natural language query generation, performance
    optimization, and comprehensive monitoring for GraphRAG operations.
    """

    def __init__(self, config: EnhancedGraphRAGConfig):
        self.config = config
        self._initialize_components()

    def _initialize_components(self):
        """Initialize all pipeline components."""
        try:
            # Initialize MongoDB connection
            self.client = MongoClient(self.config.mongodb_uri)
            self.db = self.client[self.config.database_name]

            # Initialize LLM client
            self.llm_client = OpenAI(api_key=self.config.openai_api_key)

            # Initialize GraphRAG components
            self.query_processor = GraphRAGQueryProcessor(self.llm_client)
            self.retrieval_engine = GraphRAGRetrievalEngine(self.db)
            self.generation_service = GraphRAGGenerationService(
                self.llm_client,
                query_processor=self.query_processor,
                retrieval_engine=self.retrieval_engine,
            )

            # Initialize MongoDB query components
            self.query_generator = GraphRAGMongoDBQueryGenerator(
                self.llm_client, self.db, self.config.model_name
            )
            self.index_manager = GraphRAGIndexManager(self.db)
            self.query_optimizer = GraphRAGQueryOptimizer(self.db)
            self.query_builder = GraphRAGMongoDBQueryBuilder(self.db)
            self.query_monitor = GraphRAGQueryMonitor(self.db)

            logger.info("Enhanced GraphRAG pipeline initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing enhanced GraphRAG pipeline: {e}")
            raise

    def setup_graphrag_infrastructure(self) -> Dict[str, Any]:
        """
        Set up GraphRAG infrastructure including indexes and collections.

        Returns:
            Dictionary containing setup results
        """
        try:
            results = {
                "indexes_created": {},
                "collections_verified": {},
                "setup_successful": True,
            }

            # Create GraphRAG indexes
            if self.config.enable_query_optimization:
                index_results = self.index_manager.create_graphrag_indexes()
                results["indexes_created"] = index_results

            # Verify collections exist
            required_collections = ["entities", "relations", "communities", "chunks"]
            for collection_name in required_collections:
                try:
                    collection = self.db[collection_name]
                    count = collection.count_documents({})
                    results["collections_verified"][collection_name] = {
                        "exists": True,
                        "document_count": count,
                    }
                except Exception as e:
                    results["collections_verified"][collection_name] = {
                        "exists": False,
                        "error": str(e),
                    }
                    results["setup_successful"] = False

            logger.info("GraphRAG infrastructure setup completed")
            return results

        except Exception as e:
            logger.error(f"Error setting up GraphRAG infrastructure: {e}")
            return {"setup_successful": False, "error": str(e)}

    def process_query_with_enhanced_generation(
        self,
        query: str,
        use_natural_language_queries: Optional[bool] = None,
        include_performance_analysis: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Process a query using enhanced GraphRAG with optional natural language query generation.

        Args:
            query: User's natural language query
            use_natural_language_queries: Override config setting
            include_performance_analysis: Whether to include performance analysis

        Returns:
            Enhanced GraphRAG response with query generation details
        """
        start_time = time.time()

        try:
            # Determine if natural language queries should be used
            use_nl_queries = (
                use_natural_language_queries
                if use_natural_language_queries is not None
                else self.config.enable_natural_language_queries
            )

            # Extract entities and determine query intent
            extracted_entities = self.query_processor.extract_query_entities(query)
            query_intent = self._determine_query_intent(query, extracted_entities)

            # Create query context
            context = GraphRAGQueryContext(
                user_query=query,
                extracted_entities=extracted_entities,
                query_intent=query_intent,
                collections_involved=["entities", "relations", "communities"],
                performance_requirements={
                    "max_execution_time_ms": self.config.query_timeout_ms,
                    "max_results": self.config.max_entities_per_query,
                },
            )

            # Generate MongoDB queries if enabled
            generated_queries = {}
            if use_nl_queries:
                generated_queries = self._generate_mongodb_queries(context)

            # Execute GraphRAG processing
            graphrag_response = self.generation_service.process_query_with_generation(
                query, self.db, use_traditional_rag=False
            )

            # Add query generation information
            enhanced_response = {
                **graphrag_response.__dict__,
                "query_generation": {
                    "natural_language_queries_enabled": use_nl_queries,
                    "generated_queries": generated_queries,
                    "query_intent": query_intent,
                    "extracted_entities": extracted_entities,
                },
            }

            # Add performance analysis if requested
            if (
                include_performance_analysis
                or self.config.enable_performance_monitoring
            ):
                performance_analysis = self._analyze_query_performance(
                    context, generated_queries
                )
                enhanced_response["performance_analysis"] = performance_analysis

            # Calculate total processing time
            processing_time = time.time() - start_time
            enhanced_response["total_processing_time"] = processing_time

            logger.info(f"Enhanced GraphRAG query processed in {processing_time:.2f}s")
            return enhanced_response

        except Exception as e:
            logger.error(f"Error in enhanced GraphRAG processing: {e}")
            return {
                "error": str(e),
                "processing_time": time.time() - start_time,
                "fallback_used": True,
            }

    def _determine_query_intent(self, query: str, entities: List[str]) -> str:
        """
        Determine the intent of the query based on content and entities.

        Args:
            query: User's query
            entities: Extracted entities

        Returns:
            Query intent classification
        """
        query_lower = query.lower()

        # Intent classification based on query content
        if any(
            word in query_lower
            for word in ["relationship", "related", "connected", "link"]
        ):
            return "relationship_traversal"
        elif any(
            word in query_lower for word in ["community", "group", "cluster", "summary"]
        ):
            return "community_summary"
        elif any(
            word in query_lower for word in ["who", "what", "where", "when", "how"]
        ):
            return "entity_search"
        elif len(entities) > 1:
            return "multi_entity_search"
        else:
            return "entity_search"

    def _generate_mongodb_queries(
        self, context: GraphRAGQueryContext
    ) -> Dict[str, Any]:
        """
        Generate MongoDB queries based on query context.

        Args:
            context: GraphRAG query context

        Returns:
            Dictionary containing generated queries
        """
        try:
            generated_queries = {}

            # Generate entity search query
            entity_query_result = self.query_generator.generate_entity_search_query(
                context, search_type="hybrid"
            )
            generated_queries["entity_search"] = entity_query_result

            # Generate relationship traversal query if applicable
            if context.query_intent in [
                "relationship_traversal",
                "multi_entity_search",
            ]:
                traversal_query_result = (
                    self.query_generator.generate_relationship_traversal_query(
                        context,
                        context.extracted_entities,
                        self.config.max_relationship_depth,
                    )
                )
                generated_queries["relationship_traversal"] = traversal_query_result

            # Generate community summary query if applicable
            if context.query_intent in ["community_summary", "multi_entity_search"]:
                community_query_result = (
                    self.query_generator.generate_community_summary_query(
                        context, context.extracted_entities
                    )
                )
                generated_queries["community_summary"] = community_query_result

            # Optimize queries if enabled
            if self.config.enable_query_optimization:
                for query_type, query_result in generated_queries.items():
                    if hasattr(query_result, "query") and query_result.query:
                        optimized_query = self.query_optimizer.optimize_query(
                            query_result.query, "entities"  # Default collection
                        )
                        query_result.query = optimized_query

            logger.info(f"Generated {len(generated_queries)} MongoDB queries")
            return generated_queries

        except Exception as e:
            logger.error(f"Error generating MongoDB queries: {e}")
            return {"error": str(e)}

    def _analyze_query_performance(
        self, context: GraphRAGQueryContext, generated_queries: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze the performance of generated queries.

        Args:
            context: GraphRAG query context
            generated_queries: Generated MongoDB queries

        Returns:
            Performance analysis results
        """
        try:
            performance_analysis = {
                "query_count": len(generated_queries),
                "query_analyses": {},
                "overall_performance": {},
            }

            # Analyze each generated query
            for query_type, query_result in generated_queries.items():
                if hasattr(query_result, "query") and query_result.query:
                    analysis = self.query_monitor.analyze_query_performance(
                        "entities", query_result.query
                    )
                    performance_analysis["query_analyses"][query_type] = analysis

            # Calculate overall performance metrics
            if performance_analysis["query_analyses"]:
                total_execution_time = sum(
                    analysis.get("execution_time_ms", 0)
                    for analysis in performance_analysis["query_analyses"].values()
                )
                performance_analysis["overall_performance"] = {
                    "total_execution_time_ms": total_execution_time,
                    "average_execution_time_ms": total_execution_time
                    / len(performance_analysis["query_analyses"]),
                    "queries_optimized": len(
                        [
                            analysis
                            for analysis in performance_analysis[
                                "query_analyses"
                            ].values()
                            if analysis.get("stage") != "COLLSCAN"
                        ]
                    ),
                }

            logger.info("Query performance analysis completed")
            return performance_analysis

        except Exception as e:
            logger.error(f"Error analyzing query performance: {e}")
            return {"error": str(e)}

    def get_pipeline_status(self) -> Dict[str, Any]:
        """
        Get the current status of the enhanced GraphRAG pipeline.

        Returns:
            Pipeline status information
        """
        try:
            status = {
                "pipeline_initialized": True,
                "components_status": {},
                "infrastructure_status": {},
                "configuration": {
                    "natural_language_queries": self.config.enable_natural_language_queries,
                    "query_optimization": self.config.enable_query_optimization,
                    "performance_monitoring": self.config.enable_performance_monitoring,
                    "max_entities_per_query": self.config.max_entities_per_query,
                    "max_relationship_depth": self.config.max_relationship_depth,
                },
            }

            # Check component status
            components = [
                "query_processor",
                "retrieval_engine",
                "generation_service",
                "query_generator",
                "index_manager",
                "query_optimizer",
                "query_builder",
                "query_monitor",
            ]

            for component_name in components:
                try:
                    component = getattr(self, component_name)
                    status["components_status"][component_name] = {
                        "initialized": component is not None,
                        "type": type(component).__name__,
                    }
                except Exception as e:
                    status["components_status"][component_name] = {
                        "initialized": False,
                        "error": str(e),
                    }

            # Check infrastructure status
            infrastructure_status = self.setup_graphrag_infrastructure()
            status["infrastructure_status"] = infrastructure_status

            logger.info("Pipeline status retrieved successfully")
            return status

        except Exception as e:
            logger.error(f"Error getting pipeline status: {e}")
            return {"pipeline_initialized": False, "error": str(e)}

    def optimize_pipeline_performance(self) -> Dict[str, Any]:
        """
        Optimize pipeline performance by analyzing and improving query patterns.

        Returns:
            Optimization results
        """
        try:
            optimization_results = {
                "index_optimizations": {},
                "query_optimizations": {},
                "performance_improvements": {},
            }

            # Analyze current indexes
            collections = ["entities", "relations", "communities", "chunks"]
            for collection_name in collections:
                try:
                    collection = self.db[collection_name]
                    indexes = list(collection.list_indexes())

                    optimization_results["index_optimizations"][collection_name] = {
                        "current_indexes": len(indexes),
                        "index_details": [
                            {
                                "name": idx.get("name"),
                                "key": idx.get("key"),
                                "type": idx.get("type", "regular"),
                            }
                            for idx in indexes
                        ],
                    }

                except Exception as e:
                    optimization_results["index_optimizations"][collection_name] = {
                        "error": str(e)
                    }

            # Suggest query optimizations
            optimization_results["query_optimizations"] = {
                "suggestions": [
                    "Use compound indexes for multi-field queries",
                    "Add sparse indexes for optional fields",
                    "Consider partial indexes for filtered queries",
                    "Use text indexes for full-text search",
                    "Optimize aggregation pipelines with early filtering",
                ]
            }

            logger.info("Pipeline performance optimization completed")
            return optimization_results

        except Exception as e:
            logger.error(f"Error optimizing pipeline performance: {e}")
            return {"error": str(e)}

    def close(self):
        """Close the pipeline and clean up resources."""
        try:
            if hasattr(self, "client"):
                self.client.close()
            logger.info("Enhanced GraphRAG pipeline closed")
        except Exception as e:
            logger.error(f"Error closing pipeline: {e}")


def create_enhanced_graphrag_pipeline(
    mongodb_uri: str, database_name: str, openai_api_key: str, **kwargs
) -> EnhancedGraphRAGPipeline:
    """
    Factory function to create an enhanced GraphRAG pipeline.

    Args:
        mongodb_uri: MongoDB connection URI
        database_name: Database name
        openai_api_key: OpenAI API key
        **kwargs: Additional configuration options

    Returns:
        Configured EnhancedGraphRAGPipeline instance
    """
    config = EnhancedGraphRAGConfig(
        mongodb_uri=mongodb_uri,
        database_name=database_name,
        openai_api_key=openai_api_key,
        **kwargs,
    )

    return EnhancedGraphRAGPipeline(config)
