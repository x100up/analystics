# coding=utf-8
from datetime import datetime, date, timedelta
from scripts.baseScript import BaseAnalyticsScript
import time
from models.Hive import HiveTable, HiveTablePartition
from services.HiveMetaService import HiveMetaService

PACK_TABLE_QUERY = """INSERT OVERWRITE TABLE stat_{0} PARTITION (year={1},month={2},day={3}) SELECT params, userId, `timestamp`, `hour`, minute, second \
FROM stat_{0} WHERE year={1} AND month={2} AND day={3}"""

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
            self.processApp(appCode)



    def processApp(self, appCode):
        appConfig = self.getAppConfig(appCode)
        if self.event:
            eventCodes = [self.event]
        else:
            eventCodes = [appEvent.code for appEvent in appConfig.getEvents()]
        dbSession = self.getDBSession()
        hiveMetaService = HiveMetaService(dbSession)
        for eventCode in eventCodes:
            print "\n",'start pack key {}.{} for date {}'.format(appCode, eventCode, self.date)
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
                if not hiveTablePartition.isCompact and not self.skipCheckInDB:
                    print 'Start pack table {}.{}'.format(appCode, eventCode)
                    try:
                        start = datetime.now()
                        query = PACK_TABLE_QUERY.format(eventCode, self.year, self.month, self.day)
                        self.hiveClient.execute('USE {}'.format(appCode))
                        self.hiveClient.execute(query)
                        end = datetime.now()
                        print 'Pack complete. Query time: {}'.format(end - start)
                        time.sleep(20)
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



