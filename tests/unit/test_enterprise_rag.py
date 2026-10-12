import asyncio
import pytest
from rag.hyde_service import HyDEService, hyde_service
from rag.reranker import ContextualReranker, reranker


def test_hyde_document_generation():
    service = HyDEService()
    doc = service.generate_hypothetical_document("política de devolução de produtos")
    assert "Documento Informativo Corporativo" in doc
    assert "política de devolução de produtos" in doc


def test_hyde_technical_domain_generation():
    service = HyDEService()
    doc = service.generate_hypothetical_document("protocolo de mensageria assíncrona", domain="technical")
    assert "Especificação Técnica" in doc
    assert "protocolo de mensageria assíncrona" in doc


@pytest.mark.asyncio
async def test_hyde_async_generation_with_llm_callback():
    async def mock_llm_generator(prompt: str) -> str:
        await asyncio.sleep(0.01)
        return f"Documento Sintético LLM: Resposta aprofundada para {prompt}"

    service = HyDEService(llm_generator=mock_llm_generator)
    doc = await service.generate_hypothetical_document_async("como configurar o cluster kubernetes?")
    assert "Documento Sintético LLM" in doc
    assert "kubernetes" in doc


@pytest.mark.asyncio
async def test_hyde_async_fallback_on_llm_timeout():
    async def slow_llm_generator(prompt: str) -> str:
        await asyncio.sleep(1.0)
        return "Demorou demais"

    service = HyDEService(llm_generator=slow_llm_generator)
    # Should fall back gracefully to deterministic generation
    doc = await service.generate_hypothetical_document_async("termo de adesão", timeout_seconds=0.05)
    assert "Documento Informativo Corporativo" in doc
    assert "termo de adesão" in doc


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


def test_contextual_reranker_heapq_top_k_efficiency():
    query = "performance de banco de dados postgresql"
    # Create 50 candidate documents
    documents = [
        {"content": f"Documento sobre tópico aleatório {i} sem menção ao assunto", "score": 0.4}
        for i in range(48)
    ]
    # Add 2 highly relevant documents
    documents.append({"content": "Guia de tuning de postgresql e índices para alta performance", "score": 0.95})
    documents.append({"content": "Dicas de performance e conexão em bancos de dados postgresql", "score": 0.90})

    ranked = reranker.rerank(query, documents, top_n=2)
    assert len(ranked) == 2
    assert "postgresql" in ranked[0].content
    assert "postgresql" in ranked[1].content
    assert ranked[0].rerank_score >= ranked[1].rerank_score


def test_reciprocal_rank_fusion():
    dense_results = [
        {"id": "doc1", "content": "Introdução a Redes Neurais", "score": 0.9},
        {"id": "doc2", "content": "Algoritmos Genéticos e Busca", "score": 0.85},
        {"id": "doc3", "content": "Transformers e Atenção Causal", "score": 0.8},
    ]
    sparse_results = [
        {"id": "doc3", "content": "Transformers e Atenção Causal", "score": 0.95},
        {"id": "doc1", "content": "Introdução a Redes Neurais", "score": 0.7},
        {"id": "doc4", "content": "Sistemas Especialistas Clássicos", "score": 0.6},
    ]

    fused = reranker.reciprocal_rank_fusion(dense_results, sparse_results, top_n=3, k=60)
    assert len(fused) == 3
    # Both doc1 and doc3 appeared in both lists, so they should rank highest
    top_ids = [d.metadata.get("id") or d.content for d in fused]
    assert any("Transformers" in c for c in top_ids[:2])
    assert any("Redes Neurais" in c for c in top_ids[:2])


def test_contextual_compression():
    query = "garantia estendida defeitos"
    text = (
        "Nosso catálogo inclui centenas de produtos de ponta. "
        "A garantia estendida cobre defeitos de fabricação por até 24 meses. "
        "As entregas são feitas via transportadora parceira em todo o país. "
        "Em caso de defeitos, o cliente pode acionar o reparo sem custo adicional."
    )

    compressed = reranker.compress_context(query, text, max_sentences=2)
    assert "garantia estendida" in compressed
    assert "defeitos" in compressed
    # The irrelevant sentences about delivery and product catalog should be excluded
    assert "transportadora" not in compressed
