from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import uuid
import time
import os
from embeddings.ollama_client import OllamaEmbedder
from qdrant.manager import QdrantManager
from shared.logging import logger
from shared.mlflow_logger import log_ingestion_run


class IngestionPipeline:
    def __init__(self):
        self.embedder = OllamaEmbedder()
        self.qdrant = QdrantManager()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=100, separators=["\n\n", "\n", " ", ""]
        )

    def process_pdf(self, file_path: str):
        start_time = time.time()
        file_name = os.path.basename(file_path)

        try:
            logger.info("Processing PDF for ingestion", path=file_path)
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            pages_processed = len(documents)

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
                payloads.append(
                    {
                        "content": chunk.page_content,
                        "metadata": chunk.metadata,
                        "chunk_index": i,
                    }
                )

            self.qdrant.upsert_documents(ids, vectors, payloads)
            logger.info("Ingestion complete", path=file_path)

            duration = time.time() - start_time

            # Log to MLflow
            try:
                log_ingestion_run(
                    file_name=file_name,
                    pages_processed=pages_processed,
                    chunks_created=len(chunks),
                    duration_seconds=duration,
                    success=True,
                )
            except Exception as e:
                logger.warning(f"Failed to log ingestion to MLflow: {e}")

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to process PDF: {e}", path=file_path)

            # Log failure to MLflow
            try:
                log_ingestion_run(
                    file_name=file_name,
                    pages_processed=0,
                    chunks_created=0,
                    duration_seconds=duration,
                    success=False,
                )
            except Exception as mlflow_error:
                logger.warning(
                    f"Failed to log ingestion failure to MLflow: {mlflow_error}"
                )
            raise
