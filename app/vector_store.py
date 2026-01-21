"""Vector store module using ChromaDB for knowledge storage and retrieval"""

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
import os

from app.config import CHROMA_PERSIST_DIR, COLLECTION_NAME, EMBEDDING_MODEL


class VectorStore:
    """Handles storage and retrieval of knowledge using ChromaDB"""

    def __init__(self):
        # Ensure directory exists
        os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)

        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"description": "Jarvis AI knowledge base"}
        )

        # Initialize embedding model
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)

    def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for given texts"""
        embeddings = self.embedding_model.encode(texts)
        return embeddings.tolist()

    def add_knowledge(self, documents: List[str], metadatas: Optional[List[Dict]] = None, ids: Optional[List[str]] = None) -> bool:
        """Add documents to the knowledge base"""
        try:
            if ids is None:
                # Generate unique IDs
                existing_count = self.collection.count()
                ids = [f"doc_{existing_count + i}" for i in range(len(documents))]

            if metadatas is None:
                metadatas = [{"source": "user_input"} for _ in documents]

            # Generate embeddings
            embeddings = self._get_embeddings(documents)

            # Add to collection
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            return True
        except Exception as e:
            print(f"Error adding knowledge: {e}")
            return False

    def search(self, query: str, n_results: int = 3) -> List[Dict]:
        """Search for relevant documents based on query"""
        try:
            # Generate query embedding
            query_embedding = self._get_embeddings([query])[0]

            # Search in collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )

            # Format results
            formatted_results = []
            if results and results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        "document": doc,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "distance": results['distances'][0][i] if results['distances'] else None
                    })

            return formatted_results
        except Exception as e:
            print(f"Error searching: {e}")
            return []

    def get_all_documents(self) -> Dict:
        """Retrieve all documents from the knowledge base"""
        try:
            return self.collection.get()
        except Exception as e:
            print(f"Error retrieving documents: {e}")
            return {}

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document by ID"""
        try:
            self.collection.delete(ids=[doc_id])
            return True
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False

    def clear_all(self) -> bool:
        """Clear all documents from the knowledge base"""
        try:
            # Delete and recreate collection
            self.client.delete_collection(COLLECTION_NAME)
            self.collection = self.client.get_or_create_collection(
                name=COLLECTION_NAME,
                metadata={"description": "Jarvis AI knowledge base"}
            )
            return True
        except Exception as e:
            print(f"Error clearing knowledge base: {e}")
            return False


# Singleton instance
vector_store = VectorStore()
