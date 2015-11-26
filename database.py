from pymongo import MongoClient
from datetime import datetime
import time
import simplejson as json

client = MongoClient()
db = client['primer']

LOGIN_STATUS_NEW_USER = 0
LOGIN_STATUS_EXISTING_USER = 1
SUCCESS = 3

def fb_login(fb_id, name):
    coll_user = db['users']
    if coll_user.find({"_id": fb_id}).count() == 0:
        coll_user.insert_one({
            "_id": fb_id,
            "name": name,
            "join_time": datetime.now()
        })
        return LOGIN_STATUS_NEW_USER
    else:
        return LOGIN_STATUS_EXISTING_USER

def make_suggestion(fb_id, emotion, scenario_id, content, message):
    coll_suggestion = db['suggestions']
    emotions = json.loads(str(emotion))
    coll_suggestion.insert_one({
        "user_id": fb_id,
        "emotion": {
            "sad": emotions['sad'],
            "frustrated": emotions['frustrated'],
            "angry": emotions['angry'],
            "fearful": emotions['fearful']
        },
        "scenario_id": scenario_id,
        "time": datetime.now(),
        "content": content,
        "message": message
    })
    return SUCCESS

def take_suggestion(fb_id, suggestion_id, emotion, impact, feedback):
    coll_history = db['histories']
    emotions = json.loads(str(emotion))
    coll_history.insert_one({
        "user_id": fb_id,
        "time": datetime.now(),
        "suggestion_id": suggestion_id,
        "emotion": {
            "sad": emotions['sad'],
            "frustrated": emotions['frustrated'],
            "angry": emotions['angry'],
            "fearful": emotions['fearful']
        },
        "impact": impact,
        "feedback": feedback
    })
    return SUCCESS
