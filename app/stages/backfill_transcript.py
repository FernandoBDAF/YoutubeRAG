from dataclasses import dataclass, field
from typing import List, Optional

try:
    from app.services.transcripts import get_transcript
    from config.paths import COLL_RAW_VIDEOS
    from core.base_stage import BaseStage
    from core.stage_config import BaseStageConfig
except ModuleNotFoundError:
    import sys as _sys, os as _os

    _sys.path.append(
        _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
    )
    from app.services.transcripts import get_transcript
    from config.paths import COLL_RAW_VIDEOS
    from core.base_stage import BaseStage
    from core.stage_config import BaseStageConfig


@dataclass
class BackfillTranscriptConfig(BaseStageConfig):
    languages: List[str] = field(default_factory=lambda: ["en", "en-US", "en-GB"])

    @classmethod
    def from_args_env(cls, args, env, default_db):
        base = BaseStageConfig.from_args_env(args, env, default_db)
        langs = getattr(args, "languages", None) or ["en", "en-US", "en-GB"]
        return cls(**vars(base), languages=langs)


class BackfillTranscriptStage(BaseStage):
    name = "backfill_transcript"
    description = "Fill missing transcript_raw for raw_videos or a single video"
    ConfigCls = BackfillTranscriptConfig

    def build_parser(self, p):
        super().build_parser(p)
        p.add_argument("--languages", nargs="*", default=["en", "en-US", "en-GB"])

    def iter_docs(self):
        # Read from configured read DB/collection (default raw_videos)
        src_db = self.config.read_db_name or self.config.db_name
        coll = self.get_collection(
            self.config.read_coll or COLL_RAW_VIDEOS, io="read", db_name=src_db
        )
        if self.config.video_id:
            q = {"video_id": self.config.video_id}
        else:
            q = {
                "$or": [
                    {"transcript_raw": {"$exists": False}},
                    {"transcript_raw": None},
                    {"transcript_raw": ""},
                ]
            }
        return list(coll.find(q, {"video_id": 1}))

    def handle_doc(self, d):
        vid = d["video_id"]
        src_db = self.config.read_db_name or self.config.db_name
        dst_db = self.config.write_db_name or self.config.db_name
        read_coll = self.get_collection(
            self.config.read_coll or COLL_RAW_VIDEOS, io="read", db_name=src_db
        )
        write_coll = self.get_collection(
            self.config.write_coll or COLL_RAW_VIDEOS, io="write", db_name=dst_db
        )
        existing = read_coll.find_one({"video_id": vid}, {"transcript_raw": 1})
        if (
            existing.get("transcript_raw") or ""
        ).strip() and not self.config.upsert_existing:
            self.stats["skipped"] += 1
            self.log(f"Skip existing {vid}")
            return
        url = f"https://www.youtube.com/watch?v={vid}"
        self.log(f"Fetching transcript for {vid} (langs={self.config.languages})")
        print(f"Fetching transcript for {vid} (langs={self.config.languages})")
        items = get_transcript(url, languages=self.config.languages)
        if not items:
            self.stats["failed"] += 1
            self.log(f"No transcript found for {vid}")
            print(f"No transcript found for {vid}")
            return
        text = "\n".join(i.get("text", "") for i in items if i.get("text"))
        if not self.config.dry_run:
            write_coll.update_one(
                {"video_id": vid}, {"$set": {"transcript_raw": text}}, upsert=True
            )
        self.stats["updated"] += 1
        self.log(f"Updated {vid} chars={len(text)}")
        print(f"Updated {vid} chars={len(text)}")


if __name__ == "__main__":
    stage = BackfillTranscriptStage()
    raise SystemExit(stage.run())
