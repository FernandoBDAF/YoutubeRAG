import os
import re
from typing import Any, Dict, List

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
from config.paths import DB_NAME, COLL_CLEANED, COLL_ENRICHED


CODE_FENCE_RE = re.compile(r"```([a-zA-Z0-9_+-]*)[\s\S]*?```", re.MULTILINE)


def simple_tag_extract(text: str) -> List[str]:
    candidates = set()
    for kw in [
        "react",
        "python",
        "hooks",
        "state",
        "api",
        "context",
        "reducer",
        "typescript",
        "javascript",
        "node",
    ]:
        if re.search(rf"\b{re.escape(kw)}\b", text, flags=re.IGNORECASE):
            candidates.add(kw)
    return sorted(candidates)


def simple_code_blocks(text: str) -> List[Dict[str, str]]:
    blocks: List[Dict[str, str]] = []
    for m in CODE_FENCE_RE.finditer(text):
        lang = m.group(1) or ""
        blocks.append({"lang": lang, "code": m.group(0)})
    return blocks


def enrich_text_to_segments(text: str) -> List[Dict[str, Any]]:
    # Split into segments by double newline or paragraph boundaries
    raw_segments = [s.strip() for s in re.split(r"\n\n+", text) if s.strip()]
    segments: List[Dict[str, Any]] = []
    for idx, seg in enumerate(raw_segments):
        tags = simple_tag_extract(seg)
        entities = [t for t in tags if t.lower() not in {"api"}]
        keyphrases = tags[:5]
        code_blocks = simple_code_blocks(seg)
        segments.append(
            {
                "start": 0.0,
                "end": 0.0,
                "text": seg,
                "tags": tags,
                "entities": entities,
                "keyphrases": keyphrases,
                "code_blocks": code_blocks,
                "difficulty": None,
            }
        )
    return segments


def main() -> None:
    load_dotenv()
    use_llm = os.getenv("ENRICH_WITH_LLM") == "1" or "--llm" in os.sys.argv
    client: MongoClient = get_mongo_client()
    db = client[DB_NAME]
    cleaned = db[COLL_CLEANED]
    enriched = db[COLL_ENRICHED]

    for doc in cleaned.find({"cleaned_text": {"$exists": True, "$ne": None}}).limit(20):
        video_id = doc.get("video_id")
        text = (doc.get("cleaned_text") or "").strip()
        if not video_id or not text:
            continue
        if use_llm:
            try:
                from agents.enrich_agent import EnrichmentAgent

                agent = EnrichmentAgent()
                segments = agent.annotate(text) or []
            except Exception:
                segments = enrich_text_to_segments(text)
        else:
            segments = enrich_text_to_segments(text)
        payload: Dict[str, Any] = {
            "video_id": video_id,
            "segments": segments,
        }
        enriched.update_one({"video_id": video_id}, {"$set": payload}, upsert=True)
        print(
            f"Enriched {video_id} → {COLL_ENRICHED} (segments={len(segments)} llm={use_llm})"
        )


if __name__ == "__main__":
    main()
