from datetime import timedelta

CELERYBEAT_SCHEDULE = {
    'dispatch_tasks': {
        'task': 'task.dispatch',
        'schedule': timedelta(seconds=10),
        #'args': (1,2),
    }
}

