
import os
import json

class WorkerService(object):

    def __init__(self, path):
        self.path = path

    def getFolder(self, uuid):
        return 'result/' + uuid

    def initWorker(self, worker):
        # create folders
        folder = self.getFolder(worker.uuid)
        os.makedirs(folder)

        j = {
            'workId' : worker.uuid,
            'start' : str(worker.startDate)
        }
        job_json = json.dumps(j)
        f = open(self.path + '/job.json', 'w+')
        f.write(job_json)
        f.close()

    def flushResult(self, workerUUID, data):
        folder = self.getFolder(workerUUID)
        f = open(self.path + '/result.txt', 'w+')
        f.write(json.dumps(data))
        f.close()

