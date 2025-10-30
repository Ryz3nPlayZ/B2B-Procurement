# agents/seller_agent.py

import logging
import sys
import asyncio
import json
from uagents import Agent, Context
from uagents.setup import fund_agent_if_low
from config import settings
from protocols.rfq_protocol import RFQBroadcast
from protocols.quote_protocol import QuoteMessage
from pydantic import BaseModel
from llm.llm_router import LLMRouter
from metta.metta_engine import MeTTaEngine
from metta.queries.seller_queries import SellerQueries

# --- Message Models ---
class RegisterSeller(BaseModel):
    seller_name: str

class CounterOffer(BaseModel):
    """Buyer's counter-offer during negotiation"""
    product_id: str
    proposed_price: float
    reasoning: str

# --- Agent Configuration ---
if len(sys.argv) != 2 or sys.argv[1] not in ['seller_a', 'seller_b']:
    print("Usage: python -m agents.seller_agent <seller_a | seller_b>")
    sys.exit(1)

SELLER_NAME = sys.argv[1]
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(f"agents.{SELLER_NAME}")

AGENT_SEED = settings.SELLER_A_AGENT_SEED if SELLER_NAME == 'seller_a' else settings.SELLER_B_AGENT_SEED
KB_FILE = settings.SELLER_A_KB_FILE if SELLER_NAME == 'seller_a' else settings.SELLER_B_KB_FILE

# --- Agent Definition ---
agent = Agent(
    name=SELLER_NAME,
    port=8001 if SELLER_NAME == 'seller_a' else 8002,
    seed=AGENT_SEED,
    endpoint=[f"http://127.0.0.1:{8001 if SELLER_NAME == 'seller_a' else 8002}/submit"],
)

fund_agent_if_low(agent.wallet.address())
llm_router = LLMRouter()
metta_engine = MeTTaEngine()
seller_queries = SellerQueries(metta_engine)

# Negotiation state
ACTIVE_NEGOTIATIONS = {}

# --- Agent Logic ---
@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"Seller Agent '{SELLER_NAME}' started with address: {agent.address}")
    await metta_engine.load_metta_file(KB_FILE)
    await asyncio.sleep(2)
    
    coordinator_address = "agent1qwtcsxnr2957et869u38r3yafphfg2dlppl86t99ll0ye8nv2f672zrma08"
    await ctx.send(coordinator_address, RegisterSeller(seller_name=SELLER_NAME))
    ctx.logger.info("Registration message sent to coordinator.")

