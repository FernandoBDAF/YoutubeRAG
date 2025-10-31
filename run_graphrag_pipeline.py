#!/usr/bin/env python3
"""
GraphRAG Pipeline Runner

This script provides a command-line interface for running the GraphRAG pipeline.
It supports running individual stages or the complete pipeline with various options.
"""

import argparse
import logging
import sys
import os
from typing import Optional

# Add the project root to the Python path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from app.pipelines.graphrag_pipeline import create_graphrag_pipeline
from config.graphrag_config import GraphRAGPipelineConfig
from app.pipelines.graphrag_pipeline import GraphRAGPipeline
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def setup_logging(verbose: bool = False, log_file: str = None) -> None:
    """
    Set up logging configuration for GraphRAG pipeline.

    Enhanced version matching main.py pattern to avoid issues encountered
    during ingestion pipeline testing.

    Args:
        verbose: Enable verbose (DEBUG) logging
        log_file: Optional path to log file (default: logs/pipeline/graphrag_TIMESTAMP.log)
    """
    from pathlib import Path
    from datetime import datetime

    log_level = logging.DEBUG if verbose else logging.INFO

    # Silence noisy third-party loggers FIRST (before any imports happen)
    # Only show warnings/errors from these libraries, even in verbose mode
    noisy_loggers = [
        "numba",
        "graspologic",
        "pymongo",
        "urllib3",
        "httpx",
        "httpcore",
        "openai",
        "numba.core",
        "numba.core.ssa",
        "numba.core.byteflow",
        "numba.core.interpreter",
    ]
    for logger_name in noisy_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)

    # Create log directory if needed
    if log_file is None:
        log_dir = Path("logs/pipeline")
        log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = str(log_dir / f"graphrag_{timestamp}.log")

    # Configure logging with both console and file handlers
    handlers = [
        logging.StreamHandler(sys.stdout),  # Console output
    ]

    # Add file handler if log file is specified
    log_file_path = None
    log_file_error = None
    try:
        # Resolve to absolute path for better error handling
        log_path = Path(log_file).resolve()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(str(log_path), encoding="utf-8")
        handlers.append(file_handler)
        log_file_path = str(log_path)
    except Exception as e:
        # Non-fatal: continue without file logging
        # We'll log this after basicConfig is set up
        log_file_error = str(e)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
        force=True,  # Override any existing configuration
    )

    # Re-apply silencing after basicConfig (in case it was reset)
    for logger_name in noisy_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)

    # httpx at INFO for LLM visibility
    logging.getLogger("httpx").setLevel(logging.INFO)

    logger = logging.getLogger(__name__)
    if log_file_path:
        logger.info(
            f"Logging configured: level={logging.getLevelName(log_level)}, file={log_file_path}"
        )
    else:
        if log_file and log_file_error:
            logger.warning(
                f"Failed to create log file '{log_file}': {log_file_error}. Continuing with console logging only."
            )
        logger.info(
            f"Logging configured: level={logging.getLevelName(log_level)}, file=console only"
        )


def create_config_from_args(args) -> GraphRAGPipelineConfig:
    """Create pipeline configuration from command line arguments."""
    env = dict(os.environ)
    default_db = os.getenv("DB_NAME", "mongo_hack")

    # Use from_args_env instead of manual construction
    config = GraphRAGPipelineConfig.from_args_env(args, env, default_db)

    # Override with any command-line specific args not in from_args_env
    if hasattr(args, "log_file") and args.log_file:
        config.log_file = args.log_file

    return config


def run_single_stage(pipeline: GraphRAGPipeline, stage_name: str) -> None:
    """Run a single stage of the GraphRAG pipeline."""
    logger = logging.getLogger(__name__)

    logger.info(f"Running GraphRAG stage: {stage_name}")

    try:
        exit_code = pipeline.run_stage(stage_name)

        if exit_code == 0:
            logger.info(f"Stage {stage_name} completed successfully")
        else:
            logger.error(f"Stage {stage_name} failed with exit code {exit_code}")
            sys.exit(exit_code)

    except Exception as e:
        logger.error(f"Error running stage {stage_name}: {e}")
        sys.exit(1)


def run_full_pipeline(pipeline: GraphRAGPipeline) -> None:
    """Run the complete GraphRAG pipeline."""
    logger = logging.getLogger(__name__)

    logger.info("Starting full GraphRAG pipeline execution")

    try:
        exit_code = pipeline.run_full_pipeline()

        if exit_code == 0:
            logger.info("GraphRAG pipeline completed successfully")
        else:
            logger.error(f"GraphRAG pipeline failed with exit code {exit_code}")
            sys.exit(exit_code)

    except Exception as e:
        logger.error(f"Error running GraphRAG pipeline: {e}")
        sys.exit(1)


