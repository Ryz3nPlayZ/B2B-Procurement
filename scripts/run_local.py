#!/usr/bin/env python3
"""
Run ASI System Locally

Local testing and development script for the ASI system.
"""

import os
import sys
import time
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.buyer_agent import BuyerAgent
from agents.seller_agent import SellerAgent
from agents.coordinator_agent import CoordinatorAgent
from config.settings import settings
from utils.logging_config import setup_logging


class ASILocalRunner:
    """Local runner for ASI system testing."""
    
    def __init__(self):
        self.logger = setup_logging().get_logger('asi_local_runner')
        self.agents = {}
        self.running = False
        
        # Initialize configuration
        self.config = settings.get_full_config()
        self.logger.info("ASI Local Runner initialized")
    
    def initialize_agents(self):
        """Initialize all agents for local testing."""
        try:
            # Initialize coordinator
            coordinator_config = {
                'metta': self.config['metta'],
                'llm': self.config['llm']
            }
            self.agents['coordinator'] = CoordinatorAgent('coordinator_001', coordinator_config)
            self.logger.info("Coordinator agent initialized")
            
            # Initialize buyer
            buyer_config = {
                'metta': self.config['metta'],
                'llm': self.config['llm'],
                'scoring': self.config['scoring']
            }
            self.agents['buyer'] = BuyerAgent('buyer_001', buyer_config)
            self.logger.info("Buyer agent initialized")
            
            # Initialize sellers
            seller_config = {
                'metta': self.config['metta'],
                'llm': self.config['llm']
            }
            self.agents['seller_a'] = SellerAgent('seller_a_001', seller_config)
            self.agents['seller_b'] = SellerAgent('seller_b_001', seller_config)
            self.agents['seller_c'] = SellerAgent('seller_c_001', seller_config)
            self.logger.info("Seller agents initialized")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize agents: {e}")
            return False
    
    def register_agents(self):
        """Register all agents with coordinator."""
        try:
            # Register buyer
            buyer_message = {
                "type": "agent_register",
                "agent": {
                    "id": "buyer_001",
                    "type": "buyer",
                    "capabilities": ["rfq_generation", "quote_evaluation", "negotiation"]
                }
            }
            self.agents['coordinator'].process_message(buyer_message)
            
            # Register sellers
            for seller_id, seller_agent in [('seller_a_001', 'seller_a'), ('seller_b_001', 'seller_b'), ('seller_c_001', 'seller_c')]:
                seller_message = {
                    "type": "agent_register",
                    "agent": {
                        "id": seller_id,
                        "type": "seller",
                        "capabilities": ["quote_generation", "inventory_management", "negotiation"]
                    }
                }
                self.agents['coordinator'].process_message(seller_message)
            
            self.logger.info("All agents registered with coordinator")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register agents: {e}")
            return False
    
    def run_negotiation_scenario(self):
        """Run a sample negotiation scenario."""
        self.logger.info("Starting negotiation scenario")
        
        try:
            # Step 1: Buyer creates RFQ
            rfq_request = {
                "type": "rfq_request",
                "requirements": {
                    "product": "Industrial Sensors",
                    "quantity": 100,
                    "specifications": "High precision temperature and pressure sensors",
                    "quality_standards": "ISO 9001",
                    "delivery_timeline": "30 days"
                },
                "deadline": "2024-12-31T23:59:59Z"
            }
            
            self.logger.info("Buyer creating RFQ...")
            rfq_response = self.agents['buyer'].process_message(rfq_request)
            self.logger.info(f"RFQ created: {rfq_response.get('rfq_id', 'Unknown')}")
            
            # Step 2: Sellers respond with quotes
            if 'rfq' in rfq_response:
                rfq_data = rfq_response['rfq']
                
                for seller_name in ['seller_a', 'seller_b', 'seller_c']:
                    self.logger.info(f"{seller_name} generating quote...")
                    
                    quote_response = self.agents[seller_name].process_message({
                        "type": "rfq",
                        **rfq_data
                    })
                    
                    if 'quote' in quote_response:
                        self.logger.info(f"{seller_name} generated quote: {quote_response['quote'].get('quote_id', 'Unknown')}")
                        
                        # Step 3: Buyer evaluates quote
                        self.logger.info("Buyer evaluating quote...")
                        evaluation = self.agents['buyer'].process_message(quote_response)
                        self.logger.info(f"Quote evaluation: {evaluation.get('action', 'Unknown')}")
            
            self.logger.info("Negotiation scenario completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Negotiation scenario failed: {e}")
            return False
    
    def run_system_health_check(self):
        """Run system health check."""
        self.logger.info("Running system health check")
        
        try:
            # Check coordinator status
            status_message = {"type": "system_status"}
            coordinator_status = self.agents['coordinator'].process_message(status_message)
            self.logger.info(f"Coordinator status: {coordinator_status.get('system_health', 'Unknown')}")
            
            # Check agent capabilities
            for agent_name, agent in self.agents.items():
                if hasattr(agent, 'get_capabilities'):
                    capabilities = agent.get_capabilities()
                    self.logger.info(f"{agent_name} capabilities: {capabilities.get('capabilities', [])}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
    
    def run_interactive_mode(self):
        """Run interactive mode for manual testing."""
        self.logger.info("Starting interactive mode")
        print("\n🤖 ASI System Interactive Mode")
        print("Commands:")
        print("  status - Show system status")
        print("  scenario - Run negotiation scenario")
        print("  health - Run health check")
        print("  agents - List agents")
        print("  quit - Exit")
        
        while True:
            try:
                command = input("\n> ").strip().lower()
                
                if command == 'quit':
                    break
                elif command == 'status':
                    status_message = {"type": "system_status"}
                    status = self.agents['coordinator'].process_message(status_message)
                    print(f"System Status: {status}")
                elif command == 'scenario':
                    self.run_negotiation_scenario()
                elif command == 'health':
                    self.run_system_health_check()
                elif command == 'agents':
                    for agent_name, agent in self.agents.items():
                        if hasattr(agent, 'get_capabilities'):
                            capabilities = agent.get_capabilities()
                            print(f"{agent_name}: {capabilities.get('agent_type', 'Unknown')}")
                else:
                    print("Unknown command. Type 'quit' to exit.")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
        
        self.logger.info("Interactive mode ended")
    
    def start(self):
        """Start the ASI local runner."""
        self.logger.info("Starting ASI Local Runner")
        
        try:
            # Initialize agents
            if not self.initialize_agents():
                self.logger.error("Failed to initialize agents")
                return False
            
            # Register agents
            if not self.register_agents():
                self.logger.error("Failed to register agents")
                return False
            
            # Run health check
            if not self.run_system_health_check():
                self.logger.warning("Health check failed, but continuing")
            
            # Run negotiation scenario
            if not self.run_negotiation_scenario():
                self.logger.warning("Negotiation scenario failed, but continuing")
            
            # Start interactive mode
            self.run_interactive_mode()
            
            return True
            
        except Exception as e:
            self.logger.error(f"ASI Local Runner failed: {e}")
            return False
    
    def stop(self):
        """Stop the ASI local runner."""
        self.logger.info("Stopping ASI Local Runner")
        self.running = False


def main():
    """Main entry point for the script."""
    print("🚀 Starting ASI System Local Runner")
    
    runner = ASILocalRunner()
    
    try:
        success = runner.start()
        if success:
            print("✅ ASI Local Runner completed successfully")
        else:
            print("❌ ASI Local Runner failed")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 ASI Local Runner stopped by user")
        runner.stop()
    except Exception as e:
        print(f"❌ ASI Local Runner error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

