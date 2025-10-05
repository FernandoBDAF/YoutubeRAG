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
            "Mongo_Hack/ingest.py",
            "--playlist_id",
            "PLoROMvodv4rMC33Ucp4aumGNn8SpjEork",
            "--max",
            "5",
        ]
    )
    run([sys.executable, "Mongo_Hack/clean.py"])
    run([sys.executable, "Mongo_Hack/enrich.py"])
    run([sys.executable, "Mongo_Hack/chunk_embed.py"])
    run([sys.executable, "Mongo_Hack/redundancy.py"])
    run([sys.executable, "Mongo_Hack/trust.py"])


if __name__ == "__main__":
    main()
