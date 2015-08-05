from datetime import timedelta

CELERYBEAT_SCHEDULE = {
    'get_latest_tasks': {
        'task': 'clientAgent.getLatestTasks',
        'schedule': timedelta(seconds=5),
        #'args': (1,2),
    }
}
