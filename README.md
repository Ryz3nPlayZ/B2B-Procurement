# 🤖 ASI - Autonomous Supply-Chain Intelligence

**Multi-agent procurement system using MeTTa knowledge bases, LLM reasoning, and intelligent negotiation.**

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

Built for **Innovation Lab & Hackathon 2024** 🏆

---

## 🎯 **Features**

- ✅ **MeTTa Knowledge Base Integration** - Symbolic reasoning for business rules
- ✅ **LLM-Driven Decision Making** - GPT-4/Gemini for strategic pricing & negotiation
- ✅ **Multi-Agent Coordination** - Buyer, Seller, Coordinator agents
- ✅ **Intelligent Quote Evaluation** - Combines numerical scoring + LLM quality analysis
- ✅ **Multi-Round Negotiation** - Realistic bargaining with walk-away scenarios
- ✅ **Agent Memory & Learning** - Tracks seller reputation & market trends
- ✅ **Price vs Quality Tradeoffs** - Evaluates premium pricing justification

---

## 🏗️ **Architecture**

```
┌─────────────┐
│   Buyer     │ ← Sends RFQ
│   Agent     │ → Evaluates Quotes
└──────┬──────┘ → Negotiates
       │
       ▼
┌─────────────┐
│ Coordinator │ ← Routes Messages
│   Agent     │ → Manages Registry
└──────┬──────┘
       │
       ▼
┌─────────────┐   ┌─────────────┐
│  Seller A   │   │  Seller B   │
│ (Deal-Focus)│   │(Margin-Focus)│
└─────────────┘   └─────────────┘
```

---

## 📦 **Installation**

### **Prerequisites:**
- Python 3.9+
- OpenAI API key OR Google Gemini API key
- Virtual environment (recommended)

### **Setup:**

```bash
# Clone the repository
git clone https://github.com/Ryz3nPlayZ/B2B-Procurement.git
cd B2B-Procurement

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp config.example.py config.py
# Edit config.py with your API keys and agent seeds
```

⚙️ Configuration
Create `config.py` from the template:
```python
class Settings:
    # LLM Configuration
    OPENAI_API_KEY = "your-openai-key-here"
    GEMINI_API_KEY = "your-gemini-key-here"
    
    # Agent Seeds (generate unique values)
    COORDINATOR_AGENT_SEED = "coordinator_seed_12345"
    BUYER_AGENT_SEED = "buyer_seed_67890"
    SELLER_A_AGENT_SEED = "seller_a_seed_11111"
    SELLER_B_AGENT_SEED = "seller_b_seed_22222"
```
Generate unique seeds:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

🚀 Usage
Quick Start:
```bash
# Linux/Mac
bash run_agents.sh

# Windows
run_agents.bat
```
This will start all agents simultaneously:

*   Coordinator on port 8000
*   Seller A on port 8001
*   Seller B on port 8002
*   Buyer on port 8003 (initiates RFQ automatically)

Manual Start (Separate Terminals):
```bash
# Terminal 1: Coordinator
python -m agents.coordinator_agent

# Terminal 2: Seller A
python -m agents.seller_agent seller_a

# Terminal 3: Seller B
python -m agents.seller_agent seller_b

# Terminal 4: Buyer (starts RFQ automatically)
python -m agents.buyer_agent
```

📊 Example Output
```
🏆 WINNER SELECTED: Seller B
   Price: $75.0/unit
   Quality Score: 8.5/10
   LLM Reasoning: "Superior precision (±0.2°C), 24-month warranty (2X standard)"
   
💬 Negotiation Round 1:
   Buyer offers: $67.5/unit
   Seller B counters: $72.0/unit
   
💬 Negotiation Round 2:
   Buyer offers: $70.0/unit
   Seller B accepts!
   
✅ DEAL FINALIZED at $70.0/unit!
   Delivery: 8 days
   Warranty: 24 months
```

📁 Project Structure
```
B2B-Procurement/
├── agents/                    # Agent implementations
│   ├── buyer_agent.py
│   ├── seller_agent.py
│   └── coordinator_agent.py
├── metta/                     # MeTTa knowledge engine
│   ├── metta_engine.py
│   ├── knowledge_base/
│   │   ├── buyer_policies.metta
│   │   ├── seller_a_kb.metta
│   │   └── seller_b_kb.metta
│   └── queries/
│       ├── buyer_queries.py
│       └── seller_queries.py
├── llm/                       # LLM integration
│   └── llm_router.py
├── protocols/                 # Message protocols
│   ├── rfq_protocol.py
│   └── quote_protocol.py
├── memory/                    # Agent memory & learning
│   └── agent_memory.py
├── config.example.py          # Configuration template
├── requirements.txt
├── run_agents.sh             # Linux/Mac launch script
├── run_agents.bat            # Windows launch script
└── README.md
```

