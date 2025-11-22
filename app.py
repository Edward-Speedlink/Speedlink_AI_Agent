# app.py
from fastapi import FastAPI
from pydantic import BaseModel
import chromadb
import subprocess
import ollama

# Initialize FastAPI
app = FastAPI(title="Company Assistant RAG API")

# ---- FIX HERE ----
# Use same DB path and collection name as index_data.py
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


client = chromadb.PersistentClient(path="./company_db")
collection = client.get_or_create_collection(
    name="company_info",
    embedding_function=OllamaEmbeddingFunction()
)
# -------------------

class Question(BaseModel):
    query: str

@app.get("/")
def root():
    return {"message": "Company Assistant API is running 🚀"}

@app.post("/ask")
async def ask_question(q: Question):
    results = collection.query(
        query_texts=[q.query],
        n_results=3
    )
    docs = results.get("documents", [[]])[0]
    context = "\n\n".join(docs)

    prompt = f"""
You are Speedsoft's internal company assistant.

Use the context below to answer the question as clearly and concisely as possible. 
Do not copy the context word-for-word — instead, summarize and explain in natural sentences. 
If the answer is not in the context, say: "I don’t know based on the available information."

Context:
{context}

Question:
{q.query}

Answer:
"""


    process = subprocess.Popen(
        ["ollama", "run", "llama3.1"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    output, _ = process.communicate(prompt)

    return {
        "question": q.query,
        "context_used": docs,   # 👈 for debugging
        "answer": output.strip()
    }


# app.py (add this at the end of your file)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",  # makes it accessible over your network/VM
        port=8000,
        reload=True      # auto-reload on code changes (development mode)
    )
