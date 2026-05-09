import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

class Settings:

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = "gemini-1.5-flash"

    EXA_API_KEY = os.getenv("EXA_API_KEY")
    EXA_NUM_RESULTS = 5

    MONGO_URI = os.getenv("MONGO_URI")

    MONGO_DB_NAME = "venture_alpha"
    MONGO_COLLECTION_SIGNALS = "signals"

    APP_TITLE = "Venture-Alpha AI Intelligence Layer"
    APP_VERSION = "1.0.0"
    APP_DESCRIPTION = (
        "AI reasoning service that transforms structured repository signals "
        "into investment-grade insights using Gemini 2.0 Flash and Exa Search."
    )

    def validate(self):
        if not self.GEMINI_API_KEY:
            raise EnvironmentError("GEMINI_API_KEY missing in .env")

        if not self.EXA_API_KEY:
            raise EnvironmentError("EXA_API_KEY missing in .env")

        if not self.MONGO_URI:
            raise EnvironmentError("MONGO_URI missing in .env")


settings = Settings()

# MongoClient is created lazily — only after validate() is called in app.py
def _get_mongo():
    client = MongoClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB_NAME]
    return client, db, db[settings.MONGO_COLLECTION_SIGNALS]

mongo_client, mongo_db, signals_collection = _get_mongo() if settings.MONGO_URI else (None, None, None)