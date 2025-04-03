# FastAPI Search API with Observability Stack

This project demonstrates a search API built with FastAPI and instrumented with OpenTelemetry for monitoring using Prometheus and Grafana.

## Project Structure

```
search-api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── search.py               # Search service
│   ├── cache.py                # Simple cache implementation
│   ├── telemetry.py            # OpenTelemetry setup
│   ├── middleware.py           # Custom middleware
│   └── metrics.py              # Custom metrics
├── data/
│   └── sample_data.json        # Sample data for searching
├── prometheus/
│   └── prometheus.yml          # Prometheus configuration
├── grafana/
│   ├── dashboards/
│   │   └── search_api.json     # Grafana dashboard configuration
│   └── datasources/
│       └── prometheus.yml      # Grafana datasource configuration
├── docker-compose.yml          # Docker Compose configuration
├── Dockerfile                  # Dockerfile for the API
└── requirements.txt            # Python dependencies
```

## Key Metrics Tracked

1. **Request Latency**: Time taken to process each request
2. **Request Rate**: Number of requests per second
3. **Error Rate**: Percentage of requests resulting in errors
4. **Search Query Success Rate**: Percentage of search queries returning results
5. **Resource Usage**: CPU, memory usage
6. **Cache Hit Rate**: Percentage of queries served from cache
7. **Concurrency**: Number of concurrent requests
8. **Timeout and Cancellation Rate**: Percentage of requests that time out or are cancelled

## Technology Stack

- **FastAPI**: Main API framework
- **OpenTelemetry**: Instrumentation
- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **Docker**: Containerization