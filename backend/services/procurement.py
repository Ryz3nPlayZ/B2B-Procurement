from __future__ import annotations

from datetime import datetime

from fastapi import HTTPException

from backend.schemas.models import AwardRequest, BidCreate, CatalogItemCreate, OrganizationCreate, RFQCreate, SupplierCreate, UserCreate
from backend.services.auth import generate_api_key_record
from backend.services.repositories import execute, executemany, fetch_all, fetch_one, make_id, utc_now


DEFAULT_LIMIT = 50
MAX_LIMIT = 200


def _normalize_limit(limit: int) -> int:
    return max(1, min(limit, MAX_LIMIT))


def create_organization(payload: OrganizationCreate) -> dict:
    org_id = make_id("org")
    execute(
        "INSERT INTO organizations (id, name, plan, created_at) VALUES (?, ?, ?, ?)",
        (org_id, payload.name, payload.plan, utc_now()),
    )
    return {"id": org_id}


def create_user(payload: UserCreate) -> dict:
    api_key_record = generate_api_key_record()
    user_id = make_id("usr")
    execute(
        "INSERT INTO users (id, org_id, email, role, api_key_prefix, api_key_hash, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            user_id,
            payload.org_id,
            payload.email,
            payload.role,
            api_key_record.key_prefix,
            api_key_record.key_hash,
            utc_now(),
        ),
    )
    return {"id": user_id, "api_key": api_key_record.api_key}


def create_supplier(org_id: str, payload: SupplierCreate) -> dict:
    supplier_id = make_id("sup")
    execute(
        "INSERT INTO suppliers (id, org_id, name, category, risk_rating, preferred, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (supplier_id, org_id, payload.name, payload.category, payload.risk_rating, int(payload.preferred), utc_now()),
    )
    return {"id": supplier_id}


def list_suppliers(org_id: str, *, limit: int = DEFAULT_LIMIT, offset: int = 0) -> list[dict]:
    limit = _normalize_limit(limit)
    return fetch_all(
        "SELECT * FROM suppliers WHERE org_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (org_id, limit, max(0, offset)),
    )


def create_catalog_item(org_id: str, payload: CatalogItemCreate) -> dict:
    item_id = make_id("itm")
    execute(
        "INSERT INTO catalog_items (id, org_id, sku, name, unit, target_price, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (item_id, org_id, payload.sku, payload.name, payload.unit, payload.target_price, utc_now()),
    )
    return {"id": item_id}


def list_catalog_items(org_id: str, *, limit: int = DEFAULT_LIMIT, offset: int = 0) -> list[dict]:
    limit = _normalize_limit(limit)
    return fetch_all(
        "SELECT * FROM catalog_items WHERE org_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (org_id, limit, max(0, offset)),
    )


def create_rfq(org_id: str, created_by: str, payload: RFQCreate) -> dict:
    item = fetch_one("SELECT id FROM catalog_items WHERE id = ? AND org_id = ?", (payload.item_id, org_id))
    if not item:
        raise HTTPException(status_code=404, detail="Catalog item not found")

    rfq_id = make_id("rfq")
    execute(
        """
        INSERT INTO rfqs (id, org_id, item_id, quantity, max_budget, currency, status, evaluation_strategy, created_by, created_at)
        VALUES (?, ?, ?, ?, ?, ?, 'draft', ?, ?, ?)
        """,
        (
            rfq_id,
            org_id,
            payload.item_id,
            payload.quantity,
            payload.max_budget,
            payload.currency,
            payload.evaluation_strategy,
            created_by,
            utc_now(),
        ),
    )

    if payload.supplier_ids:
        link_values = [(rfq_id, supplier_id) for supplier_id in payload.supplier_ids]
        executemany("INSERT INTO rfq_suppliers (rfq_id, supplier_id) VALUES (?, ?)", link_values)

    return {"id": rfq_id}


def publish_rfq(org_id: str, rfq_id: str) -> None:
    exists = fetch_one("SELECT id, status FROM rfqs WHERE id = ? AND org_id = ?", (rfq_id, org_id))
    if not exists:
        raise HTTPException(status_code=404, detail="RFQ not found")
    if exists["status"] not in {"draft", "published"}:
        raise HTTPException(status_code=400, detail="Only draft RFQs can be published")
    execute("UPDATE rfqs SET status = 'published' WHERE id = ?", (rfq_id,))


