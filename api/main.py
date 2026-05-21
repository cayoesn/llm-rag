from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import shutil
import os
import uuid
from redis import Redis
from rq import Queue
from config.settings import settings
from shared.logging import logger, setup_logging
from rag.service import RAGService
from worker.main import process_ingestion_task

# Initialize App
setup_logging()
app = FastAPI(title=settings.APP_NAME)

# Instrumentation
from shared.otel import setup_otel
setup_otel(app)

# Services
rag_service = RAGService()
redis_conn = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
q = Queue(settings.REDIS_QUEUE_NAME, connection=redis_conn)

# Models
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str
    context: List[dict]
    model: str

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        result = rag_service.answer_question(request.message)
        return result
    except Exception as e:
        logger.error("Chat error", error=str(e))
        raise HTTPException(status_code=500, detail="Error processing chat request")

@app.post("/ingest")
async def ingest_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    file_id = str(uuid.uuid4())
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{file_id}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Enqueue background task
    job = q.enqueue(process_ingestion_task, file_path)
    
    logger.info("Ingestion task enqueued", job_id=job.get_id(), file=file.filename)
    
    return {
        "message": "File uploaded and ingestion started",
        "job_id": job.get_id(),
        "file_id": file_id
    }
