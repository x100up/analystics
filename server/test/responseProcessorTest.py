#!/usr/bin/python
from components.HiveResponseProcessor import HiveResponseProcessor
from services.WorkerService import WorkerService
from models.Worker import Worker
import os, inspect, re

task = 1
_file = '/../TestHiveResponse'

thisPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) # script directory
resultPath = os.path.abspath(thisPath + '/../result/')

worker = Worker()
worker.workerId = task
workerService = WorkerService(resultPath, worker)
task = workerService.getTask()

r = re.compile('\s+')

f = open(os.path.abspath(thisPath + _file), 'r')
data = f.readlines()
data = [r.split(line) for line in data]

processor = HiveResponseProcessor(task)
processor.prepareData(data)