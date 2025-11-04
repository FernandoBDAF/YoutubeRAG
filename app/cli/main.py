import os
import argparse
import subprocess
import json
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv

# Configure logging for noisy third-party libraries FIRST (before any imports)
# This prevents DEBUG logs from libraries like numba, pymongo, etc.
# httpx is kept at INFO level to see API calls for verification
_noisy_loggers = [
    "numba",
    "graspologic",
    "pymongo",
    "urllib3",
    "httpcore",
    "openai",
    "numba.core",
    "numba.core.ssa",
    "numba.core.byteflow",
    "numba.core.interpreter",
]
for logger_name in _noisy_loggers:
    logging.getLogger(logger_name).setLevel(logging.WARNING)

# Keep httpx at INFO to see API calls (useful for debugging LLM operations)
# Only silence DEBUG level from httpx
logging.getLogger("httpx").setLevel(logging.INFO)

from dependencies.database.mongodb import get_mongo_client, read_collection
from core.config.paths import DB_NAME
from app.scripts.utilities.seed.seed_indexes import (
    ensure_collections_and_indexes,
    wait_for_index_ready,
)


def setup_logging(verbose: bool = False, log_file: str = None) -> None:
    """
    Set up logging configuration for the application.

    Args:
        verbose: Enable verbose (DEBUG) logging
        log_file: Optional path to log file (default: logs/pipeline/ingestion.log)
    """
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
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = str(log_dir / f"ingestion_{timestamp}.log")

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


def run_stage(stage: str, **kwargs) -> None:
    import sys

    py = sys.executable
    if stage == "ingest":
        args = kwargs.get("args") or []
        env = {**os.environ, "PYTHONPATH": os.getcwd()}
        # Pass through env flag for upsert behavior
        if "INGEST_UPSERT_EXISTING" not in env:
            env["INGEST_UPSERT_EXISTING"] = "false"
        subprocess.run(
            [py, "app/stages/ingest.py", *args],
            check=True,
            env=env,
        )
    elif stage == "backfill_transcript":
        env = {**os.environ, "PYTHONPATH": os.getcwd()}
        if "INGEST_UPSERT_EXISTING" not in env:
            env["INGEST_UPSERT_EXISTING"] = "false"
        vid = kwargs.get("video_id")
        if not vid:
            print("Backfilling all transcripts")
            subprocess.run(
                [py, "app/stages/backfill_transcript.py"],
                check=True,
                env=env,
            )
            return
        subprocess.run(
            [py, "app/stages/backfill_transcript.py", "--video_id", vid],
            check=True,
            env=env,
        )
    elif stage == "clean":
        use_llm = kwargs.get("llm", False)
        cmd = [py, "app/stages/clean.py"]
        if use_llm:
            cmd.append("--llm")
        subprocess.run(cmd, check=True, env={**os.environ, "PYTHONPATH": os.getcwd()})
    elif stage == "enrich":
        use_llm = kwargs.get("llm", False)
        cmd = [py, "app/stages/enrich.py"]
        if use_llm:
            cmd.append("--llm")
        subprocess.run(cmd, check=True, env={**os.environ, "PYTHONPATH": os.getcwd()})
    elif stage == "chunk":
        use_llm = kwargs.get("llm", False)
        chunk = kwargs.get("chunk", True)
        cmd = [py, "app/stages/chunk_embed.py"]
        if use_llm:
            cmd.append("--llm")
        if not chunk:
            cmd.append("--chunk")
        subprocess.run(cmd, check=True, env={**os.environ, "PYTHONPATH": os.getcwd()})
    elif stage == "redundancy":
        use_llm = kwargs.get("llm", False)
        cmd = [py, "app/stages/redundancy.py"]
        if use_llm:
            cmd.append("--llm")
        subprocess.run(cmd, check=True, env={**os.environ, "PYTHONPATH": os.getcwd()})
    elif stage == "trust":
        use_llm = kwargs.get("llm", False)
        cmd = [py, "app/stages/trust.py"]
        if use_llm:
            cmd.append("--llm")
        subprocess.run(cmd, check=True, env={**os.environ, "PYTHONPATH": os.getcwd()})
    elif stage == "pipeline":
        # Use implemented IngestionPipeline instead of artificial stage calling
        from business.pipelines.ingestion import IngestionPipeline

        # Create argparse.Namespace-like object from kwargs
        class Args:
            pass

        args_obj = Args()
        # Extract args list if present (for ingest stage)
        ingest_args = kwargs.get("args") or []
        # Parse ingest args if they contain playlist_id, channel_id, or video_ids
        args_obj.playlist_id = kwargs.get("playlist_id")
        args_obj.channel_id = kwargs.get("channel_id")
        args_obj.video_ids = kwargs.get("video_ids")
        args_obj.max = kwargs.get("max")
        # LLM is always enabled for pipeline stages - no need for flag
        # Get verbose from kwargs (passed from main)
        args_obj.verbose = kwargs.get("verbose", False)
        args_obj.dry_run = kwargs.get("dry_run", False)
        args_obj.db_name = kwargs.get("db_name")

        # If ingest_args is a list of strings (CLI args), parse them
        if ingest_args and isinstance(ingest_args, list):
            import argparse as _argparse

            ingest_parser = _argparse.ArgumentParser()
            ingest_parser.add_argument("--playlist_id")
            ingest_parser.add_argument("--channel_id")
            ingest_parser.add_argument("--video_ids", nargs="*")
            ingest_parser.add_argument("--max", type=int)
            parsed_ingest, _ = ingest_parser.parse_known_args(ingest_args)
            if parsed_ingest.playlist_id:
                args_obj.playlist_id = parsed_ingest.playlist_id
            if parsed_ingest.channel_id:
                args_obj.channel_id = parsed_ingest.channel_id
            if parsed_ingest.video_ids:
                args_obj.video_ids = parsed_ingest.video_ids
            if parsed_ingest.max:
                args_obj.max = parsed_ingest.max

        # Create pipeline and run
        pipeline_kwargs = {
            "playlist_id": args_obj.playlist_id,
            "channel_id": args_obj.channel_id,
            "video_ids": args_obj.video_ids,
            "max": args_obj.max,
            # LLM is always enabled - no need to pass flag
        }
        pipeline = IngestionPipeline.from_cli_args(args_obj, pipeline_kwargs)
        exit_code = pipeline.run_full_pipeline()
        if exit_code != 0:
            raise SystemExit(exit_code)
    elif stage == "ui":
        subprocess.run(
            ["streamlit", "run", "streamlit_app.py"],
            check=True,
            env={**os.environ, "PYTHONPATH": os.getcwd()},
        )
    elif stage == "scan_transcripts":
        subprocess.run(
            [py, "app/stages/scan_transcripts.py"],
            check=True,
            env={**os.environ, "PYTHONPATH": os.getcwd()},
        )
    elif stage == "health":
        subprocess.run(
            [py, "health_check.py"],
            check=True,
            env={**os.environ, "PYTHONPATH": os.getcwd()},
        )
    else:
        raise SystemExit(f"Unknown stage: {stage}")


