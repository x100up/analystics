# -*- coding: utf-8 -*-
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from hive_service import ThriftHive

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