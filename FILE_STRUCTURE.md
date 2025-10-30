# ASI Autonomous Procurement System - Complete File Structure

## Project Overview
Autonomous AI agents for procurement negotiation using uAgents, MeTTa knowledge graphs, and multi-LLM routing.

---

## Directory Tree

\ASI/
├── agents/                          # uAgent implementations
│   ├── __init__.py
│   ├── base_agent.py               # Base agent class
│   ├── buyer_agent.py              # Buyer procurement agent (268 lines)
│   ├── seller_agent.py             # Seller negotiation agent (268 lines)
│   └── coordinator_agent.py        # Agent discovery & orchestration
│
├── metta/                          # MeTTa knowledge base integration
│   ├── __init__.py
│   ├── metta_engine.py             # Hyperon MeTTa runtime wrapper
│   ├── queries/
│   │   ├── __init__.py
│   │   ├── buyer_queries.py        # Buyer KB queries (65 lines)
│   │   └── seller_queries.py       # Seller KB queries (111 lines)
│   ├── schemas/
│   │   ├── core_types.metta
│   │   ├── buyer_schema.metta
│   │   └── seller_schema.metta
│   └── knowledge_base/
│       ├── buyer_policies.metta
│       ├── seller_a.metta
│       ├── seller_b.metta
│       └── seller_c.metta
│
├── protocols/                      # Communication protocols
│   ├── __init__.py
│   ├── rfq_protocol.py            # Request for Quote
│   ├── quote_protocol.py          # Quote response
│   ├── negotiation_protocol.py    # Negotiation messages
│   ├── chat_protocol.py           # ASI:One integration
│   └── registration_protocol.py   # Agent registration
│
├── llm/                           # Multi-LLM routing
│   ├── __init__.py
│   ├── llm_router.py              # LLM dispatcher
│   ├── rate_limiter.py            # Rate limiting (12,894 bytes)
│   ├── providers/
│   │   ├── openrouter_client.py
│   │   ├── gemini_client.py
│   │   └── mistral_client.py
│   └── prompts/
│       ├── base_prompts.py
│       ├── buyer_prompts.py
│       └── seller_prompts.py
│
├── core/                          # Business logic
│   ├── message_validator.py       # Message validation (14,654 bytes)
│   ├── scoring.py                 # Quote scoring (14,530 bytes)
│   ├── negotiation_state.py       # State tracking (13,033 bytes)
│   └── deal_file.py               # Deal records (11,819 bytes)
│
├── config/                        # Configuration
│   ├── __init__.py
│   ├── settings.py                # Central settings (1,806 bytes)
│   └── .env                       # Environment variables
│
├── utils/
│   ├── logging_config.py
│   └── helpers.py
│
├── tests/
│   ├── test_buyer_agent.py        # Buyer tests (8,022 bytes)
│   └── test_metta_queries.py      # MeTTa tests (9,958 bytes)
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── METTA_SCHEMA.md
│
├── scripts/
│   ├── run_local.py
│   └── init_metta.py              # KB initialization (6,279 bytes)
│
├── deal_files/
├── run_local.sh                   # Linux/WSL startup
├── run_local.bat                  # Windows startup
├── requirements.txt
├── .gitignore
└── README.md
\
---

## Key Files Explained

### Agents (agents/)

**buyer_agent.py (268 lines)**
- Autonomous buyer for procurement
- Methods: initial_startup_and_rfq(), handle_quote(), evaluate_quotes_and_negotiate()
- Scores quotes (price 50%, delivery 20%, warranty 15%, precision 15%)
- Negotiates up to 3 rounds if over budget
- Port: 8003

**seller_agent.py (268 lines)**
- Autonomous seller handling RFQs & negotiations
- Methods: startup(), handle_rfq_broadcast(), handle_counter_offer()
- Queries MeTTa for inventory, pricing, certs, strategy
- Generates quotes with LLM context from KB
- Ports: 8001 (seller_a), 8002 (seller_b)

**coordinator_agent.py**
- Receives seller registrations
- Broadcasts RFQs to registered sellers
- Port: 8000

---

### MeTTa (metta/)

**metta_engine.py**
- Wrapper for Hyperon MeTTa runtime
- Methods: load_metta_file(), execute_query(), _atom_to_python()

**queries/buyer_queries.py (65 lines)**
| Method | Returns |
|--------|---------|
| get_required_quantity() | int |
| get_max_budget_per_unit() | float |
| get_llm_system_prompt() | str |
| get_procurement_policies() | Dict |

