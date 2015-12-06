from flask import Flask
from flask.ext.pymongo import PyMongo
from flask import request
from datetime import datetime
import simplejson
from bson.json_util import dumps
from bson import json_util
from bson.objectid import ObjectId
from flask.ext.api import status
from flask_restful import Resource, Api, reqparse
import json


EMOTION_SAD = 'sad'
EMOTION_FRUSTRATED = 'frustrated'
EMOTION_ANGRY = 'angry'
EMOTION_ANXIOUS = 'anxious'
EMOTION_KEYS = [EMOTION_SAD, EMOTION_FRUSTRATED, EMOTION_ANGRY, EMOTION_ANXIOUS]

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'primer'
mongo = PyMongo(app,config_prefix='MONGO')
api = Api(app)



'''
Login: 
    login[post: user_id, name]

Suggestion: 
    see suggestion[get: message, content]
    make suggestion[post to suggestion table: user_id, emotion, scenario_id, message, content]

SuggestionImpact:
    see effect[get:impact]    

History:
    take action[post to history table: user_id, suggestion_id, emotion, scenario_id]
    give feedback[put: history_id, rating, feedback]
'''


login_parser = reqparse.RequestParser()
login_parser.add_argument('_id', type=str)
login_parser.add_argument('name', type=str)


class Login(Resource):

    # facebook login
    def post(self):            
        args = login_parser.parse_args()
        if mongo.db.users.find({'_id': args['_id']}).count() == 0:
            mongo.db.users.insert_one({
                '_id': args['_id'],
                'name': args['name'],
                'join_time': datetime.now()
            })
            return {'status': "new user"}
        else:
            return {'status': "existing user"}



def emotion(emotion):

    emotion = json.loads(emotion)

    if type(emotion) != dict:
        raise ValueError('Expected a dict.')

    for e in EMOTION_KEYS:
        if not emotion.has_key(e):
            raise KeyError('Expected key: ' + e)
        if not 0 <= int(emotion[e]) <= 10:
            raise ValueError('Expected value between 0 and 10')
    
    return emotion



with app.app_context():
    num_scenarios = mongo.db.scenarios.count()


suggestion_parser = reqparse.RequestParser()
suggestion_parser.add_argument('user_id', type=str, required=True)
suggestion_parser.add_argument('emotion', type=emotion, required=True)
suggestion_parser.add_argument('scenario_id', type=int, choices=range(num_scenarios), required=True)
suggestion_parser.add_argument('content', type=str, required=True)
suggestion_parser.add_argument('message', type=str, required=True)


class Suggestion(Resource):

    # see suggestion
    def get(self):
        return {'status': "under construction..."}

    # make suggestion
    def post(self):
        args = suggestion_parser.parse_args() 
 
        # check if the user exists
        if validate_user(args['user_id']) == False:
            return {'err_msg': "unregistered user"}, status.HTTP_403_FORBIDDEN

        object_id = str(ObjectId())
        mongo.db.suggestions.insert_one({
            '_id': object_id,
            'user_id': args['user_id'],
            'emotion': {
                EMOTION_SAD: int(args['emotion'][EMOTION_SAD]),
                EMOTION_FRUSTRATED: int(args['emotion'][EMOTION_FRUSTRATED]),
                EMOTION_ANGRY: int(args['emotion'][EMOTION_ANGRY]),
                EMOTION_ANXIOUS: int(args['emotion'][EMOTION_ANXIOUS])
            },
            'scenario_id': int(args['scenario_id']),
            'time': datetime.now(),
            'content': args['content'],
            'message': args['message'],
            'impact': None
        })
        return {'_id': object_id, 'status': "success"}


def validate_user(user_id):
    if mongo.db.users.find({'_id': user_id}).count() == 0:
        # unregistered uesr
        return False
    else:
        # registered user
        return True


def validate_suggestion(suggestion_id):
    if mongo.db.suggestions.find({'_id': suggestion_id}).count() == 0:
        # invalid suggestion id
        return False
    else:
        # valid suggestion id
        return True


history_parser = reqparse.RequestParser()
history_parser.add_argument('user_id', type=str, required=True)
history_parser.add_argument('suggestion_id', type=str, required=True)
history_parser.add_argument('emotion', type=emotion, required=True)
history_parser.add_argument('scenario_id', type=int, choices=range(num_scenarios), required=True)

class History(Resource):

    # take action
    def post(self):
        args = history_parser.parse_args() 
 
        # check if the user exists
        if not validate_user(args['user_id']):
            return {'err_msg': "unregistered user"}, status.HTTP_403_FORBIDDEN

        # check if the suggestion exists
        if not validate_suggestion(args['suggestion_id']):
            return {'err_msg': "invalid suggestion id"}, status.HTTP_403_FORBIDDEN

        object_id = str(ObjectId())
        mongo.db.histories.insert_one({
            '_id': object_id,
            'user_id': args['user_id'],
            'suggestion_id': args['suggestion_id'],
            'emotion': {
                EMOTION_SAD: int(args['emotion'][EMOTION_SAD]),
                EMOTION_FRUSTRATED: int(args['emotion'][EMOTION_FRUSTRATED]),
                EMOTION_ANGRY: int(args['emotion'][EMOTION_ANGRY]),
                EMOTION_ANXIOUS: int(args['emotion'][EMOTION_ANXIOUS])
            },
            'scenario_id': int(args['scenario_id']),
            'time': datetime.now(),
            'rating': None,
            'feedback': None,
            'drawing': None
        })
        return {'_id': object_id, 'status': "success"}



api.add_resource(Login, '/login')
api.add_resource(Suggestion, '/suggestion')
api.add_resource(History, '/history')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
