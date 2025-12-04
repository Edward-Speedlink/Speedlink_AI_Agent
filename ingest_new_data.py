# ingest_new_data.py
import chromadb
import ollama

class OllamaEmbeddingFunction:
    def __init__(self, model="nomic-embed-text"):
        self.model = model

    def __call__(self, input):
        if isinstance(input, str):
            input = [input]

        embeddings = []
        for text in input:
            resp = ollama.embeddings(model=self.model, prompt=text)
            embeddings.append(resp["embedding"])
        return embeddings

    def name(self):
        return f"ollama-{self.model}"

# Connect to Chroma
client = chromadb.PersistentClient(path="./company_db")
collection = client.get_or_create_collection(
    name="company_info",
    embedding_function=OllamaEmbeddingFunction()
)

# Load new data
with open("company_data.txt", "r") as f:
    lines = [line.strip() for line in f if line.strip()]

# Optionally: clear old collection
# collection.delete()  # uncomment if you want a fresh start

# Add updated documents
for i, line in enumerate(lines):
    collection.add(
        ids=[f"doc_{i}"],
        documents=[line]
    )

print(f"✅ Indexed {len(lines)} documents into ChromaDB")
