"""
MLflow logging utilities for comprehensive experiment tracking and metrics.

# MLFLOW_QUICKREF

# MLflow Quick Reference

## ⚡ Uso Mais Comum

### 1. Log de Query RAG (Automático)
A API `/chat` já loga automaticamente. Ou use manualmente:

```python
from shared.mlflow_logger import log_rag_run

log_rag_run(
    question="Pergunta?",
    answer="Resposta...",
    context_count=3,
    model="llama3",
    latency_seconds=0.45,
    retrieval_score=0.89
)
```

### 2. Log de Ingestão (Automático)
A API `/ingest` já loga automaticamente. Ou use manualmente:

```python
from shared.mlflow_logger import log_ingestion_run

log_ingestion_run(
    file_name="documento.pdf",
    pages_processed=15,
    chunks_created=120,
    duration_seconds=5.2,
    success=True
)
```

### 3. Log com Context Manager (Recomendado)
```python
from shared.mlflow_logger import MLflowRun, log_params_batch, log_metrics_batch

with MLflowRun("MyExperiment", "run_001"):
    log_params_batch({"model": "llama3", "lr": 0.001})
    log_metrics_batch({"accuracy": 0.92, "loss": 0.45})
```

### 4. Encontrar Melhores Runs
```python
from shared.mlflow_logger import get_best_runs

best_runs = get_best_runs("MyExperiment", "accuracy", max_results=10)
for run in best_runs:
    print(f"{run.info.run_name}: {run.data.metrics['accuracy']}")
```

### 5. Registrar Modelo
```python
from shared.mlflow_logger import register_model, transition_model_stage

register_model(
    model_uri="runs:/abc123/model",
    model_name="my_model",
    description="Modelo em produção"
)

# Promover para produção
transition_model_stage("my_model", version=1, stage="Production")
```

---

## 📊 Acessar Dados

### Via Web
- Acesse: **http://localhost:5000**
- Clique em "Experiments" para ver todos
- Clique em um experimento para ver as runs

### Via Python
```python
from shared.mlflow_logger import get_experiment_summary, search_runs_by_metric

# Resumo de experimento
summary = get_experiment_summary("MyExperiment")
print(f"Total runs: {summary['total_runs']}")

# Buscar runs com acurácia > 0.85
runs = search_runs_by_metric("MyExperiment", "accuracy", min_value=0.85)
```

### Via REST API
```bash
curl http://localhost:5000/api/2.0/mlflow/experiments/list
curl http://localhost:5000/api/2.0/mlflow/runs/search \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"experiment_ids": ["0"]}'
```

---

## 🎯 Recursos Disponíveis

| Recurso | Função | Status |
|---------|--------|--------|
| Experiments | `set_experiment()` | ✅ Pronto |
| Runs | `MLflowRun` context | ✅ Pronto |
| Parameters | `log_params_batch()` | ✅ Pronto |
| Metrics | `log_metrics_batch()` | ✅ Pronto |
| Artifacts | `log_configs_as_artifact()` | ✅ Pronto |
| Model Registry | `register_model()` | ✅ Pronto |
| Search | `get_best_runs()` | ✅ Pronto |
| Batch Ops | `log_*_batch()` | ✅ Pronto |
| Dataset Tracking | `log_dataset_used()` | ✅ Pronto |
| Autolog | `enable_autolog()` | ✅ Pronto |

---

## 📝 Exemplos Prontos

### RAG Completa
```python
from shared.mlflow_logger import log_rag_run
import time

start = time.time()
question = "O que é IA?"
answer = "IA é inteligência artificial..."
latency = time.time() - start

log_rag_run(
    question=question,
    answer=answer,
    context_count=3,
    model="llama3",
    latency_seconds=latency,
    retrieval_score=0.89,
    metadata={"batch": "001"}
)
```

### Training Loop
```python
from shared.mlflow_logger import MLflowRun, log_metrics_batch

with MLflowRun("Training", "epoch_001"):
    for epoch in range(10):
        metrics = {
            "train_loss": 0.5 / (epoch + 1),
            "val_loss": 0.45 / (epoch + 1)
        }
        log_metrics_batch(metrics, step=epoch)
```

### Comparar Modelos
```python
from shared.mlflow_logger import MLflowRun, log_params_batch, log_metrics_batch

for model in ["llama3", "mistral"]:
    with MLflowRun("Model_Comparison", f"run_{model}"):
        log_params_batch({"model": model})
        log_metrics_batch({"accuracy": 0.92 if model == "llama3" else 0.88})
```

---

## 🚀 Próximos Passos

1. **Execute a demo**: `python mlflow_demo.py`
2. **Acesse a UI**: http://localhost:5000
3. **Use em seu código**: Copie exemplos acima
4. **Consulte dados**: Use Python Client ou Web UI

---

# MLFLOW_GUIDE

# Guia Completo de MLflow

## O que é MLflow?

MLflow é uma plataforma **completa** para gerenciar o ciclo de vida do aprendizado de máquina, incluindo:

| Recurso | Descrição |
|---------|-----------|
| **Tracking** | Registrar parâmetros, métricas, artefatos de runs |
| **Model Registry** | Versionamento e staging de modelos |
| **Models** | Servir modelos em diferentes formatos |
| **Projects** | Empacotar código reproduzível |
| **Datasets** | Rastrear datasets usados em experimentos |
| **Evaluation** | Comparar e avaliar modelos |
| **Autolog** | Logging automático de frameworks |
| **Search & Query** | Buscar runs com filtros avançados |

---

## Recursos Implementados Neste Projeto

### ✅ 1. TRACKING CORE

#### Experiments & Runs
```python
from shared.mlflow_logger import set_experiment, MLflowRun

# Usar Context Manager (recomendado)
with MLflowRun("MyExperiment", "run_001"):
    log_params_batch({"lr": 0.001})
    log_metrics_batch({"loss": 0.45})
```

#### Parameters
```python
from shared.mlflow_logger import log_params_batch

log_params_batch({
    "model": "llama3",
    "chunk_size": 1000,
    "temperature": 0.7,
    "top_p": 0.95
})
```

#### Metrics
```python
from shared.mlflow_logger import log_metrics_batch

# Simples
log_metrics_batch({"accuracy": 0.92, "f1": 0.88})

# Com histórico (training curves)
from shared.mlflow_logger import log_custom_metric_history

log_custom_metric_history("loss", [0.50, 0.42, 0.35, 0.28])
```

#### Tags
```python
import mlflow

mlflow.set_tag("model", "llama3")
mlflow.set_tag("environment", "production")
mlflow.set_tag("version", "1.2.0")
```

#### Artifacts
```python
from shared.mlflow_logger import log_configs_as_artifact

log_configs_as_artifact({
    "model_config": {"temperature": 0.7},
    "retrieval_config": {"k": 3}
})
```

### ✅ 2. ADVANCED TRACKING

#### RAG Query Logging com Metadata
```python
from shared.mlflow_logger import log_rag_run

log_rag_run(
    question="O que é Machine Learning?",
    answer="ML é uma subárea da IA...",
    context_count=3,
    model="llama3",
    latency_seconds=0.45,
    retrieval_score=0.89,
    metadata={
        "batch": "001",
        "source": "api",
        "user_id": "user123"
    }
)
```

#### Document Ingestion Logging com Estatísticas
```python
from shared.mlflow_logger import log_ingestion_run

log_ingestion_run(
    file_name="documento.pdf",
    pages_processed=15,
    chunks_created=120,
    duration_seconds=5.2,
    file_size_mb=2.5,
    chunk_stats={
        "avg_size": 850,
        "max_size": 1200,
        "min_size": 450
    },
    success=True
)
```

#### Model Performance Logging com Confusion Matrix
```python
from shared.mlflow_logger import log_model_performance

log_model_performance(
    metrics={
        "accuracy": 0.92,
        "precision": 0.89,
        "recall": 0.88,
        "f1_score": 0.885,
        "rouge_1": 0.745,
        "bleu": 0.567
    },
    params={
        "model": "llama3",
        "chunk_size": 1000
    },
    tags={
        "version": "1.2.0",
        "dataset": "benchmark"
    },
    confusion_matrix=[[85, 12], [8, 195]]
)
```

### ✅ 3. MODEL REGISTRY

Registrar e versionar modelos:

```python
from shared.mlflow_logger import register_model, transition_model_stage

# Registrar modelo
result = register_model(
    model_uri="runs:/abc123/model",
    model_name="my_rag_model",
    description="Modelo de RAG em produção",
    tags_dict={"framework": "langchain", "llm": "llama3"}
)

# Transicionar para staging
transition_model_stage("my_rag_model", version=1, stage="Staging")

# Promover para produção
transition_model_stage("my_rag_model", version=1, stage="Production")

# Arquivar versão antiga
transition_model_stage("my_rag_model", version=0, stage="Archived")
```

### ✅ 4. SEARCH & QUERY

Buscar e comparar runs:

```python
from shared.mlflow_logger import (
    get_best_runs,
    search_runs_by_metric,
    get_experiment_summary,
    compare_experiments
)

# Encontrar as 10 melhores runs por métrica
best_runs = get_best_runs("RAG_Experiment", "accuracy", max_results=10)

# Buscar runs com métrica em range
high_accuracy_runs = search_runs_by_metric(
    "RAG_Experiment",
    "accuracy",
    min_value=0.85,
    max_value=1.0
)

# Obter resumo completo de experimento
summary = get_experiment_summary("RAG_Experiment")
print(f"Total runs: {summary['total_runs']}")

# Comparar experimentos
comparison = compare_experiments(
    experiment_ids=["0", "1"],
    metric_name="accuracy"
)
```

### ✅ 5. BATCH OPERATIONS

Logar múltiplos parâmetros/métricas eficientemente:

```python
from shared.mlflow_logger import log_params_batch, log_metrics_batch

# 50+ parâmetros em uma chamada
large_config = {f"param_{i}": f"value_{i}" for i in range(50)}
log_params_batch(large_config)

# Múltiplas métricas por step
for step in range(100):
    metrics = {
        "train_loss": 0.5 - (step * 0.001),
        "val_loss": 0.45 - (step * 0.0008),
        "learning_rate": 0.001 * (1 - step/100)
    }
    log_metrics_batch(metrics, step=step)
```

### ✅ 6. CONTEXT MANAGERS

Gerenciamento automático de runs:

```python
from shared.mlflow_logger import MLflowRun

# Automático enter/exit
with MLflowRun(
    experiment_name="MyExperiment",
    run_name="my_run",
    tags={"env": "production", "version": "1.0"}
) as run:
    log_params_batch({"model": "llama3"})
    log_metrics_batch({"accuracy": 0.92})
    # Automático mlflow.end_run() ao sair
```

### ✅ 7. DATASET TRACKING

Rastrear datasets usados (MLflow 2.0+):

```python
from shared.mlflow_logger import log_dataset_used

log_dataset_used(
    name="benchmark_rag",
    uri="s3://my-bucket/datasets/benchmark.csv",
    digest="md5:abc123...",
    source="s3",
    features=["question", "answer", "context"],
    version="1.0"
)
```

### ✅ 8. AUTOLOG

Logging automático de frameworks:

```python
from shared.mlflow_logger import enable_autolog

# Habilitar para scikit-learn, TensorFlow, PyTorch, etc.
enable_autolog()

# Seu código ML normal
# Métricas e modelos serão logados automaticamente
```

---

## Como Usar: Guia Prático

### Opção 1: Teste Rápido (Recomendado)

```bash
python mlflow_demo.py
```

Isso demonstra **todos os 8 recursos** do MLflow.

### Opção 2: Usar em Seu Código

```python
from shared.mlflow_logger import set_experiment, MLflowRun, log_rag_run

# Setup
set_experiment("My_Experiment")

# Simple run
with MLflowRun("My_Experiment", "run_001"):
    log_rag_run(
        question="pergunta?",
        answer="resposta...",
        context_count=3,
        model="llama3",
        latency_seconds=0.45,
        retrieval_score=0.89
    )
```

### Opção 3: API Normal

Faça requisições normais e os dados são logados automaticamente:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Qual é o significado de IA?"}'
```

---

## Consultando Dados

### 1. Via Interface Web

Acesse **http://localhost:5000**

- **Experiments Tab**: Veja todos os experimentos criados
- **Runs**: Clique em um experimento para ver as runs
- **Charts**: Visualize métricas em gráficos interativos
- **Artifacts**: Baixe arquivos salvos (configs, logs)
- **Model Registry**: Gerencie versões de modelos

### 2. Via Python

```python
import mlflow
from mlflow.tracking import MlflowClient

client = MlflowClient("http://localhost:5000")

# Listar experimentos
experiments = client.search_experiments()
for exp in experiments:
    print(f"{exp.name}: {len(client.search_runs(exp.experiment_id))} runs")

# Buscar runs específicas
runs = client.search_runs(
    experiment_ids=["0"],
    filter_string="metrics.accuracy > 0.90"
)

for run in runs:
    print(f"Run: {run.info.run_name}")
    print(f"  Accuracy: {run.data.metrics.get('accuracy')}")
    print(f"  Model: {run.data.params.get('model')}")
```

### 3. Via REST API

```bash
# Listar experimentos
curl http://localhost:5000/api/2.0/mlflow/experiments/list

# Buscar runs
curl -X POST http://localhost:5000/api/2.0/mlflow/runs/search \
  -H "Content-Type: application/json" \
  -d '{
    "experiment_ids": ["0"],
    "filter": "metrics.accuracy > 0.90"
  }'

# Obter detalhes de run
curl http://localhost:5000/api/2.0/mlflow/runs/get?run_id=abc123
```

---

## Métricas Rastreadas

### RAG Queries
| Métrica | Descrição | Range |
|---------|-----------|-------|
| `latency_seconds` | Tempo de resposta | 0-5s |
| `context_retrieved` | Documentos recuperados | 0-100 |
| `retrieval_score` | Qualidade da recuperação | 0-1 |

### Ingestion
| Métrica | Descrição |
|---------|-----------|
| `pages_processed` | Páginas processadas |
| `chunks_created` | Chunks criados |
| `duration_seconds` | Tempo total |
| `avg_chunk_size` | Tamanho médio de chunk |

### Model Performance
| Métrica | Descrição |
|---------|-----------|
| `accuracy` | Acurácia geral |
| `precision` | Precisão por classe |
| `recall` | Recall por classe |
| `f1_score` | F1 score |
| `rouge_*` | ROUGE scores |
| `bleu` | BLEU score |
| `perplexity` | Perplexidade |

---

## Exemplos Avançados

### Exemplo 1: Pipeline de Treinamento Completo

```python
from shared.mlflow_logger import (
    set_experiment, MLflowRun, log_params_batch,
    log_metrics_batch, register_model
)

# Setup
experiment_id = set_experiment("ML_Pipeline")

# Treinamento
with MLflowRun("ML_Pipeline", "training_run_001"):
    # Log config
    log_params_batch({
        "epochs": 100,
        "batch_size": 32,
        "learning_rate": 0.001
    })
    
    # Simular treinamento
    for epoch in range(5):
        metrics = {
            "train_loss": 0.5 / (epoch + 1),
            "val_loss": 0.45 / (epoch + 1)
        }
        log_metrics_batch(metrics, step=epoch)

# Registrar modelo
register_model(
    model_uri="runs:/abc123/model",
    model_name="my_model",
    description="Melhor modelo de treinamento"
)
```

### Exemplo 2: Comparação de Modelos

```python
# Executar mesmo experimento com diferentes modelos
for model in ["llama3", "mistral", "neural-chat"]:
    with MLflowRun("Model_Comparison", f"run_{model}"):
        log_params_batch({"model": model})
        
        # Simular avaliação
        for i in range(3):
            log_metrics_batch({
                "accuracy": 0.85 + (i * 0.02),
                "latency": 0.5 - (i * 0.05)
            }, step=i)

# Encontrar melhor
best = get_best_runs("Model_Comparison", "accuracy", max_results=1)
print(f"Melhor modelo: {best[0].data.params['model']}")
```

### Exemplo 3: Análise de Performance

```python
from shared.mlflow_logger import get_experiment_summary

summary = get_experiment_summary("RAG_Experiment")

# Análises
total_runs = summary['total_runs']
avg_accuracy = sum(
    r['metrics'].get('accuracy', 0)
    for r in summary['runs']
) / total_runs if total_runs > 0 else 0

print(f"Total runs: {total_runs}")
print(f"Acurácia média: {avg_accuracy:.2%}")
```

---

## Troubleshooting

### Erro: Connection refused

```bash
# Iniciar MLflow
docker compose up -d  # ou
mlflow server --host 0.0.0.0 --port 5000
```

### Erro: ModuleNotFoundError: mlflow

```bash
pip install mlflow
```

### Dados não aparecem

1. Certifique-se que MLflow está rodando: `curl http://localhost:5000/health`
2. Verifique `MLFLOW_TRACKING_URI` em `config/settings.py`
3. Veja logs: `docker logs mlflow`

---

## Recursos Adicionais

- [Documentação Oficial MLflow](https://mlflow.org)
- [MLflow REST API](https://mlflow.org/docs/latest/rest-api.html)
- [Model Registry](https://mlflow.org/docs/latest/model-registry.html)
- [Tracking Guide](https://mlflow.org/docs/latest/tracking/)
- [MLflow Projects](https://mlflow.org/docs/latest/projects.html)

---

# MLFLOW_RESOURCES

# MLflow - Recursos Implementados

## 📊 Status Geral

| Recurso | Status | Detalhes |
|---------|--------|----------|
| Tracking Core (Runs, Params, Metrics) | ✅ Implementado | Completo com context managers |
| Tags & Metadata | ✅ Implementado | Suporte para tags estruturados |
| Artifacts | ✅ Implementado | Suporte para JSON, texto, confusão matrix |
| Model Registry | ✅ Implementado | Registro, versionamento e staging |
| Search & Query | ✅ Implementado | Busca avançada com filtros |
| Batch Operations | ✅ Implementado | Log eficiente de múltiplos itens |
| Dataset Tracking | ✅ Implementado | Rastreamento de datasets (MLflow 2.0+) |
| Autolog | ✅ Implementado | Logging automático de frameworks |
| Context Managers | ✅ Implementado | Gerenciamento automático de runs |
| Experiment Comparison | ✅ Implementado | Comparação cross-experiment |
| Custom Metrics History | ✅ Implementado | Training curves e históricos |
| REST API | ✅ Suportado | Via HTTP direto ao servidor |
| Python Client | ✅ Implementado | MlflowClient para queries avançadas |

---

## 🔧 APIs Disponíveis

### 1. Setup & Configuration
```python
setup_mlflow()                          # Inicializar conexão
set_experiment(name)                    # Ativar experimento
get_or_create_experiment(name)         # Obter ou criar experimento
enable_autolog()                        # Habilitar autolog de frameworks
```

### 2. Basic Logging
```python
log_rag_run(...)                        # Log de queries RAG
log_ingestion_run(...)                  # Log de ingestão de docs
log_model_performance(...)              # Log de performance
log_params_batch(params)                # Log múltiplos parâmetros
log_metrics_batch(metrics, step)        # Log múltiplas métricas
log_custom_metric_history(...)          # Log de histórico de métrica
log_configs_as_artifact(config)         # Log config como JSON
```

### 3. Model Registry
```python
register_model(...)                     # Registrar modelo
transition_model_stage(...)             # Transicionar stage
```

### 4. Search & Query
```python
get_best_runs(...)                      # Obter melhores runs
search_runs_by_metric(...)              # Buscar runs com filtro
get_experiment_summary(...)             # Resumo de experimento
compare_experiments(...)                # Comparar experimentos
```

### 5. Dataset Tracking
```python
log_dataset_used(...)                   # Rastrear dataset
```

### 6. Context Managers
```python
with MLflowRun(exp, run, tags):         # Gerenciar run automaticamente
    # seu código aqui
```

---

## 📈 Exemplos de Uso

### Exemplo 1: RAG Query Completa

```python
from shared.mlflow_logger import log_rag_run

log_rag_run(
    question="O que é IA?",
    answer="IA é inteligência artificial...",
    context_count=3,
    model="llama3",
    latency_seconds=0.45,
    retrieval_score=0.89,
    metadata={
        "batch": "001",
        "source": "api",
        "user_id": "user123"
    }
)
```

**Dados Registrados:**
- ✓ Parameters: question, model, context_count
- ✓ Metrics: context_retrieved, latency_seconds, retrieval_score
- ✓ Tags: pipeline, timestamp, question_length, answer_length
- ✓ Artifacts: rag_answer.txt, metadata.json

---

### Exemplo 2: Ingestão de Documento

```python
from shared.mlflow_logger import log_ingestion_run

log_ingestion_run(
    file_name="documento.pdf",
    pages_processed=15,
    chunks_created=120,
    duration_seconds=5.2,
    file_size_mb=2.5,
    chunk_stats={
        "avg_size": 850,
        "max_size": 1200,
        "min_size": 450
    },
    success=True
)
```

**Dados Registrados:**
- ✓ Parameters: file_name, success
- ✓ Metrics: pages_processed, chunks_created, duration_seconds, avg/max/min_chunk_size
- ✓ Tags: pipeline, timestamp, status, chunks_per_page
- ✓ Artifacts: ingestion_stats.json

---

### Exemplo 3: Avaliação de Modelo

```python
from shared.mlflow_logger import log_model_performance

log_model_performance(
    metrics={
        "accuracy": 0.92,
        "precision": 0.89,
        "recall": 0.88,
        "f1_score": 0.885,
        "rouge_1": 0.745,
        "bleu": 0.567,
        "perplexity": 14.8
    },
    params={
        "model": "llama3",
        "chunk_size": 1000,
        "temperature": 0.7
    },
    tags={
        "version": "1.2.0",
        "dataset": "benchmark",
        "environment": "production"
    },
    confusion_matrix=[[85, 12], [8, 195]]
)
```

**Dados Registrados:**
- ✓ 8+ Parameters: model, chunk_size, temperature, etc
- ✓ 8+ Metrics: accuracy, precision, recall, f1, rouge, bleu, perplexity
- ✓ Tags: pipeline, timestamp, version, dataset
- ✓ Artifacts: metrics.json, confusion_matrix.json

---

### Exemplo 4: Context Manager com Batch Operations

```python
from shared.mlflow_logger import MLflowRun, log_params_batch, log_metrics_batch

with MLflowRun(
    experiment_name="MyExperiment",
    run_name="training_001",
    tags={"env": "production", "version": "1.0"}
) as run:
    # Log 50+ parâmetros
    config = {f"param_{i}": f"value_{i}" for i in range(50)}
    log_params_batch(config)
    
    # Log múltiplas métricas por step
    for step in range(100):
        metrics = {
            "train_loss": 0.5 / (step + 1),
            "val_loss": 0.45 / (step + 1),
            "learning_rate": 0.001 * (1 - step/100)
        }
        log_metrics_batch(metrics, step=step)
```

---

### Exemplo 5: Search & Query

```python
from shared.mlflow_logger import (
    get_best_runs,
    search_runs_by_metric,
    compare_experiments
)

# Top 10 melhores runs por accuracy
best = get_best_runs("RAG_Experiment", "accuracy", max_results=10)

# Runs com accuracy > 0.85 e < 1.0
filtered = search_runs_by_metric(
    "RAG_Experiment",
    "accuracy",
    min_value=0.85,
    max_value=1.0
)

# Comparar dois experimentos
comparison = compare_experiments(
    experiment_ids=["0", "1"],
    metric_name="accuracy"
)
```

---

### Exemplo 6: Model Registry

```python
from shared.mlflow_logger import register_model, transition_model_stage

# Registrar
result = register_model(
    model_uri="runs:/abc123/model",
    model_name="rag_model",
    description="RAG modelo v1.2",
    tags_dict={"framework": "langchain", "llm": "llama3"}
)

# Staging
transition_model_stage("rag_model", version=1, stage="Staging")

# Production
transition_model_stage("rag_model", version=1, stage="Production")

# Archive
transition_model_stage("rag_model", version=0, stage="Archived")
```

---

## 📊 Dados Logados Atualmente

### Na API (`/chat` endpoint`)
```
RAG Query:
├── Parameters: question, model, context_count
├── Metrics: latency, retrieval_score, context_retrieved
├── Tags: pipeline, timestamp, lengths
└── Artifacts: response, metadata
```

### Na Ingestão (`/ingest` endpoint`)
```
Document Ingestion:
├── Parameters: file_name, success
├── Metrics: pages, chunks, duration, sizes
├── Tags: pipeline, status, efficiency
└── Artifacts: statistics
```

### No Avaliador (Manual)
```
Model Performance:
├── Parameters: model_config, chunk_size, etc
├── Metrics: accuracy, precision, recall, f1, rouge, bleu, perplexity
├── Tags: version, dataset, environment
└── Artifacts: metrics.json, confusion_matrix.json
```

---

## 🚀 Como Executar Demo

```bash
# 1. Certifique que MLflow está rodando
docker compose up -d

# 2. Execute demo com TODOS os recursos
python mlflow_demo.py

# 3. Acesse a UI
# http://localhost:5000
```

---

## 📚 Arquivos Modificados

| Arquivo | Mudanças |
|---------|----------|
| `shared/mlflow_logger.py` | Criado com 300+ linhas de APIs |
| `rag/service.py` | Integração de logging RAG |
| `ingestion/pipeline.py` | Integração de logging ingestão |
| `mlflow_demo.py` | Demo abrangente de 8 recursos |
| `MLFLOW_GUIDE.md` | Guia completo (50+ exemplos) |

---

## ✅ Checklist de Recursos

### Core Tracking
- [x] Experiments (criar, ativar, listar)
- [x] Runs (criar, gerenciar, finalizar)
- [x] Parameters (simples e batch)
- [x] Metrics (simples, batch, com steps)
- [x] Metrics History (training curves)
- [x] Tags (estruturados, metadados)
- [x] Artifacts (JSON, texto, matrizes)

### Advanced Features
- [x] Model Registry (registrar, versionar)
- [x] Model Staging (Staging, Production, Archived)
- [x] Search & Query (com filtros)
- [x] Experiment Comparison
- [x] Best Runs Selection
- [x] Dataset Tracking
- [x] Autolog Support

### Development Tools
- [x] Context Managers (MLflowRun)
- [x] Batch Operations (Eficiência)
- [x] Error Handling (try/except)
- [x] Logging (integration com logger)
- [x] REST API Support
- [x] Python Client API

### Documentation
- [x] Guia completo (MLFLOW_GUIDE.md)
- [x] Exemplos práticos (8 demos)
- [x] Docstrings (todas as funções)
- [x] Status de recursos

---

## 🎯 Próximos Passos Opcionais

1. **Model Serving**: `mlflow models serve` para servir modelos
2. **Projects**: Empacotar código em MLflow Projects
3. **Databricks Integration**: Conectar com Databricks
4. **Custom Metrics**: Métrica customizadas por domínio
5. **Alertas**: Disparar alertas baseado em métricas
"""
import mlflow
import mlflow.pyfunc
import json
import tempfile
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from config.settings import settings
from shared.logging import logger

