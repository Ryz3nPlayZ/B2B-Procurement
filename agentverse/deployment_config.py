# agentverse/deployment_config.py

AGENT_CONFIGS = {
    "buyer_agent": {
        "name": "ASI Buyer Agent",
        "description": "Intelligent procurement agent with MeTTa reasoning and LLM evaluation",
        "tags": ["procurement", "b2b", "negotiation", "innovationlab", "hackathon"],
        "protocols": ["rfq", "quote", "negotiation", "chat"],
        "chat_enabled": True,
        "chat_commands": [
            "/rfq <product_id> <quantity> <budget>",
            "/status",
            "/history"
        ]
    },
    "coordinator_agent": {
        "name": "ASI Coordinator",
        "description": "Central coordination agent for RFQ broadcasting and agent discovery",
        "tags": ["coordinator", "registry", "innovationlab", "hackathon"],
        "protocols": ["rfq", "registration", "chat"],
        "chat_enabled": True
    },
    "seller_a_agent": {
        "name": "Seller A - Volume Specialist",
        "description": "Fast delivery, competitive pricing, volume-focused supplier",
        "tags": ["supplier", "wholesale", "fast-delivery", "innovationlab", "hackathon"],
        "protocols": ["rfq", "quote", "negotiation", "chat"],
        "chat_enabled": True
    },
    "seller_b_agent": {
        "name": "Seller B - Premium Quality",
        "description": "Premium specs, extended warranties, quality-focused supplier",
        "tags": ["supplier", "premium", "quality", "innovationlab", "hackathon"],
        "protocols": ["rfq", "quote", "negotiation", "chat"],
        "chat_enabled": True
    }
}
