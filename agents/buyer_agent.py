# agents/buyer_agent.py

import logging
import asyncio
import json
from uagents import Agent, Context
from uagents.setup import fund_agent_if_low
from config import settings
from protocols.rfq_protocol import RFQMessage
from protocols.quote_protocol import QuoteMessage
from pydantic import BaseModel
from llm.llm_router import LLMRouter
from metta.metta_engine import MeTTaEngine
from metta.queries.buyer_queries import BuyerQueries
from memory.agent_memory import AgentMemory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agents.buyer")

# --- Message Models ---
class CounterOffer(BaseModel):
    """Buyer's counter-offer during negotiation"""
    product_id: str
    proposed_price: float
    reasoning: str

agent = Agent(
    name="BuyerAgent",
    port=8003,
    seed=settings.BUYER_AGENT_SEED,
    endpoint=["http://127.0.0.1:8003/submit"],
)

fund_agent_if_low(agent.wallet.address())
llm_router = LLMRouter()
metta_engine = MeTTaEngine()
buyer_queries = BuyerQueries(metta_engine)
buyer_memory = AgentMemory("buyer_agent")

# State tracking
RECEIVED_QUOTES = {}
NEGOTIATION_STATE = {}
QUOTE_COLLECTION_TIME = 30
MAX_NEGOTIATION_ROUNDS = 3

@agent.on_event("startup")
async def initial_startup_and_rfq(ctx: Context):
    """Startup: load KB, wait, send RFQ"""
    
    ctx.logger.info("Buyer Agent starting up...")
    await metta_engine.load_metta_file(settings.BUYER_POLICIES_FILE)
    ctx.logger.info("Buyer policies knowledge base loaded.")

    ctx.logger.info("Waiting 15 seconds for network to settle...")
    await asyncio.sleep(15)

    # --- Fetch procurement requirements from MeTTa ---
    product_id = "TS-100"
    quantity = await buyer_queries.get_required_quantity(product_id)
    max_budget = await buyer_queries.get_max_budget_per_unit(product_id)
    
    ctx.logger.info(f"Initiating RFQ for {quantity} units of {product_id} (budget: ${max_budget}/unit)")
    
    rfq = RFQMessage(
        product_id=product_id,
        quantity=quantity,
        required_specs={
            "certification": "ISO9001",
            "max_budget": max_budget
        }
    )
    
    coordinator_address = "agent1qwtcsxnr2957et869u38r3yafphfg2dlppl86t99ll0ye8nv2f672zrma08"
    await ctx.send(coordinator_address, rfq)
    ctx.logger.info(f"RFQ sent to coordinator.")
    
    # Wait for quotes with buffer
    ctx.logger.info(f"Collecting quotes for {QUOTE_COLLECTION_TIME} seconds...")
    await asyncio.sleep(QUOTE_COLLECTION_TIME)

    # Give stragglers extra time
    if len(RECEIVED_QUOTES) == 0:
        ctx.logger.warning("No quotes yet. Waiting 10 more seconds...")
        await asyncio.sleep(10)

    if len(RECEIVED_QUOTES) == 0:
        ctx.logger.error("No quotes received after 40 seconds. Procurement failed.")
        return

    ctx.logger.info(f"Received {len(RECEIVED_QUOTES)} quotes. Starting intelligent evaluation...")
    await evaluate_quotes_and_negotiate(ctx, product_id, max_budget)


@agent.on_message(model=QuoteMessage)
async def handle_quote(ctx: Context, sender: str, msg: QuoteMessage):
    """Handle incoming quotes from sellers (both initial and negotiation responses)"""
    
    ctx.logger.info(f"📬 Received quote from {sender[:20]}...: ${msg.price_per_unit}/unit, {msg.delivery_days} days")
    ctx.logger.info(f"Quote text: {msg.llm_generated_text[:100]}...")
    
    # Check if this is a negotiation response
    if sender in NEGOTIATION_STATE:
        neg = NEGOTIATION_STATE[sender]
        neg["quotes"].append(msg)
        
        ctx.logger.info(f"💬 Negotiation response from {sender[:20]}... (Round {neg['round']})")
        ctx.logger.info(f"   New price: ${msg.price_per_unit}/unit")
        
        # Check if accepted
        if msg.compliance_statements.get("accepted"):
            ctx.logger.info(f"   ✅ Seller ACCEPTED our terms at ${msg.price_per_unit}/unit!")
            neg["accepted"] = True
            neg["final_price"] = msg.price_per_unit
        else:
            ctx.logger.info(f"   🔄 Seller countered at ${msg.price_per_unit}/unit")
        
        return  # Don't store as new quote
    
    # Initial quote - store it
    RECEIVED_QUOTES[sender] = {
        "quote": msg,
        "numerical_score": calculate_numerical_score(msg)
    }
    ctx.logger.info(f"Quote stored with numerical score: {RECEIVED_QUOTES[sender]['numerical_score']:.3f}")


