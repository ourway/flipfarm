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


from flask import Flask, request, abort
from flask.ext.mako import render_template
from flask.ext.mako import MakoTemplates
import ujson
from utils import general, client_tools
from copy import copy

__version__ = general.getVersion()


'''Register extensions'''
app = Flask(__name__)
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
    if localStorageInfo:
        _rawData = ujson.loads(localStorageInfo)
        for lsd in _rawData:
            payload[lsd] = _rawData.get(lsd)
    data = client_tools.connectToServer('/api/ping', payload)
    return ujson.dumps(data)

if __name__ == "__main__":
    app.run(
        host='localhost',
        port=9000,
        debug=True,
    )
