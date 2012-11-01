#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import re, os, inspect
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
TABLE_PREFIX = config.get('hive_prefix')

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


class AnalyticsMonitor():
    TABLE_PREFIX = ''
    partNameR = re.compile('^year=(\d+)/month=(\d+)/day=(\d+)$')

    def __init__(self, appService, hiveclient):
        self.appService = appService
        self.webhdfs = WebHDFS("localhost", 14000, "hdfs")
        self.real_keys = []
        self.remove_dir_not_equal_key = False
        self.hiveclient = hiveclient

    def readAppConfig(self, appCode):
        appConfig = None
        try:
            appConfig = appService.getAppConfig(appCode)
        except IOError as e:
            self.log('error reading app (%(appname)s) configuration'%{'appname':appname})
        self.real_keys = appConfig['keys'].keys()

    def processApp(self, appCode):
        self.log('ProcessApp:'+appCode)
        self.readAppConfig(appCode)
        # получаем список директорий -ключей
        key_folders = {}
        try:
            key_folders = self.webhdfs.listdir(self.getStatRoot(appCode))
        except WebHDFSException as e:
            if e.name == WebHDFSException.FileNotFoundException:
                print 'application stat directory not found'
                return

        # ключи есть в настройках, но нет директорий
        non_existing_folders = listDiff(self.real_keys, key_folders)

        for key_name in non_existing_folders:
            self.log('folder for key "{}" app {} not exist'.format(key_name, appCode))
            return

        # есть директории, для которых нет ключей
        excess_keys = listDiff(key_folders, self.real_keys)
        for dir_name in excess_keys:
            self.log('key not found for folder "%(dir_name)s" not exist'.format(dir_name))
            if self.remove_dir_not_equal_key:
                self.log('try remove '.format(dir_name))
                self.webhdfs.rmdir(self.getStatRoot(appCode) + dir_name)


        # check table existing
        self.hiveclient.execute('CREATE DATABASE IF NOT EXISTS %(appname)s' % {'appname':appname})
        self.hiveclient.execute('USE %(appname)s' % {'appname':appname})
        tables = self.hiveclient.execute('SHOW TABLES')
        tables = [item[0] for item in tables]
        self.log('tables for app {}: '.format(appCode) + str(tables))

        for key in self.real_keys:
            table_name = self.getTableName(key)
            if not table_name in tables:
                self.log('table %(table_name)s not exist'%{'table_name':table_name})
                # create table
                q = CREATE_TABLE_QUERY%{'table_name':table_name}
                self.hiveclient.execute(q)

            # process partitions
            partitions = self.hiveclient.execute('SHOW PARTITIONS %(table_name)s'%{'table_name':table_name})
            partitions = [item[0] for item in partitions]
            self.log('partitions: ' + str(partitions))

            existing_parts = []
            for partname in partitions:
                r = self.partNameR.search(partname).group
                existing_parts.append((int(r(1)), int(r(2)), int(r(3))))
            part_folders = self.getExistPartitionFolders(appCode, key)
            self.log('exist folders: ' + str(part_folders))

            for part_folder in part_folders:
                if not part_folder in existing_parts:
                    year, month, day = part_folder
                    query =  CREATE_PARTITION_QUERY%{
                        'table_name': table_name,
                        'year': year,
                        'month': month,
                        'day': day,
                        'path': '{}/{}/{}/{}/{}/'.format(self.getStatRoot(appCode), key, year, month, day)
                    }
                    self.log('create partition ' + str(part_folder) + ' for ' + table_name)
                    self.hiveclient.execute(query)

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


hiveclient = HiveService(config.get('hive_host'), config.get('hive_port'))
monitor = AnalyticsMonitor(appService, hiveclient)
monitor.TABLE_PREFIX = TABLE_PREFIX
for appname in appnames:
    monitor.processApp(appname)
