"""
Base Agent Implementation

Shared functionality for all ASI agents including:
- MeTTa query execution
- LLM router integration
- Deal file management
- Common agent lifecycle methods
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..metta.metta_engine import MeTTaEngine
from ..llm.llm_router import LLMRouter
from ..core.deal_file import DealFile
from ..core.message_validator import MessageValidator


class BaseAgent(ABC):
    """Base class for all ASI agents with shared functionality."""
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        self.agent_id = agent_id
        self.config = config
        self.logger = logging.getLogger(f"agent.{agent_id}")
        
        # Initialize core components
        self.metta_engine = MeTTaEngine(config.get('metta', {}))
        self.llm_router = LLMRouter(config.get('llm', {}))
        self.message_validator = MessageValidator()
        
        # Agent state
        self.is_active = False
        self.current_deal_id = None
        self.deal_file = None
        
        self.logger.info(f"Initialized {self.__class__.__name__} with ID: {agent_id}")
    
    @abstractmethod
    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming message and return response."""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities and metadata."""
        pass
    
    def start_deal(self, deal_id: str, deal_data: Dict[str, Any]) -> bool:
        """Start a new deal negotiation."""
        try:
            self.deal_file = DealFile(deal_id, deal_data)
            self.current_deal_id = deal_id
            self.is_active = True
            
            # Log deal start in MeTTa knowledge base
            self.metta_engine.log_deal_start(deal_id, self.agent_id, deal_data)
            
            self.logger.info(f"Started deal {deal_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start deal {deal_id}: {e}")
            return False
    
    def end_deal(self, deal_id: str, final_state: Dict[str, Any]) -> bool:
        """End current deal and save final state."""
        try:
            if self.deal_file:
                self.deal_file.save_final_state(final_state)
                self.deal_file = None
            
            self.current_deal_id = None
            self.is_active = False
            
            # Log deal end in MeTTa knowledge base
            self.metta_engine.log_deal_end(deal_id, self.agent_id, final_state)
            
            self.logger.info(f"Ended deal {deal_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to end deal {deal_id}: {e}")
            return False
    
    def execute_metta_query(self, query: str, context: Dict[str, Any] = None) -> Any:
        """Execute MeTTa query with optional context."""
        try:
            return self.metta_engine.execute_query(query, context or {})
        except Exception as e:
            self.logger.error(f"MeTTa query failed: {e}")
            return None
    
    def get_llm_response(self, prompt: str, model_preference: str = None) -> str:
        """Get LLM response using the router."""
        try:
            return self.llm_router.get_response(prompt, model_preference)
        except Exception as e:
            self.logger.error(f"LLM request failed: {e}")
            return ""
    
    def validate_message(self, message: Dict[str, Any]) -> bool:
        """Validate incoming message format."""
        return self.message_validator.validate(message)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            "agent_id": self.agent_id,
            "is_active": self.is_active,
            "current_deal_id": self.current_deal_id,
            "timestamp": datetime.utcnow().isoformat()
        }
