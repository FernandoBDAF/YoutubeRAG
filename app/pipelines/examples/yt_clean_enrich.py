try:
    from app.pipelines.base_pipeline import StageSpec, PipelineRunner
    from app.stages.clean import CleanConfig
    from app.stages.compress import CompressConfig
    from app.stages.chunk import ChunkConfig
    from app.stages.enrich import EnrichConfig
    from app.stages.embed import EmbedConfig
except ModuleNotFoundError:
    import os as _os, sys as _sys

    _sys.path.append(
        _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", "..", ".."))
    )
    from app.pipelines.base_pipeline import StageSpec, PipelineRunner
    from app.stages.clean import CleanConfig
    from app.stages.compress import CompressConfig
    from app.stages.chunk import ChunkConfig
    from app.stages.enrich import EnrichConfig
    from app.stages.embed import EmbedConfig


# Example: cross-DB IO
# - Read raw videos from DB "source_db" and write cleaned to DB "work_db"
# - Compress reads/writes cleaned in "work_db"
# - Chunk reads cleaned from "work_db" and writes chunks to "work_db"
# - Enrich then Embed read and write chunks inside "work_db"

specs = [
    # 1) Clean
    StageSpec(
        stage="clean",
        config=CleanConfig(
            # BaseStageConfig (common)
            max=None,
            llm=True,
            verbose=True,
            dry_run=False,
            db_name=None,
            read_db_name=None,
            write_db_name=None,
            read_coll=None,
            write_coll=None,
            upsert_existing=False,
            video_id=None,
            concurrency=15,
            # Clean specific
            use_llm=True,
            llm_retries=4,
            llm_backoff_s=10.0,
            llm_qps=None,
            model_name="gpt-5-nano",
        ),
    ),
    # 2) Compress
    # StageSpec(
    #     stage="compress",
    #     config=CompressConfig(
    #         # Base
    #         max=None,
    #         llm=False,
    #         verbose=True,
    #         dry_run=False,
    #         db_name="work_db",
    #         read_db_name="work_db",
    #         write_db_name="work_db",
    #         read_coll="cleaned_transcripts",
    #         write_coll="cleaned_transcripts",
    #         upsert_existing=True,
    #         video_id="oS9aPzUNG-s",
    #         concurrency=None,
    #         # Compress specific
    #         target_tokens=1200,
    #         ratio=0.4,
    #         reorder="sort",
    #         model="microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank",
    #         source="cleaned",
    #         strict_cleanup=True,
    #     ),
    # ),
    # 3) Chunk
    StageSpec(
        stage="chunk",
        config=ChunkConfig(
            # Base
            max=None,
            llm=False,
            verbose=True,
            dry_run=False,
            db_name=None,
            read_db_name=None,
            write_db_name=None,
            read_coll=None,
            write_coll=None,
            upsert_existing=False,
            video_id=None,
            concurrency=None,
            # Chunk specific
            chunk_strategy="recursive",
            token_size=500,
            overlap_pct=0.15,
            split_chars=[".", "?", "!"],
            semantic_model=None,
        ),
    ),
    # 4) Enrich
    StageSpec(
        stage="enrich",
        config=EnrichConfig(
            # Base
            max=None,
            llm=True,
            verbose=True,
            dry_run=False,
            db_name=None,
            read_db_name=None,
            write_db_name=None,
            read_coll=None,
            write_coll=None,
            upsert_existing=False,
            video_id=None,
            concurrency=15,
            # Enrich specific
            use_llm=True,
            llm_retries=4,
            llm_backoff_s=10.0,
            llm_qps=None,
            model_name="gpt-5-nano",
        ),
    ),
    # 5) Embed
    StageSpec(
        stage="embed",
        config=EmbedConfig(
            # Base
            max=None,
            llm=False,
            verbose=True,
            dry_run=False,
            db_name=None,
            read_db_name=None,
            write_db_name=None,
            read_coll=None,
            write_coll=None,
            upsert_existing=False,
            video_id=None,
            concurrency=None,
            # Embed specific
            embed_source="chunk",  # or "summary"
            use_hybrid_embedding_text=True,
            unit_normalize_embeddings=True,
            emit_multi_vectors=False,
        ),
    ),
]


if __name__ == "__main__":
    PipelineRunner(specs).run()
