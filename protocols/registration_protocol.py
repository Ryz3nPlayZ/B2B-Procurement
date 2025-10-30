# protocols/registration_protocol.py

from uagents import Protocol
from pydantic import BaseModel

class RegisterSeller(BaseModel):
    """Message from a seller to register with the coordinator."""
    seller_name: str

# Create the protocol instance for registration
registration_protocol = Protocol("SellerRegistration")