def calculate_numerical_score(quote: QuoteMessage) -> float:
    """Score quotes numerically: lower is better"""
    price_score = quote.price_per_unit / 100.0
    delivery_score = quote.delivery_days / 30.0
    warranty_score = 1.0 - (quote.compliance_statements.get("warranty_months", 12) / 36.0)
    
    return (0.5 * price_score) + (0.2 * delivery_score) + (0.15 * warranty_score)


async def evaluate_quote_quality_with_llm(ctx: Context, quote: QuoteMessage, seller_address: str) -> dict:
    """Use LLM to evaluate quote quality beyond just numbers"""
    
    system_prompt = await buyer_queries.get_llm_system_prompt()
    
    # Extract warranty and certifications
    warranty = quote.compliance_statements.get('warranty_months', 'Unknown')
    certifications = [k for k, v in quote.compliance_statements.items() 
                     if isinstance(v, bool) and v and k not in ['accepted']]
    
    prompt = f"""Evaluate this supplier's quote for quality, trustworthiness, and value.

**Supplier Quote (Sales Pitch):**
"{quote.llm_generated_text}"

**Hard Facts (From Supplier Data):**
- Price: ${quote.price_per_unit}/unit
- Delivery: {quote.delivery_days} days
- Warranty: {warranty} months
- Certifications: {', '.join(certifications) if certifications else 'None explicitly listed'}

**Full Compliance Data:**
{json.dumps(quote.compliance_statements, indent=2)}

**Evaluation Criteria:**
1. **Quality Score (0-10)**: Does the quote provide detailed specifications? Are claims backed by data? Specific technical details?
2. **Trust Score (0-10)**: Certifications present? Professional tone? Specific details vs vague claims?
3. **Value Score (0-10)**: Does price justify what's offered? Consider warranty length, delivery speed, and specs.

**Important Scoring Guidelines (BE STRICT):**

**Warranties:**
- 12 months = 6.0/10 quality (industry baseline)
- 18 months = 7.5/10 quality
- 24+ months = 9.0/10 quality (premium, excellent!)

**Delivery Speed:**
- 3-5 days = 9.0/10 value (excellent, fast)
- 6-8 days = 7.0/10 value (acceptable)
- 9+ days = 5.0/10 value (slow)

**Technical Specs:**
- Specific precision/range values mentioned (e.g. "±0.2°C") = 8.0-9.0/10 quality
- General descriptions only = 6.0/10 quality
- No specs mentioned = 4.0/10 quality

**CRITICAL: YOUR JOB IS TO DIFFERENTIATE QUOTES!**
- If one quote has 24mo warranty and another has 12mo, the 24mo one MUST score 9.0 quality vs 6.0 quality
- If one mentions specific precision and another doesn't, score accordingly (8.0+ vs 6.0)
- DO NOT give everyone the same scores!

**Red Flags to Watch For:**
- No specific product specifications mentioned
- Overly promotional language without substance
- Missing certification details
- Price seems too good without clear justification

**Response Format:**
Return ONLY a JSON object with these exact fields. Use numeric scores based on the guidelines above.

{{
  "quality_score": <number 0.0-10.0>,
  "trust_score": <number 0.0-10.0>,
  "value_score": <number 0.0-10.0>,
  "reasoning": "<your explanation>",
  "red_flags": ["<issue1>", "<issue2>"],
  "strengths": ["<strength1>", "<strength2>"]
}}

Output ONLY the JSON object. No markdown, no code blocks, no extra text."""

    response = await llm_router.generate(
        agent_role="buyer",
        prompt=prompt,
        system_message=system_prompt
    )
    
    try:
        import re
        
        # Strip markdown code blocks if present
        cleaned_response = response.strip()
        if cleaned_response.startswith("```"):
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', cleaned_response, re.DOTALL)
            if json_match:
                cleaned_response = json_match.group(1)
            else:
                json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
                if json_match:
                    cleaned_response = json_match.group()
        
        eval_data = json.loads(cleaned_response)
        
        # Validate required fields
        required_fields = ["quality_score", "trust_score", "value_score", "reasoning"]
        for field in required_fields:
            if field not in eval_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Ensure lists exist
        if "red_flags" not in eval_data:
            eval_data["red_flags"] = []
        if "strengths" not in eval_data:
            eval_data["strengths"] = []
        
        # Combined LLM score (0-1 scale, lower is better to match numerical scoring)
        avg_llm_score = (
            eval_data["quality_score"] +
            eval_data["trust_score"] +
            eval_data["value_score"]
        ) / 30.0
        
        # Invert so lower is better (consistent with numerical scoring)
        eval_data["combined_llm_score"] = 1.0 - avg_llm_score
        
        ctx.logger.info(f"✓ LLM Evaluation for {seller_address[:20]}:")
        ctx.logger.info(f"  Quality: {eval_data['quality_score']:.1f}/10")
        ctx.logger.info(f"  Trust: {eval_data['trust_score']:.1f}/10")
        ctx.logger.info(f"  Value: {eval_data['value_score']:.1f}/10")
        ctx.logger.info(f"  Reasoning: {eval_data['reasoning']}")
        if eval_data.get("red_flags"):
            ctx.logger.warning(f"  🚩 RED FLAGS: {', '.join(eval_data['red_flags'])}")
        if eval_data.get("strengths"):
            ctx.logger.info(f"  ✨ Strengths: {', '.join(eval_data['strengths'])}")
        
        return eval_data
        
    except Exception as e:
        ctx.logger.error(f"❌ Failed to parse LLM evaluation: {e}")
        ctx.logger.error(f"Raw LLM response: {response[:300]}")
        return {
            "quality_score": 5.0,
            "trust_score": 5.0,
            "value_score": 5.0,
            "combined_llm_score": 0.5,
            "reasoning": "Evaluation failed - using neutral scores",
            "red_flags": [],
            "strengths": []
        }


