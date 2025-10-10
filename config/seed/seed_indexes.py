import os
import json
import shutil
import subprocess
from pathlib import Path
from typing import List


REQUIRED_COLLECTIONS: List[str] = [
    "raw_videos",
    "video_chunks",
    "cleaned_transcripts",
    "enriched_transcripts",
    "memory_logs",
    "video_feedback",
    "chunk_feedback",
]


def ensure_collections_and_indexes(db) -> None:
    """Create base collections and the Vector Search index if missing.

    Uses Atlas CLI if available and PROJECT_ID/CLUSTER_NAME are set. Otherwise prints
    instructions to create the index via UI/CLI.
    """
    existing = set(db.list_collection_names())
    created_any = False
    for name in REQUIRED_COLLECTIONS:
        if name not in existing:
            db.create_collection(name)
            created_any = True

    # Ensure feedback indexes
    try:
        db["video_feedback"].create_index(
            [("video_id", 1), ("session_id", 1)], unique=True
        )
    except Exception:
        pass
    try:
        db["chunk_feedback"].create_index(
            [("chunk_id", 1), ("session_id", 1)], unique=True
        )
    except Exception:
        pass
    try:
        db["video_feedback"].create_index([("video_id", 1)])
        db["chunk_feedback"].create_index([("chunk_id", 1)])
    except Exception:
        pass

    # Vector index: try Atlas CLI if present
    atlas = shutil.which("atlas")
    project_id = os.getenv("PROJECT_ID")
    cluster_name = os.getenv("CLUSTER_NAME")
    db_name = os.getenv("MONGODB_DB", "mongo_hack")

    if atlas and project_id and cluster_name:
        # Check existing indexes
        try:
            list_cmd = [
                atlas,
                "clusters",
                "search",
                "indexes",
                "list",
                "--projectId",
                project_id,
                "--clusterName",
                cluster_name,
                "--db",
                db_name,
                "--collection",
                "video_chunks",
            ]
            result = subprocess.run(
                list_cmd, capture_output=True, text=True, check=False
            )
            if result.returncode != 0:
                # Fall through to create; some atlas versions return 0 only on READY
                pass
            if "embedding_index" not in result.stdout:
                definition = (Path(__file__).parent / "vector_index.json").resolve()
                # Load and override database/collection to match env/db
                try:
                    with open(definition, "r", encoding="utf-8") as f:
                        defn = json.load(f)
                except Exception:
                    defn = {}
                defn["database"] = db_name
                defn["collectionName"] = "video_chunks"
                effective = (
                    Path(__file__).parent / "vector_index.effective.json"
                ).resolve()
                with open(effective, "w", encoding="utf-8") as f:
                    json.dump(defn, f)
                create_cmd = [
                    atlas,
                    "clusters",
                    "search",
                    "indexes",
                    "create",
                    "--projectId",
                    project_id,
                    "--clusterName",
                    cluster_name,
                    "--file",
                    str(effective),
                ]
                subprocess.run(create_cmd, check=True)
                # Optionally wait for index readiness
                try:
                    wait_for_index_ready("embedding_index")
                except Exception:
                    pass
        except Exception:
            # Non-fatal: user can create via UI
            pass
    else:
        # CLI missing; print a friendly hint once
        print(
            "Atlas CLI not detected or env PROJECT_ID/CLUSTER_NAME missing. "
            "You can create the vector index via UI or set envs and Atlas CLI to enable auto-seed."
        )


def wait_for_index_ready(
    index_name: str, timeout_s: int = 300, poll_s: int = 5
) -> None:
    atlas = shutil.which("atlas")
    project_id = os.getenv("PROJECT_ID")
    cluster_name = os.getenv("CLUSTER_NAME")
    db_name = os.getenv("MONGODB_DB", "mongo_hack")
    if not (atlas and project_id and cluster_name):
        return
    import time

    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            cmd = [
                atlas,
                "clusters",
                "search",
                "indexes",
                "list",
                "--projectId",
                project_id,
                "--clusterName",
                cluster_name,
                "--db",
                db_name,
                "--collection",
                "video_chunks",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            out = result.stdout or ""
            if index_name in out and "READY" in out:
                return
        except Exception:
            pass
        time.sleep(poll_s)
    print(f"Index '{index_name}' did not become READY within {timeout_s}s")
