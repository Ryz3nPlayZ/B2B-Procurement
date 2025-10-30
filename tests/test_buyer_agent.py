"""
Buyer Agent Tests

Test cases for buyer agent functionality.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agents.buyer_agent import BuyerAgent
from protocols.rfq_protocol import RFQMessage
from protocols.quote_protocol import QuoteMessage


class TestBuyerAgent(unittest.TestCase):
    """Test cases for BuyerAgent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'metta': {},
            'llm': {},
            'scoring': {}
        }
        self.agent_id = "buyer_001"
        self.buyer_agent = BuyerAgent(self.agent_id, self.config)
    
    def test_initialization(self):
        """Test BuyerAgent initialization."""
        self.assertEqual(self.buyer_agent.agent_id, self.agent_id)
        self.assertIsNotNone(self.buyer_agent.scorer)
        self.assertIsNotNone(self.buyer_agent.buyer_queries)
        self.assertIsInstance(self.buyer_agent.active_rfqs, dict)
        self.assertIsInstance(self.buyer_agent.received_quotes, dict)
    
    def test_process_message_rfq_request(self):
        """Test processing RFQ request message."""
        message = {
            "type": "rfq_request",
            "requirements": {
                "product": "Industrial Sensors",
                "quantity": 100,
                "specifications": "High precision"
            },
            "deadline": "2024-12-31T23:59:59Z"
        }
        
        with patch.object(self.buyer_agent, 'get_llm_response') as mock_llm, \
             patch.object(self.buyer_agent.metta_engine, 'log_rfq_created') as mock_log:
            
            mock_llm.return_value = "Generated RFQ content"
            
            result = self.buyer_agent.process_message(message)
            
            self.assertIn("type", result)
            self.assertEqual(result["type"], "rfq_created")
            self.assertIn("rfq_id", result)
            self.assertIn("rfq", result)
    
    def test_process_message_quote(self):
        """Test processing quote message."""
        quote_data = {
            "quote_id": "quote_123",
            "seller_id": "seller_001",
            "rfq_id": "rfq_123",
            "content": "Quote content",
            "pricing": {"total": 1000}
        }
        
        message = {
            "type": "quote",
            **quote_data
        }
        
        with patch.object(self.buyer_agent.scorer, 'score_offer') as mock_score, \
             patch.object(self.buyer_agent.buyer_queries, 'get_buyer_preferences') as mock_prefs, \
             patch.object(self.buyer_agent, 'get_llm_response') as mock_llm, \
             patch.object(self.buyer_agent.metta_engine, 'log_quote_received') as mock_log:
            
            mock_score.return_value = {"score": 0.8, "criteria": {}, "recommendation": "accept"}
            mock_prefs.return_value = {"preference": "value"}
            mock_llm.return_value = "Generated response"
            
            result = self.buyer_agent.process_message(message)
            
            self.assertIn("type", result)
            self.assertEqual(result["type"], "quote_response")
            self.assertIn("score", result)
            self.assertIn("action", result)
    
    def test_process_message_negotiation(self):
        """Test processing negotiation message."""
        negotiation_data = {
            "rfq_id": "rfq_123",
            "round": 2,
            "offer": {"price": 950}
        }
        
        message = {
            "type": "negotiation",
            "negotiation": negotiation_data
        }
        
        with patch.object(self.buyer_agent.buyer_queries, 'get_negotiation_strategy') as mock_strategy, \
             patch.object(self.buyer_agent, 'get_llm_response') as mock_llm:
            
            mock_strategy.return_value = {"approach": "collaborative", "method": "win-win"}
            mock_llm.return_value = "Generated counter-offer"
            
            result = self.buyer_agent.process_message(message)
            
            self.assertIn("type", result)
            self.assertEqual(result["type"], "negotiation_response")
            self.assertIn("counter_offer", result)
    
    def test_create_rfq(self):
        """Test RFQ creation."""
        request = {
            "requirements": {
                "product": "Test Product",
                "quantity": 50
            },
            "deadline": "2024-12-31T23:59:59Z"
        }
        
        with patch.object(self.buyer_agent.buyer_queries, 'get_procurement_policies') as mock_policies, \
             patch.object(self.buyer_agent.buyer_queries, 'get_budget_constraints') as mock_constraints, \
             patch.object(self.buyer_agent, 'get_llm_response') as mock_llm, \
             patch.object(self.buyer_agent.metta_engine, 'log_rfq_created') as mock_log:
            
            mock_policies.return_value = {"policy1": "description1"}
            mock_constraints.return_value = {"budget": 10000}
            mock_llm.return_value = "Generated RFQ content"
            
            result = self.buyer_agent._create_rfq(request)
            
            self.assertIn("type", result)
            self.assertEqual(result["type"], "rfq_created")
            self.assertIn("rfq_id", result)
            self.assertIn("rfq", result)
    
    def test_process_quote(self):
        """Test quote processing."""
        quote_data = {
            "quote_id": "quote_123",
            "seller_id": "seller_001",
            "rfq_id": "rfq_123",
            "content": "Quote content",
            "pricing": {"total": 1000}
        }
        
        with patch.object(self.buyer_agent.scorer, 'score_offer') as mock_score, \
             patch.object(self.buyer_agent.buyer_queries, 'get_buyer_preferences') as mock_prefs, \
             patch.object(self.buyer_agent, 'get_llm_response') as mock_llm, \
             patch.object(self.buyer_agent.metta_engine, 'log_quote_received') as mock_log:
            
            mock_score.return_value = {"score": 0.8, "criteria": {}, "recommendation": "accept"}
            mock_prefs.return_value = {"preference": "value"}
            mock_llm.return_value = "Generated response"
            
            result = self.buyer_agent._process_quote(quote_data)
            
            self.assertIn("type", result)
            self.assertEqual(result["type"], "quote_response")
            self.assertIn("score", result)
            self.assertIn("action", result)
    
    def test_get_capabilities(self):
        """Test getting agent capabilities."""
        capabilities = self.buyer_agent.get_capabilities()
        
        self.assertIn("agent_type", capabilities)
        self.assertEqual(capabilities["agent_type"], "buyer")
        self.assertIn("capabilities", capabilities)
        self.assertIn("active_rfqs", capabilities)
        self.assertIn("received_quotes", capabilities)
    
    def test_invalid_message_type(self):
        """Test handling of invalid message type."""
        message = {
            "type": "invalid_type",
            "content": "test"
        }
        
        result = self.buyer_agent.process_message(message)
        
        self.assertIn("error", result)
        self.assertIn("Unknown message type", result["error"])
    
    def test_message_validation_failure(self):
        """Test handling of invalid message format."""
        message = {
            "invalid": "message"
        }
        
        result = self.buyer_agent.process_message(message)
        
        self.assertIn("error", result)
        self.assertIn("Invalid message format", result["error"])


if __name__ == '__main__':
    unittest.main()

