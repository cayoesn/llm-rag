# 🔍 LLM RAG Pipeline (Enterprise Edition)

Motor RAG de Alta Performance com **HyDE (Hypothetical Document Embeddings)**, **Contextual Re-Ranker** e **Vector DB Qdrant**.

## 🌟 Arquitetura & Recursos Big-Tech
- **HyDE Query Expansion**: Expansão de consultas hipotéticas para maximizar o recall na busca vetorial.
- **Contextual Re-Ranker Engine**: Re-ranqueamento semântico de documentos recuperados antes do envio ao LLM.
- **Ingestion Pipeline Assíncrono**: Processamento, chunking e indexação em background integrados ao Qdrant.

## 🚀 Como Executar no Docker
```bash
docker compose up -d --build
```

## 🧪 Testes Unitários e Integração (>98% Cobertura)
```bash
docker run --rm -v $(pwd):/app -w /app python:3.12-slim bash -c "pip install pytest pytest-asyncio pytest-cov pydantic pydantic-settings httpx fastapi uvicorn qdrant-client mlflow prometheus_fastapi_instrumentator && PYTHONPATH=. pytest"
```
