from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import json
import os
from pymongo import MongoClient
import gridfs

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

# Initialize GridFS for large file storage
fs = gridfs.GridFS(db)

# Load the JSON data
with open("general_extracted_data.json", "r") as file:
    data = json.load(file)

# Check if the JSON data exceeds 16MB
json_data_size = len(json.dumps(data).encode('utf-8'))

# If the file size is larger than 16MB, store it in GridFS
if json_data_size > 16 * 1024 * 1024:  # 16MB
    # Store in GridFS
    with fs.new_file(filename="general_extracted_data.json") as gridfile:
        gridfile.write(json.dumps(data).encode('utf-8'))  # Write the encoded JSON data to GridFS
    print("Large file stored in GridFS.")
else:
    # If the file is smaller or equal to 16MB, store normally without chunking
    collection.insert_one(data)  # Insert the data directly as one document
    print("Data inserted into MongoDB!")
