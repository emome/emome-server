from pymongo import MongoClient
from datetime import datetime
import time

client = MongoClient()
db = client['primer']

LOGIN_STATUS_NEW_USER = 0
LOGIN_STATUS_EXISTING_USER = 1

def fb_login(fb_id, name):
    coll_user = db['user']
    if coll_user.find({"_id": fb_id}).count() == 0:
        coll_user.insert_one({
            "_id": fb_id,
            "name": name,
            "join_time": datetime.now()
        })
        #return coll_user.find()
        return LOGIN_STATUS_NEW_USER
    else:
        return LOGIN_STATUS_EXISTING_USER
