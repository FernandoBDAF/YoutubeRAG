import os
from typing import Optional

from pymongo import MongoClient


def get_mongo_client(uri: Optional[str] = None) -> MongoClient:
    """Create a MongoClient from env or passed URI."""
    try:
        # Ensure Mongo_Hack/.env is honored even if caller didn't load it
        from dotenv import load_dotenv
        from pathlib import Path

        load_dotenv()
    except Exception:
        pass
    uri = uri or os.getenv("MONGODB_URI")
    if not uri:
        raise RuntimeError("MONGODB_URI is not set.")
    return MongoClient(uri)