async def evaluate_quotes_and_negotiate(ctx: Context, product_id: str, max_budget: float):
    """Evaluate all quotes using BOTH numerical and LLM-based reasoning"""
    
    ctx.logger.info("=" * 70)
    ctx.logger.info("PHASE 1: LLM QUALITY ANALYSIS (Intelligent Evaluation)")
    ctx.logger.info("=" * 70)
    
    # LLM evaluates each quote
    for seller, data in RECEIVED_QUOTES.items():
        llm_eval = await evaluate_quote_quality_with_llm(ctx, data["quote"], seller)
        data["llm_evaluation"] = llm_eval
    
    ctx.logger.info("=" * 70)
    ctx.logger.info("PHASE 2: COMBINED SCORING (MeTTa Facts + LLM Reasoning)")
    ctx.logger.info("=" * 70)
    
    for seller, data in RECEIVED_QUOTES.items():
        numerical_score = data["numerical_score"]
        llm_score = data["llm_evaluation"]["combined_llm_score"]
        
        # 60% numerical (price/delivery/warranty), 40% LLM (quality/trust/value)
        final_score = (0.6 * numerical_score) + (0.4 * llm_score)
        data["final_score"] = final_score
        
        ctx.logger.info(f"Seller: {seller[:30]}...")
        ctx.logger.info(f"  Price: ${data['quote'].price_per_unit}/unit")
        ctx.logger.info(f"  Numerical Score: {numerical_score:.3f}")
        ctx.logger.info(f"  LLM Quality Score: {llm_score:.3f}")
        ctx.logger.info(f"  FINAL SCORE: {final_score:.3f} (lower = better)")
        ctx.logger.info(f"  LLM Says: {data['llm_evaluation']['reasoning']}")
    
    # Price vs Quality Tradeoff Analysis
    cheapest_seller = min(RECEIVED_QUOTES.keys(), 
                         key=lambda k: RECEIVED_QUOTES[k]["quote"].price_per_unit)
    cheapest_price = RECEIVED_QUOTES[cheapest_seller]["quote"].price_per_unit
    
    best_quality_seller = min(RECEIVED_QUOTES.keys(),
                             key=lambda k: RECEIVED_QUOTES[k]["llm_evaluation"]["combined_llm_score"])
    best_quality_score = RECEIVED_QUOTES[best_quality_seller]["llm_evaluation"]["combined_llm_score"]
    
    ctx.logger.info("=" * 70)
    ctx.logger.info("💰 PRICE vs QUALITY TRADEOFF ANALYSIS:")
    ctx.logger.info("=" * 70)
    ctx.logger.info(f"Cheapest option: {cheapest_seller[:30]}... at ${cheapest_price}/unit")
    ctx.logger.info(f"Highest quality: {best_quality_seller[:30]}... (LLM score: {best_quality_score:.3f})")
    
    if cheapest_seller != best_quality_seller:
        price_diff = RECEIVED_QUOTES[best_quality_seller]["quote"].price_per_unit - cheapest_price
        quality_diff = RECEIVED_QUOTES[cheapest_seller]["llm_evaluation"]["combined_llm_score"] - best_quality_score
        
        ctx.logger.info(f"💵 Premium for higher quality: ${price_diff:.2f}/unit")
        ctx.logger.info(f"📊 Quality improvement: {quality_diff:.3f} (lower score = better quality)")
    
    # Learning from past interactions
    ctx.logger.info("=" * 70)
    ctx.logger.info("📚 LEARNING FROM PAST INTERACTIONS")
    ctx.logger.info("=" * 70)

    for seller, data in RECEIVED_QUOTES.items():
        reputation = buyer_memory.get_seller_reputation(seller)
        data["reputation"] = reputation
        
        ctx.logger.info(f"Seller {seller[:30]}...")
        ctx.logger.info(f"  Historical Reputation: {reputation:.2f}/1.0")
        
        if reputation > 0:
            bonus = (reputation - 0.5) * 0.1
            original_score = data["final_score"]
            data["final_score"] = max(0, original_score + bonus)
            
            if bonus < 0:
                ctx.logger.warning(f"  ⚠️  Reputation penalty: +{abs(bonus):.3f} to score")
            elif bonus > 0:
                ctx.logger.info(f"  ✅ Reputation bonus: -{bonus:.3f} to score")

    # Check market trends
    market_insight = buyer_memory.get_market_insight(product_id)
    if market_insight["sample_size"] >= 3:
        ctx.logger.info(f"Market Intelligence ({market_insight['sample_size']} historical quotes):")
        ctx.logger.info(f"  Average market price: ${market_insight['avg_price']:.2f}/unit")
        ctx.logger.info(f"  Trend: {market_insight['price_trend']}")
    
    # Select best seller
    best_seller = min(RECEIVED_QUOTES.keys(), key=lambda k: RECEIVED_QUOTES[k]["final_score"])
    best_quote = RECEIVED_QUOTES[best_seller]["quote"]
    best_eval = RECEIVED_QUOTES[best_seller]["llm_evaluation"]
    best_final_score = RECEIVED_QUOTES[best_seller]["final_score"]
    
    ctx.logger.info("=" * 70)
    ctx.logger.info("🏆 WINNER SELECTED (Lowest Combined Score):")
    ctx.logger.info("=" * 70)
    ctx.logger.info(f"Seller: {best_seller[:40]}...")
    ctx.logger.info(f"Price: ${best_quote.price_per_unit}/unit")
    ctx.logger.info(f"Final Score: {best_final_score:.3f}")
    ctx.logger.info(f"LLM Reasoning: {best_eval['reasoning']}")
    ctx.logger.info("=" * 70)
    
    # ✅ FIXED NEGOTIATION LOGIC
    if best_quote.price_per_unit > max_budget:
        # Over budget - MUST negotiate
        ctx.logger.info(f"❌ Price ${best_quote.price_per_unit}/unit EXCEEDS budget ${max_budget}/unit")
        ctx.logger.info("MUST NEGOTIATE - Initiating multi-round negotiation...")
        
        # Negotiate with all sellers (give everyone a chance)
        sorted_sellers = sorted(RECEIVED_QUOTES.keys(), key=lambda k: RECEIVED_QUOTES[k]["final_score"])
        for seller in sorted_sellers:
            await start_negotiation(ctx, seller, product_id, max_budget, round_num=1)
        
        # Wait for responses and continue negotiation
        await asyncio.sleep(8)
        await continue_negotiation(ctx, product_id, max_budget)
        
        await asyncio.sleep(15)
        await finalize_negotiation(ctx, product_id, max_budget)
        
    else:
        # Within budget - accept best quote immediately
        ctx.logger.info(f"✅ Price ${best_quote.price_per_unit}/unit is within budget ${max_budget}/unit")
        ctx.logger.info(f"Quality score: {best_final_score:.3f}")
        ctx.logger.info("Accepting immediately without negotiation!")
        await finalize_deal(ctx, best_seller, best_quote)


