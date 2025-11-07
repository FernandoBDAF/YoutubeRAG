#!/usr/bin/env python3
"""Check GraphRAG data across all databases."""

from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
client = MongoClient(mongo_uri)

print("=" * 80)
print("CHECKING ALL DATABASES FOR GRAPHRAG DATA")
print("=" * 80)

for db_name in client.list_database_names():
    if db_name in ["admin", "local", "config"]:
        continue

    db = client[db_name]
    colls = db.list_collection_names()

    if "entities" in colls or "relations" in colls:
        entities_count = db.entities.count_documents({}) if "entities" in colls else 0
        relations_count = (
            db.relations.count_documents({}) if "relations" in colls else 0
        )
        mentions_count = (
            db.entity_mentions.count_documents({}) if "entity_mentions" in colls else 0
        )
        communities_count = (
            db.communities.count_documents({}) if "communities" in colls else 0
        )

        if entities_count > 0 or relations_count > 0:
            print(f"\n{db_name}:")
            print(f"  Entities: {entities_count}")
            print(f"  Relations: {relations_count}")
            print(f"  Entity Mentions: {mentions_count}")
            print(f"  Communities: {communities_count}")
