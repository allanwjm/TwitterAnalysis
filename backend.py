import json

from flask import Flask
from flask import Response
from flask import request

app = Flask(__name__)


def get_arg(key, default=None, type=str):
    return request.args.get(key, default, type)


def as_json(data):
    return Response(json.dumps(data), mimetype='application/json')


@app.route("/")
def hello():
    area = get_arg('area', 'Melbourne')
    return as_json({'area': area})


if __name__ == '__main__':
    app.debug = True
    app.run()
