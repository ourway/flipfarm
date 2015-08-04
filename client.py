#!.pyenv/bin/python

from flask import Flask
from flask.ext.mako import render_template
from flask.ext.mako import MakoTemplates
import ujson



app = Flask(__name__)
mako = MakoTemplates(app)


@app.route("/")
def index():
    body = render_template('client.tpl')
    title = 'dash'
    data = render_template('index.tpl', body=body, title=title)
    return data


@app.route("/api/pingServer", methods=['POST'])
def ping():
    ''' This method pings server'''
    return ujson.dumps({})

if __name__ == "__main__":
    app.run(
        host='localhost',
        port=9000,
        debug=True,
    )
