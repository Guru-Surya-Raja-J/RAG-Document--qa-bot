import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DB_PATH = "./db"
DATA_PATH = "./data"
COLLECTION_NAME = "document_knowledge_base"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K = 3
EMBEDDING_MODEL = "gemini-embedding-001"
GENERATION_MODEL = "gemini-2.5-flash-lite"