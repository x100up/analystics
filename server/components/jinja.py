# -*- coding: utf-8 -*-
from components.dateutil import monthNamesShort, monthNamesB, dayCountName, hourCountName, minuteCountName, secondCountName

def datetofiled(value):
    return unicode(value.strftime('%d {0} %Y %H:%M')).format(monthNamesShort[value.date().month])

def smartDatePeriod(date1, date2):
    if date2:
        '''
        Умный интервал
        '''
        _date1 = date1.date()
        _date2 = date2.date()
        _time1 = date1.time()
        _time2 = date2.time()
        _from = ''
        _to = ''
        date_template = u'С {} по {}'
        atOneDay = False
        if (_date1.year != _date2.year):
            _from += str(_date1.day) + ' ' + monthNamesB[_date1.month] + ' ' +  str(_date1.day)
            _to += str(_date2.day) + ' ' + monthNamesB[_date2.month] + ' ' +  str(_date2.day)
        elif (_date1.month != _date2.month):
            _from += str(_date1.day) + ' ' + monthNamesB[_date1.month]
            _to += str(_date2.day) + ' ' + monthNamesB[_date2.month] + ' ' +  str(_date2.year) + u' года'
        elif (_date1.day != _date2.day):
            _from += str(_date1.day)
            _to += str(_date2.day) + ' ' + monthNamesB[_date2.month] + ' ' +  str(_date2.year) + u' года'
        else:
            date_template = u'{}{}'
            _to += str(_date2.day) + ' ' + monthNamesB[_date2.month] + ' ' +  str(_date2.year) + u' года'
            atOneDay = True

        if atOneDay:
            if _time1.hour ==  _time2.hour and _time1.minute == _time2.minute:
                _to += u' в {}:{}'.format(_time1.hour, _time1.minute)
            else:
                _to += u' с {}:{} до {}:{}'.format(_time1.hour, _time1.minute, _time2.hour, _time2.minute)
        else:
            _from += ' {}:{}'.format(_time1.hour, _time1.minute)
            _to += ' {}:{}'.format(_time2.hour, _time2.minute)

        return date_template.format(_from, _to)
    else:
        return date1


def smartDateInterval(date1, date2):
    result = u''
    if date2:
        delta = date2 - date1
        if delta.days != 0:
            result += delta.days + ' ' + dayCountName(delta.days) + ' '

        hourse_delta = delta.seconds / 3600
        if hourse_delta != 0:
            result += str(hourse_delta) + ' ' + hourCountName(hourse_delta) + ' '

        minutes_delta = delta.seconds / 60
        if minutes_delta != 0:
            result += str(minutes_delta) + ' ' + minuteCountName(minutes_delta)

        if delta.seconds < 61 and delta.seconds > 0:
            result += str(delta.seconds) + ' ' + secondCountName(delta.seconds)

    return result
