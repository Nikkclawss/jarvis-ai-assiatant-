from fastapi import FastAPI
from llama_service import generate_llama
from vector_service import search
from pydantic import BaseModel

app = FastAPI()

class Query(BaseModel):
    message: str

@app.post("/chat")
def chat(req: Query):
    user_input = req.message
    context_docs = search(user_input)
    context = "\n\n".join(context_docs)

    final_prompt = f"""You are Jarvis, an AI assistant. Use this context:

CONTEXT:
{context}

USER QUESTION:
{user_input}
"""

    answer = generate_llama(final_prompt)
    return {"response": answer}
