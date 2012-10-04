# -*- coding: utf-8 -*-
from models.Task import Task

class HiveQueryConstructor():

    def __init__(self, task):
        self.task = task

    def getFields(self):
        '''
            Возвращает лист названий полей, которые должен вернуть запрос.
        '''
        fields = ['wid']
        fields.extend(self.getDateFields(self.task.interval))
        fields.extend(['value'])
        return fields

    def getHiveQuery(self, workerId):
        '''
            Генерирует запрос для Hive основываясь на зачаче Task
        '''
        dateFields = self.getDateFields(self.task.interval)
        queries = []
        isMulty = len(self.task.items) > 1

        # узнаем количество полей в выдаче для того, чтоыб дополнить запросы до одинакового количества
        fieldCount = self.task.getFieldsCount()
        print fieldCount
        for index, taskItem in self.task.items.items():
            # создаем интервалы - нужны для партицирования
            query = 'SELECT '
            if not isMulty:
                query += '\'' + str(workerId) + '\' as `wid`,'

            # дополняем поля до нужного количества иначе будет FAILED: Error in semantic analysis: Schema of both sides of union should match.
            taskFields = taskItem.getFields()
            taskFields += ['""']*(fieldCount - len(taskFields))
            print taskFields

            query += self.toSQLFields(dateFields) + ', ' + self.toSQLFields(taskFields)\
                     + ' FROM %(appname)s.stat_%(keyname)s '%{'appname': self.task.appname, 'keyname': taskItem.key}

            # временная составляющая
            intervals = self.getIntervalCondition(taskItem.start, taskItem.end)
            query += ' WHERE (' + ' OR '.join(intervals) + ')'

            # условия по тегам
            query += self.getTagsCondition(taskItem.conditions)

            # группировка
            query += ' GROUP BY ' + self.getGroupInterval(self.task.interval) + self.getTaskTagsByOperation(taskItem, 'group')
            queries.append(query)

        if not isMulty:
            return queries.pop().encode('utf-8')

        query = 'SELECT \'' + str(workerId) + '\' as `wid`, * FROM (' + ' UNION ALL ' .join(queries) +') FINAL'
        return query.encode('utf-8')

    def getStageCount(self):
        count = len(self.task.items)
        if count > 1:
            return count + 1
        else:
            return 1

    def getTagsCondition(self, conditions):
        '''
        Условия по тегам
        '''
        if conditions:
            where = []
            for tagName, tagValue in conditions.items():
                if tagValue:
                    # TODO by settings int
                    if tagName == 'age':
                        where.append(self.parseIntValue(tagName, tagValue[0]))
                    else:
                        if len(tagValue) == 1:
                            where.append("params['%(tagName)s'] = '%(tagValue)s'"%{'tagName':tagName, 'tagValue':tagValue[0]})
                        else:
                            items = []
                            for val in tagValue:
                                items.append("params['%(tagName)s'] = '%(tagValue)s'"%{'tagName':tagName, 'tagValue':val})

                            where.append('(' + ' OR '.join(items) + ')')
            if len(where):
                return ' AND ' + ' AND '.join(where)

        return ''

    def parseIntValue(self, tagName, tagValue):
        '''
        Преобразует интовые параметры в запрос
        '''
        values = tagValue.replace('- ', '-').replace(' -', '-').replace(' ', ',').replace('.', ',').split(',')
        exp = []
        for value in values:
            if '-' in value:
                value = [int(v) for v in value.split('-')]
                exp.append("(params['{0}'] >= {1} AND params['{0}'] <= {2})".format(tagName, min(value), max(value)))
            else:
                exp.append("params['{}'] = {}".format(tagName, value))

        return '(' + ' OR '.join(exp) + ')'

    def getDateFields(self, interval):
        '''
            Генерирует список полей дат, нужных для интервала
        '''
        fields = []
        fields.append(('year'))

        if  interval != Task.INTERVAL_WEEK:
            fields.append(('month'))
            fields.append(('day'))

        if  interval == Task.INTERVAL_MINUTE:
            fields.append(('hour'))
            fields.append(('minute'))

        elif  interval == Task.INTERVAL_10_MINUTE:
            fields.append(('hour'))
            fields.append(('floor(`minute` / 10) * 10', 'minute_10'))

        elif  interval == Task.INTERVAL_HOUR:
            fields.append(('hour'))

        elif  interval == Task.INTERVAL_DAY:
            pass

        elif  interval == Task.INTERVAL_WEEK:
            fields.append(('weekofyear(`timestamp`)', 'weekofyear'))
            pass

        #fields.reverse()
        return fields

    def getIntervalCondition(self, start, end):
        '''
        генерирует временные интервалы выборки
        '''
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
                if start_day == end_day:
                    intervals.append(prefix + ' AND day = %(start_day)i)'%{'start_day':start_day})
                else:
                    intervals.append(prefix + ' AND day >= %(start_day)i AND day < %(end_day)i)'%{'start_day':start_day, 'end_day':end_day})
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
                prefix = '(year = %(year)i'%{'year':start_year}
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

    def getGroupInterval(self, group_interval):
        '''
        Генерит группировку основываясь на интервале
        '''
        if group_interval == Task.INTERVAL_MINUTE:
            return ' year, month, day, hour, minute '

        if group_interval == Task.INTERVAL_10_MINUTE:
            return ' year, month, day, hour, floor(`minute` / 10) * 10 '

        if group_interval ==  Task.INTERVAL_HOUR:
            return ' year, month, day, hour'

        if group_interval == Task.INTERVAL_DAY:
            return ' year, month, day'

        if group_interval == Task.INTERVAL_WEEK:
            return ' year, weekofyear(`timestamp`)'

        raise Exception("Unknow interval")

    def getTaskTagsByOperation(self, taskItem, operation):
        g = set()
        for tagName, operations in taskItem.operations.items():
            if operation in operations:
                g.add('params[\'{0}\']'.format(tagName))

        if len(g):
            return ', ' + ', '.join(g)
        return ''

    def toSQLFields(self, fields):
        '''
        Список полей => SQL string
        '''
        sql = []
        for field in fields:
            if isinstance(field, tuple):
                fieldExp, fieldName = field
                sql.append('%(fieldExp)s AS `%(fieldName)s`'%{'fieldExp':fieldExp, 'fieldName':fieldName})
            else:
                sql.append('%(fieldExp)s'%{'fieldExp':field})
        return ', '.join(sql)