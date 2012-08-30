import threading
from thrift import Thrift
from hive_service.ttypes import HiveServerException
from models.Worker import Worker
from datetime import datetime
from service.HiveService import HiveService

class HiveWorker(threading.Thread):

    mysqlSessionMaker = None
    folderForWorkerService = None
    host = None
    port = None

    def __init__ (self, workerService):
        threading.Thread.__init__(self)
        self.daemon = True
        self.workerService = workerService

    def run(self):
        print 'worker [' + self.getName() + '] run'
        hiveClient = None
        try:
            hiveClient = HiveService(self.host, self.port)
            data = {'result' : hiveClient.execute(self.workerService.query)}
            print 'worker [' + self.getName() + '] end job'
            status = Worker.STATUS_SUCCESS

        except Thrift.TException, tx:
            data = {'exception' : tx.message }
            status = Worker.STATUS_ERROR
        except HiveServerException, tx:
            data = {'exception' : tx.message }
            status = Worker.STATUS_ERROR
        except Exception, tx:
            data = {'exception' : tx.message }
            status = Worker.STATUS_ERROR
        finally:
            if hiveClient:
                hiveClient.close()

        worker = self.workerService.getWorker()
        session = self.mysqlSessionMaker()
        worker.endDate = datetime.now()
        worker.status = status
        session.merge(worker)
        session.commit()
        self.workerService.flushResult(data)

