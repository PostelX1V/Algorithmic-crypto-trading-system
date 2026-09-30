import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("COINBASE_API_KEY")
API_SECRET = os.getenv("COINBASE_API_SECRET")

if not API_KEY or not API_SECRET:
    raise ValueError("Missing Coinbase API credentials in .env")