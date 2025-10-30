"""
Rate Limiter Implementation

Multi-provider rate limiting for LLM requests.
"""

import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict, deque


@dataclass
class RateLimit:
    """Rate limit configuration."""
    requests_per_minute: int
    requests_per_hour: int
    requests_per_day: int
    burst_limit: int = 10


class RateLimiter:
    """Multi-provider rate limiter for LLM requests."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("rate_limiter")
        
        # Rate limit configurations per provider
        self.rate_limits = self._initialize_rate_limits()
        
        # Request tracking per provider
        self.request_history = defaultdict(lambda: deque())
        self.burst_tokens = defaultdict(int)
        
        # Rate limit enforcement
        self.enforcement_enabled = config.get('enforcement_enabled', True)
        self.cleanup_interval = config.get('cleanup_interval', 300)  # 5 minutes
        self.last_cleanup = time.time()
        
        self.logger.info("RateLimiter initialized")
    
    def _initialize_rate_limits(self) -> Dict[str, RateLimit]:
        """Initialize rate limits for each provider."""
        default_limits = RateLimit(
            requests_per_minute=60,
            requests_per_hour=1000,
            requests_per_day=10000,
            burst_limit=10
        )
        
        rate_limits = {}
        
        # Provider-specific configurations
        providers = ['openrouter', 'gemini', 'mistral']
        for provider in providers:
            provider_config = self.config.get(provider, {})
            rate_limits[provider] = RateLimit(
                requests_per_minute=provider_config.get('requests_per_minute', 60),
                requests_per_hour=provider_config.get('requests_per_hour', 1000),
                requests_per_day=provider_config.get('requests_per_day', 10000),
                burst_limit=provider_config.get('burst_limit', 10)
            )
        
        return rate_limits
    
    def can_make_request(self, provider: str) -> bool:
        """Check if request can be made for provider."""
        try:
            if not self.enforcement_enabled:
                return True
            
            # Clean up old requests periodically
            self._cleanup_old_requests()
            
            # Get rate limit for provider
            rate_limit = self.rate_limits.get(provider)
            if not rate_limit:
                self.logger.warning(f"No rate limit configured for provider: {provider}")
                return True
            
            current_time = time.time()
            request_history = self.request_history[provider]
            
            # Check burst limit
            if self.burst_tokens[provider] >= rate_limit.burst_limit:
                self.logger.warning(f"Burst limit exceeded for provider: {provider}")
                return False
            
            # Check minute limit
            minute_ago = current_time - 60
            recent_requests = [req_time for req_time in request_history if req_time > minute_ago]
            if len(recent_requests) >= rate_limit.requests_per_minute:
                self.logger.warning(f"Minute limit exceeded for provider: {provider}")
                return False
            
            # Check hour limit
            hour_ago = current_time - 3600
            hourly_requests = [req_time for req_time in request_history if req_time > hour_ago]
            if len(hourly_requests) >= rate_limit.requests_per_hour:
                self.logger.warning(f"Hour limit exceeded for provider: {provider}")
                return False
            
            # Check day limit
            day_ago = current_time - 86400
            daily_requests = [req_time for req_time in request_history if req_time > day_ago]
            if len(daily_requests) >= rate_limit.requests_per_day:
                self.logger.warning(f"Day limit exceeded for provider: {provider}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking rate limit for {provider}: {e}")
            return True  # Allow request on error
    
    def record_request(self, provider: str, success: bool = True) -> bool:
        """Record a request for rate limiting."""
        try:
            current_time = time.time()
            
            # Add to request history
            self.request_history[provider].append(current_time)
            
            # Update burst tokens
            if success:
                self.burst_tokens[provider] += 1
            else:
                # Don't consume burst tokens for failed requests
                pass
            
            # Clean up old requests
            self._cleanup_old_requests()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error recording request for {provider}: {e}")
            return False
    
    def get_wait_time(self, provider: str) -> float:
        """Get wait time until next request can be made."""
        try:
            rate_limit = self.rate_limits.get(provider)
            if not rate_limit:
                return 0.0
            
            current_time = time.time()
            request_history = self.request_history[provider]
            
            # Check minute limit
            minute_ago = current_time - 60
            recent_requests = [req_time for req_time in request_history if req_time > minute_ago]
            
            if len(recent_requests) >= rate_limit.requests_per_minute:
                # Find oldest request in the last minute
                oldest_recent = min(recent_requests)
                wait_time = 60 - (current_time - oldest_recent)
                return max(0.0, wait_time)
            
            # Check burst limit
            if self.burst_tokens[provider] >= rate_limit.burst_limit:
                # Burst tokens decay over time
                decay_rate = 1.0 / 60.0  # 1 token per minute
                time_since_last = current_time - (request_history[-1] if request_history else current_time)
                decayed_tokens = max(0, self.burst_tokens[provider] - (time_since_last * decay_rate))
                
                if decayed_tokens >= rate_limit.burst_limit:
                    return 60.0  # Wait 1 minute for burst tokens to decay
            
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating wait time for {provider}: {e}")
            return 0.0
    
    def get_provider_status(self, provider: str) -> Dict[str, Any]:
        """Get rate limit status for provider."""
        try:
            rate_limit = self.rate_limits.get(provider)
            if not rate_limit:
                return {"error": "Provider not configured"}
            
            current_time = time.time()
            request_history = self.request_history[provider]
            
            # Calculate current usage
            minute_ago = current_time - 60
            hour_ago = current_time - 3600
            day_ago = current_time - 86400
            
            recent_requests = [req_time for req_time in request_history if req_time > minute_ago]
            hourly_requests = [req_time for req_time in request_history if req_time > hour_ago]
            daily_requests = [req_time for req_time in request_history if req_time > day_ago]
            
            return {
                "provider": provider,
                "current_usage": {
                    "minute": len(recent_requests),
                    "hour": len(hourly_requests),
                    "day": len(daily_requests)
                },
                "limits": {
                    "minute": rate_limit.requests_per_minute,
                    "hour": rate_limit.requests_per_hour,
                    "day": rate_limit.requests_per_day,
                    "burst": rate_limit.burst_limit
                },
                "burst_tokens": self.burst_tokens[provider],
                "can_make_request": self.can_make_request(provider),
                "wait_time": self.get_wait_time(provider)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting provider status for {provider}: {e}")
            return {"error": str(e)}
    
    def get_all_provider_status(self) -> Dict[str, Any]:
        """Get rate limit status for all providers."""
        status = {}
        for provider in self.rate_limits.keys():
            status[provider] = self.get_provider_status(provider)
        return status
    
    def reset_provider_limits(self, provider: str) -> bool:
        """Reset rate limits for a provider."""
        try:
            self.request_history[provider].clear()
            self.burst_tokens[provider] = 0
            self.logger.info(f"Reset rate limits for provider: {provider}")
            return True
        except Exception as e:
            self.logger.error(f"Error resetting limits for {provider}: {e}")
            return False
    
    def update_rate_limits(self, provider: str, new_limits: Dict[str, int]) -> bool:
        """Update rate limits for a provider."""
        try:
            if provider not in self.rate_limits:
                self.logger.error(f"Provider {provider} not configured")
                return False
            
            current_limits = self.rate_limits[provider]
            
            # Update limits
            if 'requests_per_minute' in new_limits:
                current_limits.requests_per_minute = new_limits['requests_per_minute']
            if 'requests_per_hour' in new_limits:
                current_limits.requests_per_hour = new_limits['requests_per_hour']
            if 'requests_per_day' in new_limits:
                current_limits.requests_per_day = new_limits['requests_per_day']
            if 'burst_limit' in new_limits:
                current_limits.burst_limit = new_limits['burst_limit']
            
            self.logger.info(f"Updated rate limits for provider {provider}: {new_limits}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating rate limits for {provider}: {e}")
            return False
    
    def _cleanup_old_requests(self):
        """Clean up old request history to prevent memory leaks."""
        current_time = time.time()
        
        # Only cleanup if enough time has passed
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        # Clean up requests older than 24 hours
        day_ago = current_time - 86400
        
        for provider in self.request_history:
            request_history = self.request_history[provider]
            # Remove old requests
            while request_history and request_history[0] < day_ago:
                request_history.popleft()
        
        # Decay burst tokens
        for provider in self.burst_tokens:
            if self.burst_tokens[provider] > 0:
                # Decay 1 token per minute
                time_since_cleanup = current_time - self.last_cleanup
                decay_amount = time_since_cleanup / 60.0
                self.burst_tokens[provider] = max(0, self.burst_tokens[provider] - decay_amount)
        
        self.last_cleanup = current_time
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """Get overall usage statistics."""
        try:
            current_time = time.time()
            total_requests = 0
            active_providers = 0
            
            for provider in self.request_history:
                request_history = self.request_history[provider]
                if request_history:
                    active_providers += 1
                    total_requests += len(request_history)
            
            return {
                "total_requests": total_requests,
                "active_providers": active_providers,
                "enforcement_enabled": self.enforcement_enabled,
                "last_cleanup": datetime.fromtimestamp(self.last_cleanup).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting usage statistics: {e}")
            return {"error": str(e)}

