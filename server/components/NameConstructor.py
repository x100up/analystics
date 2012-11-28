# coding=utf-8
__author__ = 'pavlenko.roman.spb@gmail.com'
from components.dateutil import smartPeriod

class NameConstructor(object):

    def __init__(self, appConfig, task):
        self.appConfig = appConfig
        self.task = task

    def generateTaskName(self):
        '''
        Генерирует имя задачи
        '''
        result = ''
        index, taskItem = self.task.items.items()[0]
        key = taskItem.key
        if self.appConfig['keys'].has_key(key) and self.appConfig['keys'][key].has_key('name'):
            result = self.appConfig['keys'][key]['name']
        _smartPeriod = smartPeriod(taskItem.start, taskItem.end)
        result += ' ' + _smartPeriod

        if len(self.task.items) > 1:
            result += ' (+' + str(len(self.task.items) - 1) + ')'

        return result


    def getKeyNameByIndex(self, index, params = None):
        '''
        return key name by taskItem index
        '''

        tags = self.appConfig['tags']

        taskItem = self.task.getTaskItem(index)
        if taskItem:
            key_name = ''
            tag_name = u'Количество'
            operation = ''

            key = taskItem.key
            if self.appConfig['keys'].has_key(key) and self.appConfig['keys'][key].has_key('description'):
                key_name = self.appConfig['keys'][key]['description'] + key_name

            operation = ''
            if params:
                if params['op'] == 'group':
                    operation += u'/кол-во'
                    if params.has_key('extra') and params['extra'] == 'userunique':
                        operation += u' поль.'
                elif params['op'] == 'avg':
                    operation += u'/среднее'
                elif params['op'] == 'sum':
                    operation += u'/сумма'
                elif params['op'] == 'count':
                    operation += u'/кол-во'
                    if params.has_key('extra') and params['extra'] == 'userunique':
                        operation += u' поль.'

                if params.has_key('conditions'):
                    for condition in params['conditions']:
                        tag_key = condition[0]
                        value = condition[1]
                        if tags.has_key(tag_key) and tags[tag_key].has_key('name'):
                            tag_name = tags[tag_key]['name']
                            operation += '[' + tag_name + '=' + str(value) + ']'


            return  key_name + operation

        return 'not name for task item: ' + str(index)

    def getTableName(self, index):
        taskItem = self.task.getTaskItem(index)
        if taskItem:
            key = taskItem.key
            key_name = key
            if self.appConfig['keys'].has_key(key) and self.appConfig['keys'][key].has_key('name'):
                key_name = self.appConfig['keys'][key]['name']
            return key_name

        return 'not name for task item: ' + str(index)

    def getTagValueName(self, tagCode, value):
        '''
            Возвращает значение тега
        '''
        tag_value = value

        if tagCode in self.appConfig['tags'].keys():
            tagConf = self.appConfig['tags'][tagCode]

            type = None
            if tagConf.has_key('type'):
                type = tagConf['type']

                if type == 'choose':
                    print tagConf['values']
                    if tagConf.has_key('values') and isinstance(tagConf['values'], dict) and tagConf['values'].has_key(value):
                        tag_value = tagConf['values'][value]

                elif type == 'boolean':
                    if bool(value):
                        tag_value = u'Да'
                    else:
                        tag_value = u'Нет'

        return tag_value

    def getTagName(self, tagCode):
        '''
            Возвращает имя тега по коду
        '''
        if self.appConfig['tags'].has_key(tagCode) and self.appConfig['tags'][tagCode].has_key('name'):
            return self.appConfig['tags'][tagCode]['name']
        return tagCode

    def prepareConditions(self, conditions):
        """
            Подготавливает список условий для отображения
        """
        result = []
        for tag, value in conditions:
            result.append((self.getTagName(tag), self.getTagValueName(tag, value)))

        return result



    def getSeriaName(self):
        return 'seria name'

    def getOperationName(self, operation):
        if (operation == 'count'):
            return u'Количество'

        if (operation == 'sum'):
            return u'Сумма'

        if (operation == 'sum'):
            return u'Среднее'

        if (operation == 'group'):
            return u'Количество'

    def getSeriesGroupName(self, seriesGroup):
        vals = []
        for s in seriesGroup.getSeries():
            vals.append(s.avg)

        if sum(vals) == 0:
            return u' нет данных'
        else:
            _min = min(vals)
            _max = max(vals)
            return u' от {} до {}'.format(int(_min), int(_max))


        return u'Серия'