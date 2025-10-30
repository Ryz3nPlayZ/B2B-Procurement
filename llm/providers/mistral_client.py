"""
Mistral Client Implementation

Integration with Mistral AI API for LLM operations.
"""

import logging
import requests
import json
from typing import Dict, Any, Optional, List
from datetime import datetime


class MistralClient:
    """Mistral AI API client for LLM integration."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("mistral_client")
        
        # API configuration
        self.api_key = config.get('api_key')
        self.base_url = config.get('base_url', 'https://api.mistral.ai/v1')
        self.default_model = config.get('default_model', 'mistral-large-latest')
        self.max_retries = config.get('max_retries', 3)
        self.timeout = config.get('timeout', 30)
        
        # Request headers
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        self.logger.info("MistralClient initialized")
    
    def generate(self, request_data: Dict[str, Any]) -> str:
        """Generate response using Mistral API."""
        try:
            # Prepare request payload
            payload = self._prepare_payload(request_data)
            
            # Make API request
            response = self._make_request(payload)
            
            # Extract and return response
            return self._extract_response(response)
            
        except Exception as e:
            self.logger.error(f"Mistral generation failed: {e}")
            raise
    
    def _prepare_payload(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare request payload for Mistral API."""
        model = request_data.get('model', self.default_model)
        prompt = request_data.get('prompt', '')
        max_tokens = request_data.get('max_tokens', 1000)
        context = request_data.get('context', {})
        
        # Build messages array
        messages = self._build_messages(prompt, context)
        
        payload = {
            'model': model,
            'messages': messages,
            'max_tokens': max_tokens,
            'temperature': 0.7,
            'stream': False
        }
        
        # Add optional parameters
        if 'temperature' in request_data:
            payload['temperature'] = request_data['temperature']
        if 'top_p' in request_data:
            payload['top_p'] = request_data['top_p']
        if 'random_seed' in request_data:
            payload['random_seed'] = request_data['random_seed']
        
        return payload
    
    def _build_messages(self, prompt: str, context: Dict[str, Any]) -> List[Dict[str, str]]:
        """Build messages array for API request."""
        messages = []
        
        # Add system message if provided
        if 'system_message' in context:
            messages.append({
                'role': 'system',
                'content': context['system_message']
            })
        
        # Add context messages if provided
        if 'conversation_history' in context:
            for msg in context['conversation_history']:
                messages.append({
                    'role': msg.get('role', 'user'),
                    'content': msg.get('content', '')
                })
        
        # Add current prompt
        messages.append({
            'role': 'user',
            'content': prompt
        })
        
        return messages
    
    def _make_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP request to Mistral API."""
        url = f"{self.base_url}/chat/completions"
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    url,
                    headers=self.headers,
                    json=payload,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:  # Rate limit
                    self.logger.warning("Rate limit exceeded, retrying...")
                    if attempt < self.max_retries - 1:
                        import time
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                else:
                    self.logger.error(f"API request failed: {response.status_code} - {response.text}")
                    raise Exception(f"API request failed: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                self.logger.warning(f"Request timeout (attempt {attempt + 1})")
                if attempt < self.max_retries - 1:
                    continue
                else:
                    raise
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Request failed: {e}")
                if attempt < self.max_retries - 1:
                    continue
                else:
                    raise
        
        raise Exception("Max retries exceeded")
    
    def _extract_response(self, response: Dict[str, Any]) -> str:
        """Extract response text from API response."""
        try:
            if 'choices' in response and len(response['choices']) > 0:
                return response['choices'][0]['message']['content']
            else:
                raise Exception("No response content found")
        except Exception as e:
            self.logger.error(f"Failed to extract response: {e}")
            raise
    
    def generate_streaming(self, request_data: Dict[str, Any]) -> List[str]:
        """Generate streaming response using Mistral API."""
        try:
            # Prepare request payload
            payload = self._prepare_payload(request_data)
            payload['stream'] = True
            
            # Make streaming request
            url = f"{self.base_url}/chat/completions"
            
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=self.timeout,
                stream=True
            )
            
            if response.status_code != 200:
                raise Exception(f"Streaming request failed: {response.status_code}")
            
            # Process streaming response
            chunks = []
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]
                        if data_str.strip() == '[DONE]':
                            break
                        try:
                            data = json.loads(data_str)
                            if 'choices' in data and len(data['choices']) > 0:
                                delta = data['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    chunks.append(delta['content'])
                        except json.JSONDecodeError:
                            continue
            
            return chunks
            
        except Exception as e:
            self.logger.error(f"Mistral streaming generation failed: {e}")
            raise
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models from Mistral."""
        try:
            url = f"{self.base_url}/models"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            else:
                self.logger.error(f"Failed to get models: {response.status_code}")
                return []
                
        except Exception as e:
            self.logger.error(f"Failed to get available models: {e}")
            return []
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific model."""
        try:
            models = self.get_available_models()
            for model in models:
                if model.get('id') == model_name:
                    return model
            return None
        except Exception as e:
            self.logger.error(f"Failed to get model info: {e}")
            return None
    
    def estimate_cost(self, prompt: str, model: str = None) -> Dict[str, Any]:
        """Estimate cost for a request."""
        try:
            model = model or self.default_model
            model_info = self.get_model_info(model)
            
            if not model_info:
                return {"error": "Model not found"}
            
            # Rough estimation based on token count
            prompt_tokens = len(prompt.split()) * 1.3  # Rough token estimation
            completion_tokens = 100  # Estimated completion tokens
            
            # Mistral pricing (approximate)
            pricing = {
                'mistral-tiny': {'prompt': 0.0001, 'completion': 0.0001},
                'mistral-small': {'prompt': 0.0002, 'completion': 0.0002},
                'mistral-medium': {'prompt': 0.0006, 'completion': 0.0006},
                'mistral-large': {'prompt': 0.001, 'completion': 0.001}
            }
            
            model_pricing = pricing.get(model, {'prompt': 0.001, 'completion': 0.001})
            prompt_cost = prompt_tokens * model_pricing['prompt']
            completion_cost = completion_tokens * model_pricing['completion']
            
            return {
                "estimated_tokens": int(prompt_tokens + completion_tokens),
                "estimated_cost": prompt_cost + completion_cost,
                "model": model,
                "pricing": model_pricing
            }
            
        except Exception as e:
            self.logger.error(f"Failed to estimate cost: {e}")
            return {"error": str(e)}
    
    def health_check(self) -> bool:
        """Check if Mistral API is accessible."""
        try:
            url = f"{self.base_url}/models"
            response = requests.get(url, headers=self.headers, timeout=10)
            return response.status_code == 200
        except Exception:
            return False

