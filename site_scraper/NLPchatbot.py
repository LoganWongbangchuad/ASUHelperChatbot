from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from pymongo import MongoClient

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

# Access the database and collection
db = client["web_data"]
collection = db["pages"]

#Function search_all_collections(database, user_query):
#    Get a list of all collections in the database
#    Initialize an empty list to store search results

#    For each collection in the list:
#        Access the collection
#        Try to perform a full-text search with the query
#            Add the search results to the results list
#        If an error occurs:
#            Log the error

#    Return the aggregated search results


def search_all_collections(db, user_query):
    collection_list = db.list_collection_names()
    results = []

    for collection in collection_list:
        current_col = db[collection]
        try:
            result = db.current_col.find({'$text':{'$search':user_query}})
            results.extend(result)        
        except Exception as e:
            print(f"Error searching collection {collection}: {e}")

    print(len(results))

    return results

search_all_collections(db, "registration")