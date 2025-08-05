import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import pandas as pd

import pandas as pd

# Read the file, force all as string, handle missing
df = pd.read_excel("Slice-policyupdated.xlsx", dtype=str)
df.fillna("", inplace=True)

# Get the column names
column_names = df.columns.tolist()

rag_data = []

for _, row in df.iterrows():
    row_data = {}
    for col in column_names:
        row_data[col] = row[col]

    # Create the text for embedding
    text = " ".join(str(value) for value in row_data.values())

    rag_data.append({
        "text": text,
        "metadata": row_data
    })

# Extract the text for embedding
texts = [item["text"] for item in rag_data]

# Load the sentence transformer model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Create the embeddings
embeddings = model.encode(texts, show_progress_bar=True)

# Create a FAISS index
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings.astype('float32'))

# Save the index and the data
faiss.write_index(index, "rag_policies.faiss")
with open("rag_data.json", "w", encoding="utf-8") as f:
    json.dump(rag_data, f, indent=2, ensure_ascii=False)

print("Vector store created successfully.")
