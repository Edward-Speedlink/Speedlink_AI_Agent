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


def query_with_context(query: str, top_k: int = 3):
    results = collection.query(query_texts=[query], n_results=top_k)
    docs = results.get("documents", [[]])[0]
    context = "\n\n".join(docs)

    prompt = f"""
    You are Speedsoft's internal assistant.
    Use ONLY the context below to answer the question.

    Context:
    {context}

    Question: {query}
    """

    response = ollama.chat(
        model="deepseek-r1:1.5b",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"]

# Example test queries
queries = [
    "Where is Speedsoft based?",
    "What does Speedsoft specialize in?",
    "who is the founder of speedlink? and how much is their staff paid on average?"
]

with open("rag_output.txt", "w") as f:
    for q in queries:
        answer = query_with_context(q)
        f.write(f"Q: {q}\nA: {answer}\n\n")

print("✅ Answers written to rag_output.txt")
