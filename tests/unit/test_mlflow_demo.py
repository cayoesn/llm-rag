import time
from unittest.mock import MagicMock, patch

import shared.mlflow_logger as mlflow_logger


def demo_basic_tracking():
    mlflow_logger.set_experiment("RAG_Advanced_Demo")

    queries = [
        {
            "question": "O que é Machine Learning?",
            "answer": "ML é uma área da IA focada em sistemas que aprendem com dados...",
            "context_count": 3,
            "latency": 0.45,
            "score": 0.89,
        },
        {
            "question": "Como funciona Deep Learning?",
            "answer": "DL usa redes neurais profundas com múltiplas camadas...",
            "context_count": 2,
            "latency": 0.52,
            "score": 0.85,
        },
    ]

    for q in queries:
        mlflow_logger.log_rag_run(
            question=q["question"],
            answer=q["answer"],
            context_count=q["context_count"],
            model="llama3",
            latency_seconds=q["latency"],
            retrieval_score=q["score"],
            metadata={"batch": "demo_001", "source": "api"},
        )
        time.sleep(0.01)


def demo_ingestion_tracking():
    mlflow_logger.set_experiment("Ingestion_Advanced_Demo")

    ingestions = [
        {
            "file": "paper_ml.pdf",
            "pages": 12,
            "chunks": 95,
            "duration": 4.2,
            "file_size": 2.5,
            "chunk_stats": {"avg_size": 850, "max_size": 1200, "min_size": 450},
        },
        {
            "file": "guide_rag.pdf",
            "pages": 8,
            "chunks": 62,
            "duration": 3.1,
            "file_size": 1.8,
            "chunk_stats": {"avg_size": 920, "max_size": 1150, "min_size": 500},
        },
    ]

    for ing in ingestions:
        mlflow_logger.log_ingestion_run(
            file_name=ing["file"],
            pages_processed=ing["pages"],
            chunks_created=ing["chunks"],
            duration_seconds=ing["duration"],
            file_size_mb=ing["file_size"],
            chunk_stats=ing["chunk_stats"],
            success=True,
        )
        time.sleep(0.01)


def demo_model_evaluation():
    mlflow_logger.set_experiment("Model_Evaluation_Advanced")

    metrics = {
        "accuracy": 0.923,
        "precision": 0.897,
        "recall": 0.885,
        "f1_score": 0.891,
        "rouge_1": 0.745,
        "rouge_2": 0.632,
        "rouge_l": 0.728,
        "bleu": 0.567,
        "perplexity": 14.8,
        "latency_ms": 450,
    }

    params = {
        "model": "llama3",
        "embedding_model": "nomic-embed-text",
        "retrieval_limit": 3,
        "chunk_size": 1000,
        "temperature": 0.7,
        "top_p": 0.95,
    }

    tags = {
        "environment": "production",
        "version": "1.2.0",
        "dataset": "benchmark_rag",
        "eval_date": "2024-01-15",
    }

    mlflow_logger.log_model_performance(
        metrics=metrics,
        params=params,
        tags=tags,
        confusion_matrix=[[85, 12], [8, 195]],
    )


def demo_context_manager():
    with mlflow_logger.MLflowRun(
        experiment_name="Context_Manager_Demo",
        run_name="rag_batch_001",
        tags={"batch": "001", "pipeline": "rag_advanced"},
    ):
        mlflow_logger.log_params_batch({"batch_size": 10, "model": "llama3", "retrieval_k": 3})

        for i in range(3):
            mlflow_logger.log_metrics_batch(
                {
                    "latency": 0.45 + (i * 0.05),
                    "retrieval_score": 0.85 + (i * 0.02),
                    "context_count": 3,
                },
                step=i,
            )
            time.sleep(0.01)

        mlflow_logger.log_configs_as_artifact(
            {
                "model_config": {"name": "llama3", "temperature": 0.7},
                "retrieval_config": {"k": 3, "threshold": 0.5},
                "embedding_config": {"model": "nomic-embed-text", "dim": 768},
            }
        )


def demo_search_and_query():
    mlflow_logger.set_experiment("Search_Demo")

    for i in range(5):
        with mlflow_logger.MLflowRun("Search_Demo", f"run_{i}"):
            mlflow_logger.log_params_batch({"iteration": i})
            mlflow_logger.log_metrics_batch({"accuracy": 0.80 + (i * 0.03)})

    mlflow_logger.get_best_runs("Search_Demo", "accuracy", max_results=3)
    mlflow_logger.search_runs_by_metric("Search_Demo", "accuracy", min_value=0.85)


