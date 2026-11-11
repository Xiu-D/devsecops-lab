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
