import os
from typing import Any, List
import re

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
from config.paths import DB_NAME, COLL_RAW_VIDEOS, COLL_CLEANED
from core.text_utils import normalize_newlines
from core.concurrency import run_llm_concurrent
from core.text_utils import normalize_newlines


def _normalize_text(text: str) -> str:
    # Normalize line endings and collapse excessive whitespace
    t = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    return t


def _split_units(text: str) -> List[str]:
    """Split text into logical units without assuming double newlines.

    Priority:
      1) blank-line separated paragraphs (\n\n)
      2) single newlines
      3) sentence boundaries
      4) whole text
    """
    t = _normalize_text(text)
    if re.search(r"\n{2,}", t):
        return [p.strip() for p in re.split(r"\n{2,}", t) if p.strip()]
    if "\n" in t:
        parts = [p.strip() for p in t.split("\n") if p.strip()]
        # If too fragmented, join lines into larger units of ~400 chars
        if len(parts) > 200:
            buf: List[str] = []
            acc = ""
            for p in parts:
                if len(acc) + len(p) + 1 <= 400:
                    acc = (acc + "\n" + p) if acc else p
                else:
                    if acc:
                        buf.append(acc)
                    acc = p
            if acc:
                buf.append(acc)
            return buf
        return parts
    # Sentence split
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", t) if s.strip()]
    if sentences:
        return sentences
    return [t] if t else []


def _split_for_cleaning(
    text: str, target_chars: int = 6000, overlap: int = 300
) -> List[str]:
    """Chunk into ~target_chars with small overlaps; robust to any formatting."""
    units = _split_units(text)
    if not units:
        return []
    chunks: List[str] = []
    buf: List[str] = []
    size = 0
    for part in units:
        p = part.strip()
        if len(p) > target_chars:
            # Flush current buffer
            if buf:
                chunks.append("\n\n".join(buf))
                buf, size = [], 0
            # Slice this very long unit into windows
            start = 0
            while start < len(p):
                end = min(len(p), start + target_chars)
                slice_txt = p[start:end]
                chunks.append(slice_txt)
                if end >= len(p):
                    break
                start = max(start + target_chars - overlap, start + 1)
            continue
        if size + len(p) + 2 <= target_chars:
            buf.append(p)
            size += len(p) + 2
        else:
            if buf:
                chunks.append("\n\n".join(buf))
            # start new buffer; include a small overlap from the last chunk
            if overlap > 0 and chunks:
                tail = chunks[-1][-overlap:]
                buf = [tail, p]
                size = len(tail) + len(p) + 2
            else:
                buf = [p]
                size = len(p)
    if buf:
        chunks.append("\n\n".join(buf))
    return chunks


def _llm_clean_text(
    agent_factory, video_id: str, raw_text: str, max_workers: int
) -> dict:
    chunks = _split_for_cleaning(raw_text)
    if not chunks:
        return {"video_id": video_id, "cleaned_text": "", "paragraphs": []}

    def _on_error(e, ch):
        return ch

    cleaned_parts = run_llm_concurrent(
        chunks,
        agent_factory,
        "clean",
        max_workers=max_workers,
        retries=int(os.getenv("LLM_RETRIES", "1") or "1"),
        backoff_s=float(os.getenv("LLM_BACKOFF_S", "0.5") or "0.5"),
        qps=None,
        jitter=True,
        on_error=_on_error,
        preserve_order=True,
    )
    cleaned_chunks: List[str] = []
    for i, out in enumerate(cleaned_parts, start=1):
        out = out or ""
        if not out.strip():
            out = chunks[i - 1]
        cleaned_chunks.append(normalize_newlines(out))
        print(f"Clean chunk {i}/{len(chunks)} for {video_id} (len={len(chunks[i-1])})")

    cleaned_text = "\n\n".join(cleaned_chunks)
    # Post-processing: strip stage cues and artifacts, standardize dashes/whitespace
    cleaned_text = normalize_newlines(cleaned_text)
    cleaned_text = re.sub(
        r"\[(APPLAUSE|SQUEAKING|RUSTLING|MUSIC|LAUGHTER|NOISE|CLICKING)\]",
        "",
        cleaned_text,
        flags=re.IGNORECASE,
    )
    cleaned_text = re.sub(r"-{2,}", " — ", cleaned_text)
    cleaned_text = re.sub(r"\s{2,}", " ", cleaned_text)
    # Build paragraphs using the same robust splitter
    para_units = _split_units(cleaned_text)
    paragraphs = [{"start": 0.0, "end": 0.0, "text": p} for p in para_units if p]
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

    def _env_bool(name: str, default: bool = False) -> bool:
        v = os.getenv(name)
        if v is None:
            return default
        return str(v).strip().lower() in {"1", "true", "yes", "on"}

    allow_upsert_existing = _env_bool("CLEAN_UPSERT_EXISTING", False)

    processed = 0
    # Process all raws; fallback to description if transcript is missing
    for doc in raw.find({}).limit(50):
        video_id = doc.get("video_id")
        text = (doc.get("transcript_raw") or doc.get("description") or "").strip()
        if not video_id or not text:
            continue
        if not doc.get("transcript_raw") and doc.get("description"):
            print(f"Clean fallback to description for {video_id}")
        # Skip existing cleaned unless env allows upsert
        if not allow_upsert_existing:
            if cleaned.find_one({"video_id": video_id}):
                print(f"Skip existing cleaned {video_id}")
                continue
        if use_llm:
            from agents.clean_agent import TranscriptCleanAgent

            concurrency = int(os.getenv("CLEAN_CONCURRENCY", "4") or "4")
            payload = _llm_clean_text(TranscriptCleanAgent, video_id, text, concurrency)
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
        # Final safety: if LLM produced empty (rare), fall back to original text
        if use_llm and not (payload.get("cleaned_text") or "").strip():
            payload["cleaned_text"] = text
            payload["paragraphs"] = [{"start": 0.0, "end": 0.0, "text": text}]
        cleaned.update_one({"video_id": video_id}, {"$set": payload}, upsert=True)
        processed += 1
        print(f"Cleaned {video_id} → {COLL_CLEANED} (llm={use_llm})")
    if processed == 0:
        print("No documents cleaned (no transcript/description found).")


if __name__ == "__main__":
    main()
