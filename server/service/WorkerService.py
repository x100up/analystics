
import os
import json

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

    def getFolder(self):
        return 'result/' + self.worker.uuid

    def init(self):
        # create folders
        os.makedirs(self.getFolder())

        j = {
            'workId': self.worker.uuid,
            'start': str(self.worker.startDate),
            'query': self.query,
            'fields' : self.fields
        }

        job_json = json.dumps(j)
        f = open(self.getFolder() + '/job.json', 'w+')
        f.write(job_json)
        f.close()


    def flushResult(self, result):
        f = open(self.getFolder() + '/result.json', 'w+')
        f.write(json.dumps(result))
        f.close()

    def getResults(self):
        f = open(self.getFolder() + '/result.json', 'r')
        result = json.load(f)
        f.close()
        return result['result']

