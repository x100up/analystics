#!/usr/bin/python
# coding=utf-8
from datetime import datetime, date
from scripts.baseScript import BaseAnalyticsScript
import time
from models.Hive import HiveTable, HiveTablePartition

PACK_TABLE_QUERY = """insert overwrite table stat_{0} PARTITION (year={1},month={2},day={3}) select params, userId, `timestamp`, `hour`, minute, second
from stat_{0} WHERE year={1} AND month={2} AND day={3}
"""

class PackerScript(BaseAnalyticsScript):

    def run(self):
        self.hiveClient = self.getHiveClient()
        self.hiveClient.execute('set hive.merge.smallfiles.avgsize = 128000000')
        self.hiveClient.execute('set hive.exec.compress.output=true')
        self.hiveClient.execute('set mapred.output.compression.codec=org.apache.hadoop.io.compress.SnappyCodec')
        self.hiveClient.execute('set hive.merge.mapfiles=true')
        self.hiveClient.execute('set mapred.output.compression.type=BLOCK')
        self.hiveClient.execute('set hive.merge.mapredfiles=true')
        self.hiveClient.execute('set hive.mergejob.maponly=true')

        now = datetime.now()
        self.year, self.month, self.day = (now.year, now.month, now.day)

        if self.options['year']:
            self.year = int(self.options['year'])

        if self.options['month']:
            self.month = int(self.options['month'])

        if self.options['day']:
            self.day = int(self.options['day'])

        for appCode in self.getAppCodes():
            self.processApp(appCode)

    def processApp(self, appCode):
        appConfig = self.getAppConfig(appCode)
        keys = [appEvent.code for appEvent in appConfig.getEvents()]

        for key in keys:
            print 'start pack key {}.{}'.format(appCode, key)
            try:
                start = datetime.now()
                query = PACK_TABLE_QUERY.format(key, self.year, self.month, self.day)
                self.hiveClient.execute('USE {}'.format(appCode))
                self.hiveClient.execute(query)
                end = datetime.now()
                print 'Pack complete. Query time: {}'.format(end - start)
                time.sleep(20)
            except Exception as ex:
                print ex.message
            else:
                app = self.getApp(appCode)
                if app:
                    dbSession = self.getDBSession()
                    hiveTable = dbSession.query(HiveTable).filter_by(appId = app.appId, eventCode = key).first()
                    if not hiveTable:
                        hiveTable = HiveTable()
                        hiveTable.appId = app.appId
                        hiveTable.eventCode = key
                        dbSession.add(hiveTable)
                        dbSession.commit()
                        print 'create new hiveTable'

                    hiveTablePartition = dbSession.query(HiveTablePartition).filter_by(hiveTableId = hiveTable.hiveTableId,
                        partitionDate = date(self.year, self.month, self.day)).first()

                    if not hiveTablePartition:
                        hiveTablePartition = HiveTablePartition
                        hiveTablePartition.hiveTableId = hiveTable.hiveTableId
                        hiveTablePartition.partitionDate = date(self.year, self.month, self.day)
                        hiveTablePartition.isCompact = True
                        print 'create new hiveTablePartition'
                    else:
                        hiveTablePartition.isCompact = True

                    print 'Set compact label to in partiton meta'

                    dbSession.add(hiveTablePartition)
                    dbSession.commit()
                else:
                    print  'cant find app {} in database'.format(appCode)



