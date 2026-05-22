from unittest.mock import MagicMock, patch

from rag.service import RAGService, prompt_from_template


def make_service(context_docs=None):
    service = RAGService.__new__(RAGService)
    service.embedder = MagicMock()
    service.embedder.embed_query.return_value = [0.1, 0.2]
    service.qdrant = MagicMock()
    service.qdrant.search.return_value = context_docs or [
        {"content": "known fact", "metadata": {}}
    ]
    service.ollama_client = MagicMock()
    service.ollama_client.generate.return_value = {"response": "answer"}
    service.model = "llama3"
    service.langfuse = None
    return service


def test_prompt_from_template_includes_context_and_question():
    prompt = prompt_from_template("context text", "question?")

    assert "context text" in prompt
    assert "question?" in prompt
    assert prompt.endswith("Answer:")


def test_answer_question_retrieves_generates_logs_and_returns_payload():
    service = make_service()

    with patch("rag.service.log_rag_run") as log_rag_run:
        result = service.answer_question("What is known?")

    service.embedder.embed_query.assert_called_once_with("What is known?")
    service.qdrant.search.assert_called_once_with([0.1, 0.2], limit=3)
    service.ollama_client.generate.assert_called_once()
    assert "known fact" in service.ollama_client.generate.call_args.kwargs["prompt"]
    log_rag_run.assert_called_once()
    assert result == {
        "answer": "answer",
        "context": [{"content": "known fact", "metadata": {}}],
        "model": "llama3",
    }


def test_answer_question_continues_when_mlflow_logging_fails():
    service = make_service(context_docs=[])

    with patch("rag.service.log_rag_run", side_effect=RuntimeError("mlflow down")):
        result = service.answer_question("Unknown?")

    assert result["answer"] == "answer"
    service.ollama_client.generate.assert_called_once()
