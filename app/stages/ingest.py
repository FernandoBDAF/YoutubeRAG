import os
import re
import sys
import argparse
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
)

try:
    from app.services.utils import get_mongo_client
except ModuleNotFoundError:
    import sys as _sys, os as _os

    _sys.path.append(
        _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
    )
    from app.services.utils import get_mongo_client
from config.paths import (
    DB_NAME,
    COLL_RAW_VIDEOS,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ingest YouTube videos → MongoDB raw_videos"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--playlist_id", type=str, help="YouTube playlist ID to ingest")
    group.add_argument(
        "--channel_id", type=str, help="YouTube channel ID to ingest recent uploads"
    )
    group.add_argument(
        "--video_ids", type=str, nargs="+", help="One or more YouTube video IDs"
    )
    parser.add_argument(
        "--max", type=int, default=10, help="Max videos to ingest (default 10)"
    )
    return parser.parse_args()


def get_youtube_client() -> Any:
    key = os.getenv("YOUTUBE_API_KEY")
    if not key:
        raise RuntimeError("YOUTUBE_API_KEY is not set")
    return build("youtube", "v3", developerKey=key)


def get_uploads_playlist_id(youtube: Any, channel_id: str) -> Optional[str]:
    # Fetch the uploads playlist for the channel
    resp = youtube.channels().list(part="contentDetails", id=channel_id).execute()
    items = resp.get("items", [])
    if not items:
        return None
    return items[0]["contentDetails"]["relatedPlaylists"].get("uploads")


def list_videos_in_playlist(youtube: Any, playlist_id: str, limit: int) -> List[str]:
    video_ids: List[str] = []
    page_token: Optional[str] = None
    while len(video_ids) < limit:
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
        except HttpError as e:
            print(f"YouTube API error for playlist_id={playlist_id}: {e}")
            break
        except Exception as e:
            print(f"Unexpected error listing playlist items: {e}")
            break
        for it in resp.get("items", []):
            vid = it.get("contentDetails", {}).get("videoId")
            if vid:
                video_ids.append(vid)
                if len(video_ids) >= limit:
                    break
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return video_ids


def list_recent_videos_for_channel(
    youtube: Any, channel_id: str, limit: int
) -> List[str]:
    uploads = get_uploads_playlist_id(youtube, channel_id)
    if not uploads:
        return []
    return list_videos_in_playlist(youtube, uploads, limit)


def fetch_video_details(
    youtube: Any, video_ids: List[str]
) -> Dict[str, Dict[str, Any]]:
    details: Dict[str, Dict[str, Any]] = {}
    # Batch in chunks of 50
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i : i + 50]
        resp = (
            youtube.videos()
            .list(
                part="snippet,contentDetails,statistics",
                id=",".join(batch),
                maxResults=50,
            )
            .execute()
        )
        for it in resp.get("items", []):
            vid = it.get("id")
            if not vid:
                continue
            details[vid] = it
    return details


_ISO_DURATION_RE = re.compile(
    r"PT(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?"
)


def parse_iso8601_duration(duration: str) -> Optional[int]:
    if not duration:
        return None
    m = _ISO_DURATION_RE.fullmatch(duration)
    if not m:
        return None
    hours = int(m.group("hours") or 0)
    minutes = int(m.group("minutes") or 0)
    seconds = int(m.group("seconds") or 0)
    return hours * 3600 + minutes * 60 + seconds


