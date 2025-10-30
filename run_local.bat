@echo off
echo "🚀 Starting ASI System Local Runner..."

REM Launching Agents in new command prompt windows
echo "1. Launching Coordinator Agent..."
start "Coordinator" cmd /k "venv\Scripts\activate && python -m agents.coordinator_agent"
timeout /t 3

echo "2. Launching Seller Agent A..."
start "Seller A" cmd /k "venv\Scripts\activate && python -m agents.seller_agent seller_a"
timeout /t 3

echo "3. Launching Seller Agent B..."
start "Seller B" cmd /k "venv\Scripts\activate && python -m agents.seller_agent seller_b"
timeout /t 3

echo "4. Launching Buyer Agent..."
start "Buyer" cmd /k "venv\Scripts\activate && python -m agents.buyer_agent"
timeout /t 3

echo "All agents have been launched in separate command prompt windows."
echo "You can now observe their logs. The Buyer will send an RFQ every 30 seconds."
echo "NOTE: You need to replace the placeholder coordinator address in seller_agent.py with the real one from its logs."