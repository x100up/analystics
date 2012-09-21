
import os, json, shutil
from models.Task import Task

class WorkerService(object):

    def __init__(self, path, worker):
        self.path = path
        self.worker = worker

    query = None

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
            'task': self.task.serialize()
        }

        job_json = json.dumps(for_json)
        f = open(self.getFolder() + '/job.json', 'w+')
        f.write(job_json)
        f.close()

    def getTask(self):
        f = open(self.getFolder() + '/job.json', 'r')
        data = json.load(f)
        task = Task()
        task.unserialize(data['task'])
        return task


    def flushResult(self, result):
        f = open(self.getFolder() + '/result.json', 'w+')
        f.write(json.dumps(result))
        f.close()

    def getResultData(self):
        f = open(self.getFolder() + '/result.json', 'r')
        result = json.load(f)
        f.close()
        return result

    def getResults(self):
        result = self.getResultData()
        return result['result']

    def getError(self):
        try:
            result = self.getResultData()
        except BaseException as exception:
            return 'Cant open result of task, because: ' + str(exception.__class__.__name__) + ' :: ' + exception.message
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

