# -*- coding: utf-8 -*-
import os, json, shutil, cPickle, logging, time

class WorkerService(object):

    RESULT_FILE = 'result.json'

    def __init__(self, path, worker = None):
        self.version = 1
        self.path = path
        self.task = None
        self.query = []
        self.result = None
        if worker:
            self.setWorker(worker)

    def setWorker(self, worker):
        self.worker = worker

    def getWorker(self):
        return self.worker

    def setQuery(self, querys):
        self.querys = querys

    def setTask(self, task):
        self.task = task

    def getFolder(self):
        return self.path + '/' + str(self.worker.workerId)

    def init(self):
        # create folders
        if self.version == 1:
            os.makedirs(self.getFolder())

        for_json = {
            'workId': self.worker.workerId,
            'querys': self.querys,
            'version': self.version
        }
        job_json = json.dumps(for_json, sort_keys=True, indent=4)
        f = open(self.getFolder() + '/job.json', 'w+')
        f.write(job_json)
        f.close()

        if self.version == 1:
            #  Создаем cPickle задачи, т.к. нах писать serialize и unserialize
            picklerFile = open(self.getFolder() + '/task.pickle', 'wb')
            pickler = cPickle.Pickler(picklerFile)
            pickler.dump(self.task)
            picklerFile.close()

    def load(self):
        f = open(self.getFolder() + '/job.json', 'r+')
        data = json.load(f)
        f.close()
        self.querys = data['querys']
        if not 'version' in data:
            data['version'] = 1
        self.version = data['version']

    def getTask(self):
        if not self.task:
            try:
                picklerFile = open(self.getFolder() + '/task.pickle', 'rb')
                pickler = cPickle.Unpickler(picklerFile)
                self.task = pickler.load()
                picklerFile.close()
            except IOError:
                pass
        return self.task

    def saveResult(self, result, version, startDate, endDate):
        if version != 1:
            data = self.getRawResults()
            # fix old versions
            if data.has_key('result'):
                data = {1:{'data': data}}
        else:
            data = {}

        data[version] = {'data': result, 'start': time.mktime(startDate.timetuple()), 'end': time.mktime(endDate.timetuple())}

        f = open(self.getFolder() + '/' + self.RESULT_FILE, 'w+')
        f.write(json.dumps(data, sort_keys=True, indent=4))
        f.close()

    def getResultData(self, version=None):
        self.result = self.getRawResults()

        # fix old versions
        if 'result'in self.result:
            self.result = {1: {'data':  self.result}}

        if version is None:
            version = max(self.result.keys())

        return self.result[version]

    def getRawResults(self):
        if not self.result:
            f = open(self.getFolder() + '/' + self.RESULT_FILE, 'r')
            self.result = json.load(f)
            f.close()
        return self.result


    def getError(self):
        try:
            result = self.getResultData()
        except BaseException as exception:
            message = 'Cant open result of task, because:  {} :: {}'.format(exception.__class__.__name__, exception.message)
            logging.getLogger('AnalyticsServer').error(message)
            return message
        else:

            if 'data' in result and 'exception' in result['data']:
                ex = ''
                for key in result['data']['exception']:
                    ex += key + ' => ' + str(result['data']['exception'][key]) + ';'
                return 'Task except: ' + ex
            else:
                return 'Wrong data in task result'

    def delete(self):
        shutil.rmtree(self.getFolder())