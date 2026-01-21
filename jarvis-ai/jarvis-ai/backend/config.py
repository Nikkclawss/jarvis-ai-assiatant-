import os
from dotenv import load_dotenv
load_dotenv()

PINECONE_API_KEY = os.getenv("pcsk_3xKoj2_FdLqCuMFfufCDAEUQ9TW3xAMSTrq5zYDRahjXyb7CWtjB9KXMs18LTsKAXAciJP")
PINECONE_INDEX = "jarvis-index"
LLM_MODEL = "llama3"
