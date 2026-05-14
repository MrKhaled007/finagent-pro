import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY")
GCP_PROJECT = os.getenv("GCP_PROJECT")

GEMINI_MODEL = "gemini-2.5-flash"
TEMPERATURE = 0.2
MAX_TOKENS = 2048