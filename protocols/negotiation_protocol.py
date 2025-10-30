"""
Negotiation Protocol Implementation

Defines multi-round bidding and negotiation protocols for the ASI system.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import json


class NegotiationStatus(Enum):
    """Negotiation status enumeration."""
    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class NegotiationRound(Enum):
    """Negotiation round types."""
    INITIAL = "initial"
    COUNTER_OFFER = "counter_offer"
    FINAL = "final"


@dataclass
class NegotiationMessage:
    """Negotiation message structure."""
    
    negotiation_id: str
    sender_id: str
    receiver_id: str
    round_type: str
    content: str
    offer: Optional[Dict[str, Any]] = None
    constraints: Optional[Dict[str, Any]] = None
    deadline: Optional[str] = None
    created_at: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NegotiationMessage':
        """Create from dictionary."""
        return cls(**data)
    
    def validate(self) -> bool:
        """Validate negotiation message structure."""
        required_fields = ['negotiation_id', 'sender_id', 'receiver_id', 'round_type', 'content']
        return all(hasattr(self, field) and getattr(self, field) is not None 
                  for field in required_fields)


@dataclass
class NegotiationSession:
    """Negotiation session tracking."""
    
    negotiation_id: str
    participants: List[str]
    status: str
    current_round: int
    max_rounds: int
    created_at: str
    updated_at: str
    messages: List[NegotiationMessage]
    final_agreement: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NegotiationSession':
        """Create from dictionary."""
        return cls(**data)
    
    def add_message(self, message: NegotiationMessage) -> bool:
        """Add message to negotiation session."""
        try:
            self.messages.append(message)
            self.updated_at = datetime.utcnow().isoformat()
            return True
        except Exception:
            return False
    
    def is_complete(self) -> bool:
        """Check if negotiation is complete."""
        return (self.status == NegotiationStatus.COMPLETED.value or 
                self.status == NegotiationStatus.FAILED.value or
                self.status == NegotiationStatus.TIMEOUT.value or
                self.current_round >= self.max_rounds)
    
    def get_latest_message(self) -> Optional[NegotiationMessage]:
        """Get the latest message in the negotiation."""
        if self.messages:
            return self.messages[-1]
        return None


@dataclass
class NegotiationStrategy:
    """Negotiation strategy configuration."""
    
    strategy_id: str
    name: str
    parameters: Dict[str, Any]
    rules: List[Dict[str, Any]]
    created_at: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NegotiationStrategy':
        """Create from dictionary."""
        return cls(**data)


class NegotiationProtocol:
    """Negotiation Protocol handler with session management and utilities."""
    
    @staticmethod
    def create_negotiation(participants: List[str], max_rounds: int = 10) -> NegotiationSession:
        """Create a new negotiation session."""
        negotiation_id = f"neg_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        
        return NegotiationSession(
            negotiation_id=negotiation_id,
            participants=participants,
            status=NegotiationStatus.INITIATED.value,
            current_round=0,
            max_rounds=max_rounds,
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
            messages=[]
        )
    
    @staticmethod
    def create_message(negotiation_id: str, sender_id: str, receiver_id: str,
                      round_type: str, content: str, offer: Dict[str, Any] = None,
                      constraints: Dict[str, Any] = None, deadline: str = None) -> NegotiationMessage:
        """Create a negotiation message."""
        return NegotiationMessage(
            negotiation_id=negotiation_id,
            sender_id=sender_id,
            receiver_id=receiver_id,
            round_type=round_type,
            content=content,
            offer=offer,
            constraints=constraints,
            deadline=deadline
        )
    
    @staticmethod
    def create_strategy(strategy_id: str, name: str, parameters: Dict[str, Any],
                       rules: List[Dict[str, Any]]) -> NegotiationStrategy:
        """Create a negotiation strategy."""
        return NegotiationStrategy(
            strategy_id=strategy_id,
            name=name,
            parameters=parameters,
            rules=rules
        )
    
    @staticmethod
    def validate_message_structure(data: Dict[str, Any]) -> bool:
        """Validate negotiation message structure."""
        required_fields = ['negotiation_id', 'sender_id', 'receiver_id', 'round_type', 'content']
        return all(field in data for field in required_fields)
    
    @staticmethod
    def validate_session_structure(data: Dict[str, Any]) -> bool:
        """Validate negotiation session structure."""
        required_fields = ['negotiation_id', 'participants', 'status', 'current_round', 'max_rounds']
        return all(field in data for field in required_fields)
    
    @staticmethod
    def calculate_negotiation_metrics(session: NegotiationSession) -> Dict[str, Any]:
        """Calculate metrics for a negotiation session."""
        return {
            'negotiation_id': session.negotiation_id,
            'total_messages': len(session.messages),
            'rounds_completed': session.current_round,
            'duration_minutes': _calculate_duration(session.created_at, session.updated_at),
            'participant_count': len(session.participants),
            'status': session.status
        }
    
    @staticmethod
    def extract_offer_terms(message: NegotiationMessage) -> Dict[str, Any]:
        """Extract offer terms from a negotiation message."""
        if not message.offer:
            return {}
        
        return {
            'price': message.offer.get('price'),
            'quantity': message.offer.get('quantity'),
            'delivery': message.offer.get('delivery'),
            'terms': message.offer.get('terms'),
            'conditions': message.offer.get('conditions')
        }


def _calculate_duration(start_time: str, end_time: str) -> float:
    """Calculate duration in minutes between two timestamps."""
    try:
        start_dt = datetime.fromisoformat(start_time)
        end_dt = datetime.fromisoformat(end_time)
        duration = end_dt - start_dt
        return duration.total_seconds() / 60
    except (ValueError, TypeError):
        return 0.0

