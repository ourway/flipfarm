from kombu import Exchange, Queue
from datetime import timedelta
from utils.client_tools import user, MAC

queueName = '%s-%s-server'%(user, MAC)

CELERY_DEFAULT_QUEUE = queueName
CELERY_QUEUES = (
            Queue(queueName, Exchange(queueName), routing_key=queueName),
)
CELERY_TASK_SERIALIZER = 'msgpack'
CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']


CELERYBEAT_SCHEDULE = {
    'dispatch_tasks': {
        'task': 'serverAgent.dispatch',
        'schedule': timedelta(seconds=5),
        #'args': (1,2),
    }
}
