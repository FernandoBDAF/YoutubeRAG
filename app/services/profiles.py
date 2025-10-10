from typing import Any, Dict, Optional, List

from datetime import datetime, timezone

from app.services.utils import get_mongo_client
from config.paths import DB_NAME


def get_profile(session_id: str) -> Optional[Dict[str, Any]]:
    client = get_mongo_client()
    db = client[DB_NAME]
    doc = db["user_profiles"].find_one({"session_id": session_id})
    return doc


def upsert_profile(session_id: str, profile: Dict[str, Any]) -> None:
    client = get_mongo_client()
    db = client[DB_NAME]
    payload = {
        "session_id": session_id,
        **profile,
        "updated_at": datetime.now(timezone.utc),
    }
    db["user_profiles"].update_one(
        {"session_id": session_id}, {"$set": payload}, upsert=True
    )


def list_profiles(limit: int = 50) -> List[Dict[str, Any]]:
    client = get_mongo_client()
    db = client[DB_NAME]
    rows = list(
        db["user_profiles"]
        .find({}, {"session_id": 1, "name": 1, "persona": 1})
        .sort("updated_at", -1)
        .limit(int(limit))
    )
    return rows


def delete_profile(session_id: str) -> None:
    client = get_mongo_client()
    db = client[DB_NAME]
    db["user_profiles"].delete_one({"session_id": session_id})
