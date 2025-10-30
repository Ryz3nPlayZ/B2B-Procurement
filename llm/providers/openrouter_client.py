# llm/providers/openrouter_client.py

import logging
import httpx
from typing import Dict, Any, List

# Configure logging for this module
logger = logging.getLogger(__name__)

# The model name we will use
OPENROUTER_DEEPSEEK_MODEL = "deepseek/deepseek-r1:free"

class OpenRouterClient:
    """Async client for the OpenRouter API, compatible with OpenAI's client library structure."""

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("OpenRouter API key is required.")
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
    
    async def generate(
        self,
        prompt: str,
        system_message: str = None,
        conversation_history: List[Dict[str, str]] = None,
        model: str = OPENROUTER_DEEPSEEK_MODEL
    ) -> str:
        """
        Generate a response using the OpenRouter API with an async HTTP client.
        """
        logger.debug(f"Generating response from OpenRouter with model: {model}")

        # Build the messages payload for the OpenAI-compatible API
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add the current user prompt
        messages.append({"role": "user", "content": prompt})

        # Prepare the full JSON payload
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 4096,
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost", # Required by OpenRouter for free models
            "X-Title": "ASI-Supply-Chain-Agent", # Required by OpenRouter for free models
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.base_url, json=payload, headers=headers, timeout=60.0)
                response.raise_for_status()

                response_data = response.json()
                
                # Extract the response text
                if response_data.get("choices"):
                    first_choice = response_data["choices"][0]
                    if first_choice.get("message"):
                        return first_choice["message"].get("content", "")

                logger.warning("No content found in OpenRouter response.")
                return "[OPENROUTER: No content found]"

        except httpx.HTTPStatusError as e:
            logger.error(f"OpenRouter API request failed with status {e.response.status_code}: {e.response.text}")
            return f"[OPENROUTER_ERROR: HTTP {e.response.status_code}]"
        except Exception as e:
            logger.error(f"An unexpected error occurred while calling OpenRouter API: {e}")
            return f"[OPENROUTER_ERROR: {str(e)}]"