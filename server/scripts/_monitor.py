#!/usr/bin/python

import logging
import re, os, inspect, json
from models.Config import Config
from components.webhdfs import WebHDFS, WebHDFSException
from components.listutils import listDiff
from services.HiveService import HiveService
from services.AppService import AppService
from optparse import OptionParser

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



optParser = OptionParser()
optParser.add_option("-a", "--app", dest="appname", help="application name")
optParser.add_option("-x", "--all", dest="all_apps", help="all applications", action="store_true")

(options, args) = optParser.parse_args()
options = options.__dict__
appService = AppService(rootPath + '/../app_configs/')
availale_apps = appService.getAppConfigList()

# - удалить лишние таблицы
# - удалить папки в hdfs, для которых нет ключей

if options['appname'] is None and options['all_apps'] is None:
    print 'App name is not set'
    print 'Availale app names: ' + str(availale_apps)
    exit()

# import app settings
if options['all_apps']:
    appnames = availale_apps
else:
    appname = options['appname']
    if appname not in availale_apps:
        print 'App name `{}` not available '.format(appname)
        print 'Availale app names: ' + str(availale_apps)
        exit()
    appnames = [appname]


class MonitorScript():




    TABLE_PREFIX = ''


    def __init__(self, appService, hiveclient, host = 'localhost', port = 14000, username = 'hdfs'):
        self.appService = appService
        self.webhdfs = WebHDFS(host, port, username)
        self.real_keys = []
        self.remove_dir_not_equal_key = False
        self.hiveclient = hiveclient

    def readAppConfig(self, appCode):
        appConfig = None
        try:
            appConfig = appService.getNewAppConfig(appCode)
        except IOError as e:
            self.log('error reading app (%(appname)s) configuration'%{'appname':appname})
        self.real_keys = [appEvent.code for appEvent in appConfig.getEvents()]



    def getExistPartitionFolders(self, appCode, key):
        '''
        return list of partitions at HDFS
        '''
        partitions = []
        folder = self.getStatRoot(appCode) + key
        years = self.webhdfs.listdir(folder)
        for year in years:
            months = self.webhdfs.listdir(folder + '/' + year)
            for month in months:
                days = self.webhdfs.listdir(folder + '/' + year + '/' + month)
                for day in days:
                    partitions.append((int(year), int(month), int(day)))

        return partitions

    def getStatRoot(self, appCode):
        return '/statistics/' + appCode + '/'

    def getTableName(self, key):
        return self.TABLE_PREFIX + key

    def log(self, message):
        print message


hiveclient = HiveService(config.get('hive_host'), int(config.get('hive_port')))
monitor = MonitorScript(appService, hiveclient, host=HDFS_HOST, port=HDFS_PORT, username=HDFS_USER)
monitor.TABLE_PREFIX = TABLE_PREFIX
for appname in appnames:
    monitor.processApp(appname)
