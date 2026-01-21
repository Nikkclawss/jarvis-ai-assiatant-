# 🤖 Jarvis AI Assistant

A personal AI assistant powered by a self-hosted LLM (LLaMA via Ollama) with knowledge storage using ChromaDB vector database and a Streamlit chatbot UI.

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Streamlit UI  │────▶│  FastAPI Server │────▶│  Ollama/LLaMA   │
│   (Frontend)    │     │   (Backend)     │     │     (LLM)       │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │    ChromaDB     │
                        │ (Vector Store)  │
                        └─────────────────┘
```

## ✨ Features

- **Conversational AI**: Natural language chat powered by LLaMA
- **Knowledge Base**: Store and retrieve information using ChromaDB vector database
- **Context-Aware Responses**: Uses RAG (Retrieval Augmented Generation) for relevant answers
- **Modern UI**: Clean Streamlit interface for easy interaction
- **RESTful API**: FastAPI backend with full CRUD operations

## 🚀 Quick Start

### Prerequisites

1. **Python 3.9+**
2. **Ollama** - Install from [ollama.ai](https://ollama.ai)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/jarvis-ai-assistant.git
   cd jarvis-ai-assistant
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup Ollama and download LLaMA**
   ```bash
   # Start Ollama service
   ollama serve

   # In another terminal, pull the LLaMA model
   ollama pull llama2
   ```

5. **Configure environment** (optional)
   ```bash
   cp .env.example .env
   # Edit .env if needed
   ```

### Running the Application

1. **Start the FastAPI backend** (Terminal 1)
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start the Streamlit UI** (Terminal 2)
   ```bash
   streamlit run streamlit_app.py
   ```

3. **Open your browser** at `http://localhost:8501`

## 📖 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome message |
| GET | `/api/status` | System status |
| POST | `/api/chat` | Send message to Jarvis |
| POST | `/api/knowledge/add` | Add documents to knowledge base |
| GET | `/api/knowledge` | Get all knowledge |
| DELETE | `/api/knowledge/{id}` | Delete specific document |
| DELETE | `/api/knowledge` | Clear all knowledge |
| POST | `/api/knowledge/search` | Search knowledge base |

## 🛠️ Tech Stack

- **LLM**: LLaMA 2 (via Ollama)
- **Vector Database**: ChromaDB
- **Backend**: FastAPI
- **Frontend**: Streamlit
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)

## 📁 Project Structure

```
jarvis-ai-assistant/
├── app/
│   ├── __init__.py
│   ├── config.py          # Configuration settings
│   ├── main.py            # FastAPI application
│   ├── llm_service.py     # LLM interaction layer
│   └── vector_store.py    # ChromaDB operations
├── data/                  # ChromaDB persistence (auto-created)
├── streamlit_app.py       # Streamlit UI
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── .gitignore
└── README.md
```

## 💡 Usage Examples

### Adding Knowledge via UI
1. Go to "Knowledge Base" tab
2. Enter information in the text area
3. Click "Add Knowledge"

### Adding Knowledge via API
```bash
curl -X POST http://localhost:8000/api/knowledge/add \
  -H "Content-Type: application/json" \
  -d '{"documents": ["Your company info here", "More facts here"]}'
```

### Chatting via API
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What do you know about our company?"}'
```

## 🔧 Configuration

Edit `.env` file to customize:

| Variable | Default | Description |
|----------|---------|-------------|
| OLLAMA_BASE_URL | http://localhost:11434 | Ollama API URL |
| OLLAMA_MODEL | llama2 | Model to use |
| CHROMA_PERSIST_DIR | ./data/chroma_db | ChromaDB storage path |

## 📝 License

MIT License

## 🤝 Contributing

Pull requests are welcome!

---

Built with ❤️ for the AI Assistant Programming Assignment
