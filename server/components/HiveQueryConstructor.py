# -*- coding: utf-8 -*-
from models.Task import Task
from datetime import datetime, timedelta
from components.dateutil import repMonth
import time, re, calendar

class HiveQueryConstructor():

    def __init__(self, task, appConfig):
        self.task = task
        self.appConfig = appConfig

    def getFields(self):
        """
            Возвращает лист названий полей, которые должен вернуть запрос.
        """
        fields = ['wid']
        fields.extend(self.getDateFields(self.task.interval))
        fields.extend(['value'])
        return fields

    def getHiveQuerys(self, workerId):
        queris = []
        now = datetime.now().date()
        for taskItem in self.task.items.values():
            if taskItem.start.date() != now and (taskItem.end.date() == now and taskItem.end.hour + taskItem.end.minute > 0 ):
                # если мы хотим получить данные за сегодня и не только - нужно дернуть 2 запроса task 12835
                separator = datetime(taskItem.end.year, taskItem.end.month, taskItem.end.day, 0, 0, 0)
                queris.append(self.constructHiveQuery(workerId, taskItem, forceEnd=separator))
                queris.append(self.constructHiveQuery(workerId, taskItem, forceStart=separator))
            else:
                queris.append(self.constructHiveQuery(workerId, taskItem))

        for q in queris:
            print '--> ', q
        return queris

    def constructHiveQuery(self, workerId, taskItem, forceStart=False, forceEnd=False):
        """
            Генерирует запрос для Hive основываясь на зачаче Task
        """

        # for expName in taskItem.getFieldsNames():
        #     field = '%({0})s as {0}'.format(expName)
        #     fieldsTemplates.append(field)
        #     #if field not in fieldsTemplates:
        #
        #
        # fieldsTemplate = ','.join(fieldsTemplates)
        # if fieldsTemplate:
        #     fieldsTemplate = ', ' + fieldsTemplate

        expressions = taskItem._getFields(not taskItem.userUnique)
        expNames = taskItem.getFieldsNames()
        fields = []
        for index, expression in expressions.iteritems():
            fields.append('{} as {}'.format(expression, index))

        # создаем интервалы - нужны для партицирования
        query = 'SELECT \'' + str(workerId) + '\' as `wid`,'

        dateFields = self.getDateFields(self.task.interval, taskItem.userUnique)
        comma = ','
        if not fields:
            comma = ''
        query += self.toSQLFields(dateFields) + ', ' + self.toSQLFields(taskItem.fields) + comma + ', '.join(fields) \
                 + ' FROM {}'.format(self.getSelectSource(taskItem, forceStart or taskItem.start, forceEnd or taskItem.end))

        if not taskItem.userUnique:
            # временная составляющая
            query += ' WHERE ' + self.getIntervalCondition(forceStart or taskItem.start, forceEnd or taskItem.end)
            # условия по тегам
            query += self.getTagsCondition(taskItem.conditions)
        else:
            # при уникальном юзере все селектим из подзапроса
            pass

        # группировка
        query += ' GROUP BY ' + self.getGroupInterval(self.task.interval, taskItem.userUnique) + \
                 self.getTaskTagsByOperation(taskItem, 'group', not taskItem.userUnique)
        return query


    def getSelectSource(self, taskItem, start, end):
        """
        Из чего выбираем - из таблицы или из выражения
        """
        if taskItem.userUnique:
            subquery = 'SELECT {}, userId '.format(self.toSQLFields(self.getDateFields(self.task.interval)))

            taskFields = taskItem.getFields(topQuery = True, isSubquery = True)
            # дополняем поля до нужного количества иначе будет FAILED: Error in semantic analysis: Schema of both sides of union should match.
            # taskFields += ['0.0'] * (self.fieldCount - len(taskFields) - len(taskItem.fields))
            if taskFields:
                subquery += ', ' + self.toSQLFields(taskFields)

            subquery += ' FROM {}.stat_{}'.format('stat_' + self.task.appname, taskItem.key)
            interval = self.getIntervalCondition(start, end)
            subquery += ' WHERE ' + interval
            subquery += self.getTagsCondition(taskItem.conditions)
            subquery += ' GROUP BY userId, ' + self.getGroupInterval(self.task.interval) + self.getTaskTagsByOperation(taskItem, 'group')
            return '(' + subquery + ') `sq_{}`'.format(taskItem.index)
        else:
            return '{}.stat_{} '.format('stat_' + self.task.appname, taskItem.key)

    def getStageCount(self):
        count = len(self.task.items)
        if count > 1:
            return count + 1
        else:
            return 1

    def getTagsCondition(self, conditions):
        """
        Условия по тегам
        """
        if conditions:
            where = []
            for eventCode, tagCode, tagValue in conditions:
                print 'Get tag for {}:{}'.format(eventCode, tagCode)
                tagType = self.appConfig.getTag(eventCode, tagCode).type
                if tagValue:
                    if tagType == 'int':
                        where.append(self.parseIntValue(tagCode, tagValue[0]))
                    elif tagType == 'timestamp':
                        start, end = self.getTSValues(tagValue[0])
                        print start, end

                        start2, end2 = (False, False)
                        if len(tagValue) > 1:
                            start2, end2 = self.getTSValues(tagValue[1])
                            if start2:
                                if end2:
                                    end = end2
                                else:
                                    end = start2

                        if end:
                            startTs = int(time.mktime(start.timetuple()))
                            endTs = int(time.mktime(end.timetuple()))
                            where.append("(params['%(tagName)s'] >= %(tagValue1)s AND params['%(tagName)s'] <= %(tagValue2)s)"%{'tagName':tagCode, 'tagValue1':startTs, 'tagValue2':endTs})
                        else:
                            ts = int(time.mktime(start.timetuple()))
                            where.append("params['%(tagName)s'] = %(tagValue)s"%{'tagName':tagCode, 'tagValue':ts})
                    else:
                        if len(tagValue) == 1:
                            where.append("params['%(tagName)s'] = '%(tagValue)s'"%{'tagName':tagCode, 'tagValue':tagValue[0]})
                        else:
                            items = []
                            for val in tagValue:
                                items.append("params['%(tagName)s'] = '%(tagValue)s'"%{'tagName':tagCode, 'tagValue':val})

                            where.append('(' + ' OR '.join(items) + ')')
            if len(where):
                return ' AND ' + ' AND '.join(where)

        return ''

    def getTSValues(self, val):
        start = False
        end = False
        dt1 = repMonth(val, decode=False)
        components1 = dt1.split(' ')

        if len(components1) == 2:
            year = int(components1[1])
            month = int(components1[0])
        else:
            year = int(components1[2])
            month = int(components1[1])

        if len(components1) >= 3:
            startDay = endDay = int(components1[0])
        else:
            startDay = 1
            endDay = calendar.monthrange(year, month)[1]

        if len(components1) < 4:
            start = datetime(year, month, startDay, 0, 0, 0)
            end = datetime(year, month, endDay, 23, 59, 59)
        elif len(components1) == 4:
            _time = components1[3]
            _time = _time.split(':')
            hour = int(_time[0])
            minutes = 0
            hasMinutes = len(_time) > 1
            if hasMinutes:
                minutes = int(_time[1])

            start = datetime(year, month, startDay, hour, minute = minutes, second=0)
            if not hasMinutes:
                end = datetime(year, month, endDay, hour, minute = minutes, second=59)

        return start, end

    def parseIntValue(self, tagName, tagValue):
        """
        Преобразует интовые параметры в запрос
        """
        values = tagValue.replace('- ', '-').replace(' -', '-').replace(' ', ',').replace('.', ',').split(',')
        exp = []
        for value in values:
            if '-' in value:
                value = [int(v) for v in value.split('-')]
                exp.append("(params['{0}'] >= {1} AND params['{0}'] <= {2})".format(tagName, min(value), max(value)))
            else:
                exp.append("params['{}'] = {}".format(tagName, value))

        return '(' + ' OR '.join(exp) + ')'

    def getDateFields(self, interval, isSubquery=False):
        """
            Генерирует список полей дат, нужных для интервала
        """
        if isSubquery:
            fields = [('`year`')]
        else:
            fields = [('year(`dt`)', 'year')]

        if interval != Task.INTERVAL_WEEK:
            if isSubquery:
                fields.append(('`month`'))
                fields.append(('`day`'))
            else:
                fields.append(('month(`dt`)', 'month'))
                fields.append(('day(`dt`)', 'day'))

        if interval == Task.INTERVAL_MINUTE:
            # noinspection PyRedundantParentheses
            fields.append(('hour'))
            # noinspection PyRedundantParentheses
            fields.append(('minute'))

        elif interval == Task.INTERVAL_10_MINUTE:
            # noinspection PyRedundantParentheses
            fields.append(('hour'))
            if isSubquery:
                # noinspection PyRedundantParentheses
                fields.append(('`minute_10`'))
            else:
                fields.append(('floor(`minute` / 10) * 10', 'minute_10'))

        elif interval == Task.INTERVAL_HOUR:
            # noinspection PyRedundantParentheses
            fields.append(('hour'))

        elif  interval == Task.INTERVAL_DAY:
            pass

        elif  interval == Task.INTERVAL_WEEK:
            if isSubquery:
                # noinspection PyRedundantParentheses
                fields.append(('`weekofyear`'))
            else:
                fields.append(('weekofyear(`timestamp`)', 'weekofyear'))

        return fields

    def getIntervalCondition(self, start, end):
        """
        Возвращает интервал выборки данных
        """
        if start.date() == end.date() or ((end.hour + end.minute == 0) and end - start <= timedelta(days=1)):
            interval = 'dt = \'%(y)d-%(m)02d-%(d)02d\'' % {'y': start.year, 'm': start.month, 'd': start.day}
        else:
            interval = 'dt >= \'%(y)d-%(m)02d-%(d)02d\'' % {'y': start.year, 'm': start.month, 'd': start.day}
            if end.hour + end.minute == 0:
                interval += ' AND dt < \'%(y)d-%(m)02d-%(d)02d\'' % {'y': end.year, 'm': end.month, 'd': end.day}
            else:
                interval += ' AND dt <= \'%(y)d-%(m)02d-%(d)02d\'' % {'y': end.year, 'm': end.month, 'd': end.day}
        return interval



    def getGroupInterval(self, group_interval, isSubquery=False):
        """
        Генерит группировку основываясь на интервале
        isSubquery = True - мы гуппируем по данным из подзапроси и нам не нужны выражения
        """
        if group_interval == Task.INTERVAL_MINUTE:
            if isSubquery:
                return ' `year`, `month`, `day`, hour, minute '
            else:
                return ' year(`dt`), month(`dt`), day(`dt`), hour, minute '

        if group_interval == Task.INTERVAL_10_MINUTE:
            if isSubquery:
                return ' `year`, `month`, `day`, hour, `minute_10` '
            else:
                return ' year(`dt`), month(`dt`), day(`dt`), hour, floor(`minute` / 10) * 10 '

        if group_interval == Task.INTERVAL_HOUR:
            if isSubquery:
                return ' `year`, `month`, `day`, hour'
            else:
                return ' year(`dt`), month(`dt`), day(`dt`), hour'

        if group_interval == Task.INTERVAL_DAY:
            if isSubquery:
                return ' `year`, `month`, `day`'
            else:
                return ' year(`dt`), month(`dt`), day(`dt`)'

        if group_interval == Task.INTERVAL_WEEK:
            if isSubquery:
                return ' `year`, `weekofyear`'
            else:
                return ' year(`dt`), weekofyear(`timestamp`)'

        raise Exception("Unknow interval")

    def getTaskTagsByOperation(self, taskItem, operation, isTopQuery = True):
        g = set()
        for tagName, operations in taskItem.operations.items():
            if operation in operations:
                if isTopQuery:
                    g.add('params[\'{0}\']'.format(tagName))
                else:
                    g.add('`group_{0}`'.format(tagName))

        if len(g):
            return ', ' + ', '.join(g)
        return ''

    def toSQLFields(self, fields):
        """
        Список полей => SQL string
        """
        sql = []
        for field in fields:
            if isinstance(field, tuple):
                fieldExp, fieldName = field
                sql.append('%(fieldExp)s AS `%(fieldName)s`'%{'fieldExp':fieldExp, 'fieldName':fieldName})
            else:
                sql.append('%(fieldExp)s'%{'fieldExp':field})
        return ', '.join(sql)