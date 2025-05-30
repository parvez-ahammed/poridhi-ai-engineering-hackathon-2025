from fastapi import FastAPI, HTTPException, Request
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
from logging_loki import LokiHandler
from fastapi.middleware.cors import CORSMiddleware
import logging


load_dotenv()

QDRANT_COLLECTION_NAME = os.environ.get("QDRANT_COLLECTION_NAME")
QDRANT_URL = os.environ.get("QDRANT_URL")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

loki_handler = LokiHandler(
    url="http://localhost:3100/loki/api/v1/push",  # Adjust if Loki is remote
    tags={"app": "fastapi-search-service"},
    version="1",
)

logger = logging.getLogger("loki_logger")
logger.setLevel(logging.INFO)
logger.addHandler(loki_handler)

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

# Add middleware to track request metrics
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception as e:
        status_code = 500
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

def search(query_text: str, query_type: str = "hybrid", limit: int = 5):
    start_time = time.time()
    success = True
    
    try:
        dense_vector = model.encode([query_text])[0]
        sparse_vector = bm25.raw_embed([query_text])[0]

        prefetch = [
            Prefetch(query=dense_vector, using="dense_vector", limit=10),
            Prefetch(query=SparseVector(**sparse_vector), using="sparse_vector", limit=10),
        ]

        if query_type == "hybrid":
            results = qdrant_client.query_points(
                collection_name=QDRANT_COLLECTION_NAME,
                prefetch=prefetch,
                query=FusionQuery(fusion=Fusion.RRF),
                with_payload=True,
                limit=30,
            )

        elif query_type == "sparse":
            results = qdrant_client.query_points(
                collection_name=QDRANT_COLLECTION_NAME,
                query=SparseVector(**sparse_vector),
                using="sparse_vector",
                with_payload=True,
                limit=30,
            )

        elif query_type == "dense":
            results = qdrant_client.query_points(
                collection_name=QDRANT_COLLECTION_NAME,
                query=dense_vector,
                using="dense_vector",
                with_payload=True,
                limit=30,
            )

        unique_titles = set()
        unique_products = []

        for points in results.points:
            title = points.payload.get("title")
            if title and title not in unique_titles and points.score >= 0.4:
                unique_titles.add(title)
                unique_products.append(points.payload)

                if len(unique_products) >= limit:
                    break
        return unique_products
        # response_data = [
        #     {"score": point.score, "payload": point.payload} for point in results.points
        # ]
        
    except Exception as e:
        success = False
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
def search_product(query: str = None, query_type="dense", limit: int = 5):
    if query is None or len(query) == 0:
        SEARCH_COUNTER.labels(query_type=query_type, status="error").inc()
        raise HTTPException(status_code=400, detail="Query is required")
    
    if query_type not in ["hybrid", "sparse", "dense"]:
        SEARCH_COUNTER.labels(query_type=query_type, status="error").inc()
        raise HTTPException(status_code=400, detail="Query type invalid")

    limit = max(5, min(limit, 20))

    try:
        query_res = search(query_text=query, query_type=query_type, limit=limit)
        logger.info("Search query", extra={
            "search_query": query,
            "results": query_res,
        })
        return query_res
    except Exception as e:
        SEARCH_COUNTER.labels(query_type=query_type, status="error").inc()
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Health check endpoint for monitoring
@app.get("/health")
def health_check():
    return {"status": "healthy"}