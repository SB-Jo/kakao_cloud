from pymongo import MongoClient
import os

'''
host = 'kakao.u0vjs.mongodb.net'
user = 'SB-Jo'
password = os.environ.get('DB_PASSWORD')
database_name = 'kakao'


MONGO_URI = f"mongodb+srv://{user}:{password}@{host}/{database_name}?retryWrites=true&w=majority"

client = MongoClient(MONGO_URI)

db = client.database_name
'''
client = MongoClient('mongodb://test:test@localhost',27017)
db = client.kakao