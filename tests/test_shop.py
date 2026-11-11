import pytest
from opentelemetry.trace import StatusCode

import shop


def test_checkout_creates_server_span_with_two_children(spans):
    resp = shop.app.test_client().get("/checkout")
    assert resp.status_code == 200
    by_name = {s.name: s for s in spans()}
    server = by_name["GET /checkout"]
    for child in ("reserve-stock", "charge-card"):
        assert by_name[child].parent.span_id == server.context.span_id
        assert by_name[child].context.trace_id == server.context.trace_id


def test_failed_payment_is_marked_as_error(spans):
    resp = shop.app.test_client().get("/checkout?fail=1")
    assert resp.status_code == 502
    by_name = {s.name: s for s in spans()}
    assert by_name["charge-card"].status.status_code == StatusCode.ERROR
    assert by_name["charge-card"].events[0].name == "exception"


def test_receipt_returns_stored_receipt():
    resp = shop.app.test_client().get("/receipt?id=A8-1001.txt")
    assert resp.status_code == 200
    assert b"A8-1001" in resp.data


@pytest.mark.parametrize("bad_id", ["../otel_setup.py", "/etc/passwd", "..%2Fshop.py", "", "."])
def test_receipt_rejects_paths_outside_receipt_dir(bad_id):
    resp = shop.app.test_client().get("/receipt?id=" + bad_id)
    assert resp.status_code == 400


def test_receipt_missing_file_is_404():
    resp = shop.app.test_client().get("/receipt?id=missing.txt")
    assert resp.status_code == 404
