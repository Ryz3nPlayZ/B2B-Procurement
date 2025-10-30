# ASI - Autonomous System Intelligence

[![Innovation Lab](https://img.shields.io/badge/Innovation%20Lab-ASI-blue.svg)](https://github.com/asi-system)
[![Hackathon](https://img.shields.io/badge/Hackathon-2024-green.svg)](https://github.com/asi-system)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![MeTTa](https://img.shields.io/badge/MeTTa-Knowledge%20Base-purple.svg)](https://github.com/trueagi/MeTTa)
[![LLM](https://img.shields.io/badge/LLM-Multi%20Provider-orange.svg)](https://openrouter.ai)

## 🚀 Overview

ASI (Autonomous System Intelligence) is a cutting-edge multi-agent platform for automated procurement and negotiation. Built for the Innovation Lab and Hackathon 2024, ASI leverages MeTTa knowledge bases, intelligent LLM routing, and sophisticated agent coordination to revolutionize business negotiations.

## ✨ Key Features

- **🤖 Multi-Agent Architecture**: Intelligent buyer, seller, and coordinator agents
- **🧠 MeTTa Knowledge Base**: Advanced reasoning with MeTTa knowledge graphs
- **🔄 Smart LLM Routing**: Multi-provider LLM integration with automatic failover
- **📊 Intelligent Scoring**: Multi-criteria offer evaluation and recommendation
- **🛡️ State Machine Safeguards**: Robust negotiation state management
- **💬 ASI:One Integration**: Seamless chat protocol integration
- **📈 Real-time Monitoring**: Comprehensive system health and performance tracking

## 🏗️ Architecture

```
ASI/
├── agents/           # Intelligent agent implementations
├── protocols/        # Message protocols and structures
├── metta/           # MeTTa knowledge base integration
├── core/            # Core system components
├── llm/             # LLM integration and routing
├── config/          # Configuration management
├── utils/           # Utility functions and helpers
├── tests/           # Comprehensive test suite
├── scripts/         # Deployment and management scripts
└── docs/            # Complete documentation
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- MeTTa runtime
- LLM API keys (OpenRouter, Gemini, Mistral)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/asi-system/asi.git
cd asi
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp config/env.example .env
# Edit .env with your API keys and configuration
```

5. **Initialize MeTTa knowledge base**
```bash
python scripts/init_metta.py
```

6. **Run local development server**
```bash
python scripts/run_local.py
```

## 🔧 Configuration

### Environment Variables

```bash
# API Keys
OPENROUTER_API_KEY=your_openrouter_key
GEMINI_API_KEY=your_gemini_key
MISTRAL_API_KEY=your_mistral_key

# System Configuration
ASI_DEBUG=false
ASI_LOG_LEVEL=INFO
ASI_MAX_CONCURRENT_REQUESTS=100

# LLM Configuration
ASI_DEFAULT_MODEL=deepseek-chat
ASI_MAX_TOKENS=4096
ASI_TEMPERATURE=0.7

# Negotiation Settings
ASI_MAX_ROUNDS=10
ASI_TIMEOUT_HOURS=24
```

### MeTTa Knowledge Base

The system uses MeTTa knowledge bases for intelligent reasoning:

- **Buyer Policies**: Procurement rules and constraints
- **Seller Catalogs**: Product information and pricing
- **Business Rules**: Decision logic and workflows

## 🤖 Agent System

### Buyer Agent
- **RFQ Generation**: Intelligent request for quote creation
- **Quote Evaluation**: Multi-criteria scoring and analysis
- **Negotiation Strategy**: Advanced negotiation tactics
- **Procurement Policies**: Automated policy enforcement

### Seller Agent
- **Quote Generation**: Competitive quote creation
- **Inventory Management**: Real-time inventory tracking
- **Pricing Strategy**: Dynamic pricing algorithms
- **Customer Relations**: Relationship management

### Coordinator Agent
- **Agent Registry**: Central agent management
- **Message Routing**: Intelligent message distribution
- **System Monitoring**: Health and performance tracking
- **Load Balancing**: Optimal resource allocation

## 🧠 LLM Integration

### Multi-Provider Support
- **OpenRouter**: DeepSeek, Qwen, and other models
- **Google Gemini**: Advanced reasoning capabilities
- **Mistral AI**: High-performance language models

### Smart Routing
- **Automatic Failover**: Seamless provider switching
- **Performance Optimization**: Model selection based on task
- **Cost Management**: Intelligent cost optimization
- **Rate Limiting**: Multi-provider rate management

## 📊 MeTTa Knowledge Base

### Knowledge Representation
```metta
;; Procurement Policies
(procurement-policy "competitive-bidding" "All purchases over $10,000 must go through competitive bidding process")

;; Product Information
(Product "A001" "Industrial Sensors" "Electronics" "High-precision temperature and pressure sensors")

;; Pricing Rules
(Pricing "A001" "wholesale" 67.50 "min-100-units")
```

### Query Examples
```python
# Get procurement policies
policies = buyer_queries.get_procurement_policies()

# Evaluate quote
evaluation = buyer_queries.evaluate_quote(quote_data)

# Assess fulfillment capability
capability = seller_queries.assess_fulfillment_capability(requirements)
```

## 🔄 Negotiation Workflow

1. **RFQ Creation**: Buyer generates intelligent RFQ
2. **Quote Generation**: Sellers create competitive quotes
3. **Evaluation**: Multi-criteria scoring and analysis
4. **Negotiation**: Multi-round intelligent negotiation
5. **Agreement**: Final agreement and documentation

## 🧪 Testing

### Run Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test modules
python -m pytest tests/test_buyer_agent.py
python -m pytest tests/test_metta_queries.py

# Run with coverage
python -m pytest --cov=. tests/
```

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: System workflow testing
- **Performance Tests**: Load and stress testing
- **MeTTa Tests**: Knowledge base validation

## 📚 Documentation

- **[Architecture Guide](docs/ARCHITECTURE.md)**: Complete system architecture
- **[MeTTa Schema](docs/METTA_SCHEMA.md)**: Knowledge base documentation
- **[API Reference](docs/API.md)**: Comprehensive API documentation

## 🤖 Live Agents (Agentverse)

### Buyer Agent
- **Agentverse URL**: https://agentverse.ai/agents/asi-buyer-agent
- **Address**: `agent1qvas8quzgnydh906ycwyy28aeskmzj4x39pm48lzjcptnl4x8qtak2hjl58`
- **Chat Protocol**: ✅ Enabled
- **Try in ASI:One**: Search "ASI Buyer" → Send `/rfq TS-100 50 75`

### Coordinator Agent
- **Agentverse URL**: https://agentverse.ai/agents/asi-coordinator
- **Address**: `agent1qwtcsxnr2957et869u38r3yafphfg2dlppl86t99ll0ye8nv2f672zrma08`
- **Chat Protocol**: ✅ Enabled
- **Try in ASI:One**: Search "ASI Coordinator"

### Seller A Agent
- **Agentverse URL**: https://agentverse.ai/agents/seller-a-volume-specialist
- **Address**: `agent1qdvsukqn674qvayrplfngd27ftm9jccym5zrncd9jhceyqkh3r8wy6n0c8s`
- **Chat Protocol**: ✅ Enabled
- **Try in ASI:One**: Search "Seller A"

### Seller B Agent
- **Agentverse URL**: https://agentverse.ai/agents/seller-b-premium-quality
- **Address**: `agent1qw4qevt4jcca8fmlxvqnx58gr46ddtcpj44gmah2a40hpvulhfdu6vppzrx`
- **Chat Protocol**: ✅ Enabled
- **Try in ASI:One**: Search "Seller B"

---

## 🧠 Learning & Adaptation

ASI agents **learn from every interaction**:

### Seller Reputation Tracking
- Tracks acceptance rate, quality scores, delivery accuracy
- Adjusts quote evaluation based on past performance
- Example: "Seller B has 85% reputation → +0.03 bonus"

### Market Intelligence
- Learns average pricing over time
- Detects price trends (increasing/decreasing)
- Alerts when quotes are 10%+ above/below market

### Demo After 5 Runs:
```
📚 LEARNING FROM PAST INTERACTIONS
Seller A: Reputation: 0.72 ✅ (accepted 5/7 times)
Seller B: Reputation: 0.85 ✅ (accepted 6/7 times)
Market Intelligence (8 historical quotes):
Average market price: $72.50/unit
Trend: decreasing
💰 Current quote is 8% below market average!
```

## 🚀 Deployment

### Local Development
```bash
python scripts/run_local.py
```

### Production Deployment
```bash
# Deploy to Agentverse
bash scripts/deploy_agents.sh

# Initialize production environment
python scripts/init_metta.py --production
```

## 🔍 Monitoring

### Health Checks
```bash
# System status
curl http://localhost:8000/health

# Agent status
curl http://localhost:8000/agents/status

# Performance metrics
curl http://localhost:8000/metrics
```

### Logging
- **Structured Logging**: JSON-formatted logs
- **Agent-Specific Logs**: Individual agent tracking
- **Performance Metrics**: Request/response monitoring
- **Error Tracking**: Comprehensive error logging

## 🤝 Contributing

We welcome contributions to the ASI project! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 Innovation Lab & Hackathon

This project was developed for the Innovation Lab and Hackathon 2024, showcasing cutting-edge AI and multi-agent systems technology.

### Key Innovations
- **MeTTa Integration**: Advanced knowledge representation
- **Multi-Agent Coordination**: Sophisticated agent interaction
- **LLM Routing**: Intelligent model selection
- **State Machine Design**: Robust negotiation management
- **Real-time Processing**: High-performance system architecture

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/asi-system/asi/issues)
- **Discussions**: [GitHub Discussions](https://github.com/asi-system/asi/discussions)

## 🌟 Acknowledgments

- **MeTTa Team**: For the powerful knowledge representation language
- **OpenRouter**: For multi-model LLM access
- **Innovation Lab**: For the platform and support
- **Hackathon Community**: For inspiration and collaboration

---

**Built with ❤️ for the Innovation Lab & Hackathon 2024**

*ASI - Autonomous System Intelligence: Revolutionizing Business Negotiations with AI*
