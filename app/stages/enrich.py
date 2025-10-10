import os
import re
import hashlib
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Tuple
from core.concurrency import run_llm_concurrent
from core.text_utils import (
    normalize_newlines,
    strip_stray_backslashes,
    count_words,
    sha256_text,
    dedup_lower,
)

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
from config.paths import DB_NAME, COLL_CLEANED, COLL_ENRICHED, COLL_RAW_VIDEOS


CODE_FENCE_RE = re.compile(r"```([a-zA-Z0-9_+-]*)[\s\S]*?```", re.MULTILINE)


def simple_tag_extract(text: str) -> List[str]:
    """Heuristic tags from a wider CS vocabulary with a bag-of-words fallback."""
    text_l = text.lower()
    vocab = [
        # General CS / algorithms
        "algorithm",
        "algorithms",
        "data structure",
        "data structures",
        "complexity",
        "big o",
        "runtime",
        "proof",
        "correctness",
        "efficiency",
        "induction",
        "recursion",
        "divide and conquer",
        "greedy",
        "dynamic programming",
        "graph",
        "graphs",
        "tree",
        "binary tree",
        "heap",
        "priority queue",
        "hash",
        "hashing",
        "set",
        "sorting",
        "search",
        "array",
        "list",
        "stack",
        "queue",
        # Dev (retain)
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
    ]
    candidates = set()
    for kw in vocab:
        if re.search(rf"\b{re.escape(kw)}\b", text_l):
            candidates.add(kw)
    if not candidates:
        # Fallback: pick top tokens (length>=6) excluding common stopwords
        stop = {
            "because",
            "about",
            "would",
            "there",
            "their",
            "which",
            "these",
            "those",
            "could",
            "should",
            "might",
            "where",
            "being",
            "between",
            "among",
            "through",
            "after",
            "before",
            "class",
            "video",
            "something",
            "someone",
            "itself",
            "within",
            "without",
            "using",
        }
        words = re.findall(r"[a-zA-Z]{6,}", text_l)
        freq: Dict[str, int] = {}
        for w in words:
            if w in stop:
                continue
            freq[w] = freq.get(w, 0) + 1
        top = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:6]
        candidates.update([w for w, _ in top])
    return sorted(candidates)


def simple_code_blocks(text: str) -> List[Dict[str, str]]:
    blocks: List[Dict[str, str]] = []
    for m in CODE_FENCE_RE.finditer(text):
        lang = m.group(1) or ""
        blocks.append({"lang": lang, "code": m.group(0)})
    return blocks


from core.enrich_utils import split_units as _split_units, pack_units as _pack_units, normalize_llm_segments