@agent.on_message(model=RFQBroadcast)
async def handle_rfq_broadcast(ctx: Context, sender: str, msg: RFQBroadcast):
    rfq = msg.rfq
    ctx.logger.info(f"📨 Received RFQ for '{rfq.product_id}' from coordinator")
    ctx.logger.info(f"   Buyer address: {msg.buyer_address}")
    ctx.logger.info(f"   Starting feasibility check...")

    # --- MeTTa First: Feasibility Check ---
    inventory_list = await seller_queries.get_inventory_for_product(rfq.product_id)
    total_inventory = sum(item['quantity'] for item in inventory_list)

    if total_inventory < rfq.quantity:
        ctx.logger.warning(f"FEASIBILITY FAIL: Insufficient inventory. Have {total_inventory}, need {rfq.quantity}. Declining.")
        return

    ctx.logger.info(f"FEASIBILITY PASS: Inventory check successful ({total_inventory} available).")

    # Check certifications
    is_certified = await seller_queries.check_certification(rfq.product_id, "ISO9001")
    if rfq.required_specs.get("certification") == "ISO9001" and not is_certified:
        ctx.logger.warning(f"FEASIBILITY FAIL: Missing required ISO9001 certification. Declining.")
        return
    
    ctx.logger.info(f"FEASIBILITY PASS: Certification check successful (ISO9001: {is_certified}).")
    ctx.logger.info("RFQ is feasible. Using LLM to determine pricing strategy...")

    # --- Fetch MeTTa data ---
    pricing_data = await seller_queries.get_pricing_for_product(rfq.product_id)
    delivery_days = await seller_queries.get_delivery_time(rfq.product_id)
    warranty_months = await seller_queries.get_warranty(rfq.product_id)
    specifications = await seller_queries.get_specifications(rfq.product_id)
    strategy = await seller_queries.get_strategy_instruction()
    system_prompt = await seller_queries.get_llm_system_prompt()
    min_price = await seller_queries.get_min_acceptable_price(rfq.product_id)

    # --- LLM DECIDES PRICING STRATEGY (JSON Response) ---
    buyer_budget = rfq.required_specs.get("max_budget", "Unknown")
    
    pricing_strategy_prompt = f"""You are deciding pricing strategy for an RFQ.

**Context:**
- Product: {rfq.product_id}
- Quantity: {rfq.quantity} units
- Buyer's Budget: {buyer_budget if buyer_budget != "Unknown" else "Unknown (they didn't share)"}
- Your Pricing Tiers: {json.dumps(pricing_data, indent=2)}
- Your Minimum Acceptable: ${min_price}/unit
- Your Strategy: {strategy}

**Decision:**
Which pricing tier should you quote? Consider:
1. Quantity thresholds
2. Buyer's budget (if known)
3. Your strategy (volume vs margin)
4. Competitiveness

Respond ONLY with valid JSON:
{{
  "chosen_tier": "retail" | "wholesale" | "bulk",
  "quoted_price": 75.0,
  "reasoning": "Brief explanation of why this tier makes sense"
}}"""

    llm_pricing_response = await llm_router.generate(
        agent_role="seller",
        prompt=pricing_strategy_prompt,
        system_message=system_prompt
    )

    # Parse LLM pricing decision
    try:
        import re
        
        # Strip markdown code blocks if present
        cleaned_response = llm_pricing_response.strip()
        if cleaned_response.startswith("```"):
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', cleaned_response, re.DOTALL)
            if json_match:
                cleaned_response = json_match.group(1)
            else:
                json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
                if json_match:
                    cleaned_response = json_match.group()
        
        pricing_decision = json.loads(cleaned_response)
            
        chosen_tier = pricing_decision["chosen_tier"]
        actual_price = pricing_decision["quoted_price"]
        pricing_reasoning = pricing_decision["reasoning"]
        
        ctx.logger.info(f"💡 LLM PRICING DECISION:")
        ctx.logger.info(f"  Tier: {chosen_tier}")
        ctx.logger.info(f"  Price: ${actual_price}/unit")
        ctx.logger.info(f"  Reasoning: {pricing_reasoning}")
        
    except Exception as e:
        ctx.logger.error(f"❌ Failed to parse LLM pricing decision: {e}")
        ctx.logger.error(f"Raw response: {llm_pricing_response[:200]}")
        ctx.logger.warning("⚠️  Falling back to MeTTa-based tier selection...")
        
        # Fallback logic
        if rfq.quantity >= 200:
            actual_price = pricing_data.get('bulk', {}).get('price', 999)
            chosen_tier = "bulk"
        elif rfq.quantity >= 50:
            actual_price = pricing_data.get('wholesale', {}).get('price', 999)
            chosen_tier = "wholesale"
        else:
            actual_price = pricing_data.get('retail', {}).get('price', 999)
            chosen_tier = "retail"

    # --- Generate Sales Pitch (LLM) ---
    sales_pitch_prompt = f"""Generate a professional sales quote for this RFQ.

**CRITICAL REQUIREMENTS:**
1. Your quote MUST state the price as ${actual_price}/unit
2. You MUST justify your pricing with specific technical advantages
3. If your price is higher than competitors might offer, EMPHASIZE what makes you worth it

**Context:**
- Product: {rfq.product_id}
- Quantity: {rfq.quantity} units
- YOUR FINAL PRICE: ${actual_price}/unit (tier: {chosen_tier})
- Buyer's Budget: {buyer_budget}

**Your Competitive Advantages (EMPHASIZE THESE EXPLICITLY):**
- Delivery: {delivery_days} days
- Warranty: {warranty_months} months {"(2X INDUSTRY STANDARD)" if warranty_months >= 24 else ""}
- Specifications: {json.dumps(specifications, indent=2)}
- ISO9001 Certified: {is_certified}

**Your Strategy:** {strategy}

**If your price is premium ($70+/unit):**
You MUST justify it by highlighting:
- Extended warranty period (if applicable)
- Superior precision/specs (mention exact values!)
- Faster delivery or better support
- Certifications and quality guarantees

Generate a 2-3 sentence sales pitch that:
1. CLEARLY states your price: ${actual_price}/unit
2. Mentions 2-3 SPECIFIC technical differentiators (use actual spec values!)
3. Justifies your value proposition clearly

Example (for premium pricing):
"We offer the {rfq.product_id} at ${actual_price}/unit with ±0.2°C precision (vs industry standard ±0.5°C), a 24-month warranty (2X standard), and German-engineered components. Delivery in {delivery_days} days with dedicated support."

Be professional, specific, and data-driven."""

    sales_pitch = await llm_router.generate(
        agent_role="seller",
        prompt=sales_pitch_prompt,
        system_message=system_prompt
    )
    
    ctx.logger.info(f"📝 Sales pitch generated: {sales_pitch[:100]}...")

    # Store negotiation state
    ACTIVE_NEGOTIATIONS[msg.buyer_address] = {
        "product_id": rfq.product_id,
        "quantity": rfq.quantity,
        "round": 0,
        "last_price": actual_price,
        "original_price": actual_price,
        "chosen_tier": chosen_tier
    }

    # --- Send Quote ---
    quote = QuoteMessage(
        product_id=rfq.product_id,
        price_per_unit=actual_price,
        delivery_days=delivery_days,
        compliance_statements={
            "ISO9001": is_certified,
            "warranty_months": warranty_months
        },
        llm_generated_text=sales_pitch
    )
    
    ctx.logger.info(f"🚀 SENDING QUOTE TO BUYER: {msg.buyer_address}")
    ctx.logger.info(f"   Price: ${actual_price}/unit")
    ctx.logger.info(f"   Product: {rfq.product_id}")
    ctx.logger.info(f"   Delivery: {delivery_days} days")
    
    await ctx.send(msg.buyer_address, quote)
    
    ctx.logger.info(f"✅ Quote sent successfully to buyer!")


