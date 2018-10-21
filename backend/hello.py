import json, ldaSimple
from flask import Flask, redirect, url_for, request, Response

app = Flask(__name__, static_url_path='', root_path='/home/ubuntu')


def get_arg(key, default=None, type=str):
    return request.args.get(key, default, type)


def as_json(data):
    return Response(json.dumps(data), mimetype='application/json')

@app.route("/")
def hello():
    weekday = get_arg('weekday', '0')
    startDate = get_arg('startDate', '2014-01-01')
    startTime = get_arg('startTime', '00:00:00')
    endDate = get_arg('endDate', '2014-12-31')
    endTime = get_arg('endTime', '23:59:59')
    suburb = get_arg('suburb', '402041047')
    city = get_arg('city', 'adelaide')
    topics = get_arg('topics', '5')
    keywords = get_arg('keywords', '5')
#    return as_json({'area2': area})
    return Response(json.dumps(ldaSimple.runTest(weekday, startDate, startTime, endDate, endTime, suburb, city, topics, keywords)), mimetype='application/json')

@app.route('/test')
def test():
    return app.send_static_file('index.html')
#    return Response(json.dumps(ldaSimple.runTest()), mimetype='application/json')


@app.route('/success/<name>')
def success(name):
    return 'welcome %s' % name

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
#        user = request.form['name']
        weekday = request.form['weekday']
        startDate = request.form['startDate']
        startTime = request.form['startTime']
        endDate = request.form['endDate']
        endTime = request.form['endTime']
        suburb = request.form['suburb']
        city = request.form['city']
        topics = request.form['topics']
        keywords = request.form['keywords']
        
#        return redirect(url_for('success', name = user))
        return Response(json.dumps(ldaSimple.runTest(weekday, startDate, startTime, endDate, endTime, suburb, city, topics, keywords)), mimetype='application/json')
    else:
        user = request.args.get('name')
        return redirect(url_for('success', name = user))
        

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
