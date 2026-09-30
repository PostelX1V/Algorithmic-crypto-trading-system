import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram_alert(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram alert skipped: missing token or chat ID")
        return

    url = f"https://api.telegram.org/bot{8575584416:AAHYO3TKEdD4YxzwozhZI-WvsmKRNtwbXm0}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print("Telegram alert error:", e)