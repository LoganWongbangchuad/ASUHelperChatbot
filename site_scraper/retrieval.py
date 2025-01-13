import os
import pymongo
import openai
from get_embeddings import get_embedding
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.operations import SearchIndexModel

# Get MongoDB URI
mongodb_uri = os.getenv("MONGODB_URI")
# Create a new client and connect to the server
client = MongoClient(mongodb_uri, server_api=ServerApi('1'))

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_URI")  # or OPENAI_API_KEY, whichever env var you use

# Access the database and collection
db = client["web_data"]
collection = db["pages"]
def get_query_results(query):
    # Generate embedding for the search query
    query_embedding = get_embedding(query)

    # Sample vector search pipeline
    pipeline = [
    {
        "$vectorSearch": {
                "index": "vector_summary_index",
                "queryVector": query_embedding,
                "path": "summary_embedding",
                "exact": True,
                "limit": 5
        }
    }, 
    {
        "$project": {
            "_id": 0, 
            "summary": 1,
            "score": {
                "$meta": "vectorSearchScore"
            }
        }
    }
    ]

    # Execute the search
    results = collection.aggregate(pipeline)

    array_of_results = []
    for doc in results:
        array_of_results.append(doc)
    return array_of_results