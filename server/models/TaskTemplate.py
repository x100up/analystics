# -*- coding: utf-8 -*-
from Base import Base
from sqlalchemy import Column, Integer, String, Enum, ForeignKey
import cPickle
from datetime import datetime, timedelta

class TaskTemplate(Base):
    SHARED_YES = 'YES'
    SHARED_NO = 'NO'

    __tablename__ = "taskTemplate"
    taskTemplateId = Column(Integer, primary_key=True)
    name = Column(String(50))
    userId = Column(Integer, ForeignKey('user.userId'),  nullable = False)
    appId = Column(Integer, ForeignKey('app.appId'),  nullable = False)
    shared = Column(Enum('YES', 'NO'), default = 'NO', nullable = False)


class TaskTemplateFile():

    def __init__(self, folder, task = None, taskTemplate = None):
        self.folder = folder
        self.task = task
        self.taskTemplate = taskTemplate
        self.timeRelatively = False
        self.baseDate = None

    def save(self):
        picklerFile = open(self.folder + '/template.{}.pickle'.format(self.taskTemplate.taskTemplateId), 'wb')
        pickler = cPickle.Pickler(picklerFile)
        pickler.dump(self)
        picklerFile.close()

    def getTask(self):
        # меняем время на относительное
        if self.timeRelatively:
            delta = datetime.now() - self.baseDate
            delta = timedelta(days = delta.days)
            for i in self.task.items:
                self.task.items[i].start = self.task.items[i].start + delta
                self.task.items[i].end = self.task.items[i].end + delta

        return self.task

    @staticmethod
    def read(folder,taskTemplate):
        picklerFile = open(folder + '/template.{}.pickle'.format(taskTemplate.taskTemplateId), 'rb')
        pickler = cPickle.Unpickler(picklerFile)
        taskTemplateFile = pickler.load()
        picklerFile.close()
        return taskTemplateFile
