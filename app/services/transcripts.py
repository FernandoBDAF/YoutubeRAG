from typing import List, Dict, Optional

from langchain_community.document_loaders import YoutubeLoader


def get_transcript(
    video_url: str,
    max_retries: int = 0,
) -> List[Dict]:
    """Fetch transcript via LangChain YoutubeLoader (transcript-only).

    Returns a list of {"text": str, "metadata": dict} items. Empty list if unavailable.
    """
    last_err: Optional[Exception] = None
    for _ in range(max_retries + 1):
        try:
            loader = YoutubeLoader.from_youtube_url(
                video_url,
                add_video_info=False,  # avoid pytube dependency/HTTP issues
            )
            docs = loader.load()
            return [
                {"text": d.page_content or "", "metadata": d.metadata or {}}
                for d in docs
                if (d.page_content or "").strip()
            ]
        except Exception as e:  # pragma: no cover - best effort
            last_err = e
            continue
    # Swallow error; upstream can decide how to handle missing transcript
    return []


