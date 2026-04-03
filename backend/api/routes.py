from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from backend.db.database import db_ready
from backend.schemas.models import APIMessage, AwardRequest, BidCreate, CatalogItemCreate, OrganizationCreate, RFQCreate, SupplierCreate, UserCreate
from backend.services.auth import AuthContext, require_auth, require_roles
from backend.services.procurement import (
    create_award,
    create_catalog_item,
    create_organization,
    create_rfq,
    create_supplier,
    create_user,
    evaluate_rfq,
    list_catalog_items,
    list_rfqs,
    list_suppliers,
    publish_rfq,
    rfq_details,
    submit_bid,
)

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "procureos-api"}


@router.get("/ready")
def ready() -> dict:
    return {"ready": db_ready()}


@router.post("/platform/organizations", response_model=APIMessage)
def org_create(payload: OrganizationCreate):
    result = create_organization(payload)
    return APIMessage(message="Organization created", id=result["id"])


@router.post("/platform/users", response_model=dict)
def user_create(payload: UserCreate):
    return create_user(payload)


@router.post("/suppliers", response_model=APIMessage)
def supplier_create(payload: SupplierCreate, ctx: AuthContext = Depends(require_roles("admin", "sourcing_manager"))):
    result = create_supplier(ctx.org_id, payload)
    return APIMessage(message="Supplier created", id=result["id"])


@router.get("/suppliers")
def supplier_list(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    ctx: AuthContext = Depends(require_auth),
):
    return list_suppliers(ctx.org_id, limit=limit, offset=offset)


@router.post("/catalog/items", response_model=APIMessage)
def item_create(payload: CatalogItemCreate, ctx: AuthContext = Depends(require_roles("admin", "sourcing_manager"))):
    result = create_catalog_item(ctx.org_id, payload)
    return APIMessage(message="Catalog item created", id=result["id"])


@router.get("/catalog/items")
def item_list(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    ctx: AuthContext = Depends(require_auth),
):
    return list_catalog_items(ctx.org_id, limit=limit, offset=offset)


@router.post("/rfqs", response_model=APIMessage)
def rfq_create(payload: RFQCreate, ctx: AuthContext = Depends(require_roles("admin", "sourcing_manager", "analyst"))):
    result = create_rfq(ctx.org_id, ctx.user_id, payload)
    return APIMessage(message="RFQ created", id=result["id"])


@router.get("/rfqs")
def rfq_list(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    ctx: AuthContext = Depends(require_auth),
):
    return list_rfqs(ctx.org_id, limit=limit, offset=offset)


@router.post("/rfqs/{rfq_id}/publish", response_model=APIMessage)
def rfq_publish(rfq_id: str, ctx: AuthContext = Depends(require_roles("admin", "sourcing_manager"))):
    publish_rfq(ctx.org_id, rfq_id)
    return APIMessage(message="RFQ published", id=rfq_id)


@router.post("/rfqs/{rfq_id}/bids", response_model=APIMessage)
def bid_submit(rfq_id: str, payload: BidCreate, ctx: AuthContext = Depends(require_roles("admin", "sourcing_manager", "analyst"))):
    result = submit_bid(ctx.org_id, rfq_id, payload)
    return APIMessage(message="Bid submitted", id=result["id"])


@router.post("/rfqs/{rfq_id}/evaluate")
def rfq_evaluate(rfq_id: str, ctx: AuthContext = Depends(require_roles("admin", "sourcing_manager", "analyst"))):
    return evaluate_rfq(ctx.org_id, rfq_id)


@router.post("/rfqs/{rfq_id}/award", response_model=APIMessage)
def rfq_award(rfq_id: str, payload: AwardRequest, ctx: AuthContext = Depends(require_roles("admin", "sourcing_manager"))):
    result = create_award(ctx.org_id, ctx.user_id, rfq_id, payload)
    return APIMessage(message="Award created", id=result["id"])


@router.get("/rfqs/{rfq_id}")
def rfq_get(rfq_id: str, ctx: AuthContext = Depends(require_auth)):
    return rfq_details(ctx.org_id, rfq_id)
