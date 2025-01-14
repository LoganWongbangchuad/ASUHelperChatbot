import os
import openai
import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Get MongoDB URI
mongodb_uri = os.getenv("MONGODB_URI")
# Create a new client and connect to the server
client = MongoClient(mongodb_uri, server_api=ServerApi('1'))

# Access the database and collection
db = client["web_data"]
collection = db["pages"]

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_URI")  # or OPENAI_API_KEY, whichever env var you use

# Choose your models
# 1) For summary (ChatCompletion model)
SUMMARY_MODEL = "gpt-3.5-turbo"
# 2) For embedding (recommended model)
EMBED_MODEL = "text-embedding-ada-002"  # "text-embedding-3-small" is likely unsupported


#count = 1

def get_embedding(text: str) -> list:
    global count  # Tell Python we want to modify the global variable 'count'
    response = openai.Embedding.create(
        input=[text],
        model=EMBED_MODEL
    )
    embedding = response.data[0]["embedding"]
    
    #print(count)
    #count += 1  # increment the global count
    
    return embedding


    '''
    try:
        embed_response = openai.Embedding.create(
            input=[text],
            model=EMBED_MODEL
        )
        embedding_vector = embed_response.data[0]["embedding"]
        return embedding_vector
    except Exception as e:
        print(f"Error creating embedding: {e}")
        return []
    '''