from fastapi import FastAPI, Query, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import logging
from datetime import datetime
import uuid
import time
import os
import sys

# OpenTelemetry imports
from opentelemetry import metrics, trace
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.system_metrics import SystemMetricsInstrumentor
from prometheus_client import start_http_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configure OpenTelemetry resource
resource = Resource.create({
    ResourceAttributes.SERVICE_NAME: "ecommerce-search-api",
    ResourceAttributes.SERVICE_VERSION: "1.0.0",
    ResourceAttributes.DEPLOYMENT_ENVIRONMENT: os.getenv("ENVIRONMENT", "development"),
    ResourceAttributes.HOST_NAME: os.getenv("HOSTNAME", "localhost"),
})

# Set up tracing
tracer_provider = TracerProvider(resource=resource)

# Add console exporter for development/debugging
console_span_exporter = ConsoleSpanExporter()
tracer_provider.add_span_processor(BatchSpanProcessor(console_span_exporter))

# Set the tracer provider
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)

# Set up metrics
prometheus_reader = PrometheusMetricReader()
metric_readers = [prometheus_reader]
meter_provider = MeterProvider(resource=resource, metric_readers=metric_readers)
metrics.set_meter_provider(meter_provider)
meter = metrics.get_meter(__name__)

# Create custom metrics
search_counter = meter.create_counter(
    name="search_requests_total",
    description="Total number of search requests",
    unit="1",
)


search_latency = meter.create_histogram(
    name="search_request_duration_seconds",
    description="Search request duration in seconds",
    unit="s",
)

search_results_counter = meter.create_counter(
    name="search_results_total",
    description="Total number of search results returned",
    unit="1",
)

# Start Prometheus HTTP server on a separate port
start_http_server(port=9464)

# Instrument libraries
LoggingInstrumentor().instrument(set_logging_format=True)
RequestsInstrumentor().instrument()
SystemMetricsInstrumentor().instrument()

