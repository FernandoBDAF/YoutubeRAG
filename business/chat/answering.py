"""
Chat Answer Generation.

This module handles answer generation for chat using different agents and modes.
Part of the BUSINESS layer - chat feature logic.
"""

from typing import Any, Dict, List

from business.agents.rag.reference_answer import ReferenceAnswerAgent
from business.agents.rag.topic_reference import TopicReferenceAgent
from business.services.rag.generation import answer_with_openai


def _merge_hits_by_doc(
    hits: List[Dict[str, Any]], max_docs: int = 5
) -> List[Dict[str, Any]]:
    """Merge search hits by document/video ID.

    Groups hits by video_id and selects representative chunks (first, middle, last).

    Args:
        hits: List of search hit documents
        max_docs: Maximum number of documents to include (default: 5)

    Returns:
        List of {"video_id": str, "chunks": List[Dict]} bundles
    """
    by_vid: Dict[str, List[Dict[str, Any]]] = {}
    for h in hits:
        vid = str(h.get("video_id"))
        by_vid.setdefault(vid, []).append(h)

    ranked_docs = sorted(
        by_vid.items(),
        key=lambda kv: max(
            float(
                x.get("final_score") or x.get("score") or x.get("search_score") or 0.0
            )
            for x in kv[1]
        ),
        reverse=True,
    )

    bundles: List[Dict[str, Any]] = []
    for vid, chunks in ranked_docs[:max_docs]:
        sel = [chunks[0]]
        if len(chunks) > 2:
            sel.append(chunks[len(chunks) // 2])
        if len(chunks) > 1:
            sel.append(chunks[-1])
        bundles.append({"video_id": vid, "chunks": sel})

    return bundles


def _anchor_from_chunk(c: Dict[str, Any]) -> Dict[str, Any]:
    """Create anchor metadata (title, URL, timestamp) from chunk.

    Args:
        c: Chunk document

    Returns:
        Dict with 'title', 'url', 'hint' for display
    """
    meta = c.get("metadata", {}) or {}
    start_sec = meta.get("start_sec")
    vid = c.get("video_id")

    # Fallback: parse timestamp_start like 'hh:mm:ss' if available
    if start_sec is None:
        ts = c.get("timestamp_start") or (
            meta.get("timestamp_start") if isinstance(meta, dict) else None
        )
        if isinstance(ts, str) and ts.count(":") >= 1:
            try:
                parts = [int(p) for p in ts.split(":")]
                if len(parts) == 3:
                    start_sec = parts[0] * 3600 + parts[1] * 60 + parts[2]
                elif len(parts) == 2:
                    start_sec = parts[0] * 60 + parts[1]
            except Exception:
                start_sec = None

    ts_param = f"&t={int(start_sec)}" if isinstance(start_sec, (int, float)) else ""
    url = f"https://www.youtube.com/watch?v={vid}{ts_param}" if vid else ""
    title = meta.get("title") or meta.get("channel_id") or str(vid)

    if isinstance(start_sec, (int, float)):
        mm = int(start_sec) // 60
        ss = int(start_sec) % 60
        hint = f"start {mm:02d}:{ss:02d} — entry point"
    else:
        hint = "start near this chunk in the transcript"

    return {"title": title, "url": url, "hint": hint}


def build_reference_bundles(hits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Build reference bundles for reference-mode answering.

    Groups hits by document and creates structured bundles with anchors.

    Args:
        hits: List of search hit documents

    Returns:
        List of reference bundles with video metadata and excerpts
    """
    bundles: List[Dict[str, Any]] = []

    for d in _merge_hits_by_doc(hits, max_docs=5):
        chunks = d.get("chunks", [])
        if not chunks:
            continue

        anchors = [_anchor_from_chunk(c) for c in chunks[:1]]
        anchor = (
            anchors[0]
            if anchors
            else {"title": d.get("video_id"), "url": "", "hint": ""}
        )

        bullets: List[str] = []
        quotes: List[str] = []
        for c in chunks[:3]:
            text = c.get("embedding_text") or c.get("text") or ""
            if text:
                bullets.append(text[:220])
                quotes.append(text[:180])

        bundles.append(
            {
                "video_id": d.get("video_id"),
                "title": anchor.get("title"),
                "url": anchor.get("url"),
                "anchor_hint": anchor.get("hint"),
                "bullets": bullets,
                "quotes": quotes,
            }
        )

    return bundles


def answer_with_context(
    contexts: List[Dict[str, Any]],
    rewritten_query: str,
    short_term_msgs: List[Dict[str, str]],
) -> str:
    """Generate answer using context and conversation memory.

    Args:
        contexts: Retrieved context documents
        rewritten_query: Rewritten query
        short_term_msgs: Recent conversation messages

    Returns:
        Generated answer string
    """
    # Optionally prepend a tiny conversational hint into the question
    history_hint = "\n\nRecent context:\n" + "\n".join(
        f"{m['role']}: {m['content'][:140]}" for m in short_term_msgs[-4:]
    )
    question = rewritten_query + history_hint
    return answer_with_openai(contexts, question)
