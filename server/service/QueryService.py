# -*- coding: utf-8 -*-
from models.Task import Task

class HiveQueryConstructor():

    def __init__(self, task):
        self.task = task

    def getFields(self):
        '''
            Возвращает лист названий полей, которые должен вернуть запрос.
            Пока аозвращает value + dateFields
        '''
        x = ['value']
        x.extend(self.getDateFields(self.task.interval))
        return x

    def getHiveQuery(self):
        '''
            Генерирует запрос для Hive основываясь на зачаче Task
        '''
        dateFields = self.getDateFields(self.task.interval)
        queries = []
        for taskItem in self.task.items:
            # создаем интервалы - нужны для партицирования
            query = 'SELECT ' + self.toSQLFields(taskItem.getFields()) + ', ' + self.toSQLFields(dateFields)\
                    + ' FROM %(appname)s.stat_%(keyname)s '%{'appname': self.task.appname, 'keyname': taskItem.key}

            # временная составляющая
            intervals = self.getIntervalCondition(taskItem.start, taskItem.end)
            query += ' WHERE ' + ' AND '.join(intervals)

            # условия по тегам
            query += self.getTagsCondition(taskItem.conditions)

            # группировка
            query += ' GROUP BY ' + self.getGroupInterval(self.task.interval)
            queries.append(query)

        if len(queries) == 1:
            return queries.pop()
        return ' UNION ' .join(queries)

    def getTagsCondition(self, conditions):
        '''
        Условия по тегам
        '''
        if conditions:
            where = []
            for key in conditions:
                    for tagName, tagValue in conditions.items():
                        if tagValue:
                            where.append("params['%(tagName)s'] = '%(tagValue)s'"%{'tagName':tagName, 'tagValue':tagValue})
            return ' AND ' + ' AND '.join(where)

        return ''

    def getDateFields(self, interval):
        '''
            Генерирует список полей дат, нужных для интервала
        '''
        fields = {}
        fields['year'] = 'year'
        fields['month'] = 'month'
        fields['day'] = 'day'

        if  interval == Task.INTERVAL_MINUTE:
            fields['hour'] = 'hour'
            fields['minute'] = 'minute'

        elif  interval == Task.INTERVAL_10_MINUTE:
            fields['hour'] = 'hour'
            fields['minute'] = 'minute'

        elif  interval == Task.INTERVAL_HOUR:
            fields['hour'] = 'hour'

        elif  interval == Task.INTERVAL_DAY:
            pass

        elif  interval == Task.INTERVAL_WEEK:
            pass

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
                prefix = '(year = %(year)i'%{'year':start_year}
                if yi == start_year:

                    for mi in range(start_month, 13):
                        prefix2 = prefix + ' AND month = %(month)i'%{'month':mi}
                        if mi == start_month:
                            intervals.append(prefix2 + ' AND day >= %(day)i)'%{'day':start_day})
                        else:
                            intervals.append(prefix2 + ')')

                elif yi == end_year:

                    for mi in range(1, end_month+1):
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
            return ' year, month, day, hour, ceil(minute / 10) '

        if group_interval ==  Task.INTERVAL_HOUR:
            return ' year, month, day, hour'

        if group_interval == Task.INTERVAL_DAY:
            return ' year, month, day'

        if group_interval == Task.INTERVAL_WEEK:
            return ' year, month, day'

        raise Exception("Unknow interval")

    def toSQLFields(self, fields):
        '''
        Список полей => SQL string
        '''
        sql = []
        for fieldName, fieldExp in fields.items():
            sql.append('%(fieldExp)s AS `%(fieldName)s`'%{'fieldExp':fieldExp, 'fieldName':fieldName})
        return ', '.join(sql)