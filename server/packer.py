#!/usr/bin/python
# coding=utf-8
import logging
import os, inspect
from datetime import datetime, timedelta
from models.Config import Config
from services.HiveService import HiveService
from services.AppService import AppService

__author__ = 'pavlenko.roman.spb@gmail.com'

# set logger
logging.basicConfig(level = logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# set configurations
rootPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) # script directory

config = Config()
config.readConfigFile(os.path.abspath(os.path.abspath(rootPath + '/../server.cfg')))

STATISTICS_ROOT = config.get('hdfs_statistic_path')
HDFS_HOST = config.get('hdfs_host')
HDFS_PORT = int(config.get('hdfs_port'))
HDFS_USER = config.get('hdfs_username')
TABLE_PREFIX = config.get('hive_prefix')

appService = AppService(rootPath + '/../app_configs/')

PACK_TABLE_QUERY = """insert overwrite table stat_{0} PARTITION (year={1},month={2},day={3}) select params, userId, `timestamp`, `hour`, minute, second
from stat_{0} WHERE year={1} AND month={2} AND day={3}
"""

class Packer():

    def __init__(self, appService, hiveClient):
        self.appService = appService
        self.hiveClient = hiveClient

    def getApplications(self):
        return ['topface']

    def pack(self, year, month, day):
        for app in self.getApplications():
            appConfig = appService.getAppConfig(app)

            for key in appConfig['keys']:
                print 'start pack key {}'.format(key)
                try:
                    start = datetime.now()
                    print start
                    query = PACK_TABLE_QUERY.format(key, year, month, day)
                    self.hiveClient.execute('USE {}'.format(app))
                    self.hiveClient.execute(query)
                    print end - start
                except Exception as ex:
                    print ex.message



datetime = datetime.now() - timedelta(days=1)

hiveClient = HiveService(config.get('hive_host'), config.get('hive_port'))
packer = Packer(appService, hiveClient)
print 'start pack for date {}.{}.{}'.format(datetime.year, datetime.month, datetime.day)
packer.pack(datetime.year, datetime.month, datetime.day)