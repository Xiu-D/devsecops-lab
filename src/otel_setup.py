"""Shared OpenTelemetry setup for the two services (A8 O-level)."""
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def init_tracing(service_name):
    provider = TracerProvider(resource=Resource.create({
        "service.name": service_name,
        "deployment.environment": "lab",
    }))
    provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)))
    trace.set_tracer_provider(provider)
    return trace.get_tracer(service_name)
