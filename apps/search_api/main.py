from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Prefetch,
    SparseVector,
    FusionQuery,
    Fusion,
)
from bm25 import BM25
import os
from dotenv import load_dotenv
import time
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import logging
import json
import uuid
import requests
from datetime import datetime

load_dotenv()

QDRANT_COLLECTION_NAME = os.environ.get("QDRANT_COLLECTION_NAME")
QDRANT_URL = os.environ.get("QDRANT_URL")
LOKI_URL = os.environ.get("LOKI_URL", "http://loki:3100")  # Default Loki URL

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = SentenceTransformer("./ml_model")
bm25 = BM25(
    stopwords_dir=os.path.abspath("./stopwards"), languages=["english", "bengali"]
)
qdrant_client = QdrantClient(url=QDRANT_URL, timeout=600)

# Define Prometheus metrics
REQUESTS_COUNTER = Counter(
    'api_requests_total', 
    'Total number of requests received', 
    ['endpoint', 'method', 'status_code']
)

SEARCH_COUNTER = Counter(
    'search_requests_total',
    'Total number of search requests by query type',
    ['query_type', 'status']
)

REQUEST_LATENCY = Histogram(
    'request_latency_seconds',
    'Request latency in seconds',
    ['endpoint', 'method'],
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0)
)

SEARCH_LATENCY = Histogram(
    'search_latency_seconds',
    'Search operation latency in seconds',
    ['query_type'],
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, 15.0, 30.0)
)

# Custom logger class for sending logs to Loki
class LokiHandler(logging.Handler):
    def __init__(self, url, app_name="search-api", labels=None):
        super().__init__()
        self.url = f"{url}/loki/api/v1/push"
        self.app_name = app_name
        self.default_labels = labels or {}
        
    def emit(self, record):
        try:
            # Generate request ID if not present
            if not hasattr(record, 'request_id'):
                record.request_id = str(uuid.uuid4())
                
            # Basic log entry information
            log_entry = {
                "message": self.format(record),
                "level": record.levelname,
                "timestamp": datetime.utcnow().isoformat(),
                "logger": record.name,
                "path": record.pathname,
                "function": record.funcName,
                "line": record.lineno,
            }
            
            # Add extra attributes from record
            for key, value in record.__dict__.items():
                if key not in ('args', 'msg', 'message', 'exc_info', 'exc_text', 'stack_info', 
                            'lineno', 'funcName', 'created', 'msecs', 'relativeCreated', 
                            'levelname', 'levelno', 'pathname', 'filename', 'module', 
                            'name', 'thread', 'threadName', 'processName', 'process'):
                    try:
                        log_entry[key] = str(value)
                    except:
                        log_entry[key] = "Unable to serialize"
            
            # Convert to string for Loki
            log_message = json.dumps(log_entry)
            
            # Prepare labels
            labels = {**self.default_labels, "app": self.app_name}
            
            # Add level as label for easy filtering
            labels["level"] = record.levelname
            
            # Add request_id if present
            if hasattr(record, 'request_id'):
                labels["request_id"] = record.request_id
                
            # Format labels for Loki
            labels_str = '{' + ','.join(f'{k}="{v}"' for k, v in labels.items()) + '}'
            
            # Current timestamp in nanoseconds
            timestamp_ns = int(time.time() * 1e9)
            
            # Prepare payload
            payload = {
                "streams": [
                    {
                        "stream": labels,
                        "values": [
                            [str(timestamp_ns), log_message]
                        ]
                    }
                ]
            }
            
            # Send to Loki
            requests.post(
                self.url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=2  # Short timeout to avoid blocking
            )
        except Exception as e:
            # Fallback to stderr since we can't log the logging error
            print(f"Error sending log to Loki: {e}", file=sys.stderr)

