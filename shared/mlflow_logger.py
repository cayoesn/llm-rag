"""Helpers for MLflow tracking used by the RAG and ingestion pipelines."""

import json
import os
import tempfile
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

import mlflow

from config.settings import settings
from shared.logging import logger


def setup_mlflow() -> None:
    """Configure MLflow tracking from application settings."""
    mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
    logger.info("MLflow tracking URI configured", uri=settings.MLFLOW_TRACKING_URI)


def get_or_create_experiment(experiment_name: str) -> str:
    setup_mlflow()
    experiment = mlflow.get_experiment_by_name(experiment_name)
    if experiment is not None:
        logger.info("Using existing MLflow experiment", experiment=experiment_name)
        return experiment.experiment_id

    experiment_id = mlflow.create_experiment(experiment_name)
    logger.info("Created MLflow experiment", experiment=experiment_name)
    return experiment_id


def set_experiment(experiment_name: str) -> str:
    experiment_id = get_or_create_experiment(experiment_name)
    mlflow.set_experiment(experiment_name)
    return experiment_id


@contextmanager
def _temp_json_artifact(payload: Dict[str, Any]):
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            json.dump(payload, tmp, indent=2)
            temp_path = tmp.name
        yield temp_path
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)


@contextmanager
def _temp_text_artifact(content: str):
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp:
            tmp.write(content)
            temp_path = tmp.name
        yield temp_path
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)


def _log_optional_metric(name: str, value: Optional[float]) -> None:
    if value is not None:
        mlflow.log_metric(name, value)


def _set_tags(tags: Optional[Dict[str, Any]]) -> None:
    for key, value in (tags or {}).items():
        mlflow.set_tag(key, value)


