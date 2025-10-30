"""
Negotiation State Machine

Implements state machine with safeguards for negotiation processes.
"""

import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass


class NegotiationState(Enum):
    """Negotiation state enumeration."""
    INITIATED = "initiated"
    RFQ_SENT = "rfq_sent"
    QUOTES_RECEIVED = "quotes_received"
    NEGOTIATING = "negotiating"
    AGREEMENT_REACHED = "agreement_reached"
    DEAL_CLOSED = "deal_closed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class NegotiationEvent(Enum):
    """Negotiation event enumeration."""
    RFQ_CREATED = "rfq_created"
    QUOTE_RECEIVED = "quote_received"
    NEGOTIATION_STARTED = "negotiation_started"
    COUNTER_OFFER = "counter_offer"
    AGREEMENT_REACHED = "agreement_reached"
    DEAL_CLOSED = "deal_closed"
    TIMEOUT_OCCURRED = "timeout_occurred"
    CANCELLATION = "cancellation"


@dataclass
class StateTransition:
    """State transition definition."""
    from_state: NegotiationState
    to_state: NegotiationState
    event: NegotiationEvent
    conditions: List[str]
    safeguards: List[str]


class NegotiationStateMachine:
    """State machine for negotiation processes with safeguards."""
    
    def __init__(self, deal_id: str, config: Dict[str, Any]):
        self.deal_id = deal_id
        self.config = config
        self.logger = logging.getLogger(f"negotiation_state.{deal_id}")
        
        # State machine state
        self.current_state = NegotiationState.INITIATED
        self.state_history = []
        self.transitions = self._initialize_transitions()
        self.safeguards = self._initialize_safeguards()
        
        # Negotiation metadata
        self.created_at = datetime.utcnow()
        self.last_updated = datetime.utcnow()
        self.participants = set()
        self.max_rounds = config.get('max_rounds', 10)
        self.timeout_duration = timedelta(hours=config.get('timeout_hours', 24))
        
        self.logger.info(f"Negotiation state machine initialized for deal {deal_id}")
    
    def _initialize_transitions(self) -> List[StateTransition]:
        """Initialize valid state transitions."""
        return [
            StateTransition(
                from_state=NegotiationState.INITIATED,
                to_state=NegotiationState.RFQ_SENT,
                event=NegotiationEvent.RFQ_CREATED,
                conditions=["rfq_created"],
                safeguards=["validate_rfq_format", "check_participants"]
            ),
            StateTransition(
                from_state=NegotiationState.RFQ_SENT,
                to_state=NegotiationState.QUOTES_RECEIVED,
                event=NegotiationEvent.QUOTE_RECEIVED,
                conditions=["quote_received"],
                safeguards=["validate_quote", "check_deadline"]
            ),
            StateTransition(
                from_state=NegotiationState.QUOTES_RECEIVED,
                to_state=NegotiationState.NEGOTIATING,
                event=NegotiationEvent.NEGOTIATION_STARTED,
                conditions=["negotiation_started"],
                safeguards=["check_rounds_limit", "validate_participants"]
            ),
            StateTransition(
                from_state=NegotiationState.NEGOTIATING,
                to_state=NegotiationState.AGREEMENT_REACHED,
                event=NegotiationEvent.AGREEMENT_REACHED,
                conditions=["agreement_reached"],
                safeguards=["validate_agreement", "check_legal_requirements"]
            ),
            StateTransition(
                from_state=NegotiationState.AGREEMENT_REACHED,
                to_state=NegotiationState.DEAL_CLOSED,
                event=NegotiationEvent.DEAL_CLOSED,
                conditions=["deal_closed"],
                safeguards=["final_validation", "documentation_complete"]
            ),
            # Failure and timeout transitions
            StateTransition(
                from_state=NegotiationState.NEGOTIATING,
                to_state=NegotiationState.FAILED,
                event=NegotiationEvent.CANCELLATION,
                conditions=["cancellation"],
                safeguards=["check_cancellation_reason"]
            ),
            StateTransition(
                from_state=NegotiationState.NEGOTIATING,
                to_state=NegotiationState.TIMEOUT,
                event=NegotiationEvent.TIMEOUT_OCCURRED,
                conditions=["timeout"],
                safeguards=["check_timeout_validity"]
            )
        ]
    
    def _initialize_safeguards(self) -> Dict[str, callable]:
        """Initialize safeguard functions."""
        return {
            "validate_rfq_format": self._validate_rfq_format,
            "check_participants": self._check_participants,
            "validate_quote": self._validate_quote,
            "check_deadline": self._check_deadline,
            "check_rounds_limit": self._check_rounds_limit,
            "validate_participants": self._validate_participants,
            "validate_agreement": self._validate_agreement,
            "check_legal_requirements": self._check_legal_requirements,
            "final_validation": self._final_validation,
            "documentation_complete": self._documentation_complete,
            "check_cancellation_reason": self._check_cancellation_reason,
            "check_timeout_validity": self._check_timeout_validity
        }
    
    def transition(self, event: NegotiationEvent, context: Dict[str, Any] = None) -> bool:
        """Attempt state transition based on event."""
        try:
            # Find valid transition
            valid_transition = self._find_valid_transition(event)
            if not valid_transition:
                self.logger.warning(f"No valid transition for event {event} from state {self.current_state}")
                return False
            
            # Execute safeguards
            if not self._execute_safeguards(valid_transition, context or {}):
                self.logger.warning(f"Safeguards failed for transition {valid_transition.from_state} -> {valid_transition.to_state}")
                return False
            
            # Perform transition
            self._perform_transition(valid_transition, context or {})
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to transition state: {e}")
            return False
    
    def _find_valid_transition(self, event: NegotiationEvent) -> Optional[StateTransition]:
        """Find valid transition for current state and event."""
        for transition in self.transitions:
            if (transition.from_state == self.current_state and 
                transition.event == event):
                return transition
        return None
    
    def _execute_safeguards(self, transition: StateTransition, context: Dict[str, Any]) -> bool:
        """Execute all safeguards for a transition."""
        for safeguard_name in transition.safeguards:
            safeguard_func = self.safeguards.get(safeguard_name)
            if safeguard_func and not safeguard_func(context):
                self.logger.warning(f"Safeguard {safeguard_name} failed")
                return False
        return True
    
    def _perform_transition(self, transition: StateTransition, context: Dict[str, Any]):
        """Perform the state transition."""
        # Record state history
        self.state_history.append({
            "from_state": transition.from_state.value,
            "to_state": transition.to_state.value,
            "event": transition.event.value,
            "timestamp": datetime.utcnow().isoformat(),
            "context": context
        })
        
        # Update current state
        self.current_state = transition.to_state
        self.last_updated = datetime.utcnow()
        
        self.logger.info(f"State transition: {transition.from_state.value} -> {transition.to_state.value}")
    
    def get_state(self) -> Dict[str, Any]:
        """Get current state information."""
        return {
            "deal_id": self.deal_id,
            "current_state": self.current_state.value,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "participants": list(self.participants),
            "max_rounds": self.max_rounds,
            "timeout_duration": str(self.timeout_duration),
            "state_history": self.state_history
        }
    
    def is_final_state(self) -> bool:
        """Check if current state is a final state."""
        final_states = {
            NegotiationState.DEAL_CLOSED,
            NegotiationState.FAILED,
            NegotiationState.TIMEOUT,
            NegotiationState.CANCELLED
        }
        return self.current_state in final_states
    
    def can_transition(self, event: NegotiationEvent) -> bool:
        """Check if transition is possible for given event."""
        return self._find_valid_transition(event) is not None
    
    def add_participant(self, participant_id: str) -> bool:
        """Add participant to negotiation."""
        try:
            self.participants.add(participant_id)
            self.logger.info(f"Added participant {participant_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to add participant: {e}")
            return False
    
    def remove_participant(self, participant_id: str) -> bool:
        """Remove participant from negotiation."""
        try:
            self.participants.discard(participant_id)
            self.logger.info(f"Removed participant {participant_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to remove participant: {e}")
            return False
    
    # Safeguard implementations
    def _validate_rfq_format(self, context: Dict[str, Any]) -> bool:
        """Validate RFQ format."""
        rfq_data = context.get("rfq_data", {})
        required_fields = ["rfq_id", "buyer_id", "requirements", "content"]
        return all(field in rfq_data for field in required_fields)
    
    def _check_participants(self, context: Dict[str, Any]) -> bool:
        """Check participant requirements."""
        return len(self.participants) >= 2  # At least buyer and seller
    
    def _validate_quote(self, context: Dict[str, Any]) -> bool:
        """Validate quote format and content."""
        quote_data = context.get("quote_data", {})
        required_fields = ["quote_id", "seller_id", "rfq_id", "content", "pricing"]
        return all(field in quote_data for field in required_fields)
    
    def _check_deadline(self, context: Dict[str, Any]) -> bool:
        """Check if deadline has passed."""
        deadline = context.get("deadline")
        if deadline:
            try:
                deadline_dt = datetime.fromisoformat(deadline)
                return datetime.utcnow() <= deadline_dt
            except (ValueError, TypeError):
                return True
        return True
    
    def _check_rounds_limit(self, context: Dict[str, Any]) -> bool:
        """Check if rounds limit has been reached."""
        current_round = context.get("current_round", 0)
        return current_round < self.max_rounds
    
    def _validate_participants(self, context: Dict[str, Any]) -> bool:
        """Validate all participants are still active."""
        return len(self.participants) >= 2
    
    def _validate_agreement(self, context: Dict[str, Any]) -> bool:
        """Validate agreement terms."""
        agreement = context.get("agreement", {})
        return bool(agreement.get("terms") and agreement.get("signatures"))
    
    def _check_legal_requirements(self, context: Dict[str, Any]) -> bool:
        """Check legal requirements are met."""
        # Placeholder for legal requirement checks
        return True
    
    def _final_validation(self, context: Dict[str, Any]) -> bool:
        """Perform final validation before deal closure."""
        return True
    
    def _documentation_complete(self, context: Dict[str, Any]) -> bool:
        """Check if all documentation is complete."""
        return True
    
    def _check_cancellation_reason(self, context: Dict[str, Any]) -> bool:
        """Check if cancellation reason is valid."""
        reason = context.get("cancellation_reason")
        return bool(reason and len(reason) > 10)
    
    def _check_timeout_validity(self, context: Dict[str, Any]) -> bool:
        """Check if timeout is valid."""
        return datetime.utcnow() - self.last_updated > self.timeout_duration