async def start_negotiation(ctx: Context, seller_address: str, product_id: str, max_budget: float, round_num: int):
    """Send counter-offer to seller"""
    
    current_price = RECEIVED_QUOTES[seller_address]["quote"].price_per_unit
    
    # Initialize negotiation state
    if seller_address not in NEGOTIATION_STATE:
        NEGOTIATION_STATE[seller_address] = {
            "product_id": product_id,
            "round": 0,
            "quotes": [RECEIVED_QUOTES[seller_address]["quote"]],
            "accepted": False,
            "walked_away": False
        }
    
    neg = NEGOTIATION_STATE[seller_address]
    neg["round"] = round_num
    
    # ✅ FIXED: Calculate aggressive but realistic counter-offer
    # Target: 10-15% below current price, but respect budget
    if current_price > max_budget:
        # Over budget: start at budget limit
        proposed_price = max_budget
    else:
        # Within budget but want discount: offer 90% of current price
        proposed_price = round(current_price * 0.90, 2)
    
    # Don't go below 80% of original quote (unrealistic)
    min_reasonable = round(current_price * 0.80, 2)
    proposed_price = max(proposed_price, min_reasonable)
    
    system_prompt = await buyer_queries.get_llm_system_prompt()
    
    prompt = f"""Generate a professional counter-offer for negotiation (Round {round_num}).

Situation:
- Seller's quote: ${current_price}/unit
- Your budget: ${max_budget}/unit
- Your counter-offer: ${proposed_price}/unit
- Discount requested: ${current_price - proposed_price:.2f}/unit ({((current_price - proposed_price) / current_price * 100):.1f}%)

Generate a 2-3 sentence counter-offer that:
1. Acknowledges their quote professionally
2. Explains why you're proposing ${proposed_price}/unit (budget constraints, competitive quotes, volume commitment)
3. Expresses strong interest in closing the deal

Be firm but respectful. Show you're serious about buying if the price works."""

    reasoning = await llm_router.generate(
        agent_role="buyer",
        prompt=prompt,
        system_message=system_prompt
    )
    
    ctx.logger.info(f"💬 Round {round_num}: Sending counter-offer to {seller_address[:20]}...")
    ctx.logger.info(f"   Their price: ${current_price}/unit")
    ctx.logger.info(f"   Our offer: ${proposed_price}/unit (${current_price - proposed_price:.2f} discount)")
    
    counter = CounterOffer(
        product_id=product_id,
        proposed_price=proposed_price,
        reasoning=reasoning
    )
    
    await ctx.send(seller_address, counter)


