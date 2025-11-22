import gspread
from google.oauth2.service_account import Credentials
import chromadb
import ollama
from apps import config, utils

def ingest_google_sheet(sheet_url: str):
    creds = Credentials.from_service_account_file(
        config.GOOGLE_SERVICE_ACCOUNT,
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
    )
    gc = gspread.authorize(creds)
    sheet = gc.open_by_url(sheet_url).sheet1
    data = "\n".join([",".join(row) for row in sheet.get_all_values()])
    return data

def build_index(data: str):
    client = chromadb.PersistentClient(path=config.VECTOR_DB_PATH)
    collection = client.get_or_create_collection("company_data")

    chunks = utils.chunk_text(data)
    for i, chunk in enumerate(chunks):
        emb = ollama.embeddings(model=config.EMBEDDING_MODEL, prompt=chunk)["embedding"]
        collection.add(documents=[chunk], embeddings=[emb], ids=[str(i)])

    print(f"✅ Indexed {len(chunks)} chunks into ChromaDB")

if __name__ == "__main__":
    # Example: replace with your sheet
    SHEET_URL = "YOUR_GOOGLE_SHEET_URL"
    data = ingest_google_sheet(SHEET_URL)
    build_index(data)
