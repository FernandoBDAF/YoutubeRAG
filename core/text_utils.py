import re
import hashlib
from typing import List


def normalize_newlines(text: str) -> str:
    if text is None:
        return ""
    t = text.replace("\r\n", "\n").replace("\r", "\n")
    t = t.replace("\\n", "\n")
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def strip_stray_backslashes(text: str) -> str:
    if text is None:
        return ""
    # Remove backslashes that are not escaping common sequences
    # Keep \\n+    text = re.sub(r"(?<!\\)\\(?![\\nrt\"'])", "", text)
    return text


def count_words(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text or ""))


def sha256_text(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest() if text else ""


def dedup_lower(seq: List[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for s in seq or []:
        k = (s or "").strip().lower()
        if not k or k in seen:
            continue
        seen.add(k)
        out.append(k)
    return out
