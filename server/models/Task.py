# -*- coding: utf-8 -*-
from __builtin__ import object
from datetime import datetime
import time

class Task(object):


    INTERVAL_MINUTE = 'minute'
    INTERVAL_10_MINUTE = '10minutes'
    INTERVAL_HOUR = 'hour'
    INTERVAL_DAY = 'day'
    INTERVAL_WEEK = 'week'

    intervals = {
        INTERVAL_MINUTE: u'1 минута',
        INTERVAL_10_MINUTE: u'10 минут',
        INTERVAL_HOUR: u'час',
        INTERVAL_DAY: u'день',
        INTERVAL_WEEK: u'неделя'
    }

    def __init__(self, *args, **kwargs):
        self.items = {}
        self.appname = ''
        self.interval = ''

        if kwargs.has_key('appname'):
            self.appname = kwargs['appname']

        if kwargs.has_key('interval'):
            self.interval = kwargs['interval']

    def addTaskItem(self, taskItem):
        self.items[taskItem.index] = taskItem

    def getTaskItem(self, index):
        if self.items.has_key(index):
            return self.items[index]

    def serialize(self):
        si = []
        for index, item in self.items.items():
            si.append(item.serialize())

        return {
            'appname': self.appname,
            'interval': self.interval,
            'items': si,
        }

    def unserialize(self, data):
        self.appname = data['appname']
        self.interval = data['interval']
        for item in data['items']:
            self.addTaskItem(TaskItem.unserialize(item))

    def getFields(self, index):
        if self.items.has_key(index):
            return self.items[index].getFields()



class TaskItem():

    def __init__(self, *args, **kwargs):
        self.index = 0
        self.start = None
        self.end = None
        self.key = None
        self.tagGroup = set()
        self.conditions = {}

        if kwargs.has_key('end'):
            self.end = kwargs['end']
        else:
            self.end = datetime.now()

        if kwargs.has_key('key'):
            self.key = kwargs['key']

        if kwargs.has_key('index'):
            self.index = kwargs['index']

        if kwargs.has_key('start'):
            self.start = kwargs['start']
        else:
            self.start = datetime.now()

        if kwargs.has_key('delta'):
            self.start = self.end - kwargs['delta']

        self.fields = [ ('count(1)','value'), ('"' + str(self.index) + '"', 'index') ]

    def addCondition(self, tag, values):
        self.conditions[tag] = values

    def addTagGroup(self, tagName):
        self.tagGroup.add(tagName)

    def getFields(self):
        group_param_set = [ ('params[\'{0}\']'.format(x), 'params_{0}'.format(x)) for x in self.tagGroup]
        return self.fields + group_param_set

    def serialize(self):
        return {
            'index': self.index,
            'start': time.mktime(self.start.timetuple()),
            'end': time.mktime(self.end.timetuple()),
            'key': self.key,
            'conditions': self.conditions
        }

    @classmethod
    def unserialize(cls, data):
        item = TaskItem()
        item.start = datetime.fromtimestamp(data['start'])
        item.end = datetime.fromtimestamp(data['end'])
        item.key = data['key']
        item.conditions = data['conditions']
        item.index = data['index']
        return item