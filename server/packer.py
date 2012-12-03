#!/usr/bin/python
# coding=utf-8
import logging
import os, inspect
from datetime import datetime, timedelta
from models.Config import Config
from services.HiveService import HiveService
from services.AppService import AppService
from optparse import OptionParser
import time

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


optParser = OptionParser()
optParser.add_option("-d", "--day", dest="day", help="day To Pack")
optParser.add_option("-m", "--month", dest="month", help="month To Pack")
optParser.add_option("-y", "--year", dest="year", help="year To Pack")
optParser.add_option("-k", "--key", dest="key", help="key To Pack")

(options, args) = optParser.parse_args()
options = options.__dict__

appService = AppService(rootPath + '/../app_configs/')
availale_apps = appService.getAppConfigList()


PACK_TABLE_QUERY = """insert overwrite table stat_{0} PARTITION (year={1},month={2},day={3}) select params, userId, `timestamp`, `hour`, minute, second
from stat_{0} WHERE year={1} AND month={2} AND day={3}
"""

class Packer():

    def __init__(self, appService, hiveClient):
        self.appService = appService
        self.hiveClient = hiveClient
        self.hiveClient.execute('SET hive.exec.compress.output=true')
        self.hiveClient.execute('SET mapred.job.priority=VERY_LOW')
        self.hiveClient.execute('SET mapred.output.compression.codec=org.apache.hadoop.io.compress.SnappyCodec')
        self.hiveClient.execute('SET mapred.output.compression.type=BLOCK')
        self.hiveClient.execute('SET hive.merge.mapfiles=true')

    def getApplications(self):
        return ['topface']

    def pack(self, year, month, day, key = None):
        for app in self.getApplications():
            appConfig = appService.getAppConfig(app)

            if key:
                keys = [key]
            else:
                keys = appConfig['keys']

            for key in keys:
                print 'start pack key {}'.format(key)
                try:
                    start = datetime.now()
                    print start
                    query = PACK_TABLE_QUERY.format(key, year, month, day)
                    self.hiveClient.execute('USE {}'.format(app))
                    self.hiveClient.execute(query)
                    end = datetime.now()
                    print end - start
                    time.sleep(90)
                except Exception as ex:
                    print ex.message

key = None
print options
if options['year'] and options['month'] and options['day']:
    year = options['year']
    month = options['month']
    day = options['day']
else:
    print 'Use -1 day'
    datetime = datetime.now() - timedelta(days=1)
    day = datetime.date().day
    month = datetime.date().month
    year = datetime.date().year

if options['key']:
    key = options['key']

hiveClient = HiveService(config.get('hive_host'), config.get('hive_port'))
packer = Packer(appService, hiveClient)
print 'start pack for date {}.{}.{}'.format(year, month, day)
packer.pack(year, month, day, key = key)