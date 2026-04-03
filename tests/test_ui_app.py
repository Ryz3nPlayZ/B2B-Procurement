from fastapi.testclient import TestClient

from ui.app import app


def test_ui_homepage_and_health():
    client = TestClient(app)

    home = client.get("/")
    assert home.status_code == 200
    assert "Procurement Copilot" in home.text

    health = client.get("/api/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"


def test_ui_session_flow_and_metrics_and_ws_events():
    client = TestClient(app)

    metrics_before = client.get("/api/metrics").json()
    assert metrics_before["sessions"] >= 0

    created = client.post(
        "/api/sessions",
        json={"product_id": "TS-100", "quantity": 120, "max_budget": 75, "priority": "balanced"},
    )
    assert created.status_code == 200
    payload = created.json()
    session_id = payload["session_id"]

    session = client.get(f"/api/sessions/{session_id}")
    assert session.status_code == 200
    assert session.json()["session_id"] == session_id

    metrics_after = client.get("/api/metrics").json()
    assert metrics_after["sessions"] >= 1

    with client.websocket_connect("/ws/events") as ws:
        event = ws.receive_json()
        assert event["session_id"] == session_id
        assert "event" in event
