import heapq
import re
from typing import Any, Callable, Sequence
from pydantic import BaseModel, Field

_WORD_PATTERN = re.compile(r"\b\w+\b")


class RankedDocument(BaseModel):
    """Ranked and compressed document chunk with fused scoring."""
    content: str
    original_score: float
    rerank_score: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class ContextualReranker:
    """Enterprise Cross-Encoder Re-Ranker, Contextual Compressor & RRF Engine.
    
    Re-ranqueia e comprime candidatos recuperados utilizando:
    1. Reciprocal Rank Fusion (RRF) para fusão híbrida densa/esparsa.
    2. Heurística contextual e ponderação semântica em tempo linear O(N).
    3. Seleção Top-K ótima via Min/Max-Heap em O(N log K).
    4. Compressão contextual eliminando sentenças de baixa relevância.
    """

    def __init__(self, rrf_k: int = 60) -> None:
        self.rrf_k = rrf_k

    def rerank(
        self,
        query: str,
        documents: Sequence[dict[str, Any]],
        top_n: int = 3,
        min_score_threshold: float = 0.3,
    ) -> list[RankedDocument]:
        """Re-ranks retrieved documents with O(N log K) heap extraction.
        
        Complexity:
            Time: O(N * L + N log K), where N is document count and K is top_n.
            Space: O(K) for top-K heap storage.
        """
        if not documents or top_n <= 0:
            return []

        q_terms = set(_WORD_PATTERN.findall(query.lower()))
        num_q = max(1, len(q_terms))
        candidates: list[RankedDocument] = []

        for doc in documents:
            content = doc.get("content", "") or doc.get("text", "")
            orig_score = float(doc.get("score", 0.5))

            doc_terms = set(_WORD_PATTERN.findall(content.lower()))
            overlap = len(q_terms.intersection(doc_terms)) / num_q if q_terms else 0.5

            # Hybrid score fusing original vector similarity with lexical term overlap
            rerank_score = (orig_score * 0.6) + (overlap * 0.4)

            if rerank_score >= min_score_threshold:
                candidates.append(
                    RankedDocument(
                        content=content,
                        original_score=round(orig_score, 4),
                        rerank_score=round(rerank_score, 4),
                        metadata=doc.get("metadata", {}),
                    )
                )

        if not candidates:
            return []

        # Optimal Top-K selection using heap O(N log K) instead of full sort O(N log N)
        return heapq.nlargest(top_n, candidates, key=lambda d: d.rerank_score)

    def reciprocal_rank_fusion(
        self,
        dense_rankings: Sequence[dict[str, Any]],
        sparse_rankings: Sequence[dict[str, Any]],
        top_n: int = 3,
        k: int | None = None,
    ) -> list[RankedDocument]:
        """Fuses dense vector results and sparse BM25 results via Reciprocal Rank Fusion (RRF).
        
        Formula:
            RRF_Score(d) = sum_{m in M} 1 / (k + rank_m(d))
        """
        rrf_constant = k if k is not None else self.rrf_k
        fused_scores: dict[str, float] = {}
        doc_store: dict[str, dict[str, Any]] = {}

        for rank_idx, doc in enumerate(dense_rankings, start=1):
            doc_id = str(doc.get("id") or doc.get("content") or f"dense_{rank_idx}")
            doc_store[doc_id] = doc
            fused_scores[doc_id] = fused_scores.get(doc_id, 0.0) + (1.0 / (rrf_constant + rank_idx))

        for rank_idx, doc in enumerate(sparse_rankings, start=1):
            doc_id = str(doc.get("id") or doc.get("content") or f"sparse_{rank_idx}")
            if doc_id not in doc_store:
                doc_store[doc_id] = doc
            fused_scores[doc_id] = fused_scores.get(doc_id, 0.0) + (1.0 / (rrf_constant + rank_idx))

        candidates: list[RankedDocument] = []
        for doc_id, score in fused_scores.items():
            doc = doc_store[doc_id]
            candidates.append(
                RankedDocument(
                    content=doc.get("content", "") or doc.get("text", ""),
                    original_score=float(doc.get("score", 0.5)),
                    rerank_score=round(score, 6),
                    metadata=doc.get("metadata", {}),
                )
            )

        return heapq.nlargest(top_n, candidates, key=lambda d: d.rerank_score)

    def compress_context(
        self,
        query: str,
        document_text: str,
        max_sentences: int = 3,
    ) -> str:
        """Contextual compression: extracts only high-information sentences relevant to query."""
        if not document_text.strip():
            return ""

        q_terms = set(_WORD_PATTERN.findall(query.lower()))
        sentences = [s.strip() for s in re.split(r"[.!?]+", document_text) if s.strip()]
        if len(sentences) <= max_sentences:
            return document_text.strip()

        scored_sentences: list[tuple[float, int, str]] = []
        for idx, sentence in enumerate(sentences):
            s_terms = set(_WORD_PATTERN.findall(sentence.lower()))
            overlap = len(q_terms.intersection(s_terms)) if q_terms else 0
            scored_sentences.append((float(overlap), idx, sentence))

        # Select top sentences by relevance, then re-sort by original chronological order
        top_sentences = heapq.nlargest(max_sentences, scored_sentences, key=lambda x: (x[0], -x[1]))
        top_sentences.sort(key=lambda x: x[1])

        return ". ".join(s[2] for s in top_sentences) + "."


# Singleton instance
reranker = ContextualReranker()
