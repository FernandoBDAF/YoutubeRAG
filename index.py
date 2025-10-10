import os
import random
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from googleapiclient.discovery import build
from langchain_community.document_loaders import YoutubeLoader
import requests

# Basic transcript loading
load_dotenv()


def _parse_proxy_list(env_val: Optional[str]) -> List[str]:
    if not env_val:
        return []
    return [p.strip() for p in env_val.split(",") if p.strip()]


def _choose_proxy() -> Optional[str]:
    proxies = _parse_proxy_list(os.getenv("PROXY_LIST"))
    if not proxies:
        return None
    return random.choice(proxies)


def _apply_proxy_env(proxy: Optional[str]) -> None:
    # Clear first
    for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"):
        if k in os.environ:
            del os.environ[k]
    if proxy:
        os.environ["http_proxy"] = proxy
        os.environ["https_proxy"] = proxy
        os.environ["HTTP_PROXY"] = proxy
        os.environ["HTTPS_PROXY"] = proxy


def get_current_ip(timeout: int = 5) -> Optional[str]:
    try:
        r = requests.get("https://httpbin.org/ip", timeout=timeout)
        if r.ok:
            return r.json().get("origin")
    except Exception:
        return None
    return None


def rotate_proxy_and_probe(
    require_ip_change: bool = False, prev_ip: Optional[str] = None
) -> Optional[str]:
    """Pick a proxy from PROXY_LIST, set env, and optionally probe external IP.

    Returns the proxy string if applied, else None.
    """
    proxy = _choose_proxy()
    _apply_proxy_env(proxy)
    current_ip = get_current_ip()
    if current_ip:
        print(f"Proxy OK, egress IP: {current_ip}")
    if require_ip_change and prev_ip and current_ip == prev_ip:
        return None
    return proxy


def _fetch_public_proxies() -> List[str]:
    """Fetch a small list of public HTTP proxies (best-effort, unreliable)."""
    sources = [
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    ]
    proxies: List[str] = []
    for url in sources:
        try:
            resp = requests.get(url, timeout=5)
            if resp.ok:
                for line in resp.text.splitlines():
                    line = line.strip()
                    if line and ":" in line:
                        # Normalize to http://host:port
                        if not line.startswith("http"):
                            line = f"http://{line}"
                        proxies.append(line)
        except Exception:
            continue
        if len(proxies) >= 50:
            break
    random.shuffle(proxies)
    return proxies[:50]


def _try_apply_working_public_proxy(prev_ip: Optional[str]) -> Optional[str]:
    candidates = _fetch_public_proxies()
    for proxy in candidates:
        _apply_proxy_env(proxy)
        ip = get_current_ip(timeout=4)
        if ip and (prev_ip is None or ip != prev_ip):
            print(f"Using public proxy {proxy} (egress {ip})")
            return proxy
    return None


# Rotate proxy (if any) before transcript request
prev_ip = get_current_ip()
rotated = rotate_proxy_and_probe(require_ip_change=True, prev_ip=prev_ip)
if rotated is None:
    # Try to auto-discover a public proxy to force IP change
    _try_apply_working_public_proxy(prev_ip)


def load_transcript_with_retry(url: str, max_retries: int = 2):
    last_err: Optional[Exception] = None
    for attempt in range(max_retries + 1):
        try:
            loader = YoutubeLoader.from_youtube_url(
                url,
                add_video_info=False,
                language=["en", "en-US", "en-GB"],
            )
            return loader.load()
        except Exception as e:
            last_err = e
            # rotate proxy and retry
            prev_ip = get_current_ip()
            if rotate_proxy_and_probe(require_ip_change=True, prev_ip=prev_ip) is None:
                _try_apply_working_public_proxy(prev_ip)
            continue
    raise last_err if last_err else RuntimeError("Unknown transcript error")


docs = load_transcript_with_retry(
    "https://www.youtube.com/watch?v=ZA-tUyM_y7s", max_retries=2
)


def fetch_youtube_metadata(video_id: str) -> Dict[str, Any]:
    api_key = os.getenv("YOUTUBE_API_KEY", "").strip()
    if not api_key:
        return {}
    try:
        # The google client will respect HTTP(S)_PROXY env vars
        yt = build("youtube", "v3", developerKey=api_key)
        resp = (
            yt.videos()
            .list(part="snippet,contentDetails,statistics", id=video_id)
            .execute()
        )
        items = resp.get("items") or []
        if not items:
            return {}
        item = items[0]
        snippet = item.get("snippet", {})
        content = item.get("contentDetails", {})
        stats = item.get("statistics", {})
        thumbs = snippet.get("thumbnails", {})
        thumb = (
            thumbs.get("maxres")
            or thumbs.get("standard")
            or thumbs.get("high")
            or thumbs.get("medium")
            or thumbs.get("default")
            or {}
        )
        return {
            "video_id": video_id,
            "title": snippet.get("title"),
            "description": snippet.get("description"),
            "channel_title": snippet.get("channelTitle"),
            "published_at": snippet.get("publishedAt"),
            "tags": snippet.get("tags"),
            "category_id": snippet.get("categoryId"),
            "thumbnail_url": thumb.get("url"),
            "duration": content.get("duration"),
            "view_count": stats.get("viewCount"),
            "like_count": stats.get("likeCount"),
            "comment_count": stats.get("commentCount"),
        }
    except Exception:
        return {}


if docs:
    vid = docs[0].metadata.get("source")
    meta = fetch_youtube_metadata(vid) if vid else {}
    if meta:
        for d in docs:
            d.metadata.update(meta)

print(docs)
