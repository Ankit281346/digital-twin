import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # LLM Settings
    # Recommended Groq Models: 
    # - llama-3.3-70b-versatile (Best quality)
    # - llama-3.1-8b-instant (Fastest, lower limits)
    # - mixtral-8x7b-32768
    # - qwen/qwen3-32b (Balanced)
    LLM_MODEL = os.getenv("LLM_MODEL", "qwen/qwen3-32b")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    # RAG Settings
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    CHROMA_PATH = os.path.join(DATA_DIR, 'chroma_db')
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

    # App Settings
    DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

config = Config()
