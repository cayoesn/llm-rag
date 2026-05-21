import ollama
from typing import List, Dict, Any
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
        self.langfuse = Langfuse(
            public_key=settings.LANGFUSE_PUBLIC_KEY,
            secret_key=settings.LANGFUSE_SECRET_KEY,
            host=settings.LANGFUSE_HOST
        )

    def answer_question(self, question: str) -> Dict[str, Any]:
        with tracer.start_as_current_span("rag_answer_question") as span:
            span.set_attribute("question", question)
            logger.info("Answering question", question=question)
            
            # Create a trace in Langfuse
            lf_trace = self.langfuse.trace(name="rag-query", input=question)
            
            # 1. Retrieval
            with tracer.start_as_current_span("retrieval"):
                retrieval_span = lf_trace.span(name="retrieval", input=question)
                query_vector = self.embedder.embed_query(question)
                context_docs = self.qdrant.search(query_vector, limit=3)
                retrieval_span.end(output=context_docs)
            
            context_text = "\n\n".join([doc["content"] for doc in context_docs])
            
            # 2. Generation
            with tracer.start_as_current_span("generation"):
                generation = lf_trace.generation(
                    name="generation",
                    model=self.model,
                    input=prompt_from_template(context_text, question),
                )
                
                prompt = prompt_from_template(context_text, question)
                response = self.ollama_client.generate(model=self.model, prompt=prompt)
                
                generation.end(output=response["response"])
            
            lf_trace.update(output=response["response"])
            
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
