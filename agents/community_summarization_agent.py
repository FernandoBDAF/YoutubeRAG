"""
Community Summarization Agent

This module implements community summarization using LLM to generate
comprehensive summaries of detected communities.
"""

import logging
import time
from typing import Dict, List, Any, Optional
from openai import OpenAI
from core.graphrag_models import ResolvedEntity, ResolvedRelationship, CommunitySummary

logger = logging.getLogger(__name__)


class CommunitySummarizationAgent:
    """
    Agent for generating summaries of detected communities using LLM.
    """

    def __init__(
        self,
        llm_client: OpenAI,
        model_name: str = "gpt-4o-mini",
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
        max_summary_length: int = 2000,
        min_summary_length: int = 100,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """
        Initialize the Community Summarization Agent.

        Args:
            llm_client: OpenAI client instance
            model_name: Model to use for summarization
            temperature: Temperature for LLM generation
            max_tokens: Maximum tokens for generation
            max_summary_length: Maximum length of summary
            min_summary_length: Minimum length of summary
            max_retries: Maximum number of retries for failed summarizations
            retry_delay: Delay between retries in seconds
        """
        self.llm_client = llm_client
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_summary_length = max_summary_length
        self.min_summary_length = min_summary_length
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # System prompt for community summarization
        self.summarization_prompt = """
        You are an expert at creating comprehensive summaries of communities of related entities from YouTube content.

        Your task is to create a clear, informative summary that captures the key aspects of a community of entities and their relationships.

        ## Instructions:

        1. **Community Overview**: Provide a clear overview of what the community represents
        2. **Key Entities**: Identify and describe the main entities in the community
        3. **Relationships**: Explain the key relationships between entities
        4. **Context**: Provide context about how these entities relate to YouTube content
        5. **Technical Focus**: Focus on technical, educational, or informational aspects
        6. **Clarity**: Write in clear, accessible language
        7. **Completeness**: Include all important information from the provided data

        ## Guidelines:
        - Start with a brief title that captures the community's essence
        - Use bullet points or structured format for clarity
        - Include specific entity names and relationship types
        - Explain the significance of the relationships
        - Keep the summary informative but concise
        - Focus on actionable insights

        ## Output Format:
        Provide a structured summary with:
        - Title: Brief descriptive title
        - Summary: Comprehensive summary paragraph
        - Key Entities: List of main entities
        - Key Relationships: List of important relationships
        - Context: How this relates to YouTube content

        ## Output:
        Provide only the structured summary, nothing else.
        """

        logger.info(f"Initialized CommunitySummarizationAgent with model {model_name}")

    def summarize_communities(
        self,
        communities: Dict[int, Dict[str, Any]],
        entities: List[ResolvedEntity],
        relationships: List[ResolvedRelationship],
    ) -> Dict[str, CommunitySummary]:
        """
        Generate summaries for all detected communities.

        Args:
            communities: Organized communities by level
            entities: List of resolved entities
            relationships: List of resolved relationships

        Returns:
            Dictionary mapping community IDs to CommunitySummary objects
        """
        logger.info(
            f"Summarizing {sum(len(level_communities) for level_communities in communities.values())} communities"
        )

        entity_map = {entity.entity_id: entity for entity in entities}
        relationship_map = {rel.relationship_id: rel for rel in relationships}

        community_summaries = {}

        for level, level_communities in communities.items():
            for community_id, community_data in level_communities.items():
                try:
                    summary = self._summarize_single_community(
                        community_data, entity_map, relationship_map
                    )
                    if summary:
                        community_summaries[community_id] = summary
                except Exception as e:
                    logger.error(f"Failed to summarize community {community_id}: {e}")
                    continue

        logger.info(f"Successfully summarized {len(community_summaries)} communities")
        return community_summaries

    def _summarize_single_community(
        self,
        community_data: Dict[str, Any],
        entity_map: Dict[str, ResolvedEntity],
        relationship_map: Dict[str, ResolvedRelationship],
    ) -> Optional[CommunitySummary]:
        """
        Generate summary for a single community.

        Args:
            community_data: Community data
            entity_map: Map of entity IDs to entities
            relationship_map: Map of relationship IDs to relationships

        Returns:
            CommunitySummary object or None if summarization fails
        """
        community_id = community_data["community_id"]
        level = community_data["level"]

        # Get entities and relationships for this community
        community_entities = []
        community_relationships = []

        for entity_id in community_data["entities"]:
            if entity_id in entity_map:
                community_entities.append(entity_map[entity_id])

        for rel_id in community_data["relationships"]:
            if rel_id in relationship_map:
                community_relationships.append(relationship_map[rel_id])

        if not community_entities:
            logger.warning(f"No entities found for community {community_id}")
            return None

        # Generate summary using LLM
        summary_text = self._generate_summary_text(
            community_entities, community_relationships
        )

        if not summary_text:
            logger.warning(f"Failed to generate summary for community {community_id}")
            return None

        # Create CommunitySummary object
        return CommunitySummary(
            community_id=community_id,
            level=level,
            title=self._extract_title(summary_text),
            summary=summary_text,
            entities=community_data["entities"],
            entity_count=community_data["entity_count"],
            relationship_count=community_data["relationship_count"],
            coherence_score=community_data["coherence_score"],
        )

    def _generate_summary_text(
        self, entities: List[ResolvedEntity], relationships: List[ResolvedRelationship]
    ) -> Optional[str]:
        """
        Generate summary text using LLM.

        Args:
            entities: Entities in the community
            relationships: Relationships in the community

        Returns:
            Generated summary text or None if generation fails
        """
        # Prepare entity information
        entities_text = "\n".join(
            [
                f"- {entity.name} ({entity.type.value}): {entity.description}"
                for entity in entities
            ]
        )

        # Prepare relationship information
        relationships_text = "\n".join(
            [
                f"- {rel.subject_id} -> {rel.object_id} ({rel.predicate}): {rel.description}"
                for rel in relationships
            ]
        )

        # Create input text
        input_text = f"""
        Entities in this community:
        {entities_text}

        Relationships in this community:
        {relationships_text}

        Please create a comprehensive summary of this community.
        """

        for attempt in range(self.max_retries):
            try:
                response = self.llm_client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": self.summarization_prompt},
                        {"role": "user", "content": input_text},
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens or 2000,
                )

                summary_text = response.choices[0].message.content.strip()

                if len(summary_text) < self.min_summary_length:
                    logger.warning(
                        f"Generated summary too short: {len(summary_text)} characters"
                    )
                    continue

                if len(summary_text) > self.max_summary_length:
                    summary_text = summary_text[: self.max_summary_length] + "..."

                return summary_text

            except Exception as e:
                logger.warning(f"Summary generation attempt {attempt + 1} failed: {e}")

                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2**attempt))
                else:
                    logger.error(f"All summary generation attempts failed")
                    return None

        return None

    def _extract_title(self, summary_text: str) -> str:
        """
        Extract title from summary text.

        Args:
            summary_text: Full summary text

        Returns:
            Extracted title
        """
        lines = summary_text.split("\n")

        # Look for title patterns
        for line in lines:
            line = line.strip()
            if line.startswith("Title:"):
                return line[6:].strip()
            elif line.startswith("#"):
                return line[1:].strip()
            elif len(line) < 100 and line.endswith(":"):
                return line[:-1].strip()

        # Fallback: use first line if it's short enough
        first_line = lines[0].strip()
        if len(first_line) < 100:
            return first_line

        # Final fallback: truncate first line
        return first_line[:50] + "..." if len(first_line) > 50 else first_line

    def summarize_large_community(
        self,
        community_data: Dict[str, Any],
        entity_map: Dict[str, ResolvedEntity],
        relationship_map: Dict[str, ResolvedRelationship],
        max_entities: int = 20,
        max_relationships: int = 30,
    ) -> Optional[CommunitySummary]:
        """
        Generate summary for a large community using hierarchical approach.

        Args:
            community_data: Community data
            entity_map: Map of entity IDs to entities
            relationship_map: Map of relationship IDs to relationships
            max_entities: Maximum entities to include in summary
            max_relationships: Maximum relationships to include in summary

        Returns:
            CommunitySummary object or None if summarization fails
        """
        community_id = community_data["community_id"]
        level = community_data["level"]

        # Get entities and relationships for this community
        community_entities = []
        community_relationships = []

        for entity_id in community_data["entities"]:
            if entity_id in entity_map:
                community_entities.append(entity_map[entity_id])

        for rel_id in community_data["relationships"]:
            if rel_id in relationship_map:
                community_relationships.append(relationship_map[rel_id])

        if not community_entities:
            return None

        # Select most important entities and relationships
        selected_entities = self._select_important_entities(
            community_entities, max_entities
        )
        selected_relationships = self._select_important_relationships(
            community_relationships, max_relationships
        )

        # Generate summary with selected items
        summary_text = self._generate_summary_text(
            selected_entities, selected_relationships
        )

        if not summary_text:
            return None

        # Add note about truncation
        if (
            len(community_entities) > max_entities
            or len(community_relationships) > max_relationships
        ):
            summary_text += f"\n\nNote: This summary covers {len(selected_entities)} of {len(community_entities)} entities and {len(selected_relationships)} of {len(community_relationships)} relationships."

        return CommunitySummary(
            community_id=community_id,
            level=level,
            title=self._extract_title(summary_text),
            summary=summary_text,
            entities=community_data["entities"],
            entity_count=community_data["entity_count"],
            relationship_count=community_data["relationship_count"],
            coherence_score=community_data["coherence_score"],
        )

    def _select_important_entities(
        self, entities: List[ResolvedEntity], max_count: int
    ) -> List[ResolvedEntity]:
        """
        Select most important entities for summarization.

        Args:
            entities: List of entities
            max_count: Maximum number of entities to select

        Returns:
            List of selected entities
        """
        if len(entities) <= max_count:
            return entities

        # Sort by confidence and source count
        sorted_entities = sorted(
            entities, key=lambda e: (e.confidence, e.source_count), reverse=True
        )

        return sorted_entities[:max_count]

    def _select_important_relationships(
        self, relationships: List[ResolvedRelationship], max_count: int
    ) -> List[ResolvedRelationship]:
        """
        Select most important relationships for summarization.

        Args:
            relationships: List of relationships
            max_count: Maximum number of relationships to select

        Returns:
            List of selected relationships
        """
        if len(relationships) <= max_count:
            return relationships

        # Sort by confidence and source count
        sorted_relationships = sorted(
            relationships, key=lambda r: (r.confidence, r.source_count), reverse=True
        )

        return sorted_relationships[:max_count]

    def get_summarization_stats(
        self, summaries: Dict[str, CommunitySummary]
    ) -> Dict[str, Any]:
        """
        Get statistics about community summarization.

        Args:
            summaries: Dictionary of community summaries

        Returns:
            Dictionary containing summarization statistics
        """
        if not summaries:
            return {
                "total_summaries": 0,
                "avg_summary_length": 0,
                "level_distribution": {},
                "coherence_distribution": {},
            }

        summary_lengths = [len(summary.summary) for summary in summaries.values()]
        avg_summary_length = sum(summary_lengths) / len(summary_lengths)

        # Level distribution
        level_distribution = {}
        for summary in summaries.values():
            level = summary.level
            level_distribution[level] = level_distribution.get(level, 0) + 1

        # Coherence distribution
        coherence_scores = [summary.coherence_score for summary in summaries.values()]
        coherence_distribution = {
            "high": len([s for s in coherence_scores if s >= 0.7]),
            "medium": len([s for s in coherence_scores if 0.4 <= s < 0.7]),
            "low": len([s for s in coherence_scores if s < 0.4]),
        }

        return {
            "total_summaries": len(summaries),
            "avg_summary_length": avg_summary_length,
            "min_summary_length": min(summary_lengths),
            "max_summary_length": max(summary_lengths),
            "level_distribution": level_distribution,
            "coherence_distribution": coherence_distribution,
            "avg_coherence": sum(coherence_scores) / len(coherence_scores),
        }