# ============================================================================
# SETUP & CONFIGURATION
# ============================================================================

def setup_mlflow():
    """Initialize MLflow tracking server."""
    mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
    logger.info(f"MLflow tracking URI set to {settings.MLFLOW_TRACKING_URI}")

def get_or_create_experiment(experiment_name: str) -> str:
    """Get or create an experiment by name."""
    setup_mlflow()
    
    experiment = mlflow.get_experiment_by_name(experiment_name)
    if experiment is None:
        experiment_id = mlflow.create_experiment(experiment_name)
        logger.info(f"Created MLflow experiment: {experiment_name}")
    else:
        experiment_id = experiment.experiment_id
        logger.info(f"Using existing MLflow experiment: {experiment_name}")
    
    return experiment_id

def set_experiment(experiment_name: str):
    """Set the active experiment."""
    setup_mlflow()
    exp_id = get_or_create_experiment(experiment_name)
    mlflow.set_experiment(experiment_name)
    return exp_id

# ============================================================================
# BASIC TRACKING
# ============================================================================

def log_rag_run(question: str, answer: str, context_count: int, model: str, 
                latency_seconds: float = None, retrieval_score: float = None,
                metadata: Dict[str, Any] = None):
    """Log a RAG query run to MLflow with comprehensive tracking."""
    setup_mlflow()
    
    with mlflow.start_run(run_name=f"rag_query_{question[:30]}"):
        # === PARAMETERS ===
        mlflow.log_param("question", question)
        mlflow.log_param("model", model)
        mlflow.log_param("context_count", context_count)
        
        # === METRICS ===
        mlflow.log_metric("context_retrieved", context_count)
        if latency_seconds:
            mlflow.log_metric("latency_seconds", latency_seconds)
        if retrieval_score:
            mlflow.log_metric("retrieval_score", retrieval_score)
        
        # === TAGS ===
        mlflow.set_tag("pipeline", "rag")
        mlflow.set_tag("timestamp", datetime.now().isoformat())
        mlflow.set_tag("question_length", len(question))
        mlflow.set_tag("answer_length", len(answer))
        
        # === ARTIFACTS ===
        # Log answer
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(f"Question: {question}\n")
            f.write(f"Answer: {answer}\n")
            f.write(f"Model: {model}\n")
            f.write(f"Context Count: {context_count}\n")
            if latency_seconds:
                f.write(f"Latency: {latency_seconds:.2f}s\n")
            f.name_temp = f.name
        
        mlflow.log_artifact(f.name_temp, artifact_path="rag_output")
        os.unlink(f.name_temp)
        
        # Log metadata as JSON if provided
        if metadata:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(metadata, f, indent=2)
                f.name_temp = f.name
            
            mlflow.log_artifact(f.name_temp, artifact_path="metadata")
            os.unlink(f.name_temp)

