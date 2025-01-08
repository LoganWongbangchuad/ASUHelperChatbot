from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import json
from pathlib import Path
import os

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

# Path to the folder containing the JSON files
folder_path = Path("extracted_pages")

# Iterate through all JSON files in the folder and insert them individually
for json_file in folder_path.glob("*.json"):
    # Skip the combined file
    if json_file.name == "combined_extracted_data.json":
        print(f"Skipping {json_file.name}.")
        continue

    try:
        with open(json_file, "r", encoding="utf-8") as file:
            # Load JSON data
            file_data = json.load(file)

            # Insert the data into MongoDB
            if isinstance(file_data, dict):  # Ensure it's a single document
                collection.insert_one(file_data)
            elif isinstance(file_data, list):  # If it's a list of documents
                collection.insert_many(file_data)
            print(f"Inserted data from {json_file.name} into MongoDB.")
    except Exception as e:
        print(f"Failed to process {json_file.name}: {e}")

print("All data inserted into MongoDB!")
