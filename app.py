#!/usr/bin/env python
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
from flask.ext.basicauth import BasicAuth
from bson.json_util import dumps
from bson.objectid import ObjectId
import ujson
from utils import general, server_tools, client_tools
from utils.parsers import alfred
from models.db import mongo
import hashlib
from copy import copy
from clientAgent import ca

__version__ = general.getVersion()

username, password = server_tools.getServerCreditentionals()


'''Register extensions'''
app = Flask(__name__)
mako = MakoTemplates(app)

app.config.update()

app.config['BASIC_AUTH_USERNAME'] = username
app.config['BASIC_AUTH_PASSWORD'] = password

basic_auth = BasicAuth(app)


@app.route("/server")
@basic_auth.required
def server():
    return 'Server'


@app.route("/client")
def client():
    body = render_template('client.tpl')
    title = 'Client Dashboard'
    data = render_template('index.tpl', body=body, title=title,
                           version=__version__)
    return data


@app.route('/api/ping', methods=['POST'])
def ping():
    ''' This method pings server'''
    client = server_tools.getClientIp(request)
    '''Find if it's client's first ping'''
    clientNewRawData = ujson.loads(request.data)
    if clientNewRawData:
        clientNewInfo = copy(clientNewRawData)
        clientNewInfo['ip'] = client
        if clientNewInfo:
            data = {'ip': client, 'info': clientNewInfo,
                    'last_ping': general.now()}
            slave = mongo.db.slaves.update({'ip': client}, data,
                                           upsert=True)  # update if find or insert new
    return ujson.dumps({'message': 'PONG', 'clientInfo': clientNewInfo,
                        'last_ping': general.now()})


@app.route('/api/clientInfo', methods=['GET'])
def clientInfo():
    client = server_tools.getClientIp(request)
    slave = mongo.db.slaves.find_one({'ip': client})
    return dumps(slave)


@app.route('/api/addJob', methods=['POST'])
def addJob():
    """Gets user uploded job description and add it to jobs"""
    category = request.values.get('category')
    if request.method == 'POST' and 'upload' in request.files:

        f = request.files['upload']
        data = {'job': f.read(), 'category': 'Alfred',
                'filename': f.filename, 'category': category}
    job = alfred.parse(data.get('job'))
    #client = request.remote_addr
    client = server_tools.getClientIp(request)
    # hash of actual uploaded file
    jobHash = hashlib.md5(data.get('job')).hexdigest()
    if job:
        newJob = {
            'name': data.get('filename'),
            'category': data.get('category'),
            'data': job,
            'md5': jobHash,
            'bucket_size': 1,
            'tags': [],
            'queue': [],
            'status': 'future',
            'datetime': general.now(),
            'owner': client,
            'priority': 500,
            'is_active': True,
            'self': False,
            'progress': 0,
        }
        #new = mongo.db.jobs.update({'md5':jobHash}, newJob, upsert=True)
        new = mongo.db.jobs.insert(newJob)
        server_tools.createNewTasks(new)
        return dumps(newJob)


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
    #client = request.remote_addr
    client = server_tools.getClientIp(request)
    jobs = server_tools.getClientJobsInformation(client)
    return ujson.dumps(jobs)


@app.route('/api/fetchQueuedTasks')
def fetchQueuedTasks():
    """Give Queued tasks for a client to render"""

    client = server_tools.getClientIp(request)
    #client = request.remote_addr
    data = server_tools.getQueuedTasksForClient(client)
    return ujson.dumps(data)


@app.route('/api/updateTask', methods=['POST'])
def updateTask():
    client = server_tools.getClientIp(request)
    data = general.unpack(request.data)

    tid = ObjectId(data.get('_id'))
    data = data.get('data')
    task = mongo.db.tasks.find_one({'_id': tid})
    if not task:
        abort(404)

    task['last_activity'] = general.now()
    for i in data:
        if data[i]:
            task[i] = data[i]

    task['slave'] = client
    mongo.db.tasks.update({'_id': tid}, task)
    if task.get('status') == 'on progress':
        job = mongo.db.jobs.find_one({'_id': task.get('job')})
        job['status'] = 'on progress'
        mongo.db.jobs.update({'_id': job.get('_id')}, job)
    if task['progress'] == 100:
	ca.AsyncResult(task.get('ctid')).revoke()
    return general.pack('OK')


