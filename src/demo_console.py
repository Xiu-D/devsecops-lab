"""A8 Task 1: OpenTelemetry SDK with console output (parent + child span)."""
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

# 1. Tracer provider: names the service that produces the telemetry
provider = TracerProvider(resource=Resource.create({"service.name": "a8-demo"}))

# 2. Exporter: decides WHERE finished spans go (here: printed to the console)
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("a8.demo")

# 3. Parent span with a child span inside it
with tracer.start_as_current_span("checkout") as parent:
    parent.set_attribute("order.id", "A8-1001")
    with tracer.start_as_current_span("charge-card") as child:
        child.set_attribute("payment.amount", 299)
        print("paid")

# 4. Summary of the hierarchy (the JSON above has the same IDs)
p, c = parent.get_span_context(), child.get_span_context()
print("\n=== span hierarchy ===")
print(f"trace_id             : {p.trace_id:032x}")
print(f"checkout    span_id  : {p.span_id:016x}   (root, no parent)")
print(f"charge-card span_id  : {c.span_id:016x}")
print(f"charge-card parent_id: {child.parent.span_id:016x}")
print("same trace?            ", c.trace_id == p.trace_id)
print("child.parent == parent?", child.parent.span_id == p.span_id)
