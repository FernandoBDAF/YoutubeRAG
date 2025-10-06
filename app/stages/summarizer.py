import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from pymongo import MongoClient

from app.services.utils import get_mongo_client
from config.paths import DB_NAME, COLL_CHUNKS


def build_context_from_hits(hits: List[Dict[str, Any]]) -> str:
    parts: List[str] = []
    for h in hits:
        parts.append(f"({h.get('video_id')}:{h.get('chunk_id')})\n{h.get('text','')}")
    return "\n\n".join(parts)


def summarize_topic(topic_regex: str, limit: int = 10) -> Dict[str, Any]:
    client: MongoClient = get_mongo_client()
    db = client[DB_NAME]
    col = db[COLL_CHUNKS]
    filters = {"metadata.tags": {"$regex": topic_regex, "$options": "i"}}
    hits = list(
        col.find(filters, {"video_id": 1, "chunk_id": 1, "text": 1}).limit(limit)
    )
    context = build_context_from_hits(hits)
    # For now return raw concatenation; UI/LLM can consume this
    return {"context": context, "count": len(hits)}


def save_summary(topic_regex: str, context: str) -> str:
    client: MongoClient = get_mongo_client()
    db = client[DB_NAME]
    coll = db.get_collection("summaries")
    doc = {"topic_regex": topic_regex, "context": context}
    res = coll.insert_one(doc)
    return str(res.inserted_id)


if __name__ == "__main__":
    load_dotenv()
    out = summarize_topic("react|state")
    print(out["context"][:500])
