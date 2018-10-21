import json

from flask import Flask
from flask import Response
from flask import request
from flask_compress import Compress
from flask_cors import CORS

from sentiment import get_sentiment

app = Flask(__name__)
Compress(app)
CORS(app)


def get_arg(key, default=None, type=str):
    return request.args.get(key, default, type)


def as_json(data):
    return Response(json.dumps(data), mimetype='application/json')


@app.route("/")
def hello():
    area = get_arg('area', 'Melbourne')
    return as_json({'area': area})


@app.route('/sentiment')
def sentiment():
    city = get_arg('city', 'melbourne').lower()
    years = list(map(int, get_arg('years', '2014,2015,2016,2017,2018').split(',')))
    weekdays = list(map(int, get_arg('weekdays', '0,1,2,3,4,5,6').split(',')))
    return as_json(get_sentiment(city, years, weekdays))


if __name__ == '__main__':
    app.debug = True
    app.run()
