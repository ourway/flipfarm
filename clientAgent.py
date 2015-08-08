
import os, sys
from subprocess import Popen, PIPE
from utils.general import readConfig, now
from utils.client_tools import getServerUrl, connectToServer, getImageInfo
import psutil
import datetime
import time
import requests
import ujson
import json
from requests import HTTPError, ConnectionError
from datetime import timedelta
import re

CONFIG = readConfig()

### celery setup




redis_host = CONFIG.get('server').get('host')
BROKER_URL = 'redis://{host}:6379/10'.format(host=redis_host)
CELERY_RESULT_BACKEND = 'redis://{host}:6379/10'.format(host=redis_host)


from celery import Celery
ca = Celery('clientAgent', broker=BROKER_URL, backend=CELERY_RESULT_BACKEND)
ca.config_from_object('clientAgentConfig')





def updateTaskInfo(task_id, **kw):
    payload = {'_id':task_id, 'data':kw}
    return connectToServer('/api/updateTask', payload)

def tasklog(task_id, log):
    payload = {'_id':task_id, 'log':log}
    return connectToServer('/api/tasklog', payload)


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
    return connectToServer('/api/taskStatus', payload)


@ca.task(name='clientAgent.execute')
def execute(cmd, task, directory='.', target=None):
    """
        Execute render and parse output and update task info
        Target is final render output.

    """

    print cmd
    #ctid = Celery.AsyncResult.task_id
    stime = time.time()
    tuuid = task.split('-')[0]
    '''chack task status and make sure its good to continue'''
    lst = getTaskStatus(tuuid)
    if lst in ['completed', 'cancelled', 'paused']:
        log = {
            'code':2,
            'typ':'INFO',
            'description': 'Task is %s, but was in queue, so flipfarm cancelled running process.'%lst,
            'brief': 'Task process abort'
        }
        tasklog(tuuid, log)
        return

    updateTaskInfo(tuuid, progress=0, started_on=now())

    '''Error handeling'''
    if not os.path.isdir(directory):
        updateTaskInfo(tuuid, status='failed', failed_on=now())
        log = {
            'code':1,
            'typ':'ERROR',
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
                        'bref':brief
                    }
                print json.dumps(log, indent=4, sort_keys=True)
                tasklog(tuuid, log)
                if typ == 'ERROR' and code not in []: #TODO
                    updateTaskInfo(tuuid, status='failed', failed_on=now())
                    p.kill()
                    return

            if progress:  ## update every 5 percent
                updateTaskInfo(tuuid, status='on progress', progress=progress)
            if progress==100:  ## completed
                updateTaskInfo(tuuid, status='completed', progress=100, finished=now())
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
    }



@ca.task(name='clientAgent.getLatestTasks')
def getLatestTasks():
    '''get list of tasks from server'''
    data = connectToServer('/api/fetchQueuedTasks')
    if not data:
        return
    data = ujson.loads(data)
    tasks =  data.get('tasks')
    if not tasks:
        return
    else:
        print 'got %s tasks.' % len(tasks)
    for task in tasks:
        proccess = task.get('proccess')
        if not proccess:
            continue
        raw_cmd = proccess.get('command')
        command = raw_cmd.format(threads=data.get('slave').get('info').get('cores') or \
                                 data.get('slave').get('info').get('cpu_count'),
                                 cwd=proccess.get('cwd'),
                                 filepath=proccess.get('filepath'))
        tname = '%s-%s'%(task.get('_id').get('$oid'), task.get('name'))
        tname=tname.replace(' ', '_')
        ctid = execute.delay(command, tname, proccess.get('cwd'), proccess.get('target'))
        updateTaskInfo(str(task['_id']['$oid']), status='ready', ctid=str(ctid))



@ca.task(name='clientAgent.simpleTest')
def simpleTest():
    print 'I am happening'
    return True




if __name__ == '__main__':
    pass
    #directory ='/Users/farsheed/Downloads/ToyStory3'
    #filename = 'sequences/seq_00/shot_00_00/renderman/Shot_00_00_0730011249/rib/0007/0007.rib'
    #md = 'prman -Progress {f}'.format(f=filename)
    #execute.delay(cmd, 'testdev2', directory)
    #getTasks.delay()
