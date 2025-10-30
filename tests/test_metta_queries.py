"""
MeTTa Queries Tests

Test cases for MeTTa knowledge base integration.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from metta.metta_engine import MeTTaEngine
from metta.queries.buyer_queries import BuyerQueries
from metta.queries.seller_queries import SellerQueries


class TestMeTTaEngine(unittest.TestCase):
    """Test cases for MeTTaEngine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'metta': {
                'enabled': True,
                'timeout': 30
            }
        }
        self.engine = MeTTaEngine(self.config)
    
    def test_initialization(self):
        """Test MeTTaEngine initialization."""
        self.assertIsNotNone(self.engine)
        self.assertIsNotNone(self.engine.session_id)
    
    def test_execute_query(self):
        """Test query execution."""
        query = "test query"
        result = self.engine.execute_query(query)
        # Mock implementation should return empty list
        self.assertIsInstance(result, list)
    
    def test_add_fact(self):
        """Test adding fact to knowledge base."""
        fact = "(test-fact test-value)"
        result = self.engine.add_fact(fact)
        self.assertTrue(result)
    
    def test_log_deal_start(self):
        """Test logging deal start."""
        deal_id = "test_deal_123"
        agent_id = "buyer_001"
        deal_data = {"amount": 1000}
        
        result = self.engine.log_deal_start(deal_id, agent_id, deal_data)
        self.assertTrue(result)
    
    def test_log_deal_end(self):
        """Test logging deal end."""
        deal_id = "test_deal_123"
        agent_id = "buyer_001"
        final_state = {"status": "completed"}
        
        result = self.engine.log_deal_end(deal_id, agent_id, final_state)
        self.assertTrue(result)
    
    def test_get_knowledge_base_status(self):
        """Test getting knowledge base status."""
        status = self.engine.get_knowledge_base_status()
        self.assertIn('session_id', status)
        self.assertIn('status', status)


