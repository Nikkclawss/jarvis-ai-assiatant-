"""LLM Service module for interacting with Gemini or Ollama"""

import requests
from typing import Optional, List, Dict

from app.config import (
    LLM_PROVIDER,
    GEMINI_API_KEY, GEMINI_MODEL,
    OLLAMA_BASE_URL, OLLAMA_MODEL
)
from app.vector_store import vector_store


class LLMService:
    """Handles communication with Gemini or Ollama LLM"""

    def __init__(self):
        self.provider = LLM_PROVIDER
        # Gemini settings
        self.gemini_api_key = GEMINI_API_KEY
        self.gemini_model = GEMINI_MODEL
        # Ollama settings
        self.ollama_base_url = OLLAMA_BASE_URL
        self.ollama_model = OLLAMA_MODEL

    def _call_gemini(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Make a request to Google Gemini API"""
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.gemini_model}:generateContent?key={self.gemini_api_key}"

            # Build the full prompt with system instruction
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            # Simple payload structure for Gemini
            payload = {
                "contents": [{
                    "parts": [{"text": full_prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 2048
                }
            }

            response = requests.post(url, json=payload, timeout=120)

            # Check for error response
            if response.status_code != 200:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get("message", response.text)
                return f"Error from Gemini API: {error_msg}"

            result = response.json()
            candidates = result.get("candidates", [])
            if candidates:
                content = candidates[0].get("content", {})
                parts = content.get("parts", [])
                if parts:
                    return parts[0].get("text", "I apologize, but I couldn't generate a response.")

            return "I apologize, but I couldn't generate a response."

        except requests.exceptions.ConnectionError:
            return "Error: Cannot connect to Gemini API. Please check your internet connection."
        except requests.exceptions.Timeout:
            return "Error: Request timed out."
        except Exception as e:
            return f"Error communicating with Gemini: {str(e)}"

    def _call_ollama(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Make a request to Ollama API"""
        try:
            url = f"{self.ollama_base_url}/api/generate"

            payload = {
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False
            }

            if system_prompt:
                payload["system"] = system_prompt

            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()

            result = response.json()
            return result.get("response", "I apologize, but I couldn't generate a response.")

        except requests.exceptions.ConnectionError:
            return "Error: Cannot connect to Ollama. Please ensure Ollama is running (run 'ollama serve' in terminal)."
        except requests.exceptions.Timeout:
            return "Error: Request timed out. The model might be loading or the query is too complex."
        except Exception as e:
            return f"Error communicating with LLM: {str(e)}"

    def _call_llm(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Route to appropriate LLM provider"""
        if self.provider == "gemini" and self.gemini_api_key:
            return self._call_gemini(prompt, system_prompt)
        else:
            return self._call_ollama(prompt, system_prompt)

    def generate_response(self, user_query: str, use_knowledge_base: bool = True) -> Dict:
        """Generate a response to user query, optionally using knowledge base context"""

        context = ""
        retrieved_docs = []

        # Retrieve relevant context from knowledge base
        if use_knowledge_base:
            search_results = vector_store.search(user_query, n_results=3)
            if search_results:
                retrieved_docs = search_results
                context_parts = [result["document"] for result in search_results]
                context = "\n".join(context_parts)

        # Build the prompt
        system_prompt = """You are Jarvis, an intelligent personal AI assistant.
You are helpful, knowledgeable, and provide accurate information.
When context is provided, use it to give relevant and specific answers.
If you don't know something, admit it honestly."""

        if context:
            prompt = f"""Context from knowledge base:
{context}

User Question: {user_query}

Based on the context provided (if relevant) and your knowledge, please provide a helpful response."""
        else:
            prompt = f"""User Question: {user_query}

Please provide a helpful response."""

        # Generate response
        response = self._call_llm(prompt, system_prompt)

        return {
            "response": response,
            "context_used": bool(context),
            "retrieved_documents": retrieved_docs
        }

    def check_status(self) -> Dict:
        """Check LLM provider status"""
        if self.provider == "gemini" and self.gemini_api_key:
            # Test Gemini API
            try:
                test_response = self._call_gemini("Say 'OK' if you're working.")
                return {
                    "provider": "gemini",
                    "model": self.gemini_model,
                    "status": "connected" if "OK" in test_response or len(test_response) > 0 else "error",
                    "message": "Gemini API is working" if "Error" not in test_response else test_response
                }
            except Exception as e:
                return {
                    "provider": "gemini",
                    "model": self.gemini_model,
                    "status": "error",
                    "message": str(e)
                }
        else:
            # Check Ollama
            try:
                response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=5)
                response.raise_for_status()

                models = response.json().get("models", [])
                model_names = [m.get("name", "").split(":")[0] for m in models]

                return {
                    "provider": "ollama",
                    "model": self.ollama_model,
                    "status": "connected" if self.ollama_model in model_names else "model_not_found",
                    "available_models": model_names,
                    "message": "Ollama is running" if model_names else "No models installed"
                }
            except Exception as e:
                return {
                    "provider": "ollama",
                    "model": self.ollama_model,
                    "status": "error",
                    "message": str(e)
                }


# Singleton instance
llm_service = LLMService()
