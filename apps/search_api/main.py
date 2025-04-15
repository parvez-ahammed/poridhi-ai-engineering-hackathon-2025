from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import random
import time
import asyncio
from typing import List, Dict, Optional
import uvicorn
from pydantic import BaseModel
import os
import logging
import json
from logging.handlers import RotatingFileHandler
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
import uuid

# Custom JSON formatter for logs (for better Loki integration)
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "trace_id": getattr(record, "trace_id", ""),
            "span_id": getattr(record, "span_id", ""),
            "request_id": getattr(record, "request_id", ""),
            "path": getattr(record, "path", ""),
            "method": getattr(record, "method", ""),
            "latency_ms": getattr(record, "latency_ms", None),
            "status_code": getattr(record, "status_code", None)
        }
        
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)

# Set up logging
log_directory = os.getenv("LOG_DIRECTORY", "logs")
# Create logs directory if it doesn't exist
os.makedirs(log_directory, exist_ok=True)

log_file = os.path.join(log_directory, "search_api.log")

# Configure logging
logger = logging.getLogger("search_api")
logger.setLevel(logging.INFO)

# Create file handler with rotation (10MB max size, keep 5 backup files)
file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
file_handler.setLevel(logging.INFO)

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create formatters and add them to the handlers
json_formatter = JsonFormatter()
file_handler.setFormatter(json_formatter)
console_handler.setFormatter(json_formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger.info("Starting Search API application")

# Set up OpenTelemetry
resource = Resource(attributes={
    SERVICE_NAME: "search-api"
})

# Set up tracing
logger.info("Configuring OpenTelemetry tracing")
tracer_provider = TracerProvider(resource=resource)
trace.set_tracer_provider(tracer_provider)
otlp_endpoint = os.getenv("OTLP_ENDPOINT", "localhost:4317")
logger.info(f"Using OTLP endpoint: {otlp_endpoint}")
otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
span_processor = BatchSpanProcessor(otlp_exporter)
tracer_provider.add_span_processor(span_processor)
tracer = trace.get_tracer(__name__)

# Set up metrics
logger.info("Configuring OpenTelemetry metrics")
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

# Helper function to get current trace context
def get_trace_context():
    span = trace.get_current_span()
    if span.is_recording():
        span_context = span.get_span_context()
        return {
            "trace_id": format(span_context.trace_id, "032x"),
            "span_id": format(span_context.span_id, "016x")
        }
    return {"trace_id": "", "span_id": ""}

# Sample data
logger.info("Initializing sample data")
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
    # Generate a unique request ID
    request_id = str(uuid.uuid4())
    
    # Get trace context
    trace_context = get_trace_context()
    
    # Add request_id as an extra to the LoggerAdapter
    logger_extra = {
        "request_id": request_id,
        "path": request.url.path,
        "method": request.method,
        "trace_id": trace_context.get("trace_id", ""),
        "span_id": trace_context.get("span_id", "")
    }
    
    # Log request start with trace information
    logger.info(
        f"Request started: {request.method} {request.url.path}",
        extra=logger_extra
    )
    
    concurrent_requests.add(1)
    start_time = time.time()
    
    try:
        response = await call_next(request)
        
        # Record latency
        latency = (time.time() - start_time) * 1000  # Convert to ms
        request_latency.record(latency)
        
        # Update logger extra with response info
        logger_extra.update({
            "status_code": response.status_code,
            "latency_ms": round(latency, 2)
        })
        
        logger.info(
            f"Request completed: {request.method} {request.url.path} - Status: {response.status_code} - Latency: {latency:.2f}ms",
            extra=logger_extra
        )
        
        # Add request ID header to response
        response.headers["X-Request-ID"] = request_id
        
        return response
    except Exception as e:
        error_counter.add(1)
        logger_extra.update({"error": str(e)})
        logger.error(
            f"Request failed: {request.method} {request.url.path} - Error: {str(e)}",
            exc_info=True,
            extra=logger_extra
        )
        raise
    finally:
        concurrent_requests.add(-1)
        # Count the request
        request_counter.add(1, {"path": request.url.path})

@app.get("/health")
async def health_check():
    trace_context = get_trace_context()
    logger.debug(
        "Health check endpoint called", 
        extra={"trace_id": trace_context.get("trace_id", ""), "span_id": trace_context.get("span_id", "")}
    )
    return {"status": "healthy"}

@app.get("/search", response_model=List[SearchResult])
async def search(q: str, timeout: float = 5.0, request: Request = None):
    trace_context = get_trace_context()
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    
    logger_extra = {
        "request_id": request_id,
        "trace_id": trace_context.get("trace_id", ""),
        "span_id": trace_context.get("span_id", ""),
        "query": q
    }
    
    logger.info(
        f"Search request received with query: '{q}', timeout: {timeout}s",
        extra=logger_extra
    )
    
    search_total_counter.add(1)
    
    with tracer.start_as_current_span("search_operation"):
        # Update trace context after starting span
        trace_context = get_trace_context()
        logger_extra.update({
            "trace_id": trace_context.get("trace_id", ""),
            "span_id": trace_context.get("span_id", "")
        })
        
        # Check cache
        if q in cache:
            logger.info(
                f"Cache hit for query: '{q}'",
                extra=logger_extra
            )
            cache_hit_counter.add(1)
            return cache[q]
        
        logger.info(
            f"Cache miss for query: '{q}'",
            extra=logger_extra
        )
        cache_miss_counter.add(1)
        
        try:
            # Simulate search with potential timeout
            logger.debug(
                f"Starting search task for query: '{q}'",
                extra=logger_extra
            )
            search_task = asyncio.create_task(perform_search(q, logger_extra))
            results = await asyncio.wait_for(search_task, timeout=timeout)
            
            # Cache the results
            cache[q] = results
            
            logger.info(
                f"Search successful for query: '{q}', found {len(results)} results",
                extra=logger_extra
            )
            search_success_counter.add(1)
            return results
        except asyncio.TimeoutError:
            logger.warning(
                f"Search timed out for query: '{q}' after {timeout}s",
                extra=logger_extra
            )
            timeout_counter.add(1)
            raise HTTPException(status_code=408, detail="Search timed out")
        except asyncio.CancelledError:
            logger.warning(
                f"Search cancelled for query: '{q}'",
                extra=logger_extra
            )
            cancellation_counter.add(1)
            raise HTTPException(status_code=499, detail="Client closed request")
        except Exception as e:
            logger_extra.update({"error": str(e)})
            logger.error(
                f"Error during search for query: '{q}' - {str(e)}",
                exc_info=True,
                extra=logger_extra
            )
            error_counter.add(1)
            raise HTTPException(status_code=500, detail="Internal server error")

async def perform_search(query: str, logger_extra: dict):
    # Simulate search latency
    processing_time = random.uniform(0.1, 1.5)
    logger.debug(
        f"Simulating processing time of {processing_time:.2f}s for query: '{query}'",
        extra=logger_extra
    )
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
    logger_extra.update({"results_count": len(results)})
    logger.debug(
        f"Search completed for query: '{query}', found {len(results)} results",
        extra=logger_extra
    )
    return results

@app.get("/metrics")
async def get_metrics():
    trace_context = get_trace_context()
    logger.debug(
        "Metrics endpoint called",
        extra={"trace_id": trace_context.get("trace_id", ""), "span_id": trace_context.get("span_id", "")}
    )
    # This endpoint will be used by Prometheus
    return {"message": "Metrics available at /metrics endpoint handled by Prometheus client"}

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup event triggered")
    # Start Prometheus HTTP server
    prometheus_port = 8000
    logger.info(f"Starting Prometheus HTTP server on port {prometheus_port}")
    start_http_server(prometheus_port)
    logger.info(f"Application started successfully, ready to accept requests")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown event triggered")
    logger.info("Application shutting down")

# Instrument FastAPI with OpenTelemetry
logger.info("Instrumenting FastAPI with OpenTelemetry")
FastAPIInstrumentor.instrument_app(app)

if __name__ == "__main__":
    host = "0.0.0.0"
    port = 8080
    logger.info(f"Starting Uvicorn server on {host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=True)