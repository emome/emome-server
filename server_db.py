from flask import Flask
from flask.ext.pymongo import PyMongo
from flask import request
from datetime import datetime
import simplejson
from bson.json_util import dumps

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'primer'
mongo = PyMongo(app,config_prefix='MONGO')

@app.route('/fb_login', methods=['POST'])
def login():
    if request.method == 'POST':
        if mongo.db.users.find({"_id": request.form['fb_id']}).count() == 0:
            mongo.db.users.insert_one({
                "_id": request.form['fb_id'],
                "name": request.form['name'],
                "join_time": datetime.now()
            })
            return dumps({"status": "new user"})
        else:
            return dumps({"status": "existing user"})

@app.route('/make_suggestion', methods=['POST'])
def make_suggestion():
    if request.method == 'POST':
        emotions = simplejson.loads(str(request.form['emotion']))
        mongo.db.suggestions.insert_one({
            "user_id": request.form['fb_id'],
            "emotion": {
                "sad": emotions['sad'],
                "frustrated": emotions['frustrated'],
                "angry": emotions['angry'],
                "fearful": emotions['fearful']
            },
            "scenario_id": request.form['scenario_id'],
            "time": datetime.now(),
            "content": request.form['content'],
            "message": request.form['message']
        })
        return dumps({"status": "success"})
    else:
        return dumps({"status": "fail"})

@app.route('/take_suggestion', methods=['POST'])
def take_suggestion():
    if request.method == 'POST':
        emotions = simplejson.loads(str(request.form['emotion']))
        mongo.db.histories.insert_one({
            "user_id": request.form['fb_id'],
            "time": datetime.now(),
            "suggestion_id": request.form['suggestion_id'],
            "emotion": {
                "sad": emotions['sad'],
                "frustrated": emotions['frustrated'],
                "angry": emotions['angry'],
                "fearful": emotions['fearful']
            },
            "impact": request.form['impact'],
            "feedback": request.form['feedback']
        })
        return dumps({"status": "success"})
    else:
        return dumps({"status": "fail"})

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
