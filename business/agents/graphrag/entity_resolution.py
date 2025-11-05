"""
Entity Resolution Agent

This module implements multi-strategy entity resolution to canonicalize entities
extracted from different chunks. It groups similar entities and resolves their
descriptions using LLM-based summarization.
"""

import logging
from core.libraries.retry import retry_llm_call
from core.libraries.logging import log_exception
import hashlib
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict
from difflib import SequenceMatcher
from openai import OpenAI
from core.models.graphrag import ResolvedEntity, EntityModel, EntityType

logger = logging.getLogger(__name__)


class EntityResolutionAgent:
    """
    Agent for resolving and canonicalizing entities across multiple chunks.
    """

    def __init__(
        self,
        llm_client: OpenAI,
        model_name: str = "gpt-4o-mini",
        temperature: float = 0.1,
        similarity_threshold: float = 0.85,
    ):
        """
        Initialize the Entity Resolution Agent.

        Args:
            llm_client: OpenAI client instance
            model_name: Model to use for resolution
            temperature: Temperature for LLM generation
            similarity_threshold: Threshold for entity similarity matching
        """
        self.llm_client = llm_client
        self.model_name = model_name
        self.temperature = temperature
        self.similarity_threshold = similarity_threshold

        # System prompt for entity description resolution
        self.resolution_prompt = """
        You are an expert at resolving and summarizing entity descriptions from multiple sources.

        Your task is to create a comprehensive, coherent description by combining multiple descriptions of the same entity.

        ## Instructions:

        1. **Combine Information**: Merge all provided descriptions into a single, comprehensive description
        2. **Resolve Contradictions**: If descriptions contradict each other, choose the most accurate or recent information
        3. **Maintain Context**: Keep the entity name and context clear throughout the description
        4. **Be Concise**: Create a well-structured description that captures all important aspects
        5. **Third Person**: Write in third person perspective
        6. **YouTube Context**: Consider that this is from YouTube content, so focus on technical and educational aspects

        ## Guidelines:
        - Include all unique information from the descriptions
        - Remove redundant or repetitive information
        - Maintain technical accuracy
        - Keep the description informative but concise
        - Ensure the description flows naturally

        ## Output:
        Provide only the resolved description, nothing else.
        """

    def resolve_entities(
        self, extracted_data: List[Dict[str, Any]]
    ) -> List[ResolvedEntity]:
        """
        Resolve entities across all extracted data.

        Args:
            extracted_data: List of extraction results from chunks

        Returns:
            List of resolved entities
        """
        logger.info(f"Resolving entities from {len(extracted_data)} extraction results")

        # Group entities by normalized name
        entity_groups = self._group_entities_by_name(extracted_data)

        logger.info(f"Found {len(entity_groups)} unique entity groups")

        resolved_entities = []

        for normalized_name, entity_group in entity_groups.items():
            try:
                resolved_entity = self._resolve_entity_group(
                    normalized_name, entity_group
                )
                if resolved_entity:
                    resolved_entities.append(resolved_entity)
            except Exception as e:
                logger.error(f"Failed to resolve entity group '{normalized_name}': {e}")
                continue

        logger.info(f"Successfully resolved {len(resolved_entities)} entities")
        return resolved_entities

    def _group_entities_by_name(
        self, extracted_data: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group entities by normalized name using multiple strategies.

        Args:
            extracted_data: List of extraction results

        Returns:
            Dictionary mapping normalized names to entity groups
        """
        entity_groups = defaultdict(list)

        for extraction in extracted_data:
            if not extraction or "entities" not in extraction:
                continue

            for entity_data in extraction["entities"]:
                entity_name = entity_data["name"]
                normalized_name = self._normalize_entity_name(entity_name)

                # Add source information
                entity_with_source = entity_data.copy()
                entity_with_source["source_chunk"] = extraction.get(
                    "chunk_id", "unknown"
                )

                entity_groups[normalized_name].append(entity_with_source)

        return dict(entity_groups)

    def _normalize_entity_name(self, name: str) -> str:
        """
        Normalize entity name for grouping.

        Args:
            name: Original entity name

        Returns:
            Normalized entity name
        """
        # Convert to lowercase and strip whitespace
        normalized = name.lower().strip()

        # Remove common prefixes/suffixes
        prefixes_to_remove = ["mr.", "ms.", "dr.", "prof.", "the "]
        suffixes_to_remove = [" inc.", " corp.", " ltd.", " llc.", " co."]

        for prefix in prefixes_to_remove:
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix) :].strip()

        for suffix in suffixes_to_remove:
            if normalized.endswith(suffix):
                normalized = normalized[: -len(suffix)].strip()

        return normalized

    def _resolve_entity_group(
        self, normalized_name: str, entity_group: List[Dict[str, Any]]
    ) -> Optional[ResolvedEntity]:
        """
        Resolve a group of entities into a single canonical entity.

        Args:
            normalized_name: Normalized name for the entity group
            entity_group: List of entity instances to resolve

        Returns:
            Resolved entity or None if resolution fails
        """
        if not entity_group:
            return None

        # If only one entity, use it directly
        if len(entity_group) == 1:
            entity_data = entity_group[0]
            return self._create_resolved_entity_from_single(
                entity_data, normalized_name
            )

        # Multiple entities - need to resolve descriptions
        return self._resolve_multiple_entities(normalized_name, entity_group)

    def _create_resolved_entity_from_single(
        self, entity_data: Dict[str, Any], normalized_name: str
    ) -> ResolvedEntity:
        """
        Create a resolved entity from a single entity instance.

        Args:
            entity_data: Single entity data
            normalized_name: Normalized name

        Returns:
            Resolved entity
        """
        canonical_name = entity_data["name"]
        entity_id = ResolvedEntity.generate_entity_id(canonical_name)

        return ResolvedEntity(
            entity_id=entity_id,
            canonical_name=canonical_name,
            name=entity_data["name"],
            type=EntityType(entity_data["type"]),
            description=entity_data["description"],
            confidence=entity_data["confidence"],
            source_count=1,
            resolution_methods=["single_instance"],
            aliases=[entity_data["name"]],
        )

    def _resolve_multiple_entities(
        self, normalized_name: str, entity_group: List[Dict[str, Any]]
    ) -> Optional[ResolvedEntity]:
        """
        Resolve multiple entity instances into a single canonical entity.

        Args:
            normalized_name: Normalized name for the entity group
            entity_group: List of entity instances

        Returns:
            Resolved entity or None if resolution fails
        """
        # Determine canonical name (most common or highest confidence)
        canonical_name = self._determine_canonical_name(entity_group)

        # Determine entity type (most common)
        entity_type = self._determine_entity_type(entity_group)

        # Resolve description using LLM
        resolved_description = self._resolve_descriptions(entity_group, canonical_name)

        if not resolved_description:
            logger.warning(
                f"Failed to resolve description for entity '{canonical_name}'"
            )
            return None

        # Calculate overall confidence
        overall_confidence = self._calculate_overall_confidence(entity_group)

        # Generate entity ID
        entity_id = ResolvedEntity.generate_entity_id(canonical_name)

        # Collect aliases
        aliases = list(set(entity["name"] for entity in entity_group))

        # Determine resolution methods used
        resolution_methods = ["llm_summary", "name_grouping"]
        if len(entity_group) > 1:
            resolution_methods.append("multi_instance")

        return ResolvedEntity(
            entity_id=entity_id,
            canonical_name=canonical_name,
            name=canonical_name,
            type=entity_type,
            description=resolved_description,
            confidence=overall_confidence,
            source_count=len(entity_group),
            resolution_methods=resolution_methods,
            aliases=aliases,
        )

    def _determine_canonical_name(self, entity_group: List[Dict[str, Any]]) -> str:
        """
        Determine the canonical name for a group of entities.

        Args:
            entity_group: List of entity instances

        Returns:
            Canonical name
        """
        # Count name occurrences
        name_counts = defaultdict(int)
        name_confidences = defaultdict(list)

        for entity in entity_group:
            name = entity["name"]
            confidence = entity["confidence"]
            name_counts[name] += 1
            name_confidences[name].append(confidence)

        # Choose name with highest count, then highest average confidence
        best_name = max(
            name_counts.keys(),
            key=lambda name: (
                name_counts[name],
                sum(name_confidences[name]) / len(name_confidences[name]),
            ),
        )

        return best_name

    def _determine_entity_type(self, entity_group: List[Dict[str, Any]]) -> EntityType:
        """
        Determine the entity type for a group of entities.

        Args:
            entity_group: List of entity instances

        Returns:
            Most common entity type
        """
        type_counts = defaultdict(int)

        for entity in entity_group:
            entity_type = entity["type"]
            type_counts[entity_type] += 1

        # Return most common type, defaulting to OTHER if tie
        most_common_type = max(type_counts.keys(), key=lambda t: type_counts[t])
        return EntityType(most_common_type)

    def _resolve_descriptions(
        self, entity_group: List[Dict[str, Any]], entity_name: str
    ) -> Optional[str]:
        """
        Resolve entity descriptions using LLM summarization.

        Args:
            entity_group: List of entity instances
            entity_name: Name of the entity

        Returns:
            Resolved description or None if resolution fails
        """
        descriptions = [entity["description"] for entity in entity_group]

        if len(descriptions) == 1:
            return descriptions[0]

        # Combine descriptions for LLM processing
        combined_descriptions = "\n\n".join(
            [f"Description {i+1}: {desc}" for i, desc in enumerate(descriptions)]
        )

        try:
            resolved_description = self._resolve_with_llm(
                entity_name, combined_descriptions
            )

            if len(resolved_description) < 10:
                logger.warning(
                    f"Resolved description too short for entity '{entity_name}'"
                )
                return None

            return resolved_description

        except Exception as e:
            log_exception(
                logger,
                f"All description resolution attempts failed for entity '{entity_name}'",
                e,
            )
            return None

    @retry_llm_call(max_attempts=3)
    def _resolve_with_llm(self, entity_name: str, combined_descriptions: str) -> str:
        """Resolve entity descriptions with automatic retry.

        Args:
            entity_name: Name of the entity
            combined_descriptions: Combined descriptions to resolve

        Returns:
            Resolved description
        """
        response = self.llm_client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.resolution_prompt},
                {
                    "role": "user",
                    "content": f"Entity: {entity_name}\n\nDescriptions:\n{combined_descriptions}",
                },
            ],
            temperature=self.temperature,
            max_tokens=1000,
        )

        return response.choices[0].message.content.strip()

    def _calculate_overall_confidence(
        self, entity_group: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate overall confidence for a group of entities.

        Args:
            entity_group: List of entity instances

        Returns:
            Overall confidence score
        """
        confidences = [entity["confidence"] for entity in entity_group]

        # Use weighted average based on source count
        total_weight = len(confidences)
        weighted_sum = sum(confidences)

        return weighted_sum / total_weight if total_weight > 0 else 0.0

    def get_resolution_stats(
        self, resolved_entities: List[ResolvedEntity]
    ) -> Dict[str, Any]:
        """
        Get statistics about entity resolution.

        Args:
            resolved_entities: List of resolved entities

        Returns:
            Dictionary containing resolution statistics
        """
        if not resolved_entities:
            return {
                "total_entities": 0,
                "single_instance_entities": 0,
                "multi_instance_entities": 0,
                "avg_source_count": 0,
                "avg_confidence": 0,
                "entity_type_distribution": {},
                "resolution_method_distribution": {},
            }

        single_instance = sum(1 for e in resolved_entities if e.source_count == 1)
        multi_instance = len(resolved_entities) - single_instance

        avg_source_count = sum(e.source_count for e in resolved_entities) / len(
            resolved_entities
        )
        avg_confidence = sum(e.confidence for e in resolved_entities) / len(
            resolved_entities
        )

        # Entity type distribution
        type_counts = defaultdict(int)
        for entity in resolved_entities:
            type_counts[entity.type.value] += 1

        # Resolution method distribution
        method_counts = defaultdict(int)
        for entity in resolved_entities:
            for method in entity.resolution_methods:
                method_counts[method] += 1

        return {
            "total_entities": len(resolved_entities),
            "single_instance_entities": single_instance,
            "multi_instance_entities": multi_instance,
            "avg_source_count": avg_source_count,
            "avg_confidence": avg_confidence,
            "entity_type_distribution": dict(type_counts),
            "resolution_method_distribution": dict(method_counts),
        }
