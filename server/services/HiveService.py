# -*- coding: utf-8 -*-
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from hive_service import ThriftHive
import logging

class HiveService():
    '''
    Инкапсулируем hive
    '''

    def __init__(self, host, port):
        self.transport = TTransport.TBufferedTransport(TSocket.TSocket(host, port))
        self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
        self.client = ThriftHive.Client(self.protocol)

    isOpen = False

    def open(self):
        try:
            self.transport.open()
        except BaseException as exception:
            logging.getLogger('AnalyticsServer').error('{}:{}'.format(exception.__class__.__name__, exception.message))
        finally:
            self.isOpen = True

    def execute(self, query):
        if  not self.isOpen:
            self.open()

        self.client.execute(query)
        return self.parseResult(self.client.fetchAll())

    def parseResult(self, result):
        data = []
        for row in result:
            data.append(row.split("\t"))

        return data

    def close(self):
        if  self.isOpen:
            self.transport.close()