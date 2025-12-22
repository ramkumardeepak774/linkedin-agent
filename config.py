import os
from pathlib import Path
from dotenv import load_dotenv

# Load env variables
load_dotenv()

class Config:
    # Paths
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    DB_PATH = DATA_DIR / "career_agent.db"
    
    # Credentials
    LINKEDIN_USERNAME = os.getenv("LINKEDIN_USERNAME")
    LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY")
    
    # Browser Settings
    HEADLESS = os.getenv("HEADLESS", "False").lower() == "true"
    BROWSER_TIMEOUT = 30000  # ms
    
    # Safety / Stealth
    MIN_DELAY = 2  # seconds
    MAX_DELAY = 10 # seconds
    
    # LLM Settings
    DEFAULT_LLM_MODEL = "accounts/fireworks/models/llama-v3-70b-instruct"
    SMART_LLM_MODEL = "gpt-4o"

    @classmethod
    def ensure_dirs(cls):
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)

Config.ensure_dirs()
