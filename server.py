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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
