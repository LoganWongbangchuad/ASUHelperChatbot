# app.py

import os
import openai
import numpy as np
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask import Flask, request, jsonify
from flask_cors import CORS
from retrieval import get_query_results  # Ensure this module is correctly implemented

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes. Adjust as needed for security.






# Get MongoDB URI
uri = os.getenv("MONGODB_URI")

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Set your OpenAI API key from the environment variable
# Ensure that OPENAI_URI contains only the API key
openai.api_key = os.getenv("OPENAI_URI")  # Ensure this environment variable is set

# Optional: Debugging - print the API key (remove in production)
# print(f"OpenAI API Key: {openai.api_key}")  # Uncomment for debugging

def cosine_similarity(vec_a, vec_b):
    """Calculate the cosine similarity between two vectors."""
    return np.dot(vec_a, vec_b) / (np.linalg.norm(vec_a) * np.linalg.norm(vec_b))

def get_embeddings(text, model="text-embedding-ada-002"):
    """Get the embedding from OpenAI for a given text using a specified model."""
    result = openai.Embedding.create(
        input=[text],
        model=model
    )
    # Return the embedding vector of the first (and only) item in 'data'
    return result["data"][0]["embedding"]

@app.route('/generate_response', methods=['POST'])
def generate_response():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided.'}), 400

    query = data['message']
    
    try:
        # 2. Retrieve documents (even if they might not be relevant)
        context_docs = get_query_results(query)
        context_string = " ".join([doc["summary"] for doc in context_docs])
        
        # 3. Build the context-based prompt
        prompt = f"""
        Use the following pieces of context to answer the question at the end.
        If there is no clear indication or no relevant information provided in this context,
        please explicitly say something like: 'Based on the information provided, there is no indication of this.'
        only say this if there is no relevant information, otherwise just speak normally.
        
        Context:
        {context_string}
        
        Question: {query}
        """
        
        # 4. Make the first call (knowledge-based)
        knowledge_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        knowledge_answer = knowledge_response.choices[0].message["content"]
        
        # 5. Check if the knowledge-based answer indicates insufficient info
        fallback_keywords = [
            "no indication", 
            "no relevant information", 
            "not enough information", 
            "no data"
        ]
        needs_fallback = any(keyword in knowledge_answer.lower() for keyword in fallback_keywords)
        
        if needs_fallback:
            # ---- FALLBACK LOGIC ----
            print("IN FALLBACK")
        
            # 6. Fallback to regular ChatGPT with a simpler prompt
            fallback_prompt = (
                f"You are a helpful Angelo State University assistant. The user asked: '{query}'. "
                f"Please provide the best possible answer for only questions "
                f"related to Angelo State University or ASU."
                f"You should search the internet to find answers to the questions."
            )
            fallback_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for Angelo State University."},
                    {"role": "user", "content": fallback_prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            fallback_answer = fallback_response.choices[0].message["content"]
        
            # Since fallback was triggered, we assume knowledge-based had no relevant info;
            # we can directly return the fallback answer.
            response_text = fallback_answer
        
        else:
            # ---- KNOWLEDGE-CHECK LOGIC ----
            # If knowledge-based AI responded with *some* info (not flagged as insufficient),
            # compare with general ChatGPT.
        
            check_prompt = (
                f"You are a Angelo State University helpful assistant. The user asked: '{query}'. "
                f"Please provide the best possible answer for questions only related to Angelo State University."
            )
            check_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a Angelo State University helpful assistant."},
                    {"role": "user", "content": check_prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            check_answer = check_response.choices[0].message["content"]
        
            # 8. Calculate semantic similarity between knowledge_answer and check_answer
            knowledge_embedding = get_embeddings(knowledge_answer)
            check_embedding = get_embeddings(check_answer)
            similarity_score = cosine_similarity(knowledge_embedding, check_embedding)
        
            # 9. Define a threshold for deciding if the answers are "close enough"
            #    You may need to tweak this threshold after testing real queries.
            similarity_threshold = 0.88
            print(f"Similarity Score: {similarity_score}")
            print()
            if similarity_score >= similarity_threshold:
                # If answers are sufficiently similar, trust the knowledge-based answer
                response_text = knowledge_answer
            else:
                # If they're too different, assume ChatGPT's answer is better
                response_text = check_answer
        
        return jsonify({'response': response_text}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred while generating the response.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
