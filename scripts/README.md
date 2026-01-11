# RAG Index Management Scripts

Эти скрипты реализуют полный цикл работы с векторной базой знаний для RAG-системы (Retrieval-Augmented Generation) на базе LangChain и ChromaDB.

## Скрипты и их назначение
### 1. Первоначальное создание индекса
**Файл скрипта**: `build_index.py`

**Что делает**:
- Загружает документы из папки ../knowledge_base/ (поддержка .md и .pdf)
- Разбивает текст на чанки размером 500 символов с перекрытием 50 символов
- Создает эмбеддинги с помощью sentence-transformers/all-MiniLM-L6-v2
- Сохраняет полный индекс в ../chroma_db

**Запуск**:

```bash
python build_index.py
```

**Предварительные требования**:
- Папка ../knowledge_base/ с файлами .md/.pdf
- Установленные зависимости: langchain, langchain-community, langchain-huggingface, chromadb, sentence-transformers

**Вывод**: Создает {N} чанков из {M} документов, сохраняет в ../chroma_db

### 2. Тестирование поиска
**Файл скрипта**: `test_search.py` 

**Что делает**:
- Загружает готовый индекс из ../chroma_db
- Выполняет семантический поиск по 3 примерам запросов
- Показывает топ-3 релевантных чанка с источником для каждого запроса

**Запуск**:

```bash
python test_search.py
```

**Предварительные требования**:
- Существующий индекс в ../chroma_db (создан build_index.py)

**Пример вывода**:

```text
Запрос: "Who was Marcus James Thornfield?"
1. [текст чанка]... [Источник: document.md, Chunk ID: 1]
```

### 3. Инкрементальное обновление индекса
**Файл скрипта**: `update_index.py` 

**Что делает**:
- Автоматически сканирует ../docs/incoming/ на новые/измененные файлы
- Вычисляет MD5-хеш для отслеживания изменений
- Добавляет только новые чанки в существующий индекс (без пересоздания)
- Перемещает обработанные файлы в ../docs/processed/
- Полное структурированное логирование + JSON статистика

**Параметры чанкинга**: 500 символов с перекрытием 50 символов

**Запуск**:

```bash
python update_index.py
# или как скрипт
chmod +x update_index.py
./update_index.py
```

**Предварительные требования**:

```text
../docs/incoming/     ← класть новые файлы сюда (.md, .txt, .pdf)
../docs/processed/    ← автоматически (не трогать)
../chroma_db/         ← существующий индекс
```

**Логи**: index_update.log + file_hashes.json

**Пример вывода**:

```text
2026-01-11 16:50:00 | INFO | 📁 Найдено файлов: 2
2026-01-11 16:50:01 | INFO | 🔄 Обработка: new_doc.pdf → 15 чанков
2026-01-11 16:50:02 | INFO | ✅ Обновление завершено за 2.3с
```

**Архитектура workflow**
```text
1. build_index.py    → первый запуск
   knowledge_base/   → chroma_db/

2. test_search.py    → проверка качества поиска

3. update_index.py   → регулярное обновление
   docs/incoming/    → docs/processed/ + chroma_db/
   Структура проекта
   text
   project/
   ├── knowledge_base/     # Исходные документы (первый запуск)
   ├── docs/
   │   ├── incoming/       # Новые файлы для обновления
   │   └── processed/      # Архив обработанных
   ├── chroma_db/          # 🗄️ Векторная БД (результат)
   ├── *.py               # Скрипты
   ├── index_update.log   # Логи обновлений
   └── file_hashes.json   # Хеши для дедупликации
```
   requirements.txt (рекомендуется)
```text
   langchain-chroma
   langchain-huggingface
   langchain-community
   chromadb
   sentence-transformers
   pypdf
```   
**Настройка cron для регулярного обновления индекса в 6:00**:

```bash
# Ежедневно в 6:00 проверять новые документы и добавить в индекс
0 6 * * * cd /path/to/scripts/dir && python update_index.py
```

