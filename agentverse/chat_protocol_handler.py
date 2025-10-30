# agentverse/chat_protocol_handler.py
from uagents import Context, Model
from protocols.chat_protocol import ChatMessage

class ChatProtocolHandler:
    """Handle chat messages from ASI:One interface"""
    
    @staticmethod
    async def handle_buyer_chat(ctx: Context, sender: str, msg: ChatMessage):
        """Handle chat commands for buyer agent"""
        text = msg.text.lower()
        
        if text.startswith("/rfq"):
            # Parse: /rfq TS-100 50 75
            parts = text.split()
            if len(parts) == 4:
                product_id = parts[1]
                quantity = int(parts[2])
                budget = float(parts[3])
                
                response = f"Starting RFQ for {quantity} units of {product_id} with budget ${budget}/unit..."
                # Trigger actual RFQ
                # ... (integrate with existing buyer_agent logic)
            else:
                response = "Usage: /rfq <product_id> <quantity> <budget>"
        
        elif text == "/status":
            response = "Buyer Agent Status: Active\nLast RFQ: TS-100 (50 units)\nOutcome: Deal finalized at $68.50/unit"
        
        elif text == "/history":
            # Show negotiation history
            response = "Recent Negotiations:\n1. TS-100: $68.50/unit (Seller B)\n2. PR-200: $45.00/unit (Seller A)"
        
        else:
            response = "Available commands:\n/rfq <product> <qty> <budget>\n/status\n/history"
        
        await ctx.send(sender, ChatMessage(text=response))
