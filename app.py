# app.py — RHODA v3 + TELEGRAM PLAYGROUND (fast & perfect)
from fastapi import FastAPI, Request
from pydantic import BaseModel
import ollama
import chromadb
import os
import requests
from typing import List
from dotenv import load_dotenv   # ← ADD THIS LINE

load_dotenv()   # ← ADD THIS LINE — THIS IS THE FIX

# === Embedding Function (Chroma 0.5+) ===
from chromadb.utils.embedding_functions import EmbeddingFunction

class OllamaEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: List[str]) -> List[List[float]]:
        return [ollama.embeddings(model="nomic-embed-text:latest", prompt=t)["embedding"] for t in input]
    def name(self) -> str:
        return "ollama-nomic"

app = FastAPI(title="RHODA — Speedlink Telegram Playground")

# Chroma
client = chromadb.PersistentClient(path="./company_db")
collection = client.get_or_create_collection(
    name="speedlink_knowledge",
    embedding_function=OllamaEmbeddingFunction(),
    metadata={"hnsw:space": "cosine"}
)

# === Fast model (you already pulled this) ===
LLM_MODEL = "llama3.2:3b-instruct-q4_0"   # <3 sec response

# === Human handover keywords ===
HANDOVER_KEYWORDS = ["human", "agent", "person", "support", "operator", "live", "talk to someone"]

SYSTEM_PROMPT = """You are RHODA, the official digital assistant of Speedlink Nigeria.
Speak in first person using "we", "our", "us". Never mention Speedsoft.
Be confident, professional, and proud to represent Speedlink.
Use ONLY the context below. If unsure, say: "Let me connect you to a team member."""

def get_answer(question: str) -> dict:
    if any(k in question.lower() for k in HANDOVER_KEYWORDS):
        return {"answer": "Connecting you to a Speedlink team member right now...", "handover": True}

    results = collection.query(query_texts=[question], n_results=8)
    context = "\n\n".join(results["documents"][0])

    prompt = f"""{SYSTEM_PROMPT}

Context:
{context}

Question: {question}

Answer (first-person, confident, max 3 sentences):"""

    resp = ollama.generate(
        model=LLM_MODEL,
        prompt=prompt,
        options={"num_predict": 120, "temperature": 0.3}
    )
    return {"answer": resp["response"].strip(), "handover": False}

@app.get("/")
def home():
    return {"status": "RHODA Telegram Playground Ready", "model": LLM_MODEL}

@app.post("/ask")
def ask(q: BaseModel):
    query: str = q.dict().get("query", "")
    return get_answer(query)

# ==================== TELEGRAM WEBHOOK ====================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # ← SET THIS IN .env
if not TELEGRAM_TOKEN:
    print("ERROR: TELEGRAM_TOKEN not found in .env file!")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

@app.post("/telegram-webhook")
async def telegram_webhook(request: Request):
    update = await request.json()
    print("TELEGRAM UPDATE RECEIVED:", update)   # ← you will see this in logs
    if "message" not in update:
        return {"ok": True}

    chat_id = update["message"]["chat"]["id"]
    text = update["message"].get("text", "").strip()
    if not text:
        return {"ok": True}

    result = get_answer(text)
    reply = result["answer"]
    print(f"Sending reply to {chat_id}: {reply}")   # ← this confirms it sends

    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={"chat_id": chat_id, "text": reply}
    )
    return {"ok": True}

# Set webhook automatically on startup
# @app.on_event("startup")
# async def set_webhook():
#     if TELEGRAM_TOKEN:
#         url = f"https://your-domain.com/telegram-webhook"  # ← CHANGE THIS
#         requests.post(f"{TELEGRAM_API}/setWebhook", json={"url": url})
#         print(f"Telegram webhook set to {url}")









######


# #####  V1 with whatsapp, ready for production Tests #########


######


# # app.py — RHODA v3 Final Production Version (Speedlink Native)
# from fastapi import FastAPI, Request, requests
# from pydantic import BaseModel
# import ollama
# import chromadb
# import os
# from typing import List
# # === CORRECT EMBEDDING FUNCTION (Chroma 0.5+ compliant) ===
# from chromadb.utils.embedding_functions import EmbeddingFunction

# app = FastAPI(title="RHODA — Speedlink Internal & Customer Assistant")

