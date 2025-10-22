import os
import json
import uuid
import argparse
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from app.services.retrieval import (
    vector_search,
    hybrid_search,
    keyword_search,
)
from app.services.indexes import setup_vector_search_index
from app.services.generation import answer_with_openai
from app.services.utils import get_mongo_client
from config.paths import DB_NAME, COLL_CHUNKS, COLL_MEMORY_LOGS


# -----------------------------
# Session & Memory Utilities
# -----------------------------

# ANSI colors (no external deps)
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"


def generate_session_id() -> str:
    return str(uuid.uuid4())


def load_long_term_memory(session_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    client = get_mongo_client()
    db = client[DB_NAME]
    cur = (
        db[COLL_MEMORY_LOGS]
        .find({"session_id": session_id})
        .sort("created_at", -1)
        .limit(int(limit))
    )
    return list(cur)


def upsert_vector_index() -> None:
    client = get_mongo_client()
    db = client[DB_NAME]
    col = db[COLL_CHUNKS]
    setup_vector_search_index(col)


def setup_logger(session_id: str, log_dir: str = "chat_logs") -> logging.Logger:
    logger = logging.getLogger(f"chat_cli_{session_id}")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    # Ensure directory
    p = Path(log_dir)
    p.mkdir(parents=True, exist_ok=True)
    # File handler per session
    fh = logging.FileHandler(p / f"{session_id}.log", encoding="utf-8")
    fh.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    # Optional console handler with minimal format
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    ch.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(ch)
    return logger


def cprint(text: str, color: str = RESET) -> None:
    print(f"{color}{text}{RESET}")


# -----------------------------
# Query Rewrite Agent
# -----------------------------


def _openai_available() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def rewrite_query(
    user_query: str,
    short_term_msgs: List[Dict[str, str]],
    long_term_logs: List[Dict[str, Any]],
    default_mode: str,
    default_k: int,
) -> Tuple[str, str, int, Optional[Dict[str, Any]]]:
    """Return (rewritten_query, tool_mode, top_k, filters).

    Falls back to identity rewrite when no LLM configured.
    """
    if not _openai_available():
        return user_query, default_mode, default_k, None

    try:
        from openai import OpenAI  # type: ignore

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Build memory snippets (truncate for safety)
        recent_msgs = short_term_msgs[-8:]
        stm = "\n".join(f"{m['role']}: {m['content'][:400]}" for m in recent_msgs)
        ltm = "\n".join(
            f"Q: {log.get('user_query_raw','')[:200]}\nA: {str(log.get('answer',''))[:300]}"
            for log in long_term_logs[:8]
        )

        system_prompt = (
            "You improve user queries for retrieval using conversation memory. "
            "Return strict JSON with keys: query, tool, k, filters. "
            "tool in {auto, vector, hybrid, keyword}; k is int 1..50; filters is a JSON object or null."
        )
        user_prompt = (
            f"USER_QUERY: {user_query}\n\n"
            f"SHORT_TERM:\n{stm or '(none)'}\n\n"
            f"LONG_TERM:\n{ltm or '(none)'}\n\n"
            f'DEFAULTS: {{"tool": "{default_mode}", "k": {default_k}}}\n\n'
            "Respond with JSON only."
        )

        resp = client.chat.completions.create(
            model=os.getenv("OPENAI_DEFAULT_MODEL", "gpt-5-nano"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        text = resp.choices[0].message.content.strip()
        data: Dict[str, Any] = json.loads(text)
        rq = str(data.get("query") or user_query)
        tool = str(data.get("tool") or default_mode).lower()
        if tool not in {"auto", "vector", "hybrid", "keyword"}:
            tool = default_mode
        k = int(data.get("k") or default_k)
        if k < 1 or k > 50:
            k = default_k
        filters = data.get("filters")
        if not isinstance(filters, dict):
            filters = None
        return rq, tool, k, filters
    except Exception:
        return user_query, default_mode, default_k, None


# -----------------------------
# Retrieval Tooling
# -----------------------------


def run_retrieval(
    mode: str,
    query_text: str,
    top_k: int,
    filters: Optional[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    client = get_mongo_client()
    db = client[DB_NAME]
    col = db[COLL_CHUNKS]

    # Ensure index exists once at first retrieval
    setup_vector_search_index(col)

    # Hybrid requires both text and vector, but the helper computes vector internally
    if mode == "hybrid":
        # hybrid_search expects both query_text and query_vector; we rely on rag.embed_query
        from app.services.rag import embed_query  # lazy import to reuse voyage logic

        qvec = embed_query(query_text)
        return hybrid_search(
            col, query_text=query_text, query_vector=qvec, top_k=top_k, filters=filters
        )
    elif mode == "keyword":
        return keyword_search(col, query_text=query_text, top_k=top_k, filters=filters)
    else:
        # vector or auto->vector by default
        from app.services.rag import embed_query  # lazy import

        qvec = embed_query(query_text)
        return vector_search(col, qvec, k=top_k, filters=filters)


def normalize_context_blocks(hits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Ensure context blocks have a 'embedding_text' or 'text' field for answer composition."""
    out: List[Dict[str, Any]] = []
    for h in hits:
        block = dict(h)
        # If only 'text' exists, mirror into 'embedding_text' for the answer helper
        if "embedding_text" not in block and "text" in block:
            block["embedding_text"] = block.get("text")
        out.append(block)
    return out


# -----------------------------
# Answer Agent
# -----------------------------


def answer_with_context(
    contexts: List[Dict[str, Any]],
    rewritten_query: str,
    short_term_msgs: List[Dict[str, str]],
) -> str:
    # Optionally prepend a tiny conversational hint into the question
    history_hint = "\n\nRecent context:\n" + "\n".join(
        f"{m['role']}: {m['content'][:140]}" for m in short_term_msgs[-4:]
    )
    question = rewritten_query + history_hint
    return answer_with_openai(contexts, question)


def persist_turn(
    session_id: str,
    raw_query: str,
    rewritten_query: str,
    mode: str,
    top_k: int,
    filters: Optional[Dict[str, Any]],
    hits: List[Dict[str, Any]],
    answer: str,
) -> None:
    client = get_mongo_client()
    db = client[DB_NAME]
    retrieved = [
        {
            "video_id": h.get("video_id"),
            "chunk_id": h.get("chunk_id"),
            "score": h.get("score") or h.get("search_score"),
            "keyword_score": h.get("keyword_score"),
            "vector_score": h.get("vector_score"),
        }
        for h in hits
    ]
    doc = {
        "session_id": session_id,
        "user_query_raw": raw_query,
        "user_query_rewritten": rewritten_query,
        "mode": mode,
        "k": int(top_k),
        "filters": filters or {},
        "retrieved": retrieved,
        "answer": answer,
        "created_at": datetime.now(timezone.utc),
    }
    db[COLL_MEMORY_LOGS].insert_one(doc)


def format_citations(hits: List[Dict[str, Any]], max_items: int = 5) -> str:
    items: List[str] = []
    seen: set[str] = set()
    for h in hits:
        vid = str(h.get("video_id"))
        cid = str(h.get("chunk_id"))
        key = f"{vid}:{cid}"
        if key in seen:
            continue
        seen.add(key)
        score = h.get("final_score") or h.get("score") or h.get("search_score")
        items.append(
            f"({key}) score={score:.3f}"
            if isinstance(score, (int, float))
            else f"({key})"
        )
        if len(items) >= max_items:
            break
    return "\n".join(items)


# -----------------------------
# Export Helpers
# -----------------------------


def export_last_turn(
    last_turn: Optional[Dict[str, Any]], fmt: str, path: Optional[str], session_id: str
) -> Optional[str]:
    if not last_turn:
        return None
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    fmt = (fmt or "json").lower()
    if fmt not in {"json", "txt", "md"}:
        fmt = "json"
    default_name = f"export_{session_id}_{ts}.{fmt}"
    out_path = Path(path) if path else Path(default_name)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if fmt == "json":
        payload = {
            "session_id": session_id,
            **{k: v for k, v in last_turn.items()},
        }
        out_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    else:
        q = last_turn.get("user_query_raw", "")
        rq = last_turn.get("user_query_rewritten", "")
        mode = last_turn.get("mode", "")
        k = last_turn.get("k", "")
        filters = last_turn.get("filters", {})
        answer = last_turn.get("answer", "")
        citations = format_citations(last_turn.get("hits", []) or [])
        if fmt == "txt":
            content = (
                f"Session: {session_id}\n\n"
                f"Question: {q}\nRewritten: {rq}\nMode: {mode}  k={k}\nFilters: {json.dumps(filters)}\n\n"
                f"Answer:\n{answer}\n\nCitations:\n{citations}\n"
            )
        else:  # md
            content = (
                f"# Export — Session {session_id}\n\n"
                f"## Question\n{q}\n\n"
                f"## Rewritten\n{rq}\n\n"
                f"## Retrieval\n- Mode: `{mode}`  k={k}\n- Filters: `{json.dumps(filters)}`\n\n"
                f"## Answer\n\n{answer}\n\n"
                f"## Citations\n\n{citations}\n"
            )
        out_path.write_text(content, encoding="utf-8")
    return str(out_path)


# -----------------------------
# CLI Orchestrator
# -----------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Agentic, Memory-Aware CLI Chat")
    parser.add_argument(
        "--session", type=str, required=False, help="Resume a session by id"
    )
    parser.add_argument("--top_k", type=int, default=8, help="Top-k retrieval")
    parser.add_argument(
        "--mode",
        type=str,
        default="auto",
        choices=["auto", "vector", "hybrid", "keyword"],
        help="Retrieval mode override",
    )
    parser.add_argument(
        "--log_dir", type=str, default="chat_logs", help="Directory for session logs"
    )
    return parser.parse_args()


def run_cli() -> None:
    args = parse_args()
    session_id = args.session or generate_session_id()
    print(f"Session: {session_id}")

    # Bootstrap index (no-op if exists)
    upsert_vector_index()

    # Load long-term memory snapshot
    long_term_logs = load_long_term_memory(session_id=session_id, limit=20)
    short_term_memory: List[Dict[str, str]] = []
    logger = setup_logger(session_id, args.log_dir)
    last_turn: Optional[Dict[str, Any]] = None

    print(
        "Type your question. Commands: :exit, :new, :history, :id, :export <fmt> [path]"
    )
    while True:
        try:
            raw = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not raw:
            continue

        if raw in {":exit", ":quit"}:
            print("Goodbye!")
            break
        if raw == ":id":
            print(f"Session: {session_id}")
            continue
        if raw.startswith(":export"):
            parts = raw.split()
            fmt = parts[1] if len(parts) >= 2 else "json"
            path = parts[2] if len(parts) >= 3 else None
            exported = export_last_turn(last_turn, fmt, path, session_id)
            if exported:
                cprint(f"Exported last turn to {exported}", GREEN)
                logger.info(f"export: path={exported} fmt={fmt}")
            else:
                cprint("No previous turn to export.", YELLOW)
            continue
        if raw == ":history":
            for m in short_term_memory[-10:]:
                role = m.get("role")
                content = m.get("content", "")[:200]
                print(f"- {role}: {content}")
            continue
        if raw == ":new":
            session_id = generate_session_id()
            long_term_logs = load_long_term_memory(session_id=session_id, limit=20)
            short_term_memory = []
            print(f"New session: {session_id}")
            logger = setup_logger(session_id, args.log_dir)
            last_turn = None
            continue

        # 1) Update short-term memory with user turn
        short_term_memory.append({"role": "user", "content": raw})

        # 2) Rewrite query (uses memory)
        cprint("[1/5] Rewriting query...", CYAN)
        logger.info("rewrite:start")
        rewritten, tool_mode, k, filters = rewrite_query(
            user_query=raw,
            short_term_msgs=short_term_memory,
            long_term_logs=long_term_logs,
            default_mode=args.mode,
            default_k=int(args.top_k),
        )
        # If user passed a concrete override, respect it
        effective_mode = args.mode if args.mode != "auto" else tool_mode
        if effective_mode == "auto":
            effective_mode = "vector"  # default path
        logger.info(
            "rewrite:done raw=%s rewritten=%s mode=%s k=%s filters=%s",
            raw[:200],
            rewritten[:200],
            effective_mode,
            k,
            json.dumps(filters or {}),
        )
        cprint(
            f"[2/5] Retrieval plan → mode={effective_mode} k={k} filters={(filters or {})}",
            BLUE,
        )

        # 3) Retrieve
        cprint("[3/5] Retrieving context...", MAGENTA)
        logger.info("retrieve:start mode=%s k=%s", effective_mode, k)
        hits = run_retrieval(
            mode=effective_mode,
            query_text=rewritten,
            top_k=k,
            filters=filters,
        )
        logger.info("retrieve:done hits=%s", len(hits))
        cprint(f"[3/5] Retrieved {len(hits)} chunks", MAGENTA)

        # 4) Answer
        cprint("[4/5] Generating answer...", YELLOW)
        logger.info("answer:start")
        contexts = normalize_context_blocks(hits)
        answer = answer_with_context(contexts, rewritten, short_term_memory)
        logger.info("answer:done chars=%s", len(answer or ""))

        # 5) Persist
        try:
            logger.info("persist:start")
            persist_turn(
                session_id=session_id,
                raw_query=raw,
                rewritten_query=rewritten,
                mode=effective_mode,
                top_k=k,
                filters=filters,
                hits=hits,
                answer=answer,
            )
            # Refresh long-term cache
            long_term_logs = load_long_term_memory(session_id=session_id, limit=20)
            logger.info("persist:done")
        except Exception as e:
            print(f"[warn] failed to persist log: {e}")
            logger.exception("persist:error %s", e)

        # 6) Emit to CLI and update short-term memory
        cprint("[5/5] Answer:\n", GREEN)
        print(answer or "(no response)")
        if hits:
            cprint("\nCitations:", DIM)
            print(format_citations(hits))
        short_term_memory.append({"role": "assistant", "content": answer})

        # Update exportable snapshot
        last_turn = {
            "user_query_raw": raw,
            "user_query_rewritten": rewritten,
            "mode": effective_mode,
            "k": k,
            "filters": filters or {},
            "hits": hits,
            "answer": answer,
        }


if __name__ == "__main__":
    # TODO:
    # skip for now: in the frontend it has to be possible to exclude questions/answer from a conversation (from the short and long term memory)
    run_cli()
