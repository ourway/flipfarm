
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
from utils.general import now, chunks, readConfig
from bson.json_util import dumps
from models.db import mongo
from celery import Celery

CONFIG = readConfig()


def getRenderCommand(category):
    if category == 'Alfred':
        command = 'prman -cwd {cwd} -t:{threads} -Progress {filepath}'
        return command


def createNewTasks(jobHash):
    """Create new tasks on database based on this new job"""
    job = mongo.db.jobs.find_one({'md5':jobHash})
    tasks = job.get('data').get('tasks')
    for task in tasks:
        data = {
            'name':task.get('name'),
            'datetime':now(),
            'status':'likely',
            'owner':job.get('owner'),
            'priority':job.get('priority'),
            'is_active':True,
            'progress':0,
            'job':job.get('_id'),
            'proccess':
                {
                    'command':getRenderCommand(job.get('category')),
                    'cwd':task.get('cwd'),
                }
        }
        newTask = mongo.db.tasks.insert(data)
        print newTask

    return

def getClientJobsInformation(client):
    """Lists active client jobs."""
    getSlaveForDispatch()
    jobs = mongo.db.jobs.find({'owner':client, 'is_active':True})
    result = [{
        'name':j.get('name'),
        'datetime':j.get('datetime'),
        'status':j.get('status').title(),
        'priority':j.get('priority'),
        'progress':j.get('progress'),
        'id':str(j.get('_id')),
        'tasks_count':mongo.db.tasks.find({'job':j.get('_id'), 'is_active':True}).count(),
        'failed_count':mongo.db.tasks.find({'job':j.get('_id'), 'is_active':True, 'status':'failed'}).count(),
    } for j in jobs]
    return result


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
    seconds_ago = now()-10
    looking_for = {
        'last_ping':{'$gt': seconds_ago},  ## $gt means greater than.  $lt means less than
        'info.cpu_count':{'$gt':0},
        'info.qmark':{'$gt':0},
    }
    slaves = list(mongo.db.slaves.find(looking_for))
    if not slaves:
        return
    freeness_list = [
        (mongo.db.tasks.find({'is_active':True}).count() or -1) /\
        (float(i.get('info').get('qmark', 0.000001)) * i.get('info').get('cpu_count')*80)
        for i in slaves]

    best_pos = freeness_list.index(min(freeness_list))
    bestChoice =  slaves[best_pos]
    return bestChoice.get('_id')


