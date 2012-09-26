# -*- coding: utf-8 -*-
import os, json, shutil, cPickle, logging

class WorkerService(object):

    RESULT_FILE = 'result.json'


    def __init__(self, path, worker):
        self.path = path
        self.worker = worker
        self.task = None
        self.query = None
        self.result = None

    def getWorker(self):
        return self.worker

    def setQuery(self, query):
        self.query = query

    def setFields(self, fields):
        self.fields = fields

    def setTask(self, task):
        self.task = task

    def getFolder(self):
        return self.path + '/' + str(self.worker.workerId)

    def init(self):
        # create folders
        os.makedirs(self.getFolder())

        for_json = {
            'workId': self.worker.workerId,
            'start': str(self.worker.startDate),
            'query': self.query,
            'fields' : self.fields,
            #'task': self.task.serialize()
        }
        job_json = json.dumps(for_json)
        f = open(self.getFolder() + '/job.json', 'w+')
        f.write(job_json)
        f.close()

        #  Создаем cPickle задачи, т.к. нах писать serialize и unserialize
        picklerFile = open(self.getFolder() + '/task.pickle', 'wb')
        pickler = cPickle.Pickler(picklerFile)
        pickler.dump(self.task)
        picklerFile.close()

    def getTask(self):
        if not self.task:
            picklerFile = open(self.getFolder() + '/task.pickle', 'rb')
            pickler = cPickle.Unpickler(picklerFile)
            self.task = pickler.load()
            picklerFile.close()
        return self.task

    def flushResult(self, result):
        f = open(self.getFolder() + '/' + self.RESULT_FILE, 'w+')
        f.write(json.dumps(result))
        f.close()

    def getResultData(self):
        if not self.result:
            f = open(self.getFolder() + '/' + self.RESULT_FILE, 'r')
            self.result = json.load(f)
            f.close()
        return self.result

    def getResults(self):
        result = self.getResultData()
        return result['result']

    def getError(self):
        try:
            result = self.getResultData()
        except BaseException as exception:
            message = 'Cant open result of task, because:  {} :: {}'.format(exception.__class__.__name__, exception.message)
            logging.getLogger('AnalyticsServer').error(message)
            return message
        else:
            if result.has_key('exception'):
                ex = ''
                for key in result['exception']:
                    ex += key + ' => ' + result['exception'][key] + ';'
                return 'Task except: ' + ex
            else:
                return 'Wrong date in task result'

    def delete(self):
        shutil.rmtree(self.getFolder())