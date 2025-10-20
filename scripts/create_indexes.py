from pymongo import MongoClient, ASCENDING
import sys
from dotenv import load_dotenv
import os


def main(uri: str, db_name: str = "mongo_hack") -> int:
    client = MongoClient(uri)
    db = client[db_name]
    chunks = db["video_chunks"]
    # Compound index for quick lookup
    print("Creating index on video_id + chunk_id ...")
    chunks.create_index(
        [("video_id", ASCENDING), ("chunk_id", ASCENDING)], name="vid_chunk"
    )
    # Optional norms/metadata index
    print("Creating index on embedding_dim and embedding_model ...")
    chunks.create_index(
        [("embedding_dim", ASCENDING), ("embedding_model", ASCENDING)],
        name="embed_meta",
    )
    print("Done")
    return 0


if __name__ == "__main__":
    # Usage: python scripts/create_indexes.py mongodb://...
    load_dotenv()
    raise SystemExit(main(os.getenv("MONGODB_URI")))