async def continue_negotiation(ctx: Context, product_id: str, max_budget: float):
    """Continue multi-round negotiation based on seller responses"""
    
    ctx.logger.info("=" * 70)
    ctx.logger.info("📊 CHECKING NEGOTIATION PROGRESS...")
    ctx.logger.info("=" * 70)
    
    for seller, neg in NEGOTIATION_STATE.items():
        if neg.get("accepted") or neg.get("walked_away"):
            continue
        
        if neg["round"] >= MAX_NEGOTIATION_ROUNDS:
            ctx.logger.info(f"⏱️  {seller[:20]}: Max rounds reached, finalizing...")
            continue
        
        # Get latest quote
        if len(neg["quotes"]) > 1:
            latest_quote = neg["quotes"][-1]
            latest_price = latest_quote.price_per_unit
            
            ctx.logger.info(f"🔄 {seller[:20]}: Latest price ${latest_price}/unit")
            
            # If still over budget, counter again
            if latest_price > max_budget:
                gap = latest_price - max_budget
                ctx.logger.info(f"   Still ${gap:.2f} over budget. Sending round {neg['round'] + 1}...")
                await start_negotiation(ctx, seller, product_id, max_budget, neg["round"] + 1)
            elif latest_price > max_budget * 0.95:
                # Within budget but try one more time for better deal
                ctx.logger.info(f"   Close to budget. Attempting final negotiation...")
                await start_negotiation(ctx, seller, product_id, max_budget, neg["round"] + 1)


