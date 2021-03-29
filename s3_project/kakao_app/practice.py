from pymongo import MongoClient
from kakao_analyze import tokenize, get_count
client = MongoClient('localhost', 27017)

db = client.kakao

db.user.delete_all