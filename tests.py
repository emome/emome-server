import os
import server
import unittest
import tempfile
import flask
import flask.ext.pymongo
import simplejson
from bson.json_util import dumps
from bson.objectid import ObjectId


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
        server.app.config["TESTING"] = True
        server.app.config["TEST_DBNAME"] = self.dbname
        server.mongo = flask.ext.pymongo.PyMongo(server.app, config_prefix="TEST")
        server.mongo.cx.drop_database(self.dbname)

    def tearDown(self):
        server.mongo.cx.drop_database(self.dbname)
        server.app.extensions['pymongo'].pop('TEST')
        super(FlaskPyMongoTest, self).tearDown()

    def login(self, name, fb_id):
        return self.app.post("/fb_login", data=dict(
            name = name,
            fb_id = fb_id
        ))
   
    def test_login(self):
        num_user = server.mongo.db.users.find({"_id":"000000"}).count()
        assert num_user == 0
        rv = self.login("Jean", "000000")
        assert '{"status": "new user"}' == rv.data
        num_user = server.mongo.db.users.find({"_id":"000000"}).count()
        assert num_user == 1
        rv = self.login("Jean", "000000")
        assert '{"status": "existing user"}' == rv.data
        num_user = server.mongo.db.users.find({"_id":"000000"}).count()
        assert num_user == 1

    def make_suggestion(self, user_id, emotion, scenario_id, content, message):
        return self.app.post("/make_suggestion", data=dict(
            user_id = user_id,
            emotion = dumps({
                "sad": emotion["sad"],
                "frustrated": emotion["frustrated"],
                "angry": emotion["angry"],
                "fearful": emotion["fearful"]               
            }),
            scenario_id = scenario_id,
            content = content,
            message = message
        ))

    def build_scenario(self):
        server.mongo.db.scenarios.insert_many([
            {"_id": 0, "name": "bossy boss"},
            {"_id": 1, "name": "rainy day sucks"},
            {"_id": 2, "name": "tired of routine tasks"},
            {"_id": 3, "name": "insomnia"}
        ])

    def test_make_suggestion(self):
        self.build_scenario()
        emotion = {
            "sad": 1,
            "frustrated": 3,
            "angry": 0,
            "fearful": 1
        }
        self.login("Jean", "000000")
        
        # check: normal
        rv = self.make_suggestion("000000", emotion, 2, "spotify", "Love this song!")
        assert rv.status_code == 200
        data = simplejson.loads(str(rv.data))
        assert "success" == data["status"]
        cursor_suggestion = server.mongo.db.suggestions.find({"_id": ObjectId(data["_id"])})
        assert 1 == cursor_suggestion.count()
        assert "000000" == cursor_suggestion[0]["user_id"]
        assert emotion == cursor_suggestion[0]["emotion"]
        assert 2 == cursor_suggestion[0]["scenario_id"]
        assert "spotify" == cursor_suggestion[0]["content"]
        assert "Love this song!" == cursor_suggestion[0]["message"]
        
        # check: unregistered user
        rv = self.make_suggestion("100", emotion, 2, "spotify", "Love this song!")
        assert rv.status_code == 403

        # check: invalid emotion values
        emotion["sad"] = 13
        rv = self.make_suggestion("000000", emotion, 2, "spotify", "Love this song!")
        assert rv.status_code == 403
        emotion["sad"] = 1

        # check: invalid scenario id
        rv = self.make_suggestion("000000", emotion, 5, "spotify", "Love this song!")
        assert rv.status_code == 403


if __name__ == '__main__':
    unittest.main()
