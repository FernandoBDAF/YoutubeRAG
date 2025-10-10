import os
from typing import Optional, List, Dict, Any

from pymongo import MongoClient


def get_mongo_client(uri: Optional[str] = None) -> MongoClient:
    """Create a MongoClient from env or passed URI."""
    try:
        # Ensure Mongo_Hack/.env is honored even if caller didn't load it
        from dotenv import load_dotenv
        from pathlib import Path

        load_dotenv()
    except Exception:
        pass
    uri = uri or os.getenv("MONGODB_URI")
    if not uri:
        raise RuntimeError("MONGODB_URI is not set.")
    return MongoClient(uri)


def read_collection(
    db,
    collection_name: str,
    video_id: Optional[str] = None,
    fields: Optional[List[str]] = None,
    limit: int = 1000,
) -> List[Dict[str, Any]]:
    """Read documents from a MongoDB collection.

    Args:
        db: A database handle from MongoClient[DB_NAME].
        collection_name: Name of the collection to read.
        video_id: If provided, filter by this video_id; when None, return all.
        fields: List of field names to project; when empty/None, return all fields.
        limit: Max documents to return (safety default 1000).

    Returns:
        A list of dict documents.
    """
    coll = db[collection_name]
    query: Dict[str, Any] = {"video_id": video_id} if video_id else {}
    projection: Optional[Dict[str, int]] = None
    if fields:
        projection = {k: 1 for k in fields}
        # Always include _id unless explicitly excluded; keep default behavior
    cursor = coll.find(query, projection).limit(int(limit))
    return list(cursor)


def ensure_user_profiles(db) -> None:
    """Ensure user_profiles exists with a session_id unique index."""
    try:
        db["user_profiles"].create_index([("session_id", 1)], unique=True)
    except Exception:
        pass
