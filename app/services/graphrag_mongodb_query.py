"""
Enhanced MongoDB Query Generation for GraphRAG.

This module provides advanced MongoDB query generation capabilities specifically
designed for GraphRAG operations, including natural language to MongoDB query
conversion, schema-aware query building, and performance optimization.
"""

import logging
import json
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from openai import OpenAI
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

logger = logging.getLogger(__name__)


@dataclass
class MongoDBQueryResult:
    """Result of MongoDB query generation."""

    query: Dict[str, Any]
    query_type: str  # "aggregation", "find", "vector_search", "hybrid"
    confidence: float
    explanation: str
    performance_hints: List[str]
    fallback_queries: List[Dict[str, Any]]


@dataclass
class GraphRAGQueryContext:
    """Context for GraphRAG query generation."""

    user_query: str
    extracted_entities: List[str]
    query_intent: (
        str  # "entity_search", "relationship_traversal", "community_summary", "hybrid"
    )
    collections_involved: List[str]
    performance_requirements: Dict[str, Any]


class GraphRAGMongoDBQueryGenerator:
    """
    Advanced MongoDB query generator for GraphRAG operations.

    This class uses LLM-driven query generation with detailed prompts,
    schema awareness, and performance optimization for GraphRAG queries.
    """

    def __init__(
        self, llm_client: OpenAI, db: Database, model_name: str = "gpt-4o-mini"
    ):
        self.llm_client = llm_client
        self.db = db
        self.model_name = model_name
        self.schema_info = self._get_database_schema()

    def _get_database_schema(self) -> Dict[str, Any]:
        """Get comprehensive database schema information."""
        try:
            schema = {"collections": {}, "indexes": {}, "sample_documents": {}}

            # Get collection schemas
            for collection_name in ["chunks", "entities", "relations", "communities"]:
                try:
                    collection = self.db[collection_name]

                    # Get sample documents
                    sample_docs = list(collection.find().limit(3))
                    schema["sample_documents"][collection_name] = sample_docs

                    # Get indexes
                    indexes = list(collection.list_indexes())
                    schema["indexes"][collection_name] = [
                        {
                            "name": idx.get("name"),
                            "key": idx.get("key"),
                            "type": idx.get("type", "regular"),
                        }
                        for idx in indexes
                    ]

                    # Get field information from sample documents
                    if sample_docs:
                        fields = set()
                        for doc in sample_docs:
                            fields.update(doc.keys())
                        schema["collections"][collection_name] = {
                            "fields": list(fields),
                            "document_count": collection.count_documents({}),
                        }

                except Exception as e:
                    logger.warning(
                        f"Could not get schema for collection {collection_name}: {e}"
                    )

            return schema

        except Exception as e:
            logger.error(f"Failed to get database schema: {e}")
            return {"collections": {}, "indexes": {}, "sample_documents": {}}

    def generate_entity_search_query(
        self, context: GraphRAGQueryContext, search_type: str = "hybrid"
    ) -> MongoDBQueryResult:
        """
        Generate MongoDB query for entity search operations.

        Args:
            context: GraphRAG query context
            search_type: Type of search ("text", "vector", "hybrid")

        Returns:
            MongoDBQueryResult with generated query
        """
        try:
            prompt = self._build_entity_search_prompt(context, search_type)

            response = self.llm_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
            )

            result_text = response.choices[0].message.content

            # Parse the LLM response
            query_result = self._parse_query_response(result_text, "entity_search")

            logger.info(
                f"Generated entity search query with confidence {query_result.confidence}"
            )
            return query_result

        except Exception as e:
            logger.error(f"Error generating entity search query: {e}")
            return self._get_fallback_entity_query(context)

    def generate_relationship_traversal_query(
        self,
        context: GraphRAGQueryContext,
        source_entities: List[str],
        max_depth: int = 2,
    ) -> MongoDBQueryResult:
        """
        Generate MongoDB query for relationship traversal.

        Args:
            context: GraphRAG query context
            source_entities: List of source entity names
            max_depth: Maximum traversal depth

        Returns:
            MongoDBQueryResult with generated query
        """
        try:
            prompt = self._build_traversal_prompt(context, source_entities, max_depth)

            response = self.llm_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
            )

            result_text = response.choices[0].message.content
            query_result = self._parse_query_response(
                result_text, "relationship_traversal"
            )

            logger.info(
                f"Generated relationship traversal query with confidence {query_result.confidence}"
            )
            return query_result

        except Exception as e:
            logger.error(f"Error generating relationship traversal query: {e}")
            return self._get_fallback_traversal_query(source_entities, max_depth)

    def generate_community_summary_query(
        self, context: GraphRAGQueryContext, entity_names: List[str]
    ) -> MongoDBQueryResult:
        """
        Generate MongoDB query for community summary retrieval.

        Args:
            context: GraphRAG query context
            entity_names: List of entity names to find communities for

        Returns:
            MongoDBQueryResult with generated query
        """
        try:
            prompt = self._build_community_prompt(context, entity_names)

            response = self.llm_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
            )

            result_text = response.choices[0].message.content
            query_result = self._parse_query_response(result_text, "community_summary")

            logger.info(
                f"Generated community summary query with confidence {query_result.confidence}"
            )
            return query_result

        except Exception as e:
            logger.error(f"Error generating community summary query: {e}")
            return self._get_fallback_community_query(entity_names)

    def _get_system_prompt(self) -> str:
        """Get the system prompt for MongoDB query generation."""
        return f"""
You are an expert MongoDB query generator specializing in GraphRAG operations. 
You generate optimized MongoDB queries based on natural language descriptions.

Database Schema:
{json.dumps(self.schema_info, indent=2)}

Key Guidelines:
1. Always use proper MongoDB aggregation pipeline syntax
2. Optimize for performance using appropriate indexes
3. Include proper error handling and fallback options
4. Use $lookup for joins between collections
5. Use $graphLookup for graph traversal operations
6. Include proper projection to limit returned fields
7. Add performance hints and explanations

Response Format:
Return a JSON object with:
- "query": The MongoDB query/aggregation pipeline
- "query_type": Type of query ("aggregation", "find", "vector_search", "hybrid")
- "confidence": Confidence score (0-1)
- "explanation": Human-readable explanation of the query
- "performance_hints": List of performance optimization hints
- "fallback_queries": List of simpler fallback queries

Example Response:
{{
    "query": {{"$match": {{"name": {{"$in": ["Entity1", "Entity2"]}}}}}},
    "query_type": "find",
    "confidence": 0.9,
    "explanation": "Find entities by name using exact match",
    "performance_hints": ["Use compound index on name field", "Limit results with $limit"],
    "fallback_queries": [{{"$match": {{"name": "Entity1"}}}}]
}}
"""

    def _build_entity_search_prompt(
        self, context: GraphRAGQueryContext, search_type: str
    ) -> str:
        """Build prompt for entity search query generation."""
        return f"""
Generate a MongoDB query to search for entities based on the following context:

User Query: {context.user_query}
Extracted Entities: {context.extracted_entities}
Search Type: {search_type}
Collections Involved: {context.collections_involved}

Requirements:
- Search for entities that match the extracted entity names
- Use appropriate search method based on search_type
- Include related entity information
- Optimize for performance
- Return entity details and relationships

Collections Available:
- entities: Contains entity information with fields like name, type, description, canonical_name
- relations: Contains relationships between entities
- chunks: Contains original text chunks with entity mentions

Generate an optimized MongoDB aggregation pipeline.
"""

    def _build_traversal_prompt(
        self, context: GraphRAGQueryContext, source_entities: List[str], max_depth: int
    ) -> str:
        """Build prompt for relationship traversal query generation."""
        return f"""
Generate a MongoDB query to traverse relationships from source entities:

User Query: {context.user_query}
Source Entities: {source_entities}
Max Depth: {max_depth}
Collections Involved: {context.collections_involved}

Requirements:
- Start from source entities
- Traverse relationships up to max_depth
- Return all connected entities and relationships
- Include relationship details and confidence scores
- Optimize for performance with proper indexing

Collections Available:
- entities: Entity information
- relations: Relationships with source_id, target_id, relationship_type, confidence

Generate an optimized MongoDB aggregation pipeline using $graphLookup.
"""

    def _build_community_prompt(
        self, context: GraphRAGQueryContext, entity_names: List[str]
    ) -> str:
        """Build prompt for community summary query generation."""
        return f"""
Generate a MongoDB query to retrieve community summaries for entities:

User Query: {context.user_query}
Entity Names: {entity_names}
Collections Involved: {context.collections_involved}

Requirements:
- Find communities that contain the specified entities
- Return community summaries and metadata
- Include community coherence scores
- Return hierarchical community information if available
- Optimize for performance

Collections Available:
- communities: Contains community information with entities array, summary, coherence_score
- entities: Entity information for cross-referencing

Generate an optimized MongoDB aggregation pipeline.
"""

    def _parse_query_response(
        self, response_text: str, query_type: str
    ) -> MongoDBQueryResult:
        """Parse LLM response into MongoDBQueryResult."""
        try:
            # Try to parse as JSON
            result_data = json.loads(response_text)

            return MongoDBQueryResult(
                query=result_data.get("query", {}),
                query_type=result_data.get("query_type", "aggregation"),
                confidence=result_data.get("confidence", 0.5),
                explanation=result_data.get("explanation", ""),
                performance_hints=result_data.get("performance_hints", []),
                fallback_queries=result_data.get("fallback_queries", []),
            )

        except json.JSONDecodeError:
            # Fallback parsing for non-JSON responses
            logger.warning("Could not parse LLM response as JSON, using fallback")
            return self._get_fallback_query(query_type)

    def _get_fallback_entity_query(
        self, context: GraphRAGQueryContext
    ) -> MongoDBQueryResult:
        """Get fallback entity search query."""
        return MongoDBQueryResult(
            query={
                "$match": {
                    "$or": [
                        {"name": {"$in": context.extracted_entities}},
                        {"canonical_name": {"$in": context.extracted_entities}},
                    ]
                }
            },
            query_type="find",
            confidence=0.3,
            explanation="Fallback entity search using exact name matching",
            performance_hints=["Create index on name and canonical_name fields"],
            fallback_queries=[],
        )

    def _get_fallback_traversal_query(
        self, source_entities: List[str], max_depth: int
    ) -> MongoDBQueryResult:
        """Get fallback relationship traversal query."""
        return MongoDBQueryResult(
            query={
                "$graphLookup": {
                    "from": "relations",
                    "startWith": "$name",
                    "connectFromField": "target_id",
                    "connectToField": "source_id",
                    "as": "related_entities",
                    "maxDepth": max_depth,
                }
            },
            query_type="aggregation",
            confidence=0.3,
            explanation="Fallback traversal using $graphLookup",
            performance_hints=["Create compound index on source_id and target_id"],
            fallback_queries=[],
        )

    def _get_fallback_community_query(
        self, entity_names: List[str]
    ) -> MongoDBQueryResult:
        """Get fallback community summary query."""
        return MongoDBQueryResult(
            query={"$match": {"entities": {"$in": entity_names}}},
            query_type="find",
            confidence=0.3,
            explanation="Fallback community search using entity array matching",
            performance_hints=["Create index on entities array field"],
            fallback_queries=[],
        )

    def _get_fallback_query(self, query_type: str) -> MongoDBQueryResult:
        """Get generic fallback query."""
        return MongoDBQueryResult(
            query={"$match": {}},
            query_type="find",
            confidence=0.1,
            explanation=f"Generic fallback query for {query_type}",
            performance_hints=["Review query generation logic"],
            fallback_queries=[],
        )


