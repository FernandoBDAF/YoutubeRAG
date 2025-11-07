#!/usr/bin/env python3
"""
Batch Experiment Runner

Achievement 2.4: Batch Experiment Runner

Script for running multiple GraphRAG experiments in batch with progress tracking,
error handling, and automatic result collection.

Usage:
    python scripts/run_experiments.py --configs configs/graphrag/*.json
    python scripts/run_experiments.py --batch-file experiments_batch.json
    python scripts/run_experiments.py --configs config1.json config2.json --parallel
"""

import sys
import os
import json
import argparse
import time
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config.graphrag import GraphRAGPipelineConfig
from business.pipelines.graphrag import GraphRAGPipeline

logger = logging.getLogger(__name__)


def load_config_file(config_path: str) -> Dict[str, Any]:
    """
    Load experiment configuration from JSON file.
    
    Args:
        config_path: Path to JSON config file
        
    Returns:
        Configuration dictionary
    """
    with open(config_path, 'r') as f:
        return json.load(f)


def load_batch_file(batch_path: str) -> List[Dict[str, Any]]:
    """
    Load batch experiment configuration file.
    
    Expected format:
    {
        "experiments": [
            {"config_path": "configs/graphrag/exp1.json", "experiment_id": "exp1"},
            {"config_path": "configs/graphrag/exp2.json", "experiment_id": "exp2"}
        ],
        "parallel": false,
        "max_workers": 2
    }
    
    Args:
        batch_path: Path to batch config file
        
    Returns:
        List of experiment configurations
    """
    with open(batch_path, 'r') as f:
        batch_config = json.load(f)
    
    experiments = []
    for exp_config in batch_config.get("experiments", []):
        config_path = exp_config.get("config_path")
        if not config_path:
            logger.warning(f"Skipping experiment without config_path: {exp_config}")
            continue
        
        config = load_config_file(config_path)
        # Override experiment_id if provided in batch config
        if "experiment_id" in exp_config:
            config["experiment_id"] = exp_config["experiment_id"]
        
        experiments.append({
            "config": config,
            "config_path": config_path,
            "experiment_id": config.get("experiment_id", Path(config_path).stem),
        })
    
    return experiments


def run_single_experiment(
    config: Dict[str, Any],
    config_path: str,
    experiment_id: str,
    retry_count: int = 0,
    max_retries: int = 2,
) -> Dict[str, Any]:
    """
    Run a single GraphRAG experiment.
    
    Achievement 2.4: Batch Experiment Runner
    
    Args:
        config: Experiment configuration dictionary
        config_path: Path to config file (for logging)
        experiment_id: Experiment identifier
        retry_count: Current retry attempt
        max_retries: Maximum number of retries on failure
        
    Returns:
        Result dictionary with status, duration, and error (if any)
    """
    start_time = time.time()
    result = {
        "experiment_id": experiment_id,
        "config_path": config_path,
        "status": "unknown",
        "duration_seconds": 0,
        "error": None,
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": None,
    }
    
    try:
        logger.info(f"🚀 Starting experiment: {experiment_id}")
        logger.info(f"   Config: {config_path}")
        
        # Create pipeline config from dictionary
        pipeline_config = GraphRAGPipelineConfig.from_dict(config)
        
        # Create and setup pipeline
        pipeline = GraphRAGPipeline(pipeline_config)
        pipeline.setup()
        
        # Run pipeline
        pipeline.run_full_pipeline()
        
        result["status"] = "completed"
        result["completed_at"] = datetime.utcnow().isoformat()
        logger.info(f"✅ Experiment completed: {experiment_id}")
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ Experiment failed: {experiment_id} - {error_msg}")
        
        # Retry logic
        if retry_count < max_retries:
            logger.info(f"🔄 Retrying experiment: {experiment_id} (attempt {retry_count + 1}/{max_retries})")
            time.sleep(5)  # Wait before retry
            return run_single_experiment(
                config, config_path, experiment_id, retry_count + 1, max_retries
            )
        
        result["status"] = "failed"
        result["error"] = error_msg
        result["completed_at"] = datetime.utcnow().isoformat()
    
    finally:
        result["duration_seconds"] = time.time() - start_time
        result["duration_formatted"] = f"{result['duration_seconds'] / 3600:.2f}h"
    
    return result


def run_experiments_sequential(
    experiments: List[Dict[str, Any]],
    progress_callback: Optional[callable] = None,
) -> List[Dict[str, Any]]:
    """
    Run experiments sequentially.
    
    Args:
        experiments: List of experiment configurations
        progress_callback: Optional callback function(status, current, total)
        
    Returns:
        List of experiment results
    """
    results = []
    total = len(experiments)
    
    for i, exp in enumerate(experiments, 1):
        if progress_callback:
            progress_callback("running", i, total)
        
        result = run_single_experiment(
            exp["config"],
            exp["config_path"],
            exp["experiment_id"],
        )
        results.append(result)
        
        if progress_callback:
            progress_callback("completed", i, total)
    
    return results


