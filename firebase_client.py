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

def get_historical_usdt_to_bob(temporality='daily'):
    if temporality == 'daily':
        collection_name = 'binance_prices_end_of_the_day'
    else:
        collection_name = 'binance_prices'
    
    url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents:runQuery?key={FIREBASE_API_KEY}"
    
    query = {
        "structuredQuery": {
            "from": [{"collectionId": collection_name}],
            "orderBy": [{"field": {"fieldPath": "timestamp"}, "direction": "DESCENDING"}],
            "limit": 10  
        }
    }

    response = requests.post(url, json=query)

    if response.status_code == 200:
        results = response.json()
        if results:
            historical_data = []
            for result in results:
                if 'document' in result:
                    doc = result['document']
                    fields = doc['fields']
                    timestamp = fields['timestamp']['timestampValue']
                    price = fields['averagePrice']['doubleValue']
                    historical_data.append({'timestamp': timestamp, 'averagePrice': price})
            return historical_data
    return []
