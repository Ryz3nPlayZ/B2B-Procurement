"""
Base Prompts

Shared prompt templates for the ASI system.
"""

from typing import Dict, Any, List


class BasePrompts:
    """Base prompt templates and utilities."""
    
    # System prompts
    CONCISE_PROTOCOL = """
    You are an AI agent in the ASI (Autonomous System Intelligence) network. 
    Follow these protocols:
    1. Be concise and professional
    2. Focus on facts and data
    3. Maintain context awareness
    4. Follow ASI communication standards
    """
    
    NEGOTIATION_PROTOCOL = """
    You are participating in a business negotiation. Follow these guidelines:
    1. Be professional and respectful
    2. Focus on mutual benefit
    3. Provide clear reasoning for positions
    4. Maintain negotiation history context
    """
    
    ANALYSIS_PROTOCOL = """
    You are analyzing business data and making recommendations. Guidelines:
    1. Base conclusions on data and facts
    2. Consider multiple perspectives
    3. Provide clear reasoning
    4. Suggest actionable next steps
    """
    
    @staticmethod
    def format_rfq_prompt(requirements: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """Format RFQ generation prompt."""
        context_str = ""
        if context:
            context_str = f"\nContext: {context}"
        
        return f"""
        Generate a professional Request for Quote (RFQ) based on these requirements:
        
        Requirements: {requirements}
        {context_str}
        
        Include:
        - Clear specifications
        - Delivery requirements
        - Quality standards
        - Timeline expectations
        - Evaluation criteria
        
        Format as a professional RFQ document.
        """
    
    @staticmethod
    def format_quote_prompt(rfq_data: Dict[str, Any], pricing_data: Dict[str, Any], 
                           inventory_data: Dict[str, Any] = None) -> str:
        """Format quote generation prompt."""
        inventory_str = ""
        if inventory_data:
            inventory_str = f"\nAvailable Inventory: {inventory_data}"
        
        return f"""
        Generate a competitive quote based on this RFQ:
        
        RFQ Details: {rfq_data}
        Pricing Information: {pricing_data}
        {inventory_str}
        
        Include:
        - Competitive pricing
        - Delivery timeline
        - Quality assurances
        - Terms and conditions
        - Value propositions
        
        Format as a professional quote document.
        """
    
    @staticmethod
    def format_negotiation_prompt(negotiation_data: Dict[str, Any], 
                                 strategy: Dict[str, Any] = None) -> str:
        """Format negotiation prompt."""
        strategy_str = ""
        if strategy:
            strategy_str = f"\nNegotiation Strategy: {strategy}"
        
        return f"""
        Generate a negotiation response based on this context:
        
        Negotiation Data: {negotiation_data}
        {strategy_str}
        
        Consider:
        - Current market conditions
        - Relationship value
        - Competitive positioning
        - Long-term benefits
        
        Provide a professional negotiation response.
        """
    
    @staticmethod
    def format_analysis_prompt(data: Dict[str, Any], analysis_type: str) -> str:
        """Format analysis prompt."""
        return f"""
        Analyze the following {analysis_type} data and provide insights:
        
        Data: {data}
        
        Provide:
        - Key findings
        - Trends and patterns
        - Risk assessment
        - Recommendations
        - Next steps
        
        Format as a professional analysis report.
        """
    
    @staticmethod
    def format_evaluation_prompt(offer_data: Dict[str, Any], 
                                criteria: Dict[str, Any] = None) -> str:
        """Format offer evaluation prompt."""
        criteria_str = ""
        if criteria:
            criteria_str = f"\nEvaluation Criteria: {criteria}"
        
        return f"""
        Evaluate this offer based on business requirements:
        
        Offer Details: {offer_data}
        {criteria_str}
        
        Evaluate:
        - Price competitiveness
        - Quality standards
        - Delivery capabilities
        - Supplier reliability
        - Risk factors
        
        Provide a detailed evaluation with recommendation.
        """
    
    @staticmethod
    def format_summary_prompt(content: str, summary_type: str = "general") -> str:
        """Format content summary prompt."""
        return f"""
        Provide a concise {summary_type} summary of the following content:
        
        Content: {content}
        
        Include:
        - Key points
        - Important details
        - Action items (if any)
        - Next steps (if any)
        
        Keep the summary clear and actionable.
        """
    
    @staticmethod
    def format_decision_prompt(options: List[Dict[str, Any]], 
                              criteria: Dict[str, Any] = None) -> str:
        """Format decision-making prompt."""
        criteria_str = ""
        if criteria:
            criteria_str = f"\nDecision Criteria: {criteria}"
        
        options_str = "\n".join([f"Option {i+1}: {opt}" for i, opt in enumerate(options)])
        
        return f"""
        Analyze these options and make a recommendation:
        
        Options:
        {options_str}
        {criteria_str}
        
        Consider:
        - Pros and cons of each option
        - Risk assessment
        - Cost-benefit analysis
        - Strategic alignment
        - Implementation feasibility
        
        Provide a clear recommendation with reasoning.
        """
    
    @staticmethod
    def format_error_handling_prompt(error_context: str, error_type: str) -> str:
        """Format error handling prompt."""
        return f"""
        Handle this {error_type} error professionally:
        
        Error Context: {error_context}
        
        Provide:
        - Clear error explanation
        - Possible causes
        - Suggested solutions
        - Prevention measures
        
        Maintain a helpful and professional tone.
        """
    
    @staticmethod
    def format_validation_prompt(data: Dict[str, Any], 
                               validation_rules: Dict[str, Any] = None) -> str:
        """Format data validation prompt."""
        rules_str = ""
        if validation_rules:
            rules_str = f"\nValidation Rules: {validation_rules}"
        
        return f"""
        Validate this data for completeness and accuracy:
        
        Data: {data}
        {rules_str}
        
        Check for:
        - Required fields
        - Data format consistency
        - Business rule compliance
        - Logical consistency
        - Completeness
        
        Provide validation results and recommendations.
        """
    
    @staticmethod
    def get_system_message(agent_type: str, context: Dict[str, Any] = None) -> str:
        """Get system message for agent type."""
        base_message = BasePrompts.CONCISE_PROTOCOL
        
        if agent_type == "buyer":
            return base_message + "\nYou are a procurement specialist focused on value and quality."
        elif agent_type == "seller":
            return base_message + "\nYou are a sales specialist focused on customer satisfaction and competitive positioning."
        elif agent_type == "coordinator":
            return base_message + "\nYou are a system coordinator focused on efficiency and reliability."
        else:
            return base_message
    
    @staticmethod
    def format_context_prompt(prompt: str, context: Dict[str, Any]) -> str:
        """Format prompt with additional context."""
        context_str = ""
        if context:
            context_items = []
            for key, value in context.items():
                context_items.append(f"{key}: {value}")
            context_str = f"\nAdditional Context:\n" + "\n".join(context_items)
        
        return f"{prompt}{context_str}"

