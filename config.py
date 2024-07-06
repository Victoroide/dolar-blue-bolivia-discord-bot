import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
FIREBASE_CONFIG = {
    'apiKey': os.getenv('PUBLIC_FIREBASE_API_KEY'),
    'authDomain': os.getenv('PUBLIC_FIREBASE_AUTH_DOMAIN'),
    'projectId': os.getenv('PUBLIC_FIREBASE_PROJECT_ID'),
    'storageBucket': os.getenv('PUBLIC_FIREBASE_STORAGE_BUCKET'),
    'messagingSenderId': os.getenv('PUBLIC_FIREBASE_MESSAGING_SENDER_ID'),
    'appId': os.getenv('PUBLIC_FIREBASE_APP_ID'),
    'measurementId': os.getenv('PUBLIC_FIREBASE_MEASUREMENT_ID')
}
THRESHOLD = 0.05
