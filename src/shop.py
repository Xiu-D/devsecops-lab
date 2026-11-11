"""A8 O-level: a Flask shop instrumented with OpenTelemetry.

Every HTTP request becomes a trace automatically (FlaskInstrumentor).
Inside a request we add our own child spans for the business steps.
"""
import random
import time

from flask import Flask, request
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Status, StatusCode

provider = TracerProvider(resource=Resource.create({
    "service.name": "shop-frontend",
    "deployment.environment": "lab",
}))
provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("a8.shop")

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)   # one line = a server span per request


@app.route("/")
def home():
    return "shop is up. try /checkout or /checkout?fail=1\n"


@app.route("/checkout")
def checkout():
    with tracer.start_as_current_span("reserve-stock") as span:
        span.set_attribute("items.count", 3)
        time.sleep(random.uniform(0.02, 0.05))  # noqa: S311 - pretend database call, not crypto

    with tracer.start_as_current_span("charge-card") as span:
        span.set_attribute("payment.amount", 299)
        time.sleep(random.uniform(0.10, 0.20))  # noqa: S311 - pretend payment provider, not crypto
        if request.args.get("fail"):
            err = RuntimeError("card declined")
            span.record_exception(err)
            span.set_status(Status(StatusCode.ERROR, "card declined"))
            return "payment failed\n", 502

    return "paid\n"


if __name__ == "__main__":
    app.run(port=8080)