# Set up the logger
def setup_logger():
    # Create logger
    logger = logging.getLogger("search_api")
    logger.setLevel(logging.INFO)
    
    # Create console handler for local development
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    # Add console handler to logger
    logger.addHandler(console_handler)
    
    # Create Loki handler if Loki URL is provided
    if LOKI_URL:
        loki_handler = LokiHandler(
            url=LOKI_URL,
            labels={"environment": os.environ.get("ENVIRONMENT", "development")}
        )
        loki_handler.setLevel(logging.INFO)
        loki_handler.setFormatter(formatter)
        logger.addHandler(loki_handler)
    
    return logger

# Initialize logger
logger = setup_logger()

# Request ID middleware
@app.middleware("http")
async def request_middleware(request: Request, call_next):
    # Generate request ID
    request_id = str(uuid.uuid4())
    
    # Add request ID to request state
    request.state.request_id = request_id
    
    # Add basic request info to logger context
    logger_context = {
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "client_host": request.client.host if request.client else "unknown"
    }
    
    # Log request start
    logger.info(f"Request started: {request.method} {request.url.path}", 
                extra=logger_context)
    
    start_time = time.time()
    
    try:
        response = await call_next(request)
        status_code = response.status_code
        
        # Update logger context with status code
        logger_context["status_code"] = status_code
        
        # Log request end
        request_time = time.time() - start_time
        logger.info(f"Request completed: {status_code} in {request_time:.3f}s", 
                    extra=logger_context)
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
    except Exception as e:
        status_code = 500
        logger_context["status_code"] = status_code
        logger_context["error"] = str(e)
        
        # Log error
        logger.error(f"Request failed: {str(e)}", extra=logger_context)
        raise e
    finally:
        end_time = time.time()
        latency = end_time - start_time
        
        # Record request metrics
        REQUESTS_COUNTER.labels(
            endpoint=request.url.path,
            method=request.method,
            status_code=status_code
        ).inc()
        
        REQUEST_LATENCY.labels(
            endpoint=request.url.path,
            method=request.method
        ).observe(latency)
        
    return response

def search(query_text: str, query_type: str = "hybrid", limit: int = 5, request_id: str = None):
    start_time = time.time()
    success = True
    
    log_context = {
        "request_id": request_id,
        "query_text": query_text,
        "query_type": query_type,
        "limit": limit
    }
    
    logger.info(f"Search started: query='{query_text}' type={query_type}", extra=log_context)
    
    try:
        # Log encoding start
        logger.debug("Encoding query text", extra=log_context)
        dense_vector = model.encode([query_text])[0]
        sparse_vector = bm25.raw_embed([query_text])[0]
        
        # Log encoding completion
        encode_time = time.time() - start_time
        logger.debug(f"Encoding completed in {encode_time:.3f}s", extra=log_context)

        prefetch = [
            Prefetch(query=dense_vector, using="dense_vector", limit=10),
            Prefetch(query=SparseVector(**sparse_vector), using="sparse_vector", limit=10),
        ]

        # Log query start
        query_start_time = time.time()
        logger.debug(f"Qdrant query started with {query_type}", extra=log_context)

        if query_type == "hybrid":
            results = qdrant_client.query_points(
                collection_name=QDRANT_COLLECTION_NAME,
                prefetch=prefetch,
                query=FusionQuery(fusion=Fusion.RRF),
                with_payload=True,
                limit=limit,
            )

        elif query_type == "sparse":
            results = qdrant_client.query_points(
                collection_name=QDRANT_COLLECTION_NAME,
                query=SparseVector(**sparse_vector),
                using="sparse_vector",
                with_payload=True,
                limit=limit,
            )

        elif query_type == "dense":
            results = qdrant_client.query_points(
                collection_name=QDRANT_COLLECTION_NAME,
                query=dense_vector,
                using="dense_vector",
                with_payload=True,
                limit=limit,
            )

        # Log query completion
        query_time = time.time() - query_start_time
        logger.debug(f"Qdrant query completed in {query_time:.3f}s, found {len(results.points)} results", 
                   extra=log_context)

        response_data = [
            {"score": point.score, "payload": point.payload} for point in results.points
        ]
        
        # Log success with result count
        total_time = time.time() - start_time
        logger.info(f"Search completed: found {len(response_data)} results in {total_time:.3f}s", 
                  extra={**log_context, "result_count": len(response_data)})
        
    except Exception as e:
        success = False
        # Log error details
        logger.error(f"Search failed: {str(e)}", 
                    extra={**log_context, "error": str(e)})
        raise e
    finally:
        # Record search metrics
        end_time = time.time()
        latency = end_time - start_time
        
        status = "success" if success else "error"
        SEARCH_COUNTER.labels(query_type=query_type, status=status).inc()
        SEARCH_LATENCY.labels(query_type=query_type).observe(latency)
    
    return response_data


