# -*- coding: utf-8 -*-
from __builtin__ import object
from datetime import datetime

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
        self.items = []
        self.appname = ''
        self.interval = ''

        if kwargs.has_key('appname'):
            self.appname = kwargs['appname']

        if kwargs.has_key('interval'):
            self.interval = kwargs['interval']




    def addTaskItem(self, taskItem):
        self.items.append(taskItem)

    conditions = {}

    def addCondition(self, key, tag, values):
        if values is None:
            return

        if not self.conditions.has_key(key):
            self.conditions[key] = {}

        if len(values) == 1:
            values = values.pop()

        self.conditions[key][tag] = values

    fields = {'count':'count(1)'}

    def getFields(self, key):
        sql = []
        for fieldName, fieldExp in self.fields.items():
            sql.append('%(fieldExp)s AS %(fieldName)s'%{'fieldExp':fieldExp, 'fieldName':fieldName})

        return ', '.join(sql)

    def prepare(self):
        self.fields['year'] = 'year'
        self.fields['month'] = 'month'
        self.fields['day'] = 'day'

        if  self.interval == self.INTERVAL_MINUTE:
            self.fields['hour'] = 'hour'
            self.fields['minute'] = 'minute'

        if  self.interval == self.INTERVAL_10_MINUTE:
            self.fields['hour'] = 'hour'
            self.fields['minute'] = 'minute'

        if  self.interval == self.INTERVAL_HOUR:
            self.fields['hour'] = 'hour'

        if  self.interval == self.INTERVAL_DAY:
            pass

        if  self.interval == self.INTERVAL_WEEK:
            pass


class TaskItem():


    def __init__(self, *args, **kwargs):
        self.index = 0
        self.start = None
        self.end = None


        if kwargs.has_key('end'):
            self.end = kwargs['end']
        else:
            self.end = datetime.now()

        if kwargs.has_key('start'):
            self.start = kwargs['start']
        else:
            self.start = datetime.now()

        if kwargs.has_key('delta'):
            self.start = self.end - kwargs['delta']