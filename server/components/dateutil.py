# -*- coding: utf-8 -*-
monthNamesShort = [u'янв', u'фев', u'март', u'апр', u'май', u'июнь', u'июль', u'авг', u'сен', u'окт', u'ноя', u'дек']
monthNamesB = [u'янвря', u'февраля', u'марта', u'апреля', u'мая', u'июня', u'июля', u'августа', u'сентября', u'октября', u'ноября', u'декабря']

def repMonth(value):
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
    count = int(str(count)[-1:])
    if count == 1:
        return u'секунда'
    elif count < 5:
        return u'секунды'
    else:
        return u'секунд'