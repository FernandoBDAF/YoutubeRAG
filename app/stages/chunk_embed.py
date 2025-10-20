import os
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

import requests
import time
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
from app.services.rate_limit import RateLimiter
from config.paths import (
    DB_NAME,
    COLL_ENRICHED,
    COLL_CHUNKS,
    VECTOR_DIM,
)
from core.text_utils import normalize_newlines, sha256_text
import re


def embed_texts(texts: List[str]) -> List[List[float]]:
    api_key = os.getenv("VOYAGE_API_KEY")
    if not api_key:
        raise RuntimeError("VOYAGE_API_KEY is not set")
    model = os.getenv("VOYAGE_EMBED_MODEL", "voyage-2")
    # Rate limiter shared per process
    limiter = RateLimiter()
    # Try official client first (handles retries/rate limits)
    try:
        import voyageai  # type: ignore

        client = voyageai.Client(
            api_key=api_key,
            max_retries=int(os.getenv("VOYAGE_MAX_RETRIES", "4")),
            timeout=int(os.getenv("VOYAGE_TIMEOUT", "60")),
        )
        limiter.wait()
        res = client.embed(texts, model=model, input_type="document")
        return list(res.embeddings)
    except Exception:
        pass

    # Fallback to HTTP with exponential backoff
    max_retries = int(os.getenv("VOYAGE_MAX_RETRIES", "4"))
    backoff_base = float(os.getenv("VOYAGE_BACKOFF_BASE", "1.5"))

    for attempt in range(max_retries + 1):
        try:
            limiter.wait()
            r = requests.post(
                "https://api.voyageai.com/v1/embeddings",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={"model": model, "input": texts},
                timeout=60,
            )
            if r.status_code in (429, 500, 502, 503, 504):
                retry_after = r.headers.get("Retry-After")
                if retry_after:
                    try:
                        sleep_s = float(retry_after)
                    except Exception:
                        sleep_s = backoff_base**attempt
                else:
                    sleep_s = backoff_base**attempt
                if attempt < max_retries:
                    limiter.delay(max(0.5, min(30.0, sleep_s)))
                    time.sleep(max(0.5, min(30.0, sleep_s)))
                    continue
            try:
                r.raise_for_status()
            except requests.HTTPError as e:
                # If final attempt failed, return empty embeddings gracefully
                if attempt >= max_retries:
                    print(
                        "Voyage embeddings: final attempt failed (",
                        r.status_code,
                        ") - returning empty batch",
                    )
                    return []
                raise
            payload = r.json()
            if "data" in payload:
                return [v.get("embedding", []) for v in payload.get("data", [])]
            if "embeddings" in payload:
                return payload.get("embeddings", [])
            return []
        except requests.HTTPError as e:
            if (
                getattr(e.response, "status_code", 0) in (429, 500, 502, 503, 504)
                and attempt < max_retries
            ):
                time.sleep(max(0.5, min(30.0, backoff_base**attempt)))
                continue
            # On last attempt or non-retryable error, return empty to avoid stage crash
            try:
                code = getattr(e.response, "status_code", None)
                print(f"Voyage embeddings HTTP error {code}; skipping batch")
            except Exception:
                pass
            return []
        except Exception:
            if attempt < max_retries:
                time.sleep(max(0.5, min(15.0, backoff_base**attempt)))
                continue
            # Give up gracefully
            return []
    print("Voyage embeddings: exhausted retries; skipping batch")
    return []


@dataclass
class ChunkConfig(BaseStageConfig):
    chunk_strategy: str = "fixed"  # fixed | recursive | semantic
    token_size: int = 500
    overlap_pct: float = 0.15
    split_chars: List[str] = field(default_factory=lambda: ["."])
    semantic_model: Optional[str] = None

    @classmethod
    def from_args_env(cls, args, env, default_db):
        base = BaseStageConfig.from_args_env(args, env, default_db)
        strategy = (
            (
                getattr(args, "chunk_strategy", None)
                or env.get("CHUNK_STRATEGY", "fixed")
            )
            .strip()
            .lower()
        )
        token_size = int(getattr(args, "token_size", env.get("TOKEN_SIZE", 500)))
        overlap_pct = float(getattr(args, "overlap_pct", env.get("OVERLAP_PCT", 0.15)))
        split_chars_arg = getattr(args, "split_chars", None) or env.get(
            "SPLIT_CHARS", "."
        )
        split_chars = [s.strip() for s in str(split_chars_arg).split(",") if s.strip()]
        semantic_model = getattr(args, "semantic_model", None) or env.get(
            "SEMANTIC_MODEL"
        )
        return cls(
            **vars(base),
            chunk_strategy=strategy,
            token_size=token_size,
            overlap_pct=overlap_pct,
            split_chars=split_chars,
            semantic_model=semantic_model,
        )


