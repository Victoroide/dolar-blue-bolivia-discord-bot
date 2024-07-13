import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
FIREBASE_API_KEY = os.getenv('PUBLIC_FIREBASE_API_KEY')
FIREBASE_PROJECT_ID = os.getenv('PUBLIC_FIREBASE_PROJECT_ID')

if not DISCORD_TOKEN or not FIREBASE_API_KEY or not FIREBASE_PROJECT_ID:
    raise ValueError("Missing necessary environment variables. Check your .env file.")
