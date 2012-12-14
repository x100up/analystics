# -*- coding: utf-8 -*-
monthNamesShort = [u'янв', u'фев', u'март', u'апр', u'май', u'июнь', u'июль', u'авг', u'сен', u'окт', u'ноя', u'дек']
monthNamesB = [u'января', u'февраля', u'марта', u'апреля', u'мая', u'июня', u'июля', u'августа', u'сентября', u'октября', u'ноября', u'декабря']

def repMonth(value, decode = True):
    if decode:
        value = value.decode('utf-8')
    for i, m in enumerate(monthNamesShort):
        value = value.replace(m, str(i + 1))
    return value

def dayCountName(count):
    count = int(str(count)[-1:])
    if count == 1:
        return u'день'
    elif count < 5:
        return u'дня'
    else:
        return u'дней'

def hourCountName(count):
    count = int(str(count)[-1:])
    if count == 1:
        return u'час'
    elif count < 5:
        return u'часа'
    else:
        return u'часов'

def minuteCountName(count):
    count = int(str(count)[-1:])
    if count == 1:
        return u'минута'
    elif count < 5:
        return u'минуты'
    else:
        return u'минут'

def secondCountName(count):
    return u'сек'
    '''
    count = int(str(count)[-1:])
    if count == 1:
        return u'секунда'
    elif count < 5:
        return u'секунды'
    else:
        return u'секунд'
            '''


def smartPeriod(date1, date2):
    _date1 = date1.date()
    _date2 = date2.date()
    _time1 = date1.time()
    _time2 = date2.time()
    _from = ''
    _to = ''
    date_template = u'c {} по {}'
    atOneDay = _date1.year == _date2.year and _date1.month == _date2.month and _date1.day == _date2.day

    if atOneDay:
        if _time1.hour ==  _time2.hour and _time1.minute == _time2.minute:
            _time_to = u' в %02d:%02d' % (_time1.hour, _time1.minute)
        else:
            _time_to = u' с %02d:%02d до %02d:%02d' % (_time1.hour, _time1.minute, _time2.hour, _time2.minute)
        _time_from = ''
    else:
        _time_from = ' %02d:%02d'% (_time1.hour, _time1.minute)
        _time_to = ' %02d:%02d' % (_time2.hour, _time2.minute)

    if (_date1.year != _date2.year):
        _from += str(_date1.day) + ' ' + _time_from + ' ' + monthNamesB[_date1.month - 1] + ' ' +  str(_date1.day)
        _to += str(_date2.day) + ' ' + _time_to + ' ' + monthNamesB[_date2.month - 1] + ' ' +  str(_date2.day)
    elif (_date1.month != _date2.month):
        _from += str(_date1.day) + ' ' + _time_from + ' ' + monthNamesB[_date1.month - 1]
        _to += str(_date2.day) + ' ' + _time_to + ' ' + monthNamesB[_date2.month - 1] + ' ' +  str(_date2.year) + u' года'
    elif (_date1.day != _date2.day):
        _from += str(_date1.day)
        _to += str(_date2.day) + ' ' + _time_to + ' ' + _time_from + ' ' + monthNamesB[_date2.month - 1] + ' ' +  str(_date2.year) + u' года'
    else:
        date_template = u'{}{}'
        _to += str(_date2.day) + ' ' + _time_to + ' ' + monthNamesB[_date2.month - 1] + ' ' +  str(_date2.year) + u' года'

    return date_template.format(_from, _to)