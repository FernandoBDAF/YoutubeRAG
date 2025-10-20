#!/usr/bin/env python3
"""
Standalone transcript fetcher for testing.

Usage:
  python Mongo_Hack/scripts/index.py --video_id <VIDEO_ID> [--languages en en-US]
  python Mongo_Hack/scripts/index.py --url https://www.youtube.com/watch?v=<VIDEO_ID>

Outputs the transcript as plain text (stdout). Exits 0 on success, 1 otherwise.
"""

import argparse
import sys
from typing import List


def fetch_with_youtube_transcript_api(video_id: str, langs: List[str]) -> str:
    try:
        from youtube_transcript_api import YouTubeTranscriptApi

        # Try requested languages in order
        for lang in langs:
            try:
                transcript = YouTubeTranscriptApi.get_transcript(
                    video_id, languages=[lang]
                )
                print("got with youtube_transcript_api")
                return "\n".join(
                    item.get("text", "") for item in transcript if item.get("text")
                )
            except Exception:
                continue
        # Fallback: any available
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        print("got with youtube_transcript_api fallback")
        return "\n".join(
            item.get("text", "") for item in transcript if item.get("text")
        )
    except Exception:
        return ""


def fetch_with_langchain_loader(video_id: str, langs: List[str]) -> str:
    try:
        from langchain_community.document_loaders import YoutubeLoader

        url = f"https://www.youtube.com/watch?v={video_id}"
        loader = YoutubeLoader.from_youtube_url(
            url, add_video_info=False, language=langs
        )
        docs = loader.load()
        parts = [d.page_content or "" for d in docs if (d.page_content or "").strip()]
        return "\n".join(parts)
    except Exception:
        return ""


def main() -> int:
    p = argparse.ArgumentParser(
        description="Fetch YouTube transcript (standalone test script)"
    )
    p.add_argument("--video_id", help="YouTube video id (e.g., dQw4w9WgXcQ)")
    p.add_argument("--url", help="YouTube video url (alternative to --video_id)")
    p.add_argument(
        "--languages",
        nargs="*",
        default=["en", "en-US", "en-GB"],
        help="Preferred languages order",
    )
    args = p.parse_args()

    vid = args.video_id
    if not vid and args.url:
        # naive parse
        import urllib.parse as _url

        q = _url.urlparse(args.url)
        if q.netloc.endswith("youtube.com"):
            qs = _url.parse_qs(q.query)
            vid = (qs.get("v") or [None])[0]
        elif q.netloc == "youtu.be":
            vid = q.path.lstrip("/")
    if not vid:
        print("Error: Provide --video_id or --url", file=sys.stderr)
        return 1

    # First try youtube_transcript_api
    text = fetch_with_youtube_transcript_api(vid, args.languages)
    if not text:
        # Fallback to LangChain loader
        text = fetch_with_langchain_loader(vid, args.languages)

    if not text:
        print("", end="")
        return 1
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
