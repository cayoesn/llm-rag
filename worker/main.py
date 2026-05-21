from redis import Redis
from rq import Worker, Queue, connections
from config.settings import settings
from shared.logging import logger, setup_logging
from ingestion.pipeline import IngestionPipeline

# Setup logging for the worker process
setup_logging()

listen = [settings.REDIS_QUEUE_NAME]
redis_conn = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)

def process_ingestion_task(file_path: str):
    try:
        pipeline = IngestionPipeline()
        pipeline.process_pdf(file_path)
        # Cleanup file after processing if needed
        # os.remove(file_path)
    except Exception as e:
        logger.error("Failed to process ingestion task", error=str(e), file=file_path)
        raise

if __name__ == '__main__':
    logger.info("Starting LLM-RAG Worker", queues=listen)
    q = Queue(settings.REDIS_QUEUE_NAME, connection=redis_conn)
    worker = Worker([q], connection=redis_conn)
    worker.work()
