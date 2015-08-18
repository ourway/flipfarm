
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
@desc: models/db.py
@author: F.Ashouri
"""

__all__ = ['mongo', 'REDIS_CLIENT']

from utils.general import readConfig
from pymongo import MongoClient
import redis

CONFIG = readConfig()

redis_host = CONFIG.get('server').get('redis_host')
redis_port = CONFIG.get('server').get('redis_port')
REDIS_CLIENT = redis.Redis(host=redis_host, port=int(redis_port))

mongo_host = CONFIG.get('server').get('mongo_host')
mongo_port = CONFIG.get('server').get('mongo_port')
client = MongoClient(host=mongo_host, port=int(mongo_port))
mongo = client.flipfarm_server_011
