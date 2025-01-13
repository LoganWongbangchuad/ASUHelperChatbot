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

# Create your index model, then create the search index
search_index_model = SearchIndexModel(
  definition = {
    "fields": [
      {
        "type": "vector",
        "path": "summary_embedding",
        "similarity": "dotProduct",
         "numDimensions": 1536
      }
    ]
  },
  name="vector_summary_index",
  type="vectorSearch",
)
collection.create_search_index(model=search_index_model)
