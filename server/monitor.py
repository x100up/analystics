#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import re, os, inspect
from models.Config import Config
from components.webhdfs import WebHDFS
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

(options, args) = optParser.parse_args()
options = options.__dict__

appService = AppService(rootPath + '/../app_configs/')
availale_apps = appService.getAppConfigList()

#
# TODO ключи конфигурации
# - удалить лишние таблицы
# - удалить папки в hdfs, для которых нет ключей


if options['appname'] is None:
    print 'App name is not set'
    print 'Availale app names: ' + str(availale_apps)
    exit()

appname = options['appname']

if appname not in availale_apps:
    print 'App name `{}` not available '.format(appname)
    print 'Availale app names: ' + str(availale_apps)
    exit()

# import app settings
appConfig = None
try:
    appConfig = appService.getAppConfig(appname)
except IOError as e:
    logging.error('error reading app (%(appname)s) configuration'%{'appname':appname})
    exit()

STATISTICS_ROOT = '/statistics/' + appname + '/'
webhdfs = WebHDFS("localhost", 14000, "hdfs")
real_keys = appConfig['keys'].keys()

print 'read ' + STATISTICS_ROOT + '......'

# читаем директорию
key_folders = {}
try:
    key_folders = webhdfs.listdir(STATISTICS_ROOT)
except BaseException as e:
    print 'Exception at read list dir'
    print e.__class__.__name__ + ': ' + e.message
    exit()


# ключи есть в настройках, но нет директорий
non_existing_folders = listDiff(real_keys, key_folders)

for key_name in non_existing_folders:
    str = 'folder for key "%(key)s"  not exist'%{'key':key_name}
    print str
    logging.info(str)
    webhdfs.mkdir(STATISTICS_ROOT + key_name)

# есть директории, для которых нет ключей
excess_keys = listDiff(key_folders, real_keys)

for dir_name in excess_keys:
    str = 'key not found for folder "%(dir_name)s"  not exist'%{'dir_name':dir_name}
    logging.info(str)
    print str
    webhdfs.rmdir(STATISTICS_ROOT + dir_name)


def getExistPartitionFolders(key):
    '''
    return list of partitions at HDFS
    '''
    partitions = []
    print(STATISTICS_ROOT + key)
    years = webhdfs.listdir(STATISTICS_ROOT + key)
    for year in years:
        months = webhdfs.listdir(STATISTICS_ROOT + key + '/' + year)
        for month in months:
            days = webhdfs.listdir(STATISTICS_ROOT + key + '/' + year + '/' + month)
            for day in days:
                partitions.append((int(year), int(month), int(day)))

    return partitions

partNameR = re.compile('^year=(\d+)/month=(\d+)/day=(\d+)$')

# check table existing
hiveclient = HiveService(config.get('hive_host'), config.get('hive_port'))
hiveclient.execute('USE %(appname)s'%{'appname':appname})
tables = hiveclient.execute('SHOW TABLES')
tables = [item[0] for item in tables]
print 'tables: ' + str(tables)
for key in real_keys:
    table_name = TABLE_PREFIX + key
    if not table_name in tables:
        print 'table %(table_name)s not exist'%{'table_name':table_name}
        # create table
        q = CREATE_TABLE_QUERY%{'table_name':table_name}
        print q
        hiveclient.execute(q)

    # process partitions
    partitions = hiveclient.execute('SHOW PARTITIONS %(table_name)s'%{'table_name':table_name})
    partitions = [item[0] for item in partitions]
    print 'partitions: ' + str(partitions)

    existing_parts = []
    for partname in partitions:
        r = partNameR.search(partname).group
        existing_parts.append((int(r(1)), int(r(2)), int(r(3))))
    part_folders = getExistPartitionFolders(key)
    print 'exist folders: ' + str(part_folders)

    for part_folder in part_folders:
        if not part_folder in existing_parts:
            year, month, day = part_folder
            query =  CREATE_PARTITION_QUERY%{
                'table_name': table_name,
                'year': year,
                'month': month,
                'day': day,
                'path': '{}/{}/{}/{}/'.format(STATISTICS_ROOT+key, year, month, day)
            }
            print query

            print 'create partition ' + str(part_folder) + ' for ' + table_name
            hiveclient.execute(query)
