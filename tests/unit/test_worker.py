from unittest.mock import MagicMock, patch

import pytest

from worker.main import process_ingestion_task


def test_process_ingestion_task_runs_pipeline():
    pipeline = MagicMock()

    with patch("worker.main.IngestionPipeline", return_value=pipeline):
        process_ingestion_task("uploads/doc.pdf")

    pipeline.process_pdf.assert_called_once_with("uploads/doc.pdf")


def test_process_ingestion_task_reraises_pipeline_errors():
    pipeline = MagicMock()
    pipeline.process_pdf.side_effect = RuntimeError("failed")

    with (
        patch("worker.main.IngestionPipeline", return_value=pipeline),
        pytest.raises(RuntimeError),
    ):
        process_ingestion_task("uploads/doc.pdf")
