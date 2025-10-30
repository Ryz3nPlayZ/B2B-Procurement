# ASI System Architecture

## Overview

The ASI (Autonomous System Intelligence) system is a multi-agent platform for automated procurement and negotiation. The system uses MeTTa knowledge bases, LLM routing, and intelligent agents to facilitate complex business negotiations.

## System Components

### 1. Agent Layer

#### BaseAgent
- **Purpose**: Shared functionality for all agents
- **Features**: MeTTa queries, LLM router, deal file management
- **Location**: `agents/base_agent.py`

#### BuyerAgent
- **Purpose**: Handles buyer logic and procurement policies
- **Features**: RFQ generation, quote evaluation, negotiation strategy
- **Location**: `agents/buyer_agent.py`

#### SellerAgent
- **Purpose**: Manages seller logic, inventory, and pricing
- **Features**: Quote generation, inventory management, negotiation
- **Location**: `agents/seller_agent.py`

#### CoordinatorAgent
- **Purpose**: Registry and discovery service
- **Features**: Agent registration, message routing, system monitoring
- **Location**: `agents/coordinator_agent.py`

### 2. Protocol Layer

#### RFQ Protocol
- **Purpose**: Request for Quote message structures
- **Features**: RFQ creation, validation, response handling
- **Location**: `protocols/rfq_protocol.py`

#### Quote Protocol
- **Purpose**: Quote and response structures
- **Features**: Quote generation, evaluation, comparison
- **Location**: `protocols/quote_protocol.py`

#### Negotiation Protocol
- **Purpose**: Multi-round bidding protocols
- **Features**: Negotiation rounds, state management, agreement tracking
- **Location**: `protocols/negotiation_protocol.py`

#### Chat Protocol
- **Purpose**: ASI:One integration
- **Features**: Chat sessions, command handling, notifications
- **Location**: `protocols/chat_protocol.py`

### 3. MeTTa Knowledge Base

#### Knowledge Base Files
- **buyer_policies.metta**: Procurement policies and constraints
- **seller_a.metta**: Seller A's catalog and business rules
- **seller_b.metta**: Seller B's catalog and business rules
- **seller_c.metta**: Seller C's catalog and business rules
- **Location**: `metta/knowledge_base/`

#### Schema Definitions
- **core_types.metta**: Base types and relationships
- **buyer_schema.metta**: Buyer-specific types
- **seller_schema.metta**: Seller-specific types
- **Location**: `metta/schemas/`

#### Query Wrappers
- **BuyerQueries**: Python wrappers for buyer MeTTa queries
- **SellerQueries**: Python wrappers for seller MeTTa queries
- **Location**: `metta/queries/`

### 4. Core System

#### Negotiation State Machine
- **Purpose**: State management with safeguards
- **Features**: State transitions, validation, timeout handling
- **Location**: `core/negotiation_state.py`

#### Message Validator
- **Purpose**: Concise message enforcement
- **Features**: Message validation, sanitization, business rules
- **Location**: `core/message_validator.py`

#### Deal File Manager
- **Purpose**: JSON memory per negotiation
- **Features**: Persistent state, history tracking, archiving
- **Location**: `core/deal_file.py`

#### Scoring System
- **Purpose**: Offer evaluation logic
- **Features**: Multi-criteria scoring, recommendation engine
- **Location**: `core/scoring.py`

### 5. LLM Integration

#### LLM Router
- **Purpose**: Smart model selection with fallbacks
- **Features**: Model selection, performance tracking, rate limiting
- **Location**: `llm/llm_router.py`

#### Provider Clients
- **OpenRouterClient**: DeepSeek, Qwen integration
- **GeminiClient**: Google Gemini integration
- **MistralClient**: Mistral AI integration
- **Location**: `llm/providers/`

#### Prompt Management
- **BasePrompts**: Shared prompt templates
- **BuyerPrompts**: Buyer-specific prompts
- **SellerPrompts**: Seller-specific prompts
- **Location**: `llm/prompts/`

### 6. Configuration

#### Settings Management
- **Purpose**: All constants and configuration
- **Features**: Environment variables, feature flags, API keys
- **Location**: `config/settings.py`

#### Environment Configuration
- **Purpose**: Environment-specific settings
- **Features**: API keys, database config, feature toggles
- **Location**: `config/env.example`

## Data Flow

### 1. Negotiation Initiation
1. Buyer creates RFQ using MeTTa knowledge base
2. RFQ is validated and stored in deal file
3. Coordinator routes RFQ to registered sellers

### 2. Quote Generation
1. Sellers receive RFQ and assess capabilities
2. MeTTa queries determine pricing and availability
3. LLM generates competitive quotes
4. Quotes are validated and stored

### 3. Quote Evaluation
1. Buyer receives quotes and applies scoring
2. MeTTa knowledge base provides evaluation criteria
3. LLM analyzes quotes and provides recommendations
4. Negotiation state machine tracks decisions

### 4. Negotiation Process
1. Multi-round negotiation with state management
2. LLM generates negotiation responses
3. MeTTa knowledge base provides strategy guidance
4. Deal file tracks all negotiation history

### 5. Agreement Finalization
1. Final agreement validation
2. Deal file archiving
3. System metrics and reporting

## Security and Validation

### Message Validation
- All messages validated against schemas
- Input sanitization and security checks
- Business rule enforcement

### State Management
- Safeguards prevent invalid state transitions
- Timeout handling and cleanup
- Audit trail for all operations

### Rate Limiting
- Multi-provider rate limiting
- Request throttling and queuing
- Performance monitoring

## Scalability and Performance

### Agent Scaling
- Stateless agent design
- Horizontal scaling support
- Load balancing capabilities

### Knowledge Base
- MeTTa query caching
- Incremental knowledge updates
- Performance optimization

### LLM Integration
- Multiple provider support
- Automatic failover
- Cost optimization

## Monitoring and Observability

### Logging
- Structured logging with context
- Agent-specific log files
- Performance metrics

### Health Checks
- System component monitoring
- Agent status tracking
- Performance indicators

### Metrics
- Request/response tracking
- Error rate monitoring
- Cost and usage analytics

## Development and Testing

### Local Development
- `scripts/run_local.py`: Local testing environment
- Interactive mode for manual testing
- Scenario-based testing

### Knowledge Base Management
- `scripts/init_metta.py`: MeTTa initialization
- Schema validation and testing
- Query performance monitoring

### Testing Framework
- Unit tests for all components
- Integration tests for workflows
- Performance and load testing

## Deployment

### Local Deployment
- Single-machine setup
- Development environment
- Testing and validation

### Production Deployment
- Multi-agent deployment
- Load balancing
- High availability

### Agentverse Integration
- `scripts/deploy_agents.sh`: Agent deployment
- Cloud-native architecture
- Scalable infrastructure

## Future Enhancements

### Advanced AI
- Multi-modal LLM support
- Advanced reasoning capabilities
- Predictive analytics

### Integration
- ERP system integration
- Blockchain integration
- IoT device connectivity

### Performance
- Real-time processing
- Edge computing support
- Advanced caching strategies

