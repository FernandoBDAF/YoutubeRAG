# APP Layer - LLM Context Guide

**Layer Purpose**: External interface - Anything that runs or talks to the external world

---

## What Belongs in APP Layer

✅ **Command-line interfaces** (CLIs with argparse)  
✅ **User interfaces** (Streamlit, web apps)  
✅ **API servers** (REST APIs, MCP servers)  
✅ **Executable scripts** (testing, diagnostics, utilities)

❌ **Business logic** (goes in BUSINESS)  
❌ **Data models** (goes in CORE)  
❌ **Infrastructure code** (goes in DEPENDENCIES)

---

## Structure

```
app/
├── cli/                # Command-line interfaces
│   ├── main.py         # Ingestion pipeline CLI
│   ├── graphrag.py     # GraphRAG pipeline CLI
│   └── chat.py         # Chat interface CLI
│
├── ui/                 # User interfaces
│   └── streamlit_app.py
│
├── api/                # REST APIs (future)
│   └── server.py       # MCP server
│
└── scripts/            # Runnable utility scripts
    ├── graphrag/       # GraphRAG testing/diagnostics
    └── utilities/      # General utilities
```

---

## Import Pattern

APP layer can import from all layers below:

```python
# app/cli/main.py
from business.pipelines.ingestion import IngestionPipeline  # BUSINESS
from core.config.paths import DB_NAME                       # CORE
from dependencies.database.mongodb import get_mongo_client  # DEPENDENCIES
```

---

## Example: CLI Structure

```python
# app/cli/graphrag.py
from business.pipelines.graphrag import GraphRAGPipeline
from core.config.graphrag import GraphRAGPipelineConfig
from dependencies.observability.logging import setup_logging

def main():
    # Parse CLI arguments (APP layer responsibility)
    args = parse_args()

    # Setup logging (via DEPENDENCIES)
    setup_logging(verbose=args.verbose, log_file=args.log_file)

    # Create configuration (from CORE)
    config = GraphRAGPipelineConfig.from_args_env(args, env, db)

    # Run pipeline (from BUSINESS)
    pipeline = GraphRAGPipeline(config)
    exit_code = pipeline.run_full_pipeline()

    sys.exit(exit_code)
```

**Key**: CLI orchestrates, business logic executes

---

## Files in APP Layer

### CLIs (3 files):

- `cli/main.py` - Ingestion pipeline CLI
- `cli/graphrag.py` - GraphRAG pipeline CLI
- `cli/chat.py` - Chat interface CLI

### UI (1 file):

- `ui/streamlit_app.py` - Streamlit dashboard

### Scripts (10 files):

- `scripts/graphrag/` - 8 GraphRAG testing scripts
- `scripts/utilities/` - 2 utility scripts

---

## Running from APP Layer

```bash
# Run CLIs
python -m app.cli.main pipeline --playlist_id ID --max 10
python -m app.cli.graphrag --max 10
python -m app.cli.chat

# Run UI
streamlit run app/ui/streamlit_app.py

# Run scripts
python -m app.scripts.graphrag.analyze_graph_structure
python -m app.scripts.utilities.full_cleanup
```

---

## When Adding New Code

**Ask**: Does this run or talk to users/external systems?

- **Yes** → APP layer
- **No** → Check other layers (BUSINESS, CORE, DEPENDENCIES)

**Examples**:

- New CLI command → `app/cli/`
- New API endpoint → `app/api/routes/`
- New diagnostic script → `app/scripts/`
- New UI screen → `app/ui/`

---

**For implementation details, see**: `documentation/architecture/`
