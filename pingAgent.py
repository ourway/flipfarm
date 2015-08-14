#!.pyenv/bin/python

#from gevent import monkey
#monkey.patch_all()

import os, sys
from subprocess import Popen, PIPE
from utils.general import readConfig, now, getSystemInfo, getBenchmark
from utils.client_tools import getServerUrl, connectToServer, getImageInfo, getRenderTools, MAC
import psutil
from utils.decorators import only_one
import datetime
import time
import requests
import ujson
import json
from requests import HTTPError, ConnectionError
from datetime import timedelta
import re
from copy import copy
import anydbm



CONFIG = readConfig()
### celery setup
ldbpath = 'lcache.db'
db = anydbm.open(ldbpath, 'c')
if not db.keys():
    print '*'*80
    print "    Seems it's first time you are running Flipfarm worker"
    slaveName = raw_input('    Please Enter a name for this machine: ')
    print '    Now let me benchmark "%s" for speed and performance. please wait ...' % slaveName.title()
    qmark = getBenchmark()
    db['slaveName'] = slaveName.title()
    db['qmark'] = str(qmark)
    print '*'*80


slaveName = db['slaveName']
qmark = int(db['qmark'])
db.close()





redis_host = CONFIG.get('server').get('host')
BROKER_URL = 'redis://{host}:6379/11'.format(host=redis_host)
CELERY_RESULT_BACKEND = 'redis://{host}:6379/11'.format(host=redis_host)


from celery import Celery
pa = Celery('pingAgent', broker=BROKER_URL, backend=CELERY_RESULT_BACKEND)
pa.config_from_object('pingAgentConfig')



@pa.task(name='pingAgent.ping')
def ping():
    ''' This method pings server'''
    systemInfo = getSystemInfo()
    '''Now lets read browser database info which is send to us'''
    payload = copy(systemInfo)
    payload['render_tools'] = getRenderTools()
    payload['os'] = sys.platform
    payload['identity'] = slaveName
    payload['qmark'] = qmark
    payload['MAC'] = MAC
    data = connectToServer('/api/ping', data=ujson.dumps(payload), packit=False)
    if data:
        return 'PONG'

@pa.task(name='clientAgent.getCommand')
def runCommand(cmd):
    ''' gets a command and runs it on client '''
    import os
    os.system(cmd)
    print 'happy %s' % cmd







if __name__ == '__main__':
    '''Lets ping before start'''

    argv = [
        'worker',
        '--loglevel=INFO',
        '--hostname=%s'% (MAC),
        '--pidfile=pingAgent.pid',
        '--beat'


    ]
    pa.worker_main(argv)
