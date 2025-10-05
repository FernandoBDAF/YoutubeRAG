import os
from typing import Any, Dict, List
import streamlit as st
from dotenv import load_dotenv

from utils import get_mongo_client
from config.paths import DB_NAME
from rag import rag_answer


def init_state() -> None:
    if "initialized" not in st.session_state:
        st.session_state["initialized"] = True


def main() -> None:
    load_dotenv()
    init_state()

    st.set_page_config(page_title="Mongo Hack RAG", layout="wide")
    st.title("Mongo Hack — YouTube RAG (MVP)")

    client = get_mongo_client()
    db = client[DB_NAME]
    st.sidebar.success(f"Connected to DB: {db.name}")

    st.sidebar.header("Filters")
    topic = st.sidebar.text_input("Topic contains")
    channel = st.sidebar.text_input(
        "Channel ID (metadata.tags and channel not yet wired)"
    )
    max_age = st.sidebar.slider("Max age (days)", min_value=0, max_value=720, value=365)
    trust_min = st.sidebar.slider(
        "Min trust score", min_value=0.0, max_value=1.0, value=0.0, step=0.05
    )

    tab_qna, tab_compare, tab_unique, tab_summaries, tab_memory, tab_ctrl = st.tabs(
        ["Q&A", "Compare", "Unique Insights", "Summaries", "Memory", "Controller"]
    )

    with tab_qna:
        st.subheader("Ask a question")
        query = st.text_area(
            "Question", placeholder="e.g., Best practices for React state management"
        )
        k = st.slider("Top-k chunks", min_value=3, max_value=20, value=8)
        # Saved queries
        if "saved_queries" not in st.session_state:
            st.session_state["saved_queries"] = []
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save query", key="save_q") and query:
                st.session_state["saved_queries"].append(query)
        with col2:
            if st.session_state["saved_queries"]:
                pick = st.selectbox(
                    "Load saved query",
                    st.session_state["saved_queries"],
                    index=len(st.session_state["saved_queries"]) - 1,
                )
                if st.button("Load", key="load_q"):
                    query = pick
                    st.experimental_rerun()

        # Persist saved queries to DB
        st.markdown("---")
        st.caption("Saved queries (persistent)")
        db_save_col, db_load_col = st.columns(2)
        with db_save_col:
            qname = st.text_input("Name (optional)", key="save_name")
            if st.button("Save to DB", key="save_db") and query:
                try:
                    doc = {
                        "name": qname or query[:40],
                        "query": query,
                        "topic": topic,
                        "channel": channel,
                    }
                    db["saved_queries"].insert_one(doc)
                    st.success("Saved.")
                except Exception as e:
                    st.error(f"Save failed: {e}")
        with db_load_col:
            try:
                saved = list(
                    db["saved_queries"]
                    .find({}, {"name": 1, "query": 1})
                    .sort("_id", -1)
                    .limit(20)
                )
            except Exception:
                saved = []
            opts = {s.get("name") or s.get("query", ""): s for s in saved}
            if opts:
                sel = st.selectbox("Pick saved", list(opts.keys()), key="db_pick")
                if st.button("Load from DB", key="load_db"):
                    query = opts[sel].get("query", "")
                    st.experimental_rerun()

        # Quick presets when DB is empty
        if not saved:
            st.markdown("---")
            st.caption("Quick presets")
            presets = [
                "Summarize React state management best practices",
                "Compare unique insights on React forms across channels",
                "List non-redundant tips about React Router in 2024",
            ]
            preset_sel = st.selectbox("Choose preset", presets, key="preset_pick")
            if st.button("Load preset", key="load_preset"):
                query = preset_sel
                st.experimental_rerun()
        st.markdown("---")
        st.caption("Retrieval weighting")
        colw1, colw2, colw3 = st.columns(3)
        with colw1:
            w_vector = st.slider("Vector", 0.0, 1.0, 0.6, 0.05)
        with colw2:
            w_trust = st.slider("Trust", 0.0, 1.0, 0.25, 0.05)
        with colw3:
            w_recency = st.slider("Recency", 0.0, 1.0, 0.15, 0.05)

        if st.button("Search", key="qna_search"):
            with st.spinner("Retrieving..."):
                filters = {}
                if topic:
                    filters = {"metadata.tags": {"$regex": topic, "$options": "i"}}
                if channel:
                    # Combine filters when both are present
                    if filters:
                        filters = {
                            "$and": [
                                filters,
                                {
                                    "metadata.channel_id": {
                                        "$regex": channel,
                                        "$options": "i",
                                    }
                                },
                            ]
                        }
                    else:
                        filters = {
                            "metadata.channel_id": {"$regex": channel, "$options": "i"}
                        }
                # Apply age filter
                if max_age < 720:
                    age_filter = {"metadata.age_days": {"$lte": max_age}}
                    filters = {"$and": [filters, age_filter]} if filters else age_filter
                # Apply trust filter
                if trust_min > 0.0:
                    trust_filter = {"trust_score": {"$gte": trust_min}}
                    filters = (
                        {"$and": [filters, trust_filter]} if filters else trust_filter
                    )
                result = rag_answer(
                    query,
                    k=k,
                    filters=filters,
                    weights={
                        "vector": w_vector,
                        "trust": w_trust,
                        "recency": w_recency,
                    },
                )
            st.subheader("Answer")
            st.write(result.get("answer", ""))
            md = result.get("answer", "") or ""
            st.download_button(
                "Download answer as Markdown",
                data=md,
                file_name="answer.md",
                mime="text/markdown",
            )
            st.subheader("Citations")
            citations = [
                f"{h.get('video_id')}:{h.get('chunk_id')} (score={h.get('score'):.3f})"
                for h in result.get("hits", [])[:k]
            ]
            for line in citations:
                st.write(f"- {line}")
            cite_text = "\n".join(citations)
            st.text_area("Copy citations", cite_text, height=120)
            st.download_button(
                "Download citations",
                data=cite_text,
                file_name="citations.txt",
                mime="text/plain",
            )
            st.subheader("Retrieved Chunks")
            for h in result.get("hits", [])[:k]:
                with st.expander(
                    f"{h.get('video_id')}:{h.get('chunk_id')} (score={h.get('score'):.3f})"
                ):
                    st.write(h.get("text", "")[:1500])

    with tab_compare:
        st.subheader("Compare Channels (beta)")
        ch_a = st.text_input("Channel A (channel_id)", key="cmp_a")
        ch_b = st.text_input("Channel B (channel_id)", key="cmp_b")
        if st.button("Load comparisons", key="cmp_btn"):
            client = get_mongo_client()
            coll = client[DB_NAME]["video_chunks"]
            filt_a: Dict[str, Any] = {"metadata.channel_id": ch_a} if ch_a else {}
            filt_b: Dict[str, Any] = {"metadata.channel_id": ch_b} if ch_b else {}
            a_rows = list(
                coll.find(filt_a, {"chunk_id": 1, "text": 1, "metadata": 1}).limit(10)
            )
            b_rows = list(
                coll.find(filt_b, {"chunk_id": 1, "text": 1, "metadata": 1}).limit(10)
            )
            # basic tag consensus/unique metrics
            tags_a = set(
                t for r in a_rows for t in r.get("metadata", {}).get("tags", [])
            )
            tags_b = set(
                t for r in b_rows for t in r.get("metadata", {}).get("tags", [])
            )
            consensus = sorted(tags_a.intersection(tags_b))
            unique_a = sorted(tags_a - tags_b)
            unique_b = sorted(tags_b - tags_a)
            st.write("Consensus tags:", ", ".join(consensus) or "—")
            st.write("Unique A tags:", ", ".join(unique_a) or "—")
            st.write("Unique B tags:", ", ".join(unique_b) or "—")
            # Export as CSV/Markdown
            import io, csv

            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["Category", "Tags"])
            writer.writerow(["Consensus", ";".join(consensus)])
            writer.writerow(["Unique_A", ";".join(unique_a)])
            writer.writerow(["Unique_B", ";".join(unique_b)])
            csv_bytes = output.getvalue().encode("utf-8")
            st.download_button(
                "Download compare metrics (CSV)",
                csv_bytes,
                file_name="compare_metrics.csv",
                mime="text/csv",
            )
            md = "\n".join(
                [
                    "# Compare Metrics",
                    f"- Consensus: {', '.join(consensus) or '—'}",
                    f"- Unique A: {', '.join(unique_a) or '—'}",
                    f"- Unique B: {', '.join(unique_b) or '—'}",
                ]
            )
            st.download_button(
                "Download compare metrics (Markdown)",
                md,
                file_name="compare_metrics.md",
                mime="text/markdown",
            )
            st.write("Channel A chunks:")
            for r in a_rows:
                st.write(
                    f"- {r.get('chunk_id')} | tags={r.get('metadata',{}).get('tags', [])}"
                )
            st.write("Channel B chunks:")
            for r in b_rows:
                st.write(
                    f"- {r.get('chunk_id')} | tags={r.get('metadata',{}).get('tags', [])}"
                )

    with tab_unique:
        st.subheader("Unique Insights (beta)")
        st.write("Filter out redundant chunks (is_redundant=false)")
        if st.button("List unique snippets", key="uniq_btn"):
            client = get_mongo_client()
            coll = client[DB_NAME]["video_chunks"]
            query_filter = {"is_redundant": {"$ne": True}}
            if topic:
                query_filter["metadata.tags"] = {"$regex": topic, "$options": "i"}
            if max_age < 720:
                query_filter["metadata.age_days"] = {"$lte": max_age}
            if trust_min > 0.0:
                query_filter["trust_score"] = {"$gte": trust_min}
            rows = list(
                coll.find(
                    query_filter,
                    {"video_id": 1, "chunk_id": 1, "text": 1, "metadata": 1},
                ).limit(20)
            )
            for r in rows:
                with st.expander(f"{r.get('video_id')}:{r.get('chunk_id')}"):
                    st.write(r.get("text", "")[:1200])

    with tab_summaries:
        st.subheader("Summaries (topic-based)")
        topic_sum = st.text_input("Topic regex", value=topic or "react|state")
        use_llm_sum = st.checkbox("Use LLM for summary", value=True, key="sum_llm")
        if st.button("Build context", key="sum_btn"):
            from summarizer import summarize_topic

            out = summarize_topic(topic_sum)
            st.write(f"Chunks included: {out.get('count')}")
            context_val = out.get("context", "")
            st.text_area("Context", context_val, height=300)
            if st.button("Generate Markdown summary", key="sum_gen"):
                try:
                    # Fetch blocks again for IDs
                    client = get_mongo_client()
                    coll = client[DB_NAME]["video_chunks"]
                    rows = list(
                        coll.find(
                            {"metadata.tags": {"$regex": topic_sum, "$options": "i"}},
                            {"video_id": 1, "chunk_id": 1, "text": 1},
                        ).limit(12)
                    )
                    if use_llm_sum:
                        from agents.summarizer_agent import SummarizerAgent

                        agent = SummarizerAgent()
                        md = agent.summarize(rows, topic_sum)
                    else:
                        # fallback: reuse plain context
                        md = f"# Summary (no LLM)\n\n{context_val[:4000]}"
                    st.text_area("Summary (Markdown)", md, height=300)
                    st.download_button(
                        "Download summary.md",
                        data=md,
                        file_name="summary.md",
                        mime="text/markdown",
                    )
                except Exception as e:
                    st.error(f"Summary generation failed: {e}")
            if st.button("Save summary", key="sum_save"):
                from summarizer import save_summary

                sid = save_summary(topic_sum, context_val)
                st.success(f"Saved summary with id: {sid}")

    with tab_memory:
        st.subheader("Recent Memory Logs")
        client = get_mongo_client()
        logs = client[DB_NAME]["memory_logs"]
        rows = list(
            logs.find({}, {"query": 1, "retrieved": 1, "answer": 1})
            .sort("_id", -1)
            .limit(20)
        )
        for i, r in enumerate(rows, start=1):
            with st.expander(f"{i}. {r.get('query','')[:80]}"):
                st.write(r.get("answer", "")[:1000])
                st.write("Citations:")
                for cite in r.get("retrieved", [])[:10]:
                    st.write(
                        f"- {cite.get('video_id')}:{cite.get('chunk_id')} (score={cite.get('score')})"
                    )

    with tab_ctrl:
        st.subheader("Pipeline Controller (per ORCHESTRACTION-INTERFACE.md)")
        py = os.sys.executable
        # Inputs
        with st.expander("Inputs"):
            playlist_id = st.text_input("Playlist ID", key="ctrl_playlist")
            channel_id = st.text_input("Channel ID", key="ctrl_channel")
            video_ids_str = st.text_input(
                "Video IDs (space-separated)", key="ctrl_vids"
            )
            use_llm = st.checkbox(
                "Use LLM for stages (clean/enrich/chunk/redundancy/trust)",
                value=True,
                key="ctrl_llm",
            )
            max_items = st.number_input(
                "Max items", min_value=1, max_value=50, value=5, step=1, key="ctrl_max"
            )

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            if st.button("Run Ingest", key="ctrl_ingest"):
                st.toast("Launching ingest...", icon="▶️")
                args = []
                if playlist_id:
                    args = ["--playlist_id", playlist_id, "--max", str(max_items)]
                elif channel_id:
                    args = ["--channel_id", channel_id, "--max", str(max_items)]
                elif video_ids_str.strip():
                    args = ["--video_ids", *video_ids_str.strip().split()]
                os.system(f"{py} Mongo_Hack/main.py ingest {' '.join(args)}")
            if st.button("Run Enrich (LLM)", key="ctrl_enrich_llm"):
                st.toast("Launching enrich with LLM...", icon="🧠")
                flag = " --llm" if use_llm else ""
                os.system(f"{py} Mongo_Hack/main.py enrich{flag}")
        with col_b:
            if st.button("Run Clean (LLM)", key="ctrl_clean_llm"):
                st.toast("Launching clean with LLM...", icon="🧼")
                flag = " --llm" if use_llm else ""
                os.system(f"{py} Mongo_Hack/main.py clean{flag}")
            if st.button("Run Chunk (LLM)", key="ctrl_chunk_llm"):
                st.toast("Launching chunk with LLM...", icon="🧩")
                flag = " --llm" if use_llm else ""
                os.system(f"{py} Mongo_Hack/main.py chunk{flag}")
        with col_c:
            if st.button("Run Redundancy (LLM)", key="ctrl_red_llm"):
                st.toast("Launching redundancy with LLM...", icon="🔁")
                flag = " --llm" if use_llm else ""
                os.system(f"{py} Mongo_Hack/main.py redundancy{flag}")
            if st.button("Run Trust (LLM)", key="ctrl_trust_llm"):
                st.toast("Launching trust with LLM...", icon="🛡️")
                flag = " --llm" if use_llm else ""
                os.system(f"{py} Mongo_Hack/main.py trust{flag}")
        st.divider()
        if st.button("Run Full Pipeline (LLM on Clean/Enrich/Chunk)", key="ctrl_pipe"):
            st.toast("Launching full pipeline...", icon="🚀")
            flag = " --llm" if use_llm else ""
            args = []
            if playlist_id:
                args = ["--playlist_id", playlist_id, "--max", str(max_items)]
            elif channel_id:
                args = ["--channel_id", channel_id, "--max", str(max_items)]
            elif video_ids_str.strip():
                args = ["--video_ids", *video_ids_str.strip().split()]
            os.system(f"{py} Mongo_Hack/main.py pipeline {' '.join(args)}{flag}")


if __name__ == "__main__":
    main()
