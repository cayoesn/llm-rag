from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Dict, Any
import uuid
from embeddings.ollama_client import OllamaEmbedder
from qdrant.manager import QdrantManager
from shared.logging import logger

class IngestionPipeline:
    def __init__(self):
        self.embedder = OllamaEmbedder()
        self.qdrant = QdrantManager()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n", "\n", " ", ""]
        )

    def process_pdf(self, file_path: str):
        logger.info("Processing PDF for ingestion", path=file_path)
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        
        chunks = self.text_splitter.split_documents(documents)
        logger.info("Split PDF into chunks", count=len(chunks))
        
        ids = []
        vectors = []
        payloads = []
        
        texts = [chunk.page_content for chunk in chunks]
        embeddings = self.embedder.embed_documents(texts)
        
        # Determine vector size from first embedding
        if embeddings:
            self.qdrant.create_collection(vector_size=len(embeddings[0]))
        
        for i, chunk in enumerate(chunks):
            doc_id = str(uuid.uuid4())
            ids.append(doc_id)
            vectors.append(embeddings[i])
            payloads.append({
                "content": chunk.page_content,
                "metadata": chunk.metadata,
                "chunk_index": i
            })
            
        self.qdrant.upsert_documents(ids, vectors, payloads)
        logger.info("Ingestion complete", path=file_path)
