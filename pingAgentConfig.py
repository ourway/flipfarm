
from kombu import Exchange, Queue
from datetime import timedelta
from utils.client_tools import user, MAC


MAC = '%s-client'%MAC
#queueName = '%s-%s'%(user, MAC)
queueName = 'FFarmRenderQueue01'
CELERY_TASK_SERIALIZER = 'msgpack'
CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml', 'pickle']

CELERY_DEFAULT_QUEUE = MAC
CELERY_QUEUES = (
            Queue(MAC, Exchange(MAC), routing_key=MAC),
)


BROKER_TRANSPORT_OPTIONS = {'fanout_prefix': True, 'fanout_patterns': True}

CELERYBEAT_SCHEDULE = {
    'ping': {
        'task': 'pingAgent.ping',
        'schedule': timedelta(seconds=2),
        'options': {'queue' : MAC}

        #'args': (1,2),
    }
}

