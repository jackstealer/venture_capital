import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("VA_DB_NAME", "venture_alpha")
COLLECTION_NAME = os.getenv("VA_SIGNALS_COLLECTION", "signals")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
signals = db[COLLECTION_NAME]

def save(document):
    url = document.get("url")
    if url:
        result = signals.update_one({"url": url}, {"$set": document}, upsert=True)
        if result.upserted_id:
            print(f"Saved new signal: {url}")
        else:
            pass
    else:
        result = signals.insert_one(document)
        print(f"Saved signal without URL: {result.inserted_id}")

