from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
import numpy as np
from sentence_transformers import SentenceTransformer

# Get MongoDB URI
uri = os.getenv("MONGODB_URI")

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Access the database
db = client["web_data"]

# Initialize the SentenceTransformer model (for embeddings)
model = SentenceTransformer('all-MiniLM-L6-v2')  # You can replace with your preferred model

def generate_query_embedding(query):
    """Generate an embedding for the user query using SentenceTransformer."""
    return model.encode([query])[0]  # Generate a single embedding

def search_collection_atlas(db, collection_name, query_embedding):
    """Search a specific collection using Atlas Vector Search for similarity."""
    
    results = []
    
    try:
        # Access the specified collection
        if collection_name in db.list_collection_names():
            print(f"Accessing collection: {collection_name}")  # Debug statement
        else:
            print(f"Collection '{collection_name}' does not exist in the database.")
            return results
        
        collection = db[collection_name]
        
        # Use Atlas Vector Search with $search and the vector operator
        pipeline = [
            {
                "$search": {
                    "index": "default",  # Specify the index you have created for vector search
                    "knnBeta": {
                        "vector": {
                            "query": query_embedding,
                            "path": "embedding",  # The field where embeddings are stored
                            "k": 10  # Number of closest vectors to retrieve
                        }
                    }
                }
            },
            {"$limit": 10}  # Optional: limit the number of results
        ]
        
        # Execute the aggregation query
        query_results = collection.aggregate(pipeline)
        results.extend(query_results)
    
    except Exception as e:
        print(f"Error searching collection {collection_name}: {e}")
    
    return results

def search_all_collections(db, user_query):
    """Search all collections in the database using Atlas Vector Search."""
    
    all_results = []
    
    try:
        # Generate the query embedding
        query_embedding = generate_query_embedding(user_query)
        
        # Get a list of all collection names in the database
        collection_names = db.list_collection_names()
        
        print(f"Searching through {len(collection_names)} collections...")
        
        # For each collection, search and collect the results
        for collection_name in collection_names:
            print(f"Searching in collection: {collection_name}")
            collection_results = search_collection_atlas(db, collection_name, query_embedding)
            if collection_results:
                all_results.extend(collection_results)
    
    except Exception as e:
        print(f"Error searching all collections: {e}")
    
    return all_results

# Specify the search query
user_query = "What scholarships does ASU have to offer?"

# Perform the search across all collections
search_results = search_all_collections(db, user_query)

# Print the results
if search_results:
    print(f"Found {len(search_results)} results:")
    for result in search_results:
        print(result)
else:
    print("No results found.")
