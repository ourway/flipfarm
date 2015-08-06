
import sys
from subprocess import Popen, PIPE
from utils.general import readConfig, now
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





def updateTaskInfo(task_id, **kw):
    payload = {'_id':task_id, 'data':kw}
    return connectToServer('/api/updateTask', payload)



def parse_prman_output(line):
    pat = re.compile(r'R[\d]*.* ([\d]+)%')
    percent = re.findall(pat, line)
    if percent:
        return percent[-1]




@ca.task(name='clientAgent.execute')
def execute(cmd, task, directory='.', target=None):
    """
        Execute render and parse output and update task info
        Target is final render output.

    """

    #ctid = Celery.AsyncResult.task_id
    stime = time.time()
    tuuid = task.split('-')[0]
    updateTaskInfo(tuuid, progress=0, started_on=now())
    try:
        p = psutil.Popen(cmd.split(), stdout=PIPE, stderr=PIPE, bufsize=16, cwd=directory)
    except OSError, e:
        updateTaskInfo(tuuid, status='failed', progress=0, failed_on=now())
        return


    updateTaskInfo(tuuid, status='on progress', pid=p.pid)
    print '*'*80
    print '\tTask: %s'%task
    print '\tCommand: %s'%cmd
    print '\tDirectory: %s'%directory
    print '\tPID: %s'%p.pid
    print '\tTarget: %s'%target
    print '*'*80
    print '\n'
    has_output = False
    progress = None
    for line in iter(p.stderr.readline, b''):
        has_output = True
        try:
            progress = int(parse_prman_output(line))
        except (TypeError, ValueError):
            pass
        print '>>> {t} {prog}% completed.'.format(t=task, prog=progress),
        if progress and not progress%5:  ## update every 5 percent
            updateTaskInfo(tuuid, status='on progress', progress=progress)
        if progress==100:  ## completed
            updateTaskInfo(tuuid, status='completed', progress=100, finished=now())

    if not has_output:
        print 'NO OUTPUT'
        updateTaskInfo(tuuid, status='completed', progress=100)


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

