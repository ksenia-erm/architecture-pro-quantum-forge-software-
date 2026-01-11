import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document


# Шаг 1: Загрузка документов
def load_docs(folder="../knowledge_base"):
    docs = []
    for file in os.listdir(folder):
        filepath = os.path.join(folder, file)
        if file.endswith('.md'):
            loader = TextLoader(filepath, encoding='utf-8')
        elif file.endswith('.pdf'):
            loader = PyPDFLoader(filepath)
        else:
            continue
        raw_docs = loader.load()
        # Добавляем метаданные
        for doc in raw_docs:
            doc.metadata.update({
                'source': file,
                'page': getattr(doc.metadata, 'page', 0)
            })
        docs.extend(raw_docs)
    return docs

# Шаг 2: Чанкинг (300-500 токенов ~100-300 слов, overlap 50 символов)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    length_function=len,
    separators=["\n\n", "\n", " ", ""]
)

# Шаг 3: Эмбеддинги
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Основной процесс
if __name__ == "__main__":
    docs = load_docs()
    chunks = splitter.split_documents(docs)
    
    print(f"Создано {len(chunks)} чанков из {len(docs)} документов.")
    
    # Шаг 4: Создание ChromaDB индекса
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="../chroma_db"
    )
    
    print("Индекс сохранен в ../chroma_db")
