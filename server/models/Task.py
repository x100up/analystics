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



class TaskItem(object):

    def __init__(self, *args, **kwargs):
        self.index = 0
        self.start = None
        self.end = None
        self.key = None
        self.name = ''
        self.operations = {}
        self.conditions = {}
        # считать уникальную статистику
        self.userUnique = False

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

    def getFields(self, topQuery = True, isSubquery = False):
        '''
        depreatede
        '''
        fields = []
        for tag, operations in self.operations.items():
            if 'sum' in operations:
                if topQuery:
                    fields.append('SUM(params[\'{0}\']) AS `sum_{0}`'.format(tag))
                else:
                    fields.append('SUM(`sum_{0}`) AS `sum_{0}`'.format(tag))

            if 'avg' in operations:
                if topQuery:
                    fields.append('AVG(params[\'{0}\']) AS `avg_{0}`'.format(tag))
                else:
                    fields.append('AVG(`avg_{0}`) AS `avg_{0}`'.format(tag))

            if 'group' in operations:
                if topQuery:
                    fields.append('params[\'{0}\'] AS `group_{0}`'.format(tag))
                else:
                    fields.append('`group_{0}` AS `group_{0}`'.format(tag))

        if isSubquery:
            return fields

        return self.fields + fields

    def _getFields(self, topQuery = True, isSubquery = False):
        fields = {}
        for tag, operations in self.operations.items():
            if 'sum' in operations:
                if topQuery:
                    fields['`sum_{0}`'.format(tag)] = 'SUM(params[\'{0}\'])'.format(tag)
                else:
                    fields['`sum_{0}`'.format(tag)] = 'SUM(`sum_{0}`)'.format(tag)

            if 'avg' in operations:
                if topQuery:
                    fields['`avg_{0}`'.format(tag)] = 'AVG(params[\'{0}\'])'.format(tag)
                else:
                    fields['`avg_{0}`'.format(tag)] = 'AVG(`avg_{0}`)'.format(tag)

            if 'group' in operations:
                if topQuery:
                    fields['`group_{0}`'.format(tag)] =  'params[\'{0}\']'.format(tag)
                else:
                    fields['`group_{0}`'.format(tag)] = '`group_{0}`'.format(tag)

        return fields

    def getFieldsNames(self):
        names = []
        for tag, operations in self.operations.items():
            if 'sum' in operations:
                names.append(('0.0', '`sum_{0}`'.format(tag)))

            if 'avg' in operations:
                names.append(('0.0', '`avg_{0}`'.format(tag)))

            if 'group' in operations:
                names.append(('\'\'', '`group_{0}`'.format(tag)))

        return names

    def getExtraFields(self):
        '''

        '''
        fields = []
        for tag, operations in self.operations.items():
            if 'sum' in operations:
                fields.append(('sum', tag, '`sum_{0}`'.format(tag)))

            if 'avg' in operations:
                fields.append(('avg', tag, '`avg_{0}`'.format(tag)))

            if 'group' in operations:
                fields.append(('group', tag, '`group_{0}`'.format(tag)))

        return fields

    def __str__(self):
        return 'TaskItem {}'.format(self.index)