import pytest
from unittest.mock import MagicMock, patch
from qdrant.manager import QdrantManager

@patch('qdrant.manager.QdrantClient')
def test_qdrant_create_collection(mock_qdrant_client):
    mock_instance = mock_qdrant_client.return_value
    mock_instance.collection_exists.return_value = False
    
    manager = QdrantManager()
    manager.create_collection(vector_size=128)
    
    mock_instance.create_collection.assert_called_once()
    assert manager.collection_name == "llm_rag_docs"

@patch('qdrant.manager.QdrantClient')
def test_qdrant_upsert(mock_qdrant_client):
    mock_instance = mock_qdrant_client.return_value
    manager = QdrantManager()
    
    manager.upsert_documents(
        ids=["1"],
        vectors=[[0.1, 0.2]],
        payloads=[{"text": "test"}]
    )
    
    mock_instance.upsert.assert_called_once()

@patch('qdrant.manager.QdrantClient')
def test_qdrant_search(mock_qdrant_client):
    mock_instance = mock_qdrant_client.return_value
    mock_hit = MagicMock()
    mock_hit.id = "point-1"
    mock_hit.payload = {"content": "found", "metadata": {"source": "test"}}
    mock_instance.query_points.return_value = MagicMock(points=[mock_hit])
    
    manager = QdrantManager()
    results = manager.search(vector=[0.1, 0.2])
    
    assert len(results) == 1
    assert results[0]["id"] == "point-1"
    assert results[0]["content"] == "found"
    assert results[0]["metadata"] == {"source": "test"}
