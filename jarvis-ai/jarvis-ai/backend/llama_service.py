import requests
from config import LLM_MODEL

def generate_llama(prompt: str):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": LLM_MODEL, "prompt": prompt}
    )
    return response.json()["response"]
