import os
import argparse
import subprocess
import json
from dotenv import load_dotenv

from app.services.utils import get_mongo_client, read_collection
from config.paths import DB_NAME
from config.seed.seed_indexes import (
    ensure_collections_and_indexes,
    wait_for_index_ready,
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
        cmd = [py, "app/stages/chunk_embed.py"]
        if use_llm:
            cmd.append("--llm")
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
        # ingest -> clean -> enrich -> chunk -> redundancy -> trust
        args = kwargs.get("args") or []
        run_stage("ingest", args=args)
        run_stage("clean", llm=kwargs.get("llm", False))
        run_stage("enrich", llm=kwargs.get("llm", False))
        run_stage("chunk", llm=kwargs.get("llm", False))
        try:
            wait_for_index_ready("embedding_index")
        except Exception:
            pass
        run_stage("redundancy", llm=kwargs.get("llm", False))
        run_stage("trust", llm=kwargs.get("llm", False))
    elif stage == "ui":
        subprocess.run(
            ["streamlit", "run", "streamlit_app.py"],
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
    sub.add_parser("wait_index", help="Wait until vector index is READY")
    sub.add_parser("health", help="Run health checks")

    args = parser.parse_args()

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
        run_stage("pipeline", args=cli_args, llm=bool(args.llm))
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
