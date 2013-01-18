# coding=utf-8
from datetime import datetime, date
from scripts.baseScript import BaseAnalyticsScript
import time
from models.Hive import HiveTable, HiveTablePartition

PACK_TABLE_QUERY = """insert overwrite table stat_{0} PARTITION (year={1},month={2},day={3}) select params, userId, `timestamp`, `hour`, minute, second \
from stat_{0} WHERE year={1} AND month={2} AND day={3}"""

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

        self.date = date(self.year, self.month, self.day)

        for appCode in self.getAppCodes():
            self.processApp(appCode)

        self.HDFSClient = self.getWebHDFSClient()

    def processApp(self, appCode):
        appConfig = self.getAppConfig(appCode)
        eventCodes = [appEvent.code for appEvent in appConfig.getEvents()]
        dbSession = self.getDBSession()
        for eventCode in eventCodes:
            print "\n",'start pack key {}.{} for date {}'.format(appCode, eventCode, self.date)
            app = self.getApp(appCode)
            if app:

                hiveTable = dbSession.query(HiveTable).filter_by(appId = app.appId, eventCode = eventCode).first()
                q = dbSession.query(HiveTablePartition).filter_by(hiveTableId = hiveTable.hiveTableId,
                    partitionDate = self.date)
                print q
                hiveTablePartition = q.first()

                if self.HDFSClient.isPartitionExist(appCode, eventCode, self.date):
                    print 'folder for partition not exist. Next event'
                    continue


                if not hiveTable:
                    hiveTable = HiveTable()
                    hiveTable.appId = app.appId
                    hiveTable.eventCode = eventCode
                    dbSession.add(hiveTable)
                    dbSession.commit()
                    print 'create new hiveTable'

                if not hiveTablePartition:
                    hiveTablePartition = HiveTablePartition()
                    hiveTablePartition.hiveTableId = hiveTable.hiveTableId
                    hiveTablePartition.partitionDate = self.date
                    hiveTablePartition.isCompact = False
                    print 'create new hiveTablePartition'
                    dbSession.add(hiveTablePartition)
                    dbSession.commit()
                else:
                    print 'Partition find in DB: {} {}'.format(hiveTablePartition.isCompact, hiveTablePartition.partitionDate, hiveTablePartition.hiveTableId)

                if not hiveTablePartition.isCompact:
                    print 'Start pack table {}.{}'.format(appCode, eventCode)
                    try:
                        start = datetime.now()
                        query = PACK_TABLE_QUERY.format(eventCode, self.year, self.month, self.day)
                        print query
                        self.hiveClient.execute('USE {}'.format(appCode))
                        self.hiveClient.execute(query)
                        end = datetime.now()
                        print 'Pack complete. Query time: {}'.format(end - start)
                        time.sleep(20)
                    except Exception as ex:
                        print 'Pack end with exception {}'.format(ex.message)
                    else:
                        hiveTablePartition.isCompact = True
                        print 'Set compact label to in partiton meta'

                        dbSession.add(hiveTablePartition)
                        dbSession.commit()
                else:
                    print 'table {}.{} already packed'.format(appCode, eventCode)
            else:
                print  'cant find app {} in database'.format(appCode)



