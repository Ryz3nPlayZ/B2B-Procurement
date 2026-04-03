from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class OrganizationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    plan: Literal["starter", "growth", "enterprise"] = "starter"


class UserCreate(BaseModel):
    org_id: str
    email: str
    role: Literal["admin", "sourcing_manager", "analyst", "viewer"] = "admin"


class SupplierCreate(BaseModel):
    name: str
    category: str
    risk_rating: float = Field(ge=0, le=10)
    preferred: bool = False


class CatalogItemCreate(BaseModel):
    sku: str
    name: str
    unit: str = "unit"
    target_price: float = Field(gt=0)


class RFQCreate(BaseModel):
    item_id: str
    quantity: int = Field(ge=1)
    max_budget: float = Field(gt=0)
    currency: str = "USD"
    evaluation_strategy: Literal["balanced", "cost", "quality", "resilience"] = "balanced"
    supplier_ids: list[str] = Field(default_factory=list)


class BidCreate(BaseModel):
    supplier_id: str
    unit_price: float = Field(gt=0)
    lead_time_days: int = Field(ge=1)
    warranty_months: int = Field(ge=0)
    quality_score: float = Field(ge=0, le=10)
    notes: str = ""


class AwardRequest(BaseModel):
    bid_id: str
    rationale: str = Field(min_length=10, max_length=1000)


class APIMessage(BaseModel):
    message: str
    id: Optional[str] = None
