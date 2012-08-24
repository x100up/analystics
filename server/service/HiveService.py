# -*- coding: utf-8 -*-
def createHiveQuery(appname, start, end, group_interval = False):
    # создаем интервалы - нужны для партицирования
    intervals = createIntervals(start, end)

    query = 'SELECT count(1) FROM %(appname)s.stat_%(keyname)s '

    # временная составляющая
    query += ' WHERE ' + ' AND '.join(intervals)

    # условия по тегам

    # группировка
    if group_interval:
        query += ' GROUP BY ' + getGroupInterval(group_interval)

    return query

def createIntervals(start, end):
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

def getGroupInterval(group_interval):
    if group_interval == 'minute':
        return ' year, month, day, hour, minute '

    if group_interval == '10minute':
        return ' year, month, day, hour, ceil(minute / 10) '

    if group_interval == 'hour':
        return ' year, month, day, hour'

    if group_interval == 'day':
        return ' year, month, day'

    if group_interval == 'week':
        pass