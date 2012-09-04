
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
        return 'result/' + self.worker.uuid

    def init(self):
        # create folders
        os.makedirs(self.getFolder())

        for_json = {
            'workId': self.worker.uuid,
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
        print self.getFolder() + '/job.json'
        f = open(self.getFolder() + '/job.json', 'r')
        data = json.load(f)
        task = Task()
        task.unserialize(data['task'])
        return task


    def flushResult(self, result):
        f = open(self.getFolder() + '/result.json', 'w+')
        f.write(json.dumps(result))
        f.close()

    def getResults(self):
        f = open(self.getFolder() + '/result.json', 'r')
        result = json.load(f)
        f.close()
        return result['result']

    def delete(self):
        shutil.rmtree(self.getFolder())

