# coding=utf-8
__author__ = 'pavlenko.roman.spb@gmail.com'
from datetime import datetime

class NameConstructor(object):

    def __init__(self, appConfig, task = None):
        self.appConfig = appConfig
        self.task = task

    def generateTaskName(self):
        '''
        Генерирует имя задачи
        '''
        return "Новая задача"

    def getTaskItemName(self, taskItem):
        return self.getEventName(taskItem.key)

    def getEventName(self, eventCode):
        return self.appConfig.getEvent(eventCode).getName()

    def getKeyNameByIndex(self, index, params = None):
        '''
        return key name by taskItem index
        '''

        taskItem = self.task.getTaskItem(index)
        if taskItem:
            eventName = self.getEventName(taskItem.key)
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
                        appTag = self.appConfig.getTag(tag_key)
                        if appTag:
                            operation += '[' + appTag.getName() + '=' + str(value) + ']'


            return  eventName + operation

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
        tag = self.appConfig.getTag(tagCode)
        if tag:
                if tag.type == 'choose':
                    if tag.values.has_key(value):
                        tag_value = tag.values[value]
                    else:
                        tag_value = 'Unknow value"{}"'.format(tag_value)

                elif tag.type == 'boolean':
                    if int(value):
                        tag_value = u'Да'
                    else:
                        tag_value = u'Нет'
                elif tag.type == 'timestamp':
                    value = int(value)
                    tag_value = datetime.fromtimestamp(value).strftime('%d %m %Y %H:%M')

        return tag_value

    def getTagName(self, tagCode):
        '''
            Возвращает имя тега по коду
        '''
        tag = self.appConfig.getTag(tagCode)
        if tag:
            return tag.getName()
        return u'Нет тега'

    def prepareConditions(self, conditions):
        """
            Подготавливает список условий для отображения
        """
        result = []
        for tag, value in conditions:
            result.append((self.getTagName(tag), self.getTagValueName(tag, value), tag, value))

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
        op = u''
        if seriesGroup.operation == 'group' or seriesGroup.operation == 'count':
            op = u'Количество '
        elif seriesGroup.operation == 'sum':
            op = u'Сумма '
        elif seriesGroup.operation == 'avg':
            op = u'Среднее '
        return op



    def getSeriesGroupSecondName(self, seriesGroup):
        vals = []
        for s in seriesGroup.getSeries():
            vals.append(s.avg)

        if sum(vals) == 0:
            return u'нет данных'
        else:
            _min = min(vals)
            _max = max(vals)
            if _min == _max:
                return  u' в среднем {}'.format(int(_min))
            return u' от {} до {}'.format(int(_min), int(_max))

