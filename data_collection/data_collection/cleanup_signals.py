import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def main():
    uri = os.getenv("MONGO_URI")
    if not uri:
        print("Missing MONGO_URI")
        return
    client = MongoClient(uri)
    col = client["venture_alpha"]["signals"]
    res = col.update_many(
        {},
        {
            "$unset": {
                "extra.funding_stage": "",
                "extra.investors": "",
                "extra.simulated": "",
            }
        },
    )
    print(f"Matched: {res.matched_count}, Modified: {res.modified_count}")

if __name__ == "__main__":
    main()

