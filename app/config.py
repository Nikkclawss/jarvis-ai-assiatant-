"""Configuration settings for Jarvis AI Assistant"""

import os
from dotenv import load_dotenv

load_dotenv()

# LLM Provider: "gemini" or "ollama"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")

# Gemini settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# Ollama settings (fallback)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")

# ChromaDB settings
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")
COLLECTION_NAME = "jarvis_knowledge"

# Embedding model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# API settings
API_HOST = "0.0.0.0"
API_PORT = 8000
