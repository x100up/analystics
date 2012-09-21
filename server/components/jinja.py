# -*- coding: utf-8 -*-
from components.dateutil import monthNamesShort
def datetofiled(value):
    return unicode(value.strftime('%d {0} %Y %H:%M')).format(monthNamesShort[value.date().month])