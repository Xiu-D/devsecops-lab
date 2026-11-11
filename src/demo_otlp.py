"""A8 Task 2: send the same parent/child spans to the OpenTelemetry Collector via OTLP."""
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

provider = TracerProvider(resource=Resource.create({"service.name": "a8-demo"}))

# Exporter changed: OTLP over gRPC to the collector instead of the console
exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
provider.add_span_processor(BatchSpanProcessor(exporter))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("a8.demo")

with tracer.start_as_current_span("checkout") as parent:
    parent.set_attribute("order.id", "A8-1001")
    with tracer.start_as_current_span("charge-card") as child:
        child.set_attribute("payment.amount", 299)
        print("paid")

p, c = parent.get_span_context(), child.get_span_context()
print(f"sent trace {p.trace_id:032x}")
print(f"  checkout    span_id {p.span_id:016x}")
print(f"  charge-card span_id {c.span_id:016x}  parent {child.parent.span_id:016x}")

# BatchSpanProcessor sends in batches: flush before the program exits
provider.shutdown()
print("flushed to collector at localhost:4317")
