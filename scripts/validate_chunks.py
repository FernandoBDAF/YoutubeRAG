import sys
from typing import Any, Dict

from pymongo import MongoClient
from dotenv import load_dotenv
import os


def validate_chunk(doc: Dict[str, Any]) -> Dict[str, Any]:
    issues = []
    required = ["video_id", "chunk_id", "chunk_text"]
    for k in required:
        if not doc.get(k):
            issues.append(f"missing:{k}")
    # basic types
    if "embedding" in doc and not isinstance(doc.get("embedding"), list):
        issues.append("embedding:not_list")
    return {"_id": doc.get("_id"), "video_id": doc.get("video_id"), "issues": issues}


def main(uri: str, db_name: str, coll_name: str = "video_chunks") -> int:
    client = MongoClient(uri)
    db = client[db_name]
    coll = db[coll_name]
    total = 0
    with_issues = 0
    for doc in coll.find(
        {}, {"video_id": 1, "chunk_id": 1, "chunk_text": 1, "embedding": 1}
    ):
        total += 1
        res = validate_chunk(doc)
        if res["issues"]:
            with_issues += 1
            print(res)
    print(f"Checked {total} documents; {with_issues} had issues")
    return 0


if __name__ == "__main__":
    # Usage: python scripts/validate_chunks.py mongodb://... mongo_hack video_chunks
    load_dotenv()
    uri = os.getenv("MONGODB_URI")
    db = sys.argv[1] if len(sys.argv) > 2 else "mongo_hack"
    coll = sys.argv[2] if len(sys.argv) > 3 else "video_chunks"
    raise SystemExit(main(uri, db, coll))

