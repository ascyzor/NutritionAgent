import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
USDA_API_KEY = st.secrets.get("USDA_API_KEY", os.getenv("USDA_API_KEY"))

# Application Settings
DEBUG_MODE = os.getenv("DEBUG_MODE", "False") == "True"
MAX_DISHES = int(os.getenv("MAX_DISHES", "50"))
DEFAULT_CALORIE_TARGET = int(os.getenv("DEFAULT_CALORIE_TARGET", "600"))

# API Endpoints
USDA_SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

# Dietary Goals
GOALS = {
    "weight_loss": {
        "calorie_multiplier": 0.85,
        "protein_priority": "medium",
        "carb_priority": "low"
    },
    "muscle_gain": {
        "calorie_multiplier": 1.15,
        "protein_priority": "high",
        "carb_priority": "medium"
    },
    "maintain_health": {
        "calorie_multiplier": 1.0,
        "protein_priority": "medium",
        "carb_priority": "medium"
    }
}

# Validation
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is required. Please set it in .env file")
if not USDA_API_KEY:
    raise ValueError("USDA_API_KEY is required. Please set it in .env file")
if MAX_DISHES <= 0:
    raise ValueError("MAX_DISHES must be a positive integer")
if DEFAULT_CALORIE_TARGET <= 0:
    raise ValueError("DEFAULT_CALORIE_TARGET must be a positive integer")
if DEBUG_MODE:
    print("Debug mode is enabled")
if DEBUG_MODE:
    print(f"Loaded configuration: MAX_DISHES={MAX_DISHES}, DEFAULT_CALORIE_TARGET={DEFAULT_CALORIE_TARGET}")


