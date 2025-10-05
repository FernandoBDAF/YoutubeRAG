import os
import argparse
from dotenv import load_dotenv

from utils import get_mongo_client
from config.paths import DB_NAME


def run_stage(stage: str, **kwargs) -> None:
    import sys

    py = sys.executable
    if stage == "ingest":
        args = kwargs.get("args") or []
        os.system(f"{py} Mongo_Hack/ingest.py {' '.join(args)}")
    elif stage == "clean":
        use_llm = kwargs.get("llm", False)
        flag = " --llm" if use_llm else ""
        os.system(f"{py} Mongo_Hack/clean.py{flag}")
    elif stage == "enrich":
        use_llm = kwargs.get("llm", False)
        flag = " --llm" if use_llm else ""
        os.system(f"{py} Mongo_Hack/enrich.py{flag}")
    elif stage == "chunk":
        use_llm = kwargs.get("llm", False)
        flag = " --llm" if use_llm else ""
        os.system(f"{py} Mongo_Hack/chunk_embed.py{flag}")
    elif stage == "redundancy":
        use_llm = kwargs.get("llm", False)
        flag = " --llm" if use_llm else ""
        os.system(f"{py} Mongo_Hack/redundancy.py{flag}")
    elif stage == "trust":
        use_llm = kwargs.get("llm", False)
        flag = " --llm" if use_llm else ""
        os.system(f"{py} Mongo_Hack/trust.py{flag}")
    elif stage == "pipeline":
        # ingest -> clean -> enrich -> chunk -> redundancy -> trust
        args = kwargs.get("args") or []
        run_stage("ingest", args=args)
        run_stage("clean", llm=kwargs.get("llm", False))
        run_stage("enrich", llm=kwargs.get("llm", False))
        run_stage("chunk", llm=kwargs.get("llm", False))
        run_stage("redundancy", llm=kwargs.get("llm", False))
        run_stage("trust", llm=kwargs.get("llm", False))
    elif stage == "ui":
        os.system("streamlit run Mongo_Hack/streamlit_app.py")
    elif stage == "health":
        os.system(f"{py} Mongo_Hack/health_check.py")
    else:
        raise SystemExit(f"Unknown stage: {stage}")


def main() -> None:
    load_dotenv()
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
    sub.add_parser("ui", help="Launch Streamlit UI")
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