def main() -> None:
    load_dotenv()

    # Auto-seed base collections and vector index if missing
    try:
        client = get_mongo_client()
        db = client[DB_NAME]
        ensure_collections_and_indexes(db)
    except Exception:
        # Non-fatal; proceed (user may not have Atlas CLI/env set yet)
        pass
    parser = argparse.ArgumentParser(description="Mongo_Hack Orchestrator")
    sub = parser.add_subparsers(dest="cmd", required=True)

    s_ing = sub.add_parser("ingest", help="Ingest videos")
    s_ing.add_argument("--playlist_id")
    s_ing.add_argument("--channel_id")
    s_ing.add_argument("--video_ids", nargs="*")
    s_ing.add_argument("--max", type=int, default=10)

    s_clean = sub.add_parser("clean", help="Clean transcripts")
    s_clean.add_argument("--llm", action="store_true")

    s_enrich = sub.add_parser("enrich", help="Enrich transcripts")
    s_enrich.add_argument("--llm", action="store_true")
    s_chunk = sub.add_parser("chunk", help="Chunk + embed")
    s_chunk.add_argument("--llm", action="store_true")
    s_chunk.add_argument("--chunk", type=bool, required=False)
    s_red = sub.add_parser("redundancy", help="Compute redundancy flags")
    s_red.add_argument("--llm", action="store_true")
    s_trust = sub.add_parser("trust", help="Compute trust scores")
    s_trust.add_argument("--llm", action="store_true")
    s_pipe = sub.add_parser("pipeline", help="Run full pipeline")
    s_pipe.add_argument("--playlist_id")
    s_pipe.add_argument("--channel_id")
    s_pipe.add_argument("--video_ids", nargs="*")
    s_pipe.add_argument("--max", type=int, default=5)
    s_pipe.add_argument("--llm", action="store_true")
    s_pipe.add_argument(
        "--upsert-existing",
        action="store_true",
        dest="upsert_existing",
        help="Force re-processing of existing documents (bypass skip checks)",
    )
    s_pipe.add_argument(
        "--verbose", action="store_true", help="Enable verbose logging (DEBUG level)"
    )
    s_pipe.add_argument(
        "--log-file",
        help="Path to log file (default: logs/pipeline/ingestion_TIMESTAMP.log)",
    )
    s_read = sub.add_parser("read", help="Read documents from a collection")
    s_read.add_argument("--collection", required=True)
    s_read.add_argument("--video_id")
    s_read.add_argument(
        "--fields",
        help="Comma-separated list of fields to return (all if omitted)",
    )
    s_read.add_argument("--limit", type=int, default=100)
    s_btf = sub.add_parser(
        "backfill_transcript", help="Backfill transcript for a single video"
    )
    s_btf.add_argument("--video_id", required=False)
    sub.add_parser("ui", help="Launch Streamlit UI")
    sub.add_parser(
        "scan_transcripts", help="Fetch transcripts for videos missing transcript_raw"
    )
    sub.add_parser("wait_index", help="Wait until vector index is READY")
    sub.add_parser("health", help="Run health checks")

    args = parser.parse_args()

    # Set up logging (INFO level by default)
    # For pipeline command, use its verbose/log-file flags
    # For other commands, default to INFO level
    # Note: verbose/log-file are subparser-specific, so check if they exist
    verbose = getattr(args, "verbose", False)
    log_file = getattr(args, "log_file", None)

    # Always configure logging (even for non-pipeline commands)
    setup_logging(verbose=verbose, log_file=log_file)

    if args.cmd == "ingest":
        cli_args = []
        if args.playlist_id:
            cli_args += ["--playlist_id", args.playlist_id, "--max", str(args.max)]
        elif args.channel_id:
            cli_args += ["--channel_id", args.channel_id, "--max", str(args.max)]
        elif args.video_ids:
            cli_args += ["--video_ids", *args.video_ids]
        run_stage("ingest", args=cli_args)
    elif args.cmd == "clean":
        run_stage("clean", llm=bool(args.llm))
    elif args.cmd == "pipeline":
        cli_args = []
        if args.playlist_id:
            cli_args += ["--playlist_id", args.playlist_id, "--max", str(args.max)]
        elif args.channel_id:
            cli_args += ["--channel_id", args.channel_id, "--max", str(args.max)]
        elif args.video_ids:
            cli_args += ["--video_ids", *args.video_ids]
        # LLM is always enabled - no need to pass flag
        # Pass verbose flag to pipeline stages (from pipeline subparser)
        pipeline_verbose = getattr(args, "verbose", False)
        run_stage("pipeline", args=cli_args, verbose=pipeline_verbose)
    elif args.cmd == "read":
        client = get_mongo_client()
        db = client[DB_NAME]
        fields = (
            [f.strip() for f in args.fields.split(",") if f.strip()]
            if getattr(args, "fields", None)
            else None
        )
        docs = read_collection(
            db,
            collection_name=args.collection,
            video_id=getattr(args, "video_id", None),
            fields=fields,
            limit=getattr(args, "limit", 100),
        )
        print(json.dumps(docs, default=str, indent=2))
    elif args.cmd == "wait_index":
        wait_for_index_ready("embedding_index")
    elif args.cmd == "backfill_transcript":
        run_stage("backfill_transcript", video_id=args.video_id)
    else:
        if args.cmd == "enrich":
            run_stage("enrich", llm=bool(getattr(args, "llm", False)))
        elif args.cmd == "chunk":
            run_stage("chunk", llm=bool(getattr(args, "llm", False)))
        elif args.cmd == "redundancy":
            run_stage("redundancy", llm=bool(getattr(args, "llm", False)))
        elif args.cmd == "trust":
            run_stage("trust", llm=bool(getattr(args, "llm", False)))
        else:
            run_stage(args.cmd)


if __name__ == "__main__":
    main()
