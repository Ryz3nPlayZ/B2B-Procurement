# agents/coordinator_agent.py
import logging
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
from config import settings
from protocols.rfq_protocol import RFQMessage, RFQBroadcast
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agents.coordinator")

class RegisterSeller(BaseModel):
    seller_name: str

coordinator = Agent(
    name="CoordinatorAgent",
    port=8000,
    seed=settings.COORDINATOR_AGENT_SEED,
    endpoint=["http://127.0.0.1:8000/submit"],
)

SELLER_REGISTRY = {}
fund_agent_if_low(coordinator.wallet.address())

@coordinator.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"Coordinator Agent started. My address is: {coordinator.address}")
    ctx.logger.info("Waiting for sellers to register...")

@coordinator.on_message(model=RegisterSeller)
async def handle_register_seller(ctx: Context, sender: str, msg: RegisterSeller):
    ctx.logger.info(f"Received registration from '{msg.seller_name}' with address {sender}")
    SELLER_REGISTRY[msg.seller_name] = sender
    ctx.logger.info(f"Current registry: {SELLER_REGISTRY}")

@coordinator.on_message(model=RFQMessage)
async def handle_rfq_from_buyer(ctx: Context, sender: str, msg: RFQMessage):
    ctx.logger.info(f"Received direct RFQ for '{msg.product_id}' from buyer {sender}")
    if not SELLER_REGISTRY:
        ctx.logger.warning("No sellers registered. Cannot forward RFQ.")
        return

    broadcast_msg = RFQBroadcast(rfq=msg, buyer_address=sender, buyer_name="BuyerAgent")
    for name, address in SELLER_REGISTRY.items():
        ctx.logger.info(f"Forwarding RFQ to seller: {name}")
        await ctx.send(address, broadcast_msg)

if __name__ == "__main__":
    coordinator.run()