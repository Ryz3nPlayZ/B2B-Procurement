# protocols/quote_protocol.py

from uagents import Protocol
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class QuoteMessage(BaseModel):
    """A seller's quote in response to an RFQ."""
    product_id: str
    price_per_unit: float
    delivery_days: int
    compliance_statements: Dict[str, Any] = Field(default_factory=dict)  # Changed from Dict[str, bool]
    llm_generated_text: str  # The persuasive text from the LLM

# Create the protocol instance
quote_protocol = Protocol("SupplyChainQuote")