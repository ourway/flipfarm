
from kombu import Exchange, Queue
from datetime import timedelta
from utils.client_tools import user, MAC
from utils.general import readConfig

pools = readConfig().get('pools', [])

MAC = '%s-client' % MAC
#queueName = '%s-%s'%(user, MAC)
queueName = 'FFarmRenderQueue01'
CELERY_TASK_SERIALIZER = 'msgpack'
CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml', 'pickle']

BROKER_TRANSPORT_OPTIONS = {'fanout_prefix': True, 'fanout_patterns': True}
BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}  # 1 hour.

CELERY_DEFAULT_QUEUE = queueName
CELERY_QUEUES = (
    Queue(queueName, Exchange(queueName), routing_key=queueName),
)

for each in pools:
    CELERY_QUEUES += (Queue(each, Exchange(each), routing_key=each),)
