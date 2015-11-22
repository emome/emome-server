import os
import server
import unittest
import tempfile

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.app = server.app.test_client()

    def tearDown(self):
        pass

    def test_emome_suggestions(self):
    	rv = self.app.get('/')
        assert '[{"suggestion_id": 0, "message": "Hey, last time I felt sad in a rainy day, I came across this playlist. It really helped.", "user_id": 0, "uri": "spotify://user:spotify:playlist:5eSMIpsnkXJhXEPyRQCTSc", "type": "Spotify"}, {"suggestion_id": 1, "message": "How about having some hot chocolate today? I feel much better having it in such a cold day :)", "user_id": 1, "uri": "yelp:///biz/the-city-bakery-new-york", "type": "Yelp"}]' == rv.data

if __name__ == '__main__':
    unittest.main()
