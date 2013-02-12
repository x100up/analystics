# -*- coding: utf-8 -*-
from scripts.baseScript import BaseAnalyticsScript
import re
from datetime import datetime

class NewScheme(BaseAnalyticsScript):

    def run(self):
        now = datetime.now()
        self.hiveclient = self.getHiveClient()
        oldTables = self.getOldTables()
        for table in oldTables:
            # partitions = self.getOldPartitions(table)
            # for partition in partitions:
            #     g = re.search('year=(\d+)\/month=(\d+)\/day=(\d+)', partition).group
                year, month, day = (2013, 2, 11)

                if month == now.month and day == now.day:
                    continue
                print 'reload {} {}.{}.{}'.format(table, year, month, day)
                try:
                    self.hiveclient.execute('USE stat_topface')
                    query = 'INSERT OVERWRITE TABLE ' + table + ' PARTITION (dt=\'%(year)d-%(month)02d-%(day)02d\')' % {'year': year, 'month': month, 'day': day} +\
                            ' SELECT params, `userId`, `timestamp`, hour, minute, second FROM topface.' + table +\
                            ' WHERE day = {} and month = {} and year = {}'.format(day, month, year)

                    self.hiveclient.execute(query)
                except Exception as e:
                    print 'exception on reload: {}'.format(e.message)
                else:
                    self.hiveclient.execute('USE topface')
                    self.hiveclient.execute('ALTER TABLE {} DROP PARTITION (year={},month={},day={})'.format(table, year, month, day))




    def getOldTables(self):
        self.hiveclient.execute('USE topface')
        tables = self.hiveclient.execute('SHOW TABLES')
        return [t[0] for t in tables]


    def getOldPartitions(self, tableName):
        self.hiveclient.execute('USE topface')
        tables = self.hiveclient.execute('SHOW PARTITIONS {}'.format(tableName))
        return [t[0] for t in tables]
