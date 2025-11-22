import chromadb
import ollama
from chromadb import Documents, EmbeddingFunction, Embeddings
from typing import List

# Correct embedding function for ChromaDB
class OllamaEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model="nomic-embed-text"):
        self.model = model

    def __call__(self, input: Documents) -> Embeddings:
        embeddings = []
        for text in input:
            try:
                resp = ollama.embeddings(model=self.model, prompt=text)
                embedding = resp["embedding"]
                # Validate embedding is not empty
                if len(embedding) == 0:
                    print(f"Warning: Empty embedding for text: '{text[:50]}...'")
                    # Create a dummy embedding to avoid errors
                    embedding = [0.0] * 384  # Adjust size based on your model
                embeddings.append(embedding)
            except Exception as e:
                print(f"Error generating embedding for text: '{text[:50]}...' - {e}")
                # Create a dummy embedding to continue
                embedding = [0.0] * 384
                embeddings.append(embedding)
        return embeddings

# Initialize persistent Chroma DB
client = chromadb.PersistentClient(path="./company_db")

collection = client.get_or_create_collection(
    name="company_info",
    embedding_function=OllamaEmbeddingFunction()
)

# Load company data with validation
with open("company_data.txt", "r") as f:
    lines = f.readlines()

# Filter out empty lines and validate data
valid_lines = []
for i, line in enumerate(lines):
    stripped_line = line.strip()
    if stripped_line:  # Only process non-empty lines
        valid_lines.append(stripped_line)
    else:
        print(f"Skipping empty line at index {i}")

print(f"Processing {len(valid_lines)} valid documents")

# Insert documents into collection
for i, line in enumerate(valid_lines):
    try:
        collection.add(
            ids=[f"doc_{i}"],
            documents=[line]
        )
        print(f"✅ Added document {i}: {line[:50]}...")
    except Exception as e:
        print(f"❌ Failed to add document {i}: {e}")

print("✅ Company data indexing completed!")










# import chromadb
# import ollama

# # Custom embedding class for Chroma (new API spec)
# class OllamaEmbeddingFunction:
#     def __init__(self, model="nomic-embed-text"):
#         self.model = model

#     def __call__(self, input):
#         # Ensure input is always a list
#         if isinstance(input, str):
#             input = [input]

#         embeddings = []
#         for text in input:
#             resp = ollama.embeddings(model=self.model, prompt=text)
#             embeddings.append(resp["embedding"])
#         return embeddings

#     def name(self):
#         return f"ollama-{self.model}"

# # Initialize persistent Chroma DB
# client = chromadb.PersistentClient(path="./company_db")

# collection = client.get_or_create_collection(
#     name="company_info",
#     embedding_function=OllamaEmbeddingFunction()
# )

# # Load company data
# with open("company_data.txt", "r") as f:
#     lines = f.readlines()

# # Insert documents into collection
# for i, line in enumerate(lines):
#     collection.add(
#         ids=[f"doc_{i}"],
#         documents=[line.strip()]
#     )

# print("✅ Company data indexed successfully!")
