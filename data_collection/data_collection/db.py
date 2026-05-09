import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["venture_alpha"]

signals = db["signals"]
scored_projects = db["scored_projects"]

def save(document):
    url = document.get("url")
    if url:
        result = signals.update_one({"url": url}, {"$set": document}, upsert=True)
        if result.upserted_id:
            print(f"Saved new signal: {url}")
        else:
            # Optionally print if it was an update, or stay silent to reduce spam
            pass
    else:
        # Fallback if there is no URL for some reason
        result = signals.insert_one(document)
        print(f"Saved signal without URL: {result.inserted_id}")
