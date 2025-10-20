import os
from typing import Any, List, Optional
from dataclasses import dataclass
import re

from dotenv import load_dotenv
from pymongo import MongoClient

try:
    from app.services.utils import get_mongo_client
    from core.base_stage import BaseStage
    from core.stage_config import BaseStageConfig
except ModuleNotFoundError:
    import sys as _sys, os as _os

    _sys.path.append(
        _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
    )
    from app.services.utils import get_mongo_client
    from core.base_stage import BaseStage
    from core.stage_config import BaseStageConfig
from config.paths import DB_NAME, COLL_RAW_VIDEOS, COLL_CLEANED
from core.text_utils import normalize_newlines
from core.concurrency import run_llm_concurrent
from typing import Optional


def _normalize_text(text: str) -> str:
    # Normalize line endings and collapse excessive whitespace
    t = (text or "").replace("\r\n", " ").replace("\r", " ").replace("\n", " ")
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
    if "." in t:
        parts = [p.strip() for p in t.split(".") if p.strip()]
        buf: List[str] = []
        acc = ""
        for p in parts:
            if len(acc) + len(p) + 1 <= 5000:
                acc = (acc + ". " + p) if acc else p
            else:
                if acc:
                    buf.append(acc)
                acc = p
        if acc:
            buf.append(acc)
        return buf
    # Sentence split
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", t) if s.strip()]
    if sentences:
        return sentences
    return [t] if t else []


