# -*- coding: utf-8 -*-
from scripts.baseScript import BaseAnalyticsScript
from components.listutils import listDiff
from models.Config import Config
import re
from datetime import date

CREATE_TABLE_QUERY = """CREATE TABLE %(table_name)s (params MAP<STRING, STRING>, `userId` INT, `timestamp` TIMESTAMP, hour INT, minute INT, second INT)
PARTITIONED BY (year INT, month INT, day INT)
ROW FORMAT DELIMITED
  FIELDS TERMINATED BY ','
COLLECTION ITEMS TERMINATED BY '\;'
MAP KEYS TERMINATED BY '='"""

CREATE_PARTITION_QUERY = """
ALTER TABLE %(table_name)s ADD
PARTITION (year=%(year)i, month=%(month)i, day=%(day)i) location '%(path)s'
"""

class MonitorScript(BaseAnalyticsScript):

    partNameR = re.compile('^year=(\d+)/month=(\d+)/day=(\d+)$')

    def run(self):
        self.hiveclient = self.getHiveClient()
        for appCode in self.getAppCodes():
            self.processApp(appCode)

    def processApp(self, appCode):
        print 'ProcessApp {}'.format(appCode)
        appConfig = self.getAppConfig(appCode)

        webHDFSClient = self.getWebHDFSClient()
        # получаем список директорий -ключей
        hdfsEvents = webHDFSClient.getEventCodes(appCode)
        realKeys = [appEvent.code for appEvent in appConfig.getEvents()]

        # ключи есть в настройках, но нет директорий
        non_existing_folders = listDiff(realKeys, hdfsEvents)

        # check table existing
        self.hiveclient.execute('CREATE DATABASE IF NOT EXISTS {}'.format(appCode))
        self.hiveclient.execute('USE {}'.format(appCode))
        tables = self.hiveclient.execute('SHOW TABLES')
        tables = [item[0] for item in tables]
        print 'tables for app {}: {} '.format(appCode, str(tables))

        for key in realKeys:

            if key in non_existing_folders:
                continue

            table_name = self.getTableName(key)
            if not table_name in tables:
                print 'table {} not exist'.format(table_name)
                # create table
                q = CREATE_TABLE_QUERY % {'table_name':table_name}
                self.hiveclient.execute(q)

            # process partitions
            partitions = self.hiveclient.execute('SHOW PARTITIONS {}'.format(table_name))
            partitions = [item[0] for item in partitions]

            existingPartitionsDates = []
            for partName in partitions:
                r = self.partNameR.search(partName).group
                existingPartitionsDates.append(date(int(r(1)), int(r(2)), int(r(3))))
            part_folders = webHDFSClient.getPartitions(appCode, key)

            for partitionDate in part_folders:
                if not partitionDate in existingPartitionsDates:
                    year, month, day = (partitionDate.year, partitionDate.month, partitionDate.day)
                    query =  CREATE_PARTITION_QUERY%{
                        'table_name': table_name,
                        'year': year,
                        'month': month,
                        'day': day,
                        'path': '{}/{}/{}/{}/{}/'.format(self.getTablePath(appCode), key, year, month, day)
                    }
                    print 'Create partition {} for {}'.format(str(partitionDate), table_name)
                    try:
                        self.hiveclient.execute(query)
                    except:
                        print 'Exception on create partition'
                    else:
                        print 'Partition successfuly created'



    def getTableName(self, key):
        return self.config.get(Config.HIVE_PREFIX) + key

    def getTablePath(self, appCode):
        return self.config.get(Config.HDFS_STAT_ROOT) + appCode + '/'