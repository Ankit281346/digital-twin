import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # LLM Settings
    # Groq Model Rate Limits (free tier):
    # - llama-3.1-8b-instant:    30,000 TPM ← best for agents (high limit, fast)
    # - llama-3.3-70b-versatile:  6,000 TPM (hits rate limit on web search)
    # - meta-llama/llama-4-scout-17b-16e-instruct: 30,000 TPM (newer, capable)
    LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    # RAG Settings
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    CHROMA_PATH = os.path.join(DATA_DIR, 'chroma_db')
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

    # App Settings
    DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

config = Config()
