"""FastAPI Backend for Jarvis AI Assistant"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional

from app.llm_service import llm_service
from app.vector_store import vector_store

# Get the project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Initialize FastAPI app
app = FastAPI(
    title="Jarvis AI Assistant",
    description="Personal AI Assistant powered by Gemini/Ollama and ChromaDB",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str
    use_knowledge_base: bool = True


class ChatResponse(BaseModel):
    response: str
    context_used: bool
    retrieved_documents: List[dict]


class KnowledgeRequest(BaseModel):
    documents: List[str]
    metadatas: Optional[List[dict]] = None


class StatusResponse(BaseModel):
    provider: str
    model: str
    status: str
    message: str
    knowledge_base_count: int
    available_models: Optional[List[str]] = None


# API Endpoints
@app.get("/api/status", response_model=StatusResponse)
async def get_status():
    """Get system status including LLM provider and knowledge base"""
    llm_status = llm_service.check_status()
    kb_docs = vector_store.get_all_documents()
    kb_count = len(kb_docs.get("ids", [])) if kb_docs else 0

    return StatusResponse(
        provider=llm_status.get("provider", "unknown"),
        model=llm_status.get("model", ""),
        status=llm_status.get("status", "unknown"),
        message=llm_status.get("message", ""),
        knowledge_base_count=kb_count,
        available_models=llm_status.get("available_models")
    )


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to Jarvis and get a response"""
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    result = llm_service.generate_response(
        user_query=request.message,
        use_knowledge_base=request.use_knowledge_base
    )

    return ChatResponse(
        response=result["response"],
        context_used=result["context_used"],
        retrieved_documents=result["retrieved_documents"]
    )


@app.post("/api/knowledge/add")
async def add_knowledge(request: KnowledgeRequest):
    """Add documents to the knowledge base"""
    if not request.documents:
        raise HTTPException(status_code=400, detail="Documents list cannot be empty")

    success = vector_store.add_knowledge(
        documents=request.documents,
        metadatas=request.metadatas
    )

    if success:
        return {"message": f"Successfully added {len(request.documents)} documents to knowledge base"}
    else:
        raise HTTPException(status_code=500, detail="Failed to add documents to knowledge base")


@app.get("/api/knowledge")
async def get_knowledge():
    """Get all documents from knowledge base"""
    docs = vector_store.get_all_documents()
    return {
        "count": len(docs.get("ids", [])),
        "documents": docs
    }


@app.delete("/api/knowledge/{doc_id}")
async def delete_knowledge(doc_id: str):
    """Delete a document from knowledge base"""
    success = vector_store.delete_document(doc_id)
    if success:
        return {"message": f"Successfully deleted document {doc_id}"}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete document")


@app.delete("/api/knowledge")
async def clear_knowledge():
    """Clear all documents from knowledge base"""
    success = vector_store.clear_all()
    if success:
        return {"message": "Successfully cleared knowledge base"}
    else:
        raise HTTPException(status_code=500, detail="Failed to clear knowledge base")


@app.post("/api/knowledge/search")
async def search_knowledge(query: str, n_results: int = 3):
    """Search the knowledge base"""
    results = vector_store.search(query, n_results)
    return {"results": results}


# Serve frontend static files
@app.get("/")
async def serve_index():
    """Serve the main frontend page"""
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/{filename}")
async def serve_static(filename: str):
    """Serve static files (css, js)"""
    file_path = os.path.join(FRONTEND_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")


if __name__ == "__main__":
    import uvicorn
    from app.config import API_HOST, API_PORT

    uvicorn.run(app, host=API_HOST, port=API_PORT)
