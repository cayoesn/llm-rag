from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Any
from config.settings import settings
from shared.logging import logger

class QdrantManager:
    def __init__(self):
        self.client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
        self.collection_name = settings.QDRANT_COLLECTION_NAME

    def create_collection(self, vector_size: int):
        if not self.client.collection_exists(self.collection_name):
            logger.info("Creating Qdrant collection", collection=self.collection_name, size=vector_size)
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE),
            )

    def upsert_documents(self, ids: List[str], vectors: List[List[float]], payloads: List[Dict[str, Any]]):
        self.client.upsert(
            collection_name=self.collection_name,
            points=models.Batch(
                ids=ids,
                vectors=vectors,
                payloads=payloads
            )
        )
        logger.info("Upserted documents to Qdrant", count=len(ids))

    def search(self, vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            limit=limit,
            with_payload=True
        )
        return [res.payload for res in results]
