
import sys
from subprocess import Popen, PIPE
from utils.general import readConfig
from utils.client_tools import getServerUrl
from utils.server_tools import getSlaveForDispatch
import psutil
import datetime
import time
import requests
import ujson
from requests import HTTPError, ConnectionError
from datetime import timedelta
import msgpack
import re

CONFIG = readConfig()

### celery setup




redis_host = CONFIG.get('server').get('host')
BROKER_URL = 'redis://{host}:6379/10'.format(host=redis_host)
CELERY_RESULT_BACKEND = 'redis://{host}:6379/10'.format(host=redis_host)



from celery import Celery
ca = Celery('clientAgent', broker=BROKER_URL, backend=CELERY_RESULT_BACKEND)
ca.config_from_object('clientAgentConfig')





def update_task_status(task_uuid, status, progress=0):
    tasksUpdateUrl = '{s}/api/updateTask'.format(s=getServerUrl())
    payload = {'status':status, 'uuid':task_uuid, 'progress':progress or None}
    try:
        r = requests.post(tasksUpdateUrl, msgpack.packb(payload))
    except ConnectionError:
        print 'Server is Down'
        return False

    return True


def parse_prman_output(line):
    pat = re.compile(r'R[\d]*.* ([\d]+)%')
    percent = re.findall(pat, line)
    if percent:
        return percent[-1]




@ca.task(name='clientAgent.execute')
def execute(cmd, task, directory='.'):
    print cmd
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
            update_task_status(tuuid, 'on progress', progress)
        if progress==100:  ## completed
            update_task_status(tuuid, 'completed', 100)

    if not has_output:
        #print 'NO OUTPUT'
        update_task_status(tuuid, 'completed', 100)


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
        'task':task
    }



@ca.task(name='clientAgent.getLatestTasks')
def getLatestTasks():
    '''get list of tasks from server'''
    fetchTasksUrl = '{s}/api/fetchLatestTasks'.format(s=getServerUrl())
    print fetchTasksUrl






if __name__ == '__main__':
    pass
    #directory ='/Users/farsheed/Downloads/ToyStory3'
    #filename = 'sequences/seq_00/shot_00_00/renderman/Shot_00_00_0730011249/rib/0007/0007.rib'
    #md = 'prman -Progress {f}'.format(f=filename)
    #execute.delay(cmd, 'testdev2', directory)
    #getTasks.delay()