def run_experiments_parallel(
    experiments: List[Dict[str, Any]],
    max_workers: int = 2,
    progress_callback: Optional[callable] = None,
) -> List[Dict[str, Any]]:
    """
    Run experiments in parallel.
    
    Args:
        experiments: List of experiment configurations
        max_workers: Maximum number of parallel workers
        progress_callback: Optional callback function(status, current, total)
        
    Returns:
        List of experiment results
    """
    results = []
    total = len(experiments)
    completed = 0
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all experiments
        future_to_exp = {
            executor.submit(
                run_single_experiment,
                exp["config"],
                exp["config_path"],
                exp["experiment_id"],
            ): exp
            for exp in experiments
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_exp):
            completed += 1
            if progress_callback:
                progress_callback("running", completed, total)
            
            result = future.result()
            results.append(result)
            
            if progress_callback:
                progress_callback("completed", completed, total)
    
    return results


def print_summary(results: List[Dict[str, Any]]) -> None:
    """
    Print summary of batch experiment results.
    
    Args:
        results: List of experiment results
    """
    total = len(results)
    completed = sum(1 for r in results if r["status"] == "completed")
    failed = sum(1 for r in results if r["status"] == "failed")
    
    total_duration = sum(r["duration_seconds"] for r in results)
    
    print("\n" + "=" * 60)
    print("Batch Experiment Summary")
    print("=" * 60)
    print(f"Total Experiments: {total}")
    print(f"Completed: {completed} ({completed/total*100:.1f}%)")
    print(f"Failed: {failed} ({failed/total*100:.1f}%)")
    print(f"Total Duration: {total_duration / 3600:.2f}h")
    print()
    
    if failed > 0:
        print("Failed Experiments:")
        for r in results:
            if r["status"] == "failed":
                print(f"  - {r['experiment_id']}: {r.get('error', 'Unknown error')}")
        print()
    
    print("Results:")
    for r in results:
        status_icon = "✅" if r["status"] == "completed" else "❌"
        print(f"  {status_icon} {r['experiment_id']}: {r.get('duration_formatted', 'N/A')}")


def main():
    """Main entry point for batch experiment runner."""
    parser = argparse.ArgumentParser(
        description="Run multiple GraphRAG experiments in batch",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--configs",
        nargs="+",
        help="Paths to experiment config files (supports glob patterns)",
    )
    
    parser.add_argument(
        "--batch-file",
        help="Path to batch configuration file",
    )
    
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run experiments in parallel",
    )
    
    parser.add_argument(
        "--max-workers",
        type=int,
        default=2,
        help="Maximum number of parallel workers (default: 2)",
    )
    
    parser.add_argument(
        "--output",
        help="Path to save results JSON file",
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    # Load experiments
    experiments = []
    
    if args.batch_file:
        experiments = load_batch_file(args.batch_file)
    elif args.configs:
        import glob
        
        config_paths = []
        for pattern in args.configs:
            config_paths.extend(glob.glob(pattern))
        
        for config_path in config_paths:
            try:
                config = load_config_file(config_path)
                experiment_id = config.get("experiment_id", Path(config_path).stem)
                experiments.append({
                    "config": config,
                    "config_path": config_path,
                    "experiment_id": experiment_id,
                })
            except Exception as e:
                logger.error(f"Failed to load config {config_path}: {e}")
                continue
    else:
        parser.error("Must provide either --configs or --batch-file")
    
    if not experiments:
        logger.error("No experiments to run")
        sys.exit(1)
    
    logger.info(f"📊 Running {len(experiments)} experiments")
    logger.info(f"   Mode: {'parallel' if args.parallel else 'sequential'}")
    if args.parallel:
        logger.info(f"   Max workers: {args.max_workers}")
    
    # Progress callback
    def progress_callback(status, current, total):
        logger.info(f"Progress: {current}/{total} experiments {status}")
    
    # Run experiments
    start_time = time.time()
    
    if args.parallel:
        results = run_experiments_parallel(
            experiments,
            max_workers=args.max_workers,
            progress_callback=progress_callback,
        )
    else:
        results = run_experiments_sequential(
            experiments,
            progress_callback=progress_callback,
        )
    
    total_duration = time.time() - start_time
    
    # Print summary
    print_summary(results)
    
    # Save results
    if args.output:
        output_data = {
            "batch_started_at": datetime.utcnow().isoformat(),
            "total_duration_seconds": total_duration,
            "experiments": results,
        }
        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2, default=str)
        logger.info(f"💾 Results saved to: {args.output}")
    
    # Exit with error code if any failed
    failed_count = sum(1 for r in results if r["status"] == "failed")
    if failed_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()


