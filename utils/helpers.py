"""
Helper Utilities

Miscellaneous utility functions for the ASI system.
"""

import json
import hashlib
import uuid
import time
import re
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from pathlib import Path


class DataHelpers:
    """Data manipulation and validation helpers."""
    
    @staticmethod
    def safe_json_loads(data: str, default: Any = None) -> Any:
        """Safely load JSON data with fallback."""
        try:
            return json.loads(data)
        except (json.JSONDecodeError, TypeError):
            return default
    
    @staticmethod
    def safe_json_dumps(data: Any, default: str = "{}") -> str:
        """Safely dump data to JSON with fallback."""
        try:
            return json.dumps(data, default=str, ensure_ascii=False)
        except (TypeError, ValueError):
            return default
    
    @staticmethod
    def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """Validate data against JSON schema (simplified)."""
        try:
            # Basic validation - check required fields
            required_fields = schema.get('required', [])
            for field in required_fields:
                if field not in data:
                    return False
            
            # Check field types
            properties = schema.get('properties', {})
            for field, field_schema in properties.items():
                if field in data:
                    expected_type = field_schema.get('type')
                    if expected_type:
                        if expected_type == 'string' and not isinstance(data[field], str):
                            return False
                        elif expected_type == 'number' and not isinstance(data[field], (int, float)):
                            return False
                        elif expected_type == 'boolean' and not isinstance(data[field], bool):
                            return False
                        elif expected_type == 'array' and not isinstance(data[field], list):
                            return False
                        elif expected_type == 'object' and not isinstance(data[field], dict):
                            return False
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = DataHelpers.deep_merge_dicts(result[key], value)
            else:
                result[key] = value
        
        return result
    
    @staticmethod
    def flatten_dict(data: Dict[str, Any], separator: str = '.') -> Dict[str, Any]:
        """Flatten nested dictionary."""
        def _flatten(obj, parent_key=''):
            items = []
            if isinstance(obj, dict):
                for k, v in obj.items():
                    new_key = f"{parent_key}{separator}{k}" if parent_key else k
                    items.extend(_flatten(v, new_key).items())
            else:
                return {parent_key: obj}
            return dict(items)
        
        return _flatten(data)
    
    @staticmethod
    def unflatten_dict(data: Dict[str, Any], separator: str = '.') -> Dict[str, Any]:
        """Unflatten dictionary with separator."""
        result = {}
        for key, value in data.items():
            keys = key.split(separator)
            current = result
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            current[keys[-1]] = value
        return result


