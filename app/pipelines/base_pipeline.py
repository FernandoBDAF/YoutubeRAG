from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Type, Union

# Stage imports (registry)
from app.stages.clean import CleanStage, CleanConfig
from app.stages.chunk import ChunkStage, ChunkConfig
from app.stages.enrich import EnrichStage, EnrichConfig
from app.stages.ingest import IngestStage, IngestConfig
from app.stages.embed import EmbedStage, EmbedConfig
from app.stages.redundancy import RedundancyStage, RedundancyConfig
from app.stages.trust import TrustStage, TrustConfig
from app.stages.compress import CompressStage, CompressConfig
from app.stages.backfill_transcript import (
    BackfillTranscriptStage,
    BackfillTranscriptConfig,
)

# GraphRAG stage imports
from app.stages.graph_extraction import GraphExtractionStage
from app.stages.entity_resolution import EntityResolutionStage
from app.stages.graph_construction import GraphConstructionStage
from app.stages.community_detection import CommunityDetectionStage
from config.stage_config import BaseStageConfig


StageClass = Union[
    Type[CleanStage],
    Type[ChunkStage],
    Type[EnrichStage],
    Type[IngestStage],
    Type[EmbedStage],
    Type[RedundancyStage],
    Type[TrustStage],
    Type[CompressStage],
    Type[BackfillTranscriptStage],
    Type[GraphExtractionStage],
    Type[EntityResolutionStage],
    Type[GraphConstructionStage],
    Type[CommunityDetectionStage],
]


STAGE_REGISTRY: Dict[str, StageClass] = {
    "clean": CleanStage,
    "chunk": ChunkStage,
    "enrich": EnrichStage,
    "ingest": IngestStage,
    "embed": EmbedStage,
    "redundancy": RedundancyStage,
    "trust": TrustStage,
    "compress": CompressStage,
    "backfill_transcript": BackfillTranscriptStage,
    "graph_extraction": GraphExtractionStage,
    "entity_resolution": EntityResolutionStage,
    "graph_construction": GraphConstructionStage,
    "community_detection": CommunityDetectionStage,
}


@dataclass
class StageSpec:
    """Strongly-typed stage specification.

    - stage can be a registry key or a Stage class
    - config must be an instance of the exact ConfigCls for the stage (or None for defaults)
    """

    stage: Union[str, StageClass]
    config: Optional[BaseStageConfig] = None


class PipelineRunner:
    def __init__(
        self,
        specs: List[StageSpec],
        default_read_db: Optional[str] = None,
        default_write_db: Optional[str] = None,
        stop_on_error: bool = True,
    ) -> None:
        self.specs = specs
        self.default_read_db = default_read_db
        self.default_write_db = default_write_db
        self.stop_on_error = stop_on_error

    def _resolve_stage_class(self, ref: Union[str, StageClass]) -> StageClass:
        if isinstance(ref, str):
            key = ref.strip().lower()
            if key not in STAGE_REGISTRY:
                raise KeyError(f"Unknown stage: {ref}")
            return STAGE_REGISTRY[key]
        return ref

    def run(self) -> int:
        exit_codes: List[int] = []
        totals = {"stages": 0, "failed": 0}
        for i, spec in enumerate(self.specs, start=1):
            stage_cls = self._resolve_stage_class(spec.stage)
            stage = stage_cls()

            # Build config object from the stage's ConfigCls
            cfg_cls = getattr(stage, "ConfigCls", None)
            if cfg_cls is None:
                raise RuntimeError(f"Stage {stage_cls.__name__} missing ConfigCls")

            if spec.config is None:
                config = cfg_cls()  # type: ignore
            else:
                if not isinstance(spec.config, cfg_cls):  # type: ignore
                    raise TypeError(
                        f"Config type mismatch for stage {stage_cls.__name__}: "
                        f"expected {cfg_cls.__name__}, got {type(spec.config).__name__}"
                    )
                config = spec.config

            print(
                f"[pipeline] ({i}/{len(self.specs)}) Running {stage.name} with read_db={config.read_db_name or config.db_name} write_db={config.write_db_name or config.db_name}"
            )
            code = stage.run(config)
            exit_codes.append(code)
            totals["stages"] += 1
            if code != 0:
                totals["failed"] += 1
                print(f"[pipeline] Stage {stage.name} failed with code {code}")
                if self.stop_on_error:
                    print("[pipeline] stop_on_error=True → stopping")
                    return code

        succeeded = totals["stages"] - totals["failed"]
        print(
            f"[pipeline] Completed stages: {succeeded}/{totals['stages']}; failures: {totals['failed']}"
        )
        return 0 if totals["failed"] == 0 else 1
