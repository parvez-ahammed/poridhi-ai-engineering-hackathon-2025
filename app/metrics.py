from prometheus_client import Counter, Gauge, Histogram, Summary
import time

# Define metrics
# 1. Request metrics
request_counter = Counter(
    'search_api_requests_total', 
    'Total number of requests received',
    ['method', 'endpoint', 'status']
)

request_latency = Histogram(
    'search_api_request_duration_seconds',
    'Request latency in seconds',
    ['method', 'endpoint'],
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, float('inf'))
)

# 2. Search specific metrics
search_query_counter = Counter(
    'search_api_search_queries_total',
    'Total number of search queries'
)

search_success_counter = Counter(
    'search_api_search_success_total',
    'Total number of successful search queries'
)

search_failure_counter = Counter(
    'search_api_search_failure_total',
    'Total number of failed search queries'
)

search_result_count = Histogram(
    'search_api_search_result_count',
    'Number of results returned by search queries',
    buckets=(0, 1, 5, 10, 25, 50, 100, float('inf'))
)

# 3. Cache metrics
cache_hit_counter = Counter(
    'search_api_cache_hits_total',
    'Total number of cache hits'
)

cache_miss_counter = Counter(
    'search_api_cache_misses_total',
    'Total number of cache misses'
)

# 4. Concurrency metrics
active_requests_gauge = Gauge(
    'search_api_active_requests',
    'Number of requests currently being processed'
)

# 5. Error metrics
error_counter = Counter(
    'search_api_errors_total',
    'Total number of errors',
    ['type', 'endpoint']
)

# 6. Timeout and cancellation metrics
timed_out_requests_counter = Counter(
    'search_api_timeouts_total',
    'Total number of timed out requests'
)

cancelled_requests_counter = Counter(
    'search_api_cancellations_total',
    'Total number of cancelled requests'
)

# 7. Resource usage
# Note: These are typically collected by the node_exporter in Prometheus
# But we can add custom resource metrics if needed
resource_usage_gauge = Gauge(
    'search_api_resource_usage',
    'Resource usage metrics',
    ['resource_type']  # cpu, memory, etc.
)

# Helper functions
def record_resource_usage(resource_type, value):
    """Record resource usage metrics"""
    resource_usage_gauge.labels(resource_type=resource_type).set(value)