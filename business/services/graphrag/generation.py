"""
GraphRAG Generation Service

This module implements answer generation for GraphRAG queries using community
summaries and entity context to provide comprehensive answers.
"""

import logging
import time
from typing import Dict, List, Any, Optional
from openai import OpenAI
from core.models.graphrag import GraphRAGResponse, GraphRAGQuery
from business.services.graphrag.query import GraphRAGQueryProcessor
from business.services.graphrag.retrieval import GraphRAGRetrievalEngine

logger = logging.getLogger(__name__)


class GraphRAGGenerationService:
    """
    Service for generating answers to GraphRAG queries using retrieved context.
    """

    def __init__(
        self,
        llm_client: OpenAI,
        model_name: str = "gpt-4o-mini",
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
        query_processor: Optional[GraphRAGQueryProcessor] = None,
        retrieval_engine: Optional[GraphRAGRetrievalEngine] = None,
    ):
        """
        Initialize the GraphRAG Generation Service.

        Args:
            llm_client: OpenAI client instance
            model_name: Model to use for answer generation
            temperature: Temperature for LLM generation
            max_tokens: Maximum tokens for generation
            query_processor: Optional query processor instance
            retrieval_engine: Optional retrieval engine instance
        """
        self.llm_client = llm_client
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.query_processor = query_processor
        self.retrieval_engine = retrieval_engine

        # System prompt for answer generation
        self.generation_prompt = """
You are an expert assistant that provides comprehensive answers using GraphRAG (Graph-based Retrieval-Augmented Generation).

Your task is to answer user questions using the provided context from a knowledge graph and community summaries.

## Instructions:

1. **Answer Comprehensively**: Use all relevant information from the context to provide a complete answer
2. **Be Accurate**: Only use information explicitly provided in the context
3. **Be Clear**: Structure your answer logically and clearly
4. **Be Specific**: Include specific details, names, and relationships when available
5. **Be Helpful**: Provide actionable insights and explanations
6. **YouTube Context**: Consider that this information comes from YouTube content, so focus on educational and technical aspects

## Guidelines:
- Start with a direct answer to the question
- Provide supporting details from the context
- Explain relationships between entities when relevant
- Include specific examples or use cases when available
- If the context doesn't contain enough information, say so clearly
- Use the community summaries to provide broader context
- Reference specific entities and their relationships

## Output:
Provide a comprehensive answer that directly addresses the user's question using the provided context.
"""

        logger.info(f"Initialized GraphRAGGenerationService with model {model_name}")

    def generate_answer(
        self,
        query: str,
        context: str,
        entities: List[Dict[str, Any]],
        communities: List[Dict[str, Any]],
    ) -> str:
        """
        Generate an answer using the provided context.

        Args:
            query: User's question
            context: Retrieved context string
            entities: List of relevant entities
            communities: List of relevant communities

        Returns:
            Generated answer
        """
        logger.info(f"Generating answer for query: {query}")

        try:
            # Prepare the prompt
            prompt = f"""
Context Information:
{context}

Question: {query}

Please provide a comprehensive answer using the context information above.
"""

            response = self.llm_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.generation_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens or 2000,
            )

            answer = response.choices[0].message.content.strip()

            logger.info(f"Generated answer with {len(answer)} characters")
            return answer

        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return "I apologize, but I encountered an error while generating an answer. Please try again."

    def process_query_with_generation(
        self, query_text: str, db, use_traditional_rag: bool = False
    ) -> GraphRAGResponse:
        """
        Process a query and generate an answer using GraphRAG.

        Args:
            query_text: User's query
            db: MongoDB database instance
            use_traditional_rag: Whether to also include traditional RAG results

        Returns:
            GraphRAGResponse object
        """
        logger.info(f"Processing query with generation: {query_text}")

        start_time = time.time()

        try:
            # Initialize components if not provided
            if not self.query_processor:
                self.query_processor = GraphRAGQueryProcessor(
                    self.llm_client, self.model_name
                )

            if not self.retrieval_engine:
                self.retrieval_engine = GraphRAGRetrievalEngine(db)

            # Process query
            processed_query = self.query_processor.process_query(query_text, db)

            # Retrieve context
            retrieval_results = self.retrieval_engine.hybrid_graphrag_search(
                query_text, processed_query.extracted_entities
            )

            # Generate answer
            answer = self.generate_answer(
                query_text,
                retrieval_results["context"],
                retrieval_results["entities"],
                retrieval_results["communities"],
            )

            # Calculate confidence based on context quality
            confidence = self._calculate_answer_confidence(
                retrieval_results["entities"],
                retrieval_results["communities"],
                retrieval_results["context"],
            )

            processing_time = time.time() - start_time

            # Create response
            response = GraphRAGResponse(
                answer=answer,
                entities=retrieval_results["entities"],
                communities=retrieval_results["communities"],
                context_sources=[],  # Could be enhanced to track specific sources
                confidence=confidence,
                processing_time=processing_time,
            )

            logger.info(f"Query processing completed in {processing_time:.2f} seconds")
            return response

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error processing query: {e}")

            return GraphRAGResponse(
                answer=f"I apologize, but I encountered an error while processing your query: {str(e)}",
                entities=[],
                communities=[],
                context_sources=[],
                confidence=0.0,
                processing_time=processing_time,
            )

    def _calculate_answer_confidence(
        self,
        entities: List[Dict[str, Any]],
        communities: List[Dict[str, Any]],
        context: str,
    ) -> float:
        """
        Calculate confidence score for the generated answer.

        Args:
            entities: List of retrieved entities
            communities: List of retrieved communities
            context: Retrieved context string

        Returns:
            Confidence score between 0 and 1
        """
        # Base confidence on available information
        entity_score = min(len(entities) / 5.0, 1.0)  # Normalize to 5 entities
        community_score = min(len(communities) / 3.0, 1.0)  # Normalize to 3 communities
        context_score = min(len(context) / 2000.0, 1.0)  # Normalize to 2000 characters

        # Weight the scores
        confidence = 0.4 * entity_score + 0.3 * community_score + 0.3 * context_score

        return min(1.0, max(0.0, confidence))

    def generate_comparative_answer(
        self,
        query: str,
        entities: List[Dict[str, Any]],
        communities: List[Dict[str, Any]],
    ) -> str:
        """
        Generate a comparative answer when multiple entities are involved.

        Args:
            query: User's query
            entities: List of entities to compare
            communities: List of relevant communities

        Returns:
            Comparative answer
        """
        logger.info(f"Generating comparative answer for {len(entities)} entities")

        # Build comparison context
        comparison_context = "## Entity Comparison:\n"

        for i, entity in enumerate(entities[:5], 1):  # Limit to 5 entities
            comparison_context += f"\n{i}. **{entity['name']}** ({entity['type']}):\n"
            comparison_context += f"   - Description: {entity['description']}\n"
            comparison_context += (
                f"   - Trust Score: {entity.get('trust_score', 'N/A')}\n"
            )
            comparison_context += (
                f"   - Centrality: {entity.get('centrality_score', 'N/A')}\n"
            )

        # Add community context
        if communities:
            comparison_context += "\n## Community Context:\n"
            for community in communities:
                comparison_context += f"\n### {community['title']}\n"
                comparison_context += f"{community['summary']}\n"

        # Generate comparative answer
        prompt = f"""
Context Information:
{comparison_context}

Question: {query}

Please provide a comparative analysis using the entity information above.
"""

        try:
            response = self.llm_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.generation_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens or 2000,
            )

            answer = response.choices[0].message.content.strip()
            logger.info(f"Generated comparative answer with {len(answer)} characters")
            return answer

        except Exception as e:
            logger.error(f"Error generating comparative answer: {e}")
            return "I apologize, but I encountered an error while generating a comparative answer."

    def generate_explanatory_answer(
        self,
        query: str,
        entities: List[Dict[str, Any]],
        communities: List[Dict[str, Any]],
    ) -> str:
        """
        Generate an explanatory answer focusing on relationships and context.

        Args:
            query: User's query
            entities: List of relevant entities
            communities: List of relevant communities

        Returns:
            Explanatory answer
        """
        logger.info(f"Generating explanatory answer for query: {query}")

        # Build explanatory context
        explanatory_context = "## Entity Relationships:\n"

        for entity in entities[:5]:
            explanatory_context += f"\n**{entity['name']}** ({entity['type']}):\n"
            explanatory_context += f"- {entity['description']}\n"
            explanatory_context += (
                f"- Trust Score: {entity.get('trust_score', 'N/A')}\n"
            )

        # Add community context for broader explanation
        if communities:
            explanatory_context += "\n## Broader Context:\n"
            for community in communities:
                explanatory_context += f"\n### {community['title']}\n"
                explanatory_context += f"{community['summary']}\n"

        # Generate explanatory answer
        prompt = f"""
Context Information:
{explanatory_context}

Question: {query}

Please provide a detailed explanation using the context information above.
Focus on relationships, causes, and broader context.
"""

        try:
            response = self.llm_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.generation_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens or 2000,
            )

            answer = response.choices[0].message.content.strip()
            logger.info(f"Generated explanatory answer with {len(answer)} characters")
            return answer

        except Exception as e:
            logger.error(f"Error generating explanatory answer: {e}")
            return "I apologize, but I encountered an error while generating an explanatory answer."

    def get_generation_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the generation service.

        Returns:
            Dictionary containing generation statistics
        """
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "has_query_processor": self.query_processor is not None,
            "has_retrieval_engine": self.retrieval_engine is not None,
        }
