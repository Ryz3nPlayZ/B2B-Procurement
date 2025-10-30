# llm/llm_router.py

import logging
import asyncio
from typing import Dict, Any, List, Optional

from config import settings
from .providers.gemini_client import GeminiClient
from .providers.openrouter_client import OpenRouterClient

logger = logging.getLogger(__name__)

class LLMRouter:
    """Routes LLM requests with proper fallback and retry logic."""

    def __init__(self):
        self.clients: Dict[str, Any] = {}
        
        # Initialize OpenRouter first (more reliable)
        if settings.OPENROUTER_API_KEY:
            try:
                self.clients['openrouter'] = OpenRouterClient(api_key=settings.OPENROUTER_API_KEY)
                logger.info("OpenRouter client initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize OpenRouter client: {e}")
        
        # Initialize Gemini as fallback
        if settings.GEMINI_API_KEY:
            try:
                self.clients['gemini'] = GeminiClient(api_key=settings.GEMINI_API_KEY)
                logger.info("Gemini client initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
        
        if not self.clients:
            logger.critical("No LLM clients initialized. Check your API keys in .env")

    async def generate(
        self,
        agent_role: str,
        prompt: str,
        system_message: str = None,
        conversation_history: List[Dict[str, str]] = None,
        max_retries: int = 3
    ) -> str:
        """Generate response with automatic fallback and retry logic."""
        
        if not self.clients:
            return "[ROUTER_ERROR: No clients available]"

        # Get model configuration
        agent_config = settings.LLM_CONFIG.get(agent_role, settings.LLM_CONFIG['seller'])
        primary_model = agent_config['primary_model']
        fallback_model = agent_config['fallback_model']

        # Determine which client to use based on model name
        primary_client = self._get_client_for_model(primary_model)
        fallback_client = self._get_client_for_model(fallback_model)

        # --- Try Primary Model with Retries ---
        if primary_client:
            for attempt in range(max_retries):
                try:
                    logger.info(f"Attempting generation with primary model: {primary_model} (attempt {attempt + 1}/{max_retries})")
                    
                    response = await primary_client.generate(
                        prompt=prompt,
                        system_message=system_message,
                        conversation_history=conversation_history,
                        model=primary_model
                    )
                    
                    # Check if response is an error
                    if not response.startswith("[") or not "ERROR" in response:
                        logger.info(f"Primary model succeeded on attempt {attempt + 1}")
                        return response
                    
                    logger.warning(f"Primary model returned error: {response[:50]}...")
                    
                    # Wait before retry (exponential backoff)
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # 1s, 2s, 4s
                        logger.info(f"Retrying in {wait_time}s...")
                        await asyncio.sleep(wait_time)
                        
                except Exception as e:
                    logger.error(f"Primary model attempt {attempt + 1} failed: {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt)
            
            logger.warning(f"Primary model failed after {max_retries} attempts")

        # --- Try Fallback Model ---
        if fallback_client:
            try:
                logger.warning(f"Falling back to model: {fallback_model}")
                
                response = await fallback_client.generate(
                    prompt=prompt,
                    system_message=system_message,
                    conversation_history=conversation_history,
                    model=fallback_model
                )
                
                if not response.startswith("[") or not "ERROR" in response:
                    logger.info("Fallback model succeeded")
                    return response
                
                logger.error(f"Fallback model also failed: {response[:50]}...")
                
            except Exception as e:
                logger.error(f"Fallback model exception: {e}")
        
        logger.error("All LLM providers failed")
        return "[ROUTER_ERROR: All models failed after retries]"

    def _get_client_for_model(self, model_name: str):
        """Determine which client handles a given model."""
        if 'deepseek' in model_name.lower() or 'openrouter' in model_name.lower():
            return self.clients.get('openrouter')
        elif 'gemini' in model_name.lower():
            return self.clients.get('gemini')
        return None