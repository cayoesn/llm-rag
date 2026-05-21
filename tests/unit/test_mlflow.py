from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import shared.mlflow_logger as mlflow_logger


def run_stub(**kwargs):
    return SimpleNamespace(
        info=SimpleNamespace(run_id=kwargs.get("run_id", "run-id"), run_name=kwargs.get("run_name", "run")),
        data=SimpleNamespace(
            metrics=kwargs.get("metrics", {}),
            params=kwargs.get("params", {}),
            tags=kwargs.get("tags", {}),
        ),
    )


def test_get_or_create_experiment_returns_existing_id():
    experiment = SimpleNamespace(experiment_id="42")

    with patch.object(mlflow_logger.mlflow, "set_tracking_uri"), patch.object(
        mlflow_logger.mlflow, "get_experiment_by_name", return_value=experiment
    ), patch.object(mlflow_logger.mlflow, "create_experiment") as create_experiment:
        assert mlflow_logger.get_or_create_experiment("existing") == "42"

    create_experiment.assert_not_called()


def test_get_or_create_experiment_creates_missing_experiment():
    with patch.object(mlflow_logger.mlflow, "set_tracking_uri"), patch.object(
        mlflow_logger.mlflow, "get_experiment_by_name", return_value=None
    ), patch.object(mlflow_logger.mlflow, "create_experiment", return_value="7") as create_experiment:
        assert mlflow_logger.get_or_create_experiment("new") == "7"

    create_experiment.assert_called_once_with("new")


def test_set_experiment_configures_active_experiment():
    with patch.object(mlflow_logger, "get_or_create_experiment", return_value="7"), patch.object(
        mlflow_logger.mlflow, "set_experiment"
    ) as set_experiment:
        assert mlflow_logger.set_experiment("rag") == "7"

    set_experiment.assert_called_once_with("rag")


def test_log_rag_run_records_params_metrics_tags_and_artifacts():
    start_run = MagicMock()
    start_run.return_value.__enter__.return_value = None

    with patch.object(mlflow_logger.mlflow, "set_tracking_uri"), patch.object(
        mlflow_logger.mlflow, "start_run", start_run
    ), patch.object(mlflow_logger.mlflow, "log_param") as log_param, patch.object(
        mlflow_logger.mlflow, "log_metric"
    ) as log_metric, patch.object(
        mlflow_logger.mlflow, "set_tag"
    ) as set_tag, patch.object(
        mlflow_logger.mlflow, "log_artifact"
    ) as log_artifact:
        mlflow_logger.log_rag_run(
            question="What is RAG?",
            answer="Retrieval augmented generation.",
            context_count=2,
            model="llama3",
            latency_seconds=0.25,
            retrieval_score=0.9,
            metadata={"source": "test"},
        )

    start_run.assert_called_once_with(run_name="rag_query_What is RAG?")
    log_param.assert_any_call("question", "What is RAG?")
    log_param.assert_any_call("model", "llama3")
    log_metric.assert_any_call("context_retrieved", 2)
    log_metric.assert_any_call("latency_seconds", 0.25)
    log_metric.assert_any_call("retrieval_score", 0.9)
    set_tag.assert_any_call("pipeline", "rag")
    assert log_artifact.call_count == 2


def test_log_ingestion_run_records_chunk_stats_and_artifact():
    start_run = MagicMock()
    start_run.return_value.__enter__.return_value = None

    with patch.object(mlflow_logger.mlflow, "set_tracking_uri"), patch.object(
        mlflow_logger.mlflow, "start_run", start_run
    ), patch.object(mlflow_logger.mlflow, "log_param") as log_param, patch.object(
        mlflow_logger.mlflow, "log_metric"
    ) as log_metric, patch.object(
        mlflow_logger.mlflow, "set_tag"
    ) as set_tag, patch.object(
        mlflow_logger.mlflow, "log_artifact"
    ) as log_artifact:
        mlflow_logger.log_ingestion_run(
            file_name="doc.pdf",
            pages_processed=4,
            chunks_created=12,
            duration_seconds=1.5,
            file_size_mb=2.0,
            chunk_stats={"avg_size": 10, "max_size": 20, "min_size": 5},
        )

    log_param.assert_any_call("file_name", "doc.pdf")
    log_metric.assert_any_call("pages_processed", 4)
    log_metric.assert_any_call("avg_chunk_size", 10)
    set_tag.assert_any_call("chunks_per_page", 3.0)
    log_artifact.assert_called_once()


