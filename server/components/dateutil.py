# -*- coding: utf-8 -*-
monthNamesShort = [u'янв', u'фев', u'март', u'апр', u'май', u'июнь', u'июль', u'авг', u'сен', u'окт', u'ноя', u'дек']

def repMonth(string):
    for i, m in enumerate(monthNamesShort):
        string = string.replace(m, str(i + 1))
    return string