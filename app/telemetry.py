from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.metrics import get_meter_provider, set_meter_provider
from prometheus_client import start_http_server
import logging

logger = logging.getLogger(__name__)

def configure_telemetry(app):
    """Configure OpenTelemetry with Prometheus exporter"""
    # Resource to identify this service
    resource = Resource.create({
        ResourceAttributes.SERVICE_NAME: "search-api",
        ResourceAttributes.SERVICE_VERSION: "1.0.0",
    })

    # Configure trace provider
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    # Configure metrics with Prometheus exporter
    prometheus_reader = PrometheusMetricReader()
    metric_readers = [prometheus_reader]
    meter_provider = MeterProvider(resource=resource, metric_readers=metric_readers)
    set_meter_provider(meter_provider)
    
    # Expose Prometheus endpoint at /metrics
    # Note: FastAPI will handle this at the /metrics endpoint defined in main.py
    
    # Configure FastAPI instrumentation
    FastAPIInstrumentor.instrument_app(
        app,
        tracer_provider=tracer_provider,
        meter_provider=meter_provider,
    )
    
    logger.info("Telemetry configured with Prometheus exporter")
    return tracer_provider, meter_provider

def get_tracer(name="search-api"):
    """Get a tracer for manual instrumentation"""
    return trace.get_tracer(name)

def get_meter(name="search-api"):
    """Get a meter for manual instrumentation"""
    return get_meter_provider().get_meter(name)