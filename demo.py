import subprocess
import webbrowser
import time
import sys

print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ASI - Autonomous System Intelligence                    ║
║   Innovation Lab Hackathon 2024                           ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

Starting demo environment...
""")

# Start UI server
print("📊 Starting web interface...")
ui_process = subprocess.Popen([sys.executable, "ui/app.py"])

time.sleep(2)

# Open browser
print("🌐 Opening browser at http://localhost:8080")
webbrowser.open("http://localhost:8080")

print("""
✅ Demo is ready!

🎮 Try these scenarios:
  1. Budget: $60 (tight) → Watch negotiation
  2. Budget: $100 (generous) → Quality wins
  3. Run 5+ times → See learning in action

Press Ctrl+C to stop demo
""")

try:
    ui_process.wait()
except KeyboardInterrupt:
    print("\n👋 Shutting down...")
    ui_process.terminate()