def log_ingestion_run(file_name: str, pages_processed: int, chunks_created: int, 
                      duration_seconds: float = None, success: bool = True,
                      file_size_mb: float = None, chunk_stats: Dict = None):
    """Log a PDF ingestion run to MLflow with detailed tracking."""
    setup_mlflow()
    
    with mlflow.start_run(run_name=f"ingest_{file_name[:30]}"):
        # === PARAMETERS ===
        mlflow.log_param("file_name", file_name)
        mlflow.log_param("success", success)
        
        # === METRICS ===
        mlflow.log_metric("pages_processed", pages_processed)
        mlflow.log_metric("chunks_created", chunks_created)
        if duration_seconds:
            mlflow.log_metric("duration_seconds", duration_seconds)
        if file_size_mb:
            mlflow.log_metric("file_size_mb", file_size_mb)
        
        if chunk_stats:
            mlflow.log_metric("avg_chunk_size", chunk_stats.get("avg_size", 0))
            mlflow.log_metric("max_chunk_size", chunk_stats.get("max_size", 0))
            mlflow.log_metric("min_chunk_size", chunk_stats.get("min_size", 0))
        
        # === TAGS ===
        mlflow.set_tag("pipeline", "ingestion")
        mlflow.set_tag("timestamp", datetime.now().isoformat())
        mlflow.set_tag("status", "success" if success else "failed")
        mlflow.set_tag("chunks_per_page", chunks_created / pages_processed if pages_processed > 0 else 0)
        
        # === ARTIFACTS ===
        # Log ingestion statistics
        stats = {
            "file_name": file_name,
            "pages_processed": pages_processed,
            "chunks_created": chunks_created,
            "duration_seconds": duration_seconds,
            "file_size_mb": file_size_mb,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        
        if chunk_stats:
            stats.update(chunk_stats)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(stats, f, indent=2)
            f.name_temp = f.name
        
        mlflow.log_artifact(f.name_temp, artifact_path="ingestion_stats")
        os.unlink(f.name_temp)

def log_model_performance(metrics: dict, params: dict = None, tags: dict = None,
                         confusion_matrix: List[List[int]] = None):
    """Log comprehensive model performance metrics to MLflow."""
    setup_mlflow()
    
    with mlflow.start_run(run_name="model_evaluation"):
        # === PARAMETERS ===
        if params:
            for key, value in params.items():
                mlflow.log_param(key, value)
        
        # === METRICS ===
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                mlflow.log_metric(key, value)
        
        # === TAGS ===
        mlflow.set_tag("pipeline", "evaluation")
        mlflow.set_tag("timestamp", datetime.now().isoformat())
        
        if tags:
            for key, value in tags.items():
                mlflow.set_tag(key, value)
        
        # === ARTIFACTS ===
        # Log metrics as JSON
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(metrics, f, indent=2)
            f.name_temp = f.name
        
        mlflow.log_artifact(f.name_temp, artifact_path="metrics")
        os.unlink(f.name_temp)
        
        # Log confusion matrix if provided
        if confusion_matrix:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump({"confusion_matrix": confusion_matrix}, f, indent=2)
                f.name_temp = f.name
            
            mlflow.log_artifact(f.name_temp, artifact_path="matrices")
            os.unlink(f.name_temp)

# ============================================================================
# DATASETS TRACKING (MLflow 2.0+)
# ============================================================================

def log_dataset_used(name: str, uri: str, digest: str, source: str = None, 
                     features: List[str] = None, version: str = None):
    """Log a dataset as input to a run."""
    setup_mlflow()
    
    dataset_input = mlflow.data.from_uri(uri, digest=digest)
    
    with mlflow.start_run(run_name=f"dataset_{name}"):
        mlflow.log_input(dataset_input, context="training")
        
        mlflow.set_tag("dataset_name", name)
        mlflow.set_tag("dataset_source", source or "unknown")
        if version:
            mlflow.set_tag("dataset_version", version)
        
        if features:
            mlflow.log_param("features_count", len(features))
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump({"features": features}, f)
                f.name_temp = f.name
            
            mlflow.log_artifact(f.name_temp, artifact_path="dataset_info")
            os.unlink(f.name_temp)

# ============================================================================
# MODEL REGISTRY
# ============================================================================

def register_model(artifact_path: str, model_name: str, model_uri: str = None,
                  description: str = None, tags_dict: Dict = None):
    """Register a model in MLflow Model Registry."""
    setup_mlflow()
    
    # Log model as artifact first if artifact_path is provided
    if artifact_path and os.path.exists(artifact_path):
        with mlflow.start_run(run_name=f"model_registration_{model_name}"):
            mlflow.log_artifact(artifact_path, artifact_path="model")
            model_uri = f"runs:/{mlflow.active_run().info.run_id}/model"
    
    # Register in model registry
    try:
        result = mlflow.register_model(
            model_uri=model_uri,
            name=model_name,
            tags=tags_dict or {},
            description=description or f"Model: {model_name}"
        )
        logger.info(f"Model registered: {model_name}")
        return result
    except Exception as e:
        logger.warning(f"Failed to register model: {e}")
        return None

def transition_model_stage(model_name: str, version: int, stage: str):
    """Transition a model version to a new stage (Staging, Production, Archived)."""
    setup_mlflow()
    
    try:
        client = mlflow.tracking.MlflowClient()
        client.transition_model_version_stage(
            name=model_name,
            version=version,
            stage=stage
        )
        logger.info(f"Model {model_name} v{version} transitioned to {stage}")
    except Exception as e:
        logger.warning(f"Failed to transition model: {e}")

# ============================================================================
# ADVANCED EXPERIMENT TRACKING
# ============================================================================

def compare_experiments(experiment_ids: List[str], metric_name: str):
    """Compare metrics across multiple experiments."""
    setup_mlflow()
    
    client = mlflow.tracking.MlflowClient()
    results = []
    
    for exp_id in experiment_ids:
        runs = client.search_runs(experiment_ids=[exp_id])
        for run in runs:
            metric_value = run.data.metrics.get(metric_name)
            if metric_value is not None:
                results.append({
                    "experiment_id": exp_id,
                    "run_id": run.info.run_id,
                    "run_name": run.info.run_name,
                    metric_name: metric_value
                })
    
    return results

def get_best_runs(experiment_name: str, metric_name: str, max_results: int = 10):
    """Get the best runs for a specific metric in an experiment."""
    setup_mlflow()
    
    client = mlflow.tracking.MlflowClient()
    experiment = mlflow.get_experiment_by_name(experiment_name)
    
    if not experiment:
        logger.warning(f"Experiment {experiment_name} not found")
        return []
    
    order_by = [f"metrics.{metric_name} DESC"]
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=order_by,
        max_results=max_results
    )
    
    return runs

