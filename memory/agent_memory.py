import json
import os
from collections import deque

class AgentMemory:
    def __init__(self, agent_id: str, memory_dir: str = "memory"):
        self.agent_id = agent_id
        self.memory_dir = memory_dir
        os.makedirs(self.memory_dir, exist_ok=True)
        self.seller_reputations_file = os.path.join(self.memory_dir, f"{agent_id}_seller_reputations.json")
        self.market_intelligence_file = os.path.join(self.memory_dir, f"{agent_id}_market_intelligence.json")
        
        self.seller_reputations = self._load_json(self.seller_reputations_file, {})
        self.market_intelligence = self._load_json(self.market_intelligence_file, {})
        
        # Ensure market intelligence has a structure for product trends
        if "product_trends" not in self.market_intelligence:
            self.market_intelligence["product_trends"] = {}

    def _load_json(self, filepath: str, default_value):
        """Load JSON file and convert lists back to deques where needed."""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                # Convert lists back to deques in product_trends
                if isinstance(data, dict) and "product_trends" in data:
                    for product_id, trends in data["product_trends"].items():
                        if "prices" in trends and isinstance(trends["prices"], list):
                            trends["prices"] = deque(trends["prices"], maxlen=10)
                        if "delivery_days" in trends and isinstance(trends["delivery_days"], list):
                            trends["delivery_days"] = deque(trends["delivery_days"], maxlen=10)
                
                return data
            except json.JSONDecodeError:
                print(f"WARNING: Corrupted JSON file '{filepath}'. Reinitializing.")
                return default_value
            except OSError as e:
                print(f"WARNING: Error loading '{filepath}': {e}. Reinitializing.")
                return default_value
        return default_value

    def _save_json(self, filepath: str, data):
        """Save data to JSON file with proper serialization."""
        try:
            # Convert deques to lists for JSON serialization
            def convert_deque(obj):
                if isinstance(obj, deque):
                    return list(obj)
                elif isinstance(obj, dict):
                    return {k: convert_deque(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_deque(item) for item in obj]
                return obj
            
            serializable_data = convert_deque(data)
            
            with open(filepath, 'w') as f:
                json.dump(serializable_data, f, indent=4)
        except OSError as e:
            print(f"ERROR: Could not save to '{filepath}': {e}. Memory will not be persistent.")

    def learn_seller_behavior(self, seller_address: str, behavior: dict):
        """
        Records a seller's behavior (e.g., deal accepted, quality score).
        Behavior dict should contain:
        - "accepted": bool (True if deal was accepted, False if rejected)
        - "quality_score": float (e.g., final score of the quote)
        - "negotiated": bool (True if negotiation occurred, False if direct acceptance)
        """
        if seller_address not in self.seller_reputations:
            self.seller_reputations[seller_address] = {
                "interactions": [],
                "acceptance_rate": 0.0,
                "avg_quality_score": 0.0
            }
        
        self.seller_reputations[seller_address]["interactions"].append(behavior)
        
        # Update metrics
        total_interactions = len(self.seller_reputations[seller_address]["interactions"])
        accepted_deals = sum(1 for i in self.seller_reputations[seller_address]["interactions"] if i["accepted"])
        total_quality_score = sum(i["quality_score"] for i in self.seller_reputations[seller_address]["interactions"])
        
        self.seller_reputations[seller_address]["acceptance_rate"] = accepted_deals / total_interactions
        self.seller_reputations[seller_address]["avg_quality_score"] = total_quality_score / total_interactions
        
        self._save_json(self.seller_reputations_file, self.seller_reputations)

    def get_seller_reputation(self, seller_address: str) -> float:
        """Returns a combined reputation score for a seller (0.0 to 1.0)."""
        if seller_address not in self.seller_reputations:
            return 0.5  # Neutral reputation for unknown sellers
        
        rep_data = self.seller_reputations[seller_address]
        
        # Simple weighted average: 70% acceptance rate, 30% avg quality score
        # Assuming quality scores are already normalized or within a comparable range
        reputation_score = (rep_data["acceptance_rate"] * 0.7) + (rep_data["avg_quality_score"] * 0.3)
        
        return reputation_score

    def learn_market_trend(self, product_id: str, price: float, delivery_days: int):
        """Records market data for a product to detect trends."""
        if product_id not in self.market_intelligence["product_trends"]:
            self.market_intelligence["product_trends"][product_id] = {
                "prices": deque(maxlen=10),  # Keep last 10 prices
                "delivery_days": deque(maxlen=10) # Keep last 10 delivery days
            }
        
        self.market_intelligence["product_trends"][product_id]["prices"].append(price)
        self.market_intelligence["product_trends"][product_id]["delivery_days"].append(delivery_days)
        
        self._save_json(self.market_intelligence_file, self.market_intelligence)

    def get_market_insight(self, product_id: str) -> dict:
        """Provides insights into market trends for a given product."""
        if product_id not in self.market_intelligence["product_trends"]:
            return {"sample_size": 0, "avg_price": 0.0, "price_trend": "N/A"}
        
        product_data = self.market_intelligence["product_trends"][product_id]
        prices = list(product_data["prices"])
        
        if not prices:
            return {"sample_size": 0, "avg_price": 0.0, "price_trend": "N/A"}
        
        avg_price = sum(prices) / len(prices)
        
        price_trend = "stable"
        if len(prices) >= 2:
            if prices[-1] > prices[0]:
                price_trend = "increasing"
            elif prices[-1] < prices[0]:
                price_trend = "decreasing"
        
        return {
            "sample_size": len(prices),
            "avg_price": avg_price,
            "price_trend": price_trend,
            "latest_price": prices[-1]
        }
