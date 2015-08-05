
import sys
from subprocess import Popen, PIPE
from utils.general import readConfig
from utils.client_tools import getServerUrl, connectToServer
import psutil
import datetime
import time
import requests
import ujson
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





def update_task_status(task_id, status, ctid, progress=0):
    payload = {'status':status, '_id':task_id, 'ctid':ctid, 'progress':progress or None}
    return connectToServer('/api/updateTask', payload)



def parse_prman_output(line):
    pat = re.compile(r'R[\d]*.* ([\d]+)%')
    percent = re.findall(pat, line)
    if percent:
        return percent[-1]




@ca.task(name='clientAgent.execute')
def execute(cmd, task, directory='.'):
    #ctid = Celery.AsyncResult.task_id
    ctid = -2
    stime = time.time()
    p = psutil.Popen(cmd.split(), stdout=PIPE, stderr=PIPE, bufsize=16, cwd=directory)
    #update_task_status(task.split('-')[0], 'on progress')
    print 'Executing %s with PID: %s' % (task, p.pid)
    tuuid = task.split('-')[0]
    has_output = False
    progress = None
    for line in iter(p.stderr.readline, b''):
        has_output = True
        try:
            progress = int(parse_prman_output(line))
        except (TypeError, ValueError):
            pass
        print '{t} {prog}% completed.'.format(t=task, prog=progress),len(line),
        if progress and not progress%5:  ## update every 5 percent
            update_task_status(tuuid, 'on progress', ctid, progress)
        if progress==100:  ## completed
            update_task_status(tuuid, 'completed', ctid, 100)

    if not has_output:
        print 'NO OUTPUT'
        update_task_status(tuuid, 'completed', ctid, 100)


    p.stdout.close()
    p.wait()

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
        'ctid':ctid
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
    for task in tasks:
        update_task_status(str(task['_id']['$oid']), 'waiting', -1)
        proccess = task.get('proccess')
        if not proccess:
            continue
        raw_cmd = proccess.get('command')
        command = raw_cmd.format(threads=data.get('slave').get('info').get('cpu_count'),
                                 cwd=proccess.get('cwd'),
                                 filepath=proccess.get('filepath'))
        tname = '%s-%s'%(task.get('_id').get('$oid'), task.get('name'))
        tname=tname.replace(' ', '_')
        execute.delay(command, tname, proccess.get('cwd'))







if __name__ == '__main__':
    pass
    #directory ='/Users/farsheed/Downloads/ToyStory3'
    #filename = 'sequences/seq_00/shot_00_00/renderman/Shot_00_00_0730011249/rib/0007/0007.rib'
    #md = 'prman -Progress {f}'.format(f=filename)
    #execute.delay(cmd, 'testdev2', directory)
    #getTasks.delay()

