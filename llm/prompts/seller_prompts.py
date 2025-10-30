"""
Seller Prompts

Seller-specific prompt templates for the ASI system.
"""

from typing import Dict, Any, List
from .base_prompts import BasePrompts


class SellerPrompts:
    """Seller-specific prompt templates."""
    
    # Seller system prompts
    SELLER_SYSTEM_PROMPT = """
    You are a sales specialist in the ASI system. Your role is to:
    1. Create competitive and compelling quotes
    2. Understand customer needs and requirements
    3. Negotiate win-win solutions
    4. Build and maintain customer relationships
    5. Maximize value for both parties
    
    Always focus on customer satisfaction, competitive positioning, and long-term relationships.
    """
    
    # Quote generation prompts
    @staticmethod
    def create_quote_prompt(rfq_data: Dict[str, Any], 
                           pricing_data: Dict[str, Any],
                           inventory_data: Dict[str, Any] = None) -> str:
        """Create quote generation prompt for seller."""
        inventory_str = ""
        if inventory_data:
            inventory_str = f"\nAvailable Inventory: {inventory_data}"
        
        return f"""
        Create a competitive quote based on this RFQ:
        
        RFQ Details: {rfq_data}
        Pricing Information: {pricing_data}
        {inventory_str}
        
        Ensure the quote includes:
        - Competitive pricing with value proposition
        - Technical specifications and capabilities
        - Quality assurances and certifications
        - Delivery timeline and logistics
        - Terms and conditions
        - Value-added services or benefits
        - Risk mitigation and guarantees
        
        Format as a professional sales proposal.
        """
    
    @staticmethod
    def competitive_analysis_prompt(competitor_data: Dict[str, Any],
                                  market_position: Dict[str, Any] = None) -> str:
        """Create competitive analysis prompt for seller."""
        position_str = ""
        if market_position:
            position_str = f"\nOur Market Position: {market_position}"
        
        return f"""
        Analyze competitive landscape and positioning:
        
        Competitor Data: {competitor_data}
        {position_str}
        
        Analyze:
        - Competitor strengths and weaknesses
        - Pricing strategies and positioning
        - Market share and trends
        - Customer preferences and needs
        - Differentiation opportunities
        - Competitive threats and opportunities
        
        Provide:
        - Competitive positioning analysis
        - Strengths to leverage
        - Weaknesses to address
        - Differentiation strategies
        - Pricing recommendations
        - Market opportunity assessment
        """
    
    @staticmethod
    def customer_needs_analysis_prompt(customer_data: Dict[str, Any],
                                     interaction_history: List[Dict[str, Any]] = None) -> str:
        """Create customer needs analysis prompt for seller."""
        history_str = ""
        if interaction_history:
            history_str = f"\nInteraction History: {interaction_history}"
        
        return f"""
        Analyze customer needs and requirements:
        
        Customer Data: {customer_data}
        {history_str}
        
        Identify:
        - Primary needs and pain points
        - Secondary requirements and preferences
        - Budget constraints and priorities
        - Decision-making criteria
        - Timeline and urgency
        - Stakeholder influences
        - Success metrics and expectations
        
        Provide:
        - Customer needs summary
        - Pain points and challenges
        - Solution requirements
        - Value proposition opportunities
        - Engagement strategy recommendations
        """
    
    # Negotiation prompts
    @staticmethod
    def negotiation_strategy_prompt(negotiation_context: Dict[str, Any],
                                  customer_profile: Dict[str, Any] = None) -> str:
        """Create negotiation strategy prompt for seller."""
        profile_str = ""
        if customer_profile:
            profile_str = f"\nCustomer Profile: {customer_profile}"
        
        return f"""
        Develop a negotiation strategy based on this context:
        
        Negotiation Context: {negotiation_context}
        {profile_str}
        
        Consider:
        - Customer's position and constraints
        - Your pricing flexibility and margins
        - Value proposition and differentiation
        - Relationship importance and history
        - Market conditions and competition
        - Long-term partnership potential
        
        Provide:
        - Negotiation objectives and priorities
        - Opening position and concessions
        - Value-based selling points
        - Alternative solutions and options
        - Win-win scenarios
        - Timeline and next steps
        """
    
    @staticmethod
    def objection_handling_prompt(objection: str, context: Dict[str, Any]) -> str:
        """Create objection handling prompt for seller."""
        return f"""
        Handle this customer objection professionally:
        
        Objection: {objection}
        Context: {context}
        
        Address:
        - Root cause of the objection
        - Customer concerns and fears
        - Value proposition reinforcement
        - Alternative solutions or approaches
        - Risk mitigation and guarantees
        - Social proof and testimonials
        
        Provide:
        - Acknowledgment and empathy
        - Clarifying questions
        - Value-based response
        - Alternative options
        - Next steps and follow-up
        """
    
    # Relationship management prompts
    @staticmethod
    def relationship_building_prompt(customer_data: Dict[str, Any],
                                 relationship_history: Dict[str, Any] = None) -> str:
        """Create relationship building prompt for seller."""
        history_str = ""
        if relationship_history:
            history_str = f"\nRelationship History: {relationship_history}"
        
        return f"""
        Develop a relationship building strategy:
        
        Customer Data: {customer_data}
        {history_str}
        
        Focus on:
        - Understanding customer's business and goals
        - Identifying mutual value opportunities
        - Building trust and credibility
        - Providing ongoing value and support
        - Anticipating future needs
        - Creating long-term partnerships
        
        Provide:
        - Relationship building objectives
        - Engagement strategies and activities
        - Value delivery opportunities
        - Communication and touchpoint plan
        - Success metrics and milestones
        """
    
    @staticmethod
    def upselling_cross_selling_prompt(customer_profile: Dict[str, Any],
                                     current_products: List[Dict[str, Any]],
                                     available_products: List[Dict[str, Any]]) -> str:
        """Create upselling/cross-selling prompt for seller."""
        current_str = "\n".join([f"- {prod}" for prod in current_products])
        available_str = "\n".join([f"- {prod}" for prod in available_products])
        
        return f"""
        Identify upselling and cross-selling opportunities:
        
        Customer Profile: {customer_profile}
        
        Current Products/Services:
        {current_str}
        
        Available Products:
        {available_str}
        
        Identify:
        - Complementary products or services
        - Upgrade opportunities
        - Additional value propositions
        - Customer needs and pain points
        - Budget and decision-making factors
        
        Provide:
        - Recommended upsell/cross-sell opportunities
        - Value propositions and benefits
        - Pricing and positioning strategies
        - Approach and messaging
        - Timeline and next steps
        """
    
    # Performance and optimization prompts
    @staticmethod
    def sales_performance_analysis_prompt(performance_data: Dict[str, Any],
                                        analysis_period: str = "quarterly") -> str:
        """Create sales performance analysis prompt for seller."""
        return f"""
        Analyze sales performance for the {analysis_period} period:
        
        Performance Data: {performance_data}
        
        Analyze:
        - Revenue and sales metrics
        - Customer acquisition and retention
        - Product/service performance
        - Market penetration and growth
        - Competitive positioning
        - Process efficiency and effectiveness
        
        Provide:
        - Performance summary and key metrics
        - Success factors and achievements
        - Challenges and improvement areas
        - Market trends and opportunities
        - Recommendations for optimization
        - Next period goals and strategies
        """
    
    @staticmethod
    def pricing_strategy_prompt(market_data: Dict[str, Any],
                              cost_data: Dict[str, Any],
                              competitive_data: Dict[str, Any] = None) -> str:
        """Create pricing strategy prompt for seller."""
        competitive_str = ""
        if competitive_data:
            competitive_str = f"\nCompetitive Data: {competitive_data}"
        
        return f"""
        Develop a pricing strategy based on market analysis:
        
        Market Data: {market_data}
        Cost Data: {cost_data}
        {competitive_str}
        
        Consider:
        - Cost structure and margins
        - Market positioning and value
        - Competitive landscape and pricing
        - Customer price sensitivity
        - Value proposition and differentiation
        - Pricing models and strategies
        
        Provide:
        - Recommended pricing strategy
        - Price points and positioning
        - Value-based pricing opportunities
        - Competitive response strategies
        - Implementation plan and timeline
        """
    
    # Communication and presentation prompts
    @staticmethod
    def sales_presentation_prompt(presentation_type: str,
                                audience_data: Dict[str, Any],
                                content_requirements: Dict[str, Any]) -> str:
        """Create sales presentation prompt for seller."""
        return f"""
        Create a {presentation_type} sales presentation:
        
        Audience: {audience_data}
        Content Requirements: {content_requirements}
        
        Ensure the presentation:
        - Addresses audience needs and interests
        - Highlights key value propositions
        - Uses compelling visuals and examples
        - Includes clear call-to-action
        - Maintains professional tone
        - Follows presentation best practices
        
        Structure for maximum impact and engagement.
        """
    
    @staticmethod
    def get_seller_system_message(context: Dict[str, Any] = None) -> str:
        """Get seller system message with context."""
        base_message = SellerPrompts.SELLER_SYSTEM_PROMPT
        
        if context:
            context_items = []
            for key, value in context.items():
                context_items.append(f"{key}: {value}")
            context_str = "\nAdditional Context:\n" + "\n".join(context_items)
            return base_message + context_str
        
        return base_message

