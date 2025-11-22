from fastapi import FastAPI
from pydantic import BaseModel
from apps import rag

app = FastAPI(title="Company AI Assistant")

class QueryRequest(BaseModel):
    question: str

@app.post("/ask")
def ask_question(req: QueryRequest):
    answer = rag.query_company_data(req.question)
    return {"question": req.question, "answer": answer}

@app.get("/")
def root():
    return {"message": "✅ Company AI Assistant is running!"}
