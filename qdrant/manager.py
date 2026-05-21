from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Any
from config.settings import settings
from shared.logging import logger

class QdrantManager:
    def __init__(self):
        try:
            self.client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
            self.collection_name = settings.QDRANT_COLLECTION_NAME
            logger.info("Connected to Qdrant", host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
        except Exception as e:
            logger.error("Failed to connect to Qdrant", error=str(e))
            self.client = None

    def create_collection(self, vector_size: int):
        if not self.client:
            logger.error("Qdrant client not initialized")
            return
            
        try:
            if not self.client.collection_exists(self.collection_name):
                logger.info("Creating Qdrant collection", collection=self.collection_name, size=vector_size)
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE),
                )
            else:
                logger.info("Qdrant collection already exists", collection=self.collection_name)
        except Exception as e:
            logger.error("Failed to create Qdrant collection", error=str(e))

    def upsert_documents(self, ids: List[str], vectors: List[List[float]], payloads: List[Dict[str, Any]]):
        if not self.client:
            logger.error("Qdrant client not initialized")
            return
            
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=models.Batch(
                    ids=ids,
                    vectors=vectors,
                    payloads=payloads
                )
            )
            logger.info("Upserted documents to Qdrant", count=len(ids))
        except Exception as e:
            logger.error("Failed to upsert documents", error=str(e))

    def search(self, vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        if not self.client:
            logger.error("Qdrant client not initialized, returning empty results")
            return []
            
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=vector,
                limit=limit,
                with_payload=True
            )
            logger.info("Search completed", results_count=len(results))
            return [{"id": res.id, "content": res.payload.get("content", ""), "metadata": res.payload.get("metadata", {})} for res in results]
        except Exception as e:
            logger.error("Search failed", error=str(e))
            return []

