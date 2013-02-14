# -*- coding: utf-8 -*-
import threading
import logging
from datetime import datetime

from thrift import Thrift
from thrift.transport.TTransport import TTransportException
from hive_service.ttypes import HiveServerException
from models.Worker import Worker
from components.HiveResponseProcessor import HiveResponseProcessor
from services.HiveService import HiveService


class HiveWorker(threading.Thread):
    """
    Тред для выполнения запроса к hive
    """
    def __init__ (self, workerService):
        self.mysqlSessionMaker = None
        self.folderForWorkerService = None
        self.host = None
        self.port = None
        self.version = 1
        self.logger = logging.getLogger('AnalyticsServer')
        threading.Thread.__init__(self)
        self.daemon = True
        self.workerService = workerService

    def setVersion(self, version):
        self.version = version

    def setTask(self, task):
        self.task = task

    def run(self):
        print 'run HiveWorker'
        self.logger.debug('worker [' + self.getName() + '] run')
        hiveClient = None
        try:
            hiveClient = HiveService(self.host, self.port)
            processor = HiveResponseProcessor(task=self.task)
            data = []
            for query in self.workerService.querys:
                print 'run {}'.format(query)
                dataPart = hiveClient.execute(query)
                print 'Data responsed'
                #print dataPart
                data += dataPart

            #print data
            print 'process data'
            data = {'result' : processor.prepareData(data)}
            print 'end process data'
            self.logger.debug('worker [' + self.getName() + '] end job')
            status = Worker.STATUS_SUCCESS
        except Thrift.TException as tx:
            data = {'exception' : {'Thrift.TException' : tx.message }}
            status = Worker.STATUS_ERROR
            self.logger.error(tx.message)
        except TTransportException as tx:
            data = {'exception' : {u'Ошибка связи с Hive' : tx.message }}
            status = Worker.STATUS_ERROR
            self.logger.error(tx.message)
        except HiveServerException as tx:
            data = {'exception' : {'HiveServerException': tx.message }}
            status = Worker.STATUS_ERROR
            self.logger.error(tx.message)
        except Exception as tx:
            print tx.message
            print tx.args
            data = {'exception': {'Exception': str(tx.message)}}
            status = Worker.STATUS_ERROR
            self.logger.error(tx.message)
        finally:
            if hiveClient:
                hiveClient.close()

        worker = self.workerService.getWorker()
        session = self.mysqlSessionMaker()
        worker.endDate = datetime.now()
        worker.status = status
        session.merge(worker)
        session.commit()
        session.close()
        self.workerService.saveResult(data, self.version, worker.startDate, worker.endDate)