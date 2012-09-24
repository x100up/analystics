# -*- coding: utf-8 -*-
import threading
from thrift import Thrift
from hive_service.ttypes import HiveServerException
from models.Worker import Worker
from models.Task import Task
from datetime import datetime
from services.HiveService import HiveService

class HiveWorker(threading.Thread):
    '''
    Тред для выполнения запроса к hive
    '''
    def __init__ (self, workerService):
        self.mysqlSessionMaker = None
        self.folderForWorkerService = None
        self.host = None
        self.port = None

        threading.Thread.__init__(self)
        self.daemon = True
        self.workerService = workerService

    def setTask(self, task):
        self.task = task

    def run(self):
        print 'worker [' + self.getName() + '] run'
        hiveClient = None
        try:
            hiveClient = HiveService(self.host, self.port)
            data = {'result' : self.prepareData(hiveClient.execute('-- ' + str(self.getName()) + "\n" + self.workerService.query))}
            print 'worker [' + self.getName() + '] end job'
            status = Worker.STATUS_SUCCESS

        except Thrift.TException as tx:
            data = {'exception' : {'Thrift.TException' : tx.message }}
            status = Worker.STATUS_ERROR
        except HiveServerException as tx:
            data = {'exception' : {'HiveServerException': tx.message }}
            status = Worker.STATUS_ERROR
        except Exception as tx:
            data = {'exception' : {'Exception': tx.message }}
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
        session.remove()
        self.workerService.flushResult(data)

    def prepareData(self, data):
        print data
        newdata = {}

        multySeria = len(self.task.items) > 1

        for item in data:
            interval = self.task.interval
            offset = 3
            y = 0
            if multySeria:
                if interval == Task.INTERVAL_HOUR:
                    y = int(item[5])
            else:
                if interval == Task.INTERVAL_HOUR:
                    offset = 4
                    y = '%(y)s/%(m)s/%(d)s %(h)s:00:00'%{'y':item[0], 'm':item[1], 'd':item[2], 'h':item[3]}

                if interval == Task.INTERVAL_MINUTE:
                    offset = 5
                    y = '%(y)s/%(m)s/%(d)s %(h)s:%(M)s:00'%{'y':item[0], 'm':item[1], 'd':item[2], 'h':item[3], 'M':item[4]}


            # цикл по строкам
            x = float(item[0 + offset])
            index = item[1 + offset]
            fields = self.task.getFields(index)

            i = 2
            params = {}
            seria_index = index
            for ex, pn in fields[2:]:
                p_val = item[i + offset]
                seria_index +=  '_' + pn + '=' + p_val
                params[pn[7:] ] = p_val # remove params_ prefix
                i += 1

            if not newdata.has_key(index):
                newdata[index] = {}

            if not newdata[index].has_key(seria_index):
                newdata[index][seria_index] = {
                    'data':[],
                    'params': params,
                }

            newdata[index][seria_index]['data'].append([y, x])

        return newdata