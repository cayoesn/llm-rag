import sys
import types
from unittest.mock import MagicMock

# Create mock rq with real Queue class that can be patched
if "rq" not in sys.modules:
    rq_mock = types.ModuleType("rq")
    class Queue:
        def __init__(self, *args, **kwargs):
            pass
        def enqueue(self, *args, **kwargs):
            job = MagicMock()
            job.id = "mock_job"
            return job
    class Worker:
        def __init__(self, *args, **kwargs):
            pass
        def work(self, *args, **kwargs):
            pass
    rq_mock.Queue = Queue
    rq_mock.Worker = Worker
    sys.modules["rq"] = rq_mock

# Create mock tenacity with real passthrough decorators
if "tenacity" not in sys.modules:
    tenacity_mock = types.ModuleType("tenacity")
    def retry(*args, **kwargs):
        def decorator(f):
            return f
        return decorator
    tenacity_mock.retry = retry
    tenacity_mock.stop_after_attempt = MagicMock()
    tenacity_mock.wait_exponential = MagicMock()
    sys.modules["tenacity"] = tenacity_mock

# Gracefully stub missing third-party packages for hermetic test execution
for module_name in [
    "ollama",
    "mlflow",
    "qdrant_client",
    "qdrant_client.http",
    "qdrant_client.http.models",
    "langchain",
    "langchain_community",
    "langchain_community.document_loaders",
    "langchain.text_splitter",
    "langchain_text_splitters",
    "langchain_community.embeddings",
    "langfuse",
    "opentelemetry.exporter",
    "opentelemetry.exporter.otlp",
    "opentelemetry.exporter.otlp.proto",
    "opentelemetry.exporter.otlp.proto.grpc",
    "opentelemetry.exporter.otlp.proto.grpc.trace_exporter",
    "opentelemetry.instrumentation",
    "opentelemetry.instrumentation.fastapi",
]:
    if module_name not in sys.modules:
        mock = MagicMock()
        sys.modules[module_name] = mock

if not hasattr(sys.modules["qdrant_client.http"], "models"):
    sys.modules["qdrant_client.http"].models = sys.modules["qdrant_client.http.models"]
