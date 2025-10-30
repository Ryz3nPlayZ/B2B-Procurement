#!/bin/bash

# run_local.sh (Corrected for 'venv' folder)

echo "🚀 Starting ASI System Local Runner (WSL/Linux)..."

echo "1. Launching Coordinator Agent..."
gnome-terminal -- bash -c "source venv/bin/activate; echo '--- COORDINATOR ---'; python -m agents.coordinator_agent; exec bash"
sleep 3

echo "2. Launching Seller Agent A..."
gnome-terminal -- bash -c "source venv/bin/activate; echo '--- SELLER A ---'; python -m agents.seller_agent seller_a; exec bash"
sleep 3

echo "3. Launching Seller Agent B..."
gnome-terminal -- bash -c "source venv/bin/activate; echo '--- SELLER B ---'; python -m agents.seller_agent seller_b; exec bash"
sleep 3

echo "4. Launching Buyer Agent..."
gnome-terminal -- bash -c "source venv/bin/activate; echo '--- BUYER ---'; python -m agents.buyer_agent; exec bash"
sleep 3

echo "✅ All agents have been launched in separate terminal windows."