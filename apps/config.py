import os
from dotenv import load_dotenv
# apps/config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    DATA_PATH: str = "data/"
    MODEL_NAME: str = "small-crm-model"
    CRM_MODEL: str = "crm-small-model"
    LLM_MODEL: str = "llama-large"
    USE_EMBEDDINGS: bool = True


settings = Settings()


load_dotenv()

# Google Sheets / Docs config
GOOGLE_SERVICE_ACCOUNT = os.getenv("GOOGLE_SERVICE_ACCOUNT", "service_account.json")

# Vector DB path
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./vector_store")

# Default embedding + LLM models
EMBEDDING_MODEL = "deepseek-r1:7b"
LLM_MODEL = "deepseek-r1:7b"
