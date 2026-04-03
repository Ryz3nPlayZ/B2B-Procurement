from fastapi.testclient import TestClient

from backend.app import app
from backend.core.settings import settings
from backend.db.database import init_db


def _auth_headers(api_key: str) -> dict:
    return {"Authorization": f"Bearer {api_key}"}


def _bootstrap_org_and_user(client: TestClient, name: str, email: str):
    org = client.post("/v1/platform/organizations", json={"name": name, "plan": "enterprise"})
    org_id = org.json()["id"]
    user = client.post(
        "/v1/platform/users",
        json={"org_id": org_id, "email": email, "role": "admin"},
    )
    return org_id, user.json()["api_key"]


def test_full_procurement_lifecycle_and_readiness(tmp_path):
    settings.sqlite_path = str(tmp_path / "procureos.db")
    init_db()

    with TestClient(app) as client:
        ready = client.get("/v1/ready")
        assert ready.status_code == 200
        assert ready.json()["ready"] is True

        _, api_key = _bootstrap_org_and_user(client, "Acme Corp", "admin@acme.com")
        headers = _auth_headers(api_key)

        supplier_a = client.post(
            "/v1/suppliers",
            headers=headers,
            json={"name": "Precision Works", "category": "electronics", "risk_rating": 2.1, "preferred": True},
        ).json()["id"]
        supplier_b = client.post(
            "/v1/suppliers",
            headers=headers,
            json={"name": "Volume Hub", "category": "electronics", "risk_rating": 4.0, "preferred": False},
        ).json()["id"]

        item_id = client.post(
            "/v1/catalog/items",
            headers=headers,
            json={"sku": "TS-100", "name": "Temperature Sensor", "unit": "unit", "target_price": 72.5},
        ).json()["id"]

        rfq_id = client.post(
            "/v1/rfqs",
            headers=headers,
            json={
                "item_id": item_id,
                "quantity": 500,
                "max_budget": 74,
                "currency": "USD",
                "evaluation_strategy": "balanced",
                "supplier_ids": [supplier_a, supplier_b],
            },
        ).json()["id"]

        publish = client.post(f"/v1/rfqs/{rfq_id}/publish", headers=headers)
        assert publish.status_code == 200

        bid_a = client.post(
            f"/v1/rfqs/{rfq_id}/bids",
            headers=headers,
            json={
                "supplier_id": supplier_a,
                "unit_price": 73.0,
                "lead_time_days": 5,
                "warranty_months": 24,
                "quality_score": 9.2,
                "notes": "Premium quality bid",
            },
        ).json()["id"]
        client.post(
            f"/v1/rfqs/{rfq_id}/bids",
            headers=headers,
            json={
                "supplier_id": supplier_b,
                "unit_price": 68.5,
                "lead_time_days": 9,
                "warranty_months": 12,
                "quality_score": 7.3,
                "notes": "Cost optimized bid",
            },
        )

        evaluation = client.post(f"/v1/rfqs/{rfq_id}/evaluate", headers=headers)
        assert evaluation.status_code == 200
        ranked = evaluation.json()
        assert ranked[0]["bid_id"]

        award = client.post(
            f"/v1/rfqs/{rfq_id}/award",
            headers=headers,
            json={"bid_id": bid_a, "rationale": "Best strategic fit with high quality and acceptable cost."},
        )
        assert award.status_code == 200

        details = client.get(f"/v1/rfqs/{rfq_id}", headers=headers)
        assert details.status_code == 200
        payload = details.json()
        assert payload["award"]["winning_bid_id"] == bid_a
        assert len(payload["bids"]) == 2


def test_auth_rejects_invalid_key_and_enforces_tenant_isolation(tmp_path):
    settings.sqlite_path = str(tmp_path / "procureos.db")
    init_db()

    with TestClient(app) as client:
        _, api_key_a = _bootstrap_org_and_user(client, "Org A", "admin@orga.com")
        _, api_key_b = _bootstrap_org_and_user(client, "Org B", "admin@orgb.com")

        bad = client.get("/v1/suppliers", headers=_auth_headers("pk_live_invalid"))
        assert bad.status_code == 401

        create_a = client.post(
            "/v1/suppliers",
            headers=_auth_headers(api_key_a),
            json={"name": "Tenant A Supplier", "category": "raw", "risk_rating": 3.0, "preferred": False},
        )
        assert create_a.status_code == 200

        list_b = client.get("/v1/suppliers", headers=_auth_headers(api_key_b))
        assert list_b.status_code == 200
        assert list_b.json() == []
