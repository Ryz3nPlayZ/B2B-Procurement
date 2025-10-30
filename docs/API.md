# ASI System API Reference

## Overview

This document provides a comprehensive API reference for the ASI (Autonomous System Intelligence) system. The API covers agent interactions, message protocols, and system operations.

## Agent API

### BaseAgent

Base class for all ASI agents with shared functionality.

#### Methods

##### `__init__(agent_id: str, config: Dict[str, Any])`
Initialize agent with ID and configuration.

**Parameters:**
- `agent_id`: Unique agent identifier
- `config`: Agent configuration dictionary

##### `process_message(message: Dict[str, Any]) -> Dict[str, Any]`
Process incoming message and return response.

**Parameters:**
- `message`: Message dictionary with type and content

**Returns:**
- Response dictionary with type and result

**Example:**
```python
message = {
    "type": "rfq_request",
    "requirements": {"product": "sensors", "quantity": 100}
}
response = agent.process_message(message)
```

##### `get_capabilities() -> Dict[str, Any]`
Return agent capabilities and metadata.

**Returns:**
- Dictionary with agent capabilities and status

##### `start_deal(deal_id: str, deal_data: Dict[str, Any]) -> bool`
Start a new deal negotiation.

**Parameters:**
- `deal_id`: Unique deal identifier
- `deal_data`: Deal configuration and requirements

**Returns:**
- Boolean indicating success

##### `end_deal(deal_id: str, final_state: Dict[str, Any]) -> bool`
End current deal and save final state.

**Parameters:**
- `deal_id`: Deal identifier
- `final_state`: Final deal state and outcomes

**Returns:**
- Boolean indicating success

### BuyerAgent

Buyer agent for procurement operations.

#### Methods

##### `process_message(message: Dict[str, Any]) -> Dict[str, Any]`
Process buyer-specific messages.

**Message Types:**
- `rfq_request`: Create new RFQ
- `quote`: Process received quote
- `negotiation`: Handle negotiation messages

**Example RFQ Request:**
```python
rfq_message = {
    "type": "rfq_request",
    "requirements": {
        "product": "Industrial Sensors",
        "quantity": 100,
        "specifications": "High precision",
        "quality_standards": "ISO 9001"
    },
    "deadline": "2024-12-31T23:59:59Z"
}
```

**Example Quote Response:**
```python
quote_message = {
    "type": "quote",
    "quote_id": "quote_123",
    "seller_id": "seller_001",
    "rfq_id": "rfq_123",
    "content": "Quote content",
    "pricing": {"total": 1000, "currency": "USD"}
}
```

### SellerAgent

Seller agent for sales operations.

#### Methods

##### `process_message(message: Dict[str, Any]) -> Dict[str, Any]`
Process seller-specific messages.

**Message Types:**
- `rfq`: Process RFQ and generate quote
- `negotiation`: Handle negotiation messages
- `inventory_update`: Update inventory information

**Example RFQ Processing:**
```python
rfq_message = {
    "type": "rfq",
    "rfq_id": "rfq_123",
    "buyer_id": "buyer_001",
    "requirements": {"product": "sensors", "quantity": 100},
    "content": "RFQ content"
}
```

### CoordinatorAgent

Central coordinator for system management.

#### Methods

##### `process_message(message: Dict[str, Any]) -> Dict[str, Any]`
Process coordinator messages.

**Message Types:**
- `agent_register`: Register new agent
- `agent_discover`: Discover agents by criteria
- `route_message`: Route message to agent
- `system_status`: Get system status
- `health_check`: Perform health check

**Example Agent Registration:**
```python
register_message = {
    "type": "agent_register",
    "agent": {
        "id": "buyer_001",
        "type": "buyer",
        "capabilities": ["rfq_generation", "quote_evaluation"]
    }
}
```

## Protocol APIs

### RFQ Protocol

Request for Quote message structures.

#### RFQMessage

```python
@dataclass
class RFQMessage:
    rfq_id: str
    buyer_id: str
    requirements: Dict[str, Any]
    content: str
    deadline: Optional[str] = None
    policies: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
```

#### Methods

##### `to_dict() -> Dict[str, Any]`
Convert RFQ to dictionary.

##### `from_dict(data: Dict[str, Any]) -> RFQMessage`
Create RFQ from dictionary.

##### `validate() -> bool`
Validate RFQ structure.

##### `is_expired() -> bool`
Check if RFQ has expired.

### Quote Protocol

Quote and response structures.

#### QuoteMessage