@app.route('/api/tasklog', methods=['POST'])
def tasklog():
    '''client sends this data'''
    data = general.unpack(request.data)
    tid = ObjectId(data.get('_id'))
    log = data.get('log')
    log['datetime'] = general.now()
    task = mongo.db.tasks.find_one({'_id': tid})
    if not task:
        abort(404)
    task['logs'].append(log)
    mongo.db.tasks.update({'_id': tid}, task)
    return general.pack('OK')


@app.route('/api/cancelJob', methods=['POST'])
def cancelJob():
    data = ujson.loads(request.data)
    jobId = data.get('id')  # get job is in string format
    _id = ObjectId(jobId)
    result = server_tools.cancelJob(_id)
    return ujson.dumps(result)


@app.route('/api/pauseJob', methods=['POST'])
def pauseJob():
    data = ujson.loads(request.data)
    jobId = data.get('id')  # get job is in string format
    _id = ObjectId(jobId)
    result = server_tools.pauseJob(_id)
    return ujson.dumps(result)


@app.route('/api/archiveJob', methods=['POST'])
def archiveJob():
    data = ujson.loads(request.data)
    jobId = data.get('id')  # get job is in string format
    _id = ObjectId(jobId)
    result = server_tools.archiveJob(_id)
    return ujson.dumps(result)


@app.route('/api/resumeJob', methods=['POST'])
def resumeJob():
    #client = request.remote_addr
    client = server_tools.getClientIp(request)
    data = ujson.loads(request.data)
    jobId = data.get('id')  # get job is in string format
    _id = ObjectId(jobId)
    result = server_tools.resumeJob(_id, client)
    return ujson.dumps(result)


@app.route('/api/tryAgainJob', methods=['POST'])
def tryAgainJob():
    data = ujson.loads(request.data)
    jobId = data.get('id')  # get job is in string format
    _id = ObjectId(jobId)
    result = server_tools.tryAgainJob(_id)
    return ujson.dumps(result)


@app.route('/api/slaves', methods=['GET'])
def slaves():
    '''Get slaves info for farm stats of client'''
    return ujson.dumps(server_tools.getSlaveInfo())


@app.route('/api/taskStatus', methods=['POST'])
def taskStatus():
    '''Get task status'''
    data = general.unpack(request.data)
    task_id = data.get('_id')  # get job is in string format
    _id = ObjectId(task_id)
    result = server_tools.getTaskStatus(_id)
    return general.pack(result)

@app.route('/api/jobDetail', methods=['POST'])
def jobDetail():
    '''Get task status'''
    data = ujson.loads(request.data)
    job_id = data.get('_id')  # get job is in string format
    _id = ObjectId(job_id)
    return ujson.dumps(server_tools.getJobDetail(_id))


@app.route('/api/workerPing', methods=['get'])
def workerPing():
    client = server_tools.getClientIp(request)
    return ujson.dumps(server_tools.getWorkerPing(client))


@app.route('/api/workerStats', methods=['get'])
def workerStats():
    client = server_tools.getClientIp(request)
    return ujson.dumps(server_tools.getWorkerStats(client))


@app.route('/api/killProcess', methods=['post'])
def killProcess():
    data = ujson.loads(request.data)
    _id = ObjectId(data.get('_id'))
    return ujson.dumps(server_tools.killTaskprocess(_id))


@app.route('/api/workerStats', methods=['get'])
def showImage():
    client = server_tools.getClientIp(request)
    data = ujson.loads(request.data)
    path = data.get(path)
    return ujson.dumps(server_tools.shoImage(client, path))


if __name__ == "__main__":

    def run_debug():
        app.run(
            host='0.0.0.0',
            port=9000,
            debug=True,
        )

    def run_tornado():
        from tornado.wsgi import WSGIContainer
        from tornado.httpserver import HTTPServer
        from tornado.ioloop import IOLoop

        http_server = HTTPServer(WSGIContainer(app))
        http_server.listen(9000)
        IOLoop.instance().start()

    def run_gevent():
        from gevent.wsgi import WSGIServer

        http_server = WSGIServer(('0.0.0.0', 9000), app)
        http_server.serve_forever()

    def run_bjoern():
	import bjoern
	bjoern.run(app, '0.0.0.0', 9000)

    #run_tornado()
    run_debug()
    #run_bjoern()
    # run_gevent()