async def finalize_negotiation(ctx: Context, product_id: str, max_budget: float):
    """Check negotiation results and select winner"""
    
    ctx.logger.info("=" * 70)
    ctx.logger.info("🏁 FINAL NEGOTIATION RESULTS:")
    ctx.logger.info("=" * 70)
    
    accepted_deals = []
    for seller, neg in NEGOTIATION_STATE.items():
        if neg.get("walked_away"):
            ctx.logger.info(f"❌ {seller[:20]}: WALKED AWAY from negotiation")
            continue
            
        if neg.get("accepted"):
            ctx.logger.info(f"✅ {seller[:20]}: ACCEPTED at ${neg['final_price']}/unit")
            accepted_deals.append((seller, neg["final_price"], neg["quotes"][-1]))
        else:
            latest_price = neg["quotes"][-1].price_per_unit if neg["quotes"] else 999
            ctx.logger.info(f"⏳ {seller[:20]}: Last offer ${latest_price}/unit (Round {neg['round']})")
            
            # Check if last offer is acceptable
            if latest_price <= max_budget:
                ctx.logger.info(f"   → Price is acceptable within budget")
                accepted_deals.append((seller, latest_price, neg["quotes"][-1]))
            else:
                ctx.logger.warning(f"   → Still over budget by ${latest_price - max_budget:.2f}/unit")
    
    if accepted_deals:
        # Pick cheapest accepted deal
        best_deal = min(accepted_deals, key=lambda x: x[1])
        winner_seller, winner_price, winner_quote = best_deal
        
        ctx.logger.info("=" * 70)
        ctx.logger.info(f"🏆 BEST NEGOTIATED DEAL: ${winner_price}/unit from {winner_seller[:20]}...")
        ctx.logger.info("=" * 70)
        
        await finalize_deal(ctx, winner_seller, winner_quote)
    else:
        # No acceptable deals - procurement failed
        ctx.logger.error("=" * 70)
        ctx.logger.error("❌ NEGOTIATION FAILED - NO ACCEPTABLE OFFERS")
        ctx.logger.error("=" * 70)
        ctx.logger.error("All sellers either:")
        ctx.logger.error("  - Walked away from negotiation")
        ctx.logger.error("  - Remained above budget threshold")
        ctx.logger.error("Procurement cannot proceed. Consider:")
        ctx.logger.error("  1. Increasing budget")
        ctx.logger.error("  2. Reducing quantity requirements")
        ctx.logger.error("  3. Relaxing specifications")


async def finalize_deal(ctx: Context, winner_address: str, winner_quote: QuoteMessage):
    """Finalize the deal with selected seller"""
    
    ctx.logger.info("=" * 70)
    ctx.logger.info("✅ DEAL FINALIZED!")
    ctx.logger.info("=" * 70)
    ctx.logger.info(f"Supplier: {winner_address}")
    ctx.logger.info(f"Product: {winner_quote.product_id}")
    ctx.logger.info(f"Price: ${winner_quote.price_per_unit}/unit")
    ctx.logger.info(f"Delivery: {winner_quote.delivery_days} days")
    ctx.logger.info(f"Warranty: {winner_quote.compliance_statements.get('warranty_months', 'N/A')} months")
    
    # Update memory
    final_score_for_memory = RECEIVED_QUOTES[winner_address]["final_score"] if winner_address in RECEIVED_QUOTES else 0.5
    
    buyer_memory.learn_seller_behavior(winner_address, {
        "accepted": True,
        "quality_score": final_score_for_memory,
        "negotiated": (winner_address in NEGOTIATION_STATE and NEGOTIATION_STATE[winner_address]["round"] > 1)
    })

    buyer_memory.learn_market_trend(
        winner_quote.product_id,
        winner_quote.price_per_unit,
        winner_quote.delivery_days
    )

    ctx.logger.info("✅ Memory updated - agent learned from this interaction!")

    # Generate PO
    system_prompt = await buyer_queries.get_llm_system_prompt()
    
    prompt = f"""Generate a formal purchase order confirmation.

Deal Details:
- Supplier: {winner_address[:40]}
- Product: {winner_quote.product_id}
- Price: ${winner_quote.price_per_unit}/unit
- Delivery: {winner_quote.delivery_days} days
- Certifications: ISO9001 verified

Write a professional 2-3 sentence PO confirmation."""

    po_text = await llm_router.generate(
        agent_role="buyer",
        prompt=prompt,
        system_message=system_prompt
    )
    
    ctx.logger.info("=" * 70)
    ctx.logger.info("📄 PURCHASE ORDER:")
    ctx.logger.info(po_text)
    ctx.logger.info("=" * 70)
    ctx.logger.info("✅ Procurement complete!")


if __name__ == "__main__":
    agent.run()