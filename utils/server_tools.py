
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

CONFIG = readConfig()


def getRenderCommand(category):
    if category == 'Alfred':
        command = 'prman -cwd {cwd} -t:{threads} -Progress {filepath}'
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
    for st in ['likely','paused', 'cancelled', 'waiting', 'future']:
        if all([s.get('status') == st for s in tasks]):
            return st.title()


    ''' On progress tasks are those whom status are on progress, started but not finsihed'''
    if any([s for s in tasks if ((s.get('status') == 'on progress') and \
                                 s.get('started_on') and not s.get('finished'))]):
        return 'On Progress'

    for t in tasks:print t.get('status')
    return 'n/a'


def getClientJobsInformation(client):
    """Lists active client jobs."""
    getSlaveForDispatch()
    jobs = mongo.db.jobs.find({'owner': client, 'is_active': True})



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
    return result or '{[]}'


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
    seconds_ago = now() - 10
    looking_for = {
        # $gt means greater than.  $lt means less than
        'last_ping': {'$gt': seconds_ago},
        'info.cpu_count': {'$gt': 0},
        'info.qmark': {'$gt': 0},
        'info.cores': {'$ne': 0},
    }
    slaves = list(mongo.db.slaves.find(looking_for))
    if not slaves:
        return
    freeness_list = [
        (mongo.db.tasks.find({'is_active': True}).count() or -1) /
        (float(i.get('info').get('qmark', 0.000001))
         * i.get('info').get('cpu_count') * 80)
        for i in slaves]

    best_pos = freeness_list.index(min(freeness_list))
    bestChoice = slaves[best_pos]
    return bestChoice.get('ip')


def dispatchTasks():
    """Dispatch tasks every few seconds using an agent"""
    """find none_finished jobs"""
    looking_for = {
        #'$and' : [{ 'status':{'$ne':'completed'} }, { 'status':{'$ne':'cancelled'}}, {'status'}],
        'status': 'future',
        'is_active': True
    }

    for job in mongo.db.jobs.find(looking_for):
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
                slave['queue'].append(task.get('_id'))
                task['status'] = 'likely'
                task['slave'] = slave.get('ip')
                mongo.db.tasks.update({'_id': task['_id']}, task)

            _d = copy(job)
            _d['status'] = 'dispatched'
            print mongo.db.jobs.update({'_id': job.get('_id')}, _d)
            return


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
