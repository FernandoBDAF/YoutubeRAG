import os
from typing import Dict, List

from dotenv import load_dotenv
from pymongo import MongoClient


def get_mongo_client() -> MongoClient:
    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise RuntimeError("MONGODB_URI not set")
    return MongoClient(uri)


def main() -> None:
    load_dotenv()
    db_name = os.getenv("MONGODB_DB", "mongo_hack")
    client = get_mongo_client()
    db = client[db_name]
    cleaned = db["cleaned_transcripts"]
    enriched = db["enriched_transcripts"]
    raw = db["raw_videos"]

    cleaned_ids = set(
        d.get("video_id")
        for d in cleaned.find({}, {"video_id": 1})
        if d.get("video_id")
    )
    enriched_ids = set(
        d.get("video_id")
        for d in enriched.find({}, {"video_id": 1})
        if d.get("video_id")
    )
    gaps = sorted(cleaned_ids - enriched_ids)

    print(f"cleaned={len(cleaned_ids)} enriched={len(enriched_ids)} gaps={len(gaps)}")
    if not gaps:
        print("No gaps — all cleaned transcripts have an enriched entry.")
        return

    rows: List[Dict[str, str]] = []
    for vid in gaps:
        rv = raw.find_one({"video_id": vid}) or {}
        title = (rv.get("title") or "")[:80]
        channel = rv.get("channel_id") or ""
        duration = rv.get("duration_seconds") or rv.get("duration") or 0
        has_tx = bool(rv.get("transcript_raw"))
        rows.append(
            {
                "video_id": vid,
                "title": title,
                "channel_id": channel,
                "duration_s": str(duration),
                "has_transcript": str(has_tx),
            }
        )

    # Simple pattern hints
    by_channel: Dict[str, int] = {}
    long_count = 0
    missing_tx = 0
    for r in rows:
        by_channel[r["channel_id"]] = by_channel.get(r["channel_id"], 0) + 1
        try:
            if int(r["duration_s"]) > 7200:
                long_count += 1
        except Exception:
            pass
        if r["has_transcript"].lower() == "false":
            missing_tx += 1

    print("Top channels by missing enrich:")
    for ch, cnt in sorted(by_channel.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"- {ch or '—'}: {cnt}")
    print(f"Long videos (>2h) among gaps: {long_count}")
    print(f"Missing transcript among gaps: {missing_tx}")

    try:
        import pandas as pd

        import io

        df = pd.DataFrame(rows)
        buf = io.StringIO()
        df.to_csv(buf, index=False)
        print("\nCSV preview (first 10 rows):\n")
        print("\n".join(buf.getvalue().splitlines()[:12]))
    except Exception:
        pass


if __name__ == "__main__":
    main()