**queries/seller_queries.py (111 lines)**
| Method | Returns |
|--------|---------|
| get_inventory_for_product() | List[Dict] |
| check_certification() | bool |
| get_pricing_for_product() | Dict |
| get_delivery_time() | int |
| get_warranty() | int |
| get_strategy_instruction() | str |
| get_specifications() | Dict |
| get_min_acceptable_price() | float |
| get_max_discount_percent() | float |
| get_negotiation_style() | str |

**Knowledge Bases**
- buyer_policies.metta: Requirements, budget, weights, LLM instructions
- seller_a.metta: Deal-focused (willing to discount)
- seller_b.metta: Alternative strategy
- seller_c.metta: Third variant

---

### LLM (llm/)

**llm_router.py**
- Routes prompts to best LLM provider
- Fallback chain: OpenRouter → Gemini → Mistral

**rate_limiter.py (12,894 bytes)**
- Token bucket rate limiting
- Per-provider limits
- Exponential backoff

**providers/**
- openrouter_client.py
- gemini_client.py
- mistral_client.py

**prompts/**
- base_prompts.py (8,387 bytes)
- buyer_prompts.py (10,562 bytes)
- seller_prompts.py

---

### Core Business Logic (core/)

**message_validator.py (14,654 bytes)**
- Schema validation
- Type checking
- Required field verification

**scoring.py (14,530 bytes)**
- Quote scoring: price(50%) + delivery(20%) + warranty(15%) + specs(15%)

**negotiation_state.py (13,033 bytes)**
- Track round count, price history, accept/reject decisions

**deal_file.py (11,819 bytes)**
- Generate deal records
- Store negotiation history

---

### Configuration & Utilities

**config/settings.py (1,806 bytes)**
- Environment variables
- Agent seeds, KB paths, API keys
- Default model: deepseek-chat
- Max tokens: 4096, Temperature: 0.7, Max rounds: 10

**config/.env**
- SELLER_A_AGENT_SEED, SELLER_B_AGENT_SEED, BUYER_AGENT_SEED
- OPENROUTER_API_KEY, GEMINI_API_KEY, MISTRAL_API_KEY

---

### Tests (tests/)

**test_buyer_agent.py (8,022 bytes)**
- Agent initialization
- Quote scoring
- Negotiation flow
- Deal finalization

**test_metta_queries.py (9,958 bytes)**
- KB loading
- Query execution
- Result parsing

Run: \python -m pytest tests/
---

### Scripts (scripts/)

**run_local.py**
- Local testing runner

**init_metta.py (6,279 bytes)**
- Initialize MeTTa KBs
- Validate syntax
- Load into runtime

---

### Documentation (docs/)

**ARCHITECTURE.md** - System design
**API.md** - API documentation
**METTA_SCHEMA.md** - MeTTa schema docs

---

## Startup Flow

\run_local.sh
  ├─> Coordinator (port 8000)
  ├─> Seller A (port 8001) → loads seller_a.metta
  ├─> Seller B (port 8002) → loads seller_b.metta
  └─> Buyer (port 8003) → loads buyer_policies.metta
\
---

## RFQ → Quote → Negotiation Flow

1. Buyer loads KB, queries required_quantity & max_budget
2. Buyer sends RFQ to Coordinator
3. Coordinator broadcasts RFQ to sellers
4. Seller checks inventory & certification via MeTTa
5. Seller queries pricing, delivery, specs from MeTTa
6. Seller uses LLM to generate quote with KB context
7. Buyer receives quotes, scores each one
8. If best quote ≤ budget → finalize deal
9. Else → start negotiation (max 3 rounds)
10. Seller evaluates counter-offer vs min_acceptable_price from MeTTa
11. Seller accepts if ≥ min OR counters with halfway price
12. Negotiation ends when accepted or rounds exhausted
13. Buyer generates PO with LLM

---

## Key Statistics

| Metric | Count |
|--------|-------|
| Python files | 25 |
| MeTTa files | 7 |
| Total Python LOC | ~2,000 |
| Total MeTTa LOC | ~150 |
| Agent types | 4 |
| LLM providers | 3 |
| Knowledge bases | 4 |
| Message types | 5+ |

---

## Design Patterns

1. **MeTTa-First:** All decisions query KB before acting
2. **LLM-Enhanced:** LLMs generate text only, not decisions
3. **Async Wrappers:** BuyerQueries/SellerQueries abstract complexity
4. **Knowledge-Driven:** Different strategies via KB, not code
5. **Multi-Provider:** Resilient LLM routing with fallback

---

## Setup & Run

\\ash
# 1. Create venv
python -m venv venv
source venv/bin/activate

# 2. Install deps
pip install -r requirements.txt

# 3. Configure .env
cp config/.env.example config/.env
# Add API keys & agent seeds

# 4. Initialize MeTTa
python scripts/init_metta.py

# 5. Start agents
./run_local.sh
\
