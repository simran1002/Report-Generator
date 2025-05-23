import time
from typing import Callable

from fastapi import Request, Response
from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP Requests",
    ["method", "endpoint", "status_code"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP Request Latency",
    ["method", "endpoint"]
)

REPORT_GENERATION_COUNT = Counter(
    "report_generation_total",
    "Total Report Generations",
    ["status"]
)

REPORT_GENERATION_LATENCY = Histogram(
    "report_generation_duration_seconds",
    "Report Generation Latency"
)


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware for collecting metrics about HTTP requests and responses.
    """
    
    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        start_time = time.time()
        
        endpoint = request.url.path
        
        try:
            response = await call_next(request)
            
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=endpoint,
                status_code=response.status_code
            ).inc()
            
            REQUEST_LATENCY.labels(
                method=request.method,
                endpoint=endpoint
            ).observe(time.time() - start_time)
            
            return response
            
        except Exception as e:
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=endpoint,
                status_code=500
            ).inc()
            
            REQUEST_LATENCY.labels(
                method=request.method,
                endpoint=endpoint
            ).observe(time.time() - start_time)
            
            raise
