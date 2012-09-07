# -*- coding: utf-8 -*-
from utils.webhdfs import WebHDFS
from utils.listutils import listDiff
from service.HiveService import HiveService
from service.AppService import AppService
import logging, re, ConfigParser
from optparse import OptionParser

# set logger
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# set configurations
configParser = ConfigParser.RawConfigParser()
configParser.read(['server.cnf'])

APP_CONFIG_PATH = configParser.get('core', 'app_config_path')
STATISTICS_ROOT = configParser.get('hdfs', 'statistic_path')
TABLE_PREFIX = configParser.get('hive', 'prefix')

CREATE_TABLE_QUERY = """
CREATE TABLE %(table_name)s (params MAP<STRING, STRING>, `timestamp` TIMESTAMP, hour INT, minute INT, second INT)
PARTITIONED BY (year INT, month INT, day INT)
ROW FORMAT DELIMITED
  FIELDS TERMINATED BY ','
COLLECTION ITEMS TERMINATED BY '\;'
MAP KEYS TERMINATED BY '=';
"""

CREATE_PARTITION_QUERY = """
ALTER TABLE %(table_name)s ADD
PARTITION (year=%(year)i, month=%(month)i, day=%(day)i) location '%(path)s'
"""

optParser = OptionParser()
optParser.add_option("-a", "--app", dest="appname", help="application name")

(options, args) = optParser.parse_args()
options = options.__dict__

appService = AppService(APP_CONFIG_PATH)
availale_apps = appService.getAppConfigList()

'''
 TODO ключи конфигурации
 - удалить лишние таблицы
 - удалить папки в hdfs, для которых нет ключей
'''

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

# читаем директорию
key_folders = {}
try:
    key_folders = webhdfs.listdir(STATISTICS_ROOT)
except Exception as e:
    print 'HDFS Exception: ' + e.message
    exit()


# ключи есть в настройках, но нет директорий
non_existing_folders = listDiff(real_keys, key_folders)

for key_name in non_existing_folders:
    str = 'folder for key "%(key)s"  not exist'%{'key':key_name}
    logging.info(str)
    webhdfs.mkdir(STATISTICS_ROOT + key_name)

# есть директории, для которых нет ключей
excess_keys = listDiff(key_folders, real_keys)

for dir_name in excess_keys:
    str = 'key not found for folder "%(dir_name)s"  not exist'%{'dir_name':dir_name}
    logging.info(str)
    print STATISTICS_ROOT + dir_name
    webhdfs.rmdir(STATISTICS_ROOT + dir_name)


def getExistPartitionFolders(key):
    partitions = []
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
hiveclient = HiveService()
hiveclient.execute('USE %(appname)s'%{'appname':appname})
tables = hiveclient.execute('SHOW TABLES')
tables = [item[0] for item in tables]
print 'tables: ' + str(tables)
for key in real_keys:
    table_name = TABLE_PREFIX + key
    if not table_name in tables:
        print 'table %(table_name)s not exist'%{'table_name':table_name}
        # create table
        hiveclient.execute(CREATE_TABLE_QUERY%{'table_name':table_name})

    # process partitions
    partitions = hiveclient.execute('SHOW PARTITIONS %(table_name)s'%{'table_name':table_name})
    partitions = [item[0] for item in partitions]
    print partitions

    existing_parts = []
    for partname in partitions:
        r = partNameR.search(partname).group
        existing_parts.append((int(r(1)), int(r(2)), int(r(3))))
    part_folders = getExistPartitionFolders(key)

    for part_folder in part_folders:
        if not part_folder in existing_parts:
            year, month, day = part_folder
            query =  CREATE_PARTITION_QUERY%{
                'table_name': table_name,
                'year': year,
                'month': month,
                'day': day,
                'path': '{}/{}/{:02d}/{}/'.format(STATISTICS_ROOT+key, year, month, day)
            }

            print 'create partition ' + str(part_folder) + ' for ' + table_name
            hiveclient.execute(query)
