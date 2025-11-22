import os
from dotenv import load_dotenv

load_dotenv()

# Google Sheets / Docs config
GOOGLE_SERVICE_ACCOUNT = os.getenv("GOOGLE_SERVICE_ACCOUNT", "service_account.json")

# Vector DB path
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./vector_store")

# Default embedding + LLM models
EMBEDDING_MODEL = "deepseek-r1:7b"
LLM_MODEL = "deepseek-r1:7b"