def log_custom_metric_history(metric_name: str, values: List[float], step_values: List[int] = None):
    """Log a metric with multiple values (useful for training curves)."""
    setup_mlflow()
    
    if step_values is None:
        step_values = list(range(len(values)))
    
    for step, value in zip(step_values, values):
        mlflow.log_metric(metric_name, value, step=step)

# ============================================================================
# CONTEXT MANAGERS & UTILITIES
# ============================================================================

class MLflowRun:
    """Context manager for MLflow runs."""
    
    def __init__(self, experiment_name: str, run_name: str, tags: Dict = None):
        self.experiment_name = experiment_name
        self.run_name = run_name
        self.tags = tags or {}
        self.run = None
    
    def __enter__(self):
        setup_mlflow()
        set_experiment(self.experiment_name)
        self.run = mlflow.start_run(run_name=self.run_name)
        
        # Log tags
        for key, value in self.tags.items():
            mlflow.set_tag(key, value)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        mlflow.end_run()
        if exc_type:
            logger.error(f"Run failed with error: {exc_val}")

def log_params_batch(params: Dict[str, Any]):
    """Log multiple parameters at once."""
    for key, value in params.items():
        mlflow.log_param(key, value)

def log_metrics_batch(metrics: Dict[str, float], step: int = None):
    """Log multiple metrics at once."""
    for key, value in metrics.items():
        if isinstance(value, (int, float)):
            mlflow.log_metric(key, value, step=step)

