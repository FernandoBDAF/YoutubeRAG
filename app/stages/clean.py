import os
from typing import Any

from dotenv import load_dotenv
from pymongo import MongoClient

try:
    from app.services.utils import get_mongo_client
except ModuleNotFoundError:
    import sys as _sys, os as _os

    _sys.path.append(
        _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
    )
    from app.services.utils import get_mongo_client
from config.paths import DB_NAME, COLL_RAW_VIDEOS, COLL_CLEANED


def _llm_clean_text(agent_cls, video_id: str, raw_text: str) -> dict:
    agent = agent_cls
    cleaned_text = agent.clean(raw_text)
    paragraphs = [
        {"start": 0.0, "end": 0.0, "text": p.strip()}
        for p in (cleaned_text or "").split("\n\n")
        if p.strip()
    ]
    return {
        "video_id": video_id,
        "cleaned_text": cleaned_text,
        "paragraphs": paragraphs,
    }


def main() -> None:
    load_dotenv()
    use_llm = os.getenv("CLEAN_WITH_LLM") == "1" or "--llm" in os.sys.argv
    client: MongoClient = get_mongo_client()
    db = client[DB_NAME]
    raw = db[COLL_RAW_VIDEOS]
    cleaned = db[COLL_CLEANED]

    processed = 0
    # Process all raws; fallback to description if transcript is missing
    for doc in raw.find({}).limit(50):
        video_id = doc.get("video_id")
        text = (doc.get("transcript_raw") or doc.get("description") or "").strip()
        if not video_id or not text:
            continue
        if use_llm:
            from agents.clean_agent import TranscriptCleanAgent

            payload = _llm_clean_text(TranscriptCleanAgent(), video_id, text)
        else:
            payload = {
                "video_id": video_id,
                "language": doc.get("transcript_language"),
                "cleaned_text": text,
                "paragraphs": [
                    {
                        "start": 0.0,
                        "end": 0.0,
                        "text": text,
                    }
                ],
            }
        cleaned.update_one({"video_id": video_id}, {"$set": payload}, upsert=True)
        processed += 1
        print(f"Cleaned {video_id} → {COLL_CLEANED} (llm={use_llm})")
    if processed == 0:
        print("No documents cleaned (no transcript/description found).")


if __name__ == "__main__":
    main()
