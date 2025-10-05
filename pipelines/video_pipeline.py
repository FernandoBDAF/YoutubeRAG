from typing import Any, Dict, Optional

from base_pipeline import BasePipeline


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
        if stage == "enrich":
            segments = payload.get("segments", [])
            return {"segments": len(segments)}
        if stage == "chunk":
            return {"chunks": payload.get("chunks", 0)}
        return {}
