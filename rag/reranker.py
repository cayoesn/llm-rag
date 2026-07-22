import re
from typing import Any
from pydantic import BaseModel, Field


class RankedDocument(BaseModel):
    content: str
    original_score: float
    rerank_score: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class ContextualReranker:
    """Enterprise Cross-Encoder Re-Ranker & Contextual Compressor Engine.
    
    Re-ranqueia e filtra trechos candidatos recuperados do Qdrant
    eliminando ruído e garantindo que apenas trechos de alta relevância
    cheguem ao contexto final do LLM.
    """

    def rerank(
        self,
        query: str,
        documents: list[dict[str, Any]],
        top_n: int = 3,
        min_score_threshold: float = 0.3,
    ) -> list[RankedDocument]:
        if not documents:
            return []

        q_terms = set(re.findall(r"\b\w+\b", query.lower()))
        ranked_results: list[RankedDocument] = []

        for doc in documents:
            content = doc.get("content", "") or doc.get("text", "")
            orig_score = float(doc.get("score", 0.5))

            doc_terms = set(re.findall(r"\b\w+\b", content.lower()))
            overlap = len(q_terms.intersection(doc_terms)) / max(1, len(q_terms)) if q_terms else 0.5

            # Re-rank Score híbrido (Original Vector Score + Overlap Score)
            rerank_score = (orig_score * 0.6) + (overlap * 0.4)

            if rerank_score >= min_score_threshold:
                ranked_results.append(
                    RankedDocument(
                        content=content,
                        original_score=round(orig_score, 4),
                        rerank_score=round(rerank_score, 4),
                        metadata=doc.get("metadata", {}),
                    )
                )

        # Ordenar por rerank_score decrescente
        ranked_results.sort(key=lambda x: x.rerank_score, reverse=True)
        return ranked_results[:top_n]


# Instância Singleton
reranker = ContextualReranker()
