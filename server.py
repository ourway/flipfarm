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


from flask import Flask, request, abort
from flask.ext.mako import render_template
from flask.ext.mako import MakoTemplates
from flask.ext.pymongo import PyMongo
from bson.json_util import dumps
import ujson
from utils import general, server_tools

__version__ = general.getVersion()


'''Register extensions'''
app = Flask(__name__)
mongo = PyMongo(app)
mako = MakoTemplates(app)


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
        clientNewInfo = general.unpack(clientNewRawData)
        if clientNewInfo:
            data = {'ip':client, 'info':clientNewInfo}
            slave = mongo.db.slave.update({'ip':client}, data, upsert=True)  ## update if find or insert new
    return general.pack({'message':'PONG', 'clientInfo':clientNewInfo})


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


if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        port=9001,
        debug=True,
    )
