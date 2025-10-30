"""
Message Validator

Concise message enforcement for ASI system communications.
"""

import logging
import json
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from enum import Enum


class MessageType(Enum):
    """Message type enumeration."""
    RFQ = "rfq"
    QUOTE = "quote"
    NEGOTIATION = "negotiation"
    CHAT = "chat"
    SYSTEM = "system"
    ERROR = "error"


class ValidationLevel(Enum):
    """Validation level enumeration."""
    STRICT = "strict"
    MODERATE = "moderate"
    LENIENT = "lenient"


class MessageValidator:
    """Message validator with configurable validation levels."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("message_validator")
        
        # Validation configuration
        self.validation_level = ValidationLevel(config.get('validation_level', 'moderate'))
        self.required_fields = self._initialize_required_fields()
        self.field_validators = self._initialize_field_validators()
        self.message_schemas = self._initialize_message_schemas()
        
        self.logger.info(f"MessageValidator initialized with level: {self.validation_level.value}")
    
    def _initialize_required_fields(self) -> Dict[str, List[str]]:
        """Initialize required fields for each message type."""
        return {
            MessageType.RFQ.value: ["rfq_id", "buyer_id", "requirements", "content"],
            MessageType.QUOTE.value: ["quote_id", "seller_id", "rfq_id", "content", "pricing"],
            MessageType.NEGOTIATION.value: ["negotiation_id", "sender_id", "receiver_id", "content"],
            MessageType.CHAT.value: ["message_id", "chat_id", "sender_id", "content"],
            MessageType.SYSTEM.value: ["message_id", "type", "content"],
            MessageType.ERROR.value: ["error_id", "type", "message"]
        }
    
    def _initialize_field_validators(self) -> Dict[str, callable]:
        """Initialize field validation functions."""
        return {
            "rfq_id": self._validate_rfq_id,
            "quote_id": self._validate_quote_id,
            "negotiation_id": self._validate_negotiation_id,
            "message_id": self._validate_message_id,
            "buyer_id": self._validate_agent_id,
            "seller_id": self._validate_agent_id,
            "sender_id": self._validate_agent_id,
            "receiver_id": self._validate_agent_id,
            "content": self._validate_content,
            "pricing": self._validate_pricing,
            "requirements": self._validate_requirements,
            "timestamp": self._validate_timestamp
        }
    
    def _initialize_message_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Initialize message schemas for validation."""
        return {
            MessageType.RFQ.value: {
                "type": "object",
                "properties": {
                    "rfq_id": {"type": "string", "pattern": r"^rfq_\d{8}_\d{6}_\d+$"},
                    "buyer_id": {"type": "string", "minLength": 1},
                    "requirements": {"type": "object"},
                    "content": {"type": "string", "minLength": 10},
                    "deadline": {"type": "string", "format": "date-time"},
                    "policies": {"type": "object"}
                },
                "required": ["rfq_id", "buyer_id", "requirements", "content"]
            },
            MessageType.QUOTE.value: {
                "type": "object",
                "properties": {
                    "quote_id": {"type": "string", "pattern": r"^quote_\d{8}_\d{6}_\d+$"},
                    "seller_id": {"type": "string", "minLength": 1},
                    "rfq_id": {"type": "string", "pattern": r"^rfq_\d{8}_\d{6}_\d+$"},
                    "content": {"type": "string", "minLength": 10},
                    "pricing": {"type": "object"},
                    "validity_period": {"type": "string", "format": "date-time"}
                },
                "required": ["quote_id", "seller_id", "rfq_id", "content", "pricing"]
            },
            MessageType.NEGOTIATION.value: {
                "type": "object",
                "properties": {
                    "negotiation_id": {"type": "string", "pattern": r"^neg_\d{8}_\d{6}_\d+$"},
                    "sender_id": {"type": "string", "minLength": 1},
                    "receiver_id": {"type": "string", "minLength": 1},
                    "content": {"type": "string", "minLength": 5},
                    "offer": {"type": "object"},
                    "constraints": {"type": "object"}
                },
                "required": ["negotiation_id", "sender_id", "receiver_id", "content"]
            }
        }
    
    def validate(self, message: Dict[str, Any]) -> bool:
        """Validate message structure and content."""
        try:
            # Check if message has required type field
            if "type" not in message:
                self.logger.error("Message missing type field")
                return False
            
            message_type = message["type"]
            
            # Validate message type
            if not self._validate_message_type(message_type):
                return False
            
            # Validate required fields
            if not self._validate_required_fields(message, message_type):
                return False
            
            # Validate field formats
            if not self._validate_field_formats(message, message_type):
                return False
            
            # Validate business rules
            if not self._validate_business_rules(message, message_type):
                return False
            
            self.logger.debug(f"Message validation successful for type: {message_type}")
            return True
            
        except Exception as e:
            self.logger.error(f"Message validation failed: {e}")
            return False
    
    def _validate_message_type(self, message_type: str) -> bool:
        """Validate message type is supported."""
        valid_types = [t.value for t in MessageType]
        if message_type not in valid_types:
            self.logger.error(f"Invalid message type: {message_type}")
            return False
        return True
    
    def _validate_required_fields(self, message: Dict[str, Any], message_type: str) -> bool:
        """Validate all required fields are present."""
        required_fields = self.required_fields.get(message_type, [])
        
        for field in required_fields:
            if field not in message:
                self.logger.error(f"Missing required field: {field}")
                return False
        
        return True
    
    def _validate_field_formats(self, message: Dict[str, Any], message_type: str) -> bool:
        """Validate field formats and types."""
        for field, value in message.items():
            validator = self.field_validators.get(field)
            if validator and not validator(value):
                self.logger.error(f"Invalid format for field {field}: {value}")
                return False
        
        return True
    
    def _validate_business_rules(self, message: Dict[str, Any], message_type: str) -> bool:
        """Validate business rules for message type."""
        if message_type == MessageType.RFQ.value:
            return self._validate_rfq_business_rules(message)
        elif message_type == MessageType.QUOTE.value:
            return self._validate_quote_business_rules(message)
        elif message_type == MessageType.NEGOTIATION.value:
            return self._validate_negotiation_business_rules(message)
        
        return True
    
    def _validate_rfq_business_rules(self, message: Dict[str, Any]) -> bool:
        """Validate RFQ business rules."""
        # Check deadline is in the future
        deadline = message.get("deadline")
        if deadline:
            try:
                deadline_dt = datetime.fromisoformat(deadline)
                if datetime.utcnow() >= deadline_dt:
                    self.logger.error("RFQ deadline is in the past")
                    return False
            except (ValueError, TypeError):
                self.logger.error("Invalid deadline format")
                return False
        
        # Check requirements are not empty
        requirements = message.get("requirements", {})
        if not requirements or len(requirements) == 0:
            self.logger.error("RFQ requirements cannot be empty")
            return False
        
        return True
    
    def _validate_quote_business_rules(self, message: Dict[str, Any]) -> bool:
        """Validate quote business rules."""
        # Check pricing is valid
        pricing = message.get("pricing", {})
        if not pricing or not isinstance(pricing, dict):
            self.logger.error("Quote pricing must be a valid object")
            return False
        
        # Check validity period is in the future
        validity_period = message.get("validity_period")
        if validity_period:
            try:
                validity_dt = datetime.fromisoformat(validity_period)
                if datetime.utcnow() >= validity_dt:
                    self.logger.error("Quote validity period is in the past")
                    return False
            except (ValueError, TypeError):
                self.logger.error("Invalid validity period format")
                return False
        
        return True
    
    def _validate_negotiation_business_rules(self, message: Dict[str, Any]) -> bool:
        """Validate negotiation business rules."""
        # Check sender and receiver are different
        sender_id = message.get("sender_id")
        receiver_id = message.get("receiver_id")
        if sender_id == receiver_id:
            self.logger.error("Negotiation sender and receiver cannot be the same")
            return False
        
        return True
    
    # Field validation functions
    def _validate_rfq_id(self, value: Any) -> bool:
        """Validate RFQ ID format."""
        if not isinstance(value, str):
            return False
        import re
        pattern = r"^rfq_\d{8}_\d{6}_\d+$"
        return bool(re.match(pattern, value))
    
    def _validate_quote_id(self, value: Any) -> bool:
        """Validate quote ID format."""
        if not isinstance(value, str):
            return False
        import re
        pattern = r"^quote_\d{8}_\d{6}_\d+$"
        return bool(re.match(pattern, value))
    
    def _validate_negotiation_id(self, value: Any) -> bool:
        """Validate negotiation ID format."""
        if not isinstance(value, str):
            return False
        import re
        pattern = r"^neg_\d{8}_\d{6}_\d+$"
        return bool(re.match(pattern, value))
    
    def _validate_message_id(self, value: Any) -> bool:
        """Validate message ID format."""
        if not isinstance(value, str):
            return False
        import re
        pattern = r"^msg_\d{8}_\d{6}_\d+$"
        return bool(re.match(pattern, value))
    
    def _validate_agent_id(self, value: Any) -> bool:
        """Validate agent ID format."""
        return isinstance(value, str) and len(value) > 0
    
    def _validate_content(self, value: Any) -> bool:
        """Validate content field."""
        return isinstance(value, str) and len(value) >= 5
    
    def _validate_pricing(self, value: Any) -> bool:
        """Validate pricing field."""
        return isinstance(value, dict) and len(value) > 0
    
    def _validate_requirements(self, value: Any) -> bool:
        """Validate requirements field."""
        return isinstance(value, dict) and len(value) > 0
    
    def _validate_timestamp(self, value: Any) -> bool:
        """Validate timestamp format."""
        if not isinstance(value, str):
            return False
        try:
            datetime.fromisoformat(value)
            return True
        except (ValueError, TypeError):
            return False
    
    def get_validation_errors(self, message: Dict[str, Any]) -> List[str]:
        """Get detailed validation errors for a message."""
        errors = []
        
        try:
            # Check message type
            if "type" not in message:
                errors.append("Missing required field: type")
                return errors
            
            message_type = message["type"]
            
            # Check required fields
            required_fields = self.required_fields.get(message_type, [])
            for field in required_fields:
                if field not in message:
                    errors.append(f"Missing required field: {field}")
            
            # Check field formats
            for field, value in message.items():
                validator = self.field_validators.get(field)
                if validator and not validator(value):
                    errors.append(f"Invalid format for field {field}: {value}")
            
        except Exception as e:
            errors.append(f"Validation error: {e}")
        
        return errors
    
    def sanitize_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize message content for security."""
        sanitized = message.copy()
        
        # Remove potentially dangerous fields
        dangerous_fields = ["script", "javascript", "eval", "exec"]
        for field in dangerous_fields:
            if field in sanitized:
                del sanitized[field]
        
        # Sanitize content fields
        if "content" in sanitized:
            sanitized["content"] = self._sanitize_content(sanitized["content"])
        
        return sanitized
    
    def _sanitize_content(self, content: str) -> str:
        """Sanitize content string."""
        # Remove HTML tags
        import re
        content = re.sub(r'<[^>]+>', '', content)
        
        # Remove script tags
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
        
        # Limit length
        max_length = self.config.get('max_content_length', 10000)
        if len(content) > max_length:
            content = content[:max_length]
        
        return content