def _llm_clean_text(
    agent_factory,
    video_id: str,
    raw_text: str,
    max_workers: int,
    retries: int = 1,
    backoff_s: float = 0.5,
    qps: Optional[float] = None,
) -> dict:
    # Remove common single-word interjections/fillers before splitting
    fillers_re = re.compile(
        r"\b(OK|Okay|Yeah|Yep|Nope|Morning|Right|So|Well|Um|Uh|Mm|Mm-hm|Mhm|Like)\b[,.!?]*\s+",
        re.IGNORECASE,
    )
    preprocessed = fillers_re.sub("", raw_text or "")
    chunks = _split_units(preprocessed)
    if not chunks:
        return {"video_id": video_id, "cleaned_text": "", "paragraphs": []}

    def _on_error(e, ch):
        return ch

    cleaned_parts = run_llm_concurrent(
        chunks,
        agent_factory,
        "clean",
        max_workers=max_workers,
        retries=int(retries),
        backoff_s=float(backoff_s),
        qps=qps,
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

    post_processed_chunks = []
    # Post-processing: strip stage cues and artifacts, standardize dashes/whitespace
    for chunck in cleaned_chunks:
        cleaned = normalize_newlines(chunck)
        cleaned = re.sub(
            r"\[(APPLAUSE|SQUEAKING|RUSTLING|MUSIC|LAUGHTER|NOISE|CLICKING)\]",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )
        cleaned = re.sub(r"-{2,}", " — ", cleaned)
        cleaned = re.sub(r"\s{2,}", " ", cleaned)
        post_processed_chunks.append(cleaned)

    # Enforce paragraphization: 6–10 sentences per paragraph (flexible)
    sentences = []
    for blk in post_processed_chunks:
        sentences.extend([s for s in re.split(r"(?<=[.!?])\s+", blk) if s.strip()])
    target_min, target_max = 6, 10
    paragraphs: List[str] = []
    buf: List[str] = []
    for s in sentences:
        buf.append(s.strip())
        if len(buf) >= target_max:
            paragraphs.append(" ".join(buf))
            buf = []
    if buf:
        # last paragraph: allow shorter if needed
        if paragraphs and len(buf) < target_min:
            paragraphs[-1] = paragraphs[-1] + " " + " ".join(buf)
        else:
            paragraphs.append(" ".join(buf))
    cleaned_text = "\n\n".join(paragraphs)
    return {"video_id": video_id, "cleaned_text": cleaned_text}


def build_embedding_text(chunk):
    summary = chunk.get("summary", "")
    entities = ", ".join([e["name"] for e in chunk.get("entities", [])[:3]])
    concepts = ", ".join([c["name"] for c in chunk.get("concepts", [])[:3]])
    base_text = chunk.get("chunk_text", "")

    # Concatenate weighted signals
    return f"Summary: {summary}\nKey Entities: {entities}\nKey Concepts: {concepts}\n\nMain Content:\n{base_text}"


@dataclass
class CleanConfig(BaseStageConfig):
    use_llm: bool = False
    # LLM tuning with explicit defaults
    llm_retries: int = 1
    llm_backoff_s: float = 0.5
    llm_qps: Optional[float] = None
    model_name: Optional[str] = None

    @classmethod
    def from_args_env(cls, args, env, default_db):
        base = BaseStageConfig.from_args_env(args, env, default_db)
        use_llm = bool(
            getattr(args, "llm", False) or (env.get("CLEAN_WITH_LLM") == "1")
        )
        return cls(
            **vars(base),
            use_llm=use_llm,
            llm_retries=int(env.get("LLM_RETRIES", "1") or "1"),
            llm_backoff_s=float(env.get("LLM_BACKOFF_S", "0.5") or "0.5"),
            llm_qps=None,
            model_name=env.get("OPENAI_DEFAULT_MODEL"),
        )


class CleanStage(BaseStage):
    name = "clean"
    description = "Clean transcripts into standardized text and paragraphs"
    ConfigCls = CleanConfig

    def build_parser(self, p):
        super().build_parser(p)

    def iter_docs(self):
        # Read from the default DB by default; allow explicit override via read_db_name/read_coll
        src_db = self.config.read_db_name or self.config.db_name
        src_coll_name = self.config.read_coll or COLL_RAW_VIDEOS
        coll = self.get_collection(src_coll_name, io="read", db_name=src_db)
        if self.config.video_id:
            return list(
                coll.find(
                    {"video_id": self.config.video_id},
                    {"video_id": 1, "transcript_raw": 1},
                )
            )
        return list(coll.find({}, {"video_id": 1, "transcript_raw": 1}))

    def handle_doc(self, doc):
        video_id = doc.get("video_id")
        text = (doc.get("transcript_raw") or "").strip()
        if not video_id or not text:
            return
        # Write to configured write collection (default cleaned_transcripts) on write DB
        # Write to default DB unless write_db_name provided
        dst_db = self.config.write_db_name or self.config.db_name
        dst_coll_name = self.config.write_coll or COLL_CLEANED
        cleaned = self.get_collection(dst_coll_name, io="write", db_name=dst_db)
        if not self.config.upsert_existing:
            existing = cleaned.find_one({"video_id": video_id}, {"cleaned_text": 1})
            if existing and (existing.get("cleaned_text") or "").strip():
                self.stats["skipped"] += 1
                self.log(f"Skip existing cleaned {video_id}")
                print(f"Skip existing cleaned {video_id}")
                return

        payload = {}
        from agents.clean_agent import TranscriptCleanAgent

        agent_factory = lambda: TranscriptCleanAgent(self.config.model_name)
        payload = _llm_clean_text(
            agent_factory,
            video_id,
            text,
            max_workers=int(self.config.concurrency or 10),
            retries=int(self.config.llm_retries or 1),
            backoff_s=float(self.config.llm_backoff_s or 0.5),
            qps=self.config.llm_qps,
        )

        if (
            payload.get("cleaned_text")
            and not (payload.get("cleaned_text") or "").strip()
        ):
            self.log(f"No cleaned text for {video_id}")
            print(f"No cleaned text for {video_id}")
            return
        if not self.config.dry_run:
            cleaned.update_one({"video_id": video_id}, {"$set": payload}, upsert=True)
        self.stats["updated"] += 1
        self.log(f"Cleaned {video_id} → {dst_coll_name} (llm={self.config.use_llm})")
        print(f"Cleaned {video_id} → {dst_coll_name} (llm={self.config.use_llm})")


if __name__ == "__main__":
    stage = CleanStage()
    raise SystemExit(stage.run())
