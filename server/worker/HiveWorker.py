import sys, threading
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from hive_service import ThriftHive
from service.WorkerService import WorkerService
from hive_service.ttypes import HiveServerException
from models.Worker import Worker
from  datetime import datetime

class HiveWorker(threading.Thread):

    mysqlSessionMaker = None
    folderForWorkerService = None

    def __init__ (self, query):
        threading.Thread.__init__(self)
        self.daemon = True
        self.query = query

    def run(self):
        print 'worker [' + self.getName() + '] run'
        try:
            # hive query
            transport = TSocket.TSocket('localhost', 10000)
            transport = TTransport.TBufferedTransport(transport)
            protocol = TBinaryProtocol.TBinaryProtocol(transport)
            client = ThriftHive.Client(protocol)
            transport.open()
            client.execute(self.query)
            data = {'result' : client.fetchAll()}
            print 'worker [' + self.getName() + '] end job'
            status = Worker.STATUS_SUCCESS

            transport.close()

        except Thrift.TException, tx:
            data = {'exception' : tx.message }
            status = Worker.STATUS_ERROR
        except HiveServerException, tx:
            data = {'exception' : tx.message }
            status = Worker.STATUS_ERROR
        except Exception, tx:
            data = {'exception' : tx.message }
            status = Worker.STATUS_ERROR

        session = self.mysqlSessionMaker()
        worker = session.query(Worker).filter_by(uuid = self.getName()).first()
        worker.endDate = datetime.now()
        worker.status = status
        session.add(worker)
        session.commit()

        ws = WorkerService(self.folderForWorkerService)
        ws.flushResult(self.getName(), data)