def log_rag_run(
    question: str,
    answer: str,
    context_count: int,
    model: str,
    latency_seconds: Optional[float] = None,
    retrieval_score: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    setup_mlflow()

    with mlflow.start_run(run_name=f"rag_query_{question[:30]}"):
        mlflow.log_param("question", question)
        mlflow.log_param("model", model)
        mlflow.log_param("context_count", context_count)

        mlflow.log_metric("context_retrieved", context_count)
        _log_optional_metric("latency_seconds", latency_seconds)
        _log_optional_metric("retrieval_score", retrieval_score)

        _set_tags(
            {
                "pipeline": "rag",
                "timestamp": datetime.now().isoformat(),
                "question_length": len(question),
                "answer_length": len(answer),
            }
        )

        output = (
            f"Question: {question}\n"
            f"Answer: {answer}\n"
            f"Model: {model}\n"
            f"Context Count: {context_count}\n"
        )
        if latency_seconds is not None:
            output += f"Latency: {latency_seconds:.2f}s\n"

        with _temp_text_artifact(output) as artifact_path:
            mlflow.log_artifact(artifact_path, artifact_path="rag_output")

        if metadata:
            with _temp_json_artifact(metadata) as artifact_path:
                mlflow.log_artifact(artifact_path, artifact_path="metadata")


def log_ingestion_run(
    file_name: str,
    pages_processed: int,
    chunks_created: int,
    duration_seconds: Optional[float] = None,
    success: bool = True,
    file_size_mb: Optional[float] = None,
    chunk_stats: Optional[Dict[str, Any]] = None,
) -> None:
    setup_mlflow()

    with mlflow.start_run(run_name=f"ingest_{file_name[:30]}"):
        mlflow.log_param("file_name", file_name)
        mlflow.log_param("success", success)

        mlflow.log_metric("pages_processed", pages_processed)
        mlflow.log_metric("chunks_created", chunks_created)
        _log_optional_metric("duration_seconds", duration_seconds)
        _log_optional_metric("file_size_mb", file_size_mb)

        if chunk_stats:
            _log_optional_metric("avg_chunk_size", chunk_stats.get("avg_size"))
            _log_optional_metric("max_chunk_size", chunk_stats.get("max_size"))
            _log_optional_metric("min_chunk_size", chunk_stats.get("min_size"))

        chunks_per_page = chunks_created / pages_processed if pages_processed > 0 else 0
        _set_tags(
            {
                "pipeline": "ingestion",
                "timestamp": datetime.now().isoformat(),
                "status": "success" if success else "failed",
                "chunks_per_page": chunks_per_page,
            }
        )

        stats = {
            "file_name": file_name,
            "pages_processed": pages_processed,
            "chunks_created": chunks_created,
            "duration_seconds": duration_seconds,
            "file_size_mb": file_size_mb,
            "success": success,
            "timestamp": datetime.now().isoformat(),
        }
        if chunk_stats:
            stats.update(chunk_stats)

        with _temp_json_artifact(stats) as artifact_path:
            mlflow.log_artifact(artifact_path, artifact_path="ingestion_stats")


def log_model_performance(
    metrics: Dict[str, Any],
    params: Optional[Dict[str, Any]] = None,
    tags: Optional[Dict[str, Any]] = None,
    confusion_matrix: Optional[List[List[int]]] = None,
) -> None:
    setup_mlflow()

    with mlflow.start_run(run_name="model_evaluation"):
        log_params_batch(params or {})
        log_metrics_batch(metrics)
        _set_tags({"pipeline": "evaluation", "timestamp": datetime.now().isoformat()})
        _set_tags(tags)

        with _temp_json_artifact(metrics) as artifact_path:
            mlflow.log_artifact(artifact_path, artifact_path="metrics")

        if confusion_matrix:
            with _temp_json_artifact({"confusion_matrix": confusion_matrix}) as artifact_path:
                mlflow.log_artifact(artifact_path, artifact_path="matrices")


def log_dataset_used(
    name: str,
    uri: str,
    digest: str,
    source: Optional[str] = None,
    features: Optional[List[str]] = None,
    version: Optional[str] = None,
) -> None:
    setup_mlflow()
    dataset_factory = getattr(mlflow.data, "from_uri", None)
    dataset_input = dataset_factory(uri, digest=digest) if dataset_factory else None

    with mlflow.start_run(run_name=f"dataset_{name}"):
        if dataset_input is not None:
            mlflow.log_input(dataset_input, context="training")
        _set_tags(
            {
                "dataset_name": name,
                "dataset_uri": uri,
                "dataset_digest": digest,
                "dataset_source": source or "unknown",
            }
        )
        if version:
            mlflow.set_tag("dataset_version", version)
        if features:
            mlflow.log_param("features_count", len(features))
            with _temp_json_artifact({"features": features}) as artifact_path:
                mlflow.log_artifact(artifact_path, artifact_path="dataset_info")


def register_model(
    artifact_path: Optional[str],
    model_name: str,
    model_uri: Optional[str] = None,
    description: Optional[str] = None,
    tags_dict: Optional[Dict[str, Any]] = None,
):
    setup_mlflow()

    if artifact_path and os.path.exists(artifact_path):
        with mlflow.start_run(run_name=f"model_registration_{model_name}"):
            mlflow.log_artifact(artifact_path, artifact_path="model")
            model_uri = f"runs:/{mlflow.active_run().info.run_id}/model"

    try:
        result = mlflow.register_model(
            model_uri=model_uri,
            name=model_name,
            tags=tags_dict or {},
            description=description or f"Model: {model_name}",
        )
        logger.info("Model registered", model=model_name)
        return result
    except Exception as exc:
        logger.warning("Failed to register model", error=str(exc))
        return None


def transition_model_stage(model_name: str, version: int, stage: str) -> None:
    setup_mlflow()

    try:
        client = mlflow.tracking.MlflowClient()
        client.transition_model_version_stage(name=model_name, version=version, stage=stage)
        logger.info("Model stage updated", model=model_name, version=version, stage=stage)
    except Exception as exc:
        logger.warning("Failed to transition model", error=str(exc))


def compare_experiments(experiment_ids: List[str], metric_name: str) -> List[Dict[str, Any]]:
    setup_mlflow()
    client = mlflow.tracking.MlflowClient()
    results = []

    for experiment_id in experiment_ids:
        for run in client.search_runs(experiment_ids=[experiment_id]):
            metric_value = run.data.metrics.get(metric_name)
            if metric_value is not None:
                results.append(
                    {
                        "experiment_id": experiment_id,
                        "run_id": run.info.run_id,
                        "run_name": run.info.run_name,
                        metric_name: metric_value,
                    }
                )

    return results


def get_best_runs(experiment_name: str, metric_name: str, max_results: int = 10):
    setup_mlflow()
    client = mlflow.tracking.MlflowClient()
    experiment = mlflow.get_experiment_by_name(experiment_name)
    if not experiment:
        logger.warning("MLflow experiment not found", experiment=experiment_name)
        return []

    return client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=[f"metrics.{metric_name} DESC"],
        max_results=max_results,
    )


