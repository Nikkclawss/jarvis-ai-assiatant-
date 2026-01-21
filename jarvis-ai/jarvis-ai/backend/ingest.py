from vector_service import add_document

documents = [
    "Diligent is a SaaS governance platform.",
    "AI assistants can enhance enterprise workflows.",
    "Vector databases enable semantic search."
]

for doc in documents:
    add_document(doc)

print("Ingestion complete!")
