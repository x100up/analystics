# -*- coding: utf-8 -*-

class HiveQueryConstructor():

    def __init__(self, task):
        self.task = task

    def getFields(self):
        '''
        Возвращает лист названий полей, которые должен вернуть запрос
        '''
        return self.task.fields.keys()

    def getHiveQuery(self):
        # создаем интервалы - нужны для партицирования
        intervals = self.getIntervalCondition(self.task.start, self.task.end)
        self.task.prepare()
        queries = {}
        for key in self.task.conditions:
            queries[key] = 'SELECT ' + self.task.getFields(key) + ' FROM %(appname)s.stat_%(keyname)s '%{'appname':self.task.appname, 'keyname':key}

        for key, query in queries.items():
            # временная составляющая
            queries[key] += ' WHERE ' + ' AND '.join(intervals)

            # условия по тегам
            queries[key] += self.getTagsCondition(self.task.conditions)

            # группировка
            queries[key] += ' GROUP BY ' + self.getGroupInterval(self.task.interval)

            return queries[key]

    def getTagsCondition(self, conditions):
        if conditions:
            where = []
            for key in conditions:
                    for tagName, tagValue in conditions[key].items():
                        if tagValue:
                            where.append("params['%(tagName)s'] = '%(tagValue)s'"%{'tagName':tagName, 'tagValue':tagValue})
            return ' AND ' + ' AND '.join(where)

        return ''

    def getIntervalCondition(self, start, end):
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

        print group_interval

        if group_interval == 'minute':
            return ' year, month, day, hour, minute '

        if group_interval == '10minute':
            return ' year, month, day, hour, ceil(minute / 10) '

        if group_interval == 'hour':
            return ' year, month, day, hour'

        if group_interval == 'day':
            return ' year, month, day'

        if group_interval == 'week':
            return ' year, month, day'

        raise Exception("Unknow interval")