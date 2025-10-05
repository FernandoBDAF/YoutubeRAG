## 🎛️ Streamlit-Controlled Agentic Flow System

### 1. Overview

In the CourseCopilot project, each stage of the RAG pipeline — from ingestion to summarization — runs as an independent agent.
To make this process observable, tunable, and demo-friendly, we integrate Streamlit as an interactive controller for the agentic flow.

The interface allows us to:

Trigger each agent individually or run the entire pipeline end-to-end.

Visualize intermediate outputs (e.g., cleaned transcripts, enrichment tags, embeddings, summaries).

Display pipeline metrics (time per stage, #chunks, redundancy rate, etc.).

Monitor and replay the agent reasoning using callback logs.

Behind the UI, an orchestration layer coordinates agents, tracks state, and exposes APIs for Streamlit to query.
We experimented with several orchestration patterns (LangChain, ControlFlow, LangGraph, Swarm) and adopted a hybrid pattern optimized for hackathon speed and transparency.

### 2. Architecture

        ┌───────────────────────────────┐
        │         Streamlit UI          │
        │  (dashboard + controller)     │
        └──────────────┬────────────────┘
                       │
            REST / Python API calls
                       │
        ┌──────────────┴──────────────┐
        │     Flow Orchestrator       │
        │ (ControlFlow or custom FSM) │
        └──────────────┬──────────────┘
                       │
             Sequential / parallel tasks
                       │
    ┌──────────────────┼──────────────────┐
    │    Agent Steps                     │
    │ Ingest → Clean → Enrich → Chunk →  │
    │ Dedup → TrustRank → Summarize → UI │
    └────────────────────────────────────┘
                       │
               MongoDB Atlas + Logs

### 3. Agentic Flow Options Considered

| Framework                            | Description                                        | Use-case fit                                 |
| ------------------------------------ | -------------------------------------------------- | -------------------------------------------- |
| ControlFlow (Prefect-style)          | Lightweight task/flow orchestration in pure Python | Clear DAG; fits deterministic pipelines      |
| LangChain + StreamlitCallbackHandler | Shows “thoughts” & tool usage in real time         | Great for summarization/RAG reasoning trace  |
| LangGraph                            | Graph-based flow with conditional branching        | Future extension for adaptive agent behavior |
| OpenAI Swarm / AutoGen               | Multi-agent collaboration framework                | Overhead for hackathon; good next step       |
| Custom FSM (Finite State Machine)    | Minimal bespoke controller (few hundred LOC)       | Fastest to implement for demo                |

We use Streamlit for visualization and either a ControlFlow or custom Python flow manager for execution.

### 4. Control Layer Reference Implementation

Below is a minimal skeleton showing how the orchestration layer can manage the pipeline steps and communicate with Streamlit.

```python
# orchestrator.py
from enum import Enum
import time

class Stage(str, Enum):
    INGEST = "ingest"
    CLEAN = "clean"
    ENRICH = "enrich"
    CHUNK = "chunk"
    DEDUP = "dedup"
    TRUST = "trust"
    SUMMARIZE = "summarize"

class AgentFlow:
    def __init__(self):
        self.state = {stage: "pending" for stage in Stage}
        self.logs = {stage: [] for stage in Stage}

    def run_stage(self, stage, func, *args, **kwargs):
        self.state[stage] = "running"
        start = time.time()
        try:
            result = func(*args, **kwargs)
            self.state[stage] = "done"
            self.logs[stage].append(f"✅ {stage} finished in {time.time()-start:.2f}s")
            return result
        except Exception as e:
            self.state[stage] = "error"
            self.logs[stage].append(f"❌ {stage} failed: {e}")
            raise

    def summary(self):
        return {s: self.state[s] for s in Stage}
```

Example integration of agents:

from agents import (
ingest_video,
clean_transcript,
enrich_transcript,
chunk_and_embed,
deduplicate,
rank_trust,
summarize_playlist
)

flow = AgentFlow()

# Example: full pipeline for one playlist

data = flow.run_stage(Stage.INGEST, ingest_video, playlist_id="PL_react_course_2024")
clean = flow.run_stage(Stage.CLEAN, clean_transcript, data)
enriched = flow.run_stage(Stage.ENRICH, enrich_transcript, clean)
chunks = flow.run_stage(Stage.CHUNK, chunk_and_embed, enriched)
deduped = flow.run_stage(Stage.DEDUP, deduplicate, chunks)
trusted = flow.run_stage(Stage.TRUST, rank_trust, deduped)
summary = flow.run_stage(Stage.SUMMARIZE, summarize_playlist, trusted)

### 5. Streamlit UI Integration

```python
# app.py
import streamlit as st
from orchestrator import flow, Stage

st.title("🎛️ Agentic Pipeline Controller")

col1, col2 = st.columns(2)
if col1.button("▶️ Run Full Pipeline"):
    with st.spinner("Running all stages..."):
        st.session_state['summary'] = flow.run_stage(Stage.INGEST, ingest_video, playlist_id="PL_react_course_2024")
        # ... run others in sequence
        st.success("Pipeline completed!")

if col2.button("🧹 Clean Transcript"):
    with st.spinner("Cleaning..."):
        result = flow.run_stage(Stage.CLEAN, clean_transcript, st.session_state['summary'])
        st.json(result[:1])  # preview

# Dashboard section
st.subheader("Pipeline Status")
st.table(flow.summary())

# Logs viewer
st.subheader("Logs")
for stage, logs in flow.logs.items():
    if logs:
        st.markdown(f"**{stage}**")
        st.code("\n".join(logs), language="bash")
```

You can extend this by:

Adding a checkbox per stage to enable/disable execution.

Displaying runtime metrics (e.g. via st.metric).

Using st.progress() bars for long-running tasks.

Showing intermediate artifacts (cleaned text, tags, embeddings) using tabs.

### 6. Real-Time Thought Visualization (Optional)

If you wrap certain stages (like summarization or retrieval) in LangChain, attach a StreamlitCallbackHandler to show intermediate reasoning steps:

from langchain.callbacks.streamlit import StreamlitCallbackHandler
from langchain.chat_models import ChatOpenAI

st_callback = StreamlitCallbackHandler(st.container())
llm = ChatOpenAI(streaming=True, callbacks=[st_callback])

response = llm.predict("Summarize how useState differs from useReducer in React.")
st.markdown(response)

This makes the agent’s decision path visible — great for demos.

### 7. Intermediate Data Visualization

You can add small dashboards for every pipeline stage:

Cleaning stats: #paragraphs, average words per paragraph.

Enrichment stats: #code blocks, top 10 tags, entity frequency (bar chart).

Chunk embedding view: UMAP 2D scatter (st.pyplot() / Plotly).

Deduplication heatmap: correlation between channels.

Trust ranking: histogram of trust scores.

Example:

import pandas as pd
import plotly.express as px

df = pd.DataFrame(trust_scores, columns=["trust_score"])
fig = px.histogram(df, x="trust_score", nbins=20, title="Trust Score Distribution")
st.plotly_chart(fig, use_container_width=True)

### 8. Future Integrations

| Future Feature                  | Description                                                                     |
| ------------------------------- | ------------------------------------------------------------------------------- |
| LangGraph visualization         | Draw the agent graph using streamlit-agraph or networkx; highlight running node |
| Prefect / ControlFlow dashboard | Connect Streamlit to Prefect or ControlFlow API to show live task statuses      |
| Async execution                 | Run stages concurrently and stream updates via WebSocket                        |
| Agent metrics                   | Track token usage, latency, and confidence per stage                            |
| Auto-parameter tuning           | Adjust chunk size, redundancy threshold from the UI                             |

### 9. Key Benefits of This Approach

✅ Transparent — every transformation visible
✅ Interactive — run, skip, or replay any stage
✅ Persistent — logs and intermediate data stored in MongoDB
✅ Adaptable — supports different orchestration backends
✅ Hackathon-friendly — visually appealing and easy to explain

### 10. References

LangChain StreamlitCallbackHandler Docs

ControlFlow AI
– lightweight task orchestration

Prefect.io
– open-source flow orchestration

LangGraph
– graph-based multi-agent orchestration

OpenAI Swarm Overview

✅ Summary

This Streamlit-controlled orchestration layer turns the agent pipeline into an interactive, inspectable system.
It demonstrates context engineering principles — capturing, transforming, and reusing knowledge with visibility at every step.
For the hackathon, it also makes your demo highly engaging: judges can literally watch the pipeline think as it processes educational videos.
