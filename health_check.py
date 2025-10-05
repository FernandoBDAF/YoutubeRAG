import os
from typing import Tuple

from dotenv import load_dotenv
from pymongo import MongoClient

from utils import get_mongo_client
from config.paths import (
    DB_NAME,
    COLL_RAW_VIDEOS,
    COLL_CLEANED,
    COLL_ENRICHED,
    COLL_CHUNKS,
)


def check_env() -> Tuple[bool, list[str]]:
    issues = []
    for key in ["MONGODB_URI", "MONGODB_DB", "VOYAGE_API_KEY"]:
        if not os.getenv(key):
            issues.append(f"Missing env: {key}")
    return (len(issues) == 0, issues)


def check_db() -> Tuple[bool, list[str]]:
    issues = []
    try:
        client: MongoClient = get_mongo_client()
        db = client[DB_NAME]
        # try simple commands
        db.list_collection_names()
    except Exception as e:
        issues.append(f"DB error: {e}")
    return (len(issues) == 0, issues)


def check_collections() -> Tuple[bool, list[str]]:
    issues = []
    client: MongoClient = get_mongo_client()
    db = client[DB_NAME]
    counts = {}
    for name in [COLL_RAW_VIDEOS, COLL_CLEANED, COLL_ENRICHED, COLL_CHUNKS]:
        try:
            counts[name] = db[name].estimated_document_count()
        except Exception as e:
            issues.append(f"Collection error {name}: {e}")
    # minimal expectations: raw and chunks may be zero, but report
    print("Counts:", counts)
    return (len(issues) == 0, issues)


def check_embeddings() -> Tuple[bool, list[str]]:
    issues = []
    client: MongoClient = get_mongo_client()
    db = client[DB_NAME]
    doc = db[COLL_CHUNKS].find_one({}, {"embedding": 1})
    if doc and isinstance(doc.get("embedding"), list):
        dim = len(doc["embedding"]) if doc["embedding"] else 0
        print("Sample embedding dim:", dim)
        if dim == 0:
            issues.append("Embeddings present but zero-length vector")
    else:
        print("No sample embedding found (ok if not yet embedded)")
    return (len(issues) == 0, issues)


def main() -> None:
    load_dotenv()
    ok_env, env_issues = check_env()
    ok_db, db_issues = check_db()
    ok_col, col_issues = check_collections()
    ok_emb, emb_issues = check_embeddings()
    all_ok = ok_env and ok_db and ok_col and ok_emb
    if not all_ok:
        print("Health check FAILED")
        for s in [env_issues, db_issues, col_issues, emb_issues]:
            for i in s:
                print("-", i)
        raise SystemExit(1)
    print("Health check OK")


if __name__ == "__main__":
    main()
