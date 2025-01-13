import os
import openai
import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from get_embeddings import get_embedding


# --------------------------------------------------
# Setup: environment variables, MongoDB, and OpenAI
# --------------------------------------------------

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
# --------------------------------------------------
# Function to Summarize Text
# --------------------------------------------------

def summarize_text(long_text: str) -> str:
    """
    Summarize long_text using GPT-3.5 (ChatCompletion).
    Returns the summary as a string.
    """
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant that summarizes text. "
                "Please provide a concise summary of the text given by the user."
            )
        },
        {
            "role": "user",
            "content": long_text
        }
    ]
    
    try:
        response = openai.ChatCompletion.create(
            model=SUMMARY_MODEL,
            messages=messages,
            max_tokens=150,  # Limit summary length if desired
            temperature=0.7
        )
        summary = response.choices[0].message["content"].strip()
        return summary
    except Exception as e:
        print(f"Error during summarization: {e}")
        return ""

# --------------------------------------------------
# Main Logic: Summarize then Embed
# --------------------------------------------------

# Example filter to ensure the fields exist and aren't empty
filter_query = {
    "$and": [
        {"title": {"$nin": [None, ""]}},
        {"description": {"$nin": [None, ""]}},
        {"paragraphs": {"$exists": True, "$ne": []}}
    ]
}

documents = collection.find(filter_query)

updated_doc_count = 0

for doc in documents:
    # Combine your fields (title, description, paragraphs) into one big text
    title = doc.get("title", "")
    description = doc.get("description", "")
    paragraphs = doc.get("paragraphs", [])  # list of strings

    # Combine them into a single text block
    combined_text = f"{title}\n\n{description}\n\n" + "\n".join(paragraphs)

    # 1) Summarize the combined text
    summary_text = summarize_text(combined_text)

    # 2) Embed the summary
    summary_embedding = get_embedding(summary_text)

    # Save both the summary and embedding
    collection.update_one(
        {"_id": doc["_id"]},
        {
            "$set": {
                "summary": summary_text,
                "summary_embedding": summary_embedding
            }
        }
    )

    updated_doc_count += 1

print(f"Successfully updated {updated_doc_count} documents with summary and summary_embedding.")


