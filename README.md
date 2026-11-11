# devsecops-lab

DevOps Assignment 9 — DevSecOps fundamentals, applied to the OpenTelemetry demo services from Assignment 8.

| Path | What |
|---|---|
| `src/shop.py` | Flask shop, auto-instrumented with OpenTelemetry |
| `src/frontend.py`, `src/payment.py` | two services, trace context propagated over HTTP |
| `src/demo_console.py`, `src/demo_otlp.py` | minimal SDK demos (console / OTLP) |
| `tests/` | pytest suite; spans go to an in-memory exporter, no Docker needed |
| `docker-compose.yml` | OpenTelemetry Collector + Jaeger |

```bash
pip install -r requirements-dev.txt
flake8 src tests      # lint + security rules (flake8-bandit)
pytest                # tests
```
