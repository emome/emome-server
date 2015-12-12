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


    def user_login(self, name, _id):
        return self.app.post('/user', data=dict(
            name=name,
            _id=_id
        ))

   
    def test_login(self):
        print("Test: user_login")

        num_user = server.mongo.db.users.find({'_id': "000000"}).count()
        assert num_user == 0
        rv = self.user_login("Jean", "000000")
        assert {'status': "new user"} == json.loads(rv.data)
        num_user = server.mongo.db.users.find({'_id': "000000"}).count()
        assert num_user == 1
        rv = self.user_login("Jean", "000000")
        assert {'status': "existing user"} == json.loads(rv.data)
        num_user = server.mongo.db.users.find({'_id':"000000"}).count()
        assert num_user == 1


    def get_scenario_dict(self):
        return self.app.get('/scenario')
    

    def test_get_scenario_dict(self):
        print("Test: get scenario list")

        rv = self.get_scenario_dict()
        scenario_dict = loads(rv.data)['data']

        db_scenario_collection = server.mongo.db.scenarios.find()
        db_scenario_dict = {}
        for scenario in db_scenario_collection:
            db_scenario_dict[scenario['_id']] = scenario['name']

        assert len(db_scenario_dict) == len(scenario_dict)
        for scenario_id in db_scenario_dict:
            assert str(scenario_id) in scenario_dict
            assert scenario_dict[str(scenario_id)] == db_scenario_dict[scenario_id]


    def make_suggestion(self, user_id, emotion, scenario_id, content, message):
        return self.app.post('/suggestion', data=dict(
            user_id=user_id,
            emotion=simplejson.dumps(emotion),
            scenario_id=scenario_id,
            content=simplejson.dumps(content),
            message=message
        ))


    def build_scenario(self):
        server.mongo.db.scenarios.insert_many([
            {'_id': '0', 'name': "bossy boss"},
            {'_id': '1', 'name': "rainy day sucks"},
            {'_id': '2', 'name': "tired of routine tasks"},
            {'_id': '3', 'name': "insomnia"}
        ])


    def create_emotion(self):
        emotion = {
            server.EMOTION_SAD: 1,
            server.EMOTION_FRUSTRATED: 3,
            server.EMOTION_ANGRY: 0,
            server.EMOTION_ANXIOUS: 1
        }
        return emotion


    def test_get_suggestion(self):
        print "Test: get suggestion"

        # setup
        emotion = self.create_emotion()
        self.user_login("Jean", "000000")
        content = self.create_content()
        rv = self.make_suggestion("000000", emotion, '2', content, "Love this song!")
        rv = self.make_suggestion("000000", emotion, '2', content, "Love this song!")
        rv = self.make_suggestion("000000", emotion, '2', content, "Love this song!")
        
        print("check: load suggestions")
        results = self.app.get('/suggestion', data=dict(
            user_id="000000",
            scenario_id = "2",
            emotion=simplejson.dumps(emotion)
        ))
        assert "success" == simplejson.loads(results.data)['status']
        assert len(simplejson.loads(results.data)['data']) <= 10

    
    def create_content(self):
        content = {
            'type': "spotify",
            'data': "9999999"
        }    
        return content


    def test_make_suggestion(self):
        print("Test: make suggestion")
        # setup
        emotion = self.create_emotion()
        content = self.create_content()
        self.user_login("Jean", "000000")
 
        # check: normal
        print("check: normal")
        rv = self.make_suggestion("000000", emotion, '2', content, "Love this song!")
        assert rv.status_code == status.HTTP_200_OK
        data = simplejson.loads(str(rv.data))
        assert "success" == data["status"]
        cursor_suggestion = server.mongo.db.suggestions.find({'_id': data['data']})
        assert 1 == cursor_suggestion.count()
        assert "000000" == cursor_suggestion[0]['user_id']
        assert emotion == cursor_suggestion[0]['emotion']
        assert '2' == cursor_suggestion[0]['scenario_id']
        assert "spotify" == cursor_suggestion[0]['content']['type']
        assert "9999999" == cursor_suggestion[0]['content']['data']
        assert "Love this song!" == cursor_suggestion[0]['message']        

        # check: unregistered user
        print("check: unregistered user")
        rv = self.make_suggestion("100", emotion, '2', content, "Love this song!")
        assert rv.status_code == status.HTTP_403_FORBIDDEN

        # check: invalid emotion values
        print("check: invalid emotion values")
        emotion[server.EMOTION_SAD] = 13
        rv = self.make_suggestion("000000", emotion, '2', content, "Love this song!")
        assert rv.status_code == status.HTTP_400_BAD_REQUEST
        emotion[server.EMOTION_SAD] = 1

        # check: invalid scenario id
        print("check: invalid scenario id")

        rv = self.make_suggestion("000000", emotion, 5, content, "Love this song!")
        assert rv.status_code == status.HTTP_400_BAD_REQUEST

        # check: invalid suggestion
        print("check: invalid content")
        content_miss_type = {'data': 999}
        rv = self.make_suggestion("000000", emotion, '2', content_miss_type, "Love this song!")
        assert rv.status_code == status.HTTP_400_BAD_REQUEST
        content_miss_data = {'type': "Spotify"}
        rv = self.make_suggestion("000000", emotion, '2', content_miss_data, "Love this song!")
        assert rv.status_code == status.HTTP_400_BAD_REQUEST


    def take_suggestion(self, user_id, suggestion_id, emotion, scenario_id):
        return self.app.post('/history', data=dict(
            user_id=user_id,
            suggestion_id=suggestion_id,
            emotion=simplejson.dumps(emotion),
            scenario_id=scenario_id
        ))


    def test_take_action(self):
        print("Test: take suggestion")

        # setup
        print("check: setup")
        emotion = self.create_emotion()
        content = self.create_content()
        
        self.user_login("Jean", "000000")
        rv = self.make_suggestion("000000", emotion, '2', content, "Love this song!")
        data = simplejson.loads(str(rv.data))
        suggestion_id = data['data']

        # check: normal
        print("check: normal")
        rv = self.take_suggestion("000000", suggestion_id, emotion, '3')
        data = simplejson.loads(str(rv.data))
        history_id = data['data']
        cursor_history = server.mongo.db.histories.find({'_id': data['data']})
        assert "000000" == cursor_history[0]['user_id']
        assert suggestion_id == cursor_history[0]['suggestion_id']
        assert emotion == cursor_history[0]['emotion']
        assert '3' == cursor_history[0]['scenario_id']

        # check: unregisted user
        print("check: unregistered user")
        rv = self.take_suggestion("100", suggestion_id, emotion,3)
        assert rv.status_code == status.HTTP_403_FORBIDDEN

        # check: invalid suggestion id
        print("check: invalid suggestion id")
        rv = self.take_suggestion("000000", "123", emotion, 3)
        assert rv.status_code == status.HTTP_403_FORBIDDEN


    def get_history(self, history_id):
        return self.app.get('/history/'+history_id)


    def give_feedback(self, history_id, rating):
        return self.app.put('/history/'+history_id, data={'rating': rating})


    def test_give_feedback(self):
        print("Test: give feedback")

        # setup
        print("check: setup")
        emotion = self.create_emotion()
        content = self.create_content()
        
        self.user_login("Jean", "000000")
        rv = self.make_suggestion("000000", emotion, '2', content, "Love this song!")
        data = simplejson.loads(str(rv.data))
        suggestion_id = data['data']

        # get history
        print("check: get history")
        rv = self.take_suggestion("000000", suggestion_id, emotion, '3')
        data = simplejson.loads(str(rv.data))
        history_id = data['data']
        cursor_history = server.mongo.db.histories.find({'_id': history_id})
        assert "000000" == cursor_history[0]['user_id']
        assert suggestion_id == cursor_history[0]['suggestion_id']
        assert emotion == cursor_history[0]['emotion']
        assert '3' == cursor_history[0]['scenario_id']
        
        rv = self.get_history(history_id)
        data = simplejson.loads(str(rv.data))

        # give feedback
        print("check: give feedback")
        rating = 5
        rv = self.give_feedback(history_id, rating)
        data = simplejson.loads(str(rv.data))
        cursor_history = server.mongo.db.histories.find({'_id': history_id})
        assert rating == cursor_history[0]['rating']


if __name__ == '__main__':
    unittest.main()
