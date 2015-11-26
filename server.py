from flask import Flask
from flask import request
import json
from bson.json_util import dumps
import database

app = Flask(__name__)

@app.route('/fb_login', methods=['POST'])
def login():
    if request.method == 'POST':
        login_status = database.fb_login(request.form['fb_id'], request.form['name'])
        if login_status == database.LOGIN_STATUS_NEW_USER:
            return dumps({"status": "new_user"})
        elif login_status == database.LOGIN_STATUS_EXISTING_USER:
            return dumps({"status": "existing_user"})

@app.route('/make_suggestion', methods=['POST'])
def make_suggestion():
    if request.method == 'POST':
        status = database.make_suggestion(request.form['fb_id'], request.form['measurement'], request.form['scenario_id'], request.form['content'], request.form['message'])
        if status == database.SUCCESS:
            return dumps({"status": "success"})

@app.route('/take_suggestion', methods=['POST'])
def take_suggestion():
    if request.method == 'POST':
        status = database.take_suggestion(request.form['fb_id'], request.form['suggestion_id'], request.form['emotion'], request.form['impact'], request.form['feedback'])
        if status == database.SUCCESS:
            return dumps({"status": "success"}) 

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