class GraphRAGIndexManager:
    """
    Manages MongoDB indexes for optimal GraphRAG performance.
    """

    def __init__(self, db: Database):
        self.db = db

    def create_graphrag_indexes(self) -> Dict[str, Any]:
        """Create all necessary indexes for GraphRAG operations."""
        results = {}

        try:
            # Entities collection indexes
            entities = self.db.entities
            results["entities"] = self._create_entity_indexes(entities)

            # Relations collection indexes
            relations = self.db.relations
            results["relations"] = self._create_relation_indexes(relations)

            # Communities collection indexes
            communities = self.db.communities
            results["communities"] = self._create_community_indexes(communities)

            # Chunks collection indexes (for GraphRAG integration)
            chunks = self.db.chunks
            results["chunks"] = self._create_chunk_graphrag_indexes(chunks)

            logger.info("GraphRAG indexes created successfully")
            return results

        except Exception as e:
            logger.error(f"Error creating GraphRAG indexes: {e}")
            return {"error": str(e)}

    def _create_entity_indexes(self, collection: Collection) -> List[str]:
        """Create indexes for entities collection."""
        indexes_created = []

        try:
            # Compound index for name and type
            collection.create_index([("name", 1), ("type", 1), ("trust_score", -1)])
            indexes_created.append("name_type_trust")

            # Text index for name and canonical_name
            collection.create_index([("name", "text"), ("canonical_name", "text")])
            indexes_created.append("name_text")

            # Sparse index for centrality score
            collection.create_index([("centrality_score", -1)], sparse=True)
            indexes_created.append("centrality_sparse")

            # Index for trust score
            collection.create_index([("trust_score", -1)])
            indexes_created.append("trust_score")

        except Exception as e:
            logger.error(f"Error creating entity indexes: {e}")

        return indexes_created

    def _create_relation_indexes(self, collection: Collection) -> List[str]:
        """Create indexes for relations collection."""
        indexes_created = []

        try:
            # Compound index for bidirectional relationship lookup
            collection.create_index(
                [("source_id", 1), ("target_id", 1), ("confidence", -1)]
            )
            indexes_created.append("source_target_confidence")

            # Reverse compound index
            collection.create_index(
                [("target_id", 1), ("source_id", 1), ("confidence", -1)]
            )
            indexes_created.append("target_source_confidence")

            # Index for relationship type
            collection.create_index([("relationship_type", 1), ("confidence", -1)])
            indexes_created.append("relationship_type")

            # Index for confidence score
            collection.create_index([("confidence", -1)])
            indexes_created.append("confidence")

        except Exception as e:
            logger.error(f"Error creating relation indexes: {e}")

        return indexes_created

    def _create_community_indexes(self, collection: Collection) -> List[str]:
        """Create indexes for communities collection."""
        indexes_created = []

        try:
            # Index for entities array
            collection.create_index(
                [("entities", 1), ("level", 1), ("coherence_score", -1)]
            )
            indexes_created.append("entities_level_coherence")

            # Index for coherence score
            collection.create_index([("coherence_score", -1)])
            indexes_created.append("coherence_score")

            # Index for level
            collection.create_index([("level", 1)])
            indexes_created.append("level")

            # Text index for summary
            collection.create_index([("summary", "text")])
            indexes_created.append("summary_text")

        except Exception as e:
            logger.error(f"Error creating community indexes: {e}")

        return indexes_created

    def _create_chunk_graphrag_indexes(self, collection: Collection) -> List[str]:
        """Create GraphRAG-specific indexes for chunks collection."""
        indexes_created = []

        try:
            # Index for GraphRAG processing status
            collection.create_index([("graphrag_extraction.status", 1)])
            indexes_created.append("graphrag_extraction_status")

            # Index for entity mentions
            collection.create_index([("graphrag_extraction.entities", 1)])
            indexes_created.append("graphrag_entities")

            # Index for community assignment
            collection.create_index([("graphrag_communities.community_id", 1)])
            indexes_created.append("graphrag_communities")

        except Exception as e:
            logger.error(f"Error creating chunk GraphRAG indexes: {e}")

        return indexes_created


