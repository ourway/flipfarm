
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

from pymongo import MongoClient
client = MongoClient()
mongo = client.flipfarm_server_009

import redis
from utils.general import readConfig

host = readConfig().get('server').get('host')
REDIS_CLIENT = redis.Redis(host=host)
