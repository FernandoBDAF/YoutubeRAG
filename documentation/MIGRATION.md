# Migration Guide: Old to New Pipeline System

This document guides you through migrating from the old pipeline system (artificial stage calling in `main.py`) to the new pipeline architecture using implemented pipelines.

## Overview of Changes

### What Changed

1. **Pipeline Implementation**: `main.py` now uses actual pipeline classes instead of artificial stage sequencing
2. **Ingestion Pipeline**: New `app/pipelines/ingestion_pipeline.py` includes all stages including redundancy and trust
3. **Pipeline Pattern**: All pipelines follow the `PipelineRunner` + `StageSpec` pattern for consistency
4. **Configuration**: Centralized configuration management via `IngestionPipelineConfig`

### What Stayed the Same

- Individual stage implementations (`app/stages/*.py`) - no changes
- Stage registry and `PipelineRunner` - already in use
- CLI interface - same commands work
- Environment variables - same variables control behavior

## Migration Steps

### Step 1: Update CLI Usage (No Changes Required)

The CLI interface remains the same:

```bash
# Still works exactly the same
python main.py pipeline --playlist_id <ID> --max 10 --llm
```

**What changed internally**: `main.py` now calls `IngestionPipeline.run_full_pipeline()` instead of manually calling stages.

### Step 2: Update Programmatic Usage

**Old Way** (if you were calling stages directly):

```python
# OLD: Manual stage calling
run_stage("ingest", args=args)
run_stage("clean", llm=True)
run_stage("enrich", llm=True)
# ... etc
```

**New Way** (using implemented pipeline):

```python
# NEW: Use implemented pipeline
from app.pipelines.ingestion_pipeline import IngestionPipeline, IngestionPipelineConfig
import os

env = dict(os.environ)
args = argparse.Namespace(playlist_id="PLxxx", max=10, llm=True)
config = IngestionPipelineConfig.from_args_env(args, env, "mongo_hack")
pipeline = IngestionPipeline(config)
exit_code = pipeline.run_full_pipeline()
```

### Step 3: Update Custom Scripts

If you have custom scripts that were calling stages manually:

**Old Pattern**:

```python
# OLD
from main import run_stage
run_stage("pipeline", args=cli_args, llm=True)
```

**New Pattern**:

```python
# NEW: Direct pipeline usage
from app.pipelines.ingestion_pipeline import IngestionPipeline
pipeline = IngestionPipeline.from_cli_args(args, kwargs)
exit_code = pipeline.run_full_pipeline()
```

## Backward Compatibility

### What Still Works

- ✅ All CLI commands (`python main.py pipeline ...`) work identically
- ✅ All environment variables work the same way
- ✅ Individual stage execution (`python main.py clean`) unchanged
- ✅ Stage-specific scripts (`python app/stages/clean.py`) unchanged

### What's New

- ✅ `IngestionPipeline` class for programmatic use
- ✅ Pipeline status monitoring capabilities
- ✅ Consistent pipeline pattern across all pipelines

### Breaking Changes

**None!** The migration is fully backward compatible. The old CLI interface continues to work, but now uses proper pipeline implementations internally.

## Understanding the New Architecture

### Pipeline Classes

**Before**: Stages were called sequentially via `run_stage()` function

**After**: Pipelines are classes that orchestrate stages using `PipelineRunner`

```python
# Old (internal implementation)
def run_pipeline():
    run_stage("ingest")
    run_stage("clean")
    # ... etc

# New (current implementation)
class IngestionPipeline:
    def run_full_pipeline(self):
        self.setup()
        return self.runner.run()  # Uses PipelineRunner
```

### Configuration Management

**Before**: Configuration passed via CLI args and env vars directly to stages

**After**: Pipeline-level configuration class (`IngestionPipelineConfig`) manages all stage configs

```python
# New pattern
config = IngestionPipelineConfig.from_args_env(args, env, default_db)
pipeline = IngestionPipeline(config)
```

### Stage Integration

**Before**: Redundancy and trust stages were called separately, not integrated into main pipeline

**After**: Redundancy and trust are part of `IngestionPipeline`, ensuring they run in correct order

## Benefits of New Architecture

1. **Proper Pipeline Abstraction**: Pipelines are first-class objects, not just function sequences
2. **Better Error Handling**: `PipelineRunner` provides consistent error handling
3. **Status Monitoring**: Pipelines can report status and handle cleanup
4. **Extensibility**: Easy to create new pipelines following the same pattern
5. **Testability**: Pipelines can be tested as units
6. **Documentation**: Pipeline architecture is clearly documented in `PIPELINE.md`

## Common Questions

### Q: Do I need to change my scripts?

**A**: Only if you were calling stages programmatically. CLI usage is unchanged.

### Q: What about the old `yt_clean_enrich.py` example?

**A**: It's kept as-is for reference but will be removed in the future. Use `IngestionPipeline` instead.

### Q: Can I still run individual stages?

**A**: Yes! Both methods work:

- `python main.py clean` (via orchestrator)
- `python app/pipelines/ingestion_pipeline.py --stage clean` (via pipeline)

### Q: What if I want to customize the pipeline order?

**A**: Create a custom pipeline class following the pattern in `documentation/PIPELINE.md`.

## Examples

### Example 1: Basic Pipeline Execution

```bash
# Works the same as before
python main.py pipeline --playlist_id PLxxx --max 10 --llm
```

### Example 2: Programmatic Pipeline Usage

```python
from app.pipelines.ingestion_pipeline import IngestionPipeline
import argparse
import os

args = argparse.Namespace(
    playlist_id="PLxxx",
    max=10,
    llm=True,
    verbose=False
)

env = dict(os.environ)
pipeline = IngestionPipeline.from_cli_args(args, {})
exit_code = pipeline.run_full_pipeline()
```

### Example 3: Custom Pipeline Configuration

```python
from app.pipelines.ingestion_pipeline import IngestionPipeline, IngestionPipelineConfig
from app.stages.chunk import ChunkConfig
import os

# Create custom configuration
env = dict(os.environ)
args = argparse.Namespace()

# Customize chunk config for PDF documents
chunk_config = ChunkConfig(
    chunk_strategy="recursive",
    token_size=300,  # Smaller chunks for PDFs
    overlap_pct=0.10
)

config = IngestionPipelineConfig.from_args_env(args, env, "mongo_hack")
config.chunk_config = chunk_config
pipeline = IngestionPipeline(config)
pipeline.run_full_pipeline()
```

## Troubleshooting

### Issue: Pipeline fails but individual stages work

**Solution**: Check that all stage configs are properly initialized. Use `--verbose` flag for detailed logs.

### Issue: Redundancy/Trust stages not running

**Solution**: Ensure you're using `IngestionPipeline` which includes these stages. The old `yt_clean_enrich.py` example doesn't include them.

### Issue: Configuration not applying

**Solution**: Check that configuration is passed correctly to `IngestionPipelineConfig.from_args_env()`.

## Next Steps

1. ✅ Use `python main.py pipeline` - it now uses the new implementation
2. ✅ Read `documentation/PIPELINE.md` for comprehensive pipeline documentation
3. ✅ Update any custom scripts to use `IngestionPipeline` class
4. ✅ Explore pipeline status monitoring and cleanup capabilities

## See Also

- `documentation/PIPELINE.md` - Comprehensive pipeline documentation
- `app/pipelines/ingestion_pipeline.py` - Ingestion pipeline implementation
- `app/pipelines/graphrag_pipeline.py` - GraphRAG pipeline reference implementation