def show_pipeline_status(pipeline: GraphRAGPipeline) -> None:
    """
    Show the current status of the GraphRAG pipeline.

    Args:
        pipeline: GraphRAG pipeline instance
    """
    logger = logging.getLogger(__name__)

    try:
        status = pipeline.get_pipeline_status()

        logger.info("GraphRAG Pipeline Status:")
        logger.info(f"Pipeline Status: {status['pipeline_status']}")

        for stage_name, stage_status in status["stage_statuses"].items():
            logger.info(f"  {stage_name}: {stage_status}")

    except Exception as e:
        logger.error(f"Error getting pipeline status: {e}")
        sys.exit(1)


def cleanup_failed_stages(pipeline: GraphRAGPipeline) -> None:
    """
    Clean up failed stage records.

    Args:
        pipeline: GraphRAG pipeline instance
    """
    logger = logging.getLogger(__name__)

    try:
        cleanup_results = pipeline.cleanup_failed_stages()

        logger.info("Cleanup Results:")
        for stage_name, count in cleanup_results.items():
            logger.info(f"  {stage_name}: {count} records cleaned up")

    except Exception as e:
        logger.error(f"Error cleaning up failed stages: {e}")
        sys.exit(1)


def main():
    """Main function for the GraphRAG pipeline runner."""
    parser = argparse.ArgumentParser(
        description="GraphRAG Pipeline Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        Examples:
        # Run the complete pipeline
        python run_graphrag_pipeline.py

        # Run a specific stage
        python run_graphrag_pipeline.py --stage graph_extraction

        # Process a specific video
        python run_graphrag_pipeline.py --video-id video_123

        # Dry run with verbose logging
        python run_graphrag_pipeline.py --dry-run --verbose

        # Show pipeline status
        python run_graphrag_pipeline.py --status

        # Clean up failed stages
        python run_graphrag_pipeline.py --cleanup
        """,
    )

    # Main operation arguments
    parser.add_argument(
        "--stage",
        choices=[
            "graph_extraction",
            "entity_resolution",
            "graph_construction",
            "community_detection",
        ],
        help="Run specific stage only",
    )
    parser.add_argument("--status", action="store_true", help="Show pipeline status")
    parser.add_argument(
        "--cleanup", action="store_true", help="Clean up failed stage records"
    )

    # Processing arguments
    parser.add_argument("--video-id", help="Process specific video ID")
    parser.add_argument(
        "--max", type=int, help="Maximum number of documents to process"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Dry run mode (no actual processing)"
    )

    # Configuration arguments
    parser.add_argument(
        "--model", default="gpt-4o-mini", help="LLM model to use (default: gpt-4o-mini)"
    )
    parser.add_argument(
        "--extraction-concurrency", type=int, help="Concurrency for extraction stage"
    )
    parser.add_argument(
        "--resolution-concurrency", type=int, help="Concurrency for resolution stage"
    )
    parser.add_argument(
        "--max-cluster-size",
        type=int,
        help="Maximum cluster size for community detection",
    )

    # Standard stage arguments (used by from_args_env)
    parser.add_argument("--db-name", help="Database name")
    parser.add_argument("--read-db-name", help="Read database name")
    parser.add_argument("--write-db-name", help="Write database name")
    parser.add_argument("--read-coll", help="Read collection name")
    parser.add_argument("--write-coll", help="Write collection name")
    parser.add_argument("--concurrency", type=int, help="Concurrency level")
    parser.add_argument(
        "--upsert-existing", action="store_true", help="Upsert existing documents"
    )

    # Logging arguments
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose logging (DEBUG level)"
    )
    parser.add_argument(
        "--log-file",
        help="Path to log file (default: logs/pipeline/graphrag_TIMESTAMP.log)",
    )
    parser.add_argument(
        "--quiet", action="store_true", help="Suppress output except errors"
    )

    args = parser.parse_args()

    # Set up logging
    if args.quiet:
        logging.basicConfig(level=logging.ERROR)
    else:
        setup_logging(args.verbose, getattr(args, "log_file", None))

    logger = logging.getLogger(__name__)

    # Validate arguments
    if args.stage and args.status:
        logger.error("Cannot specify both --stage and --status")
        sys.exit(1)

    if args.stage and args.cleanup:
        logger.error("Cannot specify both --stage and --cleanup")
        sys.exit(1)

    if args.status and args.cleanup:
        logger.error("Cannot specify both --status and --cleanup")
        sys.exit(1)

    try:
        # Create pipeline configuration
        config = create_config_from_args(args)

        # Create pipeline
        pipeline = create_graphrag_pipeline(config)

        # Execute based on arguments
        if args.status:
            show_pipeline_status(pipeline)
        elif args.cleanup:
            cleanup_failed_stages(pipeline)
        elif args.stage:
            run_single_stage(pipeline, args.stage)
        else:
            run_full_pipeline(pipeline)

    except KeyboardInterrupt:
        logger.info("Pipeline execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