def enrich_text_to_segments(
    text: str, target_chars: int = 1800
) -> List[Dict[str, Any]]:
    # Coalesce small units into ~target_chars segments
    units = _split_units(text)
    packed = _pack_units(units, target_chars=target_chars)

    segments: List[Dict[str, Any]] = []
    for seg in packed:
        tags = simple_tag_extract(seg)
        named_entities: List[str] = []
        topics: List[str] = []
        keyphrases = tags[:6]
        code_blocks = simple_code_blocks(seg)
        segments.append(
            {
                "start": 0.0,
                "end": 0.0,
                "text": seg,
                "tags": tags,
                "named_entities": named_entities,
                "topics": topics,
                "keyphrases": keyphrases,
                "code_blocks": code_blocks,
                "difficulty": None,
                "entities": (named_entities + topics),
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
    raw_videos = db[COLL_RAW_VIDEOS]

    def _env_bool(name: str, default: bool = False) -> bool:
        v = os.getenv(name)
        if v is None:
            return default
        return str(v).strip().lower() in {"1", "true", "yes", "on"}

    allow_upsert_existing = _env_bool("ENRICH_UPSERT_EXISTING", False)
    max_items_env = os.getenv("ENRICH_MAX")
    max_items = int(max_items_env) if (max_items_env or "").strip().isdigit() else 0
    verbose = _env_bool("ENRICH_VERBOSE", False)

    total_cleaned = cleaned.count_documents(
        {"cleaned_text": {"$exists": True, "$ne": None}}
    )
    total_existing = enriched.count_documents({})
    print(
        f"Enrich start: cleaned={total_cleaned} enriched={total_existing} allow_upsert_existing={allow_upsert_existing} max={max_items or 'all'} llm={use_llm}"
    )

    cursor = cleaned.find({"cleaned_text": {"$exists": True, "$ne": None}})
    if max_items and max_items > 0:
        cursor = cursor.limit(max_items)

    processed = 0
    skipped = 0
    failed = 0
    for doc in cursor:
        video_id = doc.get("video_id")
        text = (doc.get("cleaned_text") or "").strip()
        if not video_id or not text:
            continue
        if not allow_upsert_existing and enriched.find_one({"video_id": video_id}):
            if verbose:
                print(f"Skip existing enriched {video_id}")
            skipped += 1
            continue
        source = "heuristic"
        # Normalize cleaned text newlines
        text = normalize_newlines(text)
        # Fetch duration seconds if available
        rv = raw_videos.find_one({"video_id": video_id}) or {}
        duration_seconds = rv.get("duration_seconds") or rv.get("duration") or 0
        try:
            if use_llm:
                try:
                    from agents.enrich_agent import EnrichmentAgent

                    agent = EnrichmentAgent()
                    # Pre-split text into ~target_chars units and annotate concurrently (sequential map for now)
                    units = _split_units(text)
                    # Coalesce small units first to reduce API calls
                    packed_texts: List[str] = []
                    buf: List[str] = []
                    size = 0
                    for u in units:
                        if size + len(u) + 2 <= 1800:
                            buf.append(u)
                            size += len(u) + 2
                        else:
                            if buf:
                                packed_texts.append("\n\n".join(buf))
                            buf = [u]
                            size = len(u)
                    if buf:
                        packed_texts.append("\n\n".join(buf))

                    # Concurrent annotate preserving order via core helper
                    concurrency = int(os.getenv("ENRICH_CONCURRENCY", "8") or "8")

                    def _agent_factory():
                        return EnrichmentAgent()

                    def _on_error(e, chunk):
                        return {
                            "start": 0.0,
                            "end": 0.0,
                            "text": chunk,
                            "tags": simple_tag_extract(chunk),
                            "named_entities": [],
                            "topics": [],
                            "keyphrases": [],
                            "code_blocks": simple_code_blocks(chunk),
                            "difficulty": None,
                            "entities": [],
                        }

                    raw_segments = run_llm_concurrent(
                        packed_texts,
                        _agent_factory,
                        "annotate_single",
                        max_workers=concurrency,
                        retries=int(os.getenv("LLM_RETRIES", "1") or "1"),
                        backoff_s=float(os.getenv("LLM_BACKOFF_S", "0.5") or "0.5"),
                        qps=None,
                        jitter=True,
                        on_error=_on_error,
                        preserve_order=True,
                    )
                # Normalize text fields on results
                segments = normalize_llm_segments(raw_segments)
                    source = "llm"
                except Exception as _e:
                    segments = enrich_text_to_segments(text)
                    source = "heuristic_fallback"
            else:
                segments = enrich_text_to_segments(text)
                source = "heuristic"
        except Exception as e:
            failed += 1
            print(f"Enrich error video_id={video_id}: {e}")
            continue
        # Post-process: index, char_count, hash, quality flags, time estimate
        total_words = max(1, count_words(text))
        cum_words = 0
        enriched_segments: List[Dict[str, Any]] = []
        for i, s in enumerate(segments):
            seg_text = (s.get("text", "") or "").strip()
            char_count = len(seg_text)
            word_count = count_words(seg_text)
            start_ratio = (cum_words / total_words) if total_words else 0.0
            cum_words += word_count
            end_ratio = (cum_words / total_words) if total_words else 0.0
            est_start = (
                float(duration_seconds) * float(start_ratio)
                if duration_seconds
                else 0.0
            )
            est_end = (
                float(duration_seconds) * float(end_ratio) if duration_seconds else 0.0
            )
            segment_hash = sha256_text(seg_text)
            quality_flags: List[str] = []
            if not s.get("tags"):
                quality_flags.append("missing_tags")
            if char_count < 400:
                quality_flags.append("too_short")
            unique_tokens = len(set(re.findall(r"\b\w+\b", seg_text.lower())))
            ratio = (unique_tokens / max(1, word_count)) if word_count else 0.0
            if ratio < 0.25 and char_count >= 200:
                quality_flags.append("low_entropy")
            # Normalize and dedup fields
            tags = dedup_lower(s.get("tags", []))
            keyphrases = dedup_lower(s.get("keyphrases", []))
            named_entities = []
            for ne in s.get("named_entities", []) or []:
                ne = (ne or "").strip()
                if ne:
                    named_entities.append(ne.title())
            _seen = set()
            named_entities = [
                x for x in named_entities if not (x in _seen or _seen.add(x))
            ]
            topics = dedup_lower(s.get("topics", []))
            entities = s.get("entities", []) or (named_entities + topics)

            if os.getenv("ENRICH_ENFORCE_COUNTS", "false").lower() in {
                "1",
                "true",
                "yes",
                "on",
            }:
                if len(tags) > 12:
                    tags = tags[:12]
                if len(keyphrases) > 8:
                    keyphrases = keyphrases[:8]
            enriched_segments.append(
                {
                    "segment_index": i,
                    "start": est_start,
                    "end": est_end,
                    "text": seg_text,
                    "char_count": char_count,
                    "segment_hash": segment_hash,
                    "tags": tags,
                    "named_entities": named_entities,
                    "topics": topics,
                    "entities": entities,
                    "keyphrases": keyphrases,
                    "code_blocks": s.get("code_blocks", []),
                    "difficulty": s.get("difficulty"),
                    "quality_flags": quality_flags or None,
                }
            )
        # Debug metrics
        try:
            num = len(enriched_segments)
            lens = [len(s.get("text", "")) for s in enriched_segments] or [0]
            avg_len = sum(lens) / max(1, num)
            with_tags = sum(1 for s in enriched_segments if s.get("tags"))
            with_keys = sum(1 for s in enriched_segments if s.get("keyphrases"))
            timed = sum(
                1 for s in enriched_segments if (s.get("start", 0) or s.get("end", 0))
            )
            print(
                f"Enrich debug video_id={video_id} source={source} segs={num} avg_chars={avg_len:.0f} "
                f"tags_any={with_tags}/{num} keyphrases_any={with_keys}/{num} timed={timed}/{num}"
            )
        except Exception:
            pass

        # If LLM path yielded poor metadata (e.g., empty tags across many short segments),
        # fall back to heuristic coalescing/annotation for better downstream behavior.
        if source == "llm":
            try:
                if num >= 50 and with_tags == 0 and avg_len < 600:
                    segments = enrich_text_to_segments(text)
                    source = "llm_fallback_coalesce"
                    num = len(segments)
                    lens = [len(s.get("text", "")) for s in segments] or [0]
                    avg_len = sum(lens) / max(1, num)
                    with_tags = sum(1 for s in segments if s.get("tags"))
                    with_keys = sum(1 for s in segments if s.get("keyphrases"))
                    print(
                        f"Enrich adjust video_id={video_id} source={source} segs={num} avg_chars={avg_len:.0f} "
                        f"tags_any={with_tags}/{num} keyphrases_any={with_keys}/{num}"
                    )
            except Exception:
                pass
        payload: Dict[str, Any] = {
            "video_id": video_id,
            "segments": enriched_segments,
        }
        enriched.update_one({"video_id": video_id}, {"$set": payload}, upsert=True)
        processed += 1
        print(
            f"Enriched {video_id} → {COLL_ENRICHED} (segments={len(enriched_segments)} llm={use_llm} source={source})"
        )

    print(
        f"Enrich done: processed={processed} skipped_existing={skipped} failed={failed} total_candidates={(max_items or total_cleaned)}"
    )


if __name__ == "__main__":
    main()
