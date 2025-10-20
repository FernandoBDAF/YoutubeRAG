import os
from dotenv import load_dotenv
import argparse
import pandas as pd

try:
    from app.services.utils import get_mongo_client
except ModuleNotFoundError:
    import sys as _sys, os as _os

    _sys.path.append(
        _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
    )
from app.services.utils import get_mongo_client

from app.services.retrieval import vector_search
from config.paths import DB_NAME, COLL_CHUNKS
from app.services.indexes import setup_vector_search_index
from app.services.rag import embed_query

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Vector search")
    parser.add_argument("--query", type=str, required=True)
    parser.add_argument("--col", type=str, required=False)
    return parser.parse_args()

def main() -> None:
    load_dotenv()
    args = parse_args()
    client = get_mongo_client()
    db = client[DB_NAME]
    col = db[args.col or COLL_CHUNKS]
    setup_vector_search_index(col)
    query = args.query if not query else query
    qvec = embed_query(args.query)
    try:
        hits = vector_search(col, qvec, 5)
    except Exception as e:
        print(f"Error: {e}")
        return

    hits_df = pd.DataFrame(hits)

    print(hits_df)
    return hits_df

    # for hit in hits:
    #     print(f"{hit.get('chunk_id')}: {hit.get('score', 0)}")
    #     print(hit.get('text'))
    #     print(hit.get('metadata', {}).get('tags', []))
    #     print("-"*100)
    # print(f"Total hits: {len(hits)}")


if __name__ == "__main__":
    query = os.getenv("QUERY")
    print("query: ", query)
    main()