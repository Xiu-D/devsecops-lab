"""Send spans to memory instead of a collector, so tests run without Docker."""
import opentelemetry.exporter.otlp.proto.grpc.trace_exporter as otlp
import pytest
from opentelemetry import trace
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

MEMORY = InMemorySpanExporter()
otlp.OTLPSpanExporter = lambda **kwargs: MEMORY  # patched before the apps are imported


@pytest.fixture
def spans():
    MEMORY.clear()

    def finished():
        trace.get_tracer_provider().force_flush()
        return MEMORY.get_finished_spans()

    return finished
