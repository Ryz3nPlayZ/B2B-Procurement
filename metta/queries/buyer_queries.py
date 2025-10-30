# metta/queries/buyer_queries.py

import logging
from typing import Dict, Any
from ..metta_engine import MeTTaEngine

logger = logging.getLogger(__name__)

class BuyerQueries:
    def __init__(self, metta_engine: MeTTaEngine):
        self.metta_engine = metta_engine

    async def get_required_quantity(self, product_id: str) -> int:
        """Hardcoded for MVP - return from MeTTa later"""
        return 50  # Hardcoded: need 50 units

    async def get_max_budget_per_unit(self, product_id: str) -> float:
        """Hardcoded for MVP - return from MeTTa later"""
        return 75.00  # Hardcoded: $75/unit budget

    async def get_llm_system_prompt(self) -> str:
        """Hardcoded for MVP"""
        return "You are a strategic procurement agent. Analyze quotes objectively based on price, delivery, warranty, and specifications."

    async def get_procurement_policies(self) -> Dict[str, Any]:
        """Return basic procurement policies"""
        return {
            "max_budget": 75.00,
            "required_quantity": 50,
            "required_certifications": ["ISO9001"]
        }