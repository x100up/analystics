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
            data = {'result' : self.prepareData(hiveClient.execute(self.workerService.query))}
            print 'worker [' + self.getName() + '] end job'
            status = Worker.STATUS_SUCCESS

        except Thrift.TException as tx:
            data = {'exception' : {'Thrift.TException' : tx.message }}
            status = Worker.STATUS_ERROR
        except HiveServerException as tx:
            data = {'exception' : {'HiveServerException': tx.message }}
            status = Worker.STATUS_ERROR
        #except Exception as tx:
        #    data = {'exception' : {'Exception': tx.message }}
        #    status = Worker.STATUS_ERROR
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
        self.workerService.flushResult(data)

    def prepareData(self, data):
        print 'prepareData'
        newdata = {}

        multySeria = len(self.task.items) > 1

        print 'is multy: ' + str(multySeria)
        interval = self.task.interval
        print 'interval: ' + str(interval)
        print 'rows = ' + str(len(data))
        for item in data:
            # первое значение - это номер задачи
            offset = 1
            print item
            y = 0
            if interval == Task.INTERVAL_HOUR:
                y = datetime(int(item[offset + 0]), int(item[offset + 1]), int(item[offset + 2]), int(item[offset + 3]))
                offset += 4

            if interval == Task.INTERVAL_MINUTE:
                y = '%(y)s/%(m)s/%(d)s %(h)s:%(M)s:00'%{'y':item[offset + 0], 'm':item[offset + 1], 'd':item[offset + 2], 'h':item[offset + 3], 'M':item[offset + 4]}
                offset += 5


            # следующее поле - индекс
            index = str(item[0 + offset])

            # следующее поле количество
            count = int(item[1 + offset])

            # получем спсок полей
            fields = self.task.getFields(index)
            print 'data fields for ' + str(index) + ' : ' + str(fields)

            # формируем основу данных
            if not newdata.has_key(index):
                newdata[index] = {}

            # количество у нас считается всегда
            series_index = str(index) + '_count'

            # если не выбирали друге поля, то данные равны количеству
            if not newdata[index].has_key(series_index):
                newdata[index][series_index] = {'data':[],'params': {'op':'count'}}

            newdata[index][series_index]['data'].append([int(y.strftime("%s000")), count])

            # дополнительные поля
            if len(fields) > 2:
                i = 2
                for expression, val_name in fields[i:]:
                    p_val = float(item[i + offset])
                    series_index =  val_name
                    _tmp, operation, tag = val_name.split('_', 2)

                    i += 1
                    if not newdata[index].has_key(series_index):
                        newdata[index][series_index] = {'data':[],'params': {'op':operation,'tag':tag}}
                    newdata[index][series_index]['data'].append([int(y.strftime("%s000")), p_val])

        # сортировка по дате
        for index in newdata:
            for series_index in newdata[index]:
                newdata[index][series_index]['data'] = sorted(newdata[index][series_index]['data'])

        return newdata