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
@desc: client.py
@author: F.Ashouri
"""

from gevent import monkey
monkey.patch_all()

import sys
from flask import Flask, request, flash, abort, redirect
from flask.ext.mako import render_template
from flask.ext.mako import MakoTemplates

import ujson
from utils import general, client_tools
from copy import copy

__version__ = general.getVersion()


'''Register extensions'''
app = Flask(__name__)
app.config['SECRET_KEY'] = 'please dont kill my cat bro!'
mako = MakoTemplates(app)







@app.route("/")
def index():
    body = render_template('client.tpl')
    title = 'Client Dashboard'
    data = render_template('index.tpl', body=body, title=title,
                           version=__version__)
    return data


@app.route("/api/benchmark")
def benchmark():
    return ujson.dumps({'qmark':general.getBenchmark()})



@app.route("/api/pingServer", methods=['POST'])
def ping():
    ''' This method pings server'''
    systemInfo = general.getSystemInfo()
    '''Now lets read browser database info which is send to us'''
    localStorageInfo = request.data
    payload = copy(systemInfo)
    payload['render_tools'] = client_tools.getRenderTools()
    payload['os'] = sys.platform
    if localStorageInfo:
        _rawData = ujson.loads(localStorageInfo)
        for lsd in _rawData:
            payload[lsd] = _rawData.get(lsd)
    data = client_tools.connectToServer('/api/ping', payload)
    return ujson.dumps(data)


@app.route('/api/upload', methods=['GET', 'POST'])
def upload():
    category = request.values.get('category')
    if request.method == 'POST' and 'upload' in request.files:

        f = request.files['upload']
        payload = {'job':f.read(), 'category':'Alfred',
                   'filename':f.filename, 'category':category}
        result = client_tools.connectToServer('/api/addJob', payload)
        return ujson.dumps(result)
        #return redirect(url_for('show', id=rec.id))
    #return render_template('upload.html')


@app.route('/api/getJobsInfo')
def getJobsInfo():
    """Gets all jobs information for user"""
    result = client_tools.connectToServer('/api/getJobsInfo')
    #print type(result)
    return ujson.dumps(result)


@app.route('/server')
def server():
    return redirect(client_tools.getServerUrl(), code=302)


@app.route('/api/cancelJob', methods=['POST'])
def cancelJob():
    payload = ujson.loads(request.data)
    result = client_tools.connectToServer('/api/cancelJob', payload)
    return ujson.dumps(result)

@app.route('/api/archiveJob', methods=['POST'])
def archiveJob():
    payload = ujson.loads(request.data)
    result = client_tools.connectToServer('/api/archiveJob', payload)
    return ujson.dumps(result)


@app.route('/api/tryAgainJob', methods=['POST'])
def tryAgainJob():
    payload = ujson.loads(request.data)
    result = client_tools.connectToServer('/api/tryAgainJob', payload)
    return ujson.dumps(result)

@app.route('/api/pauseJob', methods=['POST'])
def pauseJob():
    payload = ujson.loads(request.data)
    result = client_tools.connectToServer('/api/pauseJob', payload)
    return ujson.dumps(result)

@app.route('/api/resumeJob', methods=['POST'])
def resumeJob():
    payload = ujson.loads(request.data)
    result = client_tools.connectToServer('/api/resumeJob', payload)
    return ujson.dumps(result)


@app.route('/api/discardNow', methods=['POST'])
def discardNow():
    cn = client_tools.cancelAllFromMyCeleryQueue()
    return ujson.dumps({'message':'All queued discarded. Also %s active tasks terminated'%(cn or 'no')})


@app.route('/api/workerPing', methods=['GET'])
def workerPing():
    result = {'down':'ok'}
    p = client_tools.getWorkerPing()
    return ujson.dumps(p or result)

@app.route('/api/workerStats', methods=['GET'])
def workerStats():
    result = {'down':'ok'}
    p = client_tools.getWorkerStats()
    return ujson.dumps(p or result)

@app.route('/api/slaves', methods=['GET'])
def slaves():
    result = client_tools.connectToServer('/api/slaves')
    return result



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

        http_server = WSGIServer(('127.0.0.1', 9000), app)
        http_server.serve_forever()

    #run_tornado()
    run_debug()
    #run_gevent()

