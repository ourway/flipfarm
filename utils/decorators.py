
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
@desc: utils/decorators.py
@author: F.Ashouri
"""

import functools

from models.db import REDIS_CLIENT


def decorator(d):
    """Make function d a decorator: d wraps a function fn.
     Peter Norvig, my good friend at Dropbox"""
    def _d(fn):
        return functools.update_wrapper(d(fn), fn)
    functools.update_wrapper(_d, d)
    return _d


@decorator
def Memoized(func):
    """Decorator that caches a function's return value  PS: Results
      This function is the reason I love python.
      without cache: 7.6e-06
      with cache: 3.2e-07
    """
    cache = {}
    key = (func.__module__, func.__name__)
    # print key
    if key not in cache:
        cache[key] = {}
    mycache = cache[key]

    def _f(*args):
        try:
            return mycache[args]
        except KeyError:
            value = func(*args)
            mycache[args] = value
            return value
        except TypeError:
            return func(*args)

    _f.cache = cache
    return _f


def only_one(function=None, key="", timeout=None):
    """Enforce only one celery task at a time."""

    def _dec(run_func):
        """Decorator."""

        def _caller(*args, **kwargs):
            """Caller."""
            ret_value = None
            have_lock = False
            lock = REDIS_CLIENT.lock(key, timeout=timeout)
            try:
                have_lock = lock.acquire(blocking=False)
                if have_lock:
                    ret_value = run_func(*args, **kwargs)
            finally:
                if have_lock:
                    lock.release()

            return ret_value

        return _caller

    return _dec(function) if function is not None else _dec
