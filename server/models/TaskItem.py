# coding=utf-8
__author__ = 'x100up'
from datetime import datetime, timedelta

class TaskItem(object):

    def __init__(self, *args, **kwargs):
        self.index = 0
        self.start = None
        self.end = None
        self.key = None
        self.name = ''
        self.operations = {}
        self.conditions = []
        # считать уникальную статистику
        self.userUnique = False

        if kwargs.has_key('start'):
            self.start = kwargs['start']
        else:
            now = datetime.now() - timedelta(days = 1)
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



    def addCondition(self, eventCode, tagCode, values):
        '''
        УСловия по значению
        '''
        self.conditions.append((eventCode, tagCode, values))

    def getConditionValue(self, eventCode, tagCode):
        for _eventCode, _tagCode, values in self.conditions:
            if eventCode == _eventCode and _tagCode == tagCode:
                return values

    def setTagOperations(self, tagName, operations):
        self.operations[tagName] = operations

    ##
    # Возвращает список операции для тега в этом таске
    ##
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
        '''

        '''
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