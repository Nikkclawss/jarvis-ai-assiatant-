# Jarvis AI Assistant

## Install Ollama
https://ollama.com/download
ollama pull llama3

## Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

## Ingest documents
python ingest.py

## Frontend
cd frontend
npm install
npm run dev

Visit: http://localhost:5173
