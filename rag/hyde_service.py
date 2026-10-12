import asyncio
import re
from typing import Any, Awaitable, Callable

_KEYWORD_PATTERN = re.compile(r"\b\w{3,}\b")


class HyDEService:
    """Enterprise HyDE (Hypothetical Document Embeddings) Engine.
    
    Transforms sparse or ambiguous user questions into dense, informative
    hypothetical documents prior to embedding calculation.
    
    Features:
    1. Asynchronous generation with custom LLM generator hook.
    2. Zero-latency deterministic fallback with domain expansion.
    3. Multi-domain hypothetical passage synthesis.
    """

    def __init__(
        self,
        llm_generator: Callable[[str], Awaitable[str]] | None = None,
    ) -> None:
        self.llm_generator = llm_generator

    def generate_hypothetical_document(self, query: str, domain: str = "general") -> str:
        """Generates a synchronous hypothetical document with deterministic domain enrichment."""
        cleaned_query = query.strip()
        if not cleaned_query:
            return ""

        keywords = list(dict.fromkeys(_KEYWORD_PATTERN.findall(cleaned_query.lower())))
        keywords_summary = ", ".join(keywords[:6]) if keywords else cleaned_query

        if domain.lower() == "technical":
            return (
                f"Documento Informativo Corporativo de Especificação Técnica sobre: {cleaned_query}.\n"
                f"Arquitetura de sistemas, protocolos, fluxos assíncronos e contratos de API relacionados a {keywords_summary}. "
                f"Diretrizes técnicas para implementação, segurança de dados e monitoramento em produção."
            )

        return (
            f"Documento Informativo Corporativo sobre: {cleaned_query}.\n"
            f"Este documento descreve detalhadamente as políticas, especificações técnicas "
            f"e diretrizes relacionadas a {cleaned_query}. Inclui regras, procedimentos, "
            f"definições operacionais e termos-chave como {keywords_summary} para esclarecimento completo."
        )

    async def generate_hypothetical_document_async(
        self,
        query: str,
        domain: str = "general",
        timeout_seconds: float = 2.0,
    ) -> str:
        """Asynchronously generates hypothetical document using LLM or falls back on timeout."""
        cleaned_query = query.strip()
        if not cleaned_query:
            return ""

        if self.llm_generator is not None:
            try:
                task = self.llm_generator(cleaned_query)
                return await asyncio.wait_for(task, timeout=timeout_seconds)
            except Exception:
                # Graceful degradation on LLM timeout or connection failure
                pass

        return self.generate_hypothetical_document(cleaned_query, domain=domain)


# Singleton instance
hyde_service = HyDEService()
