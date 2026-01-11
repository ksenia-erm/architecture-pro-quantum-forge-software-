FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/chroma_db /app/docs/{incoming,processed} /app/knowledge_base

# Открываем порт для Telegram бота
EXPOSE 8080

# Запуск Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

CMD ["/bin/bash", "-c", "\
    ollama serve & \
    sleep 5 && \
    ollama pull llama3.2:3b && \
    python rag_bot.py"]
