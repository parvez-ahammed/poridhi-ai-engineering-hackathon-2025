from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import time
import random
import asyncio
from typing import List, Dict, Optional, Any
import uvicorn
import logging

from .telemetry import configure_telemetry
from .middleware import MetricsMiddleware, RequestCancellationMiddleware
from .search import SearchService
from .cache import Cache
from .metrics import (
    search_query_counter, 
    search_success_counter, 
    search_failure_counter,
    cache_hit_counter,
    cache_miss_counter,
    active_requests_gauge,
    cancelled_requests_counter,
    timed_out_requests_counter
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize app
app = FastAPI(title="Search API Demo", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure custom middleware
app.add_middleware(MetricsMiddleware)
app.add_middleware(RequestCancellationMiddleware)

# Configure OpenTelemetry
configure_telemetry(app)

# Initialize services
search_service = SearchService()
cache = Cache()

@app.on_event("startup")
async def startup_event():
    logger.info("Loading sample data...")
    try:
        with open("data/sample_data.json", "r") as f:
            data = json.load(f)
            search_service.load_data(data)
        logger.info("Sample data loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load sample data: {e}")
        # Still start the app, but with empty data
        search_service.load_data([])

@app.get("/")
async def root():
    return {"message": "Search API is up and running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/metrics")
async def metrics():
    # This endpoint will be handled by the OpenTelemetry Prometheus exporter
    pass

@app.get("/search")
async def search(
    request: Request,
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, description="Maximum number of results"),
    timeout: float = Query(5.0, description="Search timeout in seconds")
):
    search_query_counter.inc()
    active_requests_gauge.inc()
    
    # Try to get from cache first
    cache_key = f"search:{q}:{limit}"
    cached_result = cache.get(cache_key)
    if cached_result:
        cache_hit_counter.inc()
        active_requests_gauge.dec()
        return cached_result
    
    cache_miss_counter.inc()
    
    # Simulate slow search sometimes
    if random.random() < 0.1:  # 10% chance
        delay = random.uniform(2.0, 6.0)
        if delay > timeout:
            timed_out_requests_counter.inc()
            active_requests_gauge.dec()
            raise HTTPException(status_code=408, detail="Search timed out")
        await asyncio.sleep(delay)
    
    # Check for request cancellation
    if await request.is_disconnected():
        cancelled_requests_counter.inc()
        active_requests_gauge.dec()
        # This won't actually be sent to the client since they're disconnected
        return JSONResponse(status_code=499, content={"detail": "Client disconnected"})
    
    try:
        # Perform search with timeout
        results = await asyncio.wait_for(
            search_service.search(q, limit), 
            timeout=timeout
        )
        
        # Cache the results
        response_data = {"query": q, "results": results, "count": len(results)}
        cache.set(cache_key, response_data, ttl=300)  # 5 minutes TTL
        
        search_success_counter.inc()
        active_requests_gauge.dec()
        return response_data
    
    except asyncio.TimeoutError:
        timed_out_requests_counter.inc()
        active_requests_gauge.dec()
        raise HTTPException(status_code=408, detail="Search timed out")
    
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        search_failure_counter.inc()
        active_requests_gauge.dec()
        raise HTTPException(status_code=500, detail="Search failed")

@app.get("/simulate-error")
async def simulate_error():
    """Endpoint to simulate errors for testing metrics"""
    if random.random() < 0.8:  # 80% chance of error
        raise HTTPException(status_code=500, detail="Simulated error")
    return {"message": "No error occurred"}

@app.get("/simulate-timeout")
async def simulate_timeout():
    """Endpoint to simulate timeouts for testing metrics"""
    await asyncio.sleep(10)  # Long delay
    return {"message": "This should timeout before getting here"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)