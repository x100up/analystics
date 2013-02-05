# -*- coding: utf-8 -*-
from __builtin__ import object


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
        self.name = ''
        self.interval = self.INTERVAL_DAY
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


    def getTaskItems(self):
        return self.items.values()


    def getFields(self, index):
        if self.items.has_key(index):
            return self.items[index].getFields()

    def getFieldsCount(self):
        '''
        Возвращает количество полей для всего таска, которое равно макс кол-ву полей taskItem
        @deprecated
        '''
        return max([len(self.items[i].getFields()) for i in self.items])

    def getFieldsNames(self):
        fieldsName = []
        for i in self.items:
            item = self.items[i]
            fieldsNames = item.getFieldsNames()
            for default, name in fieldsNames:
                if not name in fieldsName:
                    fieldsName.append((default, name))

        return fieldsName


