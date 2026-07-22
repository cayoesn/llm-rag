import pytest
from rag.hyde_service import HyDEService, hyde_service
from rag.reranker import ContextualReranker, reranker


def test_hyde_document_generation():
    service = HyDEService()
    doc = service.generate_hypothetical_document("política de devolução de produtos")
    assert "Documento Informativo Corporativo" in doc
    assert "política de devolução de produtos" in doc


def test_contextual_reranker():
    query = "devolução de produtos prazo"
    documents = [
        {"content": "A política de devolução permite trocas em até 30 dias.", "score": 0.8},
        {"content": "O catálogo possui eletrônicos e acessórios com frete grátis.", "score": 0.75},
    ]

    ranked = reranker.rerank(query, documents, top_n=1)
    assert len(ranked) == 1
    assert "30 dias" in ranked[0].content
    assert ranked[0].rerank_score > 0.3
