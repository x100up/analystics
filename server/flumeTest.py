__author__ = 'prog-31'

#!/usr/bin/env python
#
# tap -> flume
#
# requires: python thrift bindings + compiled flume thrift binding.
#

import time, datetime, sys, os, multiprocessing
from multiprocessing import Process, Pool
import random
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

#sys.path.extend(['ep_man', 'thriftflume'])

#import tap
#import memcacheConstants

from plume.gen_py.flume import ThriftFlumeEventServer




class FlumeDest(object):

    def __init__(self, host, port):
        self.opened = False
        self.transport = TSocket.TSocket(host, port)
        self.transport = TTransport.TBufferedTransport(self.transport)
        self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
        self.client = ThriftFlumeEventServer.Client(self.protocol)
        self.n = 0

    def open(self):
        try:
            self.transport.open()
        except :
            pass
        else:
            self.opened = True

    def send(self):
            if not self.opened:
                return None

            d = datetime.datetime.now()

            evt = ThriftFlumeEventServer.ThriftFlumeEvent(timestamp=int(time.time()),
                priority = ThriftFlumeEventServer.Priority.INFO,
                body = 'ddddddddffffffffffffffffddddddddddddd',
                nanos = 0,
                host = 'agent',
                fields = {
                    'day':str(d.day),
                    'month':str(d.month),
                    'year': str(d.year),
                    'host':'load',
                    'key':'data'
                })
            try:
                self.client.append(evt)
                self.n += 1
            except :
                pass


def loadFlume(x):
    dest = FlumeDest('192.168.2.103', random.choice([5140, 5141, 5142, 5143, 5144, 5145, 5146, 5147, 5148, 5149]))
    count = 10000
    start = time.time()
    for i in range(0, count):
        dest.open()
        dest.send()

    return (dest.n, time.time() - start)

start = time.time()

print 'CPU COUNT = ' + str(multiprocessing.cpu_count())
pCount = 10

pool = Pool(processes=pCount)
result = pool.map_async(loadFlume, range(0, pCount))
allCount = 0
allTime = 0
for count, t in result.get():
    allCount += count
    allTime += t

timeElapsed =  time.time() - start
print 'send {0} event at {1} ec.'.format(allCount, timeElapsed)
print 'speed: ' + str(allCount / timeElapsed) + ' per/sec'