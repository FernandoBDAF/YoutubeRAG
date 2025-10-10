import os
import sys
import argparse
from datetime import datetime, timezone
from typing import Optional

from dotenv import load_dotenv

try:
    from app.services.utils import get_mongo_client
except ModuleNotFoundError:
    import sys as _sys, os as _os

    _sys.path.append(
        _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
    )
    from app.services.utils import get_mongo_client

from config.paths import DB_NAME, COLL_RAW_VIDEOS


def _env_bool(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return str(v).strip().lower() in {"1", "true", "yes", "on"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Backfill a single video's transcript into raw_videos"
    )
    parser.add_argument("--video_id", required=False, help="YouTube video ID")
    return parser.parse_args()


def fetch_transcript_text(video_id: str) -> Optional[str]:
    try:
        from app.services.transcripts import get_transcript

        url = f"https://www.youtube.com/watch?v={video_id}"
        items = get_transcript(url)
        if not items:
            print(
                f"No transcript from YouTube for {video_id}, url={url}"
            )
            return None
        text = "\n".join(seg.get("text", "") for seg in items if seg.get("text"))
        text = (text or "").strip()
        if not text:
            print(
                f"Transcript loader returned empty text for {video_id}, url={url}"
            )
            return None
        return text
    except Exception as e:
        print(f"Error fetching transcript for {video_id}: {e}")
        return None


def main() -> None:
    load_dotenv()
    args = parse_args()

    client = get_mongo_client()
    db = client[DB_NAME]
    coll = db[COLL_RAW_VIDEOS]

    video_id = args.video_id

    if not video_id:
        docs = list(coll.find({"transcript_raw": None}))
        backfilled = 0
        print(f"Backfilling {len(docs)} transcripts")
        for doc in docs:
            allow_upsert_existing = _env_bool("INGEST_UPSERT_EXISTING", False)
            if (doc.get("transcript_raw") or "") and not allow_upsert_existing:
                print(f"Transcript exists; skipping {video_id} (INGEST_UPSERT_EXISTING=false)")
                continue

            text = fetch_transcript_text(doc.get("video_id"))
            if not text:
                # Better logs already printed in fetch_transcript_text
                continue

            update = {
                "transcript_raw": text,
                "transcript_language": None,  # language not provided by loader
                "fetched_at": datetime.now(timezone.utc),
            }
            coll.update_one({"video_id": video_id}, {"$set": update}, upsert=False)
            print(f"Backfilled transcript for {video_id} (chars={len(text)})")
            backfilled += 1
        print(f"Backfilled {backfilled} transcripts")
        sys.exit(0)

    doc = coll.find_one({"video_id": video_id})
    if not doc:
        print(f"No raw_videos document for {video_id}")
        sys.exit(1)

    allow_upsert_existing = _env_bool("INGEST_UPSERT_EXISTING", False)
    if (doc.get("transcript_raw") or "") and not allow_upsert_existing:
        print(f"Transcript exists; skipping {video_id} (INGEST_UPSERT_EXISTING=false)")
        sys.exit(0)

    text = fetch_transcript_text(video_id)
    if not text:
        # Better logs already printed in fetch_transcript_text
        sys.exit(0)

    update = {
        "transcript_raw": text,
        "transcript_language": None,  # language not provided by loader
        "fetched_at": datetime.now(timezone.utc),
    }
    coll.update_one({"video_id": video_id}, {"$set": update}, upsert=False)
    print(f"Backfilled transcript for {video_id} (chars={len(text)})")


if __name__ == "__main__":
    main()
