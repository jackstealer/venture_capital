# save as test_mongo.py and run from backend/
from pymongo import MongoClient
import os
uri = os.getenv('MONGO_URI', 'mongodb+srv://armanopdc:arman123@cluster0.yv6hvjv.mongodb.net/?appName=Cluster0')
client = MongoClient(uri, serverSelectionTimeoutMS=5000)
try:
    print(client.admin.command('ping'))
except Exception as e:
    print('Connect error:', repr(e))