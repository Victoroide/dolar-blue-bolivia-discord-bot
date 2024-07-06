import os
import requests
from config import FIREBASE_API_KEY, FIREBASE_PROJECT_ID

def get_latest_usdt_to_bob():
    collection_name = 'binance_prices'
    url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents:runQuery?key={FIREBASE_API_KEY}"
    
    query = {
        "structuredQuery": {
            "from": [{"collectionId": collection_name}],
            "orderBy": [{"field": {"fieldPath": "timestamp"}, "direction": "DESCENDING"}],
            "limit": 1
        }
    }

    response = requests.post(url, json=query)

    if response.status_code == 200:
        results = response.json()
        if results:
            latest_doc = results[0]['document']
            fields = latest_doc['fields']
            price = fields['averagePrice']['doubleValue']
            return price
    return None
