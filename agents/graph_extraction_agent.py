"""
Graph Extraction Agent

This module implements LLM-based entity and relationship extraction from text chunks.
Uses OpenAI's structured output capabilities with Pydantic models for reliable extraction.
"""

import logging
import time
from typing import Dict, List, Any, Optional
from openai import OpenAI
from core.graphrag_models import (
    KnowledgeModel,
    EntityModel,
    RelationshipModel,
    EntityType,
)

logger = logging.getLogger(__name__)


class GraphExtractionAgent:
    """
    Agent for extracting entities and relationships from text chunks using LLM.
    """

    def __init__(
        self,
        llm_client: OpenAI,
        model_name: str = "gpt-4o-mini",
        temperature: float = 0.1,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """
        Initialize the Graph Extraction Agent.

        Args:
            llm_client: OpenAI client instance
            model_name: Model to use for extraction
            temperature: Temperature for LLM generation
            max_retries: Maximum number of retries for failed extractions
            retry_delay: Delay between retries in seconds
        """
        self.llm_client = llm_client
        self.model_name = model_name
        self.temperature = temperature
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # System prompt for entity and relationship extraction
        self.system_prompt = """
        You are an expert at extracting entities and relationships from YouTube content transcripts.

        Your task is to identify all entities and their relationships from the given text chunk.

        ## Instructions:

        1. **Entity Extraction**: Identify all entities in the text and classify them into these types:
        - PERSON: People, individuals, characters
        - ORGANIZATION: Companies, institutions, groups, teams
        - TECHNOLOGY: Software, tools, frameworks, programming languages, platforms
        - CONCEPT: Ideas, theories, methodologies, principles
        - LOCATION: Places, cities, countries, venues
        - EVENT: Meetings, conferences, launches, incidents
        - OTHER: Anything else that doesn't fit the above categories

        2. **Relationship Extraction**: Extract ALL relationship types between each entity pair:
        - **Multiple Types**: If Entity A relates to Entity B, extract ALL applicable relationships
          * Example: "Algorithm uses Data Structure" → extract: 'uses', 'applies_to', 'depends_on'
          * Example: "Person teaches Concept" → extract: 'teaches', 'explains', 'demonstrates'
        - **Direct and Indirect**: Include both explicit and strongly implied relationships
        - **Hierarchical**: Extract parent-child, part-of, is-a relationships
          * "Sorting Algorithm" is a type of "Algorithm" → 'is_a', 'subtype_of'
          * "Step" is part of "Algorithm" → 'part_of', 'component_of'
        - **Bidirectional**: Consider reverse relationships when applicable
          * "Algorithm uses Data Structure" ↔ "Data Structure used_by Algorithm"
          * "Person teaches Concept" ↔ "Concept taught_by Person"
        - **Semantic Relationships**: Include conceptual connections
          * "Algorithm requires Data Structure" → 'requires', 'needs'
          * "Concept related_to Concept" → 'related_to', 'similar_to'
        
        **Goal**: Extract 2-5 relationship types per connected entity pair for rich graph connectivity

        3. **Quality Guidelines**:
        - Extract only entities that are clearly mentioned in the text
        - Provide comprehensive descriptions for each entity
        - Be specific about relationship types (e.g., "works_at", "uses", "located_in")
        - Assign confidence scores based on clarity of mention
        - Avoid extracting pronouns or vague references

        4. **YouTube Content Considerations**:
        - Focus on technical content, tutorials, and educational material
        - Extract technology stacks, programming concepts, and tools
        - Identify people mentioned (instructors, developers, experts)
        - Capture organizational relationships and affiliations

        ## Output Format:
        Return a structured response with entities and relationships as specified in the KnowledgeModel schema.
        """

    def extract_from_chunk(self, chunk: Dict[str, Any]) -> Optional[KnowledgeModel]:
        """
        Extract entities and relationships from a single text chunk.

        Args:
            chunk: Dictionary containing chunk data with 'text' field

        Returns:
            KnowledgeModel containing extracted entities and relationships, or None if extraction fails
        """
        if not chunk.get("chunk_text") or not chunk["chunk_text"].strip():
            logger.warning(
                f"Empty or missing text in chunk {chunk.get('chunk_id', 'unknown')}"
            )
            return None

        text = chunk["chunk_text"].strip()
        chunk_id = chunk.get("chunk_id", "unknown")

        logger.debug(f"Extracting entities from chunk {chunk_id} (length: {len(text)})")

        for attempt in range(self.max_retries):
            try:
                response = self.llm_client.beta.chat.completions.parse(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": f"Text: {text}"},
                    ],
                    response_format=KnowledgeModel,
                    temperature=self.temperature,
                    max_tokens=4000,
                )

                knowledge_model = response.choices[0].message.parsed

                # Validate and enhance the extracted knowledge
                validated_model = self._validate_and_enhance(knowledge_model, chunk)

                logger.debug(
                    f"Successfully extracted {len(validated_model.entities)} entities "
                    f"and {len(validated_model.relationships)} relationships from chunk {chunk_id}"
                )

                return validated_model

            except Exception as e:
                logger.warning(
                    f"Extraction attempt {attempt + 1} failed for chunk {chunk_id}: {e}"
                )

                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2**attempt))  # Exponential backoff
                else:
                    logger.error(f"All extraction attempts failed for chunk {chunk_id}")
                    return None

        return None

    def _validate_and_enhance(
        self, knowledge_model: KnowledgeModel, chunk: Dict[str, Any]
    ) -> KnowledgeModel:
        """
        Validate and enhance the extracted knowledge model.

        Args:
            knowledge_model: Extracted knowledge model
            chunk: Original chunk data

        Returns:
            Validated and enhanced knowledge model
        """
        # Filter out low-confidence entities
        filtered_entities = [
            entity
            for entity in knowledge_model.entities
            if entity.confidence >= 0.3  # Minimum confidence threshold
        ]

        # Filter out low-confidence relationships
        filtered_relationships = [
            rel
            for rel in knowledge_model.relationships
            if rel.confidence >= 0.3  # Minimum confidence threshold
        ]

        # Validate relationships have valid entities
        valid_entity_names = {entity.name for entity in filtered_entities}
        validated_relationships = []

        for rel in filtered_relationships:
            if (
                rel.source_entity.name in valid_entity_names
                and rel.target_entity.name in valid_entity_names
            ):
                validated_relationships.append(rel)
            else:
                logger.debug(
                    f"Skipping relationship {rel.source_entity.name} -> {rel.target_entity.name} "
                    f"due to missing entities"
                )

        # Add chunk metadata to entities
        for entity in filtered_entities:
            entity.confidence = max(entity.confidence, 0.1)  # Ensure minimum confidence

        # Add chunk metadata to relationships
        for rel in validated_relationships:
            rel.confidence = max(rel.confidence, 0.1)  # Ensure minimum confidence

        return KnowledgeModel(
            entities=filtered_entities, relationships=validated_relationships
        )

    def extract_batch(
        self, chunks: List[Dict[str, Any]]
    ) -> List[Optional[KnowledgeModel]]:
        """
        Extract entities and relationships from a batch of chunks.

        Args:
            chunks: List of chunk dictionaries

        Returns:
            List of KnowledgeModel objects (or None for failed extractions)
        """
        logger.info(f"Extracting entities from batch of {len(chunks)} chunks")

        results = []
        for i, chunk in enumerate(chunks):
            logger.debug(f"Processing chunk {i + 1}/{len(chunks)}")
            result = self.extract_from_chunk(chunk)
            results.append(result)

        successful_extractions = sum(1 for r in results if r is not None)
        logger.info(
            f"Batch extraction completed: {successful_extractions}/{len(chunks)} successful"
        )

        return results

    def get_extraction_stats(
        self, results: List[Optional[KnowledgeModel]]
    ) -> Dict[str, Any]:
        """
        Get statistics about extraction results.

        Args:
            results: List of extraction results

        Returns:
            Dictionary containing extraction statistics
        """
        successful_results = [r for r in results if r is not None]

        if not successful_results:
            return {
                "total_chunks": len(results),
                "successful_extractions": 0,
                "total_entities": 0,
                "total_relationships": 0,
                "avg_entities_per_chunk": 0,
                "avg_relationships_per_chunk": 0,
                "entity_type_distribution": {},
                "success_rate": 0.0,
            }

        total_entities = sum(len(r.entities) for r in successful_results)
        total_relationships = sum(len(r.relationships) for r in successful_results)

        # Calculate entity type distribution
        entity_type_counts = {}
        for result in successful_results:
            for entity in result.entities:
                entity_type_counts[entity.type] = (
                    entity_type_counts.get(entity.type, 0) + 1
                )

        return {
            "total_chunks": len(results),
            "successful_extractions": len(successful_results),
            "total_entities": total_entities,
            "total_relationships": total_relationships,
            "avg_entities_per_chunk": total_entities / len(successful_results),
            "avg_relationships_per_chunk": total_relationships
            / len(successful_results),
            "entity_type_distribution": entity_type_counts,
            "success_rate": len(successful_results) / len(results),
        }
