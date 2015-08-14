
from kombu import Exchange, Queue
from datetime import timedelta
from utils.client_tools import user, MAC

#queueName = '%s-%s'%(user, MAC)
queueName = 'FFarmRenderQueue01'
CELERY_TASK_SERIALIZER = 'msgpack'
CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml', 'pickle']

CELERYBEAT_SCHEDULE = {
    'ping': {
        'task': 'clientAgent.ping',
        'schedule': timedelta(seconds=5),
        #'args': (1,2),
    }
}

CELERY_DEFAULT_QUEUE = queueName
CELERY_QUEUES = (
            Queue(queueName, Exchange(queueName), routing_key=queueName),
)
