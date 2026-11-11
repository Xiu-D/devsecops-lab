"""A8 O-3: shop frontend (port 8080). Calls payment.py, passing the trace context."""
import random
import time

import requests
from flask import Flask, request
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

from otel_setup import init_tracing

tracer = init_tracing("shop-frontend")
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)   # server span for each incoming request
RequestsInstrumentor().instrument()       # client span + adds traceparent header to outgoing calls


@app.route("/checkout")
def checkout():
    with tracer.start_as_current_span("reserve-stock") as span:
        span.set_attribute("items.count", 3)
        time.sleep(random.uniform(0.02, 0.05))

    resp = requests.post("http://127.0.0.1:8081/charge",
                         json={"amount": 299, "fail": bool(request.args.get("fail"))},
                         timeout=5)
    if resp.status_code != 200:
        return "payment failed\n", 502
    return "paid\n"


if __name__ == "__main__":
    app.run(port=8080)
