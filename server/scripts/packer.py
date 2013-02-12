# coding=utf-8
"""
Скрипт упаковывает данные за день в большие файлы со сжатием snappy
"""

from datetime import datetime, date, timedelta
from scripts.baseScript import BaseAnalyticsScript
import time
from services.HiveMetaService import HiveMetaService

PACK_TABLE_QUERY = """INSERT OVERWRITE TABLE stat_{0} PARTITION (dt='{1}') SELECT params, userId, `timestamp`, `hour`, minute, second \
FROM stat_{0} WHERE dt='{1}'"""


class PackerScript(BaseAnalyticsScript):

    def run(self):
        hiveClient = self.getHiveClient()
        hiveClient.execute('set hive.merge.smallfiles.avgsize = 128000000')
        hiveClient.execute('set hive.exec.compress.output=true')
        hiveClient.execute('set mapred.output.compression.codec=org.apache.hadoop.io.compress.SnappyCodec')
        hiveClient.execute('set hive.merge.mapfiles=true')
        hiveClient.execute('set mapred.output.compression.type=BLOCK')
        hiveClient.execute('set hive.merge.mapredfiles=true')
        hiveClient.execute('set hive.stats.autogather=false')
        hiveClient.execute('set hive.mergejob.maponly=true')
        self.event = False
        self.skipCheckInDB = bool(self.options['skipCheckInDB'])
        print self.skipCheckInDB

        now = datetime.now() - timedelta(days = 1)
        self.year, self.month, self.day = (now.year, now.month, now.day)

        if self.options['year']:
            self.year = int(self.options['year'])

        if self.options['month']:
            self.month = int(self.options['month'])

        if self.options['day']:
            self.day = int(self.options['day'])

        if self.options['event']:
            self.event = self.options['event']

        self.date = date(self.year, self.month, self.day)

        self.HDFSClient = self.getWebHDFSClient()

        for appCode in self.getAppCodes():
            self.processApp(appCode, hiveClient)

    def processApp(self, appCode, hiveClient):
        appConfig = self.getAppConfig(appCode)
        if self.event:
            eventCodes = [self.event]
        else:
            eventCodes = [appEvent.code for appEvent in appConfig.getEvents()]
        dbSession = self.getDBSession()
        hiveMetaService = HiveMetaService(dbSession)
        counter = 1
        _len = len(eventCodes)
        for eventCode in eventCodes:
            print "\n",'start pack key {}.{} for date {} ({}/{})'.format(appCode, eventCode, self.date, counter, _len)
            app = self.getApp(appCode)
            if app:
                # получаем таблицу
                hiveTable = hiveMetaService.getOrCreateHiveTable(app.appId, eventCode)
                if not hiveTable:
                    print 'Cannot create new hiveTable. Terminate'
                    return

                # существует ли партиция физически
                if not self.HDFSClient.isPartitionExist(appCode, eventCode, self.date):
                    print 'folder for partition not exist. Next event'
                    continue

                # получаем партицию таблицы
                hiveTablePartition = hiveMetaService.getOrCreateHiveTablePartition(hiveTable.hiveTableId, self.date)
                if not hiveTablePartition:
                    print 'Cannot create new hiveTablePartition. Terminate'
                    continue

                # если не сжата
                if not hiveTablePartition.isCompact or self.skipCheckInDB:
                    print 'Start pack table {}.{}'.format(appCode, eventCode)
                    try:
                        start = datetime.now()
                        query = PACK_TABLE_QUERY.format(eventCode, '%(year)d-%(month)02d-%(day)02d' % {'year': self.year, 'month': self.month, 'day': self.day})
                        hiveClient.execute('USE {}'.format(self.getDBName(appCode)))
                        hiveClient.execute(query)
                        end = datetime.now()
                        print 'Pack complete. Query time: {}'.format(end - start)
                        time.sleep(10)
                    except Exception as ex:
                        print 'Pack end with exception {}'.format(ex.message)
                    else:
                        hiveTablePartition.isCompact = 1
                        print 'Set compact label to in partition meta'

                        dbSession.add(hiveTablePartition)
                        dbSession.commit()
                else:
                    print 'table {}.{} already packed'.format(appCode, eventCode)
            else:
                print  'cant find app {} in database'.format(appCode)

            counter += 1

    def getDBName(self, appCode):
        return 'stat_' + appCode