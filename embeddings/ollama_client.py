import ollama
from typing import List
from tenacity import retry, stop_after_attempt, wait_exponential
from config.settings import settings
from shared.logging import logger

class OllamaEmbedder:
    def __init__(self):
        self.client = ollama.Client(host=settings.OLLAMA_BASE_URL)
        self.model = settings.EMBEDDING_MODEL

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def embed_query(self, text: str) -> List[float]:
        try:
            response = self.client.embeddings(model=self.model, prompt=text)
            return response["embedding"]
        except Exception as e:
            logger.error("Error generating embedding", error=str(e), text=text[:50])
            raise

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_query(text) for text in texts]
