

from celery import Celery
from utils.server_tools import dispatchTasks

BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'



ca = Celery('serverAgent', broker=BROKER_URL, backend=CELERY_RESULT_BACKEND)
ca.config_from_object('serverAgentConfig')



@ca.task(name='serverAgent.dispatch')
def dispatch():
    '''dispatch tasks'''
    return dispatchTasks()






if __name__ == '__main__':
    pass
    #directory ='/Users/farsheed/Downloads/ToyStory3'
    #filename = 'sequences/seq_00/shot_00_00/renderman/Shot_00_00_0730011249/rib/0007/0007.rib'
    #md = 'prman -Progress {f}'.format(f=filename)
    #execute.delay(cmd, 'testdev2', directory)
    #getTasks.delay()


