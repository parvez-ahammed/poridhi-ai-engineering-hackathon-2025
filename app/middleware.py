from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import logging
from .metrics import request_counter, request_latency, error_counter

logger = logging.getLogger(__name__)

class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for recording request metrics"""
    
    async def dispatch(self, request: Request, call_next):
        # Start timer for request latency
        start_time = time.time()
        
        # Default status code for unhandled exceptions
        status_code = 500
        
        try:
            # Process the request
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception as e:
            # Log and count errors
            method = request.method
            endpoint = request.url.path
            logger.exception(f"Error in {method} {endpoint}: {str(e)}")
            error_counter.labels(type=type(e).__name__, endpoint=endpoint).inc()
            raise
        finally:
            # Record metrics regardless of success/failure
            method = request.method
            endpoint = request.url.path
            
            # Record request latency
            duration = time.time() - start_time
            request_latency.labels(method=method, endpoint=endpoint).observe(duration)
            
            # Record request count
            request_counter.labels(
                method=method,
                endpoint=endpoint,
                status=str(status_code)
            ).inc()

class RequestCancellationMiddleware(BaseHTTPMiddleware):
    """Middleware for handling request cancellations"""
    
    async def dispatch(self, request: Request, call_next):
        # Add a method to check if the request was disconnected
        request.is_disconnected = lambda: request.scope.get("state", {}).get("disconnected", False)
        
        # Process the request
        response = await call_next(request)
        return response