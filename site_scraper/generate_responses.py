import os
import openai
from retrieval import get_query_results

# 1. Prompt user for a question
query = input("Ask a Question! ")

# 2. Retrieve relevant documents and build context string
context_docs = get_query_results(query)
context_string = " ".join([doc["summary"] for doc in context_docs])

# 3. Construct the prompt
prompt = f"""Use the following pieces of context to answer the question at the end.
{context_string}
Question: {query}
"""

# 4. Set up your OpenAI credentials
openai.api_key = os.getenv("OPENAI_URI")  # or store your API key another way

# 5. Send the prompt to OpenAI's ChatCompletion (for GPT-3.5, GPT-4, etc.)
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": prompt}
    ],
    max_tokens=150,
    temperature=0.7  # optional tweak
)

# 6. Print the response content
print(response.choices[0].message["content"])
