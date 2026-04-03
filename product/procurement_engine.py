from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List
from uuid import uuid4


@dataclass(frozen=True)
class SellerProfile:
    seller_id: str
    base_price: float
    min_price: float
    quality_score: float
    delivery_days: int
    reliability_score: float
    message: str


class ProcurementEngine:
    """Simple, deterministic sourcing engine for product demo and API use."""

    def __init__(self) -> None:
        self._sessions: Dict[str, dict] = {}
        self._sellers: List[SellerProfile] = [
            SellerProfile(
                seller_id="volumehub",
                base_price=68.0,
                min_price=56.0,
                quality_score=7.2,
                delivery_days=9,
                reliability_score=8.0,
                message="Volume-focused supplier with strong unit economics.",
            ),
            SellerProfile(
                seller_id="precisionworks",
                base_price=76.0,
                min_price=64.0,
                quality_score=9.3,
                delivery_days=6,
                reliability_score=8.9,
                message="Premium supplier optimized for mission-critical SKUs.",
            ),
            SellerProfile(
                seller_id="agileparts",
                base_price=72.0,
                min_price=60.0,
                quality_score=8.4,
                delivery_days=4,
                reliability_score=7.8,
                message="Fast-turn supplier for volatile demand and urgent replenishment.",
            ),
        ]

    def create_session(self, payload: dict) -> dict:
        rfq = {
            "product_id": payload.get("product_id", "TS-100"),
            "quantity": int(payload.get("quantity", 100)),
            "max_budget": float(payload.get("max_budget", 75.0)),
            "priority": payload.get("priority", "balanced"),
        }
        session_id = f"rfq-{uuid4().hex[:8]}"
        created_at = datetime.utcnow().isoformat() + "Z"

        round_one = [self._initial_quote(seller, rfq) for seller in self._sellers]
        negotiated = [self._negotiate_quote(quote, rfq) for quote in round_one]
        ranked = sorted(negotiated, key=lambda q: q["composite_score"], reverse=True)
        winner = ranked[0]

        milestones = [
            {"type": "rfq_created", "note": "RFQ submitted", "at": created_at},
            {"type": "quotes_received", "note": f"{len(round_one)} supplier quotes received", "at": created_at},
            {
                "type": "winner_selected",
                "note": f"{winner['seller_id']} selected at ${winner['final_price']:.2f}/unit",
                "at": created_at,
            },
        ]

        session = {
            "session_id": session_id,
            "created_at": created_at,
            "status": "awarded",
            "rfq": rfq,
            "quotes": ranked,
            "winner": winner,
            "milestones": milestones,
            "next_actions": self._next_actions(winner, rfq),
        }
        self._sessions[session_id] = session
        return session

    def list_sessions(self) -> List[dict]:
        return list(self._sessions.values())

    def get_session(self, session_id: str) -> dict | None:
        return self._sessions.get(session_id)

    def _initial_quote(self, seller: SellerProfile, rfq: dict) -> dict:
        qty = rfq["quantity"]
        quantity_discount = min(0.15, qty / 5000)
        offered_price = round(seller.base_price * (1 - quantity_discount), 2)
        return {
            "seller_id": seller.seller_id,
            "opening_price": offered_price,
            "min_price": seller.min_price,
            "quality_score": seller.quality_score,
            "delivery_days": seller.delivery_days,
            "reliability_score": seller.reliability_score,
            "narrative": seller.message,
        }

    def _negotiate_quote(self, quote: dict, rfq: dict) -> dict:
        budget = rfq["max_budget"]
        opening_price = quote["opening_price"]

        if opening_price <= budget:
            final_price = opening_price
            concession_pct = 0.0
        else:
            gap = opening_price - budget
            concession_pct = min(0.12, gap / opening_price)
            final_price = max(quote["min_price"], round(opening_price * (1 - concession_pct), 2))

        price_fitness = max(0.0, min(10.0, 10 - max(0, final_price - budget) / max(budget, 1) * 10))
        delivery_fitness = max(0.0, 10 - quote["delivery_days"])

        priority = rfq["priority"]
        if priority == "cost":
            weights = (0.45, 0.2, 0.15, 0.2)
        elif priority == "quality":
            weights = (0.2, 0.45, 0.15, 0.2)
        else:
            weights = (0.3, 0.3, 0.2, 0.2)

        composite_score = (
            weights[0] * price_fitness
            + weights[1] * quote["quality_score"]
            + weights[2] * delivery_fitness
            + weights[3] * quote["reliability_score"]
        )

        quote.update(
            {
                "final_price": final_price,
                "concession_pct": round(concession_pct * 100, 2),
                "price_fitness": round(price_fitness, 2),
                "delivery_fitness": round(delivery_fitness, 2),
                "composite_score": round(composite_score, 2),
            }
        )
        return quote

    def _next_actions(self, winner: dict, rfq: dict) -> List[str]:
        return [
            f"Generate purchase order for {rfq['quantity']} units of {rfq['product_id']}.",
            f"Lock supplier SLA with {winner['seller_id']} at ${winner['final_price']:.2f}/unit.",
            "Invite top 2 runner-up suppliers into a backup allocation framework.",
        ]
