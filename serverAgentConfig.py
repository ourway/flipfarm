from datetime import timedelta

CELERYBEAT_SCHEDULE = {
    'dispatch_tasks': {
        'task': 'serverAgent.dispatch',
        'schedule': timedelta(seconds=5),
        #'args': (1,2),
    }
}

