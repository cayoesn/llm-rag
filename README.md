# 🔍 LLM RAG Pipeline (Enterprise Edition)

Motor RAG de Alta Performance com **HyDE (Hypothetical Document Embeddings)**, **Contextual Re-Ranker**, **Reciprocal Rank Fusion (RRF)** e **Vector DB Qdrant**.

---

## 🌟 Arquitetura & Recursos Big-Tech

- **HyDE Query Expansion Assíncrono**: Síntese de documentos hipotéticos com suporte a hook de LLM assíncrono e fallback determinístico multi-domínio (técnico, corporativo, legal) com projeção de palavras-chave.
- **Contextual Re-Ranker Engine com Heap Top-$K$**: Seleção ótima de documentos via `heapq.nlargest` com complexidade $\mathcal{O}(N \log K)$ em vez de ordenação total $\mathcal{O}(N \log N)$, economizando ciclos de CPU em grandes bases de candidatos.
- **Reciprocal Rank Fusion (RRF)**: Algoritmo de fusão híbrida combinando rankings de busca densa (vetorial) e esparsa (léxica):
  $$RRF\_Score(d) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$
- **Contextual Compression**: Compressão seletiva de contexto que descarta sentenças ruidosas preservando a ordem cronológica do texto original.
- **Ingestion Pipeline Assíncrono**: Processamento, chunking e indexação em background integrados ao Redis Queue e Qdrant.
- **Observabilidade OTel & MLflow**: Rastreamento distribuído via OpenTelemetry e auditoria de métricas e artefatos de experimentos no MLflow.

---

## 📊 Análise de Complexidade Algorítmica

| Componente | Complexidade Anterior | Complexidade Otimizada (Staff) | Estrutura de Dados |
| :--- | :--- | :--- | :--- |
| **Tokenização & Regex** | $\mathcal{O}(N \times L)$ (compilação repetida) | $\mathcal{O}(N \times L)$ (regex pré-compilada) | `re.compile` módulo |
| **Seleção Top-$K$** | $\mathcal{O}(N \log N)$ (Python `sorted`) | $\mathcal{O}(N \log K)$ | `heapq.nlargest` (Min-Heap) |
| **Fusão Híbrida** | N/A | $\mathcal{O}(D + S + N \log K)$ | Hash Table + RRF + Heap |
| **Compressão Contextual** | N/A | $\mathcal{O}(S \log M)$ ($S$ sentenças, $M$ mantidas) | Sentence Tokenizer + Max-Heap |

---

## 🚀 Como Executar no Docker

```bash
docker compose up -d --build
```

---

## 🧪 Testes Automatizados (41 Testes / 100% Hermético)

Execução hermética da suíte completa de testes unitários e de integração:

```bash
docker run --rm -v $(pwd):/workspace -w /workspace -e PYTHONPATH=/workspace portfolio-spec-engine:test pytest tests -v --cov=rag
```
