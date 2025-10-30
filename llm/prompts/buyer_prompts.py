"""
Buyer Prompts

Buyer-specific prompt templates for the ASI system.
"""

from typing import Dict, Any, List
from .base_prompts import BasePrompts


class BuyerPrompts:
    """Buyer-specific prompt templates."""
    
    # Buyer system prompts
    BUYER_SYSTEM_PROMPT = """
    You are a procurement specialist in the ASI system. Your role is to:
    1. Create clear and detailed RFQs
    2. Evaluate quotes objectively
    3. Negotiate for best value
    4. Ensure compliance with procurement policies
    5. Maintain supplier relationships
    
    Always prioritize value, quality, and compliance in your decisions.
    """
    
    # RFQ generation prompts
    @staticmethod
    def create_rfq_prompt(requirements: Dict[str, Any], policies: Dict[str, Any] = None) -> str:
        """Create RFQ generation prompt for buyer."""
        policies_str = ""
        if policies:
            policies_str = f"\nProcurement Policies: {policies}"
        
        return f"""
        Create a comprehensive Request for Quote (RFQ) based on these requirements:
        
        Requirements: {requirements}
        {policies_str}
        
        Ensure the RFQ includes:
        - Detailed technical specifications
        - Quality requirements and standards
        - Delivery timeline and location
        - Evaluation criteria and weights
        - Terms and conditions
        - Compliance requirements
        - Budget constraints (if applicable)
        
        Format as a professional procurement document.
        """
    
    @staticmethod
    def evaluate_quote_prompt(quote_data: Dict[str, Any], 
                             rfq_requirements: Dict[str, Any],
                             evaluation_criteria: Dict[str, Any] = None) -> str:
        """Create quote evaluation prompt for buyer."""
        criteria_str = ""
        if evaluation_criteria:
            criteria_str = f"\nEvaluation Criteria: {evaluation_criteria}"
        
        return f"""
        Evaluate this quote against the original RFQ requirements:
        
        Quote Details: {quote_data}
        Original RFQ Requirements: {rfq_requirements}
        {criteria_str}
        
        Evaluate based on:
        - Price competitiveness and value
        - Technical compliance with specifications
        - Quality standards and certifications
        - Delivery timeline and reliability
        - Supplier reputation and track record
        - Terms and conditions alignment
        - Risk assessment
        
        Provide:
        - Overall score (0-100)
        - Detailed evaluation by criteria
        - Strengths and weaknesses
        - Recommendation (accept/negotiate/reject)
        - Reasoning for recommendation
        """
    
    @staticmethod
    def negotiation_strategy_prompt(negotiation_context: Dict[str, Any],
                                  market_data: Dict[str, Any] = None) -> str:
        """Create negotiation strategy prompt for buyer."""
        market_str = ""
        if market_data:
            market_str = f"\nMarket Data: {market_data}"
        
        return f"""
        Develop a negotiation strategy based on this context:
        
        Negotiation Context: {negotiation_context}
        {market_str}
        
        Consider:
        - Current market conditions and pricing
        - Supplier's position and constraints
        - Your budget and timeline constraints
        - Alternative suppliers and options
        - Long-term relationship value
        - Risk mitigation strategies
        
        Provide:
        - Negotiation objectives and priorities
        - Opening position and fallback options
        - Key negotiation points
        - Concession strategy
        - Walk-away criteria
        - Timeline and milestones
        """
    
    @staticmethod
    def supplier_assessment_prompt(supplier_data: Dict[str, Any],
                                  assessment_criteria: Dict[str, Any] = None) -> str:
        """Create supplier assessment prompt for buyer."""
        criteria_str = ""
        if assessment_criteria:
            criteria_str = f"\nAssessment Criteria: {assessment_criteria}"
        
        return f"""
        Assess this supplier's capabilities and suitability:
        
        Supplier Data: {supplier_data}
        {criteria_str}
        
        Evaluate:
        - Financial stability and creditworthiness
        - Technical capabilities and expertise
        - Quality management systems
        - Delivery performance and reliability
        - Customer service and support
        - Compliance and certifications
        - Risk factors and mitigation
        - Competitive advantages
        
        Provide:
        - Overall supplier rating
        - Detailed assessment by category
        - Strengths and areas for improvement
        - Risk assessment and mitigation
        - Recommendation for engagement
        """
    
    # Decision-making prompts
    @staticmethod
    def procurement_decision_prompt(options: List[Dict[str, Any]],
                                  decision_criteria: Dict[str, Any] = None) -> str:
        """Create procurement decision prompt for buyer."""
        criteria_str = ""
        if decision_criteria:
            criteria_str = f"\nDecision Criteria: {decision_criteria}"
        
        options_str = "\n".join([f"Option {i+1}: {opt}" for i, opt in enumerate(options)])
        
        return f"""
        Make a procurement decision based on these options:
        
        Available Options:
        {options_str}
        {criteria_str}
        
        Consider:
        - Total cost of ownership (TCO)
        - Quality and performance requirements
        - Delivery timeline and reliability
        - Supplier relationship and support
        - Risk factors and mitigation
        - Compliance and regulatory requirements
        - Strategic alignment with business goals
        
        Provide:
        - Recommended option with reasoning
        - Alternative options and trade-offs
        - Risk assessment and mitigation
        - Implementation plan
        - Success metrics and monitoring
        """
    
    @staticmethod
    def contract_negotiation_prompt(contract_terms: Dict[str, Any],
                                  negotiation_points: List[str] = None) -> str:
        """Create contract negotiation prompt for buyer."""
        points_str = ""
        if negotiation_points:
            points_str = f"\nKey Negotiation Points: {negotiation_points}"
        
        return f"""
        Negotiate contract terms based on these requirements:
        
        Contract Terms: {contract_terms}
        {points_str}
        
        Focus on:
        - Pricing and payment terms
        - Delivery and performance standards
        - Quality assurance and warranties
        - Risk allocation and liability
        - Intellectual property rights
        - Termination and exit clauses
        - Dispute resolution mechanisms
        
        Provide:
        - Negotiation strategy and approach
        - Key terms to negotiate
        - Acceptable compromises
        - Deal-breakers and red lines
        - Timeline and milestones
        """
    
    # Analysis and reporting prompts
    @staticmethod
    def market_analysis_prompt(market_data: Dict[str, Any],
                              analysis_scope: str = "general") -> str:
        """Create market analysis prompt for buyer."""
        return f"""
        Analyze the market data for procurement insights:
        
        Market Data: {market_data}
        Analysis Scope: {analysis_scope}
        
        Provide:
        - Market trends and dynamics
        - Pricing analysis and benchmarks
        - Supplier landscape and competition
        - Risk factors and opportunities
        - Recommendations for procurement strategy
        - Cost optimization opportunities
        - Supplier diversification recommendations
        """
    
    @staticmethod
    def performance_review_prompt(performance_data: Dict[str, Any],
                                review_period: str = "quarterly") -> str:
        """Create performance review prompt for buyer."""
        return f"""
        Review procurement performance for the {review_period} period:
        
        Performance Data: {performance_data}
        
        Analyze:
        - Cost savings and value delivered
        - Supplier performance metrics
        - Process efficiency improvements
        - Compliance and risk management
        - Strategic goal achievement
        - Areas for improvement
        
        Provide:
        - Performance summary and key metrics
        - Success stories and achievements
        - Challenges and lessons learned
        - Recommendations for improvement
        - Next period objectives and priorities
        """
    
    # Communication prompts
    @staticmethod
    def stakeholder_communication_prompt(communication_type: str,
                                       stakeholder_data: Dict[str, Any],
                                       message_content: str) -> str:
        """Create stakeholder communication prompt for buyer."""
        return f"""
        Prepare a {communication_type} communication for stakeholders:
        
        Stakeholder Information: {stakeholder_data}
        Message Content: {message_content}
        
        Ensure the communication:
        - Is clear and professional
        - Addresses stakeholder concerns
        - Provides relevant context
        - Includes actionable information
        - Maintains appropriate tone
        - Follows organizational guidelines
        
        Format for the target audience and communication channel.
        """
    
    @staticmethod
    def get_buyer_system_message(context: Dict[str, Any] = None) -> str:
        """Get buyer system message with context."""
        base_message = BuyerPrompts.BUYER_SYSTEM_PROMPT
        
        if context:
            context_items = []
            for key, value in context.items():
                context_items.append(f"{key}: {value}")
            context_str = "\nAdditional Context:\n" + "\n".join(context_items)
            return base_message + context_str
        
        return base_message

