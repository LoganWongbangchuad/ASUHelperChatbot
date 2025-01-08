import os
import openai
import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from openai import OpenAI


# Get MongoDB URI
uri = os.getenv("MONGODB_URI")

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["web_data"]
collection = db["pages"]
# Specify your OpenAI API key and embedding model
URI = os.getenv("OPENAI_URI")
#os.environ["OPENAI_API_KEY"] = "OPENAI_URI"
#openai_client = OpenAI()
openai_client = OpenAI(api_key=URI)
SUMMARY_MODEL = "gpt-3.5-turbo"
# (2) For embedding
EMBED_MODEL = "text-embedding-3-small"

# --------------------------------------------------
# Function to Summarize Text
# --------------------------------------------------

def summarize_text(long_text: str) -> str:
    """
    Summarize long_text using GPT-3.5 (ChatCompletion).
    Returns the summary as a string.
    """
    # Prepare messages for ChatCompletion
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
        return ""  # Or handle error appropriately

# --------------------------------------------------
# Function to Generate Embedding
# --------------------------------------------------

def get_embedding(text: str) -> list:
    """
    Creates an embedding using text-embedding-ada-002 model.
    Returns the embedding as a list of floats.
    """
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
    title = doc["title"]
    description = doc["description"]
    paragraphs = doc["paragraphs"]  # list of strings

    # Combine them into a single text block
    combined_text = f"{title}\n\n{description}\n\n" + "\n".join(paragraphs)

    # 1) Summarize the combined text
    summary_text = summarize_text(combined_text)

    # 2) Embed the summary
    summary_embedding = get_embedding(summary_text)

    # Save both the summary and embedding if you want
    # (or just the embedding, depending on your use case)
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