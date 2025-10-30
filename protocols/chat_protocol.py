"""
Chat Protocol Implementation

Defines ASI:One integration and chat protocols for the ASI system.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import json


class ChatMessageType(Enum):
    """Chat message types."""
    TEXT = "text"
    COMMAND = "command"
    QUERY = "query"
    RESPONSE = "response"
    ERROR = "error"
    SYSTEM = "system"


class ChatRole(Enum):
    """Chat participant roles."""
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"
    COORDINATOR = "coordinator"


@dataclass
class ChatMessage:
    """Chat message structure for ASI:One integration."""
    
    message_id: str
    chat_id: str
    sender_id: str
    sender_role: str
    message_type: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatMessage':
        """Create from dictionary."""
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ChatMessage':
        """Create from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def validate(self) -> bool:
        """Validate chat message structure."""
        required_fields = ['message_id', 'chat_id', 'sender_id', 'sender_role', 'message_type', 'content']
        return all(hasattr(self, field) and getattr(self, field) is not None 
                  for field in required_fields)


@dataclass
class ChatSession:
    """Chat session tracking."""
    
    chat_id: str
    participants: List[str]
    created_at: str
    last_activity: str
    is_active: bool
    messages: List[ChatMessage]
    session_metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatSession':
        """Create from dictionary."""
        return cls(**data)
    
    def add_message(self, message: ChatMessage) -> bool:
        """Add message to chat session."""
        try:
            self.messages.append(message)
            self.last_activity = datetime.utcnow().isoformat()
            return True
        except Exception:
            return False
    
    def get_messages_by_type(self, message_type: str) -> List[ChatMessage]:
        """Get messages filtered by type."""
        return [msg for msg in self.messages if msg.message_type == message_type]
    
    def get_messages_by_sender(self, sender_id: str) -> List[ChatMessage]:
        """Get messages filtered by sender."""
        return [msg for msg in self.messages if msg.sender_id == sender_id]


@dataclass
class ChatCommand:
    """Chat command structure."""
    
    command_id: str
    command_type: str
    parameters: Dict[str, Any]
    sender_id: str
    chat_id: str
    created_at: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatCommand':
        """Create from dictionary."""
        return cls(**data)
    
    def validate(self) -> bool:
        """Validate chat command structure."""
        required_fields = ['command_id', 'command_type', 'parameters', 'sender_id', 'chat_id']
        return all(hasattr(self, field) and getattr(self, field) is not None 
                  for field in required_fields)


@dataclass
class ASIOneIntegration:
    """ASI:One integration configuration."""
    
    integration_id: str
    api_endpoint: str
    authentication: Dict[str, Any]
    capabilities: List[str]
    is_active: bool
    created_at: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ASIOneIntegration':
        """Create from dictionary."""
        return cls(**data)


class ChatProtocol:
    """Chat Protocol handler with ASI:One integration utilities."""
    
    @staticmethod
    def create_chat_session(participants: List[str], metadata: Dict[str, Any] = None) -> ChatSession:
        """Create a new chat session."""
        chat_id = f"chat_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        current_time = datetime.utcnow().isoformat()
        
        return ChatSession(
            chat_id=chat_id,
            participants=participants,
            created_at=current_time,
            last_activity=current_time,
            is_active=True,
            messages=[],
            session_metadata=metadata or {}
        )
    
    @staticmethod
    def create_message(chat_id: str, sender_id: str, sender_role: str,
                      message_type: str, content: str, metadata: Dict[str, Any] = None) -> ChatMessage:
        """Create a chat message."""
        message_id = f"msg_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        
        return ChatMessage(
            message_id=message_id,
            chat_id=chat_id,
            sender_id=sender_id,
            sender_role=sender_role,
            message_type=message_type,
            content=content,
            metadata=metadata or {}
        )
    
    @staticmethod
    def create_command(command_type: str, parameters: Dict[str, Any],
                      sender_id: str, chat_id: str) -> ChatCommand:
        """Create a chat command."""
        command_id = f"cmd_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        
        return ChatCommand(
            command_id=command_id,
            command_type=command_type,
            parameters=parameters,
            sender_id=sender_id,
            chat_id=chat_id
        )
    
    @staticmethod
    def create_asi_one_integration(api_endpoint: str, authentication: Dict[str, Any],
                                 capabilities: List[str]) -> ASIOneIntegration:
        """Create ASI:One integration configuration."""
        integration_id = f"asi_one_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        
        return ASIOneIntegration(
            integration_id=integration_id,
            api_endpoint=api_endpoint,
            authentication=authentication,
            capabilities=capabilities,
            is_active=True
        )
    
    @staticmethod
    def validate_message_structure(data: Dict[str, Any]) -> bool:
        """Validate chat message structure."""
        required_fields = ['message_id', 'chat_id', 'sender_id', 'sender_role', 'message_type', 'content']
        return all(field in data for field in required_fields)
    
    @staticmethod
    def validate_command_structure(data: Dict[str, Any]) -> bool:
        """Validate chat command structure."""
        required_fields = ['command_id', 'command_type', 'parameters', 'sender_id', 'chat_id']
        return all(field in data for field in required_fields)
    
    @staticmethod
    def extract_commands_from_message(message: ChatMessage) -> List[ChatCommand]:
        """Extract commands from a chat message."""
        commands = []
        
        if message.message_type == ChatMessageType.COMMAND.value:
            # Parse command from content
            try:
                command_data = json.loads(message.content)
                command = ChatCommand.from_dict(command_data)
                if command.validate():
                    commands.append(command)
            except (json.JSONDecodeError, KeyError):
                pass
        
        return commands
    
    @staticmethod
    def format_agent_response(agent_id: str, response_content: str, 
                            metadata: Dict[str, Any] = None) -> ChatMessage:
        """Format agent response for chat."""
        return ChatMessage(
            message_id=f"msg_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}",
            chat_id="system",  # Will be set by caller
            sender_id=agent_id,
            sender_role=ChatRole.AGENT.value,
            message_type=ChatMessageType.RESPONSE.value,
            content=response_content,
            metadata=metadata or {}
        )
    
    @staticmethod
    def calculate_chat_metrics(session: ChatSession) -> Dict[str, Any]:
        """Calculate metrics for a chat session."""
        return {
            'chat_id': session.chat_id,
            'total_messages': len(session.messages),
            'participant_count': len(session.participants),
            'duration_minutes': _calculate_chat_duration(session.created_at, session.last_activity),
            'is_active': session.is_active,
            'message_types': _count_message_types(session.messages)
        }


def _calculate_chat_duration(start_time: str, end_time: str) -> float:
    """Calculate duration in minutes between two timestamps."""
    try:
        start_dt = datetime.fromisoformat(start_time)
        end_dt = datetime.fromisoformat(end_time)
        duration = end_dt - start_dt
        return duration.total_seconds() / 60
    except (ValueError, TypeError):
        return 0.0


def _count_message_types(messages: List[ChatMessage]) -> Dict[str, int]:
    """Count messages by type."""
    type_counts = {}
    for message in messages:
        msg_type = message.message_type
        type_counts[msg_type] = type_counts.get(msg_type, 0) + 1
    return type_counts

