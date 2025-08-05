import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load the FAISS index and RAG data
index = faiss.read_index("rag_policies.faiss")
with open("rag_data.json", "r", encoding="utf-8") as f:
    rag_data = json.load(f)

# Load the sentence transformer model
model = SentenceTransformer("all-MiniLM-L6-v2")

def generate_rego_policy(query):
    # Embed the query
    query_embedding = model.encode([query])

    # Search for the most relevant documents
    k = 2  # Number of documents to retrieve
    distances, indices = index.search(query_embedding.astype('float32'), k)

    # Generate the Rego policy from the retrieved documents
    retrieved_docs = [rag_data[i] for i in indices[0]]

    # This is a simple example of how to generate a Rego policy.
    # You will likely need to customize this part based on your specific needs.
    policy = "package main\n\n# Generated Rego Policy\n\n"
    for doc in retrieved_docs:
        metadata = doc["metadata"]
        policy += f"# MO Type: {metadata['MO Type']}, Full Path: {metadata['Full Path']}, Attribute: {metadata['Attribute ']}, Operation: {metadata['Operation']}, Value: {metadata['Value']}\n"
        policy += f"allow {{\n    input.mo_type == \"{metadata['MO Type']}\"\n    input.full_path == \"{metadata['Full Path']}\"\n    input.attribute == \"{metadata['Attribute ']}\"\n    input.operation == \"{metadata['Operation']}\"\n    input.value == \"{metadata['Value']}\"\n}}\n\n"

    return policy

if __name__ == "__main__":
    # Get user input
    user_query = input("Enter your query to generate a Rego policy: ")

    # Generate and print the policy
    rego_policy = generate_rego_policy(user_query)
    print("\nGenerated Rego Policy:\n")
    print(rego_policy)
