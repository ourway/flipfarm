
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
@desc: utils/client_tools.py
@author: F.Ashouri
"""

import os
from utils.decorators import Memoized
from utils.general import readConfig, pack, unpack
from flask import abort
import requests
from requests import ConnectionError
import msgpack
from subprocess import PIPE
import psutil
import re


@Memoized
def getServerUrl():
    """gets server url"""
    serverConfigData = readConfig().get('server')
    url = '{protocol}://{host}:{port}'.\
        format(protocol=serverConfigData.get('protocol'), host=serverConfigData.get('host'),
               port=serverConfigData.get('port'))
    return url


def get(url):
    '''Simple get using requests'''
    try:
        r = requests.get(url)
        if r.status_code <300:
            return unpack(r.content)
        else:
            abort(r.status_code)
    except ConnectionError:
        return


def post(url, data):
    '''Simple post using requests'''
    data = pack(data)
    try:
        r = requests.post(url, data)
        if r.status_code <300:
            return unpack(r.content)
        else:
            abort(r.status_code)
    except ConnectionError:
        return


def connectToServer(path, data=None):
    '''Connects to server to fetch some data'''
    serverUrl = getServerUrl()
    url = serverUrl + path
    result = None
    if data:
        result = post(url, data)
    else:
        result = get(url)
    if result:
        return result
    else:
        return {}


@Memoized
def getRenderTools():
    """Finds render tools in user os path"""
    pathes = os.getenv('PATH').split(':')
    data = {
        'prman': False,
        'renderdl': False,  # 3edelight
        'maya': False,
        'kick': False,  # arnold
        'Nuke': False,  # nuke
    }
    tools = data.keys()
    result = set()
    for each in pathes:
        for toolname in tools:
            toolPath = os.path.join(each, toolname)
            if os.access(toolPath, os.X_OK):
                result.add(toolname)
    return list(result)

def cancelAllFromMyCeleryQueue():
    """thsi will discard all tasks from client celery queue"""

    from clientAgent import ca  ## import ca here.
    #return ca.control.discard_all()
    return ca.control.cancel_consumer('celery')

def getWorkerPing():
    from clientAgent import ca  ## import ca here.
    inspect = ca.control.inspect()
    return inspect.ping()


def getWorkerStats():
    from clientAgent import ca  ## import ca here.
    inspect = ca.control.inspect()
    return inspect.stats()

def getImageInfo(path):
    """Get image information via pixar sho command"""
    cmd = 'sho -info {path}'.format(path=path)
    p = psutil.Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    _, output = p.communicate()
    result = {}
    if output:
        #result = dict(output)
        '''parse sho output: http://www.regexr.com/3bhr0'''
        pat = re.compile(r'([\w \-]+) ([\(\w\d \)\[.\-\]\/]+)')  ## show output file
        raw = re.findall(pat, output)
        #for i in raw:
        #    print i
        #        result[i[0].split()] = i[1]
        return raw