🤖 Live Agents (Agentverse)
Buyer Agent

*   Address: `agent1qvas8quzgnydh906ycwyy28aeskmzj4x39pm48lzjcptnl4x8qtak2hjl58`
*   Agentverse: View Agent

Coordinator Agent

*   Address: `agent1qwtcsxnr2957et869u38r3yafphfg2dlppl86t99ll0ye8nv2f672zrma08`
*   Agentverse: View Agent

Seller A Agent (Volume Specialist)

*   Address: `agent1qdvsukqn674qvayrplfngd27ftm9jccym5zrncd9jhceyqkh3r8wy6n0c8s`
*   Strategy: High-volume, competitive pricing
*   Agentverse: View Agent

Seller B Agent (Premium Quality)

*   Address: `agent1qw4qevt4jcca8fmlxvqnx58gr46ddtcpj44gmah2a40hpvulhfdu6vppzrx`
*   Strategy: Premium quality, extended warranty
*   Agentverse: View Agent


🧠 Agent Learning & Adaptation
ASI agents learn from every interaction:
Seller Reputation Tracking

*   Tracks acceptance rate, quality scores, delivery accuracy
*   Adjusts quote evaluation based on past performance
*   Example: "Seller B has 85% reputation → bonus to score"

Market Intelligence

*   Learns average pricing over time
*   Detects price trends (increasing/decreasing)
*   Alerts when quotes deviate significantly from market

Demo After 5 Runs:
```
📚 LEARNING FROM PAST INTERACTIONS
Seller A: Reputation: 0.72 ✅ (accepted 5/7 times)
Seller B: Reputation: 0.85 ✅ (accepted 6/7 times)

Market Intelligence (8 historical quotes):
  Average market price: $72.50/unit
  Trend: decreasing
  💰 Current quote is 8% below market average!
```

🔧 How It Works
1.  RFQ Creation
    Buyer agent generates request for quote:

    *   Product: TS-100 (Industrial Temperature Sensor)
    *   Quantity: 50 units
    *   Budget: $75/unit
    *   Requirements: ISO9001 certification

2.  Quote Generation
    Sellers use MeTTa knowledge base + LLM to:

    *   Check inventory feasibility
    *   Select pricing tier (retail/wholesale/bulk)
    *   Generate competitive sales pitch
    *   Highlight technical differentiators

3.  Intelligent Evaluation
    Buyer combines:

    *   Numerical scoring (60%): Price, delivery, warranty
    *   LLM quality analysis (40%): Technical specs, trust signals, value proposition

4.  Multi-Round Negotiation

    *   Buyer counters if price > budget or quality justifies it
    *   Sellers accept/counter/walk-away based on MeTTa constraints
    *   Up to 3 rounds with escalation logic

5.  Deal Finalization

    *   Best negotiated deal selected
    *   Memory updated for future learning
    *   Purchase order generated


🎓 Key Innovations

1.  Hybrid Reasoning: MeTTa symbolic KB + LLM neural reasoning
2.  Stubborn Negotiation: Sellers never accept first offer (realistic behavior)
3.  Quality Premium Detection: Buyer pays more if LLM justifies value
4.  Walk-Away Scenarios: Failed negotiations when terms unreasonable
5.  Adaptive Memory: Agent performance improves over time


🤝 Contributing
Contributions welcome! Please:

1.  Fork the repository
2.  Create a feature branch (`git checkout -b feature/amazing-feature`)
3.  Commit your changes (`git commit -m 'Add amazing feature'`)
4.  Push to the branch (`git push origin feature/amazing-feature`)
5.  Open a Pull Request


📝 License
This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments

*   Fetch.ai - uAgents framework
*   Hyperon - MeTTa symbolic reasoning
*   OpenAI / Google - LLM APIs
*   Innovation Lab & Hackathon 2024 - Platform and inspiration


📧 Contact

*   GitHub: @Ryz3nPlayZ
*   Repository: B2B-Procurement


🔮 Future Roadmap

*   Multi-product procurement
*   Real-time market analysis dashboard
*   Blockchain-based smart contracts
*   Web UI for monitoring
*   AWS Lambda deployment
*   Advanced negotiation strategies


⭐ Star this repo if you find it useful!
Built with ❤️ for Innovation Lab & Hackathon 2024
