# Copyright (c) 2012-2014 Waldemar Augustyn. All rights reserved.

# Simple CPU bench mark test.
#
# It can be run stand alone on a command line:
#
#   python qmark.py
#
# or it can be invoked from a python program:
#
#   from qmark import qmark
#   result = qmark()

import gevent
from gevent.queue import Queue
import time

__all__ = ["qmark"]

CLIENTS = 419
SERVERS = 79
RUNS = 7


class QMark:
    ''' Simple CPU benchmark test
    Greenlet servers read messages from their queues, update trace information, 
    and send them back to the originators.

    Greenlet clients create a single message and pass it sequentially through
    all servers.  Clients exit when the message passes through all servers.  The
    test ends when all clients complete.

     Message format

        CMD:TRACE

        CMD		- command
                    exit	- exit
                    queue	- update trace and continue test

        TRACE	- list of visited clients and servers, the last item is the
                  originator of the message

     For example:

        server 1:	queue:client(1)
        client 1:	queue:client(1)-server(1)
        server 2:	queue:client(1)-server(1)-client(1)
        client 1:	queue:client(1)-server(1)-client(1)-server(2)
        ...

    '''

    def __init__(self, num_clients, num_servers, debug=False):
        self.num_clients = num_clients
        self.num_servers = num_servers
        self.debug = debug

    def client(self, cid):
        ''' Greenlet client
        '''
        count = self.num_servers
        dstid = divmod(cid, self.num_servers)[1]
        msgout = 'queue:client({0})'.format(cid)
        self.server_queues[dstid].put(msgout)
        for msg in self.client_queues[cid]:
            cmd, trace = msg.split(':')
            if self.debug:
                print('client({0}):  {1}'.format(cid, msg))
            count -= 1
            if count < 1:
                break
            dstid = divmod(dstid + 1, self.num_servers)[1]
            msgout = msg + '-client({0})'.format(cid)
            self.server_queues[dstid].put(msgout)
            gevent.sleep(0)
        if self.debug:
            print('client({0}):  exit'.format(cid))

    def run(self):
        '''Run the benchmark
        '''
        start_time = time.time()
        self.client_queues = [Queue() for _ in range(self.num_clients)]
        self.server_queues = [Queue() for _ in range(self.num_servers)]
        qglets = [gevent.spawn(self.server, ix)
                  for ix in range(self.num_servers)]
        cglets = [gevent.spawn(self.client, ix)
                  for ix in range(self.num_clients)]
        gevent.joinall(cglets)
        for qq in self.server_queues:
            qq.put('exit:admin')
        gevent.joinall(qglets)
        result = time.time() - start_time
        return result

    def server(self, sid):
        ''' Greenlet server
        '''
        for msg in self.server_queues[sid]:
            if self.debug:
                print('server({0}):  {1}'.format(sid, msg))
            cmd, trace = msg.split(':')
            if cmd == 'exit':
                break
            dstid = int(msg[msg.rindex('(') + 1: msg.rindex(')')])
            msgout = msg + '-server({0})'.format(sid)
            self.client_queues[dstid].put(msgout)
            gevent.sleep(0)


def run_qmark(num_clients, num_servers, num_runs=1):
    ''' run benchmark test
    '''

    if num_runs < 1:
        num_runs = 1
    runs = []   # List of bench mark results
    for ix in range(num_runs):
        qmark = QMark(num_clients, num_servers)
        result = qmark.run()
        runs.append(result)
    return runs


def qmark():
    ''' Return cpu performance indicator
    '''
    results = run_qmark(CLIENTS, SERVERS, RUNS)
    avg = sum(results) / len(results)
    return int(1000.0 / avg)


if __name__ == '__main__':
    import math
##    results = run_qmark(3, 2, 1)
##    results = run_qmark(419, 79, 7)
    results = run_qmark(CLIENTS, SERVERS, RUNS)
    num_runs = len(results)
    avg = sum(results) / num_runs
    sqr = [(x - avg) * (x - avg) for x in results]
    stdev = math.sqrt(sum(sqr) / num_runs)
    qm = int(1000.0 / avg)

    print('results [s]:  {0}'.format(
        '  '.join(['{0:5.3f}'.format(x) for x in results])))
    print('average [s]:  {0:5.3f}'.format(avg))
    print('stdev [s]:    {0:5.3f}'.format(stdev))
    print('qmark:        {0}'.format(qm))
##    print('qmark():      {0}'.format(qmark()))
