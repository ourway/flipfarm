
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
@desc: utils/server_tools.py
@author: F.Ashouri
"""

'''
$eq	Matches values that are equal to a specified value.
$gt	Matches values that are greater than a specified value.
$gte	Matches values that are greater than or equal to a specified value.
$lt	Matches values that are less than a specified value.
$lte	Matches values that are less than or equal to a specified value.
$ne	Matches all values that are not equal to a specified value.
$in	Matches any of the values specified in an array.
$nin	Matches none of the values specified in an array.

More info on:
    http://docs.mongodb.org/manual/reference/operator/query/
'''


from utils.general import now, chunks, readConfig
from bson.json_util import dumps
from models.db import mongo
from copy import copy
import ujson
import time
from random import choice
from itertools import cycle
from clientAgent import execute, ca
from pingAgent import pa

CONFIG = readConfig()


def getClientIp(request):
    '''get correct client ip'''
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    return ip

def getRenderCommand(category):
    if category == 'Alfred':
        command = 'prman -statsfile {cwd}/.flipfarmPrmanStats-{task}.xml -cwd {cwd} -t:{threads} -Progress {filepath}'
        return command


def addTaskToQueue(taskId):
    data = mongo.db.tasks.find_one({'_id':taskId})
    '''Revoke the task if it's available'''
    if data.get('ctid'):
        ca.AsyncResult(data.get('ctid')).revoke()

    proccess = data.get('proccess')
    raw_cmd = proccess.get('command')
    command = raw_cmd.format(threads=1,
                             cwd=proccess.get('cwd'), task=data.get('name').replace(' ', '_'),
                             filepath=proccess.get('filepath'))
    tname = '%s-%s'%(data.get('_id'), data.get('name'))
    tname=tname.replace(' ', '_')
    ctid = execute.apply_async(args=[command, tname, proccess.get('cwd'), proccess.get('target')],
                               routing_key='FFarmRenderQueue01',
                               exchange='FFarmRenderQueue01',
                               queue='FFarmRenderQueue01')
    data['ctid'] = str(ctid)
    mongo.db.tasks.update({'_id':taskId}, data)
    return ctid

def createNewTasks(_id):
    """Create new tasks on database based on this new job"""
    job = mongo.db.jobs.find_one({'_id': _id})
    tasks = job.get('data').get('tasks')
    for task in tasks:
        data = {
            'name': task.get('name'),
            'datetime': now(),
            'status': 'ready',
            'owner': job.get('owner'),
            'priority': job.get('priority'),
            'is_active': True,
            'slave': None,
            'last_activity': now(),
            'started_on': None,
            'finished_on': None,
            'paused_on': None,
            'logs': [],
            'ctid':None,
            'target_info':{},
            'cancelled_on': None,
            'progress': 0,
            'job': job.get('_id'),
            'proccess':
                {
                    'command': getRenderCommand(job.get('category')),
                    'cwd': task.get('cwd'),
                    'filepath': task.get('filepath'),
                    'target': task.get('target'),
            }
        }
        newTask = mongo.db.tasks.insert(data)
        ctid = addTaskToQueue(newTask)
        #updateTaskInfo(str(task['_id']['$oid']), status='ready', ctid=str(ctid))
    job['status'] = 'ready'
    mongo.db.jobs.update({'_id': _id}, job)

    return


def getJobStatus(job):
    """Calculate Job Status"""
    tasks = mongo.db.tasks.find({'job': job.get('_id'), 'status':{'$ne':'completed'}}).count()
    if not tasks:
        return 'Completed'
    else:
        return job.get('status').title()

def getClientJobsInformation(client):
    """Lists active client jobs."""
    #getSlaveForDispatch()
    #jobs = mongo.db.jobs.find({'owner': client, 'is_active': True})
    jobs = mongo.db.jobs.find({'is_active': True})



        #        result = i.title()
        # if any([s.get('status')=='on progress' for s in tasks]):
        #    result = 'On Progress'
        # return result

    result = [{
        'name': j.get('name'),
        'datetime': j.get('datetime'),
        'status': getJobStatus(j),
        'priority': j.get('priority'),
        'progress': sum([t.get('progress') for t in mongo.db.tasks.find({'job': j.get('_id')})]) /
        (mongo.db.tasks.find({'job': j.get('_id')}).count() or -1),
        'id': str(j.get('_id')),
        'tasks_count': mongo.db.tasks.find({'job': j.get('_id'), 'is_active': True}).count(),
        'failed_count': mongo.db.tasks.find({'job': j.get('_id'), 'is_active': True, 'status': 'failed'}).count(),
        'completed_count': mongo.db.tasks.find({'job': j.get('_id'), 'is_active': True, 'status': 'completed'}).count(),
        'active_task':'Frame 43',
    } for j in jobs]
    return result or {}




def getQueuedTasksForClient(client):
    """Lets send client tasks for render"""
    c = mongo.db.tasks.find().count()
    queueTasks = mongo.db.tasks.find(
        {'status': 'likely', 'is_active': True, 'slave': client})
    if queueTasks.count():
        slave = mongo.db.slaves.find_one({'ip': client})
        return dumps({'tasks': queueTasks, 'slave': slave})


def getServerCreditentionals():
    auth = CONFIG.get('auth')
    if not auth:
        return 'USER', 'PASS'
    else:
        return auth.get('username'), auth.get('password')


def cancelJob(_id):
    """cancelled a job
        Cancelling a job usually means cancelling whole tasks.
        Also probabaly we have to send kill dognal to active
        task processes
    """
    job = mongo.db.jobs.find_one({'_id':_id})
    tasks = mongo.db.tasks.find({'job':_id})
    for each in tasks:
        _t = ca.AsyncResult(each.get('ctid'))
        _t.revoke()
    job['status'] = 'cancelled'
    """Set status of job to cancelled"""
    mongo.db.jobs.update({'_id':_id}, job)
    """Bulk update tasks"""
    bulk = mongo.db.tasks.initialize_unordered_bulk_op()
    bulk.find({'job':_id, 'status':{'$ne':'completed'} }).update({
                                '$set': {
                                    'status': "cancelled",
                                    'cancelled_on':now(),
                                    'slave':None,
                                }})
    bulk.execute()

    return {'info':'success'}


def tryAgainJob(_id):
    """Try Again a cancelled job.
        It means schanging all tasks status to future and reset slave info to None.
    """
    job = mongo.db.jobs.find_one({'_id':_id, 'status':{'$ne':'completed'}})

    """Bulk update tasks"""
    bulk = mongo.db.tasks.initialize_unordered_bulk_op()
    looking_for = {'job':_id, 'status':{'$ne':'completed'} }
    tasks = mongo.db.tasks.find(looking_for)
    for each in tasks:
        addTaskToQueue(each.get('_id'))

    bulk.find(looking_for).update({
                                '$set': {
                                    'status': "ready",
                                    'restarted_on':now(),
                                    'slave':None,
                                }})
    bulk.execute()
    job['status'] = 'ready'
    """Set status of job to future"""
    mongo.db.jobs.update({'_id':_id}, job)
    return {'info':'success'}


def pauseJob(_id):
    """Pause the job.
    Pausing a job means changing all ready tasks tasks status to pause.
    """
    job = mongo.db.jobs.find_one({'_id':_id})
    tasks = mongo.db.tasks.find({'job':_id})
    for each in tasks:
        _t = ca.AsyncResult(each.get('ctid'))
        _t.revoke()
    job['status'] = 'paused'
    """Set status of job to paused"""
    mongo.db.jobs.update({'_id':_id}, job)
    """Bulk update tasks"""
    bulk = mongo.db.tasks.initialize_unordered_bulk_op()
    bulk.find({'job':_id, 'status':{'$ne':'completed'}}).update({
                                '$set': {
                                    'status': "paused",
                                    'paused_on':now(),
                                }})
    bulk.execute()

    return {'info':'success'}


def resumeJob(_id, client):
    """resume the job.
    resuming a job means changing all tasks status to future.
    """
    return tryAgainJob(_id)


def archiveJob(_id):
    """archive the job.
    archiving a job means changing all tasks is_active to False.
    """
    job = mongo.db.jobs.find_one({'_id':_id})
    """Set status of job to future"""
    job['status'] = 'archived'
    job['is_active'] = False
    """find slave"""
    mongo.db.jobs.update({'_id':_id}, job)
    """Bulk update tasks"""
    bulk = mongo.db.tasks.initialize_unordered_bulk_op()
    bulk.find({'job':_id}).update({
                                '$set': {
                                    'archived':now(),
                                    'is_active':False
                                }})
    bulk.execute()

    return {'info':'success'}

def getTaskStatus(_id):
    '''Get task status'''
    task = mongo.db.tasks.find_one({'_id':_id})
    if task:
        return task.get('status', 'N/A')

def getSlaveInfo(client=None):
    """Get slaves information"""
    inspect = pa.control.inspect()
    result = []
    pings = inspect.ping()
    if pings:
        for each in pings:
            _mac = each.split('@')[-1]
            print _mac
            slave = mongo.db.slaves.find_one({'info.MAC':_mac})
            result.append(slave)

    return ujson.loads(dumps(result))

def getJobDetail(_id):
    '''Get job detail for show in a modal'''
    job = mongo.db.jobs.find_one({'_id':_id})
    output = {}
    output['jobInfo'] = ujson.loads(dumps(job))
    tasks = list(mongo.db.tasks.find({'job':_id}))
    output['tasksInfo'] = ujson.loads(dumps(tasks))
    return output

def cancelAllFromMyCeleryQueue(client):
    """thsi will discard all tasks from client celery queue"""
    slave = mongo.db.slaves.find_one({'ip':client})
    if slave:
        _mac = slave['info'].get('MAC')
        return ca.control.discard_all(destination=['celery@%s'%_mac])
    #  return ca.control.cancel_consumer('celery')

def getWorkerPing(client):
    slave = mongo.db.slaves.find_one({'ip':client})
    if slave:
        _mac = slave['info'].get('MAC')
        inspect = pa.control.inspect(destination=['celery@%s'%_mac])
        return inspect.ping()


def getWorkerStats(client):
    slave = mongo.db.slaves.find_one({'ip':client})
    if slave:
        _mac = slave['info'].get('MAC')
        inspect = pa.control.inspect(destination=['celery@%s'%_mac])
        return inspect.stats()


def killTaskprocess(_id):
    task = mongo.db.tasks.find_one({'_id':_id})
    ctid = task.get('ctid')
    pid = task.get('pid')
    res = ca.AsyncResult(ctid)
    res.revoke(terminate=True)
    task['status'] = 'failed'

    mongo.db.tasks.update({'_id':_id}, task)
    return {'message':'OK'}
