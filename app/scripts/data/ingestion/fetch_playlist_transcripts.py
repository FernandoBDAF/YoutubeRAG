"""
Fetch transcripts for a YouTube playlist and upsert them into MongoDB.

Uses the YouTube Data API to list playlist items and youtube_transcript_api
to pull captions (preferring English, then translating to English when
possible). Segments are stitched with simple pause-based punctuation so the
text is easier to chunk and embed downstream.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Iterable, List, Optional, Sequence

from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pymongo import MongoClient
from youtube_transcript_api import YouTubeTranscriptApi, Transcript, NoTranscriptFound


def list_playlist_video_ids(api_key: str, playlist_id: str, limit: int) -> List[str]:
    youtube = build("youtube", "v3", developerKey=api_key)
    ids: List[str] = []
    page_token: Optional[str] = None
    while len(ids) < limit:
        try:
            resp = (
                youtube.playlistItems()
                .list(
                    part="contentDetails",
                    playlistId=playlist_id,
                    maxResults=50,
                    pageToken=page_token,
                )
                .execute()
            )
        except HttpError as exc:
            print(f"[playlist] YouTube API error: {exc}")
            break
        for item in resp.get("items", []):
            vid = item.get("contentDetails", {}).get("videoId")
            if vid:
                ids.append(vid)
                if len(ids) >= limit:
                    break
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return ids


def _choose_transcript(
    transcripts: Iterable[Transcript], languages: Sequence[str]
) -> Optional[Transcript]:
    # Prefer manually created in target languages, then generated, then translatable to en.
    langs = list(languages) or ["en", "en-US", "en-GB"]
    for t in transcripts:
        if not t.is_generated and t.language_code in langs:
            return t
    for t in transcripts:
        if t.language_code in langs:
            return t
    for t in transcripts:
        if t.is_translatable:
            try:
                return t.translate("en")
            except Exception:
                continue
    return None


def stitch_segments(segments: List[object], gap_threshold: float = 1.5) -> str:
    """
    Join transcript segments with simple pause-aware punctuation.

    Adds a period when the silence between segments exceeds ``gap_threshold``
    seconds and the current text does not already end with terminal punctuation.
    """
    if not segments:
        return ""

    pieces: List[str] = []
    last_end: float = 0.0
    for seg in segments:
        if hasattr(seg, "text"):
            text = str(getattr(seg, "text", "") or "").strip()
            start = float(getattr(seg, "start", 0.0) or 0.0)
            duration = float(getattr(seg, "duration", 0.0) or 0.0)
        elif isinstance(seg, dict):
            text = str(seg.get("text", "") or "").strip()
            start = float(seg.get("start", 0.0) or 0.0)
            duration = float(seg.get("duration", 0.0) or 0.0)
        else:
            text = str(seg or "").strip()
            start = 0.0
            duration = 0.0
        if not text:
            continue
        gap = start - last_end
        if pieces:
            if gap > gap_threshold and not re.search(r"[.!?]$", pieces[-1]):
                pieces[-1] = pieces[-1].rstrip() + "."
            pieces.append(" " + text)
        else:
            pieces.append(text)
        last_end = start + duration

    combined = "".join(pieces)
    # Normalize whitespace and ensure terminal punctuation.
    combined = " ".join(combined.split())
    if combined and not re.search(r"[.!?]$", combined):
        combined += "."
    return combined


def fetch_transcript_text(video_id: str, languages: Sequence[str]) -> Optional[str]:
    """
    Return stitched transcript text or None if unavailable.

    Fallback order:
    1) YouTubeTranscriptApi().list(...) (newer youtube-transcript-api)
    2) YouTubeTranscriptApi().fetch(...) (direct fetch shortcut)
    """
    api = YouTubeTranscriptApi()

    # Preferred: list transcripts and choose manually (handles translation when available)
    try:
        transcript_list = api.list(video_id)
        chosen = _choose_transcript(transcript_list, languages)
        if chosen is not None:
            try:
                segments = chosen.fetch()
                text = stitch_segments(segments)
                if text.strip():
                    return text
                print(f"[transcript] Empty transcript after stitching for {video_id}")
                return None
            except Exception as exc:
                print(f"[transcript] Failed to fetch transcript for {video_id}: {exc}")
        else:
            print(f"[transcript] No usable transcript for {video_id}")
    except NoTranscriptFound:
        print(f"[transcript] No transcripts available for {video_id}")
    except Exception as exc:
        print(f"[transcript] Failed to list transcripts for {video_id}: {exc}")

    # Fallback: direct fetch shortcut (may succeed when list had issues)
    try:
        segments = api.fetch(video_id, languages=list(languages) or None)
        text = stitch_segments(segments)
        if text.strip():
            return text
    except NoTranscriptFound:
        print(f"[transcript] No transcripts available (fallback fetch) for {video_id}")
    except Exception as exc:
        print(f"[transcript] Fallback fetch failed for {video_id}: {exc}")
    return None


def upsert_transcript(
    client: MongoClient,
    db_name: str,
    video_id: str,
    transcript_text: str,
    language: str,
    collection: str = "raw_videos",
) -> None:
    coll = client[db_name][collection]
    coll.update_one(
        {"video_id": video_id},
        {"$set": {"transcript_raw": transcript_text, "transcript_language": language}},
        upsert=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch YouTube transcripts for a playlist and upsert into MongoDB."
    )
    parser.add_argument("--playlist_id", required=True, help="YouTube playlist ID")
    parser.add_argument("--max", type=int, default=10, help="Max videos to process")
    parser.add_argument(
        "--languages",
        default="en,en-US,en-GB",
        help="Comma-separated language preferences (fallback to translation)",
    )
    parser.add_argument(
        "--gap-threshold",
        type=float,
        default=1.5,
        help="Seconds of silence to trigger sentence break insertion",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Fetch and stitch but do not write to Mongo"
    )
    args = parser.parse_args()

    load_dotenv(Path("..") / ".env")

    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise SystemExit("YOUTUBE_API_KEY is required.")
    mongo_uri = os.getenv("MONGODB_ATLAS_URI") or os.getenv("MONGODB_URI")
    if not mongo_uri:
        raise SystemExit("MONGODB_ATLAS_URI or MONGODB_URI is required.")
    db_name = os.getenv("ATLAS_DB_NAME") or os.getenv("MONGODB_DB") or "media_rag"

    languages = [lang.strip() for lang in args.languages.split(",") if lang.strip()]

    video_ids = list_playlist_video_ids(api_key, args.playlist_id, args.max)
    if not video_ids:
        raise SystemExit(f"No videos found for playlist {args.playlist_id}")

    print(f"[playlist] Found {len(video_ids)} video(s) (max={args.max})")
    client = MongoClient(mongo_uri)

    processed = 0
    for vid in video_ids:
        text = fetch_transcript_text(vid, languages)
        if not text:
            continue
        print(f"[upsert] video_id={vid} chars={len(text)}")
        if not args.dry_run:
            upsert_transcript(client, db_name, vid, text, language=languages[0] or "en")
        processed += 1

    print(f"[done] Processed {processed} / {len(video_ids)} with transcripts")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
