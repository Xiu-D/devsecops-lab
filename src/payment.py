"""A8 O-3: payment service (port 8081). Called by frontend.py over HTTP."""
import random
import time

from flask import Flask, jsonify, request
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.trace import Status, StatusCode

from otel_setup import init_tracing

tracer = init_tracing("shop-payment")
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)   # reads the incoming traceparent header


@app.route("/charge", methods=["POST"])
def charge():
    # The W3C header that carries the trace context between the two services
    print("received traceparent:", request.headers.get("traceparent"), flush=True)
    order = request.get_json()

    with tracer.start_as_current_span("fraud-check") as span:
        span.set_attribute("payment.amount", order["amount"])
        time.sleep(random.uniform(0.02, 0.04))  # noqa: S311 - simulated latency, not crypto

    with tracer.start_as_current_span("bank-authorize") as span:
        time.sleep(random.uniform(0.08, 0.15))  # noqa: S311 - pretend external bank API, not crypto
        if order.get("fail"):
            span.record_exception(RuntimeError("card declined"))
            span.set_status(Status(StatusCode.ERROR, "card declined"))
            return jsonify(status="declined"), 402

    return jsonify(status="approved")


if __name__ == "__main__":
    app.run(port=8081)
