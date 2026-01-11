import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = Chroma(persist_directory="../chroma_db", embedding_function=embeddings)

# Примеры запросов (релевантны QuantumForge)
queries = [
    "Who was Marcus James Thornfield?",
    "When were Attack at Godric's Hollow?",
    "Who does Elena Blackwell married?"
]

for query in queries:
    results = db.similarity_search(query, k=3)
    print(f"\nЗапрос: {query}")
    for i, doc in enumerate(results, 1):
        print(f"{i}. {doc.page_content[:200]}... [Источник: {doc.metadata['source']}, Chunk ID: {i}]")
