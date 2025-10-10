import os
from typing import Any, Dict, Optional

from core.base_pipeline import BasePipeline


class VideoPipeline(BasePipeline):
    """Thin wrapper to standardize stage names and directories if needed.

    Current implementation uses DB collections; file helpers remain available for
    future enhancements (e.g., caching artifacts to disk per video_id).
    """

    def __init__(self) -> None:
        # Stage order can be used to report progress
        self.stages: list[str] = [
            "ingest",
            "clean",
            "enrich",
            "chunk",
            "redundancy",
            "trust",
        ]

    def summarize_artifact(self, stage: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if stage == "clean":
            cleaned_text = payload.get("cleaned_text", "")
            return {"cleaned_len": len(cleaned_text)}
        if stage == "ingest":
            return {
                "has_metadata": bool(payload.get("title")),
                "has_transcript": bool(payload.get("transcript_raw")),
            }
        if stage == "enrich":
            segments = payload.get("segments", [])
            return {"segments": len(segments)}
        if stage == "chunk":
            return {"chunks": payload.get("chunks", 0)}
        return {}

    @staticmethod
    def allow_upsert_existing() -> bool:
        val = os.getenv("INGEST_UPSERT_EXISTING", "false").strip().lower()
        return val in {"1", "true", "yes", "on"}
