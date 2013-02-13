# -*- coding: utf-8 -*-
from models.Task import Task
from datetime import datetime
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

    def getHiveQuery(self, workerId):
        """
            Генерирует запрос для Hive основываясь на зачаче Task
        """

        queries = []
        isMulty = len(self.task.items) > 1

        # узнаем количество полей в выдаче для того, чтоыб дополнить запросы до одинакового количества
        # self.fieldCount = self.task.getFieldsCount()
        # какие поля должны быть в запросе, для синхронизации UNION
        self.fieldsName = self.task.getFieldsNames()
        fieldsTemplates = []
        for default, name in self.fieldsName:
            field = '%({0})s as {0}'.format(name)
            if field not in fieldsTemplates:
                fieldsTemplates.append(field)

        fieldsTemplate = ','.join(fieldsTemplates)
        if fieldsTemplate:
            fieldsTemplate = ', ' + fieldsTemplate

        for index, taskItem in self.task.items.items():
            fields = taskItem._getFields(not taskItem.userUnique)
            for default, fieldsName in self.fieldsName:
                if not fieldsName in fields:
                    fields[fieldsName] =default

            # создаем интервалы - нужны для партицирования
            query = 'SELECT '
            if not isMulty:
                query += '\'' + str(workerId) + '\' as `wid`,'

            dateFields = self.getDateFields(self.task.interval, taskItem.userUnique)

            query += self.toSQLFields(dateFields) + ', ' + self.toSQLFields(taskItem.fields) + fieldsTemplate%fields\
                     + ' FROM {}'.format(self.getSelectSource(taskItem))

            if not taskItem.userUnique:
                # временная составляющая
                intervals = self.getIntervalCondition(taskItem.start, taskItem.end)
                query += ' WHERE (' + ' OR '.join(intervals) + ')'
                # условия по тегам
                query += self.getTagsCondition(taskItem.conditions)
            else:
                # при уникальном юзере все селектим из подзапроса
                pass

            # группировка
            query += ' GROUP BY ' + self.getGroupInterval(self.task.interval, taskItem.userUnique) + self.getTaskTagsByOperation(taskItem, 'group', not taskItem.userUnique)
            queries.append(query)

        if not isMulty:
            return queries.pop().encode('utf-8')

        query = 'SELECT \'' + str(workerId) + '\' as `wid`, * FROM (' + ' UNION ALL ' .join(queries) +') FINAL'
        return query.encode('utf-8')

    def getSelectSource(self, taskItem):
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

            subquery += ' FROM {}.stat_{}'.format(self.task.appname, taskItem.key)
            intervals = self.getIntervalCondition(taskItem.start, taskItem.end)
            subquery += ' WHERE (' + ' OR '.join(intervals) + ')'
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
        dt1 = repMonth(val, decode = False)
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

    def getDateFields(self, interval, isSubquery = False):
        """
            Генерирует список полей дат, нужных для интервала
        """
        fields = [('year(`dt`)', 'year')]

        if  interval != Task.INTERVAL_WEEK:
            fields.append(('month(`dt`)', 'month'))
            fields.append(('day(`dt`)', 'day'))

        if  interval == Task.INTERVAL_MINUTE:
            # noinspection PyRedundantParentheses
            fields.append(('hour'))
            # noinspection PyRedundantParentheses
            fields.append(('minute'))

        elif  interval == Task.INTERVAL_10_MINUTE:
            # noinspection PyRedundantParentheses
            fields.append(('hour'))
            if isSubquery:
                # noinspection PyRedundantParentheses
                fields.append(('minute_10'))
            else:
                fields.append(('floor(`minute` / 10) * 10', 'minute_10'))

        elif  interval == Task.INTERVAL_HOUR:
            # noinspection PyRedundantParentheses
            fields.append(('hour'))

        elif  interval == Task.INTERVAL_DAY:
            pass

        elif  interval == Task.INTERVAL_WEEK:
            if isSubquery:
                # noinspection PyRedundantParentheses
                fields.append(('weekofyear'))
            else:
                fields.append(('weekofyear(`timestamp`)', 'weekofyear'))

        #fields.reverse()
        return fields

    def getIntervalCondition(self, start, end):
        intervals = []
        if start.date() == end.date():
            intervals.append('dt = \'%(y)d-%(m)02d-%(d)02d\'' % {'y': start.year, 'm': start.month, 'd': start.day})
        else:
            intervals.append('dt >= \'%(y)d-%(m)02d-%(d)02d\'' % {'y': start.year, 'm': start.month, 'd': start.day} \
                + ' AND dt <= \'%(y)d-%(m)02d-%(d)02d\'' % {'y': end.year, 'm': end.month, 'd': end.day})
        return intervals


    def getIntervalCondition_old(self, start, end):
        """
        генерирует временные интервалы выборки
        """
        intervals = []
        start_year = start.date().year
        end_year = end.date().year
        start_month = start.date().month
        end_month = end.date().month
        start_day = start.date().day
        end_day = end.date().day

        if start_year == end_year:
            prefix = '(year = %(year)i'%{'year':start_year}
            if start_month == end_month:
                prefix += ' AND month = %(month)i'%{'month':start_month}
                if (start_day == end_day) or (end_day - start_day == 1 and end.hour == 0 and end.minute == 0):
                    intervals.append(prefix + ' AND day = %(start_day)i)'%{'start_day':start_day})
                else:
                    intervals.append(prefix + ' AND day >= %(start_day)i AND day <= %(end_day)i)'%{'start_day':start_day, 'end_day':end_day})
            else:
                for mi in range(start_month, end_month + 1):
                    prefix2 = prefix + ' AND month = %(month)i'%{'month':mi}
                    if mi == start_month:
                        intervals.append(prefix2 + ' AND day >= %(day)i)'%{'day':start_day})
                    elif mi == end_month:
                        intervals.append(prefix2 + ' AND day <= %(day)i)'%{'day':end_day})
                    else:
                        intervals.append(prefix2 + ')')
        else:
            # разные годы
            for yi in range(start_year, end_year + 1):
                prefix = '(year = %(year)i'%{'year':yi}
                if yi == start_year:

                    for mi in range(start_month, 12 + 1):
                        prefix2 = prefix + ' AND month = %(month)i'%{'month':mi}
                        if mi == start_month:
                            intervals.append(prefix2 + ' AND day >= %(day)i)'%{'day':start_day})
                        else:
                            intervals.append(prefix2 + ')')

                elif yi == end_year:

                    for mi in range(1, end_month + 1):
                        prefix2 = prefix + ' AND month = %(month)i'%{'month':mi}
                        if mi == end_month:
                            intervals.append(prefix2 + ' AND day <= %(day)i)'%{'day':end_day})
                        else:
                            intervals.append(prefix2 + ')')

                else:
                    # весь год
                    intervals.append(prefix)
        return intervals

    def getGroupInterval(self, group_interval, isSubquery = False):
        """
        Генерит группировку основываясь на интервале
        """
        if group_interval == Task.INTERVAL_MINUTE:
            if isSubquery:
                return ' year, month, day, hour, minute '
            else:
                return ' year(`dt`), month(`dt`), day(`dt`), hour, minute '

        if group_interval == Task.INTERVAL_10_MINUTE:
            if isSubquery:
                return ' year, month, day, hour, minute_10 '
            else:
                return ' year(`dt`), month(`dt`), day(`dt`), hour, floor(`minute` / 10) * 10 '

        if group_interval ==  Task.INTERVAL_HOUR:
            if isSubquery:
                return ' year, month, day, hour'
            else:
                return ' year(`dt`), month(`dt`), day(`dt`), hour'

        if group_interval == Task.INTERVAL_DAY:
            if isSubquery:
                return ' year, month, day'
            else:
                return ' year(`dt`), month(`dt`), day(`dt`)'

        if group_interval == Task.INTERVAL_WEEK:
            if isSubquery:
                return ' year, weekofyear'
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