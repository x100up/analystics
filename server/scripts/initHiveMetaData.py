#!/usr/bin/python
# coding=utf-8
__author__ = 'x100up'
from scripts.baseScript import BaseAnalyticsScript
from models.Hive import HiveTable, HiveTablePartition

class InitHiveMetaDataScript(BaseAnalyticsScript):

    def run(self):
        appCodes = self.getAppCodes()
        for appCode in appCodes:
            appConfig = self.getAppConfig(appCode)
            self.processApp(appConfig)

    def processApp(self, appConfig):
        dbSession = self.getDBSession()
        appCode = appConfig.getAppCode()
        app = self.getApp(appCode)
        if not app:
            print 'Cant find app with code {}. Terminate.'.format(appCode)
            self.terminate()
        print 'Process app {}'.format(appCode)

        for appEvent in appConfig.getEvents():
            hiveTable = dbSession.query(HiveTable).filter_by(appId = app.appId, eventCode = appEvent.code).first()
            if not hiveTable:
                hiveTable = HiveTable()
                hiveTable.appId = app.appId
                hiveTable.eventCode = appEvent.code
                dbSession.add(hiveTable)
                dbSession.commit()

            self.processHiveTable(hiveTable, appCode, appEvent.code)

    def processHiveTable(self, hiveTable, appCode, eventCode):
        dbSession = self.getDBSession()
        analyticsWebHDFS = self.getWebHDFSClient()
        partitionsDates = analyticsWebHDFS.getPartitions(appCode, eventCode)
        for partitionDate in partitionsDates:
            hivePartition = dbSession.query(HiveTablePartition).filter_by(hiveTableId = hiveTable.hiveTableId, partitionDate = partitionDate).first()
            if not hivePartition:
                hivePartition = HiveTablePartition()
                hivePartition.hiveTableId = hiveTable.hiveTableId
                hivePartition.partitionDate = partitionDate
                hivePartition.isCompact = False
                dbSession.add(hivePartition)
                dbSession.commit()
                print('Add hive partition {} for date {}'.format(eventCode, partitionDate))

        if partitionsDates:
            minDate = min(partitionsDates)
            hiveTable.startFrom = minDate
            dbSession.add(hiveTable)
            dbSession.commit()


script = InitHiveMetaDataScript()
script.run()