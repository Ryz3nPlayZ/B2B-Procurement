# ProcureOS — Enterprise Procurement API

ProcureOS is now packaged as a deployable, API-first procurement backend suitable for **paid pilots and internal production use**.

## Is it ready for people to buy and use?

**Yes for paid pilots now**, with critical baseline controls implemented:
- Multi-tenant data isolation (`org_id`-scoped reads/writes)
- Role-based access control (`admin`, `sourcing_manager`, `analyst`, `viewer`)
- API key security with **hash-at-rest** storage
- RFQ lifecycle state machine (`draft → published → evaluated → awarded`)
- Deterministic audit-ready scoring and award rationale
- Readiness endpoint and basic per-IP rate limiting
- Containerized deployment and bootstrap tooling

For large regulated enterprises, see `docs/prd/ENTERPRISE_PRD_SUMMER_2026.md` for remaining roadmap items (SSO, approvals, SIEM, SOC2 controls, ERP adapters).

## Architecture

- `backend/app.py` — FastAPI app + middleware (CORS, rate limiting)
- `backend/api/routes.py` — versioned routes (`/v1`)
- `backend/db/database.py` — schema + DB bootstrap + readiness check
- `backend/services/auth.py` — hashed API key auth + role checks
- `backend/services/procurement.py` — procurement workflows and scoring
- `backend/schemas/models.py` — Pydantic contracts
- `scripts/bootstrap_enterprise.py` — first-tenant bootstrap helper

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.app:app --reload --port 8090
```

Health + readiness:

```bash
curl http://localhost:8090/v1/health
curl http://localhost:8090/v1/ready
```

## Bootstrap a tenant and admin key

```bash
python scripts/bootstrap_enterprise.py --org "Acme Corp" --email "admin@acme.com"
```

## Docker deployment

```bash
docker compose up --build
```

## API summary

Platform bootstrap (no auth):
- `POST /v1/platform/organizations`
- `POST /v1/platform/users` (returns one-time API key)

Authenticated APIs:
- `POST /v1/suppliers`, `GET /v1/suppliers?limit=&offset=`
- `POST /v1/catalog/items`, `GET /v1/catalog/items?limit=&offset=`
- `POST /v1/rfqs`, `GET /v1/rfqs?limit=&offset=`
- `POST /v1/rfqs/{rfq_id}/publish`
- `POST /v1/rfqs/{rfq_id}/bids`
- `POST /v1/rfqs/{rfq_id}/evaluate`
- `POST /v1/rfqs/{rfq_id}/award`
- `GET /v1/rfqs/{rfq_id}`

## Tests

```bash
pytest -q tests/test_enterprise_backend.py
pytest -q tests/test_procurement_engine.py
```


## UI experience (polished operator console)

Run the UI locally:

```bash
uvicorn ui.app:app --reload --port 8080
```

UI API + websocket endpoints:
- `GET /api/health`
- `GET /api/metrics`
- `POST /api/sessions`
- `GET /api/sessions`
- `GET /api/sessions/{session_id}`
- `WS /ws/events`

## Product strategy + PRD

- `docs/prd/ENTERPRISE_PRD_SUMMER_2026.md`

## Legacy modules

Legacy demo modules in `ui/`, `agents/`, and `product/` are retained for reference and experimentation.
