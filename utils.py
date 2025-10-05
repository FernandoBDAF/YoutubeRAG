import os
from typing import Optional

from pymongo import MongoClient


def get_mongo_client(uri: Optional[str] = None) -> MongoClient:
    """Create a MongoClient from env or passed URI."""
    uri = uri or os.getenv("MONGODB_URI")
    if not uri:
        raise RuntimeError("MONGODB_URI is not set.")
    return MongoClient(uri)