# # === Clean Ollama embedding function (official client) ===
# class OllamaEmbeddingFunction(EmbeddingFunction):
#     def __call__(self, input: List[str]) -> List[List[float]]:
#         return [
#             ollama.embeddings(model="nomic-embed-text:latest", prompt=text)["embedding"]
#             for text in input
#         ]
    
#     def name(self) -> str:
#         return "ollama-nomic-embed"
    

# # === Chroma DB ===
# client = chromadb.PersistentClient(path="./company_db")
# collection = client.get_or_create_collection(
#     name="speedlink_knowledge",
#     embedding_function=OllamaEmbeddingFunction(),
#     metadata={"hnsw:space": "cosine"}
# )

# # === Request Models ===
# class Query(BaseModel):
#     query: str

# class WebhookMessage(BaseModel):
#     entry: list

# # === Human handover keywords ===
# HANDOVER_KEYWORDS = ["human", "agent", "person", "support", "operator", "live", "talk to someone"]

# # === SYSTEM PROMPT — THIS IS THE KEY TO FIRST-PERSON & NO HALLUCINATION ===
# SYSTEM_PROMPT = """You are RHODA, the official digital assistant of Speedlink Nigeria.
# You speak ONLY in first person: use "we", "our", "us" when referring to Speedlink.
# Never say "Speedsoft" — that company does not exist.
# Never say "I think" or "it appears" — be confident and direct.
# Answer using ONLY the context below. If the answer is not there, say:
# "I don't have that information right now. Let me connect you to a team member who can help."

# You are helpful, professional, and proud to represent Speedlink."""

# def get_answer(question: str) -> dict:
#     # Trigger handover early
#     if any(word in question.lower() for word in HANDOVER_KEYWORDS):
#         return {
#             "answer": "One moment please — connecting you to a Speedlink team member right away.",
#             "handover": True
#         }

#     # Retrieve top 8 chunks
#     results = collection.query(query_texts=[question], n_results=8)
#     docs = results["documents"][0]
#     context = "\n\n".join(docs)

#     full_prompt = f"""{SYSTEM_PROMPT}

# Context:
# {context}

# Question: {question}

# Answer (first-person, confident, professional):"""

#     try:
#         # resp = ollama.generate(model="llama3.1:8b", prompt=full_prompt)  # or 8b
#         # resp = ollama.generate(model="llama3.1:8b-instruct-q4_0", prompt=full_prompt)
#         resp = ollama.generate(model="llama3.2:3b-instruct-q4_0", prompt=full_prompt, options={"num_predict": 128, "temperature":0.3})
#         answer = resp["response"].strip()
#     except Exception as e:
#         answer = "Sorry, I'm having trouble connecting to my brain right now. Please try again in a moment."

#     return {"answer": answer, "handover": False}

# # === API Endpoints ===
# @app.get("/")
# def home():
#     return {"status": "RHODA v3 live", "company": "Speedlink Nigeria", "assistant": "Real-time Human-handover Omniscient Digital Assistant"}

# @app.post("/ask")
# def ask(q: Query):
#     return get_answer(q.query)

# # === WhatsApp Webhook (cleaned & working) ===
# @app.post("/webhook")
# async def webhook(request: Request):
#     data = await request.json()
#     for entry in data.get("entry", []):
#         for change in entry.get("changes", []):
#             for message in change.get("value", {}).get("messages", []):
#                 phone = message["from"]
#                 text = message.get("text", {}).get("body", "").strip()
#                 if not text:
#                     continue

#                 result = get_answer(text)
#                 reply = result["answer"]

#                 # Send reply via Meta API
#                 requests.post(
#                     f"https://graph.facebook.com/v20.0/{os.getenv('WHATSAPP_PHONE_NUMBER_ID')}/messages",
#                     headers={"Authorization": f"Bearer {os.getenv('WHATSAPP_TOKEN')}"},
#                     json={
#                         "messaging_product": "whatsapp",
#                         "to": phone,
#                         "type": "text",
#                         "text": {"body": reply}
#                     }
#                 )
#     return {"status": "ok"}

# @app.get("/webhook")
# def verify(request: Request):
#     if request.query_params.get("hub.mode") == "subscribe" and request.query_params.get("hub.verify_token") == os.getenv("WHATSAPP_VERIFY_TOKEN"):
#         return request.query_params.get("hub.challenge")
#     return "Forbidden", 403






