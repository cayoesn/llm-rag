import pytest
from unittest.mock import MagicMock, patch
from embeddings.ollama_client import OllamaEmbedder

def test_ollama_embedder_init():
    with patch('ollama.Client') as mock_client:
        embedder = OllamaEmbedder()
        assert embedder.model == "nomic-embed-text"
        mock_client.assert_called_once()

def test_embed_query_success():
    with patch('ollama.Client') as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.embeddings.return_value = {"embedding": [0.1, 0.2, 0.3]}
        
        embedder = OllamaEmbedder()
        result = embedder.embed_query("hello")
        
        assert result == [0.1, 0.2, 0.3]
        mock_instance.embeddings.assert_called_once_with(model="nomic-embed-text", prompt="hello")

def test_embed_documents():
    with patch('ollama.Client') as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.embeddings.return_value = {"embedding": [0.1, 0.2]}
        
        embedder = OllamaEmbedder()
        texts = ["text1", "text2"]
        result = embedder.embed_documents(texts)
        
        assert len(result) == 2
        assert result[0] == [0.1, 0.2]
        assert mock_instance.embeddings.call_count == 2
