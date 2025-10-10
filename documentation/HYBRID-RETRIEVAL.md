# Hybrid Retrieval, Hashing Fallback, Bulk Upserts, and wait_index — Deep Dive

This guide explains the new capabilities added to Mongo_Hack to improve recall, resilience, and throughput during the hackathon:

- Hybrid Atlas Search (keyword + vector) in one query
- HashingVectorizer fallback embeddings (offline, deterministic)
- Bulk upserts for faster chunk writes
- Atlas Search index readiness waiter (`wait_index`)
- UI additions: Hybrid tab and optional LLM streaming toggle

Each section includes project snippets and demo tips using the built-in Streamlit app.

## 1) Hybrid Atlas Search (keyword + vector)

Project code (excerpt):

```1:44:Mongo_Hack/app/services/retrieval.py
import os
from typing import Any, Dict, List, Optional
from pymongo.collection import Collection

def hybrid_search(
    col: Collection,
    query_text: str,
    query_vector: List[float],
    top_k: int = 8,
    filters: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    ...
    search_stage: Dict[str, Any] = {"$search": {"compound": {"should": compound_should}}}
    if filters:
        search_stage["$search"]["filter"] = filters
    pipeline = [..., {"$project": {"search_score": {"$meta": "searchScore"}, "_sd": {"$meta": "searchScoreDetails"}}}, {"$addFields": {"keyword_score": {"$ifNull": ["$_sd.textScore", null]}, "vector_score": {"$ifNull": ["$_sd.vectorSearchScore", null]} }}, {"$project": {"_sd": 0}}, {"$limit": int(top_k)}]
    try:
        return list(col.aggregate(pipeline))
    except Exception:
        # Fallback to vectorSearch only
        vs_pipeline = [..., {"$project": {"search_score": {"$meta": "vectorSearchScore"}}}]
        return list(col.aggregate(vs_pipeline))
```

UI usage: “Hybrid Search” tab → enter query, adjust Top‑k and filters, review `search_score` plus `keyword_score` and `vector_score`; export CSV.

## 2) HashingVectorizer Fallback Embeddings

Project code:

```1:22:Mongo_Hack/core/embedder_hashing.py
class HashingEmbedder:
    def __init__(self, n_features: int = 1024) -> None: ...
    def embed(self, text: str) -> List[float]: ...
```

Wiring in chunking:

```159:205:Mongo_Hack/app/stages/chunk_embed.py
embedder_choice = os.getenv("EMBEDDER", "voyage").strip().lower()
hashing_dim = int(os.getenv("VECTOR_DIM", str(VECTOR_DIM)))
...
if embedder_choice == "hashing":
    from core.embedder_hashing import HashingEmbedder
    hasher = HashingEmbedder(n_features=hashing_dim)
    vectors = [hasher.embed(t) for t in texts]
else:
    vectors = embed_texts(texts) if texts else []
```

## 3) Bulk Upserts (batched)

Project code:

```269:299:Mongo_Hack/app/stages/chunk_embed.py
from pymongo import UpdateOne
BATCH = 500
for i in range(0, len(out_docs), BATCH):
    batch = out_docs[i : i + BATCH]
    ops = [UpdateOne({"video_id": d["video_id"], "chunk_id": d["chunk_id"]}, {"$set": d}, upsert=True) for d in batch]
    chunks_coll.bulk_write(ops, ordered=False)
```

## 4) Index Readiness Waiter

Project code:

```127:164:Mongo_Hack/config/seed/seed_indexes.py
def wait_for_index_ready(index_name: str, timeout_s: int = 300, poll_s: int = 5) -> None:
    ...
    if index_name in out and "READY" in out:
        return
```

CLI:

```bash
python Mongo_Hack/main.py wait_index
```

## 5) UI additions

- Q&A: “Stream LLM answer” toggle (wired through as a flag to `rag_answer`).
- Hybrid tab: results table (with `search_score`, `keyword_score`, and `vector_score`) with CSV export + expandable snippets.

Snippets:

```201:261:Mongo_Hack/streamlit_app.py
stream_ans = st.checkbox("Stream LLM answer", value=(os.getenv("LLM_STREAMING","false").lower() in ("1","true","yes")), key="qna_stream")
...
result = rag_answer(..., streaming=bool(stream_ans))
```

```573:599:Mongo_Hack/streamlit_app.py
if hits_h:
    st.caption(f"Found {len(hits_h)} hits")
    # DataFrame + CSV export block (includes per-operator scores)
    for h in hits_h:
        with st.expander(...):
            st.write(h.get("text", "")[:1500])
```

## 6) Env flags

Added in `env.example`:

- `EMBEDDER=voyage|hashing`
- `VECTOR_DIM=1024`
- `TOP_K=8`
- `LLM_STREAMING=false`

## Demo checklist

- Compare Vector vs Hybrid tabs for recall/precision; point out keyword vs vector contributions using the scores.
- Switch to `EMBEDDER=hashing` and re-run chunk stage; verify `embedding_model` and `embedding_dim`.
- Observe faster chunk writes with bulk upserts for larger transcripts.
- Run `wait_index` before testing retrieval on a fresh cluster.