def submit_bid(org_id: str, rfq_id: str, payload: BidCreate) -> dict:
    rfq = fetch_one("SELECT id, status FROM rfqs WHERE id = ? AND org_id = ?", (rfq_id, org_id))
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")
    if rfq["status"] not in {"published", "evaluated"}:
        raise HTTPException(status_code=400, detail="RFQ must be published before bids")

    supplier = fetch_one("SELECT id FROM suppliers WHERE id = ? AND org_id = ?", (payload.supplier_id, org_id))
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    bid_id = make_id("bid")
    execute(
        """
        INSERT INTO bids (id, rfq_id, supplier_id, unit_price, lead_time_days, warranty_months, quality_score, notes, submitted_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            bid_id,
            rfq_id,
            payload.supplier_id,
            payload.unit_price,
            payload.lead_time_days,
            payload.warranty_months,
            payload.quality_score,
            payload.notes,
            utc_now(),
        ),
    )
    return {"id": bid_id}


def evaluate_rfq(org_id: str, rfq_id: str) -> list[dict]:
    rfq = fetch_one("SELECT * FROM rfqs WHERE id = ? AND org_id = ?", (rfq_id, org_id))
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")

    bids = fetch_all(
        """
        SELECT b.*, s.risk_rating
        FROM bids b
        JOIN suppliers s ON s.id = b.supplier_id
        WHERE b.rfq_id = ? AND s.org_id = ?
        """,
        (rfq_id, org_id),
    )
    if not bids:
        raise HTTPException(status_code=400, detail="No bids to evaluate")

    execute("DELETE FROM bid_scores WHERE bid_id IN (SELECT id FROM bids WHERE rfq_id = ?)", (rfq_id,))

    scored = []
    for bid in bids:
        price_score = max(0.0, 10 - ((bid["unit_price"] - rfq["max_budget"]) / max(1, rfq["max_budget"]) * 10))
        quality_score = bid["quality_score"]
        delivery_score = max(0.0, 10 - bid["lead_time_days"])
        risk_score = max(0.0, 10 - bid["risk_rating"])

        strategy = rfq["evaluation_strategy"]
        if strategy == "cost":
            weights = (0.5, 0.2, 0.15, 0.15)
        elif strategy == "quality":
            weights = (0.2, 0.5, 0.15, 0.15)
        elif strategy == "resilience":
            weights = (0.2, 0.2, 0.2, 0.4)
        else:
            weights = (0.35, 0.3, 0.2, 0.15)

        composite = (
            weights[0] * price_score
            + weights[1] * quality_score
            + weights[2] * delivery_score
            + weights[3] * risk_score
        )

        execute(
            """
            INSERT INTO bid_scores (bid_id, price_score, quality_score, delivery_score, risk_score, composite_score, evaluated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                bid["id"],
                round(price_score, 2),
                round(quality_score, 2),
                round(delivery_score, 2),
                round(risk_score, 2),
                round(composite, 2),
                datetime.utcnow().isoformat() + "Z",
            ),
        )
        scored.append({"bid_id": bid["id"], "composite_score": round(composite, 2)})

    execute("UPDATE rfqs SET status = 'evaluated' WHERE id = ?", (rfq_id,))

    return sorted(scored, key=lambda item: item["composite_score"], reverse=True)


def create_award(org_id: str, awarded_by: str, rfq_id: str, payload: AwardRequest) -> dict:
    rfq = fetch_one("SELECT id, status FROM rfqs WHERE id = ? AND org_id = ?", (rfq_id, org_id))
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")
    if rfq["status"] not in {"evaluated", "awarded"}:
        raise HTTPException(status_code=400, detail="RFQ must be evaluated before awarding")

    bid = fetch_one(
        "SELECT b.id FROM bids b JOIN suppliers s ON s.id=b.supplier_id WHERE b.id = ? AND b.rfq_id = ? AND s.org_id = ?",
        (payload.bid_id, rfq_id, org_id),
    )
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found for this RFQ")

    award_id = make_id("awd")
    execute(
        "INSERT OR REPLACE INTO awards (id, rfq_id, winning_bid_id, awarded_by, rationale, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (award_id, rfq_id, payload.bid_id, awarded_by, payload.rationale, utc_now()),
    )
    execute("UPDATE rfqs SET status = 'awarded' WHERE id = ?", (rfq_id,))
    return {"id": award_id}


def rfq_details(org_id: str, rfq_id: str) -> dict:
    rfq = fetch_one("SELECT * FROM rfqs WHERE id = ? AND org_id = ?", (rfq_id, org_id))
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")

    bids = fetch_all(
        """
        SELECT b.*, s.name AS supplier_name, bs.composite_score
        FROM bids b
        JOIN suppliers s ON s.id = b.supplier_id
        LEFT JOIN bid_scores bs ON bs.bid_id = b.id
        WHERE b.rfq_id = ? AND s.org_id = ?
        ORDER BY bs.composite_score DESC, b.submitted_at ASC
        """,
        (rfq_id, org_id),
    )
    award = fetch_one("SELECT * FROM awards WHERE rfq_id = ?", (rfq_id,))

    return {"rfq": rfq, "bids": bids, "award": award}


def list_rfqs(org_id: str, *, limit: int = DEFAULT_LIMIT, offset: int = 0) -> list[dict]:
    limit = _normalize_limit(limit)
    return fetch_all(
        "SELECT * FROM rfqs WHERE org_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (org_id, limit, max(0, offset)),
    )