def test_log_model_performance_records_numeric_metrics_only_and_matrix():
    start_run = MagicMock()
    start_run.return_value.__enter__.return_value = None

    with patch.object(mlflow_logger.mlflow, "set_tracking_uri"), patch.object(
        mlflow_logger.mlflow, "start_run", start_run
    ), patch.object(mlflow_logger.mlflow, "log_param") as log_param, patch.object(
        mlflow_logger.mlflow, "log_metric"
    ) as log_metric, patch.object(
        mlflow_logger.mlflow, "set_tag"
    ) as set_tag, patch.object(
        mlflow_logger.mlflow, "log_artifact"
    ) as log_artifact:
        mlflow_logger.log_model_performance(
            metrics={"accuracy": 0.91, "notes": "ignored"},
            params={"model": "llama3"},
            tags={"dataset": "eval"},
            confusion_matrix=[[1, 0], [0, 1]],
        )

    log_param.assert_called_once_with("model", "llama3")
    log_metric.assert_called_once_with("accuracy", 0.91, step=None)
    set_tag.assert_any_call("pipeline", "evaluation")
    set_tag.assert_any_call("dataset", "eval")
    assert log_artifact.call_count == 2


def test_mlflow_run_context_sets_experiment_tags_and_ends_run():
    with patch.object(mlflow_logger, "set_experiment") as set_experiment, patch.object(
        mlflow_logger.mlflow, "start_run", return_value="run"
    ) as start_run, patch.object(mlflow_logger.mlflow, "set_tag") as set_tag, patch.object(
        mlflow_logger.mlflow, "end_run"
    ) as end_run:
        with mlflow_logger.MLflowRun("exp", "run-name", tags={"env": "test"}) as active:
            assert active.run == "run"

    set_experiment.assert_called_once_with("exp")
    start_run.assert_called_once_with(run_name="run-name")
    set_tag.assert_called_once_with("env", "test")
    end_run.assert_called_once()


def test_search_runs_by_metric_builds_range_filter():
    experiment = SimpleNamespace(experiment_id="9")
    client = MagicMock()
    client.search_runs.return_value = ["run"]

    with patch.object(mlflow_logger.mlflow, "set_tracking_uri"), patch.object(
        mlflow_logger.mlflow, "get_experiment_by_name", return_value=experiment
    ), patch.object(mlflow_logger.mlflow.tracking, "MlflowClient", return_value=client):
        assert mlflow_logger.search_runs_by_metric("exp", "accuracy", 0.8, 0.95) == ["run"]

    client.search_runs.assert_called_once_with(
        experiment_ids=["9"],
        filter_string="metrics.accuracy >= 0.8 AND metrics.accuracy <= 0.95",
    )


def test_get_best_runs_returns_empty_for_missing_experiment():
    with patch.object(mlflow_logger.mlflow, "set_tracking_uri"), patch.object(
        mlflow_logger.mlflow, "get_experiment_by_name", return_value=None
    ), patch.object(mlflow_logger.mlflow.tracking, "MlflowClient") as client_class:
        assert mlflow_logger.get_best_runs("missing", "accuracy") == []

    client_class.return_value.search_runs.assert_not_called()


def test_get_experiment_summary_serializes_runs():
    experiment = SimpleNamespace(experiment_id="3")
    client = MagicMock()
    client.search_runs.return_value = [
        run_stub(run_id="r1", run_name="one", metrics={"score": 1.0}, params={"p": "v"}, tags={"t": "x"})
    ]

    with patch.object(mlflow_logger.mlflow, "set_tracking_uri"), patch.object(
        mlflow_logger.mlflow, "get_experiment_by_name", return_value=experiment
    ), patch.object(mlflow_logger.mlflow.tracking, "MlflowClient", return_value=client):
        summary = mlflow_logger.get_experiment_summary("exp")

    assert summary["total_runs"] == 1
    assert summary["runs"][0]["run_id"] == "r1"
    assert summary["runs"][0]["metrics"] == {"score": 1.0}


def test_compare_experiments_keeps_runs_with_metric():
    client = MagicMock()
    client.search_runs.side_effect = [
        [run_stub(run_id="a", run_name="first", metrics={"score": 0.7})],
        [run_stub(run_id="b", run_name="second", metrics={})],
    ]

    with patch.object(mlflow_logger.mlflow, "set_tracking_uri"), patch.object(
        mlflow_logger.mlflow.tracking, "MlflowClient", return_value=client
    ):
        result = mlflow_logger.compare_experiments(["1", "2"], "score")

    assert result == [{"experiment_id": "1", "run_id": "a", "run_name": "first", "score": 0.7}]


