# Agentverse Deployment Guide

## 🚀 Quick Deploy

### 1. Login to Agentverse
Visit https://agentverse.ai/ and sign in

### 2. Create New Hosted Agent

For each agent (buyer, coordinator, seller_a, seller_b):

1. Click "Create Agent"
2. Choose "Python Agent"
3. Copy code from `agents/<agent_name>.py`
4. Set environment variables:
   - `OPENROUTER_API_KEY`
   - `GEMINI_API_KEY`
5. Enable protocols:
   - ✅ RFQ Protocol
   - ✅ Quote Protocol
   - ✅ Negotiation Protocol
   - ✅ **Chat Protocol** (REQUIRED!)
6. Add tags: `innovationlab`, `hackathon`
7. Deploy

### 3. Get Agent Addresses

After deployment, copy agent addresses:

- Buyer: `agent1qvas8quzgnydh906ycwyy28aeskmzj4x39pm48lzjcptnl4x8qtak2hjl58`
- Coordinator: `agent1qwtcsxnr2957et869u38r3yafphfg2dlppl86t99ll0ye8nv2f672zrma08`
- Seller A: `agent1qdvsukqn674qvayrplfngd27ftm9jccym5zrncd9jhceyqkh3r8wy6n0c8s`
- Seller B: `agent1qw4qevt4jcca8fmlxvqnx58gr46ddtcpj44gmah2a40hpvulhfdu6vppzrx`

### 4. Test Chat Protocol

1. Go to ASI:One interface
2. Search for "ASI Buyer Agent"
3. Send: `/rfq TS-100 50 75`
4. Watch negotiation unfold!

### 5. Verify Registration

All agents should appear at:
- https://agentverse.ai/agents?tag=innovationlab
- https://agentverse.ai/agents?tag=hackathon

## ✅ Deployment Checklist

- [ ] All 4 agents deployed on Agentverse
- [ ] Chat Protocol enabled for all agents
- [ ] Tags `innovationlab` and `hackathon` added
- [ ] Agents discoverable via ASI:One
- [ ] Test chat commands working
- [ ] Agent addresses documented in main README
Action: Actually deploy to Agentverse following this guide!
