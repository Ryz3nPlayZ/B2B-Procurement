# protocols/rfq_protocol.py

from uagents import Protocol
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class RFQMessage(BaseModel):
    """Message to request a quote for a product."""
    product_id: str
    quantity: int
    required_specs: Dict[str, Any] = Field(default_factory=dict)

class RFQBroadcast(BaseModel):
    """Message broadcast by the coordinator to all sellers."""
    rfq: RFQMessage
    buyer_address: str
    buyer_name: str

# Create the protocol instance
rfq_protocol = Protocol("SupplyChainRFQ")