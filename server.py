from flask import Flask
from flask import request
import json

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def static_interaction():
	if request.method == 'POST':
		return json.dumps({'sad': request.form['sad'], \
		'frustrated': request.form['frustrated'], \
		'anger': request.form['anger'], \
		'fear': request.form['fear']})
	else:
		return json.dumps([ \
		{
			'user_id': 0000,\
			'suggestion_id': 0000, \
			'message': 'Hey, last time I felt sad in a rainy day, I came across this playlist. It really helped.',\
			'type': 'Spotify', \
			'uri': 'spotify://user:spotify:playlist:5eSMIpsnkXJhXEPyRQCTSc'}, \
		{
			'user_id': 0001, \
			'suggestion_id': 0001, \
			'message': 'How about having some hot chocolate today? I feel much better having it in such a cold day :)',\
			'type': 'Yelp', \
			'uri': 'yelp:///biz/the-city-bakery-new-york'} ])

if __name__ == '__main__':
	app.run()