@agent.on_message(model=CounterOffer)
async def handle_counter_offer(ctx: Context, sender: str, msg: CounterOffer):
    """Handle buyer's counter-offer with LLM-based negotiation decision"""
    
    ctx.logger.info(f"💬 Received counter-offer from buyer: ${msg.proposed_price}/unit")
    ctx.logger.info(f"   Buyer's reasoning: {msg.reasoning}")
    
    if sender not in ACTIVE_NEGOTIATIONS:
        ctx.logger.warning("No active negotiation with this buyer. Ignoring.")
        return
    
    neg_state = ACTIVE_NEGOTIATIONS[sender]
    neg_state["round"] += 1
    
    # --- Fetch MeTTa constraints ---
    min_price = await seller_queries.get_min_acceptable_price(msg.product_id)
    max_discount = await seller_queries.get_max_discount_percent(msg.product_id)
    strategy = await seller_queries.get_strategy_instruction()
    system_prompt = await seller_queries.get_llm_system_prompt()
    original_price = neg_state["last_price"]
    
    ctx.logger.info(f"🔄 Negotiation Round {neg_state['round']}/3")
    ctx.logger.info(f"  Our last price: ${original_price}/unit")
    ctx.logger.info(f"  Our minimum: ${min_price}/unit")
    ctx.logger.info(f"  Their offer: ${msg.proposed_price}/unit")
    
    # ✅ CHECK: Is offer too low immediately?
    if msg.proposed_price < min_price * 0.95:  # More than 5% below minimum
        ctx.logger.warning(f"⚠️  Offer is far below our minimum (${min_price}/unit)")
        ctx.logger.info("Walking away from this negotiation.")
        
        rejection_prompt = f"""Generate a 1-2 sentence polite but firm rejection.

The buyer offered ${msg.proposed_price}/unit but your minimum is ${min_price}/unit.
This offer is too low to continue negotiation.

Thank them professionally and explain you cannot meet their price requirements."""

        rejection_text = await llm_router.generate(
            agent_role="seller",
            prompt=rejection_prompt,
            system_message=system_prompt
        )
        
        ctx.logger.info(f"Rejection message: {rejection_text}")
        del ACTIVE_NEGOTIATIONS[sender]
        return

    # --- LLM DECIDES: Accept, Counter, or Walk Away (JSON) ---
    negotiation_decision_prompt = f"""You are negotiating with a buyer. Decide your response.

**Situation:**
- Your original quoted price: ${neg_state['original_price']}/unit
- Your last price: ${original_price}/unit
- Your absolute minimum: ${min_price}/unit (you CANNOT go below this)
- Buyer's counter-offer: ${msg.proposed_price}/unit
- Buyer's reasoning: "{msg.reasoning}"
- Negotiation round: {neg_state['round']}/3
- Your strategy: {strategy}

**Negotiation Rules:**
- Round 1: NEVER accept immediately (be stubborn, counter-offer)
- Round 2-3: Consider accepting if offer is close to your minimum
- Round 3: Last chance - accept reasonable offers or walk away

**Options:**
1. ACCEPT their offer (if >= ${min_price} AND round >= 2)
2. COUNTER with a new price (between ${min_price} and ${original_price})
3. WALK_AWAY (if offer too low or round >= 3 with no progress)

Respond ONLY with valid JSON:
{{
  "decision": "accept" | "counter" | "walk_away",
  "counter_price": 70.0,
  "reasoning": "Brief explanation of your decision"
}}

If decision is "accept" or "walk_away", set counter_price to 0."""

    llm_negotiation_response = await llm_router.generate(
        agent_role="seller",
        prompt=negotiation_decision_prompt,
        system_message=system_prompt
    )

    # Parse LLM negotiation decision
    try:
        import re
        
        # Strip markdown code blocks
        cleaned_response = llm_negotiation_response.strip()
        if cleaned_response.startswith("```"):
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', cleaned_response, re.DOTALL)
            if json_match:
                cleaned_response = json_match.group(1)
            else:
                json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
                if json_match:
                    cleaned_response = json_match.group()
        
        negotiation_decision = json.loads(cleaned_response)
        decision = negotiation_decision["decision"]
        counter_price = negotiation_decision.get("counter_price", 0)
        reasoning = negotiation_decision["reasoning"]
        
        # ✅ ENFORCE STUBBORNNESS: Never accept on round 1
        if decision == "accept" and neg_state["round"] == 1:
            ctx.logger.info(f"⚠️  LLM wanted to accept on round 1, forcing counter-offer (be stubborn)")
            decision = "counter"
            # Counter at midpoint between their offer and our last price
            counter_price = round((msg.proposed_price + original_price) / 2, 2)
            counter_price = max(min_price, counter_price)
            reasoning = "We appreciate your offer but believe our product warrants a higher price. Let's find middle ground."
        
        ctx.logger.info(f"💡 LLM NEGOTIATION DECISION:")
        ctx.logger.info(f"  Decision: {decision.upper()}")
        ctx.logger.info(f"  Reasoning: {reasoning}")
        
    except Exception as e:
        ctx.logger.error(f"❌ Failed to parse LLM negotiation decision: {e}")
        ctx.logger.error(f"Raw response: {llm_negotiation_response[:200]}")
        # Fallback to rule-based logic
        if neg_state["round"] == 1:
            decision = "counter"
            counter_price = round((msg.proposed_price + original_price) / 2, 2)
        elif msg.proposed_price >= min_price:
            decision = "accept"
            counter_price = msg.proposed_price
        elif neg_state["round"] >= 3:
            decision = "walk_away"
            counter_price = 0
        else:
            decision = "counter"
            counter_price = max(min_price, round((min_price + msg.proposed_price) / 2, 2))
        reasoning = "Fallback decision due to LLM parsing error"

    # --- Execute Decision ---
    if decision == "accept":
        # ACCEPT
        ctx.logger.info(f"✅ ACCEPTING buyer's offer at ${msg.proposed_price}/unit")
        
        acceptance_prompt = f"""Generate a 1-2 sentence acceptance message.

You're accepting the buyer's counter-offer of ${msg.proposed_price}/unit after {neg_state['round']} rounds of negotiation.

Be professional, express enthusiasm about working together, and confirm next steps."""

        acceptance_text = await llm_router.generate(
            agent_role="seller",
            prompt=acceptance_prompt,
            system_message=system_prompt
        )
        
        delivery_days = await seller_queries.get_delivery_time(msg.product_id)
        warranty_months = await seller_queries.get_warranty(msg.product_id)
        
        quote = QuoteMessage(
            product_id=msg.product_id,
            price_per_unit=msg.proposed_price,
            delivery_days=delivery_days,
            compliance_statements={
                "accepted": True,
                "warranty_months": warranty_months
            },
            llm_generated_text=acceptance_text
        )
        
        await ctx.send(sender, quote)
        ctx.logger.info("✅ Acceptance sent to buyer. Deal closed!")
        del ACTIVE_NEGOTIATIONS[sender]
        
    elif decision == "walk_away":
        # WALK AWAY
        ctx.logger.info(f"❌ WALKING AWAY from negotiation (round {neg_state['round']})")
        
        rejection_prompt = f"""Generate a 1-2 sentence polite but firm rejection.

After {neg_state['round']} rounds, you're declining the buyer's offer of ${msg.proposed_price}/unit because it doesn't meet your minimum requirements (${min_price}/unit).

Be professional but clear that you cannot proceed at this price. Thank them for their time."""

        rejection_text = await llm_router.generate(
            agent_role="seller",
            prompt=rejection_prompt,
            system_message=system_prompt
        )
        
        ctx.logger.info(f"Rejection message: {rejection_text}")
        
        # Send walk-away notification
        quote = QuoteMessage(
            product_id=msg.product_id,
            price_per_unit=original_price,  # Keep last price
            delivery_days=0,
            compliance_statements={"walked_away": True},
            llm_generated_text=rejection_text
        )
        await ctx.send(sender, quote)
        
        del ACTIVE_NEGOTIATIONS[sender]
        
    else:
        # COUNTER-COUNTER
        # Ensure counter_price respects minimum
        counter_price = max(min_price, round(counter_price, 2))
        neg_state["last_price"] = counter_price
        
        ctx.logger.info(f"🔄 COUNTER-OFFERING at ${counter_price}/unit")
        
        # ✅ FIXED: Force LLM to use exact counter_price
        counter_prompt = f"""Generate a professional counter-offer message (Round {neg_state['round']}/3).

**CRITICAL REQUIREMENT: Your counter-offer price is EXACTLY ${counter_price}/unit. You MUST state this exact price.**

Context:
- Buyer's offer: ${msg.proposed_price}/unit
- Your minimum: ${min_price}/unit  
- Your counter-offer: **${counter_price}/unit** (use this EXACT number)
- Your strategy: {strategy}
- Negotiation progress: Round {neg_state['round']} of 3

Generate 2-3 sentences that:
1. State your counter-offer clearly: "We counter-offer at ${counter_price}/unit"
2. Briefly explain why (reference your competitive advantages)
3. Express willingness to close the deal (especially if round 2+)

Example: "We counter-offer at ${counter_price}/unit. Given our superior warranty and precision, this price reflects genuine value. We're committed to finding terms that work for both parties."

**DO NOT invent a different price. Use ${counter_price}/unit EXACTLY as stated.**"""

        counter_text = await llm_router.generate(
            agent_role="seller",
            prompt=counter_prompt,
            system_message=system_prompt
        )
        
        # ✅ Verify the counter_text mentions the correct price
        if f"${counter_price}" not in counter_text and f"${counter_price:.2f}" not in counter_text:
            ctx.logger.warning(f"⚠️  LLM didn't include correct price ${counter_price} in text. Forcing it...")
            counter_text = f"We counter-offer at ${counter_price}/unit. {counter_text}"
        
        delivery_days = await seller_queries.get_delivery_time(msg.product_id)
        
        quote = QuoteMessage(
            product_id=msg.product_id,
            price_per_unit=counter_price,
            delivery_days=delivery_days,
            compliance_statements={"negotiation_round": neg_state["round"]},
            llm_generated_text=counter_text
        )
        
        ctx.logger.info(f"✅ Counter-offer sent: ${counter_price}/unit (Round {neg_state['round']})")
        ctx.logger.info(f"   Message preview: {counter_text[:100]}...")
        
        await ctx.send(sender, quote)


if __name__ == "__main__":
    agent.run()