"""
Chat Memory and Session Management.

This module handles session management and long-term memory for chat conversations.
Part of the BUSINESS layer - chat feature business logic.
"""

import uuid
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from dependencies.database.mongodb import get_mongo_client
from core.config.paths import DB_NAME, COLL_MEMORY_LOGS


def generate_session_id() -> str:
    """Generate a unique session ID.

    Returns:
        UUID string for session identification
    """
    return str(uuid.uuid4())


def load_long_term_memory(session_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Load long-term memory logs for a session.

    Args:
        session_id: Session identifier
        limit: Maximum number of logs to retrieve (default: 20)

    Returns:
        List of memory log documents, most recent first
    """
    client = get_mongo_client()
    db = client[DB_NAME]
    cur = (
        db[COLL_MEMORY_LOGS]
        .find({"session_id": session_id})
        .sort("created_at", -1)
        .limit(int(limit))
    )
    return list(cur)


def setup_chat_logger(session_id: str, log_dir: str = "chat_logs") -> logging.Logger:
    """Setup session-specific logger for chat.

    Args:
        session_id: Session identifier
        log_dir: Directory for chat logs (default: "chat_logs")

    Returns:
        Configured logger instance
    """
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


def persist_turn(
    session_id: str,
    raw_query: str,
    rewritten_query: str,
    mode: str,
    top_k: int,
    filters: Optional[Dict[str, Any]],
    hits: List[Dict[str, Any]],
    answer: str,
    agent: Optional[str] = "reference_answer",
) -> None:
    """Persist a conversation turn to long-term memory.

    Args:
        session_id: Session identifier
        raw_query: Original user query
        rewritten_query: Rewritten query (after context)
        mode: Retrieval mode used
        top_k: Number of results requested
        filters: Filters applied
        hits: Search result documents
        answer: Generated answer
        agent: Agent used for answering (default: "reference_answer")
    """
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
        "agent": agent,
        "created_at": datetime.now(timezone.utc),
    }

    db[COLL_MEMORY_LOGS].insert_one(doc)
