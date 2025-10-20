from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class BaseStageConfig:
    max: Optional[int] = None
    llm: bool = False
    verbose: bool = False
    dry_run: bool = False
    db_name: Optional[str] = None
    # Optional IO overrides (read/write DB and collection names)
    read_db_name: Optional[str] = None
    write_db_name: Optional[str] = None
    read_coll: Optional[str] = None
    write_coll: Optional[str] = None
    upsert_existing: bool = False
    video_id: Optional[str] = None
    concurrency: Optional[int] = None

    @classmethod
    def from_args_env(
        cls, args: Any, env: Dict[str, str], default_db: str
    ) -> "BaseStageConfig":
        # Pull IO overrides from args or env if present; remain optional for backward compatibility
        read_db = getattr(args, "read_db_name", None) or env.get("READ_DB_NAME")
        write_db = getattr(args, "write_db_name", None) or env.get("WRITE_DB_NAME")
        read_coll = getattr(args, "read_coll", None) or env.get("READ_COLL")
        write_coll = getattr(args, "write_coll", None) or env.get("WRITE_COLL")

        return cls(
            max=getattr(args, "max", None),
            # remove llm from args
            llm=bool(getattr(args, "llm", False)),
            verbose=bool(getattr(args, "verbose", False)),
            dry_run=bool(getattr(args, "dry_run", False)),
            db_name=getattr(args, "db_name", None) or env.get("DB_NAME") or default_db,
            read_db_name=read_db,
            write_db_name=write_db,
            read_coll=read_coll,
            write_coll=write_coll,
            upsert_existing=bool(getattr(args, "upsert_existing", False)),
            video_id=getattr(args, "video_id", None),
            concurrency=(
                int(getattr(args, "concurrency"))
                if getattr(args, "concurrency", None) is not None
                else None
            ),
        )