class StringHelpers:
    """String manipulation and validation helpers."""
    
    @staticmethod
    def sanitize_string(text: str, max_length: int = None) -> str:
        """Sanitize string by removing dangerous characters."""
        if not isinstance(text, str):
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove script tags
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove potentially dangerous characters
        text = re.sub(r'[<>"\']', '', text)
        
        # Limit length
        if max_length and len(text) > max_length:
            text = text[:max_length]
        
        return text.strip()
    
    @staticmethod
    def generate_id(prefix: str = "", length: int = 8) -> str:
        """Generate unique ID with optional prefix."""
        if prefix:
            return f"{prefix}_{uuid.uuid4().hex[:length]}"
        return uuid.uuid4().hex[:length]
    
    @staticmethod
    def generate_hash(data: str, algorithm: str = 'sha256') -> str:
        """Generate hash for data."""
        if algorithm == 'md5':
            return hashlib.md5(data.encode()).hexdigest()
        elif algorithm == 'sha1':
            return hashlib.sha1(data.encode()).hexdigest()
        elif algorithm == 'sha256':
            return hashlib.sha256(data.encode()).hexdigest()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format."""
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(pattern, url))
    
    @staticmethod
    def extract_domain(email: str) -> Optional[str]:
        """Extract domain from email."""
        if '@' in email:
            return email.split('@')[1]
        return None


class TimeHelpers:
    """Time and date manipulation helpers."""
    
    @staticmethod
    def get_timestamp() -> str:
        """Get current timestamp in ISO format."""
        return datetime.utcnow().isoformat()
    
    @staticmethod
    def parse_timestamp(timestamp: str) -> Optional[datetime]:
        """Parse timestamp string to datetime object."""
        try:
            return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None
    
    @staticmethod
    def is_timestamp_valid(timestamp: str) -> bool:
        """Check if timestamp string is valid."""
        return TimeHelpers.parse_timestamp(timestamp) is not None
    
    @staticmethod
    def get_time_difference(start_time: str, end_time: str = None) -> timedelta:
        """Get time difference between timestamps."""
        if end_time is None:
            end_time = TimeHelpers.get_timestamp()
        
        start_dt = TimeHelpers.parse_timestamp(start_time)
        end_dt = TimeHelpers.parse_timestamp(end_time)
        
        if start_dt and end_dt:
            return end_dt - start_dt
        return timedelta(0)
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in seconds to human readable format."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        elif seconds < 86400:
            hours = seconds / 3600
            return f"{hours:.1f}h"
        else:
            days = seconds / 86400
            return f"{days:.1f}d"
    
    @staticmethod
    def is_expired(timestamp: str, expiry_hours: int = 24) -> bool:
        """Check if timestamp is expired."""
        if not TimeHelpers.is_timestamp_valid(timestamp):
            return True
        
        timestamp_dt = TimeHelpers.parse_timestamp(timestamp)
        expiry_time = timestamp_dt + timedelta(hours=expiry_hours)
        
        return datetime.utcnow() > expiry_time


class FileHelpers:
    """File and path manipulation helpers."""
    
    @staticmethod
    def ensure_directory(path: str) -> bool:
        """Ensure directory exists, create if not."""
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False
    
    @staticmethod
    def safe_write_file(file_path: str, content: str, encoding: str = 'utf-8') -> bool:
        """Safely write content to file."""
        try:
            # Ensure directory exists
            FileHelpers.ensure_directory(str(Path(file_path).parent))
            
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            return True
        except Exception:
            return False
    
    @staticmethod
    def safe_read_file(file_path: str, encoding: str = 'utf-8') -> Optional[str]:
        """Safely read content from file."""
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except Exception:
            return None
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """Get file size in bytes."""
        try:
            return Path(file_path).stat().st_size
        except Exception:
            return 0
    
    @staticmethod
    def file_exists(file_path: str) -> bool:
        """Check if file exists."""
        return Path(file_path).exists()
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """Delete file safely."""
        try:
            Path(file_path).unlink()
            return True
        except Exception:
            return False


class ValidationHelpers:
    """Data validation helpers."""
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
        """Validate required fields and return missing fields."""
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == "":
                missing_fields.append(field)
        return missing_fields
    
    @staticmethod
    def validate_field_types(data: Dict[str, Any], field_types: Dict[str, type]) -> List[str]:
        """Validate field types and return invalid fields."""
        invalid_fields = []
        for field, expected_type in field_types.items():
            if field in data and not isinstance(data[field], expected_type):
                invalid_fields.append(field)
        return invalid_fields
    
    @staticmethod
    def validate_string_length(data: Dict[str, Any], field_lengths: Dict[str, int]) -> List[str]:
        """Validate string field lengths and return invalid fields."""
        invalid_fields = []
        for field, max_length in field_lengths.items():
            if field in data and isinstance(data[field], str) and len(data[field]) > max_length:
                invalid_fields.append(field)
        return invalid_fields
    
    @staticmethod
    def validate_numeric_range(data: Dict[str, Any], field_ranges: Dict[str, tuple]) -> List[str]:
        """Validate numeric field ranges and return invalid fields."""
        invalid_fields = []
        for field, (min_val, max_val) in field_ranges.items():
            if field in data and isinstance(data[field], (int, float)):
                if not (min_val <= data[field] <= max_val):
                    invalid_fields.append(field)
        return invalid_fields


class PerformanceHelpers:
    """Performance monitoring and optimization helpers."""
    
    @staticmethod
    def measure_time(func):
        """Decorator to measure function execution time."""
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            print(f"Function {func.__name__} executed in {execution_time:.4f} seconds")
            return result
        return wrapper
    
    @staticmethod
    def create_timer() -> Dict[str, float]:
        """Create a timer for measuring multiple operations."""
        return {'start': time.time()}
    
    @staticmethod
    def mark_timer(timer: Dict[str, float], name: str):
        """Mark a point in the timer."""
        timer[name] = time.time()
    
    @staticmethod
    def get_timer_duration(timer: Dict[str, float], start_name: str, end_name: str) -> float:
        """Get duration between two timer marks."""
        if start_name in timer and end_name in timer:
            return timer[end_name] - timer[start_name]
        return 0.0
    
    @staticmethod
    def format_performance_metrics(metrics: Dict[str, float]) -> str:
        """Format performance metrics for display."""
        formatted = []
        for name, value in metrics.items():
            if name.endswith('_time'):
                formatted.append(f"{name}: {value:.4f}s")
            elif name.endswith('_count'):
                formatted.append(f"{name}: {int(value)}")
            else:
                formatted.append(f"{name}: {value}")
        return "\n".join(formatted)


class SecurityHelpers:
    """Security-related helper functions."""
    
    @staticmethod
    def mask_sensitive_data(data: Dict[str, Any], sensitive_fields: List[str] = None) -> Dict[str, Any]:
        """Mask sensitive data in dictionary."""
        if sensitive_fields is None:
            sensitive_fields = ['password', 'api_key', 'secret', 'token', 'key']
        
        masked_data = data.copy()
        
        for key, value in masked_data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_fields):
                if isinstance(value, str) and len(value) > 4:
                    masked_data[key] = value[:2] + "*" * (len(value) - 4) + value[-2:]
                else:
                    masked_data[key] = "***"
        
        return masked_data
    
    @staticmethod
    def validate_api_key_format(api_key: str) -> bool:
        """Validate API key format (basic validation)."""
        if not isinstance(api_key, str):
            return False
        
        # Basic format validation
        if len(api_key) < 10:
            return False
        
        # Check for common patterns
        if api_key.startswith('sk-') or api_key.startswith('AIza') or api_key.startswith('Bearer '):
            return True
        
        # Generic validation - alphanumeric with some special chars
        pattern = r'^[a-zA-Z0-9_\-\.]+$'
        return bool(re.match(pattern, api_key))
    
    @staticmethod
    def sanitize_input(data: Union[str, Dict[str, Any]]) -> Union[str, Dict[str, Any]]:
        """Sanitize input data for security."""
        if isinstance(data, str):
            return StringHelpers.sanitize_string(data)
        elif isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                if isinstance(value, str):
                    sanitized[key] = StringHelpers.sanitize_string(value)
                elif isinstance(value, dict):
                    sanitized[key] = SecurityHelpers.sanitize_input(value)
                else:
                    sanitized[key] = value
            return sanitized
        else:
            return data

