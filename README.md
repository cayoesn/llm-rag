# LLM-RAG Platform 🚀

LLM-RAG is an enterprise-grade, open-source RAG (Retrieval-Augmented Generation) and LLMOps platform designed for local-first execution. It provides a modular architecture for document ingestion, semantic search, and context-aware LLM generation, with a heavy focus on professional observability and asynchronous processing.

## 🏗️ Architecture

```mermaid
graph TD
    User((User)) --> API[FastAPI]
    API --> Redis[(Redis Queue)]
    Redis --> Worker[Async Worker]
    Worker --> Ingestion[Ingestion Pipeline]
    Ingestion --> Ollama[Ollama Embeddings]
    Ingestion --> Qdrant[(Qdrant Vector DB)]
    
    API --> RAG[RAG Service]
    RAG --> Qdrant
    RAG --> Ollama[Ollama LLM]
    
    API -.-> OTEL[OpenTelemetry/Jaeger]
    RAG -.-> Langfuse[Langfuse Tracing]
    RAG -.-> MLflow[MLflow Eval]
    API -.-> Prometheus[Prometheus Metrics]
    Prometheus --> Grafana[Grafana Dashboards]
```

## 🛠️ Stack Tecnológica

| Componente | Tecnologia | Propósito |
|------------|------------|-----------|
| **Backend** | FastAPI | High-performance API orchestration. |
| **Inference** | Ollama | Local serving of LLMs (Llama 3, Qwen) and Embeddings. |
| **Vector DB** | Qdrant | Semantic search and metadata filtering. |
| **Tracing** | Langfuse | Prompt management and detailed trace spans. |
| **Distributed Tracing** | Jaeger | OpenTelemetry-based system-wide tracing. |
| **Task Queue** | Redis | Asynchronous background ingestion. |
| **Metrics** | Prometheus | Real-time monitoring and alerting. |
| **Visualization** | Grafana | Infrastructure and LLM performance dashboards. |
| **Evaluation** | Ragas | Systematic evaluation of RAG faithfulness and relevance. |

## 🚀 Como Executar

### Pré-requisitos
- Docker & Docker Compose
- Python 3.11+ (para desenvolvimento local)

### Passo a Passo

1. **Clonar o repositório**
   ```bash
   git clone https://github.com/cayoesn/llm-rag
   cd llm-rag
   ```

2. **Configurar o Ambiente**
   ```bash
   cp .env.example .env
   # Edite o .env conforme necessário
   ```

3. **Subir os Containers**
   ```bash
   make up
   ```

4. **Ollama Setup**
   Após os containers subirem, baixe os modelos:
   ```bash
   docker exec -it llm_rag_ollama ollama pull llama3
   docker exec -it llm_rag_ollama ollama pull nomic-embed-text
   ```

## 📊 Observabilidade & LLMOps

A plataforma vem pré-configurada com as seguintes credenciais para facilitar o primeiro acesso:

| Serviço | URL | Usuário / Email | Senha |
|------------|-----|-----------------|-------|
| **Langfuse** | `http://localhost:3000` | `admin@llmrag.com` | `admin123` |
| **Grafana** | `http://localhost:3001` | `admin` | `admin` |
| **Jaeger** | `http://localhost:16686` | *(Sem Login)* | - |
| **MLflow** | `http://localhost:5000` | *(Sem Login)* | - |
| **Qdrant DB** | `http://localhost:6333/dashboard` | *(Sem Login)* | - |
| **FastAPI Docs** | `http://localhost:8000/docs` | *(Sem Login)* | - |

> **Nota:** As chaves de API do Langfuse já foram geradas automaticamente e injetadas no serviço da API. Você pode começar a testar e os traces aparecerão instantaneamente.

## 🧪 Conceitos de LLMOps Aplicados

- **Semantic Caching**: Redução de latência usando Redis para queries similares.
- **Async Ingestion**: Workers independentes para processamento de PDFs pesados.
- **Structured Logging**: Logs em JSON para fácil integração com ELK/Loki.
- **Retry Logic**: Resiliência em chamadas de API usando Tenacity.
- **RAG Evaluation**: Métricas de Faithfulness e Answer Relevance com Ragas.
