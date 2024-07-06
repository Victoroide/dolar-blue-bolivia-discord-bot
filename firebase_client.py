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

def get_historical_usdt_to_bob(temporality='hourly'):
    collection_name = 'binance_prices' if temporality == 'hourly' else 'binance_prices_end_of_the_day'
    url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents:runQuery?key={FIREBASE_API_KEY}"
    
    query = {
        "structuredQuery": {
            "from": [{"collectionId": collection_name}],
            "orderBy": [{"field": {"fieldPath": "timestamp"}, "direction": "DESCENDING"}],
            "limit": 10
        }
    }

    response = requests.post(url, json=query)

    historical_data = []
    if response.status_code == 200:
        results = response.json()
        for result in results:
            if 'document' in result:
                doc = result['document']
                fields = doc['fields']
                timestamp = fields['timestamp']['timestampValue']
                average_price = fields['averagePrice']['doubleValue']
                historical_data.append({
                    'timestamp': timestamp,
                    'averagePrice': average_price
                })
    return historical_data
