from pinecone import Pinecone, ServerlessSpec
from config import PINECONE_API_KEY, PINECONE_INDEX
import hashlib

pc = Pinecone(api_key=PINECONE_API_KEY)

if PINECONE_INDEX not in pc.list_indexes().names():
    pc.create_index(
        name=PINECONE_INDEX,
        dimension=768,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

index = pc.Index(PINECONE_INDEX)

def embed_text(text: str):
    import requests
    response = requests.post(
        "http://localhost:11434/api/embeddings",
        json={"model": "llama3", "prompt": text}
    )
    return response.json()["embedding"]

def add_document(text: str):
    vector = embed_text(text)
    doc_id = hashlib.md5(text.encode()).hexdigest()
    index.upsert([{"id": doc_id, "values": vector, "metadata": {"text": text}}])

def search(query: str):
    vector = embed_text(query)
    result = index.query(vector=vector, top_k=3, include_metadata=True)
    return [match["metadata"]["text"] for match in result["matches"]]