def log_custom_metric_history(
    metric_name: str,
    values: List[float],
    step_values: Optional[List[int]] = None,
) -> None:
    steps = step_values if step_values is not None else list(range(len(values)))
    for step, value in zip(steps, values):
        mlflow.log_metric(metric_name, value, step=step)


class MLflowRun:
    """Context manager for MLflow runs."""

    def __init__(self, experiment_name: str, run_name: str, tags: Optional[Dict[str, Any]] = None):
        self.experiment_name = experiment_name
        self.run_name = run_name
        self.tags = tags or {}
        self.run = None

    def __enter__(self):
        set_experiment(self.experiment_name)
        self.run = mlflow.start_run(run_name=self.run_name)
        _set_tags(self.tags)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        mlflow.end_run()
        if exc_type:
            logger.error("MLflow run failed", error=str(exc_val))


def log_params_batch(params: Dict[str, Any]) -> None:
    for key, value in params.items():
        mlflow.log_param(key, value)


def log_metrics_batch(metrics: Dict[str, Any], step: Optional[int] = None) -> None:
    for key, value in metrics.items():
        if isinstance(value, (int, float)):
            mlflow.log_metric(key, value, step=step)


def log_configs_as_artifact(config: Dict[str, Any], artifact_name: str = "config.json") -> None:
    setup_mlflow()
    with _temp_json_artifact(config) as artifact_path:
        mlflow.log_artifact(artifact_path, artifact_path="configs")


def search_runs_by_metric(
    experiment_name: str,
    metric_name: str,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
):
    setup_mlflow()
    client = mlflow.tracking.MlflowClient()
    experiment = mlflow.get_experiment_by_name(experiment_name)
    if not experiment:
        return []

    filters = []
    if min_value is not None:
        filters.append(f"metrics.{metric_name} >= {min_value}")
    if max_value is not None:
        filters.append(f"metrics.{metric_name} <= {max_value}")

    return client.search_runs(
        experiment_ids=[experiment.experiment_id],
        filter_string=" AND ".join(filters) if filters else None,
    )


def get_experiment_summary(experiment_name: str) -> Dict[str, Any]:
    setup_mlflow()
    client = mlflow.tracking.MlflowClient()
    experiment = mlflow.get_experiment_by_name(experiment_name)
    if not experiment:
        return {}

    runs = client.search_runs(experiment_ids=[experiment.experiment_id])
    return {
        "experiment_name": experiment_name,
        "experiment_id": experiment.experiment_id,
        "total_runs": len(runs),
        "runs": [
            {
                "run_id": run.info.run_id,
                "run_name": run.info.run_name,
                "metrics": run.data.metrics,
                "params": run.data.params,
                "tags": run.data.tags,
            }
            for run in runs
        ],
    }


def enable_autolog() -> None:
    setup_mlflow()
    try:
        mlflow.autolog()
        logger.info("MLflow autolog enabled")
    except Exception as exc:
        logger.warning("Failed to enable MLflow autolog", error=str(exc))
