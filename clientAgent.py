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
BROKER_URL = 'redis://{host}:6379/10'.format(host=redis_host)
CELERY_RESULT_BACKEND = 'redis://{host}:6379/10'.format(host=redis_host)
BROKER_TRANSPORT_OPTIONS = {'fanout_prefix': True}

from celery import Celery
ca = Celery('clientAgent', broker=BROKER_URL, backend=CELERY_RESULT_BACKEND)
ca.config_from_object('clientAgentConfig')




def updateTaskInfo(task_id, **kw):
    payload = {'_id':task_id, 'data':kw}
    return connectToServer('/api/updateTask', data=payload)

def tasklog(task_id, log):
    payload = {'_id':task_id, 'log':log}
    return connectToServer('/api/tasklog', data=payload)


def parse_prman_output(line):

    '''first lets catch errors'''
    pat = re.compile(r'(R[\d]+).*\{([\w]+)\}(.*) \((.*)\)')
    text = re.findall(pat, line)
    if len(text):
        return text[-1]  ## cause its a single topple
    '''then try to find percentage'''
    pat = re.compile(r'R[\d]*.* ([\d]+)%')
    percent = re.findall(pat, line)
    if percent:
        return percent[-1]


def getTaskStatus(task_id):
    '''Get latest task status from server'''
    payload = {'_id':task_id}
    return connectToServer('/api/taskStatus', data=payload)


@ca.task(name='clientAgent.execute')
#@only_one(key='happy1')
def execute(cmd, task, directory='.', target=None):
    """
        Execute render and parse output and update task info
        Target is final render output.

    """

    #ctid = Celery.AsyncResult.task_id
    stime = time.time()
    tuuid = task.split('-')[0]
    '''chack task status and make sure its good to continue'''


    updateTaskInfo(tuuid, progress=0, started_on=now(), slave_name=slaveName)

    '''Error handeling'''
    if not os.path.isdir(directory):
        updateTaskInfo(tuuid, status='failed', failed_on=now())
        log = {
            'code':'FF001',
            'type':'ERROR',
            'description': 'FlipFarm: Directory "%s" not found'%directory,
            'brief': 'Directory not found'
        }
        tasklog(tuuid, log)
        print json.dumps(log, indent=4, sort_keys=True)
        return

    p = psutil.Popen(cmd.split(), stdout=PIPE, stderr=PIPE, bufsize=16, cwd=directory)
    updateTaskInfo(tuuid, status='on progress', pid=p.pid)
    processInfo = {
        'Task':task,
        'Command':cmd,
        'Directory':directory,
        'PID':p.pid,
        'Target':target
    }
    print '*'*80
    print json.dumps(processInfo, indent=4, sort_keys=True)
    print '*'*80
    print '\n'
    has_output = False
    progress = None
    for line in iter(p.stderr.readline, b''):
        has_output = True
        result = parse_prman_output(line)
        if result:
            try:
                '''Progressing ...'''
                progress = int(result)
                print '>>> {t} {prog}% completed.'.format(t=task, prog=progress),

            except (TypeError, ValueError):
                '''we probabaly have some error codes'''
                code, typ, desc, brief = result
                log = {
                        'code':code,
                        'type':typ,
                        'description':desc,
                        'brief':brief
                    }
                print json.dumps(log, indent=4, sort_keys=True)
                tasklog(tuuid, log)
                if typ in ['ERROR', 'SEVERE'] and code not in []: #TODO
                    updateTaskInfo(tuuid, status='failed', failed_on=now())
                    p.kill()
                    return

            if progress:  ## update every 5 percent
                updateTaskInfo(tuuid, status='on progress', progress=progress)
            if progress==100:  ## completed
                updateTaskInfo(tuuid, status='completed', progress=100, finished_on=now())
        else:
            pass  ## for now

    if not has_output:
        print 'NO OUTPUT'
        updateTaskInfo(tuuid, status='completed', progress=100)


    p.stdout.close()
    p.stderr.close()
    p.wait()
    if target and 'exr' in target:  ## for prman ##TODO
        iminfo = getImageInfo(target)
        updateTaskInfo(tuuid, target_info=iminfo)



    #f.write('########## %s | FlipFarm Log ##########\n' % datetime.datetime.now())
    #p.wait() # wait for the subprocess to exit
    etime = time.time()
    #f.write('\n\n{"time":%s}\n'%(etime-stime))
    #update_task_status(task.split('-')[0], 'completed')
    return {
        'pid':p.pid,
        'time':etime-stime,
        'start':stime,
        'end':etime,
        'command':cmd,
        'task':task,
        'slave':slaveName
    }



@ca.task(name='clientAgent.ping')
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

@ca.task(name='clientAgent.getCommand')
def runCommand(cmd):
    ''' gets a command and runs it on client '''
    import os
    os.system(cmd)
    print 'happy %s' % cmd





@ca.task(name='clientAgent.simpleTest')
def simpleTest():
    print 'I am happening'
    return True




if __name__ == '__main__':
    '''Lets ping before start'''

    argv = [
        'worker',
        '--loglevel=INFO',
        '--hostname=%s'% (MAC),
        '--concurrency=1',
        '--pidfile=clientAgent.pid',


    ]
    ca.worker_main(argv)