def test_register_model_logs_existing_artifact_and_registers_model(tmp_path):
    model_file = tmp_path / "model.bin"
    model_file.write_text("model")
    active_run = SimpleNamespace(info=SimpleNamespace(run_id="abc"))

    start_run = MagicMock()
    start_run.return_value.__enter__.return_value = None

    with patch.object(mlflow_logger.mlflow, "set_tracking_uri"), patch.object(
        mlflow_logger.mlflow, "start_run", start_run
    ), patch.object(mlflow_logger.mlflow, "log_artifact") as log_artifact, patch.object(
        mlflow_logger.mlflow, "active_run", return_value=active_run
    ), patch.object(
        mlflow_logger.mlflow, "register_model", return_value="registered"
    ) as register_model:
        result = mlflow_logger.register_model(str(model_file), "model-name")

    assert result == "registered"
    log_artifact.assert_called_once_with(str(model_file), artifact_path="model")
    register_model.assert_called_once()
    assert register_model.call_args.kwargs["model_uri"] == "runs:/abc/model"


def test_transition_model_stage_uses_tracking_client():
    client = MagicMock()

    with patch.object(mlflow_logger.mlflow, "set_tracking_uri"), patch.object(
        mlflow_logger.mlflow.tracking, "MlflowClient", return_value=client
    ):
        mlflow_logger.transition_model_stage("model", 2, "Production")

    client.transition_model_version_stage.assert_called_once_with(
        name="model", version=2, stage="Production"
    )


def test_log_dataset_used_records_features():
    start_run = MagicMock()
    start_run.return_value.__enter__.return_value = None
    dataset = object()

    with patch.object(mlflow_logger.mlflow, "set_tracking_uri"), patch.object(
        mlflow_logger.mlflow.data, "from_uri", return_value=dataset, create=True
    ), patch.object(mlflow_logger.mlflow, "start_run", start_run), patch.object(
        mlflow_logger.mlflow, "log_input"
    ) as log_input, patch.object(
        mlflow_logger.mlflow, "set_tag"
    ) as set_tag, patch.object(
        mlflow_logger.mlflow, "log_param"
    ) as log_param, patch.object(
        mlflow_logger.mlflow, "log_artifact"
    ) as log_artifact:
        mlflow_logger.log_dataset_used(
            name="dataset",
            uri="s3://bucket/data.csv",
            digest="abc",
            source="s3",
            features=["question", "answer"],
            version="1",
        )

    log_input.assert_called_once_with(dataset, context="training")
    set_tag.assert_any_call("dataset_source", "s3")
    set_tag.assert_any_call("dataset_uri", "s3://bucket/data.csv")
    set_tag.assert_any_call("dataset_digest", "abc")
    set_tag.assert_any_call("dataset_version", "1")
    log_param.assert_called_once_with("features_count", 2)
    log_artifact.assert_called_once()


def test_log_dataset_used_skips_input_when_uri_factory_is_unavailable():
    start_run = MagicMock()
    start_run.return_value.__enter__.return_value = None
    original_from_uri = getattr(mlflow_logger.mlflow.data, "from_uri", None)

    if original_from_uri is not None:
        delattr(mlflow_logger.mlflow.data, "from_uri")

    try:
        with patch.object(mlflow_logger.mlflow, "set_tracking_uri"), patch.object(
            mlflow_logger.mlflow, "start_run", start_run
        ), patch.object(mlflow_logger.mlflow, "log_input") as log_input, patch.object(
            mlflow_logger.mlflow, "set_tag"
        ) as set_tag:
            mlflow_logger.log_dataset_used("dataset", "file://data.csv", "digest")
    finally:
        if original_from_uri is not None:
            setattr(mlflow_logger.mlflow.data, "from_uri", original_from_uri)

    log_input.assert_not_called()
    set_tag.assert_any_call("dataset_uri", "file://data.csv")


def test_batch_helpers_and_autolog():
    with patch.object(mlflow_logger.mlflow, "log_param") as log_param, patch.object(
        mlflow_logger.mlflow, "log_metric"
    ) as log_metric:
        mlflow_logger.log_params_batch({"a": 1})
        mlflow_logger.log_metrics_batch({"m": 2.5, "skip": "text"}, step=4)
        mlflow_logger.log_custom_metric_history("loss", [0.3, 0.2])

    log_param.assert_called_once_with("a", 1)
    log_metric.assert_any_call("m", 2.5, step=4)
    log_metric.assert_any_call("loss", 0.3, step=0)
    log_metric.assert_any_call("loss", 0.2, step=1)

    with patch.object(mlflow_logger.mlflow, "set_tracking_uri"), patch.object(
        mlflow_logger.mlflow, "autolog"
    ) as autolog:
        mlflow_logger.enable_autolog()

    autolog.assert_called_once()
