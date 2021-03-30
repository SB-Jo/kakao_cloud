from pymongo import MongoClient
import os


client = MongoClient('mongodb://test:test@localhost',27017)
db = client.kakao

db.kakao.delete_many({'userid':'sbjo'})