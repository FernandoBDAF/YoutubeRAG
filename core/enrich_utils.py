import re
from typing import Any, Dict, List, Tuple

from core.text_utils import normalize_newlines, strip_stray_backslashes


def split_units(text: str) -> List[str]:
    t = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    if re.search(r"\n{2,}", t):
        return [p.strip() for p in re.split(r"\n{2,}", t) if p.strip()]
    if "\n" in t:
        return [p.strip() for p in t.split("\n") if p.strip()]
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", t) if s.strip()]
    return sents if sents else ([t] if t else [])


def pack_units(units: List[str], target_chars: int = 1800) -> List[str]:
    buffer: List[str] = []
    size = 0
    packed: List[str] = []
    for u in units:
        if size + len(u) + 2 <= target_chars:
            buffer.append(u)
            size += len(u) + 2
        else:
            if buffer:
                packed.append("\n\n".join(buffer))
            buffer = [u]
            size = len(u)
    if buffer:
        packed.append("\n\n".join(buffer))
    return packed


def normalize_llm_segments(raw_segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    segments: List[Dict[str, Any]] = []
    for s in raw_segments:
        seg_text = normalize_newlines(s.get("text", "") or "")
        seg_text = strip_stray_backslashes(seg_text)
        segments.append(
            {
                "start": float(s.get("start", 0.0) or 0.0),
                "end": float(s.get("end", 0.0) or 0.0),
                "text": seg_text,
                "tags": s.get("tags", []),
                "named_entities": s.get("named_entities", []),
                "topics": s.get("topics", []),
                "keyphrases": s.get("keyphrases", []),
                "code_blocks": s.get("code_blocks", []),
                "difficulty": s.get("difficulty"),
                "entities": s.get("entities", []),
            }
        )
    return segments
