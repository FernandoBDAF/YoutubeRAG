from typing import Any, Dict, Optional

import os
from googleapiclient.discovery import build


def get_youtube_metadata(video_id: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    key = api_key or os.getenv("YOUTUBE_API_KEY")
    if not key:
        raise RuntimeError("YOUTUBE_API_KEY is not set")
    yt = build("youtube", "v3", developerKey=key)
    resp = yt.videos().list(part="snippet,contentDetails,statistics", id=video_id).execute()
    items = resp.get("items", [])
    if not items:
        return {"video_id": video_id}
    it = items[0]
    snippet = it.get("snippet", {})
    stats = it.get("statistics", {})
    content = it.get("contentDetails", {})
    thumbs = snippet.get("thumbnails", {}) or {}
    thumb_url = None
    for key in ["maxres", "standard", "high", "medium", "default"]:
        if key in thumbs and thumbs[key].get("url"):
            thumb_url = thumbs[key]["url"]
            break
    return {
        "video_id": it.get("id"),
        "title": snippet.get("title"),
        "description": snippet.get("description"),
        "channel_id": snippet.get("channelId"),
        "channel_title": snippet.get("channelTitle"),
        "published_at": snippet.get("publishedAt"),
        "tags": snippet.get("tags", []) or [],
        "category_id": snippet.get("categoryId"),
        "thumbnail_url": thumb_url,
        "duration": content.get("duration"),
        "view_count": int(stats.get("viewCount", 0) or 0),
        "like_count": int(stats.get("likeCount", 0) or 0),
        "comment_count": int(stats.get("commentCount", 0) or 0),
    }


