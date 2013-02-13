# coding=utf-8
__author__ = 'x100up'
from scripts.baseScript import BaseAnalyticsScript
from components.webhdfs import WebHDFSException
from services.HiveMetaService import HiveMetaService

class InitHiveMetaDataScript(BaseAnalyticsScript):

    def run(self):
        print 'run InitHiveMetaDataScript'
        appCodes = self.getAppCodes()
        self.hiveMetaService = HiveMetaService(self.getDBSession())


        for appCode in appCodes:
            appConfig = self.getAppConfig(appCode)
            self.processApp(appConfig)

    def processApp(self, appConfig):
        appCode = appConfig.getAppCode()
        app = self.getApp(appCode)
        if not app:
            print 'Cant find app with code {}. Terminate.'.format(appCode)
            self.terminate()
        print 'Process app {}'.format(appCode)

        for appEvent in appConfig.getEvents():
            hiveTable = self.hiveMetaService.getOrCreateHiveTable(app.appId, appEvent.code)
            if not hiveTable:
                print 'Cant get or create HiveTable for {}, {}'.format(appCode, appEvent.code)
                continue
            self.processHiveTable(hiveTable, appCode, appEvent.code)

    def processHiveTable(self, hiveTable, appCode, eventCode):
        print 'processHiveTable for {}, {}'.format(appCode, eventCode)
        dbSession = self.getDBSession()
        analyticsWebHDFS = self.getWebHDFSClient()
        try:
            partitionsDates = analyticsWebHDFS.getPartitions(appCode, eventCode)
        except WebHDFSException as e:
            print 'Exception on getPartitions: {}'.format(e.message)
        else:
            for partitionDate in partitionsDates:
                hivePartition = self.hiveMetaService.getOrCreateHiveTablePartition(hiveTable.hiveTableId, partitionDate)
                if not hivePartition:
                    print('Cant get or create partition for {} date {}'.format(eventCode, hivePartition.partitionDate))
                    continue

            if partitionsDates:
                minDate = min(partitionsDates)
                hiveTable.startFrom = minDate
                dbSession.add(hiveTable)
                dbSession.commit()
                print 'Set start from {} {} {}'.format(appCode, eventCode, minDate)