class GraphRAGQueryOptimizer:
    """
    Optimizes MongoDB queries for GraphRAG operations.
    """

    def __init__(self, db: Database):
        self.db = db

    def optimize_query(
        self, query: Dict[str, Any], collection_name: str
    ) -> Dict[str, Any]:
        """
        Optimize a MongoDB query for better performance.

        Args:
            query: MongoDB query to optimize
            collection_name: Name of the collection

        Returns:
            Optimized query with performance improvements
        """
        try:
            collection = self.db[collection_name]
            optimized_query = query.copy()

            # Add performance optimizations
            optimized_query = self._add_early_filtering(optimized_query)
            optimized_query = self._add_result_limiting(optimized_query)
            optimized_query = self._add_projection(optimized_query)
            optimized_query = self._add_query_hints(optimized_query, collection)

            logger.info(f"Query optimized for collection {collection_name}")
            return optimized_query

        except Exception as e:
            logger.error(f"Error optimizing query: {e}")
            return query

    def _add_early_filtering(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Add early filtering to reduce data processing."""
        if "$match" not in query:
            query["$match"] = {}

        # Add common filters for GraphRAG
        if "$match" in query:
            match_stage = query["$match"]

            # Add trust score filter if not present
            if "trust_score" not in match_stage:
                match_stage["trust_score"] = {"$gte": 0.3}

            # Add confidence filter for relations
            if "confidence" not in match_stage:
                match_stage["confidence"] = {"$gte": 0.5}

        return query

    def _add_result_limiting(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Add result limiting to prevent large result sets."""
        if "$limit" not in query:
            query["$limit"] = 100  # Default limit for GraphRAG queries

        return query

    def _add_projection(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Add projection to limit returned fields."""
        if "$project" not in query:
            query["$project"] = {
                "_id": 1,
                "name": 1,
                "type": 1,
                "description": 1,
                "trust_score": 1,
                "centrality_score": 1,
            }

        return query

    def _add_query_hints(
        self, query: Dict[str, Any], collection: Collection
    ) -> Dict[str, Any]:
        """Add query hints based on available indexes."""
        try:
            indexes = list(collection.list_indexes())
            index_names = [idx.get("name") for idx in indexes if idx.get("name")]

            # Add hint for most appropriate index
            if index_names:
                query["$hint"] = index_names[0]  # Use first available index

        except Exception as e:
            logger.warning(f"Could not add query hints: {e}")

        return query


class GraphRAGMongoDBQueryBuilder:
    """
    Builder for complex GraphRAG MongoDB queries.
    """

    def __init__(self, db: Database):
        self.db = db

    def build_hybrid_search_query(
        self,
        query_text: str,
        query_vector: List[float],
        entity_filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        Build a hybrid search query combining text and vector search.

        Args:
            query_text: Text query
            query_vector: Vector representation of query
            entity_filters: Optional entity filters
            limit: Maximum results to return

        Returns:
            MongoDB aggregation pipeline for hybrid search
        """
        pipeline = []

        # Add match stage for entity filters
        if entity_filters:
            pipeline.append({"$match": entity_filters})

        # Add vector search stage
        pipeline.append(
            {
                "$vectorSearch": {
                    "index": "vector_index",  # This should match your vector index name
                    "path": "embedding",
                    "queryVector": query_vector,
                    "numCandidates": limit * 10,
                    "limit": limit,
                }
            }
        )

        # Add text search stage
        pipeline.append(
            {
                "$search": {
                    "index": "text_index",  # This should match your text index name
                    "text": {
                        "query": query_text,
                        "path": ["name", "description", "summary"],
                    },
                }
            }
        )

        # Add projection stage
        pipeline.append(
            {
                "$project": {
                    "_id": 1,
                    "name": 1,
                    "type": 1,
                    "description": 1,
                    "trust_score": 1,
                    "centrality_score": 1,
                    "score": {"$meta": "searchScore"},
                }
            }
        )

        # Add limit stage
        pipeline.append({"$limit": limit})

        return {"pipeline": pipeline}

    def build_context_assembly_query(
        self,
        entity_ids: List[str],
        include_relationships: bool = True,
        include_communities: bool = True,
        max_context_length: int = 4000,
    ) -> Dict[str, Any]:
        """
        Build a query to assemble context from entities, relationships, and communities.

        Args:
            entity_ids: List of entity IDs to include
            include_relationships: Whether to include relationship information
            include_communities: Whether to include community summaries
            max_context_length: Maximum context length in characters

        Returns:
            MongoDB aggregation pipeline for context assembly
        """
        pipeline = []

        # Start with entities
        pipeline.append({"$match": {"_id": {"$in": entity_ids}}})

        # Add entity information
        pipeline.append(
            {
                "$project": {
                    "_id": 1,
                    "name": 1,
                    "type": 1,
                    "description": 1,
                    "trust_score": 1,
                    "centrality_score": 1,
                }
            }
        )

        # Add relationships if requested
        if include_relationships:
            pipeline.append(
                {
                    "$lookup": {
                        "from": "relations",
                        "localField": "_id",
                        "foreignField": "source_id",
                        "as": "outgoing_relations",
                    }
                }
            )

            pipeline.append(
                {
                    "$lookup": {
                        "from": "relations",
                        "localField": "_id",
                        "foreignField": "target_id",
                        "as": "incoming_relations",
                    }
                }
            )

        # Add communities if requested
        if include_communities:
            pipeline.append(
                {
                    "$lookup": {
                        "from": "communities",
                        "localField": "_id",
                        "foreignField": "entities",
                        "as": "communities",
                    }
                }
            )

        # Add context assembly stage
        pipeline.append(
            {
                "$addFields": {
                    "context": {
                        "$concat": [
                            "Name: ",
                            "$name",
                            "\n",
                            "Type: ",
                            "$type",
                            "\n",
                            "Description: ",
                            "$description",
                            "\n",
                            "Trust Score: ",
                            {"$toString": "$trust_score"},
                            "\n",
                            "Centrality Score: ",
                            {"$toString": "$centrality_score"},
                            "\n",
                        ]
                    }
                }
            }
        )

        return {"pipeline": pipeline}


class GraphRAGQueryMonitor:
    """
    Monitors and analyzes GraphRAG query performance.
    """

    def __init__(self, db: Database):
        self.db = db

    def analyze_query_performance(
        self, collection_name: str, query: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze the performance of a MongoDB query.

        Args:
            collection_name: Name of the collection
            query: MongoDB query to analyze

        Returns:
            Performance analysis results
        """
        try:
            collection = self.db[collection_name]

            # Execute query with explain
            explain_result = collection.find(query).explain("executionStats")

            # Extract performance metrics
            execution_stats = explain_result.get("executionStats", {})

            analysis = {
                "execution_time_ms": execution_stats.get("executionTimeMillis", 0),
                "documents_examined": execution_stats.get("totalDocsExamined", 0),
                "documents_returned": execution_stats.get("totalDocsReturned", 0),
                "indexes_used": execution_stats.get("totalKeysExamined", 0),
                "stage": explain_result.get("queryPlanner", {})
                .get("winningPlan", {})
                .get("stage", "unknown"),
                "index_name": self._get_index_name(explain_result),
                "optimization_suggestions": self._get_optimization_suggestions(
                    explain_result
                ),
            }

            logger.info(f"Query performance analyzed for {collection_name}")
            return analysis

        except Exception as e:
            logger.error(f"Error analyzing query performance: {e}")
            return {"error": str(e)}

    def _get_index_name(self, explain_result: Dict[str, Any]) -> Optional[str]:
        """Extract index name from explain result."""
        try:
            winning_plan = explain_result.get("queryPlanner", {}).get("winningPlan", {})
            return winning_plan.get("indexName")
        except Exception:
            return None

    def _get_optimization_suggestions(
        self, explain_result: Dict[str, Any]
    ) -> List[str]:
        """Generate optimization suggestions based on explain result."""
        suggestions = []

        try:
            execution_stats = explain_result.get("executionStats", {})

            # Check for collection scan
            if (
                execution_stats.get("totalDocsExamined", 0)
                > execution_stats.get("totalDocsReturned", 0) * 2
            ):
                suggestions.append(
                    "Consider adding an index to reduce document examination"
                )

            # Check execution time
            if execution_stats.get("executionTimeMillis", 0) > 100:
                suggestions.append(
                    "Query execution time is high, consider optimization"
                )

            # Check for index usage
            if not self._get_index_name(explain_result):
                suggestions.append(
                    "Query is not using an index, consider adding appropriate indexes"
                )

        except Exception as e:
            logger.warning(f"Could not generate optimization suggestions: {e}")

        return suggestions
