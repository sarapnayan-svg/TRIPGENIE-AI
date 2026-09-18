"""
Central configuration for the TripGenie AI backend.
Loads secrets from a local .env file (never commit .env to git).
"""
import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "claude-3-5-sonnet-20241022")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "6"))

# Optional Weather API Key (e.g. OpenWeatherMap)
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")

if not ANTHROPIC_API_KEY:
    print(
        "[WARNING] ANTHROPIC_API_KEY is not set. Copy .env.example to .env "
        "and add your key from https://console.anthropic.com/ before calling "
        "the /api/plan-trip or /api/chat endpoints."
    )
