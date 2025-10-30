# llm/providers/gemini_client.py

import logging
import httpx
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-2.0-flash"

class GeminiClient:
    """Async client for Google Gemini API."""

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Gemini API key is required.")
        self.api_key = api_key
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    
    async def generate(
        self,
        prompt: str,
        system_message: str = None,
        conversation_history: List[Dict[str, str]] = None,
        model: str = None  # ADDED - accept but ignore for compatibility
    ) -> str:
        """
        Generate a response using the Gemini API with an async HTTP client.
        """
        logger.debug(f"Generating response from Gemini with model: {GEMINI_MODEL}")

        # Build the contents payload for the Gemini API
        contents = []
        if conversation_history:
            for msg in conversation_history:
                role = "user" if msg.get("role") == "user" else "model"
                contents.append({"role": role, "parts": [{"text": msg.get("content", "")}]})
        
        # Add the current user prompt
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        # Prepare the full JSON payload
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 4096,
            }
        }
        
        # Add system instruction if provided
        if system_message:
            payload["systemInstruction"] = {"parts": [{"text": system_message}]}

        headers = {
            'Content-Type': 'application/json',
        }
        params = {
            'key': self.api_key
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.base_url, json=payload, headers=headers, params=params, timeout=60.0)
                response.raise_for_status()

                response_data = response.json()
                
                # Extract the response text
                if response_data.get("candidates"):
                    first_candidate = response_data["candidates"][0]
                    if first_candidate.get("content", {}).get("parts"):
                        return first_candidate["content"]["parts"][0].get("text", "")
                
                logger.warning("No content found in Gemini response.")
                return "[GEMINI: No content found]"

        except httpx.HTTPStatusError as e:
            logger.error(f"Gemini API request failed with status {e.response.status_code}: {e.response.text}")
            return f"[GEMINI_ERROR: HTTP {e.response.status_code}]"
        except Exception as e:
            logger.error(f"An unexpected error occurred while calling Gemini API: {e}")
            return f"[GEMINI_ERROR: {str(e)}]"