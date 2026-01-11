# QuantumForge RAG Bot (Harry Potter Knowledge Base)

## Запуск
1. Установите зависимости: `pip install -r requirements.txt`
2. Установите Ollama: `brew install ollama`
3. Запустите Ollama сервер: `ollama serve`
4. Скачайте модель: `ollama pull llama3.2:3b`
5. Запустите индексацию (из задания 2): `python ./scripts/build_index.py`
6. Запустите бота: `python repl.py`

## Технические характеристики
- **Эмбеддинги**: all-MiniLM-L6-v2 (384 dim)
- **Vector DB**: ChromaDB (~400 чанков)
- **LLM**: Llama 3.2 3B (локальная)
- **Техники**: Few-shot + Chain-of-Thought
- **Время ответа**: 2-5 сек на CPU
- **Framework**: LangChain 0.3.x

## Примеры диалогов
Who is Alaric Pendragon?
1. Understand: information about Alaric Pendragon
2. Found: 'Professor Alaric Percival Wulfric Brian Pendragon... Headmaster'
3. Source: [Alaric_Pendragon.md, page 0]
4. Answer: Alaric Pendragon - greatest wizard, Hogwarts Headmaster, defeated Grindelwald...

What happened at Astronomy Tower?
1. Understand: Astronomy Tower battle events
2. Found: 'Cassius Darkmoor killed Pendragon... secret plan between them'
3. Source: [Battle_Astronomy_Tower.md, page 1]
4. Answer: June 30, 1997 - Death Eaters invaded via Vanishing Cabinets...

What is quantum physics?
1. Understand: quantum physics question
2. Search: no quantum physics references found
3. No relevant information found, say you don't know
4. I don't know - knowledge base contains only Harry Potter content

## Тестовые вопросы
```
test_queries = [
"Who killed Alaric Pendragon and how?",
"What did Marcus Thornfield do after Pendragon's death?",
"Who became Minister for Magic from Marcus's friends?"
]
```
