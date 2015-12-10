from flask import Flask, request
from flask.ext.pymongo import PyMongo
from datetime import datetime
import simplejson
from bson.json_util import dumps
from bson import json_util
from bson.objectid import ObjectId
from flask.ext.api import status
from flask_restful import Resource, Api, reqparse, abort
import json
#import extract_songs



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

Scenario:
    pass scenario collection to the frontend[get: scenario_list]

Suggestion: 
    see suggestion[get: message, content]
    make suggestion[post to suggestion table: user_id, emotion, scenario_id, message, content]

SuggestionImpact:
    see effect[get:impact]    

History:
    take action[post to history table: user_id, suggestion_id, emotion, scenario_id]
    give feedback[put: history_id, rating, feedback]
'''


user_parser = reqparse.RequestParser()
user_parser.add_argument('_id', type=str)
user_parser.add_argument('name', type=str)


class User(Resource):

    # user login
    def post(self):            
        args = user_parser.parse_args()
        if mongo.db.users.find({'_id': args['_id']}).count() == 0:
            mongo.db.users.insert_one({
                '_id': args['_id'],
                'name': args['name'],
                'join_time': datetime.now()
            })
            return {'status': "new user"}
        else:
            return {'status': "existing user"}



class Scenario(Resource):

    # pass scenario collection to the frontend
    def get(self):
        with app.app_context():
            scenario_collection = mongo.db.scenarios.find()
    
        scenario_dict = {}   
        for scenario in scenario_collection:
            scenario_dict[scenario['_id']] = scenario['name']

        return {'data': scenario_dict, 'status': "success"}



def emotion(emotion):

    emotion = json.loads(emotion)

    if type(emotion) != dict:
        raise ValueError('Expected a dict.')

    for e in EMOTION_KEYS:
        if e not in emotion:
            raise KeyError('Expected key: ' + e)
        if not 0 <= int(emotion[e]) <= 10:
            raise ValueError('Expected value between 0 and 10')
    
    return emotion


def scenario_id(scenario_id):
    
    if type(scenario_id) != unicode:
        raise ValueError('Expected a unicode.')

    num_scenarios = 0
    with app.app_context():
        num_scenarios = mongo.db.scenarios.count()
    
    if int(scenario_id) not in range(num_scenarios):
        raise ValueError('Expected scenario id to be less than '+str(num_scenarios))

    return scenario_id


def content(content):

    content = json.loads(content)

    if type(content) != dict:
        raise ValueError('Expected {\'type\': API_TYPE, \'data\': DATA}')

    if 'type' not in content:
        raise ValueError('Expected an Api type')

    if 'data' not in content:
        raise ValueError('Expected suggestion data')

    return content

suggestion_parser = reqparse.RequestParser()
suggestion_parser.add_argument('user_id', type=str, required=True)
suggestion_parser.add_argument('emotion', type=emotion, required=True)
suggestion_parser.add_argument('scenario_id', type=scenario_id, required=True)
suggestion_parser.add_argument('content', type=content, required=True)
suggestion_parser.add_argument('message', type=str, required=True)

get_suggestion_parser = reqparse.RequestParser()
get_suggestion_parser.add_argument('user_id', type=str, required=True)
get_suggestion_parser.add_argument('emotion', type=emotion, required=True)
get_suggestion_parser.add_argument('scenario_id', type=scenario_id, required=True)


class Suggestion(Resource):

    # see suggestion
    def get(self):
        args = get_suggestion_parser.parse_args()
        print type(args), args
        
        '''
        # do some processing to retrieve suggestions
        sad = args['emotion']['sad']
        frustrated = args['emotion']['frustrated']
        angry = args['emotion']['angry']
        anxious = args['emotion']['anxious']                
        print sad, frustrated, angry, anxious
        
        songs = extract_songs.extract_songs(int(sad), int(frustrated), int(angry), int(anxious))
        print songs        
        '''

        cursor = mongo.db.suggestions.find()
        print cursor.count()
        suggestion_list = []
        for data in cursor[:5]:
            suggestion_list.append({
                'suggestion_id': data['_id'], 
                'content': {
                    'type': data['content']['type'],
                    'data': data['content']['data']
                },
                'message': data['message'],
            })

        return {'data': suggestion_list, 'status': "success"}


        '''
        suggestion_list = []
        suggestion_list.append({'suggestion_id': "12345", 'content': {'type': 'Yelp', 'data': '7777777'}, 'message': "Hi, how are you? Take some rest :)"})
        
        return {'data': suggestion_list, 'status': "success"}
        '''


    # make suggestion
    def post(self):
        args = suggestion_parser.parse_args() 
        
        # check if the user exists
        if not validate_user(args['user_id']):
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
            'scenario_id': args['scenario_id'],
            'time': datetime.now(),
            'content': args['content'],
            'message': args['message'],
            'impact': None
        })
        return {'data': object_id, 'status': "success"}


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


historyList_parser = reqparse.RequestParser()
historyList_parser.add_argument('user_id', type=str, required=True)
historyList_parser.add_argument('suggestion_id', type=str, required=True)
historyList_parser.add_argument('emotion', type=emotion, required=True)
historyList_parser.add_argument('scenario_id', type=scenario_id, required=True)

class HistoryList(Resource):

    # take action
    def post(self):
        args = historyList_parser.parse_args() 
 
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
            'scenario_id': args['scenario_id'],
            'time': datetime.now(),
            'rating': None,
            'feedback': None,
            'drawing': None
        })

        return {'data': object_id, 'status': "success"}



def history_id(history_id):
    
    if mongo.db.histories.find({'_id': history_id}).count() == 0:
        raise ValueError('Invalid history id')

    return history_id


history_parser = reqparse.RequestParser()
history_parser.add_argument('rating', type=int, choices=range(1,6), required=True)


class History(Resource):
    
    def get(self, history_id):
        
        if mongo.db.histories.find({'_id': history_id}).count() == 0:
            abort(404, message="History {} doesn't exist".format(history_id))
        
        cursor = mongo.db.histories.find({'_id': history_id})
        data = cursor[0]
        return {
                    'data': {
                        'user_id': data['user_id'],
                        'scenario_id': data['scenario_id'],
                        'suggestion_id': data['suggestion_id'],
                        'history_id': data['_id']
                    }, 
                    'status': "success"
                }

    def put(self, history_id):
       
        args = history_parser.parse_args() 
        result = mongo.db.histories.update_one(
            {'_id': history_id},
            {
                "$set": {'rating': args['rating']}
            }
        )
        return {'data': "nice job!", 'status': "success"}




api.add_resource(User, '/user')
api.add_resource(Scenario, '/scenario')
api.add_resource(Suggestion, '/suggestion')
api.add_resource(HistoryList, '/history')
api.add_resource(History, '/history/<history_id>')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
