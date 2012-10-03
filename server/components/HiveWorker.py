# -*- coding: utf-8 -*-
import threading
import logging
import time
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
        self.logger = logging.getLogger('AnalyticsServer')
        threading.Thread.__init__(self)
        self.daemon = True
        self.workerService = workerService

    def setTask(self, task):
        self.task = task

    def run(self):
        self.logger.debug('worker [' + self.getName() + '] run')
        hiveClient = None
        try:
            hiveClient = HiveService(self.host, self.port)
            data = {'result' : self.prepareData(hiveClient.execute(self.workerService.query))}
            self.logger.debug('worker [' + self.getName() + '] end job')
            status = Worker.STATUS_SUCCESS

        except Thrift.TException as tx:
            data = {'exception' : {'Thrift.TException' : tx.message }}
            status = Worker.STATUS_ERROR
            self.logger.error(tx.message)
        except HiveServerException as tx:
            data = {'exception' : {'HiveServerException': tx.message }}
            status = Worker.STATUS_ERROR
            self.logger.error(tx.message)
        #except Exception as tx:
        #    data = {'exception' : {'Exception': tx.message }}
        #    status = Worker.STATUS_ERROR
        #    self.logger.error(tx.message)
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
        newdata = {}

        #multySeria = len(self.task.items) > 1

        interval = self.task.interval
        for item in data:
            # первое значение - это номер задачи
            offset = 1
            y = 0

            if interval == Task.INTERVAL_MINUTE or interval == Task.INTERVAL_10_MINUTE:
                y = datetime(int(item[offset + 0]), int(item[offset + 1]), int(item[offset + 2]), hour = int(item[offset + 3]),
                             minute = int(item[offset + 4]))
                offset += 5
            elif interval == Task.INTERVAL_HOUR:
                y = datetime(int(item[offset + 0]), int(item[offset + 1]), int(item[offset + 2]), hour = int(item[offset + 3]))
                offset += 4
            elif interval == Task.INTERVAL_DAY:
                y = datetime(int(item[offset + 0]), int(item[offset + 1]), int(item[offset + 2]))
                offset += 3
            elif interval == Task.INTERVAL_WEEK:
                y = time.strptime('{} {} 1'.format(item[offset + 0], item[offset + 1]), '%Y %W %w')
                y = datetime.fromtimestamp(time.mktime(y))
                offset += 2


            # следующее поле - индекс
            index = str(item[0 + offset])

            # следующее поле количество
            count = int(item[1 + offset])

            # формируем основу данных
            if not newdata.has_key(index):
                newdata[index] = {}

            # количество у нас считается всегда
            series_index = str(index) + '_count'

            # если не выбирали друге поля, то данные равны количеству
            if not newdata[index].has_key(series_index):
                newdata[index][series_index] = {'data':[],'params': [{'op':'count'}]}

            newdata[index][series_index]['data'].append([int(y.strftime("%s000")), count])

            # если есть не только номер серии и количество,
            # но и другие поля

            taskItem = self.task.getTaskItem(index)
            extraFields = taskItem.getExtraFields()
            offset += 2
            series_index = ''
            print '---------------------------------'
            print item
            print extraFields
            params = []
            value = count
            for operation, tag in extraFields:

                if operation == 'group':
                    # группировка - значение по умолчанию count
                    series_index += tag + '=' + item[offset]
                    params.append({'op': operation, 'tag': tag, 'value':item[offset]})
                else:
                    # sum или avg
                    # если выбраны обе операции, то это два разных значения в одной строке
                    # и пока нихера не будет работать
                    value = float(item[offset])
                    series_index = operation + '::' + tag
                    params.append({'op': operation, 'tag': tag})
                offset += 1

            print params

            if not newdata[index].has_key(series_index):
                newdata[index][series_index] = {'data': [], 'params': params}

            newdata[index][series_index]['data'].append([int(y.strftime("%s000")), value])



    # сортировка по дате
        for index in newdata:
            for series_index in newdata[index]:
                newdata[index][series_index]['data'] = sorted(newdata[index][series_index]['data'])

        return newdata