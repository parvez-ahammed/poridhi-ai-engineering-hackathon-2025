from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import random
import time
import asyncio
from typing import List, Dict, Optional
import uvicorn
from pydantic import BaseModel
import os
from opentelemetry import metrics, trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from prometheus_client import start_http_server

# Set up OpenTelemetry
resource = Resource(attributes={
    SERVICE_NAME: "search-api"
})

# Set up tracing
tracer_provider = TracerProvider(resource=resource)
trace.set_tracer_provider(tracer_provider)
otlp_exporter = OTLPSpanExporter(endpoint=os.getenv("OTLP_ENDPOINT", "localhost:4317"))
span_processor = BatchSpanProcessor(otlp_exporter)
tracer_provider.add_span_processor(span_processor)
tracer = trace.get_tracer(__name__)

# Set up metrics
prometheus_reader = PrometheusMetricReader()
meter_provider = MeterProvider(resource=resource, metric_readers=[prometheus_reader])
metrics.set_meter_provider(meter_provider)
meter = metrics.get_meter(__name__)

# Create metrics
request_counter = meter.create_counter(
    name="request_counter",
    description="Counts the number of requests",
)

request_latency = meter.create_histogram(
    name="request_latency",
    description="Latency of requests",
    unit="ms",
)

error_counter = meter.create_counter(
    name="error_counter",
    description="Count of errors",
)

search_success_counter = meter.create_counter(
    name="search_success_counter",
    description="Count of successful searches",
)

search_total_counter = meter.create_counter(
    name="search_total_counter",
    description="Total count of searches",
)

cache_hit_counter = meter.create_counter(
    name="cache_hit_counter",
    description="Count of cache hits",
)

cache_miss_counter = meter.create_counter(
    name="cache_miss_counter",
    description="Count of cache misses",
)

concurrent_requests = meter.create_up_down_counter(
    name="concurrent_requests",
    description="Number of concurrent requests",
)

timeout_counter = meter.create_counter(
    name="timeout_counter",
    description="Count of timeouts",
)

cancellation_counter = meter.create_counter(
    name="cancellation_counter",
    description="Count of cancellations",
)

# Sample data
sample_data = [
    {"id": 1, "title": "FastAPI in Action", "content": "Learn about FastAPI framework"},
    {"id": 2, "title": "Python Programming", "content": "Best practices for Python"},
    {"id": 3, "title": "OpenTelemetry Guide", "content": "Monitoring with OpenTelemetry"},
    {"id": 4, "title": "Prometheus Metrics", "content": "Using Prometheus for monitoring"},
    {"id": 5, "title": "Grafana Dashboards", "content": "Creating effective dashboards"},
]

# Simple in-memory cache
cache = {}

app = FastAPI(title="Search API Demo")

class SearchQuery(BaseModel):
    query: str
    timeout: Optional[float] = 1.0

class SearchResult(BaseModel):
    id: int
    title: str
    content: str
    relevance: float

@app.middleware("http")
async def add_metrics_middleware(request: Request, call_next):
    concurrent_requests.add(1)
    start_time = time.time()
    
    try:
        response = await call_next(request)
        
        # Record latency
        latency = (time.time() - start_time) * 1000  # Convert to ms
        request_latency.record(latency)
        
        return response
    except Exception as e:
        error_counter.add(1)
        raise
    finally:
        concurrent_requests.add(-1)
        # Count the request
        request_counter.add(1, {"path": request.url.path})

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/search", response_model=List[SearchResult])
async def search(q: str, timeout: float = 5.0):
    search_total_counter.add(1)
    
    with tracer.start_as_current_span("search_operation"):
        # Check cache
        if q in cache:
            cache_hit_counter.add(1)
            return cache[q]
        
        cache_miss_counter.add(1)
        
        try:
            # Simulate search with potential timeout
            search_task = asyncio.create_task(perform_search(q))
            results = await asyncio.wait_for(search_task, timeout=timeout)
            
            # Cache the results
            cache[q] = results
            
            search_success_counter.add(1)
            return results
        except asyncio.TimeoutError:
            timeout_counter.add(1)
            raise HTTPException(status_code=408, detail="Search timed out")
        except asyncio.CancelledError:
            cancellation_counter.add(1)
            raise HTTPException(status_code=499, detail="Client closed request")

async def perform_search(query: str):
    # Simulate search latency
    processing_time = random.uniform(0.1, 1.5)
    await asyncio.sleep(processing_time)
    
    # Simple search implementation
    results = []
    for item in sample_data:
        # Check if query appears in title or content
        if query.lower() in item["title"].lower() or query.lower() in item["content"].lower():
            # Calculate a fake relevance score
            relevance = random.uniform(0.5, 1.0)
            results.append(SearchResult(
                id=item["id"],
                title=item["title"],
                content=item["content"],
                relevance=relevance
            ))
    
    # Sort by relevance
    results.sort(key=lambda x: x.relevance, reverse=True)
    return results

@app.get("/metrics")
async def get_metrics():
    # This endpoint will be used by Prometheus
    return {"message": "Metrics available at /metrics endpoint handled by Prometheus client"}

@app.on_event("startup")
async def startup_event():
    # Start Prometheus HTTP server
    start_http_server(8000)

# Instrument FastAPI with OpenTelemetry
FastAPIInstrumentor.instrument_app(app)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)