class ChunkStage(BaseStage):
    name = "chunk"
    description = "Chunk enriched segments and generate embeddings"
    ConfigCls = ChunkConfig

    def build_parser(self, p):
        super().build_parser(p)
        p.add_argument(
            "--chunk_strategy",
            choices=["fixed", "recursive", "semantic"],
            default="fixed",
        )
        p.add_argument("--token_size", type=int, default=500)
        p.add_argument("--overlap_pct", type=float, default=0.15)
        p.add_argument("--split_chars", type=str, default=".")
        p.add_argument("--semantic_model", type=str)
        try:
            p.add_argument("--video_id", type=str)
        except Exception:
            pass
        try:
            p.add_argument("--upsert_existing", action="store_true")
        except Exception:
            pass

    def iter_docs(self):
        if self.config.video_id:
            docs = list(
                self.db[COLL_ENRICHED].find(
                    {"video_id": self.config.video_id}, {"video_id": 1, "segments": 1}
                )
            )
            print(
                f"[chunk] Selected {len(docs)} doc(s) for video_id={self.config.video_id}"
            )
            return docs
        enriched = self.db[COLL_ENRICHED]
        docs = list(enriched.find({"segments": {"$exists": True, "$ne": []}}))
        print(
            f"[chunk] Selected {len(docs)} enriched doc(s) for processing (strategy={self.config.chunk_strategy})"
        )
        return docs

    def handle_doc(self, doc):
        db = self.db
        chunks_coll = db[COLL_CHUNKS]
        video_id = doc.get("video_id")
        segments = doc.get("segments", [])
        if not video_id or not segments:
            return
        print(
            f"[chunk] Processing video_id={video_id} with strategy={self.config.chunk_strategy} token_size={self.config.token_size} overlap_pct={self.config.overlap_pct}"
        )
        try:
            rv = db["raw_videos"].find_one(
                {"video_id": video_id}, {"channel_id": 1, "published_at": 1}
            )
        except Exception:
            rv = None
        # Build full text then apply selected chunking strategy
        full_text = "\n".join([s.get("text") for s in segments])
        print(f"[chunk] Full text length={len(full_text)} chars")
        chunks_plain = []
        try:
            if self.config.chunk_strategy == "fixed":
                from langchain.text_splitter import TokenTextSplitter

                splitter = TokenTextSplitter(
                    chunk_size=int(self.config.token_size),
                    chunk_overlap=int(
                        self.config.token_size * float(self.config.overlap_pct)
                    ),
                )
                chunks_plain = splitter.split_text(full_text)
            elif self.config.chunk_strategy == "recursive":
                from langchain.text_splitter import RecursiveCharacterTextSplitter

                splitter = RecursiveCharacterTextSplitter(
                    separators=self.config.split_chars or ["."],
                    chunk_size=int(self.config.token_size),
                    chunk_overlap=int(
                        self.config.token_size * float(self.config.overlap_pct)
                    ),
                )
                chunks_plain = splitter.split_text(full_text)
            elif self.config.chunk_strategy == "semantic":
                from langchain_experimental.text_splitter import SemanticChunker
                from langchain_openai import OpenAIEmbeddings

                # Prefer voyage embeddings via our embed_texts wrapper is not directly supported by LC; use OpenAI if SEMANTIC_MODEL points there
                model_name = self.config.semantic_model or os.getenv(
                    "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
                )
                emb = OpenAIEmbeddings(model=model_name)
                splitter = SemanticChunker(embeddings=emb)
                chunks_plain = splitter.split_text(full_text)
        except Exception as e:
            # Fallback: no chunking
            chunks_plain = [full_text]
            print(f"[chunk] Chunking failed ({e}); using single chunk fallback")
        print(f"[chunk] Produced {len(chunks_plain)} chunk(s) before normalization")
        texts = [
            normalize_newlines(c if isinstance(c, str) else (c.get("text") or ""))
            for c in chunks_plain
        ]
        cue_re = re.compile(
            r"\[(APPLAUSE|SQUEAKING|RUSTLING|MUSIC|LAUGHTER|NOISE|CLICKING)\]",
            re.IGNORECASE,
        )
        display_texts = [cue_re.sub("", t) for t in texts]
        texts = display_texts
        # Embeddings: Voyage only (simplified per plan)
        print(f"[chunk] Embedding {len(texts)} chunk text(s) with Voyage")
        vectors = embed_texts(texts) if texts else []
        print(f"[chunk] Received {len(vectors)} embedding vector(s)")
        age_days = 180
        channel_id = None
        try:
            from datetime import datetime, timezone

            if rv and rv.get("published_at"):
                published = rv.get("published_at")
                if isinstance(published, str):
                    try:
                        published_dt = datetime.fromisoformat(
                            published.replace("Z", "+00:00")
                        )
                    except Exception:
                        published_dt = None
                else:
                    published_dt = published
                if published_dt:
                    now = datetime.now(timezone.utc)
                    age_days = max(0, int((now - published_dt).days))
            if rv and rv.get("channel_id"):
                channel_id = rv.get("channel_id")
        except Exception:
            pass
        code_present_any = any(bool(s.get("code_blocks")) for s in segments)
        # Capture chunking parameters used for this run
        chunking_info: Dict[str, Any] = {
            "strategy": self.config.chunk_strategy,
            "token_size": int(self.config.token_size),
            "overlap_pct": float(self.config.overlap_pct),
        }
        if self.config.chunk_strategy in ("recursive", "semantic"):
            chunking_info["split_chars"] = self.config.split_chars or ["."]
        if self.config.chunk_strategy == "semantic":
            chunking_info["semantic_model"] = self.config.semantic_model or os.getenv(
                "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
            )
        raw_tags: List[str] = [t for s in segments for t in s.get("tags", [])]
        _seen: set[str] = set()
        _norm_tags: List[str] = []
        for t in raw_tags:
            k = (t or "").strip().lower().replace("_", "-")
            if not k or k in _seen:
                continue
            _seen.add(k)
            _norm_tags.append(k)
        tags_union: List[str] = sorted(_norm_tags)
        out_docs: List[Dict[str, Any]] = []
        for i, (text, vec, disp) in enumerate(
            zip(texts, vectors, display_texts), start=1
        ):
            chunk_hash = sha256_text(text)
            out_docs.append(
                {
                    "video_id": video_id,
                    "chunk_id": f"{video_id}:{i:04d}",
                    "text": text,
                    "display_text": disp,
                    "chunk_hash": chunk_hash,
                    "metadata": {
                        "tags": tags_union,
                        "age_days": age_days,
                        "code_present": code_present_any,
                        "channel_id": channel_id,
                        "chunking": chunking_info,
                    },
                    "embedding": vec,
                    "embedding_model": os.getenv("VOYAGE_EMBED_MODEL", "voyage-2"),
                    "embedding_dim": VECTOR_DIM,
                }
            )
        if out_docs:
            if not self.config.upsert_existing:
                if chunks_coll.find_one({"video_id": video_id}):
                    print(f"Skip existing chunks {video_id}")
                    return
            else:
                try:
                    res = chunks_coll.delete_many({"video_id": video_id})
                    print(
                        f"[chunk] Removed {getattr(res, 'deleted_count', 0)} existing chunk(s) for video_id={video_id}"
                    )
                except Exception:
                    # proceed even if delete fails; upserts will overwrite matching chunk_ids
                    print(
                        f"[chunk] Warning: failed to delete existing chunks for video_id={video_id}; proceeding with upserts"
                    )
            try:
                from pymongo import UpdateOne

                BATCH = 500
                for i in range(0, len(out_docs), BATCH):
                    batch = out_docs[i : i + BATCH]
                    print(
                        f"[chunk] Writing batch {i//BATCH + 1} with {len(batch)} chunk(s)"
                    )
                    ops = [
                        UpdateOne(
                            {"video_id": d["video_id"], "chunk_id": d["chunk_id"]},
                            {"$set": d},
                            upsert=True,
                        )
                        for d in batch
                    ]
                    if ops:
                        chunks_coll.bulk_write(ops, ordered=False)
            except Exception:
                for d in out_docs:
                    chunks_coll.update_one(
                        {"video_id": d["video_id"], "chunk_id": d["chunk_id"]},
                        {"$set": d},
                        upsert=True,
                    )
            print(
                f"Chunked+Embedded {video_id}: {len(out_docs)} chunks (strategy={self.config.chunk_strategy})"
            )


if __name__ == "__main__":
    stage = ChunkStage()
    raise SystemExit(stage.run())
