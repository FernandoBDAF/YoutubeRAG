from pymongo.operations import SearchIndexModel
from pymongo.collection import Collection
import time
from pymongo.errors import OperationFailure
import json


def setup_vector_search_index(
    collection: Collection,
    text_embedding_field_name: str = "embedding",
    vector_search_index_name: str = "vector_index_text",
):

    vector_search_index_model = SearchIndexModel(
        definition={
            "mappings": {
                "dynamic": True,
                "fields": {
                    text_embedding_field_name: {
                        "dimensions": 1024,
                        "similarity": "cosine",
                        "type": "vector",
                    }
                },
            }
        },
        name=vector_search_index_name,
    )

    index_exists = False
    print(f"Listing search indexes for collection: {collection.name}")
    for index in collection.list_search_indexes():
        if index["name"] == vector_search_index_name:
            index_exists = True
            break

    if not index_exists:
        try:
            result = collection.create_search_index(vector_search_index_model)
            print("Creating index...")
            time.sleep(20)
            print(f"Index created successfully: {result}")
        except OperationFailure as e:
            print(f"Error creating vector search index: {str(e)}")
    else:
        print(f"Index '{vector_search_index_name}' already exists.")
