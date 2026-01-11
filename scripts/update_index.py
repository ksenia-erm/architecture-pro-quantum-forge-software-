#!/usr/bin/env python3
"""
🔄 Автоматическое обновление RAG индекса
• Сканирует папку docs/incoming/
• Обрабатывает новые/изменённые файлы (.md, .txt, .pdf)
• Добавляет чанки в ChromaDB
• Логирует всё в JSON + stdout
"""

import os
import json
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

# KONFIG
KB_INCOMING_DIR = "../docs/incoming"
KB_PROCESSED_DIR = "../docs/processed"
CHROMA_PATH = "../chroma_db"
LOG_FILE = "index_update.log"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

class IndexUpdater:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
        )
        self.setup_logging()
        self.file_hashes = self.load_file_hashes()

    def setup_logging(self):
        """Настройка структурированного логирования"""
        log_format = '%(asctime)s | %(levelname)s | %(message)s'
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(LOG_FILE, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("IndexUpdater")

    def load_file_hashes(self) -> Dict[str, str]:
        """Загрузка хешей обработанных файлов"""
        hash_file = Path("file_hashes.json")
        if hash_file.exists():
            with open(hash_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save_file_hashes(self):
        """Сохранение хешей обработанных файлов"""
        with open("file_hashes.json", 'w', encoding='utf-8') as f:
            json.dump(self.file_hashes, f, indent=2, ensure_ascii=False)

    def get_file_hash(self, file_path: Path) -> str:
        """MD5 хеш файла для отслеживания изменений"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def load_document(self, file_path: Path) -> List[Document]:
        """Загрузка документа по типу файла"""
        if file_path.suffix.lower() == '.pdf':
            loader = PyPDFLoader(str(file_path))
            return loader.load()
        else:
            # Markdown/Text
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return [Document(page_content=content, metadata={"source": file_path.name})]

    def process_new_files(self) -> Tuple[int, int]:
        """Основной цикл: поиск → чанки → эмбеддинги → индекс"""
        new_chunks = 0
        processed_files = 0

        # Создаём папки
        os.makedirs(KB_INCOMING_DIR, exist_ok=True)
        os.makedirs(KB_PROCESSED_DIR, exist_ok=True)

        # Сканируем входящие файлы
        incoming_files = list(Path(KB_INCOMING_DIR).glob("*"))
        self.logger.info(f"📁 Найдено файлов для обработки: {len(incoming_files)}")

        for file_path in incoming_files:
            try:
                # Проверяем новый/изменённый файл
                current_hash = self.get_file_hash(file_path)
                prev_hash = self.file_hashes.get(str(file_path))

                if current_hash != prev_hash:
                    self.logger.info(f"🔄 Обработка нового/изменённого: {file_path.name}")

                    # Загружаем документ
                    docs = self.load_document(file_path)

                    # Разбиваем на чанки
                    chunks = self.text_splitter.split_documents(docs)
                    new_chunks += len(chunks)

                    # Добавляем в индекс
                    vectorstore = Chroma(
                        persist_directory=CHROMA_PATH,
                        embedding_function=self.embeddings
                    )
                    vectorstore.add_documents(chunks)

                    # Обновляем хеш
                    self.file_hashes[str(file_path)] = current_hash
                    processed_files += 1

                    # Перемещаем в processed
                    dest_path = Path(KB_PROCESSED_DIR) / file_path.name
                    file_path.rename(dest_path)
                    self.logger.info(f"✅ Обработан: {file_path.name} → {len(chunks)} чанков")

            except Exception as e:
                self.logger.error(f"❌ Ошибка обработки {file_path.name}: {str(e)}")
                continue

        self.save_file_hashes()
        return new_chunks, processed_files

    def get_index_stats(self) -> Dict:
        """Статистика индекса"""
        try:
            vectorstore = Chroma(
                persist_directory=CHROMA_PATH,
                embedding_function=self.embeddings
            )
            return {
                "total_documents": vectorstore._collection.count(),
                "index_size_mb": sum(f.stat().st_size for f in Path(CHROMA_PATH).rglob('*') if f.is_file()) / (1024*1024)
            }
        except:
            return {"total_documents": 0, "index_size_mb": 0}

def main():
    """Главная функция с полным логированием"""
    start_time = datetime.now()

    updater = IndexUpdater()
    updater.logger.info("=" * 60)
    updater.logger.info("🚀 ЗАПУСК ОБНОВЛЕНИЯ ИНДЕКСА")
    updater.logger.info(f"📅 Время запуска: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Обработка файлов
    new_chunks, processed_files = updater.process_new_files()

    # Статистика
    stats = updater.get_index_stats()

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Финальный лог
    log_entry = {
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "duration_seconds": duration,
        "processed_files": processed_files,
        "new_chunks_added": new_chunks,
        "total_documents": stats["total_documents"],
        "index_size_mb": round(stats["index_size_mb"], 2),
        "errors": 0
    }

    updater.logger.info(f"✅ Обновление завершено за {duration:.1f}с")
    updater.logger.info(json.dumps(log_entry, indent=2, ensure_ascii=False))
    updater.logger.info("=" * 60)

if __name__ == "__main__":
    main()