def demo_experiment_summary():
    mlflow_logger.get_experiment_summary("RAG_Advanced_Demo")


def demo_batch_operations():
    with mlflow_logger.MLflowRun("Batch_Operations_Demo", "batch_run_001"):
        large_params = {f"param_{i}": f"value_{i}" for i in range(20)}
        mlflow_logger.log_params_batch(large_params)

        for step in range(5):
            metrics = {f"metric_{i}": i + step * 0.1 for i in range(10)}
            mlflow_logger.log_metrics_batch(metrics, step=step)
            time.sleep(0.01)


def demo_compare_experiments():
    for exp_name in ["Exp_A", "Exp_B"]:
        mlflow_logger.set_experiment(exp_name)
        for i in range(2):
            with mlflow_logger.MLflowRun(exp_name, f"run_{i}"):
                mlflow_logger.log_params_batch({"iteration": i})
                mlflow_logger.log_metrics_batch({"score": 0.75 + (i * 0.05)})

    mlflow_logger.compare_experiments(["0", "1"], "score")


def test_demo_basic_tracking_calls_logger():
    with patch("shared.mlflow_logger.set_experiment") as mock_set_exp, patch(
        "shared.mlflow_logger.log_rag_run"
    ) as mock_log_rag, patch("tests.unit.test_mlflow_demo.time.sleep"):
        demo_basic_tracking()

    assert mock_set_exp.call_count == 1
    assert mock_log_rag.call_count == 2


def test_demo_ingestion_tracking_calls_logger():
    with patch("shared.mlflow_logger.set_experiment"), patch(
        "shared.mlflow_logger.log_ingestion_run"
    ) as mock_log_ingestion, patch("tests.unit.test_mlflow_demo.time.sleep"):
        demo_ingestion_tracking()

    assert mock_log_ingestion.call_count == 2


def test_demo_model_evaluation_calls_logger():
    with patch("shared.mlflow_logger.set_experiment"), patch(
        "shared.mlflow_logger.log_model_performance"
    ) as mock_model_perf:
        demo_model_evaluation()

    assert mock_model_perf.called


def test_demo_context_manager_uses_mlflowrun_and_batch_helpers():
    with patch("shared.mlflow_logger.MLflowRun") as mock_mlflow_run, patch(
        "shared.mlflow_logger.log_params_batch"
    ), patch("shared.mlflow_logger.log_metrics_batch"), patch(
        "shared.mlflow_logger.log_configs_as_artifact"
    ), patch("tests.unit.test_mlflow_demo.time.sleep"):
        demo_context_manager()

    assert mock_mlflow_run.called


def test_demo_search_and_query_calls_search_helpers():
    with patch("shared.mlflow_logger.set_experiment"), patch(
        "shared.mlflow_logger.MLflowRun"
    ), patch("shared.mlflow_logger.log_params_batch"), patch(
        "shared.mlflow_logger.log_metrics_batch"
    ), patch("shared.mlflow_logger.get_best_runs") as mock_best, patch(
        "shared.mlflow_logger.search_runs_by_metric"
    ) as mock_search:
        mock_best.return_value = []
        mock_search.return_value = []
        demo_search_and_query()

    assert mock_best.called
    assert mock_search.called


def test_demo_experiment_summary_uses_summary_api():
    with patch("shared.mlflow_logger.get_experiment_summary") as mock_summary:
        mock_summary.return_value = {"experiment_name": "RAG_Advanced_Demo", "total_runs": 0, "runs": []}
        demo_experiment_summary()

    assert mock_summary.called


def test_demo_batch_operations_uses_context_manager():
    with patch("shared.mlflow_logger.MLflowRun"), patch(
        "shared.mlflow_logger.log_params_batch"
    ), patch("shared.mlflow_logger.log_metrics_batch"), patch(
        "tests.unit.test_mlflow_demo.time.sleep"
    ):
        demo_batch_operations()


def test_demo_compare_experiments_calls_compare():
    with patch("shared.mlflow_logger.set_experiment"), patch(
        "shared.mlflow_logger.MLflowRun"
    ), patch("shared.mlflow_logger.log_params_batch"), patch(
        "shared.mlflow_logger.log_metrics_batch"
    ), patch("shared.mlflow_logger.compare_experiments") as mock_compare:
        mock_compare.return_value = []
        demo_compare_experiments()

    assert mock_compare.called
