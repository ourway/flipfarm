
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
@desc: utils/general.py
@author: F.Ashouri
"""
import os
import requests
from requests import ConnectionError
import msgpack
import ujson
import psutil
import uuid
import getpass
from datetime import datetime, timedelta
from utils.opensource.qmark import qmark

USER = getpass.getuser()

def getVersion():
    """Reads VERSION file in flipfarm root directory and returns"""
    with open('VERSION') as f:
        return f.read()


def readConfig():
    """Reads config.json and returns result"""
    if os.path.isfile('config.json'):
        with open('config.json') as f:
            return ujson.load(f)


def pack(data):
    """Packs data using msgpack.packb"""
    if data!=None:
        return msgpack.packb(data)
    else:
        return msgpack.packb('')

def unpack(data):
    """Unpacks data using msgpack.unpackb"""
    if data!=None:
        return msgpack.unpackb(data)
    else:
        return ''


def getMemoryInfo():
    """Gets memory information"""
    vmStats = psutil.virtual_memory()
    result = {
        'wired_memory': 0,
        'active_memory': vmStats[5] / 1024 / 1024,
        'inactive_memory': vmStats[6] / 1024 / 1024,
        'free_memory': vmStats[4] / 1024 / 1024,
        'real_mem_total': vmStats[0] / 1024 / 1024,
        'percent': vmStats[2],
    }
    return result


def getCPUInfo():
    """Gets CPU information"""
    return {
        'percpu': psutil.cpu_percent(percpu=1),
        'overall': psutil.cpu_percent(),
    }

def getDiskInfo():
    """Gets disk usage information"""
    home = os.getenv('HOME')
    data = psutil.disk_usage(home)
    return {
        'total': data[0],
        'used': data[1],
        'free': data[2],
        'percent': data[3]
    }


def getSystemInfo():
    """A wrapper aroung info methods"""
    CPUInfo = getCPUInfo()
    memoryInfo = getMemoryInfo()
    diskInfo = getDiskInfo()

    systemData = {
        'cpu_count': len(CPUInfo.get('percpu')),
        'memory': memoryInfo,
        'cpu': CPUInfo,
        'disk': diskInfo,
        'user': USER
    }
    return systemData


def getUUID():
    data = base64.encodestring(uuid.uuid4().get_bytes()).strip()[:-5]
    return data.replace('/', '').replace('+', '').replace('-', '')

def getBenchmark():
    """benchmarks system based on qmark opensource module"""
    return qmark()


def now():
    """ get current time in unix time """
    return int(datetime.now().strftime('%s'))

def chunks(l, n):
    """Yield successive n-sized chunks from l.
    http://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks-in-python
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

