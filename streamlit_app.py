import os
from typing import Any, Dict, List
import streamlit as st
from dotenv import load_dotenv

from app.services.utils import get_mongo_client
from app.services.filters import build_filters
from app.services.ui_utils import rows_from_hits, render_table_and_csv
from app.services import (
    upsert_video_feedback,
    upsert_chunk_feedback,
    get_video_feedback_for_session,
    get_chunk_feedback_for_session,
    aggregate_video_feedback,
    aggregate_chunk_feedback,
)
from uuid import uuid4
from config.paths import DB_NAME
from app.services.rag import rag_answer


def init_state() -> None:
    if "initialized" not in st.session_state:
        st.session_state["initialized"] = True
    if "session_id" not in st.session_state:
        sid = os.getenv("SESSION_ID") or str(uuid4())
        st.session_state["session_id"] = sid


def main() -> None:
    load_dotenv()
    init_state()

    st.set_page_config(page_title="Mongo Hack RAG", layout="wide")
    st.title("Mongo Hack — YouTube RAG (MVP)")

    client = get_mongo_client()
    db = client[DB_NAME]
    st.sidebar.success(f"Connected to DB: {db.name}")
    # Top KPIs
    k1, k2, k3, k4, k5 = st.columns(5)
    try:
        with k1:
            st.metric("raw_videos", db["raw_videos"].count_documents({}))
        with k2:
            st.metric("video_chunks", db["video_chunks"].count_documents({}))
        with k3:
            st.metric(
                "cleaned_transcripts", db["cleaned_transcripts"].count_documents({})
            )
        with k4:
            st.metric("video_feedback", db["video_feedback"].count_documents({}))
        with k5:
            st.metric("chunk_feedback", db["chunk_feedback"].count_documents({}))
    except Exception:
        st.caption("Metrics unavailable (no permissions or collections missing)")
    if st.button("Refresh metrics", key="refresh_metrics"):
        st.experimental_rerun()

    # Quick Profile selector (promoted)
    st.sidebar.header("Profile")
    try:
        from app.services.profiles import list_profiles

        profs_sb = list_profiles()
        name_to_sid_sb = {
            (p.get("name") or p.get("session_id") or ""): p.get("session_id")
            for p in profs_sb
        }
        if name_to_sid_sb:
            pick_prof_sb = st.sidebar.selectbox(
                "Load profile", list(name_to_sid_sb.keys()), key="prof_pick_sb"
            )
            if st.sidebar.button("Load", key="prof_load_sb"):
                sid = name_to_sid_sb.get(pick_prof_sb)
                if sid:
                    st.session_state["session_id"] = sid
                    st.sidebar.success(f"Loaded: {pick_prof_sb}")
        if st.sidebar.button("New session profile", key="prof_new_sb"):
            from uuid import uuid4

            st.session_state["session_id"] = str(uuid4())
            st.sidebar.success("New session created")
        # Quick save preset
        try:
            from app.services.profiles import upsert_profile

            quick_name = st.sidebar.text_input(
                "Profile name (save)", key="prof_name_sb"
            )
            if st.sidebar.button("Save preset", key="prof_save_sb"):
                sid = st.session_state.get("session_id")
                persona = st.session_state.get("persona")
                prof = {
                    "name": quick_name or sid,
                    "persona": persona,
                    "defaults": {
                        "topic": st.session_state.get("default_topic"),
                        "channel": st.session_state.get("default_channel"),
                    },
                }
                if sid:
                    upsert_profile(sid, prof)
                    st.sidebar.success("Preset saved")
        except Exception:
            pass
        # Persona summary
        persona = st.session_state.get("persona") or {}
        if persona:
            w = persona.get("weights") or {}
            st.sidebar.caption(
                f"Persona: {persona.get('name','Custom')} | W: v={w.get('vector','—')}, t={w.get('trust','—')}, r={w.get('recency','—')}"
            )
    except Exception:
        pass

    st.sidebar.header("Filters")
    topic = st.sidebar.text_input(
        "Topic contains", value=st.session_state.get("default_topic", "")
    )
    channel = st.sidebar.text_input(
        "Channel ID (metadata.tags and channel not yet wired)",
        value=st.session_state.get("default_channel", ""),
    )
    max_age = st.sidebar.slider("Max age (days)", min_value=0, max_value=720, value=365)
    trust_min = st.sidebar.slider(
        "Min trust score", min_value=0.0, max_value=1.0, value=0.0, step=0.05
    )

    (
        tab_qna,
        tab_vector,
        tab_hybrid,
        tab_explore,
        tab_compare,
        tab_unique,
        tab_summaries,
        tab_memory,
        tab_ctrl,
    ) = st.tabs(
        [
            "Q&A",
            "Vector Search",
            "Hybrid Search",
            "Explore",
            "Compare",
            "Unique Insights",
            "Summaries",
            "Memory",
            "Controller",
        ]
    )

    with tab_qna:
        st.subheader("Ask a question")
        st.caption(
            "Q&A retrieves top chunks and generates an answer. Use the sliders to balance vector/trust/recency and toggles for streaming/hybrid/reweight."
        )
        with st.expander("Session", expanded=False):
            st.code(st.session_state.get("session_id", ""))
            if st.button("New session", key="new_sess"):
                st.session_state["session_id"] = str(uuid4())
                st.success("New session created")
                st.experimental_rerun()
            # Personalization helpers
            st.caption("Recent queries (this session)")
            if "recent_q" not in st.session_state:
                st.session_state["recent_q"] = []
            if st.session_state.get("recent_q"):
                pick_r = st.selectbox(
                    "Pick recent", st.session_state["recent_q"][-10:], key="pick_recent"
                )
                if st.button("Load recent", key="load_recent"):
                    query = pick_r
                    st.experimental_rerun()
        # Your feedback so far (session summary)
        with st.expander("Your feedback so far", expanded=False):
            try:
                sess = st.session_state.get("session_id")
                if sess:
                    vfb = list(
                        db["video_feedback"]
                        .find({"session_id": sess}, {"rating": 1, "tags": 1})
                        .limit(200)
                    )
                    cfb = list(
                        db["chunk_feedback"]
                        .find({"session_id": sess}, {"rating": 1, "tags": 1})
                        .limit(200)
                    )

                    def _agg(rows):
                        if not rows:
                            return {"count": 0, "avg": None, "top_tags": []}
                        cnt = len(rows)
                        avg = sum(int(r.get("rating", 0) or 0) for r in rows) / cnt
                        tags: Dict[str, int] = {}
                        for r in rows:
                            for t in r.get("tags", []) or []:
                                tags[t] = tags.get(t, 0) + 1
                        top = sorted(tags.items(), key=lambda x: x[1], reverse=True)[:5]
                        return {"count": cnt, "avg": round(avg, 2), "top_tags": top}

                    vagg = _agg(vfb)
                    cagg = _agg(cfb)
                    st.write(
                        f"Video feedback — count: {vagg['count']} | avg: {vagg['avg'] or '—'} | top tags: "
                        + ", ".join([t for t, _ in vagg["top_tags"]])
                    )
                    st.write(
                        f"Chunk feedback — count: {cagg['count']} | avg: {cagg['avg'] or '—'} | top tags: "
                        + ", ".join([t for t, _ in cagg["top_tags"]])
                    )
                else:
                    st.caption("No session id")
            except Exception as e:
                st.caption(f"Feedback summary unavailable: {e}")
        # Restore last defaults (topic/channel) if present
        default_topic = st.session_state.get("default_topic", "")
        default_channel = st.session_state.get("default_channel", "")
        with st.columns([4, 1])[0]:
            query = st.text_area(
                "Question",
                placeholder="e.g., Best practices for React state management",
                help="Enter your question. Retrieval will fetch top chunks; the LLM will answer using only the retrieved context.",
            )
        k = st.slider(
            "Top-k chunks",
            min_value=3,
            max_value=20,
            value=8,
            help="How many chunks to retrieve before answering.",
        )
        use_hybrid_qna = st.checkbox(
            "Use Hybrid Retrieval for Q&A", value=False, key="qna_hybrid"
        )
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

        # Shortcuts (optional)
        with st.expander("Shortcuts (optional)", expanded=False):
            st.caption(
                "Quick presets & popular topics are optional helpers; no defaults are enforced."
            )
            presets = [
                "Summarize React state management best practices",
                "Compare unique insights on React forms across channels",
                "List non-redundant tips about React Router in 2024",
            ]
            preset_sel = st.selectbox("Choose preset", presets, key="preset_pick")
            if st.button("Load preset", key="load_preset"):
                query = preset_sel
                st.experimental_rerun()
        # Popular topics quick filter
        st.markdown("---")
        st.caption("Popular Topics")
        popular = st.multiselect(
            "Select topics (adds regex filter)",
            [
                "react",
                "hooks",
                "state",
                "router",
                "typescript",
                "python",
                "api",
            ],
            default=[],
            key="qna_topics",
        )
        st.markdown("---")
        st.caption("Retrieval weighting")
        colw1, colw2, colw3 = st.columns(3)
        with colw1:
            w_vector = st.slider(
                "Vector", 0.0, 1.0, 0.6, 0.05, help="Semantic similarity contribution."
            )
        with colw2:
            w_trust = st.slider(
                "Trust",
                0.0,
                1.0,
                0.25,
                0.05,
                help="Trust score contribution (heuristics/LLM-assisted).",
            )
        with colw3:
            w_recency = st.slider(
                "Recency", 0.0, 1.0, 0.15, 0.05, help="Favors newer content."
            )
        feedback_alpha = st.slider("Feedback weight (alpha)", 0.0, 1.0, 0.2, 0.05)
        st.caption(
            "Note: feedback weight is previewed in UI; retrieval currently uses vector/trust/recency weights."
        )
        reweight = st.checkbox(
            "Reweight by persona/feedback",
            value=False,
            key="qna_reweight",
            help="Bias results toward persona interests, current topic, and your top feedback tags.",
        )
        re_alpha = (
            st.slider("Reweight alpha", 0.0, 0.5, 0.15, 0.05, key="qna_reweight_alpha")
            if reweight
            else 0.0
        )

        colstream, colexcl = st.columns([1, 1])
        with colstream:
            stream_ans = st.checkbox(
                "Stream LLM answer",
                value=(
                    os.getenv("LLM_STREAMING", "false").lower() in ("1", "true", "yes")
                ),
                key="qna_stream",
            )
        with colexcl:
            exclude_red = st.checkbox(
                "Exclude redundant chunks", value=True, key="qna_excl_red"
            )
        if st.button("Search", key="qna_search"):
            with st.spinner("Retrieving..."):
                # Build filters via shared builder
                tag_regex = topic or ""
                if popular:
                    tag_regex = (tag_regex + "|" + "|".join(popular)).strip("|")
                filters = build_filters(
                    topic=tag_regex,
                    channel=channel,
                    max_age=max_age if max_age < 720 else None,
                    trust_min=trust_min if trust_min > 0.0 else None,
                    exclude_redundant=bool(exclude_red),
                )
                from app.services.rag import rag_hybrid_answer

                result = (rag_hybrid_answer if bool(use_hybrid_qna) else rag_answer)(
                    query,
                    k=k,
                    filters=filters,
                    weights={
                        "vector": w_vector,
                        "trust": w_trust,
                        "recency": w_recency,
                    },
                    streaming=bool(stream_ans),
                    session_id=st.session_state.get("session_id"),
                )
                # Optional reweighting by persona/feedback-driven tags
                if reweight and result and result.get("hits"):
                    try:
                        sess = st.session_state.get("session_id")
                        # gather top feedback tags for this session
                        tag_counts: Dict[str, int] = {}
                        for r in (
                            db["video_feedback"]
                            .find({"session_id": sess}, {"tags": 1})
                            .limit(200)
                        ):
                            for t in r.get("tags", []) or []:
                                t2 = (t or "").strip().lower().replace("_", "-")
                                if t2:
                                    tag_counts[t2] = tag_counts.get(t2, 0) + 1
                        top_fb = [
                            t
                            for t, _ in sorted(
                                tag_counts.items(), key=lambda x: x[1], reverse=True
                            )[:5]
                        ]
                        # persona interests and current topic as tags
                        persona = st.session_state.get("persona", {}) or {}
                        p_interests = [
                            (s or "").strip().lower().replace("_", "-")
                            for s in (persona.get("interests") or [])
                        ]
                        topic_tags = [(topic or "").strip().lower().replace("_", "-")]
                        interest_set = {
                            t for t in (top_fb + p_interests + topic_tags) if t
                        }
                        prefer_code = bool(
                            (persona.get("bias") or {}).get("code_present")
                        )
                        # compute adjusted scores
                        hits = result.get("hits", [])
                        adj = []
                        for h in hits:
                            meta = h.get("metadata", {}) or {}
                            tags = [
                                (t or "").strip().lower().replace("_", "-")
                                for t in (meta.get("tags") or [])
                            ]
                            overlap = len(interest_set.intersection(set(tags)))
                            base = float(h.get("final_score", 0.0) or 0.0) or float(
                                h.get("score", 0.0) or 0.0
                            )
                            factor = 1.0 + float(re_alpha or 0.0) * float(
                                min(overlap, 3)
                            )
                            if prefer_code and bool(meta.get("code_present")):
                                factor += 0.1
                            adjusted = base * factor
                            h["score"] = adjusted
                            adj.append(h)
                        result["hits"] = sorted(
                            adj, key=lambda x: x.get("score", 0.0), reverse=True
                        )
                    except Exception as e:
                        st.caption(f"Reweight skipped: {e}")
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
            # Track recent query in session
            try:
                if query:
                    rq = st.session_state.get("recent_q", [])
                    rq.append(query)
                    st.session_state["recent_q"] = rq[-20:]
                # Save latest defaults
                if topic:
                    st.session_state["default_topic"] = topic
                if channel:
                    st.session_state["default_channel"] = channel
            except Exception:
                pass
            # Video-level feedback for first cited video
            if result.get("hits"):
                first = result["hits"][0]
                v_id = first.get("video_id")
                if v_id:
                    with st.expander(f"Video feedback for {v_id}", expanded=False):
                        vagg = aggregate_video_feedback(db, v_id)
                        st.caption(
                            f"Avg rating: {vagg.get('avg_rating') or '—'} | Count: {vagg.get('count')} | Top tags: "
                            + ", ".join([t for t, _ in vagg.get("top_tags", [])])
                        )
                        sess = st.session_state.get("session_id")
                        vprev = (
                            get_video_feedback_for_session(db, sess, v_id)
                            if sess
                            else None
                        )
                        v_r_def = int(vprev.get("rating", 3)) if vprev else 3
                        v_rating = st.slider(
                            "Your rating", 1, 5, v_r_def, key=f"vrate_{v_id}"
                        )
                        v_tag_suggest = [t for t, _ in vagg.get("top_tags", [])]
                        v_tags_sel = st.multiselect(
                            "Tags",
                            v_tag_suggest,
                            default=vprev.get("tags", []) if vprev else [],
                            key=f"vtags_{v_id}",
                        )
                        v_add_tags = st.text_input(
                            "Add tags (comma-separated)", key=f"vaddtags_{v_id}"
                        )
                        v_note = st.text_area(
                            "Optional note",
                            value=vprev.get("note", "") if vprev else "",
                            key=f"vnote_{v_id}",
                        )
                        if st.button("Save video feedback", key=f"vsave_{v_id}"):
                            extra_tags = [
                                s.strip()
                                for s in (v_add_tags or "").split(",")
                                if s.strip()
                            ]
                            all_tags = list({*v_tags_sel, *extra_tags})
                            try:
                                upsert_video_feedback(
                                    db, sess, v_id, v_rating, all_tags, v_note
                                )
                                st.success("Saved video feedback")
                            except Exception as e:
                                st.error(f"Save failed: {e}")

            st.subheader("Retrieved Chunks")
            for h in result.get("hits", [])[:k]:
                with st.expander(
                    f"{h.get('video_id')}:{h.get('chunk_id')} (score={h.get('score'):.3f})"
                ):
                    st.write(h.get("text", "")[:1500])
                    # Chunk feedback UI
                    chunk_id = h.get("chunk_id")
                    video_id = h.get("video_id")
                    if chunk_id and video_id:
                        agg = aggregate_chunk_feedback(db, chunk_id)
                        st.caption(
                            f"Avg rating: {agg.get('avg_rating') or '—'} | Count: {agg.get('count')} | Top tags: "
                            + ", ".join([t for t, _ in agg.get("top_tags", [])])
                        )
                        sess = st.session_state.get("session_id")
                        prev = (
                            get_chunk_feedback_for_session(db, sess, chunk_id)
                            if sess
                            else None
                        )
                        r_def = int(prev.get("rating", 3)) if prev else 3
                        rating = st.slider(
                            "Your rating", 1, 5, r_def, key=f"rate_{chunk_id}"
                        )
                        tag_suggest = [t for t, _ in agg.get("top_tags", [])]
                        tags_sel = st.multiselect(
                            "Tags",
                            tag_suggest,
                            default=prev.get("tags", []) if prev else [],
                            key=f"tags_{chunk_id}",
                        )
                        add_tags = st.text_input(
                            "Add tags (comma-separated)", key=f"addtags_{chunk_id}"
                        )
                        note = st.text_area(
                            "Optional note",
                            value=prev.get("note", "") if prev else "",
                            key=f"note_{chunk_id}",
                        )
                        if st.button("Save feedback", key=f"save_{chunk_id}"):
                            extra_tags = [
                                s.strip()
                                for s in (add_tags or "").split(",")
                                if s.strip()
                            ]
                            all_tags = list({*tags_sel, *extra_tags})
                            try:
                                upsert_chunk_feedback(
                                    db, sess, chunk_id, video_id, rating, all_tags, note
                                )
                                st.success("Saved chunk feedback")
                            except Exception as e:
                                st.error(f"Save failed: {e}")
            # Full retrieval context (for copy/download)
            full_ctx = "\n\n".join(
                [
                    f"({h.get('video_id')}:{h.get('chunk_id')})\n{h.get('text','')[:2000]}"
                    for h in result.get("hits", [])[:k]
                ]
            )
            st.subheader("Full Retrieval Context")
            st.text_area("Context", full_ctx, height=240)
            st.download_button(
                "Download context",
                data=full_ctx,
                file_name="retrieval_context.txt",
                mime="text/plain",
            )

    with tab_vector:
        st.subheader("Vector Search (semantic only)")
        from app.services.rag import embed_query, vector_search

        q_vs = st.text_input("Semantic query", key="vs_query")
        k_vs = st.slider("Top-k", min_value=3, max_value=30, value=10, key="vs_k")
        st.caption("Use the same filters from the sidebar")
        if st.button("Run vector search", key="vs_btn") and q_vs.strip():
            with st.spinner("Searching..."):
                try:
                    qvec = embed_query(q_vs)
                    # Build filters via shared helper
                    exclude_red_vs = st.checkbox(
                        "Exclude redundant", value=True, key="vs_excl"
                    )
                    tag_regex_list = st.session_state.get("qna_topics", [])
                    tag_regex_str = "|".join(tag_regex_list) if tag_regex_list else ""
                    rgx = (
                        topic + ("|" + tag_regex_str if tag_regex_str else "")
                    ).strip("|")
                    filters_vs = build_filters(
                        topic=rgx,
                        channel=channel,
                        max_age=max_age if max_age < 720 else None,
                        trust_min=trust_min if trust_min > 0.0 else None,
                        exclude_redundant=bool(exclude_red_vs),
                    )
                    hits = vector_search(
                        db["video_chunks"], qvec, k=k_vs, filters=filters_vs
                    )
                except Exception as e:
                    hits = []
                    st.error(f"Vector search failed: {e}")
            if hits:
                st.caption(f"Found {len(hits)} hits")
                for h in hits:
                    with st.expander(
                        f"{h.get('video_id')}:{h.get('chunk_id')} (score={h.get('score'):.3f})"
                    ):
                        st.write(h.get("text", "")[:1500])
            else:
                st.info("No results.")

    with tab_hybrid:
        st.subheader("Hybrid Search (keyword + vector)")
        from app.services.rag import embed_query
        from app.services.retrieval import hybrid_search

        q_h = st.text_input("Query", key="hy_query")
        k_h = st.slider(
            "Top-k",
            min_value=3,
            max_value=30,
            value=int(os.getenv("TOP_K", "10")),
            key="hy_k",
        )
        st.caption("Uses sidebar filters; shows search_score")
        if st.button("Run hybrid search", key="hy_btn") and q_h.strip():
            with st.spinner("Searching..."):
                try:
                    qvec_h = embed_query(q_h)
                    # Build filters same as vector tab
                    filters_h: Dict[str, Any] = {}
                    tag_regex = st.session_state.get("qna_topics", [])
                    tag_regex_str = "|".join(tag_regex) if tag_regex else ""
                    if topic or tag_regex_str:
                        rgx = topic + ("|" + tag_regex_str if tag_regex_str else "")
                        rgx = rgx.strip("|")
                        if rgx:
                            filters_h = {
                                "metadata.tags": {"$regex": rgx, "$options": "i"}
                            }
                    if channel:
                        if filters_h:
                            filters_h = {
                                "$and": [
                                    filters_h,
                                    {
                                        "metadata.channel_id": {
                                            "$regex": channel,
                                            "$options": "i",
                                        }
                                    },
                                ]
                            }
                        else:
                            filters_h = {
                                "metadata.channel_id": {
                                    "$regex": channel,
                                    "$options": "i",
                                }
                            }
                    if max_age < 720:
                        age_filter = {"metadata.age_days": {"$lte": max_age}}
                        filters_h = (
                            {"$and": [filters_h, age_filter]}
                            if filters_h
                            else age_filter
                        )
                    if trust_min > 0.0:
                        trust_filter = {"trust_score": {"$gte": trust_min}}
                        filters_h = (
                            {"$and": [filters_h, trust_filter]}
                            if filters_h
                            else trust_filter
                        )
                    exclude_red_h = st.checkbox(
                        "Exclude redundant", value=True, key="hy_excl"
                    )
                    if exclude_red_h:
                        red_filter = {"is_redundant": {"$ne": True}}
                        filters_h = (
                            {"$and": [filters_h, red_filter]}
                            if filters_h
                            else red_filter
                        )
                    hits_h = hybrid_search(
                        db["video_chunks"], q_h, qvec_h, top_k=k_h, filters=filters_h
                    )
                except Exception as e:
                    hits_h = []
                    st.error(f"Hybrid search failed: {e}")

            if hits_h:
                st.caption(f"Found {len(hits_h)} hits")
                # Table + CSV export
                try:
                    import pandas as pd

                    rows = [
                        {
                            "video_id": h.get("video_id"),
                            "chunk_id": h.get("chunk_id"),
                            "search_score": h.get("search_score"),
                            "keyword_score": h.get("keyword_score"),
                            "vector_score": h.get("vector_score"),
                            "trust": h.get("trust_score"),
                            "tags": ", ".join(
                                (h.get("metadata", {}) or {}).get("tags", [])[:6]
                            ),
                            "text": (h.get("text", "") or "")[:160],
                        }
                        for h in hits_h
                    ]
                    dfh = pd.DataFrame(rows)
                    st.dataframe(dfh, use_container_width=True)
                    st.download_button(
                        "Download hybrid results (CSV)",
                        dfh.to_csv(index=False).encode("utf-8"),
                        file_name="hybrid_results.csv",
                        mime="text/csv",
                    )
                except Exception as e:
                    st.caption(f"Tabular view unavailable: {e}")
                for h in hits_h:
                    sscore = h.get("search_score")
                    with st.expander(
                        f"{h.get('video_id')}:{h.get('chunk_id')} (search={sscore:.3f})"
                    ):
                        st.write(h.get("text", "")[:1500])
            else:
                st.info("No results.")

    # Retrieval Lab (new tab)
    (tab_lab,) = st.tabs(["Retrieval Lab"])
    with tab_lab:
        st.subheader("Retrieval Lab — Compare Modes")
        from app.services.retrieval import keyword_search, structured_search

        q_lab = st.text_input("Query", key="lab_q", value="react hooks")
        k_lab = st.slider("Top-k", 3, 30, 10, key="lab_k")
        st.caption(
            "Runs keyword-only, vector-only, hybrid, and structured queries side-by-side."
        )
        if st.button("Run Lab", key="lab_run") and q_lab.strip():
            with st.spinner("Running modes..."):
                try:
                    qvec = embed_query(q_lab)
                    # Reuse sidebar filters
                    filters_lab = {}
                    if topic:
                        filters_lab = {
                            "metadata.tags": {"$regex": topic, "$options": "i"}
                        }
                    if channel:
                        filters_lab = (
                            {
                                "$and": [
                                    filters_lab,
                                    {
                                        "metadata.channel_id": {
                                            "$regex": channel,
                                            "$options": "i",
                                        }
                                    },
                                ]
                            }
                            if filters_lab
                            else {
                                "metadata.channel_id": {
                                    "$regex": channel,
                                    "$options": "i",
                                }
                            }
                        )
                    kw = keyword_search(
                        db[DB_NAME]["video_chunks"],
                        q_lab,
                        top_k=k_lab,
                        filters=filters_lab,
                    )
                    from app.services.rag import vector_search as _vs

                    vec = _vs(
                        db[DB_NAME]["video_chunks"], qvec, k=k_lab, filters=filters_lab
                    )
                    hyb = hybrid_search(
                        db["video_chunks"],
                        q_lab,
                        qvec,
                        top_k=k_lab,
                        filters=filters_lab,
                    )
                    structured = structured_search(
                        db[DB_NAME]["video_chunks"],
                        filters=filters_lab,
                        sort_by={"trust_score": -1},
                        top_k=k_lab,
                    )
                except Exception as e:
                    kw, vec, hyb, structured = [], [], [], []
                    st.error(f"Lab run failed: {e}")
            cols = st.columns(4)
            for col, (name, rows) in zip(
                cols,
                [
                    ("Keyword", kw),
                    ("Vector", vec),
                    ("Hybrid", hyb),
                    ("Structured", structured),
                ],
            ):
                with col:
                    st.caption(f"{name} ({len(rows)})")
                    try:
                        import pandas as pd

                        if rows:
                            df = pd.DataFrame(
                                [
                                    {
                                        "video_id": r.get("video_id"),
                                        "chunk_id": r.get("chunk_id"),
                                        "score": r.get("score")
                                        or r.get("search_score"),
                                        "text": (r.get("text", "") or "")[:120],
                                    }
                                    for r in rows
                                ]
                            )
                            st.dataframe(df, use_container_width=True)
                        else:
                            st.write("—")
                    except Exception:
                        st.write("—")

    with tab_explore:
        st.subheader("Explore Mongo Collections")
        colx1, colx2 = st.columns(2)
        with colx1:
            st.markdown("#### raw_videos")
            rv_title = st.text_input("Title regex", key="rv_title")
            rv_desc = st.text_input("Description regex", key="rv_desc")
            rv_channel = st.text_input("Channel ID regex", key="rv_channel")
            rv_has_tx = st.checkbox("Has transcript", value=False, key="rv_has_tx")
            if st.button("Search raw_videos", key="rv_btn"):
                q: Dict[str, Any] = {}
                clauses: List[Dict[str, Any]] = []
                if rv_title:
                    clauses.append({"title": {"$regex": rv_title, "$options": "i"}})
                if rv_desc:
                    clauses.append(
                        {"description": {"$regex": rv_desc, "$options": "i"}}
                    )
                if rv_channel:
                    clauses.append(
                        {"channel_id": {"$regex": rv_channel, "$options": "i"}}
                    )
                if rv_has_tx:
                    clauses.append(
                        {
                            "transcript_raw": {
                                "$exists": True,
                                "$type": "string",
                                "$ne": "",
                            }
                        }
                    )
                if clauses:
                    q = {"$and": clauses}
                rows = list(
                    db["raw_videos"]
                    .find(
                        q,
                        {
                            "video_id": 1,
                            "title": 1,
                            "channel_id": 1,
                            "published_at": 1,
                            "stats": 1,
                            "transcript_raw": 1,
                        },
                    )
                    .limit(100)
                )
                try:
                    import pandas as pd

                    df = pd.DataFrame(
                        [
                            {
                                "video_id": r.get("video_id"),
                                "title": (r.get("title") or "")[:80],
                                "channel_id": r.get("channel_id"),
                                "published_at": r.get("published_at"),
                                "views": (r.get("stats", {}) or {}).get("viewCount"),
                                "has_tx": bool(r.get("transcript_raw")),
                            }
                            for r in rows
                        ]
                    )
                    st.dataframe(df, use_container_width=True)
                    st.download_button(
                        "Download CSV",
                        df.to_csv(index=False).encode("utf-8"),
                        file_name="raw_videos_query.csv",
                        mime="text/csv",
                    )
                except Exception as e:
                    st.error(f"Render failed: {e}")
        with colx2:
            st.markdown("#### video_chunks")
            vc_tags = st.text_input("Tags regex", key="vc_tags")
            vc_trust_min = st.slider("Min trust", 0.0, 1.0, 0.0, 0.05, key="vc_trust")
            vc_excl_red = st.checkbox("Exclude redundant", value=True, key="vc_excl")
            if st.button("Search chunks", key="vc_btn"):
                q2: Dict[str, Any] = {}
                if vc_tags:
                    q2["metadata.tags"] = {"$regex": vc_tags, "$options": "i"}
                if vc_trust_min > 0.0:
                    q2["trust_score"] = {"$gte": vc_trust_min}
                if vc_excl_red:
                    q2["is_redundant"] = {"$ne": True}
                rows2 = list(
                    db["video_chunks"]
                    .find(
                        q2,
                        {
                            "video_id": 1,
                            "chunk_id": 1,
                            "text": 1,
                            "metadata": 1,
                            "trust_score": 1,
                        },
                    )
                    .limit(200)
                )
                try:
                    import pandas as pd

                    df2 = pd.DataFrame(
                        [
                            {
                                "video_id": r.get("video_id"),
                                "chunk_id": r.get("chunk_id"),
                                "trust": r.get("trust_score"),
                                "tags": ", ".join(
                                    (r.get("metadata", {}) or {}).get("tags", [])[:6]
                                ),
                                "text": (r.get("text", "") or "")[:160],
                            }
                            for r in rows2
                        ]
                    )
                    st.dataframe(df2, use_container_width=True)
                    st.download_button(
                        "Download CSV",
                        df2.to_csv(index=False).encode("utf-8"),
                        file_name="video_chunks_query.csv",
                        mime="text/csv",
                    )
                except Exception as e:
                    st.error(f"Render failed: {e}")

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
                coll.find(
                    filt_a, {"chunk_id": 1, "text": 1, "metadata": 1, "trust_score": 1}
                ).limit(50)
            )
            b_rows = list(
                coll.find(
                    filt_b, {"chunk_id": 1, "text": 1, "metadata": 1, "trust_score": 1}
                ).limit(50)
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
            import pandas as pd

            st.write("Channel A chunks (top by trust):")
            df_a = pd.DataFrame(
                [
                    {
                        "chunk_id": r.get("chunk_id"),
                        "trust": r.get("trust_score"),
                        "tags": ", ".join(r.get("metadata", {}).get("tags", [])[:6]),
                        "text": r.get("text", "")[:140],
                    }
                    for r in sorted(
                        a_rows, key=lambda x: x.get("trust_score", 0.0), reverse=True
                    )[:20]
                ]
            )
            st.dataframe(df_a, use_container_width=True)
            st.write("Channel B chunks (top by trust):")
            df_b = pd.DataFrame(
                [
                    {
                        "chunk_id": r.get("chunk_id"),
                        "trust": r.get("trust_score"),
                        "tags": ", ".join(r.get("metadata", {}).get("tags", [])[:6]),
                        "text": r.get("text", "")[:140],
                    }
                    for r in sorted(
                        b_rows, key=lambda x: x.get("trust_score", 0.0), reverse=True
                    )[:20]
                ]
            )
            st.dataframe(df_b, use_container_width=True)
            # Top channels summary (by avg trust)
            try:
                import pandas as pd
                import numpy as np

                both = a_rows + b_rows
                rows_ch = [
                    {
                        "channel": r.get("metadata", {}).get("channel_id"),
                        "trust": r.get("trust_score", 0.0),
                    }
                    for r in both
                    if r.get("metadata", {}).get("channel_id")
                ]
                if rows_ch:
                    df_ch = pd.DataFrame(rows_ch)
                    agg = (
                        df_ch.groupby("channel")["trust"]
                        .agg(["count", "mean", "max"])
                        .reset_index()
                    )
                    agg = agg.sort_values(
                        by=["mean", "count"], ascending=[False, False]
                    ).head(10)
                    st.subheader("Top Channels (by avg trust)")
                    st.dataframe(agg, use_container_width=True)
            except Exception as e:
                st.caption(f"Top channels summary unavailable: {e}")

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
                    {
                        "video_id": 1,
                        "chunk_id": 1,
                        "text": 1,
                        "metadata": 1,
                        "trust_score": 1,
                    },
                ).limit(50)
            )
            import pandas as pd

            df_u = pd.DataFrame(
                [
                    {
                        "video_id": r.get("video_id"),
                        "chunk_id": r.get("chunk_id"),
                        "trust": r.get("trust_score"),
                        "tags": ", ".join(r.get("metadata", {}).get("tags", [])[:6]),
                        "text": r.get("text", "")[:160],
                    }
                    for r in rows
                ]
            )
            st.dataframe(df_u, use_container_width=True)
            # Exports
            csv_u = df_u.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download unique (CSV)",
                csv_u,
                file_name="unique_snippets.csv",
                mime="text/csv",
            )
            md_u = "\n".join(
                [
                    "# Unique Insights",
                    *[
                        f"- {row.video_id}:{row.chunk_id} | trust={row.trust} | {row.tags} | {row.text}"
                        for _, row in df_u.iterrows()
                    ],
                ]
            )
            st.download_button(
                "Download unique (Markdown)",
                md_u,
                file_name="unique_snippets.md",
                mime="text/markdown",
            )
            # Mini dashboards
            try:
                import pandas as pd
                import plotly.express as px

                # Top tags
                tag_counts: Dict[str, int] = {}
                for tags in df_u["tags"].fillna("").tolist():
                    for t in [s.strip() for s in tags.split(",") if s.strip()]:
                        tag_counts[t] = tag_counts.get(t, 0) + 1
                if tag_counts:
                    st.subheader("Top Tags (Unique)")
                    df_tags = pd.DataFrame(
                        sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[
                            :15
                        ],
                        columns=["tag", "count"],
                    )
                    fig = px.bar(df_tags, x="tag", y="count", title="Top Tags")
                    st.plotly_chart(fig, use_container_width=True)

                # Trust histogram
                st.subheader("Trust Score Distribution (Unique)")
                df_hist = df_u[["trust"]].dropna()
                fig2 = px.histogram(df_hist, x="trust", nbins=20)
                st.plotly_chart(fig2, use_container_width=True)
            except Exception as e:
                st.caption(f"Mini-dash unavailable: {e}")

    with tab_summaries:
        st.subheader("Summaries (topic-based)")
        topic_sum = st.text_input("Topic regex", value=topic or "react|state")
        use_llm_sum = st.checkbox("Use LLM for summary", value=True, key="sum_llm")
        if st.button("Build context", key="sum_btn"):
            from app.stages.summarizer import summarize_topic

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
                from app.stages.summarizer import save_summary

                sid = save_summary(topic_sum, context_val)
                st.success(f"Saved summary with id: {sid}")
        st.markdown("---")
        st.caption("Saved Summaries")
        try:
            client = get_mongo_client()
            coll = client[DB_NAME]["summaries"]
            saved_rows = list(
                coll.find({}, {"topic_regex": 1, "context": 1})
                .sort("_id", -1)
                .limit(20)
            )
        except Exception:
            saved_rows = []
        if saved_rows:
            names = [
                f"{i+1}. {r.get('topic_regex','')[:40]}"
                for i, r in enumerate(saved_rows)
            ]
            pick_idx = st.selectbox(
                "Select saved summary",
                list(range(len(names))),
                format_func=lambda i: names[i],
                key="sum_pick",
            )
            picked = saved_rows[pick_idx]
            st.text_area("Saved context", picked.get("context", ""), height=240)
            st.download_button(
                "Download saved summary",
                data=picked.get("context", ""),
                file_name="saved_summary.md",
                mime="text/markdown",
            )
            if st.button("Delete saved", key="sum_del"):
                try:
                    coll.delete_one({"_id": picked["_id"]})
                    st.success("Deleted. Reload the page to refresh list.")
                except Exception as e:
                    st.error(f"Delete failed: {e}")

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
            st.caption(
                f"Embedder: {os.getenv('EMBEDDER','voyage')} | Vector dim: {os.getenv('VECTOR_DIM','1024')}"
            )
            st.caption(
                "Tip: If you switch to hashing, ensure Atlas index numDimensions matches VECTOR_DIM."
            )
            if st.button("Wait for Atlas index READY", key="ctrl_wait_index"):
                os.system(f"{py} Mongo_Hack/main.py wait_index")
        # Persona & Session Manager
        with st.expander("Persona & Session"):
            client = get_mongo_client()
            db = client[DB_NAME]
            from app.services.utils import ensure_user_profiles

            ensure_user_profiles(db)
            from app.services.profiles import (
                list_profiles,
                upsert_profile,
                delete_profile,
                get_profile,
            )

            # Profile selector
            profs = list_profiles()
            name_to_sid = {
                (p.get("name") or p.get("session_id") or ""): p.get("session_id")
                for p in profs
            }
            if name_to_sid:
                pick_prof = st.selectbox(
                    "Load profile", list(name_to_sid.keys()), key="prof_pick"
                )
                if st.button("Load", key="prof_load"):
                    sid = name_to_sid.get(pick_prof)
                    if sid:
                        st.session_state["session_id"] = sid
                        st.success(f"Loaded profile: {pick_prof}")
            # New/Save/Delete
            new_name = st.text_input("Profile name", key="prof_name")
            if st.button("New Profile (new session)", key="prof_new"):
                from uuid import uuid4

                st.session_state["session_id"] = str(uuid4())
                st.success("New session created; set persona and Save preset.")
            personas = [
                {
                    "name": "Academic Research",
                    "weights": {"vector": 0.5, "trust": 0.35, "recency": 0.15},
                    "bias": {"code_present": False},
                },
                {
                    "name": "Job Seeker",
                    "weights": {"vector": 0.45, "trust": 0.2, "recency": 0.35},
                    "bias": {"code_present": True},
                },
                {
                    "name": "Custom",
                    "weights": {"vector": 0.6, "trust": 0.25, "recency": 0.15},
                    "bias": {},
                },
            ]
            pnames = [p["name"] for p in personas]
            pick_p = st.selectbox("Select persona", pnames, key="persona_pick")
            if st.button("Apply persona", key="apply_persona"):
                chosen = next(
                    (p for p in personas if p["name"] == pick_p), personas[-1]
                )
                st.session_state["persona"] = chosen
                st.success(f"Applied persona: {pick_p}")
            # Context Manager
            st.markdown("#### Context Manager")
            interests = st.text_input("Interests (comma)", key="ctx_interests")
            pref_channels = st.text_input(
                "Preferred channels (comma)", key="ctx_channels"
            )
            prefer_recent = st.checkbox("Prefer recent", value=False, key="ctx_recent")
            if st.button("Save preset", key="save_preset"):
                try:
                    sess = st.session_state.get("session_id")
                    if not sess:
                        st.warning("No session id")
                    else:
                        prof = {
                            "name": new_name or sess,
                            "persona": st.session_state.get("persona"),
                            "interests": [
                                s.strip()
                                for s in (interests or "").split(",")
                                if s.strip()
                            ],
                            "preferred_channels": [
                                s.strip()
                                for s in (pref_channels or "").split(",")
                                if s.strip()
                            ],
                            "prefer_recent": bool(prefer_recent),
                            "defaults": {
                                "topic": st.session_state.get("default_topic"),
                                "channel": st.session_state.get("default_channel"),
                            },
                        }
                        upsert_profile(sess, prof)
                        st.success("Preset saved to user_profiles")
                except Exception as e:
                    st.error(f"Save failed: {e}")
            if st.button("Delete current profile", key="prof_del"):
                try:
                    sid = st.session_state.get("session_id")
                    if sid:
                        delete_profile(sid)
                        st.success("Deleted current profile")
                except Exception as e:
                    st.error(f"Delete failed: {e}")
            if st.button("Apply from interactions", key="apply_from_interactions"):
                try:
                    # naive inference from recent queries and feedback tags
                    sess = st.session_state.get("session_id")
                    client = get_mongo_client()
                    db = client[DB_NAME]
                    recents = st.session_state.get("recent_q", [])[-5:]
                    tag_counts: Dict[str, int] = {}
                    for r in (
                        db["video_feedback"]
                        .find({"session_id": sess}, {"tags": 1})
                        .limit(200)
                    ):
                        for t in r.get("tags", []) or []:
                            tag_counts[t] = tag_counts.get(t, 0) + 1
                    top_tags = [
                        t
                        for t, _ in sorted(
                            tag_counts.items(), key=lambda x: x[1], reverse=True
                        )[:5]
                    ]
                    st.session_state["default_topic"] = (
                        top_tags[0]
                        if top_tags
                        else st.session_state.get("default_topic")
                    ) or ""
                    st.success("Applied preferences from interactions")
                except Exception as e:
                    st.error(f"Inference failed: {e}")
            # Session switcher (simple)
            sid = st.session_state.get("session_id")
            new_sid = st.text_input(
                "Switch to session id", value=sid or "", key="switch_sid"
            )
            if st.button("Switch session", key="switch_session") and new_sid:
                st.session_state["session_id"] = new_sid
                st.success("Session switched.")

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
                st.session_state["last_ingest_args"] = args
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
        if st.button("Run Full Pipeline for Last Ingest Args", key="ctrl_pipe_last"):
            last = st.session_state.get("last_ingest_args")
            if last:
                flag = " --llm" if use_llm else ""
                st.toast("Launching full pipeline for last ingest args...", icon="🚀")
                os.system(f"{py} Mongo_Hack/main.py pipeline {' '.join(last)}{flag}")
            else:
                st.warning("No previous ingest args found in this session.")


if __name__ == "__main__":
    main()
