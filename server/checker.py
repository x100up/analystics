# coding=utf-8
# сканирует директории и сверяет их с ключами
from models.Config import Config
from components.webhdfs import WebHDFS
from services.AppService import AppService
import os, inspect

# set configurations
rootPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) # script directory

config = Config()
config.readConfigFile(os.path.abspath(os.path.abspath(rootPath + '/../server.cfg')))

STATISTICS_ROOT = config.get('hdfs_statistic_path') + 'topface/'
HDFS_HOST = config.get('hdfs_host')
HDFS_PORT = int(config.get('hdfs_port'))
HDFS_USER = config.get('hdfs_username')
webHDFS = WebHDFS(HDFS_HOST, HDFS_PORT, HDFS_USER)

dirs = webHDFS.listdir(STATISTICS_ROOT)

appService = AppService(rootPath + '/../app_configs/')
appConfig = appService.getNewAppConfig('topface')
events = [e.code for e in appConfig.getEvents()]

for dir in dirs:
    if not dir in events:
        print 'Directory {} exist, but event code not found in config'.format(dir)