def log_configs_as_artifact(config: Dict, artifact_name: str = "config.json"):
    """Log configuration as JSON artifact."""
    setup_mlflow()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f, indent=2)
        f.name_temp = f.name
    
    mlflow.log_artifact(f.name_temp, artifact_path="configs")
    os.unlink(f.name_temp)

# ============================================================================
# SEARCH & QUERY
# ============================================================================

def search_runs_by_metric(experiment_name: str, metric_name: str, 
                         min_value: float = None, max_value: float = None):
    """Search runs by metric value range."""
    setup_mlflow()
    
    client = mlflow.tracking.MlflowClient()
    experiment = mlflow.get_experiment_by_name(experiment_name)
    
    if not experiment:
        return []
    
    filter_str = ""
    if min_value is not None:
        filter_str += f"metrics.{metric_name} >= {min_value}"
    if max_value is not None:
        if filter_str:
            filter_str += " AND "
        filter_str += f"metrics.{metric_name} <= {max_value}"
    
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        filter_string=filter_str if filter_str else None
    )
    
    return runs

def get_experiment_summary(experiment_name: str) -> Dict:
    """Get a summary of an experiment."""
    setup_mlflow()
    
    client = mlflow.tracking.MlflowClient()
    experiment = mlflow.get_experiment_by_name(experiment_name)
    
    if not experiment:
        return {}
    
    runs = client.search_runs(experiment_ids=[experiment.experiment_id])
    
    summary = {
        "experiment_name": experiment_name,
        "experiment_id": experiment.experiment_id,
        "total_runs": len(runs),
        "runs": []
    }
    
    for run in runs:
        summary["runs"].append({
            "run_id": run.info.run_id,
            "run_name": run.info.run_name,
            "metrics": run.data.metrics,
            "params": run.data.params,
            "tags": run.data.tags
        })
    
    return summary

# ============================================================================
# AUTOLOG & FRAMEWORK INTEGRATION
# ============================================================================

def enable_autolog():
    """Enable autolog for supported frameworks."""
    setup_mlflow()
    
    try:
        mlflow.autolog()
        logger.info("MLflow autolog enabled")
    except Exception as e:
        logger.warning(f"Failed to enable autolog: {e}")
