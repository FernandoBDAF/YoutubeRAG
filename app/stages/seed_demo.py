import subprocess
import sys


def run(cmd: list[str]) -> None:
    print("$", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main() -> None:
    # Adjust playlist_id or channel_id before running
    run(
        [
            sys.executable,
            "Mongo_Hack/app/stages/ingest.py",
            "--playlist_id",
            "PLdlA6gN07G8dyQs86ebumuNiiqcyfXb8f",
            "--max",
            "5",
        ]
    )
    run([sys.executable, "Mongo_Hack/app/stages/clean.py"])
    run([sys.executable, "Mongo_Hack/app/stages/enrich.py"])
    run([sys.executable, "Mongo_Hack/app/stages/chunk_embed.py"])
    run([sys.executable, "Mongo_Hack/app/stages/redundancy.py"])
    run([sys.executable, "Mongo_Hack/app/stages/trust.py"])


if __name__ == "__main__":
    main()