@app.get("/products")
def search_product(query: str = None, query_type="dense", limit: int = 5, request: Request = None):
    request_id = getattr(request.state, "request_id", None) if request else None
    
    log_context = {
        "request_id": request_id,
        "endpoint": "/products",
        "query": query,
        "query_type": query_type,
        "limit": limit
    }
    
    if query is None or len(query) == 0:
        logger.warning("Invalid request: empty query", extra=log_context)
        SEARCH_COUNTER.labels(query_type=query_type, status="error").inc()
        raise HTTPException(status_code=400, detail="Query is required")
    
    if query_type not in ["hybrid", "sparse", "dense"]:
        logger.warning(f"Invalid request: unsupported query type '{query_type}'", extra=log_context)
        SEARCH_COUNTER.labels(query_type=query_type, status="error").inc()
        raise HTTPException(status_code=400, detail="Query type invalid")

    limit = max(5, min(limit, 20))
    logger.info(f"Product search request: query='{query}' type={query_type} limit={limit}", 
              extra=log_context)

    try:
        query_res = search(query_text=query, query_type=query_type, limit=limit, request_id=request_id)
        logger.info(f"Product search success: returned {len(query_res)} results", 
                  extra={**log_context, "result_count": len(query_res)})
        return query_res
    except Exception as e:
        logger.error(f"Product search error: {str(e)}", extra={**log_context, "error": str(e)})
        SEARCH_COUNTER.labels(query_type=query_type, status="error").inc()
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Health check endpoint for monitoring
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Log viewer endpoint - useful for debugging
@app.get("/logs")
def view_recent_logs(limit: int = 100):
    """View recent logs (only works if Loki is accessible)"""
    try:
        # Query Loki for recent logs
        response = requests.get(
            f"{LOKI_URL}/loki/api/v1/query_range",
            params={
                "query": '{app="search-api"}',
                "limit": limit,
                "direction": "backward"
            },
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            logs = []
            
            # Extract logs from response
            if "data" in data and "result" in data["data"]:
                for stream in data["data"]["result"]:
                    for value in stream.get("values", []):
                        try:
                            timestamp, log_entry = value
                            log_data = json.loads(log_entry)
                            logs.append(log_data)
                        except:
                            logs.append({"message": log_entry})
            
            return {"logs": logs}
        else:
            return {"error": f"Failed to fetch logs: {response.status_code}", "detail": response.text}
    
    except Exception as e:
        logger.error(f"Error fetching logs: {str(e)}")
        return {"error": f"Failed to fetch logs: {str(e)}"}

# Add a test endpoint for log generation
@app.get("/test-log")
def test_log(level: str = "info", message: str = "Test log message"):
    """Generate test logs at different levels"""
    log_context = {"test": True, "source": "test-log-endpoint"}
    
    if level.lower() == "debug":
        logger.debug(message, extra=log_context)
    elif level.lower() == "info":
        logger.info(message, extra=log_context)
    elif level.lower() == "warning":
        logger.warning(message, extra=log_context)
    elif level.lower() == "error":
        logger.error(message, extra=log_context)
    else:
        logger.info(f"{level}: {message}", extra=log_context)
        
    return {"status": "ok", "level": level, "message": message}