# Create FastAPI app
app = FastAPI(
    title="E-commerce Search API",
    description="Search API for e-commerce products with OpenTelemetry metrics",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Instrument FastAPI with OpenTelemetry
# Remove the trace_query_params parameter
FastAPIInstrumentor.instrument_app(
    app, 
    meter_provider=meter_provider, 
    tracer_provider=tracer_provider,
    excluded_urls="/metrics,/health"
)


# Add middleware for request timing
@app.middleware("http")
async def add_timing_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Add processing time header
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

# Models
class Product(BaseModel):
    id: str
    name: str
    description: str
    price: float
    category: str
    image_url: str
    in_stock: bool

class SearchResponse(BaseModel):
    products: List[Product]
    total: int
    page: int
    page_size: int
    total_pages: int

# Dummy product data
products = [
    {
        "id": str(uuid.uuid4()),
        "name": "Smartphone X",
        "description": "Latest smartphone with advanced features and high-resolution camera",
        "price": 999.99,
        "category": "electronics",
        "image_url": "https://example.com/smartphone-x.jpg",
        "in_stock": True
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Laptop Pro",
        "description": "High-performance laptop for professionals and gamers",
        "price": 1499.99,
        "category": "electronics",
        "image_url": "https://example.com/laptop-pro.jpg",
        "in_stock": True
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Wireless Headphones",
        "description": "Noise-cancelling wireless headphones with long battery life",
        "price": 249.99,
        "category": "electronics",
        "image_url": "https://example.com/wireless-headphones.jpg",
        "in_stock": True
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Coffee Maker",
        "description": "Automatic coffee maker with timer and multiple brewing options",
        "price": 89.99,
        "category": "home",
        "image_url": "https://example.com/coffee-maker.jpg",
        "in_stock": True
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Running Shoes",
        "description": "Lightweight running shoes for athletes and casual runners",
        "price": 129.99,
        "category": "fashion",
        "image_url": "https://example.com/running-shoes.jpg",
        "in_stock": False
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Smart Watch",
        "description": "Fitness tracker and smartwatch with heart rate monitoring",
        "price": 199.99,
        "category": "electronics",
        "image_url": "https://example.com/smart-watch.jpg",
        "in_stock": True
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Blender",
        "description": "High-speed blender for smoothies and food processing",
        "price": 79.99,
        "category": "home",
        "image_url": "https://example.com/blender.jpg",
        "in_stock": True
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Yoga Mat",
        "description": "Non-slip yoga mat for exercise and meditation",
        "price": 29.99,
        "category": "sports",
        "image_url": "https://example.com/yoga-mat.jpg",
        "in_stock": True
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Desk Lamp",
        "description": "Adjustable LED desk lamp with multiple brightness levels",
        "price": 39.99,
        "category": "home",
        "image_url": "https://example.com/desk-lamp.jpg",
        "in_stock": False
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Bluetooth Speaker",
        "description": "Portable bluetooth speaker with enhanced bass and water resistance",
        "price": 69.99,
        "category": "electronics",
        "image_url": "https://example.com/bluetooth-speaker.jpg",
        "in_stock": True
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Winter Jacket",
        "description": "Warm winter jacket with water-resistant outer layer",
        "price": 149.99,
        "category": "fashion",
        "image_url": "https://example.com/winter-jacket.jpg",
        "in_stock": True
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Gaming Console",
        "description": "Next-generation gaming console with 4K graphics",
        "price": 499.99,
        "category": "electronics",
        "image_url": "https://example.com/gaming-console.jpg",
        "in_stock": False
    },
]

# API endpoints
@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    """Health check endpoint that returns API status"""
    return {
        "status": "online",
        "api": "E-commerce Search API",
        "version": "1.0.0",
        "metrics": "Available at :9464/metrics",
    }

@app.get("/health", status_code=status.HTTP_200_OK)
async def health():
    """Health check endpoint for monitoring systems"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/search", response_model=SearchResponse)
async def search_products(
    q: str = Query(..., min_length=1, description="Search query for product name or description"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=50, description="Number of products per page")
):
    """
    Search for products based on name or description
    
    - **q**: Search term to match against product name and description
    - **page**: Page number for pagination (starts at 1)
    - **page_size**: Number of products per page (max 50)
    """
    # Create a span for this search operation
    with tracer.start_as_current_span("search_products") as span:
        span.set_attribute("search.query", q)
        span.set_attribute("search.page", page)
        span.set_attribute("search.page_size", page_size)
        
        # Record search request in metrics
        search_counter.add(1, {"query_length": len(q)})
        
        start_time = time.time()
        
        try:
            # Log the search request
            logger.info(f"Search request: query='{q}', page={page}, page_size={page_size}")
            
            # Search in product name and description (case-insensitive)
            query = q.lower()
            
            # Create a span for the filtering operation
            with tracer.start_as_current_span("filter_products") as filter_span:
                matched_products = [
                    p for p in products 
                    if query in p["name"].lower() or query in p["description"].lower()
                ]
                filter_span.set_attribute("matched_products", len(matched_products))
            
            # Calculate pagination
            total_products = len(matched_products)
            total_pages = max(1, (total_products + page_size - 1) // page_size)
            
            # Record the number of results found
            search_results_counter.add(total_products, {
                "query": q[:50],  # Truncate long queries
                "results_found": "true" if total_products > 0 else "false"
            })
            
            span.set_attribute("search.results.total", total_products)
            span.set_attribute("search.results.pages", total_pages)
            
            # Validate page number
            if page > total_pages:
                span.set_attribute("search.error", "page_not_found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Page {page} not found. Total pages: {total_pages}"
                )
            
            # Get products for the requested page
            with tracer.start_as_current_span("paginate_results"):
                start_idx = (page - 1) * page_size
                end_idx = min(start_idx + page_size, total_products)
                paged_products = matched_products[start_idx:end_idx]
            
            # Convert to Pydantic models
            product_models = [Product(**p) for p in paged_products]
            
            # Record search latency
            duration = time.time() - start_time
            search_latency.record(duration, {
                "result_size": str(min(10, len(paged_products))),
                "page": str(page)
            })
            
            span.set_attribute("search.duration", duration)
            
            return SearchResponse(
                products=product_models,
                total=total_products,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )
            
        except HTTPException as e:
            # Record exception in span
            span.record_exception(e)
            span.set_attribute("error", True)
            span.set_attribute("error.type", "http_exception")
            span.set_attribute("error.code", e.status_code)
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            # Record exception in span
            span.record_exception(e)
            span.set_attribute("error", True)
            span.set_attribute("error.type", type(e).__name__)
            
            # Log unexpected errors and return a generic error message
            logger.error(f"Error processing search: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while processing your search"
            )
        finally:
            # Record final search latency if not already done
            if 'duration' not in locals():
                duration = time.time() - start_time
                search_latency.record(duration, {"error": "true"})

# Metrics endpoint (for documentation purposes - actual metrics are on port 9464)
@app.get("/metrics-info")
async def metrics_info():
    """Information about available metrics"""
    return {
        "message": "Prometheus metrics are available at :9464/metrics",
        "available_metrics": [
            "search_requests_total - Counter for total search requests",
            "search_request_duration_seconds - Histogram of search request durations",
            "search_results_total - Counter for total search results returned",
            "http_server_* - Auto-instrumented HTTP server metrics",
            "system_* - System metrics (CPU, memory, etc.)",
            "process_* - Process metrics",
        ]
    }

# Run the application
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting E-commerce Search API with OpenTelemetry and Prometheus metrics")
    logger.info("Prometheus metrics available at http://localhost:9464/metrics")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)