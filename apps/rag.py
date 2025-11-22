import chromadb
import ollama
from apps.config import settings

# Set Ollama API base if using API client
# ollama.set_base_url(settings.OLLAMA_BASE_URL)

def query_with_context(query: str, top_k: int = 3):
    client = chromadb.PersistentClient(path=settings.VECTOR_DB_PATH)
    coll = client.get_or_create_collection(name=settings.COLLECTION_NAME,
                                           embedding_function=lambda text: ollama.embeddings(
                                               model="nomic-embed-text", prompt=text)["embedding"])

    results = coll.query(query_texts=[query], n_results=top_k)
    docs = results.get("documents", [[]])[0]
    context = "\n\n".join(docs)

    prompt = f"You are an internal assistant. Use ONLY this context:\n\n{context}\n\nQuestion: {query}"
    resp = ollama.chat(model="deepseek-r1:1.5b", messages=[{"role":"user", "content":prompt}])
    return resp["message"]["content"]




