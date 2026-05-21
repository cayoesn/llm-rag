import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@patch("rag.service.RAGService.answer_question")
def test_chat_endpoint(mock_answer):
    mock_answer.return_value = {
        "answer": "Test answer",
        "context": [{"content": "source"}],
        "model": "llama3"
    }
    
    response = client.post("/chat", json={"message": "What is LLM-RAG?"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "Test answer"
    assert data["model"] == "llama3"

@patch("rq.Queue.enqueue")
def test_ingest_endpoint(mock_enqueue):
    mock_job = MagicMock()
    mock_job.id = "job_123"
    mock_enqueue.return_value = mock_job
    
    # Create a dummy PDF content
    pdf_content = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"
    
    response = client.post(
        "/ingest",
        files={"file": ("test.pdf", pdf_content, "application/pdf")}
    )
    
    assert response.status_code == 200
    assert "job_id" in response.json()
    assert response.json()["job_id"] == "job_123"

def test_ingest_wrong_file_type():
    response = client.post(
        "/ingest",
        files={"file": ("test.txt", b"hello", "text/plain")}
    )
    assert response.status_code == 400
    assert "Only PDF files are supported" in response.json()["detail"]
