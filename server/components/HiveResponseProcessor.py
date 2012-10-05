# -*- coding: utf-8 -*-
from models.Task import Task, TaskItem
from datetime import datetime, timedelta, time
from pprint import pprint
import copy
class HiveResponseProcessor():

    def __init__(self, task):
        self.task = task
        self.operationsCache = {}

    def getDateMatrix(self, default = 0):
        '''
        Возвращает ожидаемы список дат с нулевыми значениями
        '''
        interval = self.task.interval
        delta = timedelta(minutes = 1)
        if interval == Task.INTERVAL_10_MINUTE:
            delta = timedelta(minutes = 10)
        elif interval == Task.INTERVAL_DAY:
            delta = timedelta(days = 1)
        elif interval == Task.INTERVAL_WEEK:
            delta = timedelta(days = 7)

        matrixes = {}
        for i in self.task.items:
            taskItem = self.task.items[i]
            start = taskItem.start
            end = taskItem.end
            matrix = {}
            while start < end:
                matrix[int(start.strftime("%s000"))] = default
                start = start + delta
            matrixes[i] = matrix
        return matrixes

    def registerDateParser(self):
        '''
        Регистрирует функцию парсинга даты
        '''
        interval = self.task.interval
        if interval == Task.INTERVAL_MINUTE or interval == Task.INTERVAL_10_MINUTE:
            self.dateParser = self._parserByMinute
        elif interval == Task.INTERVAL_HOUR:
            self.dateParser = self._parserByHour
        elif interval == Task.INTERVAL_DAY:
            self.dateParser = self._parserByDay
        elif interval == Task.INTERVAL_WEEK:
            self.dateParser = self._parserByWeek

    def prepareData(self, data):
        self.registerDateParser()
        dateMatrixes = self.getDateMatrix()
        result = {}
        for line in data:
            # данные в этой строке
            values = {}

            # получаем дату, первое значение - это номер задачи, поэтому смещение равно 1
            offset, date = self.dateParser(line, 1)
            date = int(date)

            # следующее поле - индекс подзадачи
            taskItemIndex = str(line[offset])
            offset += 1

            # следующее поле всегда количество, общее или группы
            count = int(line[offset])
            values['count'] = [count, {'op':'count'}]
            offset += 1


            taskItem = self.task.getTaskItem(taskItemIndex)
            extraFields = taskItem.getExtraFields()
            # если есть операции то есть и дополнительные поля
            if extraFields:
                params = [] # параметры выборк для этой строки
                for operation, tag in extraFields:
                    # операция, тег, значение
                    params.append((operation, tag, line[offset]))
                    offset += 1

                conditions = [] # список условий, применимых для этой строки
                for operation, tag, value in params:
                    if operation == 'group' :
                        # если есть группа, то кол-во не катит
                        # в строке всегда одна запись кол-во в группе
                        if values.has_key('count'):
                            del values['count']
                            values['group'] = [count, {'op' : 'group'}]

                        conditions.append((tag, value))
                    else:
                        # для каждого тега свое значение операции
                        values[operation + '_' + tag] = [float(value), {'op' : operation, 'tag': tag}]

                # кладем условия в каждое значение
                for index in values:
                    values[index][1]['conditions'] = conditions

            # строим id серии
            for index in values:
                value = values[index]
                seria_id = str(taskItemIndex) + '_' + index
                opts = value[1]
                if opts.has_key('conditions'):
                    for tag, tag_value in opts['conditions']:
                        seria_id += '_' + tag + '=' + tag_value

                if not result.has_key(taskItemIndex):
                    result[taskItemIndex] = {}

                if not result[taskItemIndex].has_key(seria_id):
                    # еще нет серии
                    result[taskItemIndex][seria_id] = {
                        'data': copy.copy(dateMatrixes[taskItemIndex]),
                        'params': opts
                    }

                if not result[taskItemIndex][seria_id]['data'].has_key(date):
                    print 'Warning: unexpected date '

                result[taskItemIndex][seria_id]['data'][date] = value[0]

        for taskItemIndex in result:
            for seria_id in result[taskItemIndex]:
                result[taskItemIndex][seria_id]['data'] = sorted(result[taskItemIndex][seria_id]['data'].items())

        return result

    def _parserByMinute(self, line, offset = 1):
        return (offset + 5, datetime(int(line[offset + 0]), int(line[offset + 1]), int(line[offset + 2]), hour = int(line[offset + 3]),
                                     minute = int(line[offset + 4])).strftime("%s000"))

    def _parserByHour(self, line, offset = 1):
        return (offset + 4, datetime(int(line[offset + 0]), int(line[offset + 1]), int(line[offset + 2]), hour = int(line[offset + 3])).strftime("%s000"))

    def _parserByDay(self, item, offset = 1):
        return (offset + 3,  datetime(int(item[offset + 0]), int(item[offset + 1]), int(item[offset + 2])).strftime("%s000"))

    def _parserByWeek(self, item, offset = 1):
        return (offset + 2, datetime.fromtimestamp(time.mktime(time.strptime('{} {} 1'.format(item[offset + 0], item[offset + 1]), '%Y %W %w'))).strftime("%s000"))