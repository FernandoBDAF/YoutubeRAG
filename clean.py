import os
from typing import Any

from dotenv import load_dotenv
from pymongo import MongoClient

from utils import get_mongo_client
from config.paths import DB_NAME, COLL_RAW_VIDEOS, COLL_CLEANED


def _llm_clean_text(agent_cls, video_id: str, raw_text: str) -> dict:
    system_prompt = (
        "You are TranscriptCleanAgent. You specialize in converting auto-generated "
        "video transcripts into clean, human-readable educational text. Preserve "
        "factual content and code syntax while improving punctuation, casing, and "
        "sentence boundaries. Do not paraphrase or add commentary. Maintain the "
        "same language as the input."
    )
    user_prompt = (
        "INPUT TRANSCRIPT:\n"
        f"{raw_text[:120000]}\n\n"
        "TASKS:\n"
        "1. Fix punctuation and casing.\n"
        '2. Remove filler words ("uh", "um", "you know") and false starts.\n'
        "3. Split into natural paragraphs (around 4–6 sentences each).\n"
        "4. Keep all code or command examples intact, preserving indentation.\n"
        "5. If you find malformed code, wrap it in triple backticks with the correct language.\n\n"
        "OUTPUT: A single cleaned text suitable to be split into paragraphs."
    )
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

    # Simple stub or LLM-based cleaner
    for doc in raw.find({"transcript_raw": {"$exists": True, "$ne": None}}).limit(20):
        video_id = doc.get("video_id")
        text = (doc.get("transcript_raw") or "").strip()
        if not video_id or not text:
            continue
        if use_llm:
            # Use dedicated TranscriptCleanAgent wrapper
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
        print(f"Cleaned {video_id} → {COLL_CLEANED} (llm={use_llm})")


if __name__ == "__main__":
    main()
