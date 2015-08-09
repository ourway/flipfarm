
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

CONFIG = readConfig()


def getRenderCommand(category):
    if category == 'Alfred':
        command = 'prman -statsfile {cwd}/.flipfarmPrmanStats-{task}.xml -cwd {cwd} -t:{threads} -Progress {filepath}'
        return command


def createNewTasks(_id):
    """Create new tasks on database based on this new job"""
    job = mongo.db.jobs.find_one({'_id': _id})
    tasks = job.get('data').get('tasks')
    for task in tasks:
        data = {
            'name': task.get('name'),
            'datetime': now(),
            'status': 'future',
            'owner': job.get('owner'),
            'priority': job.get('priority'),
            'is_active': True,
            'slave': None,
            'last_activity': now(),
            'started_on': None,
            'finished_on': None,
            'paused_on': None,
            'logs': [],
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
        print newTask

    return


def getJobStatus(tasks):
    """Calculate Job Status"""
    if not tasks:
        return 'Completed'
    result = 'Likely'
    for st in ['failed', 'likely','paused', 'cancelled', 'waiting', 'future']:
        if all([s.get('status') == st for s in tasks]):
            return st.title()


    ''' On progress tasks are those whom status are on progress, started but not finsihed'''
    if any([s for s in tasks if ((s.get('status') == 'on progress') and \
                                 s.get('started_on') and not s.get('finished'))]):
        return 'On Progress'

    return 'Waiting'


def getClientJobsInformation(client):
    """Lists active client jobs."""
    getSlaveForDispatch()
    #jobs = mongo.db.jobs.find({'owner': client, 'is_active': True})
    jobs = mongo.db.jobs.find({'is_active': True})



        #        result = i.title()
        # if any([s.get('status')=='on progress' for s in tasks]):
        #    result = 'On Progress'
        # return result

    result = [{
        'name': j.get('name'),
        'datetime': j.get('datetime'),
        'status': getJobStatus(list(mongo.db.tasks.find({'job': j.get('_id'), 'status':{'$ne':'completed'}}))),
        'priority': j.get('priority'),
        'progress': sum([t.get('progress') for t in mongo.db.tasks.find({'job': j.get('_id')})]) /
        (mongo.db.tasks.find({'job': j.get('_id')}).count() or -1),
        'id': str(j.get('_id')),
        'tasks_count': mongo.db.tasks.find({'job': j.get('_id'), 'is_active': True}).count(),
        'failed_count': mongo.db.tasks.find({'job': j.get('_id'), 'is_active': True, 'status': 'failed'}).count(),
        'active_task':'Frame 43',
    } for j in jobs]
    return result or {}


def getSlaveForDispatch():
    '''
    Find the best slave for dispatching process
    example:
        machine 1 benchmark is 1000 and has 25 active tasks
        machine 2 benchmark is 4000 and has 80 active tasks
        So:
            freeness of machine 1 is: 25/1000 = .025
            and freeness of machine 2 is: 80/4000 = .020

            So:
                machine 2 is better choice

    '''
    seconds_ago = now() - 60

    '''Remove off slaves'''
    looking_for = {
        # $gt means greater than.  $lt means less than
       'last_ping': {'$lt': seconds_ago},
    }
    bulk = mongo.db.tasks.initialize_unordered_bulk_op()
    bulk.find(looking_for).update({
                                '$set': {
                                    'info.worker': False,
                                }})
    bulk.execute()

    looking_for = {
        # $gt means greater than.  $lt means less than
        'last_ping': {'$gt': seconds_ago},
        'info.cpu_count': {'$gt': 0},
        'info.qmark': {'$gt': 0},
        'info.cores': {'$ne': 0},
        'info.worker':True,
    }
    slaves = list(mongo.db.slaves.find(looking_for))
    print slaves




    if not slaves:
        return
    freeness_list = [
        (mongo.db.tasks.find({'is_active': True, 'slave':i.get('ip')}).count() or -1) /
        (float(i.get('info').get('qmark', 0.000001)) * i.get('info').get('cpu_count') * 80)
        for i in slaves]

    best_pos = freeness_list.index(min(freeness_list))
    bestChoice = slaves[best_pos]
    return bestChoice.get('ip')

def dispatchTasksJob(job, slave=None):
        """now find available tasks"""
        looking_for = {
            'is_active': True,
            'status': 'future',
            'slave': None,
            'job': job.get('_id')
        }

        tasks = mongo.db.tasks.find(looking_for)
        '''Create buckets of tasks'''
        buckets = chunks(list(tasks), job.get('bucket_size', 10))
        for bucket in buckets:
            if not slave:
                bestChoice = mongo.db.slaves.find({'ip': getSlaveForDispatch()})
                if bestChoice.count():
                    slave = bestChoice.next()
                else:
                    print 'Slave not found!!'
                    continue
            '''Lets add bucket tasks to slave queue'''
            '''update slave info on db'''
            mongo.db.slaves.update({'_id':slave.get('_id')}, slave)

            for task in bucket:
                if not hasattr(slave, 'queue'):
                    slave['queue'] = []
                slave['queue'].append(task.get('_id'))
                """Lets update slave info"""
                mongo.db.slaves.update({'_id': slave['_id']}, slave)
                task['status'] = 'likely'
                task['slave'] = slave.get('ip')
                print '%s tasks submited to %s' % (len(bucket), slave.get('identity') or slave.get('ip'))
                mongo.db.tasks.update({'_id': task['_id']}, task)

        _d = copy(job)
        _d['status'] = 'dispatched'
        print mongo.db.jobs.update({'_id': job.get('_id')}, _d)

def dispatchTasks(slave=None):
    """Dispatch tasks every few seconds using an agent
        If slave is something, then we force add the task to that slave.
    """
    """find none_finished jobs"""
    looking_for = {
        #'$and' : [{ 'status':{'$ne':'completed'} }, { 'status':{'$ne':'cancelled'}}, {'status'}],
        'status': 'future',
        'is_active': True
    }
    for job in mongo.db.jobs.find(looking_for):
        dispatchTasksJob(job, slave)


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
    job['status'] = 'future'
    """Set status of job to future"""
    mongo.db.jobs.update({'_id':_id}, job)
    """Bulk update tasks"""
    bulk = mongo.db.tasks.initialize_unordered_bulk_op()
    bulk.find({'job':_id, 'status':{'$ne':'completed'} }).update({
                                '$set': {
                                    'status': "future",
                                    'restarted_on':now(),
                                    'slave':None,
                                }})
    bulk.execute()

    return {'info':'success'}


def pauseJob(_id):
    """Pause the job.
    Pausing a job means changing all ready tasks tasks status to pause.
    """
    job = mongo.db.jobs.find_one({'_id':_id})
    job['status'] = 'paused'
    """Set status of job to paused"""
    mongo.db.jobs.update({'_id':_id}, job)
    """Bulk update tasks"""
    bulk = mongo.db.tasks.initialize_unordered_bulk_op()
    bulk.find({'job':_id, 'status':'ready' }).update({
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
    job = mongo.db.jobs.find_one({'_id':_id})
    """Set status of job to future"""
    job['status'] = 'future'
    """find slave"""
    slave = mongo.db.slaves.find_one({'ip':client})
    mongo.db.jobs.update({'_id':_id}, job)
    """Bulk update tasks"""
    bulk = mongo.db.tasks.initialize_unordered_bulk_op()
    bulk.find({'job':_id, 'status':{'$ne':'completed'} }).update({
                                '$set': {
                                    'status': "future",
                                    'paused_on':now(),
                                    'slave': None,
                                }})
    bulk.execute()

    dispatchTasks(slave)

    return {'info':'success'}


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
	slaves = mongo.db.slaves.find()
        #for i in slaves:
            #if  now() - i.get('last_ping')<20:
            #    print i.get('ip')
	return dumps(slaves)

def getJobDetail(_id):
    '''Get job detail for show in a modal'''
    job = mongo.db.jobs.find_one({'_id':_id})
    output = {}
    output['jobInfo'] = ujson.loads(dumps(job))
    tasks = list(mongo.db.tasks.find({'job':_id}))
    output['tasksInfo'] = ujson.loads(dumps(tasks))
    return output
