import os
import shutil
import json

memory_dir = "memory"
buyer_reputations_file = os.path.join(memory_dir, "buyer_agent_seller_reputations.json")
buyer_market_intelligence_file = os.path.join(memory_dir, "buyer_agent_market_intelligence.json")

print(f"Attempting to fix permissions for '{memory_dir}' directory...")

# 1. Remove existing memory directory if it exists
if os.path.exists(memory_dir):
    print(f"Removing existing directory: {memory_dir}")
    try:
        shutil.rmtree(memory_dir)
        print(f"Successfully removed '{memory_dir}'.")
    except OSError as e:
        print(f"Error removing directory '{memory_dir}': {e}")
        print("Please ensure no files in 'memory' are open and try again.")
        exit(1)

# 2. Recreate the memory directory
print(f"Recreating directory: {memory_dir}")
try:
    os.makedirs(memory_dir, exist_ok=True)
    print(f"Successfully recreated '{memory_dir}'.")
except OSError as e:
    print(f"Error recreating directory '{memory_dir}': {e}")
    exit(1)

# 3. Create initial empty JSON files with correct permissions
print("Creating initial memory files...")
try:
    with open(buyer_reputations_file, 'w') as f:
        json.dump({}, f, indent=4)
    print(f"Created '{buyer_reputations_file}'.")

    with open(buyer_market_intelligence_file, 'w') as f:
        json.dump({"product_trends": {}}, f, indent=4)
    print(f"Created '{buyer_market_intelligence_file}'.")
    
    print("Memory directory and files initialized with correct permissions.")
    print("You should now be able to run the agents without permission errors.")

except OSError as e:
    print(f"Error creating initial memory files: {e}")
    exit(1)