```python
@dataclass
class QuoteMessage:
    quote_id: str
    seller_id: str
    rfq_id: str
    content: str
    pricing: Dict[str, Any]
    validity_period: Optional[str] = None
    terms_conditions: Optional[Dict[str, Any]] = None
    certifications: Optional[List[str]] = None
    created_at: Optional[str] = None
```

#### Methods

##### `to_dict() -> Dict[str, Any]`
Convert quote to dictionary.

##### `from_dict(data: Dict[str, Any]) -> QuoteMessage`
Create quote from dictionary.

##### `validate() -> bool`
Validate quote structure.

##### `get_total_price() -> float`
Get total price from pricing data.

### Negotiation Protocol

Multi-round negotiation structures.

#### NegotiationMessage

```python
@dataclass
class NegotiationMessage:
    negotiation_id: str
    sender_id: str
    receiver_id: str
    round_type: str
    content: str
    offer: Optional[Dict[str, Any]] = None
    constraints: Optional[Dict[str, Any]] = None
    deadline: Optional[str] = None
    created_at: Optional[str] = None
```

#### NegotiationSession

```python
@dataclass
class NegotiationSession:
    negotiation_id: str
    participants: List[str]
    status: str
    current_round: int
    max_rounds: int
    created_at: str
    updated_at: str
    messages: List[NegotiationMessage]
    final_agreement: Optional[Dict[str, Any]] = None
```

### Chat Protocol

ASI:One integration structures.

#### ChatMessage

```python
@dataclass
class ChatMessage:
    message_id: str
    chat_id: str
    sender_id: str
    sender_role: str
    message_type: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None
```

## Core System APIs

### NegotiationStateMachine

State machine for negotiation processes.

#### Methods

##### `__init__(deal_id: str, config: Dict[str, Any])`
Initialize state machine.

##### `transition(event: NegotiationEvent, context: Dict[str, Any] = None) -> bool`
Attempt state transition.

##### `get_state() -> Dict[str, Any]`
Get current state information.

##### `is_final_state() -> bool`
Check if current state is final.

##### `can_transition(event: NegotiationEvent) -> bool`
Check if transition is possible.

### MessageValidator

Message validation and enforcement.

#### Methods

##### `__init__(config: Dict[str, Any])`
Initialize validator.

##### `validate(message: Dict[str, Any]) -> bool`
Validate message structure.

##### `get_validation_errors(message: Dict[str, Any]) -> List[str]`
Get detailed validation errors.

##### `sanitize_message(message: Dict[str, Any]) -> Dict[str, Any]`
Sanitize message content.

### DealFile

Persistent deal state management.

#### Methods

##### `__init__(deal_id: str, initial_data: Dict[str, Any] = None)`
Initialize deal file.

##### `add_participant(participant_id: str, role: str, metadata: Dict[str, Any] = None) -> bool`
Add participant to deal.

##### `add_message(message: Dict[str, Any]) -> bool`
Add message to deal history.

##### `add_negotiation_round(round_data: Dict[str, Any]) -> bool`
Add negotiation round.

##### `update_status(status: str, reason: str = None) -> bool`
Update deal status.

##### `get_deal_data() -> Dict[str, Any]`
Get complete deal data.

### OfferScorer

Offer evaluation and scoring.

#### Methods

##### `__init__(config: Dict[str, Any])`
Initialize scorer.

##### `score_offer(offer_data: Dict[str, Any]) -> ScoreResult`
Score an offer.

##### `compare_offers(offers: List[Dict[str, Any]]) -> List[Tuple[Dict[str, Any], ScoreResult]]`
Compare multiple offers.

##### `get_scoring_criteria() -> List[Dict[str, Any]]`
Get scoring criteria information.

## LLM Integration APIs

### LLMRouter

Smart LLM model selection and routing.

#### Methods

##### `__init__(config: Dict[str, Any])`
Initialize router.

##### `get_response(prompt: str, model_preference: str = None, context: Dict[str, Any] = None) -> str`
Get LLM response.

##### `get_model_status() -> Dict[str, Any]`
Get status of all models.

##### `get_usage_stats() -> Dict[str, Any]`
Get usage statistics.

### Provider Clients

#### OpenRouterClient

```python
class OpenRouterClient:
    def __init__(self, config: Dict[str, Any])
    def generate(self, request_data: Dict[str, Any]) -> str
    def get_available_models(self) -> List[Dict[str, Any]]
    def estimate_cost(self, prompt: str, model: str = None) -> Dict[str, Any]
```

#### GeminiClient

