"""
GraphRAG Pipeline

This module implements the complete GraphRAG pipeline that orchestrates
all stages from entity extraction to community detection and summarization.
"""

import logging
import time
import argparse
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from core.config.graphrag import (
    GraphRAGPipelineConfig,
    GraphExtractionConfig,
    EntityResolutionConfig,
    GraphConstructionConfig,
    CommunityDetectionConfig,
)
from business.pipelines.runner import StageSpec, PipelineRunner
from business.services.graphrag.indexes import (
    create_graphrag_indexes,
    ensure_graphrag_collections,
)

logger = logging.getLogger(__name__)


class GraphRAGPipeline:
    """
    Complete GraphRAG pipeline orchestrating all stages.
    """

    def __init__(self, config: GraphRAGPipelineConfig):
        """
        Initialize the GraphRAG Pipeline.

        Args:
            config: Configuration for the pipeline
        """
        self.config = config
        self.specs = self._create_stage_specs()
        self.runner = PipelineRunner(
            self.specs, stop_on_error=not config.continue_on_error
        )

        # Initialize database connection for setup()
        from dependencies.database.mongodb import get_mongo_client
        from core.config.paths import DB_NAME

        self.client = get_mongo_client()
        db_name = config.extraction_config.db_name or DB_NAME
        self.db = self.client[db_name]  # ✅ Now available for setup()

        logger.info("Initialized GraphRAGPipeline with PipelineRunner")

    def _create_stage_specs(self) -> List[StageSpec]:
        """
        Create stage specifications for the GraphRAG pipeline using registry keys.

        Returns:
            List of stage specifications
        """
        return [
            StageSpec(
                stage="graph_extraction",  # ✅ Use registry key
                config=self.config.extraction_config,
            ),
            StageSpec(
                stage="entity_resolution",
                config=self.config.resolution_config,
            ),
            StageSpec(
                stage="graph_construction",
                config=self.config.construction_config,
            ),
            StageSpec(
                stage="community_detection",
                config=self.config.detection_config,
            ),
        ]

    def setup(self) -> None:
        """
        Set up the GraphRAG pipeline by creating necessary collections and indexes.
        """
        logger.info("Setting up GraphRAG pipeline...")

        try:
            # Ensure GraphRAG collections exist
            # Note: This handles existing collections gracefully
            ensure_graphrag_collections(self.db)

            # Create GraphRAG indexes
            # Note: Index creation is idempotent (duplicate indexes are ignored)
            create_graphrag_indexes(self.db)

            logger.info("GraphRAG pipeline setup completed successfully")

        except Exception as e:
            # Log error but don't fail if collections already exist
            error_msg = str(e).lower()
            if (
                "already exists" in error_msg
                or "collection" in error_msg
                and "exists" in error_msg
            ):
                logger.warning(
                    f"Some GraphRAG collections may already exist: {e}. "
                    f"Continuing with pipeline execution."
                )
            else:
                logger.error(f"Failed to setup GraphRAG pipeline: {e}")
                raise

    def run_stage(self, stage_name: str) -> int:
        """Run a specific stage."""
        logger.info(f"Running GraphRAG stage: {stage_name}")

        # Find stage spec
        for spec in self.specs:
            if spec.stage == stage_name:
                # Run single stage using PipelineRunner
                return PipelineRunner([spec]).run()

        raise ValueError(f"Unknown stage: {stage_name}")

    def run_full_pipeline(self) -> int:
        """Run the complete GraphRAG pipeline."""
        logger.info("Starting full GraphRAG pipeline execution")

        # Setup (create indexes, etc.)
        self.setup()

        # Run pipeline using PipelineRunner
        exit_code = self.runner.run()

        if exit_code == 0:
            logger.info("GraphRAG pipeline completed successfully")
        else:
            logger.error("GraphRAG pipeline failed")

        return exit_code

    # TODO: Implement retry logic in PipelineRunner for production reliability
    # Desired behavior:
    # - Configurable retry attempts via config.max_retries
    # - Exponential backoff via config.retry_delay
    # - Selective retry based on error types (transient vs permanent)
    # - Per-stage retry configuration
    # Example:
    #   PipelineRunner(specs, max_retries=3, retry_delay=5.0, retry_on_errors=[...])

    # TODO: Implement comprehensive statistics aggregation for pipeline monitoring
    # Desired behavior:
    # - Real-time stats collection during pipeline execution
    # - Aggregation across all stages (total processed, failed, skipped)
    # - Performance metrics (avg time per doc, throughput)
    # - Progress tracking (percentage complete, ETA)
    # - Integration with monitoring dashboard
    # Implementation should use callbacks or hooks in PipelineRunner

    # Note: _calculate_overall_stats() removed - functionality covered by statistics aggregation TODO above

    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current status of the GraphRAG pipeline."""
        try:
            from app.pipelines.base_pipeline import STAGE_REGISTRY

            stage_statuses = {}

            for spec in self.specs:
                stage_name = (
                    spec.stage if isinstance(spec.stage, str) else spec.stage.name
                )
                stage_cls = (
                    STAGE_REGISTRY.get(stage_name)
                    if isinstance(spec.stage, str)
                    else spec.stage
                )

                if not stage_cls:
                    stage_statuses[stage_name] = {
                        "error": "Stage class not found in registry"
                    }
                    continue

                try:
                    # Create temporary stage instance to get stats
                    stage = stage_cls()
                    stage.setup()  # Initialize to get stats methods

                    # Get stats using actual method names
                    stats = {}
                    if hasattr(stage, "get_processing_stats"):  # GraphExtractionStage
                        stats = stage.get_processing_stats()
                    elif hasattr(
                        stage, "get_resolution_stats"
                    ):  # EntityResolutionStage
                        stats = stage.get_resolution_stats()
                    elif hasattr(
                        stage, "get_construction_stats"
                    ):  # GraphConstructionStage
                        stats = stage.get_construction_stats()
                    elif hasattr(
                        stage, "get_detection_stats"
                    ):  # CommunityDetectionStage
                        stats = stage.get_detection_stats()
                    else:
                        stats = {
                            "status": "unknown",
                            "message": "No stats method available",
                        }

                    stage_statuses[stage_name] = stats

                except Exception as e:
                    logger.warning(f"Failed to get stats for stage {stage_name}: {e}")
                    stage_statuses[stage_name] = {"error": str(e)}

            return {
                "pipeline_status": "active",
                "stage_statuses": stage_statuses,
                "timestamp": time.time(),
            }

        except Exception as e:
            logger.error(f"Failed to get pipeline status: {e}")
            return {
                "pipeline_status": "error",
                "error": str(e),
                "timestamp": time.time(),
            }

    def cleanup_failed_stages(self) -> Dict[str, int]:
        """Clean up failed stage records to allow retry."""
        from app.pipelines.base_pipeline import STAGE_REGISTRY

        cleanup_results = {}

        for spec in self.specs:
            stage_name = spec.stage if isinstance(spec.stage, str) else spec.stage.name
            stage_cls = (
                STAGE_REGISTRY.get(stage_name)
                if isinstance(spec.stage, str)
                else spec.stage
            )

            if not stage_cls:
                logger.warning(f"Stage class not found for {stage_name}")
                cleanup_results[stage_name] = 0
                continue

            try:
                # Create temporary stage instance to call cleanup methods
                stage = stage_cls()

                # Apply config if available (needed for cleanup methods that query collections)
                if spec.config:
                    # Temporarily set config for cleanup operations
                    stage.config = spec.config

                # Call cleanup method based on stage type
                count = 0
                if hasattr(stage, "cleanup_failed_extractions"):
                    count = stage.cleanup_failed_extractions()
                elif hasattr(stage, "cleanup_failed_resolutions"):
                    count = stage.cleanup_failed_resolutions()
                elif hasattr(stage, "cleanup_failed_constructions"):
                    count = stage.cleanup_failed_constructions()
                elif hasattr(stage, "cleanup_failed_detections"):
                    count = stage.cleanup_failed_detections()
                else:
                    logger.warning(f"Stage {stage_name} has no cleanup method")

                cleanup_results[stage_name] = count

            except Exception as e:
                logger.error(f"Failed to cleanup stage {stage_name}: {e}")
                cleanup_results[stage_name] = 0

        return cleanup_results


def create_graphrag_pipeline(
    config: Optional[GraphRAGPipelineConfig] = None,
) -> GraphRAGPipeline:
    """
    Create a GraphRAG pipeline with default configuration.

    Args:
        config: Optional custom configuration

    Returns:
        GraphRAGPipeline instance
    """
    if config is None:
        config = GraphRAGPipelineConfig()

    return GraphRAGPipeline(config)


if __name__ == "__main__":
    # CLI interface for running the GraphRAG pipeline
    parser = argparse.ArgumentParser(description="GraphRAG Pipeline Runner")
    parser.add_argument("--stage", help="Run specific stage only")
    parser.add_argument("--video-id", help="Process specific video ID")
    parser.add_argument(
        "--max", type=int, help="Maximum number of documents to process"
    )
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    # Configure logging
    # Note: This is a basic fallback. For full logging features (file output,
    # third-party silencing, etc.), use run_graphrag_pipeline.py instead.
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Silencing noisy loggers (minimal, use run_graphrag_pipeline.py for full setup)
    for logger_name in ["numba", "graspologic", "pymongo", "urllib3", "httpcore"]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.INFO)

    # Create pipeline
    pipeline = create_graphrag_pipeline()

    # Run pipeline
    if args.stage:
        result = pipeline.run_stage(args.stage)
    else:
        result = pipeline.run_full_pipeline()

    print(f"Pipeline result: {result}")
