FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir chromadb>=0.5.0 sentence-transformers>=3.0.0 openai>=1.0.0 \
    fastapi>=0.111.0 uvicorn>=0.30.0 pypdf>=4.0.0

COPY . .

EXPOSE 8000
CMD ["python", "main.py"]
