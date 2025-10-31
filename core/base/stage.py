import os
import time
import argparse
import logging
from typing import Any, Dict, Iterable, Optional

from dotenv import load_dotenv
from pymongo import MongoClient

try:
    from dependencies.database.mongodb import get_mongo_client
except ModuleNotFoundError:
    import sys as _sys, os as _os

    _sys.path.append(_os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..")))
    from dependencies.database.mongodb import get_mongo_client

from core.config.paths import DB_NAME as DEFAULT_DB
from core.models.config import BaseStageConfig


class BaseStage:
    name = "base"
    description = ""
    ConfigCls = BaseStageConfig

    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        self.args: argparse.Namespace = argparse.Namespace()
        self.config: BaseStageConfig = self.ConfigCls()
        self.client: MongoClient = None  # type: ignore
        self.db = None
        self.db_read = None
        self.db_write = None
        self.logger = logger or logging.getLogger(self.name)
        self.start_ts = time.time()
        self.stats = {"processed": 0, "skipped": 0, "failed": 0, "updated": 0}

    def build_parser(self, p: argparse.ArgumentParser) -> None:
        p.add_argument("--max", type=int)
        p.add_argument("--llm", action="store_true")
        p.add_argument("--verbose", action="store_true")
        p.add_argument("--dry_run", action="store_true")
        p.add_argument(
            "--db_name",
            help="Override DB name (defaults to config.paths.DB_NAME or $DB_NAME)",
        )
        p.add_argument("--upsert_existing", action="store_true")
        p.add_argument("--video_id", type=str)
        p.add_argument("--concurrency", type=int)

    def parse_args(self) -> None:
        p = argparse.ArgumentParser(description=self.description or self.name)
        self.build_parser(p)
        self.args = p.parse_args()

    def setup(self) -> None:
        load_dotenv()
        self.client = get_mongo_client()
        # Determine default/read/write DBs with fallbacks
        default_db_name = self.config.db_name or DEFAULT_DB
        # If specific read/write DBs aren't provided, fall back to the default DB
        write_db_name = self.config.write_db_name or default_db_name
        read_db_name = self.config.read_db_name or default_db_name
        # Default DB (backward compatibility)
        self.db = self.client[default_db_name]
        # Explicit read/write handles for per-stage overrides
        self.db_write = self.client[write_db_name]
        self.db_read = self.client[read_db_name]

    def log(self, msg: str) -> None:
        self.logger.info(f"[{self.name}] {msg}")

    def env_bool(self, key: str, default: bool = False) -> bool:
        v = os.getenv(key, str(default)).strip().lower()
        return v in {"1", "true", "yes", "on"}

    def build_config_from_args_env(self) -> BaseStageConfig:
        return self.ConfigCls.from_args_env(self.args, dict(os.environ), DEFAULT_DB)

    # Convenience helper to fetch collection from the desired IO side
    def get_collection(
        self, name: str, io: str = "read", db_name: Optional[str] = None
    ):
        """Return a collection handle.

        - If db_name is provided, return collection from that explicit database
        - Else, return from read/write DB selected by `io`
        """
        if db_name:
            return self.client[db_name][name]
        if io == "write":
            return self.db_write[name]
        return self.db_read[name]

    def iter_docs(self) -> Iterable[Dict[str, Any]]:
        raise NotImplementedError

    def handle_doc(self, doc: Dict[str, Any]) -> None:
        raise NotImplementedError

    def finalize(self) -> None:
        dur = time.time() - self.start_ts
        self.log(
            f"Summary: processed={self.stats['processed']} updated={self.stats['updated']} "
            f"skipped={self.stats['skipped']} failed={self.stats['failed']} in {dur:.1f}s"
        )

    def run(self, config: Optional[BaseStageConfig] = None) -> int:
        if config is None:
            self.parse_args()
            self.config = self.build_config_from_args_env()
        else:
            self.config = config
        self.setup()
        try:
            docs = list(self.iter_docs())
            total_docs = len(docs)
            if self.config.max:
                total_docs = min(total_docs, int(self.config.max))

            if total_docs > 0:
                self.logger.info(
                    f"[{self.name}] Processing {total_docs} document(s) "
                    f"(max={self.config.max if self.config.max else 'unlimited'})"
                )

            for i, d in enumerate(docs):
                if self.config.max and i >= int(self.config.max):
                    break
                try:
                    # Log progress for batches (every 10% or every 10 items, whichever is more frequent)
                    if total_docs > 10 and (i + 1) % max(1, total_docs // 10) == 0:
                        progress_pct = int((i + 1) / total_docs * 100)
                        self.logger.info(
                            f"[{self.name}] Progress: {i + 1}/{total_docs} ({progress_pct}%) "
                            f"processed={self.stats['processed']} "
                            f"updated={self.stats['updated']} "
                            f"skipped={self.stats['skipped']} "
                            f"failed={self.stats['failed']}"
                        )
                    self.handle_doc(d)
                    self.stats["processed"] += 1
                except Exception as e:
                    self.stats["failed"] += 1
                    self.log(f"Error: {e}")
                    self.logger.error(
                        f"[{self.name}] Error executing for document: {e}",
                        exc_info=False,
                    )
            self.finalize()
            return 0
        except Exception as e:
            self.log(f"Fatal: {e}")
            return 1
