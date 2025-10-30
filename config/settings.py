# config/settings.py

import os
from dotenv import load_dotenv

load_dotenv()

# --- AGENT SEEDS ---
BUYER_AGENT_SEED = os.getenv("BUYER_AGENT_SEED", "buyer_secret_seed_phrase_123456789")
SELLER_A_AGENT_SEED = os.getenv("SELLER_A_AGENT_SEED", "seller_a_secret_seed_phrase_123456789")
SELLER_B_AGENT_SEED = os.getenv("SELLER_B_AGENT_SEED", "seller_b_secret_seed_phrase_123456789")
COORDINATOR_AGENT_SEED = os.getenv("COORDINATOR_AGENT_SEED", "coordinator_secret_seed_phrase_123456789")

# --- LLM PROVIDER API KEYS ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# --- LLM CONFIGURATION ---
LLM_CONFIG = {
    "buyer": {
        "primary_model": "gemini-2.0-flash",  # Correct free model
        "fallback_model": "deepseek/deepseek-chat-v3-0324:free",                # Gemini fallback
    },
    "seller": {
        "primary_model": "gemini-2.0-flash",  # Correct free model
        "fallback_model": "deepseek/deepseek-chat-v3-0324:free",                # Gemini fallback
    }
}

# --- METTA KNOWLEDGE BASE FILE PATHS ---
BUYER_POLICIES_FILE = "metta/knowledge_base/buyer_policies.metta"
SELLER_A_KB_FILE = "metta/knowledge_base/seller_a.metta"
SELLER_B_KB_FILE = "metta/knowledge_base/seller_b.metta"