from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from ingestion.pipeline import IngestionPipeline


def make_pipeline():
    pipeline = IngestionPipeline.__new__(IngestionPipeline)
    pipeline.embedder = MagicMock()
    pipeline.qdrant = MagicMock()
    pipeline.text_splitter = MagicMock()
    return pipeline


def test_process_pdf_embeds_chunks_upserts_and_logs_success(tmp_path):
    file_path = tmp_path / "doc.pdf"
    file_path.write_bytes(b"%PDF")
    document = SimpleNamespace(page_content="page", metadata={"page": 1})
    chunks = [
        SimpleNamespace(page_content="chunk one", metadata={"page": 1}),
        SimpleNamespace(page_content="chunk two", metadata={"page": 1}),
    ]
    pipeline = make_pipeline()
    pipeline.text_splitter.split_documents.return_value = chunks
    pipeline.embedder.embed_documents.return_value = [[0.1, 0.2], [0.3, 0.4]]

    loader = MagicMock()
    loader.load.return_value = [document]

    with patch("ingestion.pipeline.PyPDFLoader", return_value=loader), patch(
        "ingestion.pipeline.log_ingestion_run"
    ) as log_ingestion, patch("ingestion.pipeline.uuid.uuid4", side_effect=["id-1", "id-2"]):
        pipeline.process_pdf(str(file_path))

    pipeline.embedder.embed_documents.assert_called_once_with(["chunk one", "chunk two"])
    pipeline.qdrant.create_collection.assert_called_once_with(vector_size=2)
    pipeline.qdrant.upsert_documents.assert_called_once()
    ids, vectors, payloads = pipeline.qdrant.upsert_documents.call_args.args
    assert ids == ["id-1", "id-2"]
    assert vectors == [[0.1, 0.2], [0.3, 0.4]]
    assert payloads[0]["content"] == "chunk one"
    log_ingestion.assert_called_once()
    assert log_ingestion.call_args.kwargs["success"] is True
    assert log_ingestion.call_args.kwargs["pages_processed"] == 1
    assert log_ingestion.call_args.kwargs["chunks_created"] == 2


def test_process_pdf_logs_failure_and_reraises(tmp_path):
    file_path = tmp_path / "broken.pdf"
    file_path.write_bytes(b"bad")
    pipeline = make_pipeline()
    loader = MagicMock()
    loader.load.side_effect = RuntimeError("bad pdf")

    with patch("ingestion.pipeline.PyPDFLoader", return_value=loader), patch(
        "ingestion.pipeline.log_ingestion_run"
    ) as log_ingestion, pytest.raises(RuntimeError, match="bad pdf"):
        pipeline.process_pdf(str(file_path))

    log_ingestion.assert_called_once()
    assert log_ingestion.call_args.kwargs["success"] is False
    assert log_ingestion.call_args.kwargs["pages_processed"] == 0
    pipeline.qdrant.upsert_documents.assert_not_called()