def fetch_transcript_text(video_id: str) -> Tuple[Optional[str], Optional[str]]:
    try:
        # Try English/manual first, then generated, then any available
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        entries = None
        lang: Optional[str] = None

        # 1) Preferred explicit transcript (any provider) in English variants
        try:
            tr = transcript_list.find_transcript(["en", "en-US", "en-GB"])  # type: ignore
            entries = tr.fetch()
            lang = tr.language
        except Exception:
            pass

        # 2) Manually created (human) transcript in English variants
        if entries is None:
            try:
                tr = transcript_list.find_manually_created_transcript(["en", "en-US", "en-GB"])  # type: ignore
                entries = tr.fetch()
                lang = tr.language
            except Exception:
                pass

        # 3) Auto-generated transcript in English variants
        if entries is None:
            try:
                tr = transcript_list.find_generated_transcript(["en", "en-US", "en-GB"])  # type: ignore
                entries = tr.fetch()
                lang = tr.language
            except Exception:
                pass

        # 4) Fallback: first available transcript of any kind/language
        if entries is None:
            try:
                tr_any = next(iter(transcript_list), None)
                if tr_any is not None:
                    entries = tr_any.fetch()
                    lang = tr_any.language
            except Exception:
                pass

        if entries is None:
            return None, None

        text = "\n".join(e.get("text", "") for e in entries)
        return text, lang
    except (TranscriptsDisabled, NoTranscriptFound):
        return None, None
    except Exception:
        return None, None


def compute_engagement_score(stats: Dict[str, Any]) -> Optional[float]:
    try:
        views = float(stats.get("viewCount", 0))
        likes = float(stats.get("likeCount", 0))
        comments = float(stats.get("commentCount", 0))
        if views <= 0:
            return None
        return min(1.0, (likes * 2.0 + comments * 3.0) / max(100.0, views))
    except Exception:
        return None


def to_raw_video_doc(
    item: Dict[str, Any], transcript_text: Optional[str], transcript_lang: Optional[str]
) -> Dict[str, Any]:
    snippet = item.get("snippet", {})
    stats = item.get("statistics", {})
    content = item.get("contentDetails", {})

    published_at = snippet.get("publishedAt")
    title = snippet.get("title")
    description = snippet.get("description")
    channel_id = snippet.get("channelId")
    channel_title = snippet.get("channelTitle")
    tags = snippet.get("tags", []) or []
    thumbnails = (snippet.get("thumbnails", {}) or {}).copy()
    thumb_url = None
    for key in ["maxres", "standard", "high", "medium", "default"]:
        if key in thumbnails and thumbnails[key].get("url"):
            thumb_url = thumbnails[key]["url"]
            break

    return {
        "video_id": item.get("id"),
        "title": title,
        "description": description,
        "channel_id": channel_id,
        "channel_title": channel_title,
        "published_at": published_at,
        "duration_seconds": parse_iso8601_duration(content.get("duration")),
        "stats": {
            "viewCount": int(stats.get("viewCount", 0) or 0),
            "likeCount": int(stats.get("likeCount", 0) or 0),
            "commentCount": int(stats.get("commentCount", 0) or 0),
        },
        "keywords": tags,
        "engagement_score": compute_engagement_score(stats),
        "transcript_raw": transcript_text,
        "transcript_language": transcript_lang,
        "thumbnail_url": thumb_url,
        "fetched_at": datetime.utcnow().isoformat(),
    }


def upsert_raw_video(db, doc: Dict[str, Any]) -> None:
    coll = db[COLL_RAW_VIDEOS]
    coll.update_one({"video_id": doc["video_id"]}, {"$set": doc}, upsert=True)


def main() -> None:
    load_dotenv()
    args = parse_args()
    youtube = get_youtube_client()

    # Resolve video IDs
    if args.playlist_id:
        video_ids = list_videos_in_playlist(youtube, args.playlist_id, args.max)
    elif args.channel_id:
        video_ids = list_recent_videos_for_channel(youtube, args.channel_id, args.max)
    else:
        video_ids = args.video_ids[: args.max]

    if not video_ids:
        print("No videos to ingest.")
        sys.exit(0)

    details = fetch_video_details(youtube, video_ids)

    client = get_mongo_client()
    db = client[DB_NAME]

    success = 0
    for vid in video_ids:
        item = details.get(vid)
        if not item:
            continue
        transcript_text, transcript_lang = fetch_transcript_text(vid)
        doc = to_raw_video_doc(item, transcript_text, transcript_lang)
        upsert_raw_video(db, doc)
        success += 1
        print(f"Ingested {vid}: title='{doc.get('title','')[:60]}'")

    print(
        f"Done. Upserted {success} / {len(video_ids)} videos into '{COLL_RAW_VIDEOS}'."
    )


if __name__ == "__main__":
    main()
