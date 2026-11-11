import threading

import pytest
from werkzeug.serving import make_server

import frontend
import payment


@pytest.fixture
def payment_server():
    server = make_server("127.0.0.1", 8081, payment.app)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield
    server.shutdown()


def test_two_services_share_one_trace(payment_server, spans):
    resp = frontend.app.test_client().get("/checkout")
    assert resp.status_code == 200
    finished = spans()
    by_name = {s.name: s for s in finished}
    assert len({s.context.trace_id for s in finished}) == 1  # one trace across both services
    # payment's server span is a child of frontend's outgoing HTTP client span
    assert by_name["POST /charge"].parent.span_id == by_name["POST"].context.span_id
