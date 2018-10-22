import json
import sys

from flask import Flask
from flask import Response
from flask import redirect
from flask import request
from flask_compress import Compress
from flask_cors import CORS
from flask import redirect, url_for

from sentiment import get_sentiment
from ldaSimple import get_topic

app = Flask(__name__, static_url_path='', static_folder='build')
Compress(app)
CORS(app)


def get_arg(key, default=None, type=str):
    return request.args.get(key, default, type)


def as_json(data):
    return Response(json.dumps(data), mimetype='application/json')


@app.route("/")
def index():
    return redirect('index.html')


@app.route('/sentiment')
def sentiment():
    city = get_arg('city', 'melbourne').lower()
    years = list(map(int, get_arg('years', '2014,2015,2016,2017,2018').split(',')))
    weekdays = list(map(int, get_arg('weekdays', '0,1,2,3,4,5,6').split(',')))
    return as_json(get_sentiment(city, years, weekdays))


@app.route('/topic', methods = ['POST', 'GET'])
def topic():
    if request.method == 'POST':
        weekday = request.form['weekday']
        startDate = request.form['startDate']
        startTime = request.form['startTime']
        endDate = request.form['endDate']
        endTime = request.form['endTime']
        suburb = request.form['suburb']
        city = request.form['city']
        topics = request.form['topics']
        keywords = request.form['keywords']
        return as_json(get_topic(weekday, startDate, startTime, endDate, endTime, suburb, city, topics, keywords))
    else:
        pass


if __name__ == '__main__':
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
        debug = False
    else:
        port = 5000
        debug = True

    app.run(host='0.0.0.0', port=port, debug=debug)
