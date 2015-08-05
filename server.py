#!.pyenv/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Farsheed Ashouri'

"""
   ___              _                   _
  / __\_ _ _ __ ___| |__   ___  ___  __| |
 / _\/ _` | '__/ __| '_ \ / _ \/ _ \/ _` |
/ / | (_| | |  \__ \ | | |  __/  __/ (_| |
\/   \__,_|_|  |___/_| |_|\___|\___|\__,_|

Just remember: Each comment is like an apology!
Clean code is much better than Cleaner comments!
'''


'''
@desc: server.py
@author: F.Ashouri
"""

from gevent import monkey
monkey.patch_all()

from flask import Flask, request, abort, jsonify
from flask.ext.mako import render_template
from flask.ext.mako import MakoTemplates
from bson.json_util import dumps
import ujson
from utils import general, server_tools
from utils.parsers import alfred
from models.db import mongo
import hashlib
from copy import copy

__version__ = general.getVersion()


'''Register extensions'''
app = Flask(__name__)
mako = MakoTemplates(app)

app.config.update()



@app.route("/")
def index():
    body = render_template('server.tpl')
    title = 'Server Dashboard'
    data = render_template('index.tpl', body=body, title=title,
                           version=__version__)
    return data


@app.route('/api/ping', methods=['POST'])
def ping():
    ''' This method pings server'''
    client = request.remote_addr

    '''Find if it's client's first ping'''
    clientNewRawData = request.data
    if clientNewRawData:
        clientNewInfo = copy(general.unpack(clientNewRawData))
        clientNewInfo['ip'] = client
        if clientNewInfo:
            data = {'ip':client, 'info':clientNewInfo, 'last_ping':general.now()}
            slave = mongo.db.slaves.update({'ip':client}, data, upsert=True)  ## update if find or insert new
    return general.pack({'message':'PONG', 'clientInfo':clientNewInfo, 'last_ping':general.now()})




@app.route('/api/addJob', methods=['POST'])
def addJob():
    """Gets user uploded job description and add it to jobs"""
    data = general.unpack(request.data)
    job = alfred.parse(data.get('job'))
    client = request.remote_addr
    jobHash = hashlib.md5(data.get('job')).hexdigest()  ## hash of actual uploaded file
    if job:
        newJob = {
            'name':data.get('filename'),
            'category':data.get('category'),
            'data':job,
            'md5': jobHash,
            'status':'likely',
            'datetime':general.now(),
            'owner': client,
            'priority':500,
            'is_active':True,
            'progress':0,
        }
        new = mongo.db.jobs.update({'md5':jobHash}, newJob, upsert=True)
        server_tools.createNewTasks(jobHash)
        return general.pack(newJob)


@app.route('/api/dbtest/<entery>', methods=['GET', 'POST'])
def dbtest(entery):
    """Simple mongodb database test"""
    if request.method == 'POST':
        if not request.data:
            abort(400)
        newData = ujson.loads(request.data)
        new = mongo.db.dbtest.insert({'key': entery, 'data': newData})
        return dumps(mongo.db.dbtest.find_one({'_id': new})), 201
    elif request.method == 'GET':
        data = mongo.db.dbtest.find({'key': entery})
        return dumps(data)

@app.route('/api/getJobsInfo')
def getJobsInfo():
    """List jobs information for client"""
    client = request.remote_addr
    jobs = server_tools.getClientJobsInformation(client)
    return general.pack(jobs)


if __name__ == "__main__":

    def run_debug():
        app.run(
            host='0.0.0.0',
            port=9001,
            debug=True,
        )

    def run_tornado():
        from tornado.wsgi import WSGIContainer
        from tornado.httpserver import HTTPServer
        from tornado.ioloop import IOLoop

        http_server = HTTPServer(WSGIContainer(app))
        http_server.listen(9001)
        IOLoop.instance().start()

    def run_gevent():
        from gevent.wsgi import WSGIServer

        http_server = WSGIServer(('0.0.0.0', 9001), app)
        http_server.serve_forever()

    #run_tornado()
    run_debug()
    #run_gevent()