class TestBuyerQueries(unittest.TestCase):
    """Test cases for BuyerQueries."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_engine = Mock(spec=MeTTaEngine)
        self.buyer_queries = BuyerQueries(self.mock_engine)
    
    def test_initialization(self):
        """Test BuyerQueries initialization."""
        self.assertIsNotNone(self.buyer_queries)
        self.assertEqual(self.buyer_queries.metta_engine, self.mock_engine)
    
    def test_get_procurement_policies(self):
        """Test getting procurement policies."""
        # Mock engine response
        mock_result = [
            ["procurement-policy", "competitive-bidding", "All purchases over $10,000 must go through competitive bidding process"],
            ["procurement-policy", "vendor-diversification", "No single vendor should account for more than 40% of total procurement"]
        ]
        self.mock_engine.execute_query.return_value = mock_result
        
        policies = self.buyer_queries.get_procurement_policies()
        
        self.assertIsInstance(policies, dict)
        self.assertIn("competitive-bidding", policies)
        self.assertIn("vendor-diversification", policies)
    
    def test_get_budget_constraints(self):
        """Test getting budget constraints."""
        # Mock engine response
        mock_result = [
            ["budget-constraint", "quarterly", 100000.0, "Q1-2024"],
            ["budget-constraint", "annual", 500000.0, "2024"]
        ]
        self.mock_engine.execute_query.return_value = mock_result
        
        constraints = self.buyer_queries.get_budget_constraints()
        
        self.assertIsInstance(constraints, dict)
        self.assertIn("quarterly", constraints)
        self.assertIn("annual", constraints)
    
    def test_get_quality_requirements(self):
        """Test getting quality requirements."""
        # Mock engine response
        mock_result = [
            ["quality-requirement", "delivery-time", "standard", 7.0],
            ["quality-requirement", "warranty", "minimum", 12.0]
        ]
        self.mock_engine.execute_query.return_value = mock_result
        
        requirements = self.buyer_queries.get_quality_requirements()
        
        self.assertIsInstance(requirements, dict)
        self.assertIn("delivery-time", requirements)
        self.assertIn("warranty", requirements)
    
    def test_evaluate_quote(self):
        """Test quote evaluation."""
        quote_data = {
            "price": 1000,
            "quality": "high",
            "delivery": "fast"
        }
        
        result = self.buyer_queries.evaluate_quote(quote_data)
        
        self.assertIsInstance(result, dict)
        self.assertIn("score", result)
        self.assertIn("criteria", result)
        self.assertIn("recommendation", result)
    
    def test_get_approval_requirements(self):
        """Test getting approval requirements."""
        # Test different amounts
        low_amount = 5000
        medium_amount = 25000
        high_amount = 100000
        
        low_result = self.buyer_queries.get_approval_requirements(low_amount)
        medium_result = self.buyer_queries.get_approval_requirements(medium_amount)
        high_result = self.buyer_queries.get_approval_requirements(high_amount)
        
        self.assertEqual(low_result["level"], "low")
        self.assertEqual(medium_result["level"], "medium")
        self.assertEqual(high_result["level"], "high")


class TestSellerQueries(unittest.TestCase):
    """Test cases for SellerQueries."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_engine = Mock(spec=MeTTaEngine)
        self.seller_queries = SellerQueries(self.mock_engine)
    
    def test_initialization(self):
        """Test SellerQueries initialization."""
        self.assertIsNotNone(self.seller_queries)
        self.assertEqual(self.seller_queries.metta_engine, self.mock_engine)
    
    def test_get_inventory(self):
        """Test getting inventory."""
        # Mock engine response
        mock_result = [
            ["Inventory", "A001", "warehouse-1", 150, 45.50],
            ["Inventory", "A001", "warehouse-2", 75, 45.50]
        ]
        self.mock_engine.execute_query.return_value = mock_result
        
        inventory = self.seller_queries.get_inventory()
        
        self.assertIsInstance(inventory, dict)
        self.assertIn("A001", inventory)
    
    def test_get_pricing_rules(self):
        """Test getting pricing rules."""
        # Mock engine response
        mock_result = [
            ["Pricing", "A001", "retail", 89.99, "standard"],
            ["Pricing", "A001", "wholesale", 67.50, "min-100-units"]
        ]
        self.mock_engine.execute_query.return_value = mock_result
        
        pricing = self.seller_queries.get_pricing_rules()
        
        self.assertIsInstance(pricing, dict)
        self.assertIn("A001", pricing)
    
    def test_get_products(self):
        """Test getting products."""
        # Mock engine response
        mock_result = [
            ["Product", "A001", "Industrial Sensors", "Electronics", "High-precision temperature and pressure sensors"],
            ["Product", "A002", "Control Systems", "Automation", "PLC-based control systems for manufacturing"]
        ]
        self.mock_engine.execute_query.return_value = mock_result
        
        products = self.seller_queries.get_products()
        
        self.assertIsInstance(products, dict)
        self.assertIn("A001", products)
        self.assertIn("A002", products)
    
    def test_assess_fulfillment_capability(self):
        """Test fulfillment capability assessment."""
        requirements = {
            "products": ["A001", "A002"],
            "quantities": [10, 5]
        }
        
        # Mock inventory and capabilities
        with patch.object(self.seller_queries, 'get_inventory') as mock_inventory, \
             patch.object(self.seller_queries, 'get_capabilities') as mock_capabilities:
            
            mock_inventory.return_value = {
                "A001": [{"location": "warehouse-1", "quantity": 100, "cost": 45.50}],
                "A002": [{"location": "warehouse-1", "quantity": 50, "cost": 1250.00}]
            }
            mock_capabilities.return_value = {
                "manufacturing": {"description": "custom-design", "level": "high"}
            }
            
            result = self.seller_queries.assess_fulfillment_capability(requirements)
            
            self.assertIsInstance(result, dict)
            self.assertIn("can_fulfill", result)
    
    def test_get_pricing_for_requirements(self):
        """Test getting pricing for requirements."""
        requirements = {
            "products": ["A001"],
            "quantities": [10]
        }
        
        # Mock pricing rules
        with patch.object(self.seller_queries, 'get_pricing_rules') as mock_pricing:
            mock_pricing.return_value = {
                "A001": {
                    "wholesale": {"price": 67.50, "conditions": "min-100-units"},
                    "retail": {"price": 89.99, "conditions": "standard"}
                }
            }
            
            result = self.seller_queries.get_pricing_for_requirements(requirements)
            
            self.assertIsInstance(result, dict)
            self.assertIn("base_price", result)


if __name__ == '__main__':
    unittest.main()

