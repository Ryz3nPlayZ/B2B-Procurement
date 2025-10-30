# metta/queries/seller_queries.py

import logging
from typing import Dict, Any, List
from ..metta_engine import MeTTaEngine

class SellerQueries:
    def __init__(self, metta_engine: MeTTaEngine):
        self.metta_engine = metta_engine
        self.logger = logging.getLogger("seller_queries")

    async def get_inventory_for_product(self, product_id: str) -> List[Dict[str, Any]]:
        query = f"!(match &self (Inventory {product_id} $loc $qty $cost) (list $loc $qty $cost))"
        results = await self.metta_engine.execute_query(query)
        
        inventory_list = []
        for result in results:
            if isinstance(result, list) and len(result) >= 4:
                inventory_list.append({
                    "location": str(result[1]),
                    "quantity": int(float(str(result[2]))),  # FIXED
                    "cost": float(str(result[3]))            # FIXED
                })
        return inventory_list

    async def check_certification(self, product_id: str, cert_type: str) -> bool:
        query = f"!(match &self (certification {product_id} {cert_type} $issuer) True)"
        results = await self.metta_engine.execute_query(query)
        return len(results) > 0

    async def get_pricing_for_product(self, product_id: str) -> Dict[str, Any]:
        query = f"!(match &self (Pricing {product_id} $tier $price $cond) (list $tier $price $cond))"
        results = await self.metta_engine.execute_query(query)
        
        pricing = {}
        for result in results:
            if isinstance(result, list) and len(result) >= 4:
                tier = str(result[1])
                pricing[tier] = {
                    "price": float(str(result[2])),      # FIXED
                    "conditions": str(result[3])
                }
        return pricing

    async def get_llm_system_prompt(self) -> str:
        query = '!(match &self (llm-instruction system-prompt $text) (list $text))'
        results = await self.metta_engine.execute_query(query)
        if results and isinstance(results[0], list) and len(results[0]) > 1:
            return str(results[0][1]).strip('"')
        return "You are a professional sales agent."

    async def get_delivery_time(self, product_id: str) -> int:
        query = f"!(match &self (delivery-time {product_id} $days) (list $days))"
        results = await self.metta_engine.execute_query(query)
        if results and isinstance(results[0], list) and len(results[0]) > 1:
            return int(float(str(results[0][1])))  # FIXED
        return 14

    async def get_warranty(self, product_id: str) -> int:
        query = f"!(match &self (warranty {product_id} $months) (list $months))"
        results = await self.metta_engine.execute_query(query)
        if results and isinstance(results[0], list) and len(results[0]) > 1:
            return int(float(str(results[0][1])))  # FIXED
        return 12

    async def get_specifications(self, product_id: str) -> Dict[str, str]:
        query = f"!(match &self (specification {product_id} $spec $value) (list $spec $value))"
        results = await self.metta_engine.execute_query(query)
        
        specs = {}
        for result in results:
            if isinstance(result, list) and len(result) >= 3:
                specs[str(result[1])] = str(result[2])
        return specs

    async def get_strategy_instruction(self) -> str:
        persona_query = "!(match &self (persona $p) (list $p))"
        persona_res = await self.metta_engine.execute_query(persona_query)
        persona = str(persona_res[0][1]) if persona_res and len(persona_res[0]) > 1 else "default"

        strategy_query = f"!(match &self (strategy-instruction {persona} $text) (list $text))"
        strategy_res = await self.metta_engine.execute_query(strategy_query)
        if strategy_res and isinstance(strategy_res[0], list) and len(strategy_res[0]) > 1:
            return str(strategy_res[0][1]).strip('"')
        return "Focus on customer needs."

    async def get_min_acceptable_price(self, product_id: str) -> float:
        query = f"!(match &self (min-acceptable-price {product_id} $price) (list $price))"
        results = await self.metta_engine.execute_query(query)
        if results and isinstance(results[0], list) and len(results[0]) > 1:
            return float(str(results[0][1]))  # FIXED
        return 0.0

    async def get_max_discount_percent(self, product_id: str) -> float:
        query = f"!(match &self (max-discount-percent {product_id} $pct) (list $pct))"
        results = await self.metta_engine.execute_query(query)
        if results and isinstance(results[0], list) and len(results[0]) > 1:
            return float(str(results[0][1]))  # FIXED
        return 0.0

    async def get_negotiation_style(self) -> str:
        query = '!(match &self (llm-instruction negotiation-style $text) (list $text))'
        results = await self.metta_engine.execute_query(query)
        if results and isinstance(results[0], list) and len(results[0]) > 1:
            return str(results[0][1]).strip('"')
        return "Be professional and fair."