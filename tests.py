import os
import server
import unittest
import flask
import flask.ext.pymongo
from flask.ext.api import status
import simplejson
from bson.json_util import dumps, loads
import json


class FlaskRequestTest(unittest.TestCase):

    def setUp(self):
        self.app = server.app.test_client()
        self.context = server.app.test_request_context('/')
        self.context.push()

    def tearDown(self):
        self.context.pop()


class FlaskPyMongoTest(FlaskRequestTest):

    def setUp(self):
        super(FlaskPyMongoTest, self).setUp()

        self.dbname = self.__class__.__name__
        server.app.config['TESTING'] = True
        server.app.config['TEST_DBNAME'] = self.dbname
        server.mongo = flask.ext.pymongo.PyMongo(server.app, config_prefix='TEST')
        server.mongo.cx.drop_database(self.dbname)

        self.build_scenario()

    def tearDown(self):
        server.mongo.cx.drop_database(self.dbname)
        server.app.extensions['pymongo'].pop('TEST')
        super(FlaskPyMongoTest, self).tearDown()

    def login(self, name, _id):
        return self.app.post('/login', data=dict(
            name = name,
            _id = _id
        ))
   
    def test_login(self):
        print("Test: login")

        num_user = server.mongo.db.users.find({'_id': "000000"}).count()
        assert num_user == 0
        rv = self.login("Jean", "000000")
        assert {'status': "new user"} == json.loads(rv.data)
        num_user = server.mongo.db.users.find({'_id': "000000"}).count()
        assert num_user == 1
        rv = self.login("Jean", "000000")
        assert {'status': "existing user"} == json.loads(rv.data)
        num_user = server.mongo.db.users.find({'_id':"000000"}).count()
        assert num_user == 1

    def make_suggestion(self, user_id, emotion, scenario_id, content, message):
        return self.app.post('/suggestion', data=dict(
            user_id = user_id,
            emotion = dumps(emotion),
            scenario_id = scenario_id,
            content = content,
            message = message
        ))

    def build_scenario(self):
        server.mongo.db.scenarios.insert_many([
            {'_id': 0, 'name': "bossy boss"},
            {'_id': 1, 'name': "rainy day sucks"},
            {'_id': 2, 'name': "tired of routine tasks"},
            {'_id': 3, 'name': "insomnia"}
        ])

    def create_emotion(self):
        emotion = {
            server.EMOTION_SAD: 1,
            server.EMOTION_FRUSTRATED: 3,
            server.EMOTION_ANGRY: 0,
            server.EMOTION_ANXIOUS: 1
        }
        return emotion

    def test_make_suggestion(self):
        print("Test: make suggestion")
        # setup
        emotion = self.create_emotion()
        self.login("Jean", "000000")
 
        # check: normal
        print "check: normal"
        rv = self.make_suggestion("000000", emotion, 2, "spotify", "Love this song!")
        assert rv.status_code == status.HTTP_200_OK
        data = simplejson.loads(str(rv.data))
        assert "success" == data["status"]
        cursor_suggestion = server.mongo.db.suggestions.find({'_id': data['_id']})
        assert 1 == cursor_suggestion.count()
        assert "000000" == cursor_suggestion[0]['user_id']
        assert emotion == cursor_suggestion[0]['emotion']
        assert 2 == cursor_suggestion[0]['scenario_id']
        assert "spotify" == cursor_suggestion[0]['content']
        assert "Love this song!" == cursor_suggestion[0]['message']        

        # check: unregistered user
        print "check: unregistered user"
        rv = self.make_suggestion("100", emotion, 2, "spotify", "Love this song!")
        assert rv.status_code == status.HTTP_403_FORBIDDEN

        # check: invalid emotion values
        print "check: invalid emotion values"
        emotion[server.EMOTION_SAD] = 13
        rv = self.make_suggestion("000000", emotion, 2, "spotify", "Love this song!")
        assert rv.status_code == status.HTTP_400_BAD_REQUEST
        emotion[server.EMOTION_SAD] = 1

        # check: invalid scenario id
        print "check: invalid scenario id"

        rv = self.make_suggestion("000000", emotion, 5, "spotify", "Love this song!")
        assert rv.status_code == status.HTTP_400_BAD_REQUEST

    
    def take_suggestion(self, user_id, suggestion_id, emotion, scenario_id):
        return self.app.post('/history', data=dict(
            user_id = user_id,
            suggestion_id = suggestion_id,
            emotion = dumps(emotion),
            scenario_id = scenario_id
        ))


    def test_take_action(self):
        print("Test: take suggestion")

        # setup
        emotion = self.create_emotion()
        self.login("Jean", "000000")
        rv = self.make_suggestion("000000", emotion, 2, "spotify", "Love this song!") 
        data = simplejson.loads(str(rv.data))
        suggestion_id = data['_id']

        # check: normal
        print "check: normal"
        rv = self.take_suggestion("000000", suggestion_id, emotion, 3)
        data = simplejson.loads(str(rv.data))
        history_id = data['_id']
        cursor_history = server.mongo.db.histories.find({'_id': data['_id']})
        assert "000000" == cursor_history[0]['user_id']
        assert suggestion_id == cursor_history[0]['suggestion_id']
        assert emotion == cursor_history[0]['emotion']
        assert 3 == cursor_history[0]['scenario_id']

        # check: unregisted user
        print "check: unregistered user"
        rv = self.take_suggestion("100", suggestion_id, emotion,3)
        assert rv.status_code == status.HTTP_403_FORBIDDEN

        # check: invalid suggestion id
        print "check: invalid suggestion id"
        rv = self.take_suggestion("000000", "123", emotion, 3)
        assert rv.status_code == status.HTTP_403_FORBIDDEN


if __name__ == '__main__':
    unittest.main()