```python
class GeminiClient:
    def __init__(self, config: Dict[str, Any])
    def generate(self, request_data: Dict[str, Any]) -> str
    def generate_with_vision(self, prompt: str, image_data: bytes, image_mime_type: str = "image/jpeg") -> str
    def start_chat_session(self, context: Dict[str, Any] = None) -> Any
```

#### MistralClient

```python
class MistralClient:
    def __init__(self, config: Dict[str, Any])
    def generate(self, request_data: Dict[str, Any]) -> str
    def generate_streaming(self, request_data: Dict[str, Any]) -> List[str]
    def get_available_models(self) -> List[Dict[str, Any]]
```

## MeTTa Knowledge Base APIs

### MeTTaEngine

MeTTa knowledge base engine.

#### Methods

##### `__init__(config: Dict[str, Any])`
Initialize engine.

##### `execute_query(query: str, context: Dict[str, Any] = None) -> Any`
Execute MeTTa query.

##### `load_knowledge_base(kb_path: str) -> bool`
Load knowledge base from file.

##### `add_fact(fact: str) -> bool`
Add fact to knowledge base.

##### `remove_fact(fact: str) -> bool`
Remove fact from knowledge base.

### Query Wrappers

#### BuyerQueries

```python
class BuyerQueries:
    def __init__(self, metta_engine: MeTTaEngine)
    def get_procurement_policies(self) -> Dict[str, Any]
    def get_budget_constraints(self) -> Dict[str, Any]
    def get_quality_requirements(self) -> Dict[str, Any]
    def evaluate_quote(self, quote_data: Dict[str, Any]) -> Dict[str, Any]
    def get_negotiation_strategy(self, rfq_id: str, history: List[Dict[str, Any]]) -> Dict[str, Any]
```

#### SellerQueries

```python
class SellerQueries:
    def __init__(self, metta_engine: MeTTaEngine)
    def get_inventory(self) -> Dict[str, Any]
    def get_pricing_rules(self) -> Dict[str, Any]
    def get_products(self) -> Dict[str, Any]
    def assess_fulfillment_capability(self, requirements: Dict[str, Any]) -> Dict[str, Any]
    def get_pricing_for_requirements(self, requirements: Dict[str, Any]) -> Dict[str, Any]
```

## Configuration APIs

### Settings

System configuration management.

#### Methods

##### `get_llm_config() -> Dict[str, Any]`
Get LLM configuration.

##### `get_metta_config() -> Dict[str, Any]`
Get MeTTa configuration.

##### `get_negotiation_config() -> Dict[str, Any]`
Get negotiation configuration.

##### `get_scoring_config() -> Dict[str, Any]`
Get scoring configuration.

##### `get_system_config() -> Dict[str, Any]`
Get system configuration.

##### `get_full_config() -> Dict[str, Any]`
Get complete configuration.

##### `validate_config() -> List[str]`
Validate configuration and return errors.

## Error Handling

### Common Error Types

#### Validation Errors
```python
{
    "error": "Invalid message format",
    "details": ["Missing required field: type"]
}
```

#### State Machine Errors
```python
{
    "error": "Invalid state transition",
    "current_state": "negotiating",
    "requested_event": "invalid_event"
}
```

#### LLM Errors
```python
{
    "error": "LLM request failed",
    "provider": "openrouter",
    "model": "deepseek-chat",
    "details": "Rate limit exceeded"
}
```

### Error Response Format

All API errors follow this format:

```python
{
    "error": "Error message",
    "error_type": "validation|state|llm|system",
    "details": "Additional error details",
    "timestamp": "2024-01-01T00:00:00Z"
}
```

## Rate Limiting

### Rate Limit Headers

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1640995200
```

### Rate Limit Response

```python
{
    "error": "Rate limit exceeded",
    "retry_after": 60,
    "limit": 60,
    "remaining": 0
}
```

## Authentication

### API Key Authentication

```http
Authorization: Bearer your_api_key_here
```

### Agent Authentication

```python
{
    "agent_id": "buyer_001",
    "agent_type": "buyer",
    "api_key": "agent_specific_key"
}
```

## Monitoring and Health Checks

### Health Check Endpoint

```python
GET /health
```

**Response:**
```python
{
    "status": "healthy",
    "timestamp": "2024-01-01T00:00:00Z",
    "components": {
        "metta": "healthy",
        "llm": "healthy",
        "agents": "healthy"
    }
}
```

### Metrics Endpoint

```python
GET /metrics
```

**Response:**
```python
{
    "requests_total": 1000,
    "requests_successful": 950,
    "requests_failed": 50,
    "average_response_time": 0.5,
    "active_agents": 5,
    "active_deals": 10
}
```

