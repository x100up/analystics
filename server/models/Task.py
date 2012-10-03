# -*- coding: utf-8 -*-
from __builtin__ import object
from datetime import datetime, timedelta
import time

class Task(object):
    INTERVAL_MINUTE = 'minute'
    INTERVAL_10_MINUTE = '10minutes'
    INTERVAL_HOUR = 'hour'
    INTERVAL_DAY = 'day'
    INTERVAL_WEEK = 'week'

    intervals = (
        (INTERVAL_MINUTE, u'1 минута'),
        (INTERVAL_10_MINUTE, u'10 минут'),
        (INTERVAL_HOUR, u'час'),
        (INTERVAL_DAY, u'день'),
        (INTERVAL_WEEK, u'неделя')
    )

    def __init__(self, *args, **kwargs):
        self.items = {}
        self.appname = ''
        self.interval = self.INTERVAL_HOUR
        self.stageCount = 0

        if kwargs.has_key('appname'):
            self.appname = kwargs['appname']

        if kwargs.has_key('interval'):
            self.interval = kwargs['interval']

    def addTaskItem(self, taskItem):
        self.items[taskItem.index] = taskItem

    def getTaskItem(self, index):
        if self.items.has_key(index):
            return self.items[index]


    def getFields(self, index):
        if self.items.has_key(index):
            return self.items[index].getFields()

    def getFieldsCount(self):
        '''
        Возвращает количество полей для всего таска, которое равно макс кол-ву полей taskItem
        '''
        return max([len(self.items[i].getFields()) for i in self.items])



class TaskItem():

    def __init__(self, *args, **kwargs):
        self.index = 0
        self.start = None
        self.end = None
        self.key = None
        self.operations = {}
        self.conditions = {}

        if kwargs.has_key('start'):
            self.start = kwargs['start']
        else:
            now = datetime.now()
            time = now.time()
            self.start = now - timedelta(hours = time.hour, minutes = time.minute, seconds = time.second)

        if kwargs.has_key('end'):
            self.end = kwargs['end']
        else:
            self.end = self.start + timedelta(days = 1)

        if kwargs.has_key('key'):
            self.key = kwargs['key']

        if kwargs.has_key('index'):
            self.index = kwargs['index']

        self.fields = [ ('"' + str(self.index) + '"', 'index'), ('count(1)','count') ]

    def addCondition(self, tag, values):
        self.conditions[tag] = values

    def setTagOperations(self, tagName, operations):
        self.operations[tagName] = operations

    def getTagOperations(self, tagName):
        if self.operations.has_key(tagName):
            return self.operations[tagName]
        return []

    def getFields(self):
        fields = []
        for tag, operations in self.operations.items():
            if 'sum' in operations:
                fields.append('SUM(params[\'{0}\'])'.format(tag))

            if 'avg' in operations:
                fields.append('AVG(params[\'{0}\'])'.format(tag))

            if 'group' in operations:
                fields.append('params[\'{0}\']'.format(tag))

        return self.fields + fields

    def getExtraFields(self):
        '''

        '''
        fields = []
        for tag, operations in self.operations.items():
            if 'sum' in operations:
                fields.append(('sum', tag))

            if 'avg' in operations:
                fields.append(('avg', tag))

            if 'group' in operations:
                fields.append(('group', tag))

        return fields