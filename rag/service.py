import ollama
from typing import Dict, Any
from langfuse import Langfuse
from embeddings.ollama_client import OllamaEmbedder
from qdrant.manager import QdrantManager
from config.settings import settings
from shared.logging import logger
from shared.otel import tracer

class RAGService:
    def __init__(self):
        self.embedder = OllamaEmbedder()
        self.qdrant = QdrantManager()
        self.ollama_client = ollama.Client(host=settings.OLLAMA_BASE_URL)
        self.model = settings.LLM_MODEL
        
        # Initialize Langfuse only if keys and a supported API are available
        self.langfuse = None
        if settings.LANGFUSE_PUBLIC_KEY and settings.LANGFUSE_SECRET_KEY:
            try:
                lf = Langfuse(
                    public_key=settings.LANGFUSE_PUBLIC_KEY,
                    secret_key=settings.LANGFUSE_SECRET_KEY,
                    host=settings.LANGFUSE_HOST
                )
                if hasattr(lf, "observe") or hasattr(lf, "trace"):
                    self.langfuse = lf
                else:
                    logger.warning("Langfuse SDK does not support observe/trace, tracing disabled")
            except Exception as e:
                logger.warning(f"Failed to initialize Langfuse: {e}, tracing disabled")

    def answer_question(self, question: str) -> Dict[str, Any]:
        with tracer.start_as_current_span("rag_answer_question") as span:
            span.set_attribute("question", question)
            logger.info("Answering question", question=question)
            
            # 1. Retrieval
            with tracer.start_as_current_span("retrieval"):
                query_vector = self.embedder.embed_query(question)
                context_docs = self.qdrant.search(query_vector, limit=3)
                logger.info("Retrieved context docs", count=len(context_docs), docs=context_docs)
            
            if not context_docs:
                logger.warning("No context documents found for question", question=question)
            
            context_text = "\n\n".join([doc["content"] for doc in context_docs])
            
            # 2. Generation
            with tracer.start_as_current_span("generation"):
                prompt = prompt_from_template(context_text, question)
                response = self.ollama_client.generate(model=self.model, prompt=prompt)
            
            if self.langfuse:
                try:
                    if hasattr(self.langfuse, "observe"):
                        self.langfuse.observe(
                            name="rag-query",
                            input={"question": question},
                            output={"answer": response["response"]},
                            model=self.model
                        )
                    else:
                        logger.debug("Langfuse client initialized but no supported logging method found")
                except Exception as e:
                    logger.warning(f"Failed to log to Langfuse: {e}")
            
            return {
                "answer": response["response"],
                "context": context_docs,
                "model": self.model
            }

    def answer_question(self, question: str) -> Dict[str, Any]:
        with tracer.start_as_current_span("rag_answer_question") as span:
            span.set_attribute("question", question)
            logger.info("Answering question", question=question)
            
            # 1. Retrieval
            with tracer.start_as_current_span("retrieval"):
                query_vector = self.embedder.embed_query(question)
                context_docs = self.qdrant.search(query_vector, limit=3)
            
            context_text = "\n\n".join([doc["content"] for doc in context_docs])
            
            # 2. Generation
            with tracer.start_as_current_span("generation"):
                prompt = prompt_from_template(context_text, question)
                response = self.ollama_client.generate(model=self.model, prompt=prompt)
            
            # Log to Langfuse if available
            if self.langfuse:
                try:
                    # Use Langfuse SDK observation method
                    self.langfuse.observe(
                        name="rag-query",
                        input={"question": question},
                        output={"answer": response["response"]},
                        model=self.model
                    )
                except Exception as e:
                    logger.warning(f"Failed to log to Langfuse: {e}")
            
            return {
                "answer": response["response"],
                "context": context_docs,
                "model": self.model
            }

def prompt_from_template(context: str, question: str) -> str:
    return f"""Use the following context to answer the question. If you don't know the answer, just say you don't know.

Context:
{context}

Question: {question}

Answer:"""
